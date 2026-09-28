# -*- coding: utf-8 -*-
"""关键发现验证与利用：**词面通道单独**是否强于**融合系统**？

线索（scripts/_p3_prf_rm3.py 的对照）：
  盲测 206 上，**lex 通道单独** hit@6 = 192/206 = **0.9320**，
  而融合后的正式系统（eval_blind_lex_tiebreak.json）full = 172/206 = **0.8350**。
  若成立，说明 graph/mention/vector 三通道在**稀释**词面通道的强候选。

本脚本在**生产路径**（full，含向量、含 RRF 融合）上：
  1. 复现"融合 vs lex-only"差距；
  2. 扫描 w_lex（权重只在 300cn 选，盲测**留出**）；
  3. 找出能逼近 lex-only 上限的配置。

判据（预注册）：300cn 选参；要求盲测**不降**才可采纳。
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

from compendium_rag import pipeline as P                       # noqa: E402
from compendium_rag.config import get_settings                 # noqa: E402
from compendium_rag.retriever import RetrievalResult           # noqa: E402
from _r5_variant_scan import clear_ppr_cache, install_fast_ppr  # noqa: E402
from _lex_channel_full import LexIndex, load_cases             # noqa: E402


def retrieve(rets, query, qvec, top_k, lex, w_lex, lex_top, mode):
    """mode: 'fused' 走四通道 RRF；'lexonly' 只用词面通道。"""
    res = RetrievalResult(query=query)
    if mode == "lexonly":
        res.evidence = rets.rrf_fuse({"lex": dict(lex.search(query, lex_top))},
                                     weights={"lex": 1.0}, top_n=max(top_k * 4, 24))
        return res
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
        channels["vector"] = rets.vector_channel(qvec, 30)
    res.evidence = rets.rrf_fuse(channels, weights={"lex": w_lex},
                                 top_n=max(top_k * 4, 24))
    return res


def ev(kb, lex, cases, qvecs, w_lex, lex_top, mode, top_k=6):
    chunks = kb.retriever.chunks
    hit6, per = 0, {}
    for c in cases:
        clear_ppr_cache()
        res = retrieve(kb.retriever, c["q"], qvecs.get(c["qid"]), top_k,
                       lex, w_lex, lex_top, mode)
        h = False
        for e in res.evidence[:top_k]:
            ch = chunks.get(e.chunk_id)
            if not ch:
                continue
            b = f"{ch.text}\n{ch.chapter_title}\n{ch.scene_title}\n{ch.part_title}"
            if any(k in b for k in c["keywords"]):
                h = True
                break
        hit6 += h
        per[c["qid"]] = h
    return hit6, len(cases), per


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--weights", default="1.0,2.0,4.0,8.0,16.0")
    ap.add_argument("--limit", type=int, default=0)
    args = ap.parse_args()

    s = get_settings()
    kb = P.load_kb(s)
    print("[build] lex index …")
    lex = LexIndex(kb.chunks)
    install_fast_ppr()

    q300 = (json.loads((ROOT / "data/compendium_rag/reports/rank_collect_v6c300_top30.json")
                       .read_text(encoding="utf-8")).get("qvecs") or {})
    qb = (json.loads((ROOT / "data/compendium_rag/reports/rank_collect_v6cblind_top30.json")
                     .read_text(encoding="utf-8")).get("qvecs") or {})
    ans = "\n".join(c.text for c in kb.chunks)
    c300 = [c for c in load_cases(ROOT / "data/knowledge/_audit/rag_testset_300_cn.json")
            if any(k in ans for k in c["keywords"])]
    blind = [c for c in load_cases(ROOT / "data/knowledge/_audit/blind_v1/questions_strict.json")
             if any(k in ans for k in c["keywords"])]
    if args.limit:
        c300, blind = c300[:args.limit], blind[:args.limit]
    print(f"[tset] 300cn n={len(c300)}  盲测 n={len(blind)}")

    # 1) lex-only 上限（两集）
    for name, cases, qv in (("300cn", c300, q300), ("盲测", blind, qb)):
        h, n, _ = ev(kb, lex, cases, qv, 0, 30, "lexonly")
        print(f"\n[lex-only 上限] {name}: {h}/{n} = {h/n:.4f}")

    # 2) 300cn 选 w_lex（fused）
    print("\n=== 300cn（调参集，fused）===")
    base = None
    best = None
    for w in [float(x) for x in args.weights.split(",")]:
        h, n, per = ev(kb, lex, c300, q300, w, 30, "fused")
        if base is None:
            base = per
        up = sum(1 for q in per if per[q] and not base[q])
        dn = sum(1 for q in base if base[q] and not per[q])
        if best is None or h > best[0]:
            best = (h, w)
        print(f"  w_lex={w:<5} {h}/{n} = {h/n:.4f}  up={up} down={dn}")

    print(f"\n  300cn 最优: hit={best[0]} w_lex={best[1]}")
    print("\n=== 盲测 206（留出集）===")
    h0, n0, p0 = ev(kb, lex, blind, qb, 1.0, 30, "fused")
    hb, nb, pb = ev(kb, lex, blind, qb, best[1], 30, "fused")
    hn, nn, pn = ev(kb, lex, blind, qb, 0, 30, "lexonly")
    up = sorted(q for q in pb if pb[q] and not p0[q])
    dn = sorted(q for q in p0 if p0[q] and not pb[q])
    print(f"  现状 w=1.0     : {h0}/{n0} = {h0/n0:.4f}")
    print(f"  300cn 选出 w={best[1]:<4}: {hb}/{nb} = {hb/nb:.4f}")
    print(f"  lex-only 上限  : {hn}/{nn} = {hn/nn:.4f}")
    print(f"  up={len(up)} {up[:8]}  down={len(dn)} {dn[:8]}")
    print(f"  Δ vs 现状 = {(hb-h0)/n0*100:+.2f}pt")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
