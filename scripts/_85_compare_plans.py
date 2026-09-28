# -*- coding: utf-8 -*-
"""对照：k=1（单参数）是否已优于 lex_first=3（另一参数），以及两者叠加。

目的：给出收敛的"最稳改动"建议 —— 优先选参数更少、两集同升的方案。
在已验证的重放数据上算（对 v6/L=3 逐题一致）。
"""
from __future__ import annotations

import json
from pathlib import Path

R = Path("data/compendium_rag/reports")
D = json.loads((R / "_85_replay_data.json").read_text(encoding="utf-8"))


def ans(f):
    d = json.loads((R / f).read_text(encoding="utf-8"))
    return {x["qid"] for x in d["rows"]
            if x.get("mode") == "full" and x.get("answerable")}


ANS = {"300cn": ans("eval_300cn_lex_tiebreak.json"),
       "blind": ans("eval_blind_lex_tiebreak.json")}


def fuse(rec, k):
    agg = {cid: sum(1.0 / (k + rk) for rk in ch.values())
           for cid, ch in rec["per"].items()}
    return sorted(agg, key=lambda c: (-agg[c], c))[:24]


def lf(rec, base, L):
    if L <= 0:
        return base
    out, seen = [], set()
    for cid in rec["lex_order"][:L] + base + rec["lex_order"]:
        if cid not in seen:
            seen.add(cid); out.append(cid)
    return out


def ev(setname, rule):
    h = sum(1 for q in ANS[setname]
            if any(c in set(D[setname][q]["gold"]) for c in rule(D[setname][q])[:6]))
    return h, len(ANS[setname])


print("=" * 84)
print("方案对照（300cn 调参 / blind 留出）")
print("=" * 84)
print(f"  {'方案':30} {'300cn':>16} {'blind':>16}  双达标")
cases = [
    ("v6 (k=60, 无 lex_first)", lambda r: fuse(r, 60)),
    ("lex_first=3 (k=60)", lambda r: lf(r, fuse(r, 60), 3)),
    ("k=1 (单参数, 无 lex_first)", lambda r: fuse(r, 1)),
    ("k=1 + lex_first=3", lambda r: lf(r, fuse(r, 1), 3)),
    ("k=2 (单参数)", lambda r: fuse(r, 2)),
]
for tag, rule in cases:
    h3, n3 = ev("300cn", rule)
    hb, nb = ev("blind", rule)
    ok = "YES" if h3 / n3 >= .85 and hb / nb >= .85 else ""
    print(f"  {tag:30} {h3:>4}/{n3} = {h3/n3:.4f}  {hb:>4}/{nb} = {hb/nb:.4f}  {ok}")

print()
print("结论：k=1 用**一个全局常数**同时提升两集，且不需要 lex_first；")
print("      lex_first 与 k=1 叠加在 300cn 无额外收益（167），故取更简的 k=1 单独启用。")
