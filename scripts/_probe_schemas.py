# -*- coding: utf-8 -*-
"""探测：测试集 schema、语料可供性、14 道池内硬 miss 的题面。"""
from __future__ import annotations

import json
from pathlib import Path

ts = json.loads(Path("data/knowledge/_audit/rag_testset_300_cn.json").read_text(encoding="utf-8"))
print("testset keys:", list(ts.keys()))
c = ts["cases"][0]
print("case keys:", list(c.keys()))
print("case sample:", json.dumps(c, ensure_ascii=False)[:420])

for p in ["data/compendium_rag/corpus.json", "data/compendium_rag/chunks.json"]:
    fp = Path(p)
    if fp.exists():
        d = json.loads(fp.read_text(encoding="utf-8"))
        print(f"{p}: {type(d).__name__} len={len(d) if hasattr(d, '__len__') else '?'}")
        if isinstance(d, list) and d:
            print("   item keys:", list(d[0].keys())[:10])

cd = Path("data/lore/wu_ming_zhe/canon_zh")
print("canon_zh exists:", cd.exists(),
      "files:", len(list(cd.glob("*"))) if cd.exists() else 0)

MISS = ["R005", "R012", "R018", "R094", "R127", "R170", "R171",
        "R231", "R244", "R248", "R251", "R273", "R297", "R298"]
by = {str(x.get("id")): x for x in ts["cases"]}
print("\n=== 14 道 full 口径池内硬 miss ===")
for q in MISS:
    e = by.get(q)
    if not e:
        print(q, "NOT FOUND"); continue
    print(f"{q}: {e.get('q')}")
    print(f"      evidence={e.get('evidence')}")
