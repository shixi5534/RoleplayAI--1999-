# -*- coding: utf-8 -*-
"""深挖 lex_first 在 300cn 上的 up=7/down=7 净零。

关键问题：为什么把词面前 3 名提到最前，会**弄丢** 7 道 v6 本来命中的题？
若能定位"哪些题被 lex_first 挤掉"以及"被挤掉的块原本排第几"，
就能设计一个**只增不减**的改法（真正的安全杠杆）。
"""
from __future__ import annotations

import json
from pathlib import Path

R = Path("data/compendium_rag/reports")


def load(f: str) -> dict[str, dict]:
    d = json.loads((R / f).read_text(encoding="utf-8"))
    return {r["qid"]: r for r in d["rows"]
            if r.get("mode") == "full" and r.get("answerable")}


v6 = load("eval_300cn_lex_tiebreak.json")
lf = load("eval_300cn_lexfirst.json")

down = sorted(q for q in v6 if v6[q].get("hit") and not lf[q].get("hit"))
up = sorted(q for q in v6 if lf[q].get("hit") and not v6[q].get("hit"))
print("=" * 84)
print(f"300cn lex_first 净零拆解：up={len(up)} down={len(down)}")
print("=" * 84)

print("\n--- DOWN（v6 命中，lex_first 弄丢）---")
for q in down:
    r = lf[q]
    print(f"  {q}: rr v6={v6[q].get('rr')} -> lf={r.get('rr')}  n_ev={r.get('n_evidence')}")

print("\n--- UP（lex_first 救回）---")
for q in up:
    print(f"  {q}: rr v6={v6[q].get('rr')} -> lf={lf[q].get('rr')}")

# 现在用缓存看真实的天花板：如果只取"v6 序 + lex 前N 的并集（不重排）"会怎样？
print()
print("=" * 84)
print("关键思路：lex_first 是**重排**（把 lex 前3 强行插到最前），会挤掉 v6 已命中的块。")
print("若改成**只增不减的并集**（v6 序保持在前，lex 前列只补 v6 没有的），")
print("则 down 必须为 0，而 up 取决于 lex 补进来的块是否落在 top-6。")
print("=" * 84)

cache_path = R / "_85_channel_cache.json"
if not cache_path.exists():
    print("\n(缓存还没建好，稍后重跑本分析)")
    raise SystemExit(0)

CACHE = json.loads(cache_path.read_text(encoding="utf-8"))
recs = CACHE["sets"]["300cn"]
K, TOPN = 60, 24


def rrf(channels, weights, top_n=TOPN):
    agg = {}
    for ch in sorted(channels):
        w = weights.get(ch, 1.0)
        for rank, (cid, _r) in enumerate(channels[ch], start=1):
            agg[cid] = agg.get(cid, 0.0) + w * (1.0 / (K + rank))
    return sorted(agg, key=lambda c: (-agg[c], c))[:top_n]


# 复现 v6 与 lex_first 的序，验证理解正确
def order_v6(r):
    ch = {k: v for k, v in r["channels"].items() if v}
    return rrf(ch, {"lex": 1.0})


def order_lexfirst(r, n=3):
    base = order_v6(r)
    lex_ranked = [cid for cid, _ in r["channels"]["lex"]]
    out, seen = [], set()
    for cid in lex_ranked[:n] + base + lex_ranked:
        if cid not in seen:
            seen.add(cid)
            out.append(cid)
    return out


def hit(order, gold):
    return any(c in gold for c in order[:6])


mismatch = 0
for qid, r in recs.items():
    gold = set(r["gold"])
    if not gold:
        continue
    if hit(order_lexfirst(r, 3), gold) != bool(lf.get(qid, {}).get("hit")):
        mismatch += 1
print(f"\n离线 lex_first=3 复现：与官方不一致 {mismatch} 题（应为 0 或极少）")

# 只增不减的并集方案
print("\n--- 只增不减并集：base 序在前，lex 前 L 名只补 base 缺失的 ---")
print("  （此方案 down 恒为 0，因为 base 的前 6 位置不变）")
for L in (1, 2, 3, 5, 8, 12, 20):
    h = 0
    for qid, r in recs.items():
        gold = set(r["gold"])
        if not gold:
            continue
        base = order_v6(r)
        lex_ranked = [cid for cid, _ in r["channels"]["lex"]]
        merged, seen = [], set()
        for cid in base:                      # v6 序全保留在前
            if cid not in seen:
                seen.add(cid); merged.append(cid)
        for cid in lex_ranked[:L]:            # lex 前列只补缺
            if cid not in seen:
                seen.add(cid); merged.append(cid)
        if hit(merged, gold):
            h += 1
    print(f"    L={L:<3} hit={h}/196 = {h/196:.4f}")
