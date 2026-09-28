# -*- coding: utf-8 -*-
"""目标① 干预测试：放宽向量通道 vector_top（30 → 50/100/200）。

依据（scripts/_miss_vector_reach.py）：14 道 miss 中 **7 道**的 gold 在
向量全库排名 8–50，而当前 vector_top=30 把它们截断了 —— 这是**可救**的一类。

判据（预注册）：
  - 主判据：全量 196 题 hit@6 提升且 **down 尽量为 0**；
  - 副判据：14 道 miss 中命中数增加；
  - 风险：放宽向量池会引入弱相关候选，可能拉低既有题的排序（须逐题看 down）。

用采集文件已存 qvecs 复现向量通道（相对比较有效，绝对数字以正式 eval300 为准）。
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


def retrieve(rets, query, qvec, top_k, lex, w_lex, lex_top, vector_top):
    res = RetrievalResult(query=query)
    seeds = rets.link(query, top_k=6)
    seeds = [s for s in seeds if s.score >= 0.34] or seeds[:2]
    res.seeds = seeds
    channels = {"lex": dict(lex.search(query, lex_top))}
    if seeds:
        gc, edges = rets.graph_channel(seeds)
        res.edges = edges
        channels["graph"] = gc
        channels["mention"] = rets.mention_channel(seeds)
    if qvec is not None:
        channels["vector"] = rets.vector_channel(qvec, vector_top)
    evs = rets.rrf_fuse(channels, weights={"lex": w_lex}, top_n=max(top_k * 4, 24))
    res.evidence = evs
    return res


def run(kb, lex, cases, qvecs, w_lex, lex_top, vector_top, top_k=6):
    hits, perq = 0, {}
    for c in cases:
        clear_ppr_cache()
        res = retrieve(kb.retriever, c["q"], qvecs.get(c["qid"]), top_k,
                       lex, w_lex, lex_top, vector_top)
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

    cd = json.loads(Path(args.collect).read_text(encoding="utf-8"))
    qvecs = cd.get("qvecs") or {}
    cases = load_cases(ROOT / "data/knowledge/_audit/rag_testset_300_cn.json")
    ans = "\n".join(c.text for c in kb.chunks)
    cases = [c for c in cases if any(k in ans for k in c["keywords"])]
    miss_cases = [c for c in cases if c["qid"] in MISS]
    print(f"[tset] answerable n={len(cases)}")

    base = None
    for vt in (30, 50, 100, 200):
        h, perq = run(kb, lex, cases, qvecs, 1.0, 30, vt)
        n = len(cases)
        if base is None:
            base = perq
        up = [q for q in base if not base[q][0] and perq[q][0]]
        dn = [q for q in base if base[q][0] and not perq[q][0]]
        mh = sum(1 for c in miss_cases if perq[c["qid"]][0])
        tag = "（现状）" if vt == 30 else ""
        print(f"\n[vector_top={vt:<4}] hit@6 {h}/{n} = {h / n:.4f}  "
              f"up={len(up)} down={len(dn)}  MISS命中={mh}/14 {tag}")
        if up:
            print(f"    up: {sorted(up)}")
        if dn:
            print(f"    down: {sorted(dn)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
