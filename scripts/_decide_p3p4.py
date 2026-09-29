# -*- coding: utf-8 -*-
"""P3 / P4 是否值得立项 —— 用 v7 之后的**新事实**重新评估。

前序结论建立在 v6(k=60) 的 "14 道池内 miss" 上；v7(k=1) 已改变命中集合。
本脚本回答三个可判定问题：
  Q1 当前 300cn 的 miss 里，gold 是否**已在池内**（→ 需更强重排 = P4）
     还是**根本不在池内**（→ 需补抽提/查询侧 = P3）？
  Q2 池上限（hit@30）离 0.85 有多远？重排的理论天花板是多少？
  Q3 若只救"池内但未进 top-6"的题，能达到什么水平？P4 的上界是多少？

只读既有工件（v6/v7 的 collect + eval），不跑检索。
"""
from __future__ import annotations

import json
from pathlib import Path

R = Path("data/compendium_rag/reports")
AUDIT = Path("data/knowledge/_audit")

reg = json.loads((AUDIT / "gold_defects_registry.json").read_text(encoding="utf-8"))
DEFECT = set(reg["exempt_qids_conservative"])


def collect(f: str) -> dict[str, dict]:
    d = json.loads((R / f).read_text(encoding="utf-8"))
    return {r["qid"]: r for r in d["rows"]
            if r.get("mode") == "full" and r.get("answerable")}


def hits(f: str) -> set[str]:
    d = json.loads((R / f).read_text(encoding="utf-8"))
    return {r["qid"] for r in d["rows"]
            if r.get("mode") == "full" and r.get("answerable") and r.get("hit")}


for tag, cf, ef in [("v6 (k=60)", "rank_collect_v6c300_top30.json",
                     "eval_300cn_lex_tiebreak.json"),
                    ("v7 (k=1)", "rank_collect_k1c300_top30.json",
                     "eval_300cn_k1.json")]:
    C = collect(cf)
    H = hits(ef)
    miss = sorted(set(C) - H)
    miss_eff = [q for q in miss if q not in DEFECT]

    inpool = [q for q in miss_eff if C[q].get("rank")]          # gold 在池内
    outpool = [q for q in miss_eff if not C[q].get("rank")]     # gold 不在池内

    print("=" * 92)
    print(f"[{tag}]  answerable={len(C)}  hit={len(H)}  有效miss={len(miss_eff)}"
          f"  (另 {len(miss)-len(miss_eff)} 道为 gold 缺陷)")
    print("=" * 92)
    print(f"   A. 池内但未进 top-6（重排可救 → P4）: {len(inpool)}  {inpool}")
    if inpool:
        rk = sorted(C[q]["rank"] for q in inpool)
        print(f"      池内名次分布: {rk}")
    print(f"   B. 不在池内（需补抽提/查询侧 → P3）: {len(outpool)}  {outpool}")

    n_all = len(C)
    ceiling = sum(1 for q in C if C[q].get("rank"))
    print(f"   → 池上限 hit@30 = {ceiling}/{n_all} = {ceiling/n_all:.4f}"
          f"（全量）/ 有效 {sum(1 for q in C if C[q].get('rank') and q not in DEFECT)}"
          f"/{n_all-len(DEFECT & set(C))} = "
          f"{sum(1 for q in C if C[q].get('rank') and q not in DEFECT)/(n_all-len(DEFECT & set(C))):.4f}")
    print(f"   → P4 理论收益上限 = 救回 A 组全部 {len(inpool)} 道"
          f" => 裸 hit@6 可达 {len(H)+len(inpool)}/{n_all} = "
          f"{(len(H)+len(inpool))/n_all:.4f}")
    print()

print("=" * 92)
print("结论")
print("=" * 92)
print("  · 若 A 组远大于 B 组 → 瓶颈在**重排**（P4 值得做）")
print("  · 若 B 组不可忽略   → 需**补抽提**（P3），且 P4 救不了它们")
