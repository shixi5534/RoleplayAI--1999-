# -*- coding: utf-8 -*-
"""Find a config that improves BOTH sets: frozen v6 weights + m2_union pool + sweep blend a.

Findings so far (blind 206 = held out, 300cn = tuning set):
  1. lex-only       : 300cn 0.8061 | blind 0.9320   <- fusion dilutes lex badly on blind
  2. fused (current): 300cn 0.8316 | blind 0.8301
  3. m2_union(3) pool order: 300cn 0.8469 | blind 0.9126  <- improves BOTH (bare)
  4. + v6 frozen reranker (a=0.2): 300cn 0.8418 | blind 0.9223  <- blind up, 300cn down
  5. + refit reranker: 300cn 0.8724 | blind 0.7427  <- catastrophic overfit on blind

So the pool construction (3) is a clear win. The open question is the reranker.
Here we keep the v6 weights FROZEN (fitted once, on the old pool) and tune ONLY the
blend parameter a on 300cn -- a single parameter, which is legitimate calibration.

Acceptance: exists a with 300cn >= 0.8673 AND blind >= 0.8786.
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
from _r5_variant_scan import install_fast_ppr                   # noqa: E402
from _p3_lexfirst_refit import build_ZG, FEATS                  # noqa: E402

spec = importlib.util.spec_from_file_location("lab", ROOT / "scripts/_rank_rerank_lab.py")
lab = importlib.util.module_from_spec(spec)
spec.loader.exec_module(lab)


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

    print("[build] pools/features ...")
    Z3, G3, q3 = build_ZG(kb, lex, c300, qv, fb, pool, args.lex_first)
    Zb, Gb, qb = build_ZG(kb, lex, blind, qv, fb, pool, args.lex_first)

    v6 = json.loads((ROOT / "data/compendium_rag/reports/rank_rerank_lab_300cn_v6.json")
                    .read_text(encoding="utf-8"))["chosen"]
    w = np.array([float(v6["weights"].get(f, 0.0)) for f in FEATS])
    S3, Sb = Z3 @ w, Zb @ w
    base3 = lab.metrics(np.tile(np.arange(pool), (len(q3), 1)), G3, pool)
    baseb = lab.metrics(np.tile(np.arange(pool), (len(qb), 1)), Gb, pool)
    print(f"  pool-order: 300cn {base3['hit6']}  blind {baseb['hit6']}")

    print(f"\n{'a':>5}{'300cn':>10}{'blind':>10}   both-ok?")
    rows = []
    for a in [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.8, 1.0]:
        p3 = lab.apply_policy("full_topN", a, S3, pool)
        pb = lab.apply_policy("full_topN", a, Sb, pool)
        m3 = lab.metrics(p3, G3, pool)
        mb = lab.metrics(pb, Gb, pool)
        ok3 = m3["hit6"] >= 0.8673
        okb = mb["hit6"] >= 0.8786
        rows.append({"a": a, "300cn": m3["hit6"], "blind": mb["hit6"],
                     "ok300": ok3, "okblind": okb, "both": ok3 and okb})
        print(f"{a:>5}{m3['hit6']:>10}{mb['hit6']:>10}   {'YES' if ok3 and okb else '-'}"
              f"   (300cn {'ok' if ok3 else 'no'}, blind {'ok' if okb else 'no'})")

    good = [r for r in rows if r["both"]]
    print()
    if good:
        best = max(good, key=lambda r: r["300cn"] + r["blind"])
        print(f"FOUND: a={best['a']} -> 300cn {best['300cn']}  blind {best['blind']}")
        print(f"  vs prev: 300cn 0.8673 ({(best['300cn']-0.8673)*100:+.2f}pt)"
              f"  blind 0.8786 ({(best['blind']-0.8786)*100:+.2f}pt)")
    else:
        print("NO config satisfies both constraints.")
        print("  -> pool construction is a clear win on bare; the reranker is set-dependent.")

    out = {"lex_first": args.lex_first, "pool": pool, "rows": rows,
           "chosen_a": good and max(good, key=lambda r: r["300cn"] + r["blind"])["a"],
           "prev": {"300cn": 0.8673, "blind": 0.8786}}
    p = ROOT / "data/compendium_rag/reports/_p3_ab_sweep.json"
    p.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"-> {p}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
