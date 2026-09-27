# -*- coding: utf-8 -*-
"""探测 corpus/chunks 结构 + 14 道 miss 的题型学分类（供盲测与召回改进用）。"""
from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

for p in ["data/compendium_rag/corpus.json", "data/compendium_rag/chunks.json"]:
    d = json.loads(Path(p).read_text(encoding="utf-8"))
    print(f"=== {p} ===")
    print("top keys:", list(d.keys()))
    for k, v in d.items():
        if isinstance(v, list):
            print(f"  {k}: list len={len(v)}")
            if v and isinstance(v[0], dict):
                print(f"     item keys: {list(v[0].keys())}")
                print(f"     item sample: {json.dumps(v[0], ensure_ascii=False)[:220]}")
        else:
            print(f"  {k}: {type(v).__name__}")

ts = json.loads(Path("data/knowledge/_audit/rag_testset_300_cn.json").read_text(encoding="utf-8"))
cases = ts["cases"]
by = {str(x.get("id")): x for x in cases}
MISS = ["R005", "R012", "R018", "R094", "R127", "R170", "R171",
        "R231", "R244", "R248", "R251", "R273", "R297", "R298"]

print("\n=== miss 分类：是否问英文名 / 题型 / 章 / 难度 ===")
print(f"{'qid':6} {'askEN':6} {'type':10} {'hop':7} {'diff':7} {'chap':6} evidence")
for q in MISS:
    e = by[q]
    d = e.get("dims") or {}
    print(f"{q:6} {str(e.get('_asks_english_name')):6} {d.get('type',''):10} "
          f"{d.get('hop',''):7} {d.get('difficulty',''):7} {d.get('chapter',''):6} "
          f"{e.get('evidence')}")

print("\n=== 全区 300 题中 _asks_english_name 分布 ===")
print(Counter(bool(x.get("_asks_english_name")) for x in cases))
print("\n=== 全区 dims 分布 ===")
for k in ("type", "hop", "difficulty", "depth"):
    print(f"  {k}: {Counter((x.get('dims') or {}).get(k) for x in cases)}")

# miss 里英文名占比 vs 全区
miss_en = sum(1 for q in MISS if by[q].get("_asks_english_name"))
all_en = sum(1 for x in cases if x.get("_asks_english_name"))
print(f"\nmiss 中问英文名: {miss_en}/{len(MISS)} = {miss_en/len(MISS):.2%}")
print(f"全区中问英文名: {all_en}/{len(cases)} = {all_en/len(cases):.2%}")
