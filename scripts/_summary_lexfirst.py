# -*- coding: utf-8 -*-
"""汇总官方路径的 lex_first 前后对照（盲测 206 / 300cn）。"""
import json
import os
from pathlib import Path

R = Path("data/compendium_rag/reports")


def r(f):
    p = R / f
    if not p.exists():
        return None
    d = json.loads(p.read_text(encoding="utf-8"))
    o = {}
    for m in ("full", "graph_only"):
        rows = [x for x in d["rows"] if x.get("mode") == m and x.get("answerable")]
        if rows:
            o[m] = (sum(1 for x in rows if x.get("hit")), len(rows))
    un = [x for x in d["rows"] if x.get("mode") == "full" and not x.get("answerable")]
    o["unans"] = (sum(1 for x in un if x.get("hit")), len(un))
    return o


def show(title, rows):
    print(f"=== {title} ===")
    for lbl, f in rows:
        o = r(f)
        if not o:
            print(f"  {lbl:26} (missing)")
            continue
        fu, go, un = o["full"], o["graph_only"], o["unans"]
        print(f"  {lbl:26} full={fu[0]}/{fu[1]}={fu[0]/fu[1]:.4f}"
              f"  graph_only={go[0]}/{go[1]}={go[0]/go[1]:.4f}"
              f"  unans={un[0]}/{un[1]}")
    print()


show("盲测 206（官方路径，冷启动）", [
    ("lex=0 (v5)", "eval_blind_lex_off.json"),
    ("lex=1 (v6)", "eval_blind_lex_tiebreak.json"),
    ("lex=1 + lex_first=3", "eval_blind_lexfirst.json"),
])
show("300cn（官方路径，冷启动）", [
    ("lex=0 (v5)", "eval_300cn_after_r5.json"),
    ("lex=1 (v6)", "eval_300cn_lex_tiebreak.json"),
    ("lex=1 + lex_first=3", "eval_300cn_lexfirst.json"),
])
