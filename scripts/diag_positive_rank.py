# -*- coding: utf-8 -*-
"""逐题正例位次归因（P0-3 的可交付版本，**零生产改动**）。

为什么不用改 trace
    需求是「每题输出候选池大小、正例是否在池、正例的融合排名、返回情况」。
    关键洞察：**融合后的候选池本身可直接观测**——
    `retrieve(top_chunks=100)` 返回的就是融合列表（实测上限 28 块、中位 22），
    也就是"截断前的池子"。所以不需要动生产代码就能拿到融合排名。
    （逐通道的 BM25/向量**原始**排名仍需在通道层加埋点，另立任务。）

每题输出一条记录
    pool_size            候选池块数
    group_ranks[]        每个证据组在池中的最佳位次（0 = 不在池）
    full_rank            首个「单块覆盖全部证据组」的块在池中的位次（0 = 池中没有）
    final_rank           同一个块在生产返回列表（top=6+2）中的位次（0 = 没返回）
    inject_pass          evaluate_case 的产品口径判定
    verdict              四类归因结论（见下）

四类归因（与方案 §二 对应）
    A 不在候选池        → full_rank == 0  ⇒ 修查询理解 / 索引切块
    B 在池但没返回      → full_rank > 返回上限 ⇒ 修融合 / top-k
    C 返回了但太靠后    → final_rank > 2  ⇒ 修排序（产品只装得下约 2 块）
    D 位次够前却仍失败  → final_rank <= 2 但 inject 失败 ⇒ 查评估口径 / 装配预算
    OK 通过

用法：.venv/Scripts/python.exe -X utf8 scripts/diag_positive_rank.py
"""
from __future__ import annotations

import json
import sys
import time
import traceback
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

import eval_plot_rag as E  # noqa: E402
from roleplay.config import get_settings  # noqa: E402
from roleplay.core.knowledge.factory import build_plot_registry  # noqa: E402

AUDIT = ROOT / "data" / "knowledge" / "_audit"
TESTSET = AUDIT / "rag_testset_300_clean.json"
LOG = AUDIT / "_positive_rank.txt"
HB = AUDIT / "_positive_rank_heartbeat.txt"
POOL = 100          # 请求 100，实际拿到融合池全量
BUDGET = 2400


def beat(msg: str) -> None:
    with HB.open("a", encoding="utf-8") as f:
        f.write(f"{time.strftime('%H:%M:%S')} {msg}\n")


def main() -> int:
    out: list[str] = []
    HB.write_text(f"start {time.strftime('%H:%M:%S')}\n", encoding="utf-8")

    def p(*a):
        line = " ".join(str(x) for x in a)
        out.append(line)
        print(line, flush=True)

    cases = json.loads(TESTSET.read_text(encoding="utf-8"))
    s = get_settings()
    retr = build_plot_registry(s).get("wu_ming_zhe")
    oracle = E.build_oracle(retr.corpus, cases)
    by_hash = {c.hash: c.text for c in retr.corpus.chunks}
    top_prod = int(getattr(s, "plot_max_chunks", 6))
    lf_prod = int(getattr(s, "plot_lexical_fallback", 2))
    n_ret = top_prod + lf_prod

    p("=" * 88)
    p(f"逐题正例位次归因｜n={len(cases)}｜生产返回上限 {n_ret}（{top_prod}+{lf_prod}）"
      f"｜池探测 top={POOL}")
    p("=" * 88)

    rows: list[dict] = []
    t0 = time.time()
    for i, item in enumerate(cases):
        if i % 25 == 0:
            beat(f"case {i}/{len(cases)}")
        qid = str(item["id"])
        groups = item.get("evidence") or []

        pool = retr.retrieve(item["q"], top_chunks=POOL, lexical_fallback=0)
        pool_h = [E.chunk_hash(c.text) for c in pool]

        group_ranks: list[int] = []
        for g in groups:
            kws = [str(k) for k in (g if isinstance(g, list) else [g])]
            rk = 0
            for idx, h in enumerate(pool_h, 1):
                txt = by_hash.get(h, "")
                if any(kw in txt for kw in kws):
                    rk = idx
                    break
            group_ranks.append(rk)

        # 首个「单块覆盖全部证据组」的位次
        full_rank = 0
        for idx, h in enumerate(pool_h, 1):
            txt = by_hash.get(h, "")
            if groups and all(any(kw in txt for kw in
                                  (g if isinstance(g, list) else [g])) for g in groups):
                full_rank = idx
                break

        final = retr.retrieve(item["q"], top_chunks=top_prod, lexical_fallback=lf_prod)
        final_h = [E.chunk_hash(c.text) for c in final]
        final_rank = 0
        for idx, h in enumerate(final_h, 1):
            txt = by_hash.get(h, "")
            if groups and all(any(kw in txt for kw in
                                  (g if isinstance(g, list) else [g])) for g in groups):
                final_rank = idx
                break

        row = E.evaluate_case(retr, item, oracle[qid], top_prod, lf_prod, BUDGET)
        inject = bool(row.get("inject_pass"))

        if inject:
            verdict = "OK"
        elif full_rank == 0:
            verdict = "A_不在候选池"
        elif full_rank > n_ret:
            verdict = "B_在池但没返回"
        elif final_rank > 2:
            verdict = "C_返回了但太靠后"
        else:
            verdict = "D_位次够前却仍失败"

        rows.append({"id": qid, "n_groups": len(groups), "pool_size": len(pool),
                     "group_ranks": group_ranks, "full_rank": full_rank,
                     "final_rank": final_rank, "inject_pass": inject,
                     "strict_pass": bool(row.get("strict_pass")),
                     "verdict": verdict})

    n = len(rows)
    cnt = Counter(r["verdict"] for r in rows)
    ok = cnt.get("OK", 0)
    p()
    p("-" * 88)
    p(f"{'归因结论':<22}{'题数':>6}{'占失分':>10}{'占全量':>10}{'下一步修哪里':>28}")
    p("-" * 88)
    NEXT = {
        "A_不在候选池": "查询理解 / 索引切块",
        "B_在池但没返回": "融合 / top-k",
        "C_返回了但太靠后": "排序（只装得下约 2 块）",
        "D_位次够前却仍失败": "评估口径 / 装配预算",
    }
    failed = n - ok
    for v in ("A_不在候选池", "B_在池但没返回", "C_返回了但太靠后", "D_位次够前却仍失败"):
        c = cnt.get(v, 0)
        share = (c / failed) if failed else 0.0
        p(f"{v:<22}{c:>6}{share:>10.1%}{c / n:>10.1%}{NEXT[v]:>28}")
    p("-" * 88)
    p(f"{'OK（inject 通过）':<22}{ok:>6}{'—':>10}{ok / n:>10.1%}")
    p(f"{'合计':<22}{n:>6}{'—':>10}{1.0:>10.1%}")
    p("=" * 88)

    pool_sizes = sorted(r["pool_size"] for r in rows)
    p()
    p(f"候选池大小：中位 {pool_sizes[n // 2]}｜最小 {pool_sizes[0]}｜最大 {pool_sizes[-1]}")
    for lo, hi in ((0, 5), (6, 10), (11, 20), (21, 30)):
        p(f"  {lo:>2}-{hi:<2} 块：{sum(1 for x in pool_sizes if lo <= x <= hi):>3} 题")
    p()
    p(f"耗时 {(time.time() - t0) / 60:.1f} min")

    LOG.write_text("\n".join(out), encoding="utf-8")
    (AUDIT / "positive_rank.json").write_text(json.dumps(rows, ensure_ascii=False, indent=1),
                                              encoding="utf-8")
    beat("完成")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except SystemExit:
        raise          # SystemExit 是正常退出，别记成异常
    except BaseException:  # noqa: BLE001
        with LOG.open("a", encoding="utf-8") as f:
            f.write("\n[TRACEBACK]\n" + traceback.format_exc())
        raise
