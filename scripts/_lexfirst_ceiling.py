# -*- coding: utf-8 -*-
"""Does the fusion restructure lift the POOL CEILING (hit@30) -- the bound on object 1?

Object 1 asks to compress the 14 in-pool hard misses; the ceiling is hit@30 = 0.9286.
Here we measure, on the official path (eval300-style), for each config:
  pool-order hit@6, hit@10, hit@30 (ceiling), and the in-pool miss list.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

from compendium_rag import pipeline as P                        # noqa: E402
from compendium_rag.config import get_settings                  # noqa: E402
from _lex_channel_full import LexIndex, load_cases              # noqa: E402
from _r5_variant_scan import clear_ppr_cache, install_fast_ppr   # noqa: E402
from _fusion_restructure import channels_for, ranked_ids        # noqa: E402


def ranked_for(kb, lex, q, qvec, lex_first, pool=30):
    clear_ppr_cache()
    lex_scored = dict(lex.search(q, 30))
    ch, _ = channels_for(kb.retriever, q, qvec)
    ch["lex"] = lex_scored
    fused = kb.retriever.rrf_fuse(ch, weights={"lex": 1.0}, top_n=max(pool, 24))
    fused_ids = [e.chunk_id for e in fused]
    if lex_first <= 0:
        return fused_ids[:pool]
    lex_ids = ranked_ids(lex_scored, pool)
    out, seen = [], set()
    for cid in lex_ids[:lex_first] + fused_ids + lex_ids:
        if cid and cid not in seen:
            seen.add(cid)
            out.append(cid)
    return out[:pool]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--set", default=str(ROOT / "data/knowledge/_audit/rag_testset_300_cn.json"))
    ap.add_argument("--collect", default=str(ROOT / "data/compendium_rag/reports/rank_collect_v6c300_top30.json"))
    ap.add_argument("--lex-first", default="0,3,6")
    args = ap.parse_args()

    s = get_settings()
    kb = P.load_kb(s)
    print("[build] lex index ...")
    lex = LexIndex(kb.chunks)
    install_fast_ppr()
    qv = (json.loads(Path(args.collect).read_text(encoding="utf-8")).get("qvecs") or {})
    cases = load_cases(Path(args.set))
    ans = "\n".join(c.text for c in kb.chunks)
    cases = [c for c in cases if any(k in ans for k in c["keywords"])]
    chunks = kb.retriever.chunks
    blob = {cid: f"{c.text}\n{c.chapter_title}\n{c.scene_title}\n{c.part_title}"
            for cid, c in chunks.items()}

    print(f"[tset] {Path(args.set).name} n={len(cases)}")
    for lf in [int(x) for x in args.lex_first.split(",")]:
        counts = {6: 0, 10: 0, 30: 0}
        miss = []
        for c in cases:
            ids = ranked_for(kb, lex, c["q"], qv.get(c["qid"]), lf, 30)
            first = next((i for i, cid in enumerate(ids, 1)
                          if any(k in blob.get(cid, "") for k in c["keywords"])), None)
            for k in counts:
                if first and first <= k:
                    counts[k] += 1
            if not first:
                miss.append(c["qid"])
        n = len(cases)
        print(f"\n[lex_first={lf}]")
        for k in (6, 10, 30):
            print(f"   hit@{k:<3} = {counts[k]}/{n} = {counts[k]/n:.4f}")
        print(f"   池内 miss ({len(miss)}): {miss}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
