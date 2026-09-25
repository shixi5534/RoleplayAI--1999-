# -*- coding: utf-8 -*-
"""B4（查询扩展）天花板测试 —— **先测上界，再决定值不值得做**。

背景
    96 个缺口证据组里 **95 个的题面不含该实体的任何名字**
    （如「海盗船上的歌手是谁」→ 答案 星锑）。当前每题平均只有 1.43 个种子。
    B4 的思路是：中文描述 → 猜出实体名 → 注入种子 → 走图谱路径。

为什么要先测天花板
    B4 是开发项（要做实体链接 / LLM 猜测），成本高。
    在投入之前必须先确认：**就算完美猜中实体，检索能不能变好？**
    如果完美扩展都救不回来，那 B4 建了也白建。

做法（作弊上界，非真实实现）
    把每题 evidence 的全部关键词**直接拼到 query 后面**，模拟"完美查询扩展"。
    oracle 是按语料预计算的、与 query 无关，所以可以直接复用。

⚠️ 这是**上界**，不是 B4 的真实收益——真实 B4 必须在不知道答案的前提下猜实体。
   本脚本只回答"天花板有多高"，用来决定要不要投入。

用法：.venv/Scripts/python.exe -X utf8 scripts/diag_b4_ceiling.py
"""
from __future__ import annotations

import json
import statistics
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

import eval_plot_rag as E  # noqa: E402
from roleplay.config import get_settings  # noqa: E402
from roleplay.core.knowledge.factory import build_plot_registry  # noqa: E402

AUDIT = ROOT / "data" / "knowledge" / "_audit"
TESTSET = AUDIT / "rag_testset_300_clean.json"
BUDGET = 2400


def top2_hit(chunks, full) -> bool:
    return any(E.chunk_hash(c.text) in full for c in chunks[:2])


def main() -> int:
    cases = json.loads(TESTSET.read_text(encoding="utf-8"))
    s = get_settings()
    retr = build_plot_registry(s).get("wu_ming_zhe")
    oracle = E.build_oracle(retr.corpus, cases)
    top_prod = int(getattr(s, "plot_max_chunks", 6))
    lf_prod = int(getattr(s, "plot_lexical_fallback", 2))

    out: list[str] = []

    def p(*a):
        line = " ".join(str(x) for x in a)
        out.append(line)
        print(line, flush=True)

    n = len(cases)
    agg = {"b_inject": 0, "x_inject": 0, "b_strict": 0, "x_strict": 0,
           "b_top2": 0, "x_top2": 0}
    lat: list[float] = []
    rows: list[dict] = []
    t_all = time.time()

    for item in cases:
        qid = str(item["id"])
        full = oracle[qid]["full"]
        # 完美扩展：把所有证据组的所有备选关键词拼到 query 后
        kws: list[str] = []
        for g in (item.get("evidence") or []):
            kws.extend(str(k) for k in (g if isinstance(g, list) else [g]))
        expanded = dict(item)
        expanded["q"] = f"{item['q']} {' '.join(kws)}".strip()

        cap: dict[str, list] = {}

        def grab_base(q, chunks):
            cap["b"] = chunks
            return chunks

        def grab_x(q, chunks):
            cap["x"] = chunks
            return chunks

        rb = E.evaluate_case(retr, item, oracle[qid], top_prod, lf_prod, BUDGET,
                             chunks_transform=grab_base)
        t0 = time.perf_counter()
        rx = E.evaluate_case(retr, expanded, oracle[qid], top_prod, lf_prod, BUDGET,
                             chunks_transform=grab_x)
        lat.append((time.perf_counter() - t0) * 1000)

        agg["b_inject"] += bool(rb.get("inject_pass"))
        agg["x_inject"] += bool(rx.get("inject_pass"))
        agg["b_strict"] += bool(rb.get("strict_pass"))
        agg["x_strict"] += bool(rx.get("strict_pass"))
        agg["b_top2"] += top2_hit(cap.get("b") or [], full)
        agg["x_top2"] += top2_hit(cap.get("x") or [], full)
        rows.append({"id": qid,
                     "n_groups": len(item.get("evidence") or []),
                     "b_inject": bool(rb.get("inject_pass")),
                     "x_inject": bool(rx.get("inject_pass")),
                     "b_top2": bool(top2_hit(cap.get("b") or [], full)),
                     "x_top2": bool(top2_hit(cap.get("x") or [], full))})

    p("=" * 78)
    p(f"B4 天花板测试（完美查询扩展，作弊上界）｜n={n}｜耗时 {(time.time() - t_all) / 60:.1f} min")
    p("=" * 78)
    p(f"{'指标':<14}{'现状':>10}{'完美扩展':>12}{'Δ':>10}")
    p("-" * 78)
    for key, label in (("inject", "inject_pass"), ("strict", "strict_pass"),
                       ("top2", "top2_hit")):
        b, x = agg[f"b_{key}"] / n, agg[f"x_{key}"] / n
        p(f"{label:<14}{b:>10.4f}{x:>12.4f}{x - b:>+10.4f}")
    p("-" * 78)

    # 分层：单组 vs 多组
    single = [r for r in rows if r["n_groups"] == 1]
    multi = [r for r in rows if r["n_groups"] >= 2]
    p()
    p("分层 Δinject：")
    for label, sub in (("单组题", single), ("多组题", multi)):
        if not sub:
            continue
        d = (sum(r["x_inject"] for r in sub) - sum(r["b_inject"] for r in sub)) / len(sub)
        p(f"  {label}（{len(sub)} 题）{d:+.4f}")

    di = (agg["x_inject"] - agg["b_inject"]) / n
    p()
    p("=" * 78)
    p("判定")
    p("=" * 78)
    p(f"  完美查询扩展的 Δinject = {di:+.4f}（{agg['x_inject'] - agg['b_inject']:+d} 题）")
    if di >= 0.10:
        p("  ✅ 天花板很高 ⇒ B4 值得投入（真实实现会低于此值，但有空间）")
    elif di >= 0.03:
        p("  ⚠️ 天花板中等 ⇒ B4 可做，但需先验证「能否在不看答案的前提下猜中实体」")
    else:
        p("  ❌ 天花板太低 ⇒ 就算完美猜中实体也救不回来，B4 方向不成立")
        p("     （说明瓶颈不在「查询里有没有实体名」，而在排序/匹配本身）")

    (AUDIT / "_b4_ceiling.txt").write_text("\n".join(out), encoding="utf-8")
    (AUDIT / "b4_ceiling.json").write_text(json.dumps(rows, ensure_ascii=False, indent=1),
                                           encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
