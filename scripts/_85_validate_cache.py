# -*- coding: utf-8 -*-
"""校验：从通道缓存离线复算，能否**逐题精确复现** BASELINE_v6 的已知数字。

这是整套离线实验的信任基础 —— 若复现不出 0.8418 / 0.8350，则后续所有扫参都不可信。
"""
from __future__ import annotations

import json
from pathlib import Path

R = Path("data/compendium_rag/reports")
CACHE = json.loads((R / "_85_channel_cache.json").read_text(encoding="utf-8"))
K = 60
TOPN = 24


def rrf(channels: dict[str, list[list]], weights: dict[str, float], top_n: int) -> list[str]:
    agg: dict[str, float] = {}
    for ch in sorted(channels):
        w = weights.get(ch, 1.0)
        for rank, (cid, _raw) in enumerate(channels[ch], start=1):
            agg[cid] = agg.get(cid, 0.0) + w * (1.0 / (K + rank))
    return sorted(agg, key=lambda c: (-agg[c], c))[:top_n]


def hit6(order: list[str], gold: set[str]) -> bool:
    return any(c in gold for c in order[:6])


# 官方 v6 = lex 权重 1.0，四通道全开，rrf top_n = max(6*4,24) = 24
configs = {
    "300cn": ("eval_300cn_lex_tiebreak.json", {"lex": 1.0}, 196),
    "blind": ("eval_blind_lex_tiebreak.json", {"lex": 1.0}, 206),
}
print("=" * 80)
print("离线复算 vs 官方 eval（v6：lex=1.0，rrf top_n=24，四通道）")
print("=" * 80)
for setname, (evf, w, want_n) in configs.items():
    recs = CACHE["sets"][setname]
    off_hits = set()
    n_ans = 0
    for qid, r in recs.items():
        gold = set(r["gold"])
        if not gold:
            continue
        n_ans += 1
        order = rrf({k: v for k, v in r["channels"].items() if v}, w, TOPN)
        if hit6(order, gold):
            off_hits.add(qid)

    ev = json.loads((R / evf).read_text(encoding="utf-8"))
    ev_hits = {x["qid"] for x in ev["rows"]
               if x.get("mode") == "full" and x.get("answerable") and x.get("hit")}
    ev_ans = {x["qid"] for x in ev["rows"]
              if x.get("mode") == "full" and x.get("answerable")}

    print(f"\n  [{setname}]")
    print(f"    离线 n={n_ans} 官方 n={len(ev_ans)}   题集一致={set(recs) >= ev_ans or n_ans==len(ev_ans)}")
    print(f"    离线 hit@6 = {len(off_hits)}/{n_ans} = {len(off_hits)/n_ans:.4f}")
    print(f"    官方 hit@6 = {len(ev_hits)}/{len(ev_ans)} = {len(ev_hits)/len(ev_ans):.4f}")
    only_off = sorted(off_hits - ev_hits)
    only_ev = sorted(ev_hits - off_hits)
    print(f"    ⚠ 只有离线命中 ({len(only_off)}): {only_off}")
    print(f"    ⚠ 只有官方命中 ({len(only_ev)}): {only_ev}")
    print(f"    逐题一致 = {not only_off and not only_ev}")
