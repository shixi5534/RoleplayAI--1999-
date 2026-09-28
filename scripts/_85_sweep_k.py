# -*- coding: utf-8 -*-
"""精细扫描：k 在 1..8 邻域 + 与 lex_first 的组合（在已验证的重放数据上）。"""
from __future__ import annotations

import json
from pathlib import Path

R = Path("data/compendium_rag/reports")
D = json.loads((R / "_85_replay_data.json").read_text(encoding="utf-8"))


def official_ans(f):
    d = json.loads((R / f).read_text(encoding="utf-8"))
    return {x["qid"] for x in d["rows"]
            if x.get("mode") == "full" and x.get("answerable")}


ANS = {"300cn": official_ans("eval_300cn_lex_tiebreak.json"),
       "blind": official_ans("eval_blind_lex_tiebreak.json")}


def fuse(rec, k, weights=None, top_n=24):
    w = weights or {"lex": 1.0}
    agg = {}
    for cid, chans in rec["per"].items():
        agg[cid] = sum(w.get(ch, 1.0) * (1.0 / (k + rk)) for ch, rk in chans.items())
    return sorted(agg, key=lambda c: (-agg[c], c))[:top_n]


def lexfirst(rec, base, L):
    if L <= 0:
        return base
    out, seen = [], set()
    for cid in rec["lex_order"][:L] + base + rec["lex_order"]:
        if cid not in seen:
            seen.add(cid); out.append(cid)
    return out


def ev(setname, rule):
    h, hits = 0, set()
    for qid in ANS[setname]:
        rec = D[setname][qid]
        if any(c in set(rec["gold"]) for c in rule(rec)[:6]):
            h += 1; hits.add(qid)
    return h, len(ANS[setname]), hits


print("=" * 92)
print("k 精细扫描（无 lex_first）")
print("=" * 92)
print(f"  {'k':>4} {'300cn':>18} {'blind':>18}   双达标")
for k in (1, 2, 3, 4, 5, 6, 7, 8, 60):
    h3, n3, _ = ev("300cn", lambda r, k=k: fuse(r, k))
    hb, nb, _ = ev("blind", lambda r, k=k: fuse(r, k))
    both = "YES" if h3 / n3 >= 0.85 and hb / nb >= 0.85 else ""
    print(f"  {k:>4} {h3:>4}/{n3} = {h3/n3:.4f}   {hb:>4}/{nb} = {hb/nb:.4f}   {both}")

print()
print("=" * 92)
print("k=1 与 lex_first 组合")
print("=" * 92)
print(f"  {'L':>4} {'300cn':>18} {'blind':>18}   双达标   (k=1)")
for L in (0, 1, 2, 3, 4, 5, 6):
    h3, n3, _ = ev("300cn", lambda r, L=L: lexfirst(r, fuse(r, 1), L))
    hb, nb, _ = ev("blind", lambda r, L=L: lexfirst(r, fuse(r, 1), L))
    both = "YES" if h3 / n3 >= 0.85 and hb / nb >= 0.85 else ""
    print(f"  {L:>4} {h3:>4}/{n3} = {h3/n3:.4f}   {hb:>4}/{nb} = {hb/nb:.4f}   {both}")

print()
print("=" * 92)
print("最优 k=1 的逐题得失（相对 v6 k=60）")
print("=" * 92)
for setname in ("300cn", "blind"):
    _, _, q60 = ev(setname, lambda r: fuse(r, 60))
    _, _, q1 = ev(setname, lambda r: fuse(r, 1))
    up = sorted(q1 - q60); dn = sorted(q60 - q1)
    print(f"\n  [{setname}] up={len(up)} down={len(dn)}")
    print(f"    up  : {up}")
    print(f"    down: {dn}")

print()
print("=" * 92)
print("k=1 + L=3 的逐题得失")
print("=" * 92)
for setname in ("300cn", "blind"):
    _, _, q60 = ev(setname, lambda r: fuse(r, 60))
    _, _, qx = ev(setname, lambda r: lexfirst(r, fuse(r, 1), 3))
    up = sorted(qx - q60); dn = sorted(q60 - qx)
    print(f"\n  [{setname}] up={len(up)} down={len(dn)}")
    print(f"    up  : {up}")
    print(f"    down: {dn}")
