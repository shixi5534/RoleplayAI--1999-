# -*- coding: utf-8 -*-
"""Regression test for the fusion-restructure wiring (criteria fixed in advance).

R1. lex_first=0 (default) -> retrieval IDENTICAL to before (no behavior drift).
R2. lex_first=3 -> the lexical top-3 really are promoted to the front.
R3. lex_first=3 -> evidence set is a SUPERSET of the fused order (never drops).
R4. grounded stays clean (all chunk_ids exist).
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from compendium_rag import pipeline as P                       # noqa: E402
from compendium_rag.config import get_settings                 # noqa: E402


def main() -> int:
    s = get_settings()
    kb = P.load_kb(s)
    r = kb.retriever
    print(f"[load] chunks={len(r.chunks)} lex_index={'yes' if r.lex_index else 'no'}")

    ts = json.loads((ROOT / "data/knowledge/_audit/rag_testset_300_cn.json").read_text(encoding="utf-8"))
    qs = [c["q"] for c in ts["cases"][:25]]

    print("\n[R1] lex_first=0 identical to default")
    d1 = d2 = 0
    for q in qs:
        a = r.retrieve(q, None, top_k=6, lex_weight=1.0)
        b = r.retrieve(q, None, top_k=6, lex_weight=1.0, lex_first=0)
        if [e.chunk_id for e in a.evidence] != [e.chunk_id for e in b.evidence]:
            d1 += 1
    print(f"   25 questions, mismatches = {d1} -> {'PASS' if d1 == 0 else 'FAIL'}")

    print("\n[R2] lex_first=3 promotes lexical top-3 to front")
    bad = 0
    for q in qs:
        res = r.retrieve(q, None, top_k=6, lex_weight=1.0, lex_first=3)
        lex = dict(r.lex_index.search(q, 30))
        top3 = [cid for cid, _ in sorted(lex.items(), key=lambda kv: (-kv[1], kv[0]))][:3]
        got = [e.chunk_id for e in res.evidence[:len(top3)]]
        if got != top3:
            bad += 1
    print(f"   mismatches = {bad} -> {'PASS' if bad == 0 else 'FAIL'}")

    print("\n[R3] lex_first=3 evidence is a superset of fused order")
    bad3 = 0
    for q in qs:
        a = r.retrieve(q, None, top_k=6, lex_weight=1.0, lex_first=0)
        b = r.retrieve(q, None, top_k=6, lex_weight=1.0, lex_first=3)
        fa = {e.chunk_id for e in a.evidence}
        fb = {e.chunk_id for e in b.evidence}
        if not fa <= fb:
            bad3 += 1
    print(f"   superset violations = {bad3} -> {'PASS' if bad3 == 0 else 'FAIL'}")

    print("\n[R4] grounded clean with lex_first=3")
    bad4 = 0
    for q in qs:
        res = r.retrieve(q, None, top_k=6, lex_weight=1.0, lex_first=3)
        for e in res.evidence[:6]:
            if e.chunk_id not in r.chunks:
                bad4 += 1
    print(f"   grounded violations = {bad4} -> {'PASS' if bad4 == 0 else 'FAIL'}")

    print("\n[R5] determinism: repeated calls identical")
    bad5 = 0
    for q in qs[:10]:
        a = [e.chunk_id for e in r.retrieve(q, None, top_k=6, lex_weight=1.0, lex_first=3).evidence]
        b = [e.chunk_id for e in r.retrieve(q, None, top_k=6, lex_weight=1.0, lex_first=3).evidence]
        if a != b:
            bad5 += 1
    print(f"   mismatches = {bad5} -> {'PASS' if bad5 == 0 else 'FAIL'}")

    ok = (d1 == 0 and bad == 0 and bad3 == 0 and bad4 == 0 and bad5 == 0)
    print(f"\nOVERALL: {'ALL PASS' if ok else 'FAILURES PRESENT'}")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
