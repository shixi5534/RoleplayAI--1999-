# -*- coding: utf-8 -*-
"""输出语料章节清单，用于把盲写题任务切分给多个子代理（互不重叠）。"""
from __future__ import annotations

import json
from collections import Counter, defaultdict
from pathlib import Path

c = json.loads(Path("data/compendium_rag/corpus.json").read_text(encoding="utf-8"))
print("stats:", json.dumps(c["stats"], ensure_ascii=False)[:300])
ch = c["chapters"]
print(f"chapters={len(ch)}")
print("category 分布:", Counter(x["category"] for x in ch))

# 按 category 分组列出 doc_id + 章节号 + 标题
g = defaultdict(list)
for x in ch:
    g[x["category"]].append((x["chapter_id"], x["doc_id"], x["title"], x.get("units")))
for cat, items in g.items():
    print(f"\n=== {cat} ({len(items)}) ===")
    for cid, doc, title, units in items[:200]:
        print(f"  {cid}\t{doc}\t{title}\t{units}")
