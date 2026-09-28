# -*- coding: utf-8 -*-
"""目标① 最后一测：7 道「语义可达却被融合压过」的 miss，能否靠 **提高向量通道
在 RRF 中的权重** 救回？

依据（scripts/_miss_vector_reach.py）：这 7 道 gold 在向量全库排 14–50，
但 RRF 只给 1/(60+rank) 的分，被 graph/mention/lex 的强候选压过 -> 融合权重问题。

判据（预注册）：
  - 若提高 vector 权重能救回其中若干道，且**全量 down=0** -> 值得落盘；
  - 若全量下降或零救回 -> 否决，路由到 P4（交叉编码器）。
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

from compendium_rag import pipeline as P                      # noqa: E402
from compendium_rag.config import get_settings                # noqa: E402
from compendium_rag.retriever import RetrievalResult          # noqa: E402
from _r5_variant_scan import clear_ppr_cache, install_fast_ppr  # noqa: E402
from _lex_channel_full import LexIndex, load_cases            # noqa: E402

MISS = ["R001", "R005", "R012", "R094", "R127", "R170", "R171",
        "R180", "R244", "R248", "R273", "R292", "R297", "R298"]
# 语义可达的 7 道（gold 向量排名 ≤100）
REACHABLE = ["R001", "R180", "R244", "R248", "R273", "R292", "R298"]


def retrieve(rets, query, qvec, top_k, lex, w_lex, w_vec, vector_top=50):
    res = RetrievalResult(query=query)
    seeds = rets.link(query, top_k=6)
    seeds = [s for s in seeds if s.score >= 0.34] or seeds[:2]
    res.seeds = seeds
    channels = {"lex": dict(lex.search(query, 30))}
    if seeds:
        gc, edges = rets.graph_channel(seeds)
        res.edges = edges
        channels["graph"] = gc
        channels["mention"] = rets.mention_channel(seeds)
    if qvec is not None:
        channels["vector"] = rets.vector_channel(qvec, vector_top)
    evs = rets.rrf_fuse(channels, weights={"lex": w_lex, "vector": w_vec},
                        top_n=max(top_k * 4, 24))
    res.evidence = evs
    return res


def run(kb, lex, cases, qvecs, w_lex, w_vec, vector_top=50, top_k=6):
    hits, perq = 0, {}
    for c in cases:
        clear_ppr_cache()
        res = retrieve(kb.retriever, c["q"], qvecs.get(c["qid"]), top_k,
                       lex, w_lex, w_vec, vector_top)
        hit, rr = False, 0.0
        for rank, e in enumerate(res.evidence[:top_k], start=1):
            ch = kb.retriever.chunks.get(e.chunk_id)
            if not ch:
                continue
            b = f"{ch.text}\n{ch.chapter_title}\n{ch.scene_title}\n{ch.part_title}"
            if any(k in b for k in c["keywords"]):
                hit, rr = True, 1.0 / rank
                break
        hits += hit
        perq[c["qid"]] = (hit, rr)
    return hits, perq


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--collect", default=str(ROOT / "data/compendium_rag/reports/rank_collect_v6c300_top30.json"))
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

    base = None
    for wv in (1.0, 2.0, 3.0, 5.0):
        h, perq = run(kb, lex, cases, qvecs, 1.0, wv)
        n = len(cases)
        if base is None:
            base = perq
        up = [q for q in base if not base[q][0] and perq[q][0]]
        dn = [q for q in base if base[q][0] and not perq[q][0]]
        reach = [q for q in REACHABLE if perq[q][0]]
        tag = "（现状）" if wv == 1.0 else ""
        print(f"\n[w_vector={wv:<4}] hit@6 {h}/{n} = {h/n:.4f}  up={len(up)} down={len(dn)} {tag}")
        print(f"    语义可达 7 道中命中: {len(reach)}/7 {reach}")
        if up:
            print(f"    up: {sorted(up)}")
        if dn:
            print(f"    down: {sorted(dn)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
