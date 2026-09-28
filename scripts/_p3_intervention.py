# -*- coding: utf-8 -*-
"""目标① 干预实验（聚焦 14 道池内 miss + 全量控制组）。

诊断（scripts/_miss_p3_triage.py）给出三类：
  4 零种子 / 3 跨篇 / **7 同篇但通道未带回**（最可治）

本脚本测试三种**最小**干预：
  I1 lex_top 加大（30 → 60/100）：扩大词面候选
  I2 章节通道：把"种子实体所在章节"的块作为独立 RRF 通道
     （针对 7 道同篇题 —— gold 与种子同篇却未进池）
  I3 组合 I1+I2

判据（预注册）：
  - 主判据：**全量 196 题** hit@6 不低于现状（无回归）；
  - 副判据：14 道 miss 中进池（top-30）与进 top-6 的题数增加；
  - 任一干预若造成全量回归则否决。

为控制耗时，用 300cn 采集文件里已存的 qvecs 复现向量通道（相对比较有效）。
"""
from __future__ import annotations

import argparse
import json
import math
import re
import sys
from collections import Counter, defaultdict
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


def retrieve(rets, query, qvec, top_k, lex, w_lex, lex_top,
             chap_chunks=None, w_chap=0.0):
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
        if w_chap > 0 and chap_chunks is not None:
            # 章节通道：种子实体出现过的章节里的块，按词面分排序取前 N
            chaps = set()
            for s_ in seeds:
                for cid in rets.graph.entities[s_.eid].chunk_ids:
                    ch = rets.chunks[cid].chapter_title
                    chaps.add(ch)
            cand = [cid for cid, c in rets.chunks.items() if c.chapter_title in chaps]
            if cand:
                lexmap = dict(lex.search(query, 10 ** 6))
                scored = [(cid, lexmap.get(cid, 0.0)) for cid in cand]
                scored.sort(key=lambda kv: (-kv[1], kv[0]))
                channels["chapter"] = {cid: sc for cid, sc in scored[:60] if sc > 0}
    if qvec is not None:
        channels["vector"] = rets.vector_channel(qvec, 30)
    weights = {"lex": w_lex}
    if w_chap > 0:
        weights["chapter"] = w_chap
    evs = rets.rrf_fuse(channels, weights=weights, top_n=max(top_k * 4, 24))
    res.evidence = evs
    return res


def run(kb, lex, cases, qvecs, w_lex, lex_top, w_chap=0.0, top_k=6):
    hits, perq = 0, {}
    for c in cases:
        clear_ppr_cache()
        res = retrieve(kb.retriever, c["q"], qvecs.get(c["qid"]), top_k,
                       lex, w_lex, lex_top, None, w_chap)
        hit = False
        rr = 0.0
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
    ap.add_argument("--set", default=str(ROOT / "data/knowledge/_audit/rag_testset_300_cn.json"))
    ap.add_argument("--collect", default=str(ROOT / "data/compendium_rag/reports/rank_collect_v6c300_top30.json"))
    args = ap.parse_args()

    s = get_settings()
    kb = P.load_kb(s)
    print("[build] lex index …")
    lex = LexIndex(kb.chunks)
    install_fast_ppr()

    cd = json.loads(Path(args.collect).read_text(encoding="utf-8"))
    qvecs = cd.get("qvecs") or {}
    cases = load_cases(Path(args.set))
    ans = "\n".join(c.text for c in kb.chunks)
    cases = [c for c in cases if any(k in ans for k in c["keywords"])]
    miss_cases = [c for c in cases if c["qid"] in MISS]
    print(f"[tset] answerable n={len(cases)}  其中 MISS n={len(miss_cases)}")

    variants = [
        ("现状 lex_top=30 w_lex=1.0", dict(w_lex=1.0, lex_top=30, w_chap=0.0)),
        ("I1 lex_top=60", dict(w_lex=1.0, lex_top=60, w_chap=0.0)),
        ("I1 lex_top=100", dict(w_lex=1.0, lex_top=100, w_chap=0.0)),
        ("I2 章节通道 w=0.5", dict(w_lex=1.0, lex_top=30, w_chap=0.5)),
        ("I2 章节通道 w=1.0", dict(w_lex=1.0, lex_top=30, w_chap=1.0)),
        ("I3 lex60+chap0.5", dict(w_lex=1.0, lex_top=60, w_chap=0.5)),
    ]
    base = None
    for label, kw in variants:
        h, perq = run(kb, lex, cases, qvecs, **kw)
        n = len(cases)
        if base is None:
            base = perq
        up = [q for q in base if not base[q][0] and perq[q][0]]
        dn = [q for q in base if base[q][0] and not perq[q][0]]
        print(f"\n[{label:26}] hit@6 {h}/{n} = {h / n:.4f}  up={len(up)} down={len(dn)}")
        if up:
            print(f"    up: {sorted(up)[:10]}")
        if dn:
            print(f"    down: {sorted(dn)[:10]}")
        # MISS 在三者中的表现
        mh = sum(1 for c in miss_cases if perq[c["qid"]][0])
        print(f"    14 道 miss 中命中 = {mh}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
