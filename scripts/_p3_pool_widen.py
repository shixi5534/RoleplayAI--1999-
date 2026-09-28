# -*- coding: utf-8 -*-
"""目标① 关键假设测试：**放宽喂给重排器的候选池** 能否救回「语义可达」的 miss？

机理（本轮实测推出的结构性结论）：
  RRF 是**纯排名制**融合：某候选若在**每个**通道都排 14 名开外，
  则无论权重怎么调，它都进不了 top-6（top-6 必然是该通道的前几名）。
  实测佐证：把 vector 权重提到 5.0，7 道语义可达题**依然 0 命中**，
  且全量 down 从 0 涨到 7 —— 权重不是解法。

  但 7 道题的 gold 在**向量全库排名 14–50**，即**方向是对的、只是被排名制挡住**。
  所以正解是：把 RRF 的候选池（top_n）放宽，再把整个池交给**打分制重排器**
  （其 `cos` 特征直接用余弦相似度，能把向量排名靠前的候选顶上来）。

判据（预注册）：
  - 若放宽池 + 冻结重排能让 7 道中若干道进入 top-6，且**全量不降** -> 值得落盘；
  - 否则路由到 P4（交叉编码器）。
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

from compendium_rag import pipeline as P                      # noqa: E402
from compendium_rag.config import get_settings                # noqa: E402
from compendium_rag.retriever import RetrievalResult          # noqa: E402
from _r5_variant_scan import clear_ppr_cache, install_fast_ppr  # noqa: E402
from _lex_channel_full import LexIndex, load_cases            # noqa: E402

REACHABLE = ["R001", "R180", "R244", "R248", "R273", "R292", "R298"]
MISS = ["R001", "R005", "R012", "R094", "R127", "R170", "R171",
        "R180", "R244", "R248", "R273", "R292", "R297", "R298"]


def build_pool(rets, query, qvec, lex, top_n, vector_top=50):
    """返回 (chunk_id, 通道分) 的加宽候选池（RRF 序）。"""
    seeds = rets.link(query, top_k=6)
    seeds = [s for s in seeds if s.score >= 0.34] or seeds[:2]
    channels = {"lex": dict(lex.search(query, 30))}
    if seeds:
        gc, _ = rets.graph_channel(seeds)
        channels["graph"] = gc
        channels["mention"] = rets.mention_channel(seeds)
    if qvec is not None:
        channels["vector"] = rets.vector_channel(qvec, vector_top)
    evs = rets.rrf_fuse(channels, weights={"lex": 1.0}, top_n=top_n)
    return evs, seeds


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--collect", default=str(ROOT / "data/compendium_rag/reports/rank_collect_v6c300_top30.json"))
    ap.add_argument("--pool", type=int, default=60)
    args = ap.parse_args()

    s = get_settings()
    kb = P.load_kb(s)
    print("[build] lex index …")
    lex = LexIndex(kb.chunks)
    install_fast_ppr()
    qvecs = (json.loads(Path(args.collect).read_text(encoding="utf-8")).get("qvecs") or {})
    cases = load_cases(ROOT / "data/knowledge/_audit/rag_testset_300_cn.json")
    ans = "\n".join(c.text for c in kb.chunks)
    cases = [c for c in cases if any(k in ans for k in c["keywords"])]

    # 用冻结的 v6 重排权重给候选打分：需与 lab 的特征口径一致，
    # 这里改为「直接测池覆盖」——先看放宽池后 gold 是否进池（这是重排的前提）。
    print(f"\n=== 放宽 RRF 池到 top_n={args.pool} 后，gold 是否进池 ===")
    print(f"{'qid':6}{'池内gold排名':>12}   （旧池 top_n=24）")
    print("-" * 56)
    inpool_new = inpool_old = 0
    detail = {}
    for c in cases:
        clear_ppr_cache()
        evs_new, _ = build_pool(kb.retriever, c["q"], qvecs.get(c["qid"]), lex, args.pool)
        evs_old, _ = build_pool(kb.retriever, c["q"], qvecs.get(c["qid"]), lex, 24)
        def rank_of(evs):
            for i, e in enumerate(evs, 1):
                ch = kb.retriever.chunks.get(e.chunk_id)
                if not ch:
                    continue
                b = f"{ch.text}\n{ch.chapter_title}\n{ch.scene_title}\n{ch.part_title}"
                if any(k in b for k in c["keywords"]):
                    return i
            return None
        rn, ro = rank_of(evs_new), rank_of(evs_old)
        detail[c["qid"]] = {"new": rn, "old": ro}
        if rn:
            inpool_new += 1
        if ro:
            inpool_old += 1
        if c["qid"] in MISS:
            print(f"{c['qid']:6}{str(rn):>12}   old={ro}")

    n = len(cases)
    print(f"\n全量 {n} 题：进池 gold")
    print(f"  旧池 top_n=24 : {inpool_old}/{n} = {inpool_old/n:.4f}")
    print(f"  新池 top_n={args.pool}: {inpool_new}/{n} = {inpool_new/n:.4f}   (+{inpool_new-inpool_old})")
    print(f"\n14 道 miss 中，新池进池数 = {sum(1 for q in MISS if detail.get(q,{}).get('new'))}/14")
    print(f"  其中旧池未进、新池进入的: "
          f"{[q for q in MISS if detail.get(q,{}).get('new') and not detail.get(q,{}).get('old')]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
