# -*- coding: utf-8 -*-
"""三线对照总表：lex=0 (BASELINE_v5 口径) vs lex=1 (v6 候选)。"""
import json
from pathlib import Path

R = Path("data/compendium_rag/reports")


def s(name):
    d = json.loads((R / name).read_text(encoding="utf-8"))
    o = {}
    for m in ("full", "graph_only"):
        rows = [x for x in d["rows"] if x.get("mode") == m and x.get("answerable")]
        if rows:
            o[m] = (sum(1 for x in rows if x.get("hit")), len(rows))
    un = [x for x in d["rows"] if x.get("mode") == "full" and not x.get("answerable")]
    o["unans"] = (sum(1 for x in un if x.get("hit")), len(un))
    rows = [x for x in d["rows"] if x.get("mode") == "full" and x.get("answerable")]
    o["grounded"] = (sum(1 for x in rows if x.get("grounded")), len(rows))
    return o


ROWS = [
    ("300cn  lex=0 (v5)", "eval_300cn_after_r5.json"),
    ("300cn  lex=1 (v6)", "eval_300cn_lex_tiebreak.json"),
    ("gen120 lex=0 (v5)", "eval_gen_recheck_postrebuild_20260927.json"),
    ("gen120 lex=1 (v6)", "eval_gen_lex_tiebreak.json"),
    ("blind206 lex=0", "eval_blind_lex_off.json"),
    ("blind206 lex=1 (v6)", "eval_blind_lex_tiebreak.json"),
]
print(f"{'口径':22}{'full':>18}{'graph_only':>18}{'unans':>10}{'grounded':>11}")
for lbl, f in ROWS:
    o = s(f)
    fu, go, un, gr = o["full"], o["graph_only"], o["unans"], o["grounded"]
    print(f"{lbl:22}{fu[0]:>5}/{fu[1]:<4}={fu[0]/fu[1]:.4f}"
          f"{go[0]:>4}/{go[1]:<4}={go[0]/go[1]:.4f}"
          f"{un[0]:>6}/{un[1]:<3}{gr[0]:>6}/{gr[1]:<4}")
