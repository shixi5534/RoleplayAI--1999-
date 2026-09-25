# -*- coding: utf-8 -*-
"""B4 真实实现之一：**实体级伪相关反馈（PRF）**。

为什么走这条路
    `diag_b4_ceiling.py` 实测「完美查询扩展」的天花板是 **+25.67 pt**
    （inject 62.00% → 87.67%），是所有方向里最大的空间。
    但现成的语义实体链接（`semantic_link_*`）实测最多只 +1 题——
    因为 bge-m3 认为"错实体"更像答案（与全项目其它结论一致）。
    LLM 又不一定懂这部作品的设定。

    于是换一条**不需要外部知识**的路：
        第一轮用原查询检索 → 取回块里**已经出现的实体** → 用它们做二次检索。
    原理：第一轮即使没召回「答案块」，也常能召回**同一场景/章节的邻居块**，
    这些块里往往就提到了我们要找的那个实体。等于用检索结果自己给自己做扩展。

实现（离线，不改生产）
    1. pass1 = retrieve(q)
    2. 对 pass1 每块调 graph.link_detailed(block.text) → 该块提到的实体
    3. 跨块聚合（出现块数优先，权重和次之）→ 取 top-N 实体名
    4. pass2 = retrieve(q + " " + 这些实体名)
    5. 用 evaluate_case 同口径对比 pass1 / pass2

⚠️ 负样本护栏：PRF 会凭空往查询里加实体名，**很可能引发负样本注入**。
   本脚本先只看正样本收益；若有效，必须复测 negatives 才能谈接入。

用法：.venv/Scripts/python.exe -X utf8 scripts/diag_b4_prf.py
"""
from __future__ import annotations

import json
import sys
import time
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

# 心跳：脚本跑到哪一步一目了然（本机 stdout 重定向不可读，只能靠文件）
_HB = ROOT / "data" / "knowledge" / "_audit" / "_b4_prf_heartbeat.txt"


def _beat(msg: str) -> None:
    with _HB.open("a", encoding="utf-8") as f:
        f.write(f"{time.strftime('%H:%M:%S')} {msg}\n")


_HB.write_text(f"start argv={sys.argv}\n", encoding="utf-8")
_beat("imports 前置标记")

import eval_plot_rag as E  # noqa: E402
from roleplay.config import get_settings  # noqa: E402
from roleplay.core.knowledge.factory import build_plot_registry  # noqa: E402

_beat("imports 完成")

AUDIT = ROOT / "data" / "knowledge" / "_audit"
TESTSET = AUDIT / "rag_testset_300_clean.json"
BUDGET = 2400
NS = (1, 3, 5)          # 扩展实体数


def top2_hit(chunks, full) -> bool:
    return any(E.chunk_hash(c.text) in full for c in chunks[:2])


def main() -> int:
    import traceback
    _beat("main() 进入")
    log_path = AUDIT / "_b4_prf.txt"
    try:
        rc = _run()
        _beat(f"_run 正常返回 {rc}")
        return rc
    except BaseException:  # noqa: BLE001  连 SystemExit/KeyboardInterrupt 一起记
        _beat("捕获到异常，写 traceback")
        # PowerShell 的 stdout 重定向会把输出写成 UTF-16（读不出来），
        # 所以异常也必须自己落盘，否则只能看到一个没有信息的"退出码 1"。
        with log_path.open("a", encoding="utf-8") as f:
            f.write("\n[TRACEBACK]\n" + traceback.format_exc())
        raise


def _run() -> int:
    cases = json.loads(TESTSET.read_text(encoding="utf-8"))
    _beat(f"题集载入 {len(cases)}")
    s = get_settings()
    retr = build_plot_registry(s).get("wu_ming_zhe")
    _beat(f"检索器就绪 type={type(retr).__name__}")
    # 注意：link_detailed 是 **检索器自身** 的方法（同一类里定义），
    # 不是 retr.graph 的——实测 retr.graph 为 None。
    _beat(f"has_link_detailed={hasattr(retr, 'link_detailed')}")
    if not hasattr(retr, "link_detailed"):
        _beat("[FATAL] 检索器不支持 link_detailed")
        print("[FATAL] 检索器不支持 link_detailed")
        return 2
    oracle = E.build_oracle(retr.corpus, cases)
    top_prod = int(getattr(s, "plot_max_chunks", 6))
    lf_prod = int(getattr(s, "plot_lexical_fallback", 2))

    out: list[str] = []

    def p(*a):
        line = " ".join(str(x) for x in a)
        out.append(line)
        print(line, flush=True)

    n = len(cases)
    # 指标：base + 每个 N 一列
    agg = {"base_inject": 0, "base_strict": 0, "base_top2": 0}
    for k in NS:
        agg[f"n{k}_inject"] = 0
        agg[f"n{k}_strict"] = 0
        agg[f"n{k}_top2"] = 0
    rows: list[dict] = []
    t_all = time.time()

    for _i, item in enumerate(cases):
        if _i % 25 == 0:
            _beat(f"case {_i}/{n}")
        qid = str(item["id"])
        full = oracle[qid]["full"]

        # ---- pass1：原查询 ----
        cap1: dict[str, list] = {}

        def grab1(q, chunks):
            cap1["c"] = chunks
            return chunks

        r1 = E.evaluate_case(retr, item, oracle[qid], top_prod, lf_prod, BUDGET,
                             chunks_transform=grab1)
        chunks1 = cap1.get("c") or []

        # ---- 从 pass1 块里抽实体 ----
        seen_blocks: Counter[str] = Counter()
        wsum: defaultdict[str, float] = defaultdict(float)
        name_of: dict[str, str] = {}
        for c in chunks1:
            try:
                linked = retr.link_detailed(c.text or "")
            except Exception:  # noqa: BLE001
                linked = {}
            for eid, info in linked.items():
                seen_blocks[eid] += 1
                wsum[eid] += float(info.get("weight") or 0.0)
                name_of.setdefault(eid, str(info.get("name") or ""))
        ranked = sorted(seen_blocks, key=lambda e: (-seen_blocks[e], -wsum[e]))

        rec = {"id": qid, "n_groups": len(item.get("evidence") or []),
               "base_inject": bool(r1.get("inject_pass")),
               "base_top2": bool(top2_hit(chunks1, full))}
        agg["base_inject"] += rec["base_inject"]
        agg["base_strict"] += bool(r1.get("strict_pass"))
        agg["base_top2"] += rec["base_top2"]

        # ---- pass2：每种 N 各跑一次 ----
        for k in NS:
            names = [name_of[e] for e in ranked[:k] if name_of.get(e)]
            if not names:
                item2 = item
            else:
                item2 = dict(item)
                item2["q"] = f"{item['q']} {' '.join(names)}"
            cap2: dict[str, list] = {}

            def grab2(q, chunks):
                cap2["c"] = chunks
                return chunks

            r2 = E.evaluate_case(retr, item2, oracle[qid], top_prod, lf_prod, BUDGET,
                                 chunks_transform=grab2)
            agg[f"n{k}_inject"] += bool(r2.get("inject_pass"))
            agg[f"n{k}_strict"] += bool(r2.get("strict_pass"))
            agg[f"n{k}_top2"] += top2_hit(cap2.get("c") or [], full)
            rec[f"n{k}_inject"] = bool(r2.get("inject_pass"))
        rows.append(rec)

    p("=" * 84)
    p(f"B4 实体级伪相关反馈（PRF）｜n={n}｜耗时 {(time.time() - t_all) / 60:.1f} min")
    p("=" * 84)
    p(f"{'指标':<16}{'基线':>10}{'扩展1':>10}{'扩展3':>10}{'扩展5':>10}")
    p("-" * 84)
    for key, label in (("inject", "inject_pass"), ("strict", "strict_pass"),
                       ("top2", "top2_hit")):
        b = agg[f"base_{key}"] / n
        cells = "".join(f"{agg[f'n{k}_{key}'] / n:>10.4f}" for k in NS)
        p(f"{label:<16}{b:>10.4f}{cells}")
    p("-" * 84)
    p(f"{'Δinject':<16}{'—':>10}" +
      "".join(f"{(agg[f'n{k}_inject'] - agg['base_inject']) / n:>+10.4f}" for k in NS))
    p("=" * 84)

    best_k = max(NS, key=lambda k: agg[f"n{k}_inject"])
    delta = (agg[f"n{best_k}_inject"] - agg["base_inject"]) / n
    p(f"最佳扩展数 N={best_k}｜Δinject = {delta:+.4f}"
      f"（{agg[f'n{best_k}_inject'] - agg['base_inject']:+d} 题）")
    p()
    if delta >= 0.05:
        p("✅ PRF 有效 ⇒ 值得继续（并必须复测 negatives 负样本护栏）")
    elif delta > 0:
        p("⚠️ PRF 有微弱正收益 ⇒ 需要看分层与负样本，谨慎推进")
    else:
        p("❌ PRF 无效 ⇒ B4 用这条路也拿不到天花板；需 LLM 实体链接或人工术语表")
    p()
    p("⚠️ 天花板（完美扩展）是 +25.67 pt，本脚本衡量的是**可自动获得的部分**。")

    (AUDIT / "_b4_prf.txt").write_text("\n".join(out), encoding="utf-8")
    (AUDIT / "b4_prf.json").write_text(json.dumps(rows, ensure_ascii=False, indent=1),
                                       encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
