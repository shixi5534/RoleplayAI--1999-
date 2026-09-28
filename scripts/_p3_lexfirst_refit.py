# -*- coding: utf-8 -*-
"""P3/fusion restructure: refit reranker on the NEW pool order, then freeze -> blind.

Why refit is required:
  _fusion_restructure_accept.py plugged m2_union(3) into a reranker that had been
  fitted on the OLD pool. Pool composition AND order both changed, so the old
  weights no longer match: blind 0.8786 -> 0.9223 (up) but 300cn 0.8673 -> 0.8418 (down).

Protocol (must be followed to avoid self-deception):
  1. Build NEW pools with m2_union(L) for both sets (same rule).
  2. Tune + fit weights on 300cn ONLY.
  3. Freeze that config and apply to blind 206 (held out).
  4. Report overfitting check (2-fold) + safety line.

Acceptance (pre-registered):
  - blind production >= 0.8786 (no regression)
  - 300cn production >= 0.8673 (no regression)
  BOTH must hold for a real improvement.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

from compendium_rag import pipeline as P                        # noqa: E402
from compendium_rag.config import get_settings                  # noqa: E402
from _lex_channel_full import LexIndex, load_cases              # noqa: E402
from _r5_variant_scan import clear_ppr_cache, install_fast_ppr   # noqa: E402
from _fusion_restructure import channels_for, ranked_ids        # noqa: E402

spec = importlib.util.spec_from_file_location("lab", ROOT / "scripts/_rank_rerank_lab.py")
lab = importlib.util.module_from_spec(spec)
spec.loader.exec_module(lab)

FEATS = lab.BASE_FEATURES


def build_pool(kb, lex, q, qvec, top_n=30, lex_first=3):
    """m2_union(lex_first): lex top-L first, then fused order, then rest of lex (dedup)."""
    clear_ppr_cache()
    lex_scored = dict(lex.search(q, 30))
    ch, _ = channels_for(kb.retriever, q, qvec)
    ch["lex"] = lex_scored
    fused = kb.retriever.rrf_fuse(ch, weights={"lex": 1.0}, top_n=max(top_n, 24))
    fused_ids = [e.chunk_id for e in fused]
    lex_ids = ranked_ids(lex_scored, top_n)
    out, seen = [], set()
    for cid in lex_ids[:lex_first] + fused_ids + lex_ids:
        if cid and cid not in seen:
            seen.add(cid)
            out.append(cid)
    return out[:top_n]


def build_ZG(kb, lex, cases, qv, fb, pool, lex_first):
    Zs, Gs, qids = [], [], []
    for c in cases:
        qvec = qv.get(c["qid"])
        ids = build_pool(kb, lex, c["q"], qvec, pool, lex_first)
        if len(ids) < pool:
            ids += [ids[-1]] * (pool - len(ids))
        Z1, _ = fb.question(c["q"], qvec, [{"chunk_id": x} for x in ids], kb.retriever.link)
        Zs.append(Z1)
        row = []
        for cid in ids:
            ch = kb.retriever.chunks.get(cid)
            b = (f"{ch.text}\n{ch.chapter_title}\n{ch.scene_title}\n{ch.part_title}"
                 if ch else "")
            row.append(any(k in b for k in c["keywords"]))
        Gs.append(row)
        qids.append(c["qid"])
    return np.stack(Zs), np.array(Gs, dtype=bool), qids


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--lex-first", type=int, default=3)
    ap.add_argument("--pool", type=int, default=30)
    args = ap.parse_args()

    s = get_settings()
    kb = P.load_kb(s)
    print("[build] lex index ...")
    lex = LexIndex(kb.chunks)
    install_fast_ppr()
    fb = lab.FeatureBuilder(kb)
    pool = args.pool

    qv = {}
    for f in ("rank_collect_v6c300_top30.json", "rank_collect_v6cblind_top30.json"):
        p = ROOT / "data/compendium_rag/reports" / f
        if p.exists():
            qv.update(json.loads(p.read_text(encoding="utf-8")).get("qvecs") or {})

    ans = "\n".join(c.text for c in kb.chunks)
    c300 = [c for c in load_cases(ROOT / "data/knowledge/_audit/rag_testset_300_cn.json")
            if any(k in ans for k in c["keywords"])]
    blind = [c for c in load_cases(ROOT / "data/knowledge/_audit/blind_v1/questions_strict.json")
             if any(k in ans for k in c["keywords"])]

    print(f"[cfg] m2_union(lex_first={args.lex_first}) pool={pool}")
    print("[build] 300cn pool/features ...")
    Z3, G3, q3 = build_ZG(kb, lex, c300, qv, fb, pool, args.lex_first)
    base_perm = np.tile(np.arange(pool), (len(q3), 1))
    base3 = lab.metrics(base_perm, G3, pool)
    base_hit6, _a, _b, _c = lab.eval_perm(base_perm, G3, pool)
    print(f"  300cn pool-order hit@6 = {base3['hit6']}")

    print("[fit] sweep on 300cn ...")
    w_eq = np.ones(Z3.shape[2])
    idx = np.arange(len(q3))
    configs = lab.sweep_configs(Z3, G3, idx, q3, base_hit6, {"eq": w_eq}, FEATS, pool)
    best = lab.pick_best(configs)
    print(f"  chosen = {best['name']}  hit@6(300cn) = {best['hit6']}")

    # 2-fold overfitting check (fast substitute for full LOO-CV)
    print("[cv] 2-fold check ...")
    n = len(q3)
    half = n // 2
    ia, ib = np.arange(half), np.arange(half, n)
    cA = lab.sweep_configs(Z3, G3, ia, [q3[i] for i in ia], base_hit6[ia],
                           {"eq": w_eq}, FEATS, pool)
    bA = lab.pick_best(cA)
    wA = np.array([float(bA["weights"].get(f, 0.0)) for f in FEATS])
    pA = lab.apply_policy(bA["policy"], bA["params"][list(bA["params"])[0]], Z3[ib] @ wA, pool)
    mA = lab.metrics(pA, G3[ib], pool)
    print(f"  A-fold pick {bA['name']} -> B-fold hit {mA['hit6']}")

    print("[build] blind pool/features ...")
    Zb, Gb, qb = build_ZG(kb, lex, blind, qv, fb, pool, args.lex_first)
    baseB = lab.metrics(np.tile(np.arange(pool), (len(qb), 1)), Gb, pool)
    wbest = np.array([float(best["weights"].get(f, 0.0)) for f in FEATS])
    pkey = list(best["params"])[0]
    permb = lab.apply_policy(best["policy"], best["params"][pkey], Zb @ wbest, pool)
    mb = lab.metrics(permb, Gb, pool)
    hb, _a, _b, _c = lab.eval_perm(np.tile(np.arange(pool), (len(qb), 1)), Gb, pool)
    up, down = lab.flips(permb, Gb, qb, hb, pool)

    print()
    print("=" * 72)
    print("RESULT: new pool + refit reranker (frozen, applied to blind)")
    print("=" * 72)
    print(f"  300cn : pool {base3['hit6']}  ->  rerank {best['hit6']}   (2-fold {mA['hit6']})")
    print(f"  blind : pool {baseB['hit6']}  ->  rerank {mb['hit6']}   up={len(up)} down={len(down)}")
    print(f"  prev  : 300cn 0.8673 / blind 0.8786")
    ok3 = best["hit6"] >= 0.8673
    okb = mb["hit6"] >= 0.8786
    print(f"  300cn no-regress: {'PASS' if ok3 else 'FAIL'}   blind no-regress: {'PASS' if okb else 'FAIL'}")

    out = {"lex_first": args.lex_first, "pool": pool,
           "300cn": {"pool_hit6": base3["hit6"], "rerank_hit6": best["hit6"],
                     "fold_check": mA["hit6"]},
           "blind206": {"pool_hit6": baseB["hit6"], "rerank_hit6": mb["hit6"],
                        "hit10": mb["hit10"], "up": len(up), "down": len(down),
                        "up_qids": up[:25], "down_qids": down[:25]},
           "chosen": {k: best[k] for k in ("name", "policy", "params", "weights")},
           "prev": {"300cn": 0.8673, "blind206": 0.8786},
           "verdict": {"300cn_no_regress": bool(ok3), "blind_no_regress": bool(okb)}}
    p = ROOT / "data/compendium_rag/reports/_p3_lexfirst_refit.json"
    p.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"-> {p}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
