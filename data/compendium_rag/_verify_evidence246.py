# -*- coding: utf-8 -*-
"""batch246 证据逐字核对:evidence 去掉中文引号后须为原文连续子串。"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
dump = {json.loads(l)["key"]: json.loads(l)["text"]
        for l in (ROOT / "_dump246.txt").read_text(encoding="utf-8-sig").splitlines() if l.strip()}
data = json.loads((ROOT / "_agent_batch246.json").read_text(encoding="utf-8"))
QUOTES = str.maketrans("", "", "\u201c\u201d\u2018\u2019\"\u300c\u300d")
miss = 0
for k, blk in data.items():
    src = dump[k].translate(QUOTES)
    for r in blk["relations"]:
        ev = r["evidence"].translate(QUOTES)
        if ev not in src:
            miss += 1
            print(f"✗ {k} {r['src']}-{r['relation']}->{r['dst']}: {r['evidence']}")
print(f"\n核对 {sum(len(b['relations']) for b in data.values())} 条证据，未命中 {miss} 条")
sys.exit(1 if miss else 0)
