# -*- coding: utf-8 -*-
"""对账 blind：v6 vs k=1（含 graph_only 与安全线）。"""
from __future__ import annotations

import json
from pathlib import Path

R = Path("data/compendium_rag/reports")


def cal(f: str):
    p = R / f
    if not p.exists():
        return None
    d = json.loads(p.read_text(encoding="utf-8"))
    rows = d["rows"]
    get = lambda mode, ans: [r for r in rows
                             if r.get("mode") == mode
                             and (ans is None or bool(r.get("answerable")) == ans)]
    sel = get("full", True)
    h = sum(1 for r in sel if r.get("hit"))
    go = get("graph_only", True)
    return {
        "n": len(sel), "hits": h, "rate": h / len(sel),
        "hit_q": {r["qid"] for r in sel if r.get("hit")},
        "go": (sum(1 for r in go if r.get("hit")), len(go)),
        "grounded": sum(1 for r in sel if r.get("grounded")) / len(sel),
    }


for setname, ref, new in [("blind", "eval_blind_lex_tiebreak.json", "eval_blind_k1.json")]:
    a, b = cal(ref), cal(new)
    if not a or not b:
        print(f"[{setname}] 缺文件"); continue
    print("=" * 78)
    print(f"[{setname} 留出集]  v6 vs k=1")
    print("=" * 78)
    print(f"  v6   full {a['hits']}/{a['n']} = {a['rate']:.4f}   graph_only {a['go'][0]}/{a['go'][1]}")
    print(f"  k=1  full {b['hits']}/{b['n']} = {b['rate']:.4f}   graph_only {b['go'][0]}/{b['go'][1]}")
    print(f"  达标(≥0.85) = {b['rate'] >= 0.85}   grounded={b['grounded']:.4f}")
    up = sorted(b["hit_q"] - a["hit_q"]); dn = sorted(a["hit_q"] - b["hit_q"])
    print(f"  up={len(up)}  {up}")
    print(f"  down={len(dn)}  {dn}")
