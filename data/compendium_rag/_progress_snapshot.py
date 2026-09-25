# -*- coding: utf-8 -*-
"""权威进度快照：用 extract.cache_key 公式精确统计各分类/各版本进度。

口径说明（交接文档坑 6）：
  - 进度以「已抽块数」为准，cache 文件数因内容哈希去重会略少；
  - 本脚本直接用与提取器一致的 cache_key 公式，覆盖全量 chunks，无遗漏。
"""
import json
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT.parent.parent / "src"))

from compendium_rag.config import get_settings          # noqa: E402
from compendium_rag.pipeline import load_chunks          # noqa: E402
from compendium_rag.extract import PROMPT_VERSION, cache_key  # noqa: E402

s = get_settings()
chunks = load_chunks(s)
cache_keys = {p.stem for p in (ROOT / "cache").rglob("*.json")}

done = [c for c in chunks if cache_key(c, s.llm_model, PROMPT_VERSION) in cache_keys]
print(f"模型={s.llm_model}  提示词={PROMPT_VERSION}")
print(f"已抽 {len(done)}/{len(chunks)} "
      f"({len(done)/len(chunks)*100:.1f}%)  剩 {len(chunks)-len(done)}")
print(f"（cache 文件数 {len(cache_keys)}，差额为内容哈希去重）")
print()

tot = defaultdict(int)
got = defaultdict(int)
for c in chunks:
    tot[c.category] += 1
for c in done:
    got[c.category] += 1

print(f"{'category':18s} {'done':>6s} {'total':>6s} {'pct':>7s}")
for cat in sorted(tot):
    print(f"{cat:18s} {got[cat]:6d} {tot[cat]:6d} {got[cat]/tot[cat]*100:6.1f}%")
print(f"{'TOTAL':18s} {sum(got.values()):6d} {sum(tot.values()):6d} "
      f"{sum(got.values())/sum(tot.values())*100:6.1f}%")

print()
print("=== activity 各版本 ===")
docs = defaultdict(lambda: [0, 0])
for c in chunks:
    if c.category == "activity":
        docs[c.doc_id][0] += 1
dset = {c.chunk_id for c in done}
for c in chunks:
    if c.category == "activity" and c.chunk_id in dset:
        docs[c.doc_id][1] += 1

closed = 0
for doc, (t, g) in sorted(docs.items()):
    if g == t:
        closed += 1
        mark = "✅ 闭环"
    elif g == 0:
        mark = "   未抽"
    else:
        mark = f"   {g}/{t}"
    print(f"  {doc:46s} {t:4d} 块  {mark}")
print(f"\n  activity: {closed} 版闭环 / {len(docs)} 版总数")
