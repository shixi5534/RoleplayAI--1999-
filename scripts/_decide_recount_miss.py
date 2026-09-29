# -*- coding: utf-8 -*-
"""v7 之后：重新计算 miss 分布，为 P3/P4 决策提供事实依据。

前序 P3/P4 论证都建立在 "14 道池内 miss" 上，而那是 v6(k=60) 的数字。
v7(k=1) 已改变命中集合，必须先看**当前**真相再决定是否投入 P3/P4。
"""
from __future__ import annotations

import json
from pathlib import Path

R = Path("data/compendium_rag/reports")


def rows(f: str, mode: str = "full", ans: bool | None = True) -> dict[str, dict]:
    d = json.loads((R / f).read_text(encoding="utf-8"))
    return {r["qid"]: r for r in d["rows"]
            if r.get("mode") == mode
            and (ans is None or bool(r.get("answerable")) == ans)}


SETS = {
    "300cn": ("eval_300cn_k1.json", "eval_300cn_lex_tiebreak.json"),
    "blind206": ("eval_blind_k1.json", "eval_blind_lex_tiebreak.json"),
    "gen120": ("eval_gen120_k1.json", "eval_gen_lex_on.json"),
}

gold = json.loads((Path("data/knowledge/_audit/_85_gold_audit.json"))
                  .read_text(encoding="utf-8"))
defect = set(gold["summary"]["defective_qids"])

print("=" * 92)
print("v7(k=1) vs v6(k=60) 的 miss 对照")
print("=" * 92)
allmiss: dict[str, set[str]] = {}
for name, (f7, f6) in SETS.items():
    a, b = rows(f7), rows(f6)
    miss7 = {q for q, r in a.items() if not r.get("hit")}
    miss6 = {q for q, r in b.items() if not r.get("hit")}
    allmiss[name] = miss7
    print(f"\n[{name}]  n={len(a)}")
    print(f"   v6 miss = {len(miss6)}   v7 miss = {len(miss7)}")
    print(f"   v7 新掉的 (v6中/v7失) = {sorted(miss7 - miss6)}")
    print(f"   v7 救回的 (v6失/v7中) = {sorted(miss6 - miss7)}")
    print(f"   v7 miss 题号 = {sorted(miss7)}")

print()
print("=" * 92)
print("v7 miss 中有多少是 gold 缺陷题（已审计）")
print("=" * 92)
for name, m in allmiss.items():
    d = sorted(m & defect)
    v = sorted(m - defect)
    print(f"  [{name}] miss={len(m)}  gold缺陷={len(d)} {d}")
    print(f"           有效miss={len(v)}  {v}")

print()
print("=" * 92)
print("300cn 池上限（hit@30）—— 重排的理论天花板")
print("=" * 92)
from collections import Counter
for tag, f in [("v6 pool (k=60)", "rank_collect_v6c300_top30.json"),
               ("v7 pool (k=1)", "rank_collect_k1c300_top30.json")]:
    p = R / f
    if not p.exists():
        print(f"  [{tag}] 缺文件")
        continue
    d = json.loads(p.read_text(encoding="utf-8"))
    rs = [r for r in d["rows"] if r.get("mode") == "full" and r.get("answerable")]
    inpool = sum(1 for r in rs if r.get("rank"))
    print(f"  {tag:18} 池内 = {inpool}/{len(rs)} = {inpool/len(rs):.4f}")
