# -*- coding: utf-8 -*-
"""只读探针（batch160）：核对候选实体名是否已在 graph.json 中。"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
idx = {e["name"]: e for e in json.loads(
    (ROOT / "graph.json").read_text(encoding="utf-8"))["entities"]}

CANDIDATES = [
    # 人物
    "挖掘艺术", "梅兰妮", "艾西", "查尔顿", "艾弗森", "威廉警长", "警长",
    "汤姆森", "皮克勒斯", "APPLe", "星锑", "温迪", "纳尔森", "爱丽丝",
    "报童", "流浪汉", "安保机器人", "安保员", "警犬",
    "劳伦斯", "拉米雷斯", "佩恩", "崔斯特", "贪婪杰克",
    # 组织 / 地点
    "新人类", "新苏格兰场", "警察局", "机车酒吧", "失眠夜旅馆", "安息旅馆",
    "蜜蜂号糖果屋", "邦德街", "摄政街", "卡纳比街", "伦敦", "北环路",
    # 物品 / 概念
    "伦敦之心", "雷米特杯", "安保指南", "安全制约-Ⅰ型", "镜面肥皂泡",
    "肥皂泡", "洁净灵水枪", "臭臭泥清新剂", "易形帽", "黏人球", "藏身杯子",
    "硝酸闪光纸", "鼻涕虫香精", "今日足球", "消防车", "泡泡",
    "神秘学家", "安保公司", "波普",
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
for sub in ["梅兰妮", "艾西", "查尔顿", "艾弗森", "汤姆森", "温迪", "纳尔森",
            "爱丽丝", "雷米特", "伦敦之心", "新人类", "苏格兰场", "机车",
            "失眠夜", "安息", "蜜蜂", "邦德", "摄政", "消防", "清新剂",
            "易形", "黏人", "藏身", "闪光纸", "香精", "足球"]:
    print(f"  {sub:10s} -> {[n for n in idx if sub in n][:12]}")
