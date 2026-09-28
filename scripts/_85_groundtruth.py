# -*- coding: utf-8 -*-
"""目标 85% —— 地面真相：哪些口径还没到 0.85，以及各配置下的 miss 清单。

只读既有 eval 工件，不改任何东西。判据统一为 mode=full 且 answerable。
"""
from __future__ import annotations

import json
from pathlib import Path

R = Path("data/compendium_rag/reports")


def load(f: str) -> dict[str, dict]:
    d = json.loads((R / f).read_text(encoding="utf-8"))
    out = {}
    for r in d["rows"]:
        if r.get("mode") == "full" and r.get("answerable"):
            out[r["qid"]] = r
    return out


SETS = {
    "盲测206": {
        "lex=0 (v5)": "eval_blind_lex_off.json",
        "lex=1 (v6)": "eval_blind_lex_tiebreak.json",
        "lex=1 + lex_first=3": "eval_blind_lexfirst.json",
    },
    "300cn(196)": {
        "lex=0 (v5)": "eval_300cn_v6_tb_lexoff.json",
        "lex=1 (v6)": "eval_300cn_lex_tiebreak.json",
        "lex=1 + lex_first=3": "eval_300cn_lexfirst.json",
    },
}

print("=" * 86)
print("① 裸检索 hit@6 —— 哪些口径未达 0.85")
print("=" * 86)
data: dict[str, dict[str, dict]] = {}
for setname, cfgs in SETS.items():
    data[setname] = {}
    print(f"\n  [{setname}]")
    for cfg, f in cfgs.items():
        rows = load(f)
        data[setname][cfg] = rows
        h = sum(1 for r in rows.values() if r.get("hit"))
        n = len(rows)
        rate = h / n
        flag = "PASS" if rate >= 0.85 else f"FAIL(差 {0.85*n - h:.1f} 题 = 需 +{-(-(0.85*n-h)//1):.0f})"
        print(f"    {cfg:22} {h}/{n} = {rate:.4f}   {flag}")

print()
print("=" * 86)
print("② lex_first=3 的逐题得失（相对 v6）")
print("=" * 86)
for setname in SETS:
    v6 = data[setname]["lex=1 (v6)"]
    lf = data[setname]["lex=1 + lex_first=3"]
    qids = sorted(set(v6) & set(lf))
    up = [q for q in qids if lf[q].get("hit") and not v6[q].get("hit")]
    dn = [q for q in qids if v6[q].get("hit") and not lf[q].get("hit")]
    print(f"\n  [{setname}]  up={len(up)} down={len(dn)}")
    print(f"    up  : {up}")
    print(f"    down: {dn}")

print()
print("=" * 86)
print("③ 仍被 miss 的题（lex_first=3 口径）—— 这是要攻的靶子")
print("=" * 86)
targets: dict[str, list[str]] = {}
for setname in SETS:
    lf = data[setname]["lex=1 + lex_first=3"]
    miss = sorted(q for q, r in lf.items() if not r.get("hit"))
    targets[setname] = miss
    print(f"\n  [{setname}] miss={len(miss)}")
    print(f"    {miss}")

print()
print("=" * 86)
print("④ 300cn miss 是否同时被盲测 miss（判断是不是普遍性缺陷 vs 单集特例）")
print("=" * 86)
m300 = set(targets["300cn(196)"])
print(f"  300cn miss {len(m300)} 道；其中在盲测也 miss 的：{sorted(m300 & set(targets['盲测206']))}")

out = {k: sorted(v) for k, v in targets.items()}
Path("data/compendium_rag/reports/_85_targets.json").write_text(
    json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
print()
print("  -> 已写 data/compendium_rag/reports/_85_targets.json")
