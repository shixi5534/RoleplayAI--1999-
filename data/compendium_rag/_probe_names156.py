# -*- coding: utf-8 -*-
"""只读探针（batch156）：核对候选实体名是否已在 graph.json 中。"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
idx = {e["name"]: e for e in json.loads(
    (ROOT / "graph.json").read_text(encoding="utf-8"))["entities"]}

CANDIDATES = [
    "坎吉拉", "贾纳丹", "萨尔曼少爷", "萨尔曼老爷", "仆人Ⅰ", "仆人Ⅱ",
    "喷吉", "夏尔贾", "辛哈大叔", "拾荒人辛格", "巴蒂亚", "苦修者",
    "警员", "警员Ⅱ", "摩卢旁卡村", "大篷车", "科罗曼德海岸",
    "蓝陶", "匕首", "手枪", "火车", "铁轨", "流浪者营地", "湖边",
    "罗望子", "扁豆罐头", "圣灰", "薄荷糖", "识字本",
    "金孔雀", "卡比尔", "暴君", "莎丽", "萨罗逾河",
    "魔精贩子", "野生魔精幼崽", "教师", "学生", "扒手", "新巴别塔",
    "神秘学家", "怜悯心", "魔精", "纱丽",
]

print("=== already in graph ===")
for c in CANDIDATES:
    e = idx.get(c)
    if e:
        print(f"  YES  {c:16s} type={e['type']:4s} m={e['mentions']:4d} "
              f"aliases={e['aliases']} desc={e['desc']!r}")

print()
print("=== NOT in graph ===")
for c in CANDIDATES:
    if c not in idx:
        print(f"  no   {c}")

print()
print("=== fuzzy ===")
for sub in ["巴蒂亚", "辛格", "苦修", "科罗曼德", "圣灰", "薄荷", "识字",
            "孔雀", "卡比尔", "暴君", "莎丽", "萨罗逾", "贩子", "扒手",
            "扁豆", "罗望子", "营地", "铁轨"]:
    print(f"  {sub:10s} -> {[n for n in idx if sub in n][:12]}")
