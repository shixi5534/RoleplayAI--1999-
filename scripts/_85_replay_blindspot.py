# -*- coding: utf-8 -*-
"""量化离线重放的**已知盲区**：k=1 可能把「k=60 时排 30 名外」的候选提进来。

collect 只存了 k=60 下的 fused top-30。k=1 与 k=60 的候选集合差异无法从该文件观察。
本脚本给出**上界估计**：若把池放宽到全部可观测候选（30）后 top-6 已定，
则真正的差异只可能来自「完全未记录」的候选。

做法：
  1. 用重放数据在 k=1 下算 top-24（模拟生产的池切分）；
  2. 检查 gold 是否可能来自「未记录但被某通道排前列」的块 —— 用 lex 全序（60 深）作为
     唯一可观测的「更宽」通道，量化有多少 gold 落在 lex 前列却不在 fused 池内。
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


def fuse(rec, k, top_n):
    agg = {}
    for cid, chans in rec["per"].items():
        agg[cid] = sum(1.0 / (k + rk) for rk in chans.values())
    return sorted(agg, key=lambda c: (-agg[c], c))[:top_n]


for setname, evf in [("300cn", "eval_300cn_lex_tiebreak.json"),
                     ("blind", "eval_blind_lex_tiebreak.json")]:
    A = ans(evf)
    n_pool_gain = 0
    n_gold_only_lex = 0
    examples = []
    for qid in A:
        rec = D[setname][qid]
        gold = set(rec["gold"])
        pool24 = set(fuse(rec, 1, 24))
        top6 = fuse(rec, 1, 6)
        # gold 是否在 lex 前 60 但不在 fused 池内（潜在的"未记录"遗漏）
        lex60 = set(rec["lex_order"][:60])
        cand = (gold & lex60) - pool24
        if cand:
            n_gold_only_lex += 1
            if len(examples) < 6:
                examples.append((qid, sorted(cand)[:2]))
        # 池从 24 放宽到全部可观测（30）能否改善 top-6
        pool_all = set(fuse(rec, 1, 999))
        if not any(c in gold for c in top6) and any(c in gold for c in pool24):
            n_pool_gain += 1
    print(f"\n[{setname}] n={len(A)}")
    print(f"  gold 在 lex 前 60 但**不在 k=1 fused 池(24)** 的题数 = {n_gold_only_lex}")
    print(f"    （这些是重放**看不到**的候选 —— 真实 k=1 可能额外改善）")
    if examples:
        print(f"    样例: {examples}")
    print(f"  gold 在池内(24)但不在 top-6 的题数 = {n_pool_gain}"
          f"  （需更强重排才可救，非 k 能解决）")
