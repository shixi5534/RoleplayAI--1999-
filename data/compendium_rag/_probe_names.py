# -*- coding: utf-8 -*-
"""一次性只读探查：近几轮 batch 是否共用同一批实体名（判断邻居批次命名约定）。"""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
COMMON = ["重塑追随者Ⅰ", "重塑追随者Ⅱ", "苏菲亚", "37", "6", "教众Ⅰ",
          "重塑之手", "报童", "伦纳德", "挖掘艺术", "重塑使徒", "孩子",
          "无理数", "整数", "有理数"]

for n in (133, 134, 135, 136, 137):
    p = ROOT / f"_gen_batch{n}.py"
    raw = p.read_text(encoding="utf-8")
    names = set(re.findall(r'E\(\s*"([^"]+)"', raw))
    hits = [x for x in COMMON if x in names]
    print(f"{n}: E-names={len(names)}  common={hits}")

print()
for n in (133, 134, 135, 136, 137):
    p = ROOT / f"_agent_batch{n}.json"
    d = json.loads(p.read_text(encoding="utf-8"))
    allnames = set()
    for blk in d.values():
        for e in blk["entities"]:
            allnames.add(e["name"])
    hits = [x for x in COMMON if x in allnames]
    print(f"{n}(json): {sorted(d)[0][:40]}...  common={hits}")
