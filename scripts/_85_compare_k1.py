# -*- coding: utf-8 -*-
"""严格对账：k=1 的 eval 工件 vs v6 基线（统一口径 mode=full, answerable）。"""
from __future__ import annotations

import json
import sys
from pathlib import Path

R = Path("data/compendium_rag/reports")


def cal(f: str):
    p = R / f
    if not p.exists():
        return None
    d = json.loads(p.read_text(encoding="utf-8"))
    rows = d["rows"]
    sel = [r for r in rows if r.get("mode") == "full" and r.get("answerable")]
    un = [r for r in rows if r.get("mode") == "full" and not r.get("answerable")]
    go = [r for r in rows if r.get("mode") == "graph_only" and r.get("answerable")]
    h = sum(1 for r in sel if r.get("hit"))
    return {
        "n": len(sel), "hits": h, "rate": h / len(sel),
        "hit_q": {r["qid"] for r in sel if r.get("hit")},
        "unans": (sum(1 for r in un if r.get("hit")), len(un)),
        "grounded": (sum(1 for r in sel if r.get("grounded")) / len(sel)) if sel else None,
        "go": (sum(1 for r in go if r.get("hit")), len(go)) if go else None,
    }


pairs = [("300cn", "eval_300cn_lex_tiebreak.json", "eval_300cn_k1.json")]
for setname, ref, new in pairs:
    a, b = cal(ref), cal(new)
    if not a or not b:
        print(f"[{setname}] 缺文件 ref={ref} new={new}")
        continue
    print("=" * 78)
    print(f"[{setname}]  v6(基线) vs k=1")
    print("=" * 78)
    print(f"  v6   {a['hits']}/{a['n']} = {a['rate']:.4f}   unans={a['unans']}  grounded={a['grounded']:.4f}")
    print(f"  k=1  {b['hits']}/{b['n']} = {b['rate']:.4f}   unans={b['unans']}  grounded={b['grounded']:.4f}")
    print(f"  达标(≥0.85) = {b['rate'] >= 0.85}")
    up = sorted(b["hit_q"] - a["hit_q"]); dn = sorted(a["hit_q"] - b["hit_q"])
    print(f"  up={len(up)}  {up}")
    print(f"  down={len(dn)}  {dn}")
    if b["go"]:
        print(f"  graph_only: v6 {a['go'][0]}/{a['go'][1]}  ->  k=1 {b['go'][0]}/{b['go'][1]}")
    print(f"  安全线 unanswerable 命中: v6 {a['unans'][0]}/{a['unans'][1]} -> k=1 {b['unans'][0]}/{b['unans'][1]}")
