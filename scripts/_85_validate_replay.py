# -*- coding: utf-8 -*-
"""校验离线重放器能否精确复现官方 v6 / lex_first 数字。

若不能逐题一致，则一切扫参作废。
"""
from __future__ import annotations

import json
from pathlib import Path

R = Path("data/compendium_rag/reports")
D = json.loads((R / "_85_replay_data.json").read_text(encoding="utf-8"))
K, TOPN = 60, 24


def fuse(per, weights, k=K, top_n=TOPN):
    agg = {}
    for cid, chans in per.items():
        s = sum(weights.get(ch, 1.0) * (1.0 / (k + rk)) for ch, rk in chans.items())
        agg[cid] = s
    return sorted(agg, key=lambda c: (-agg[c], c))[:top_n]


def lexfirst(rec, base, L):
    if L <= 0:
        return base
    out, seen = [], set()
    for cid in rec["lex_order"][:L] + base + rec["lex_order"]:
        if cid not in seen:
            seen.add(cid)
            out.append(cid)
    return out


def hit(order, gold):
    return any(c in gold for c in order[:6])


def official(fname):
    d = json.loads((R / fname).read_text(encoding="utf-8"))
    return {x["qid"]: x for x in d["rows"]
            if x.get("mode") == "full" and x.get("answerable")}


print("=" * 88)
print("离线重放 vs 官方 eval —— 逐题一致性（这是信任基础）")
print("=" * 88)
for setname, evf, L in [("300cn", "eval_300cn_lex_tiebreak.json", 0),
                        ("300cn", "eval_300cn_lexfirst.json", 3),
                        ("blind", "eval_blind_lex_tiebreak.json", 0),
                        ("blind", "eval_blind_lexfirst.json", 3)]:
    recs = D[setname]
    off = official(evf)
    off_hits = {q for q, r in off.items() if r.get("hit")}
    off_ans = set(off)
    off_rate = f"{len(off_hits)}/{len(off_ans)} = {len(off_hits)/len(off_ans):.4f}"

    my = 0
    my_hits = set()
    for qid in off_ans:                 # 只评官方认定的 answerable 题
        rec = recs[qid]
        base = fuse(rec["per"], {"lex": 1.0})
        order = lexfirst(rec, base, L) if L else base
        if hit(order, set(rec["gold"])):
            my += 1
            my_hits.add(qid)
    only_my = sorted(my_hits - off_hits)
    only_off = sorted(off_hits - my_hits)
    print(f"\n  [{setname} L={L}] {evf}")
    print(f"    官方 {off_rate}")
    print(f"    离线 {my}/{len(off_ans)} = {my/len(off_ans):.4f}")
    print(f"    只有离线命中 ({len(only_my)}): {only_my[:12]}")
    print(f"    只有官方命中 ({len(only_off)}): {only_off[:12]}")
    print(f"    逐题一致 = {not only_my and not only_off}")
