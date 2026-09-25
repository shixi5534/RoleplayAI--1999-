# -*- coding: utf-8 -*-
"""修正「6 / 艾尔玛 / 亚齐」的别名污染（一次性数据修复）。

问题：rebuild 时下列别名声明把三个语义不同的对象并成了单节点：
  - batch25  : 实体 "6"    aliases ['亚齐']
  - batch90  : 实体 "6"    aliases ['艾尔玛']  (type 角色)
  - batch91  : 实体 "艾尔玛" aliases ['6']，实体 "亚齐" aliases ['6']
「6」是阿派朗学派领袖之位（概念），艾尔玛与亚齐是先后两代持有者（不同的人）。
本脚本从批文件中剥离这些别名，并把实体 "6" 统一为「概念」类型；
改动的批文件会重新 submit 覆盖缓存，之后 rebuild 即可得到三个独立节点。
"""
import json
import glob
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PERSON_NAMES = {"艾尔玛", "亚齐"}
ROLE_TOKENS = {"6", "现任6", "上一任6"}
changed = []

for fp in sorted(glob.glob(str(ROOT / "_agent_batch*.json"))):
    path = Path(fp)
    raw = path.read_text(encoding="utf-8")
    data = json.loads(raw)
    dirty = False
    for key, blk in data.items():
        for e in blk.get("entities", []):
            name = e.get("name", "")
            aliases = list(e.get("aliases") or [])
            new = list(aliases)
            if name in PERSON_NAMES:
                new = [a for a in new if a not in ROLE_TOKENS]
            elif name == "6":
                new = [a for a in new if a not in PERSON_NAMES]
                if e.get("type") != "概念":
                    e["type"] = "概念"
                    dirty = True
            if new != aliases:
                e["aliases"] = new
                dirty = True
    if dirty:
        path.write_text(json.dumps(data, ensure_ascii=False, indent=1),
                        encoding="utf-8")
        changed.append(path.name)

print("已修正批文件:", changed or "(无)")
