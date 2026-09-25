# -*- coding: utf-8 -*-
"""只读探针（batch162）：核对候选实体名是否已在 graph.json 中。"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
idx = {e["name"]: e for e in json.loads(
    (ROOT / "graph.json").read_text(encoding="utf-8"))["entities"]}

CANDIDATES = [
    "挖掘艺术", "梅兰妮", "艾西", "星锑", "APPLe", "皮克勒斯", "查尔顿",
    "温迪", "纳尔森", "爱丽丝", "艾弗森", "安保机器人", "安保犬",
    "新人类", "安保指南", "雷米特杯", "伦敦之心", "通风管道", "通风口",
    "空想肥皂泡", "空想肥皂水", "翻译器", "麦克风", "广播电台",
    "闭路电视", "电闸箱", "保险丝", "监控室", "展厅", "大厅",
    "宠物留存区", "世界杯", "遥控器", "镇静喷剂", "军用弹药",
    "图钉胶水枪", "磁性黏胶", "螺旋扇", "爬行擒拿术", "物物相易",
    "重塑·信徒", "塔利亚", "红牌", "防盗网", "警犬",
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
for sub in ["重塑", "塔利亚", "通风", "电闸", "保险丝", "监控", "闭路",
            "麦克风", "广播", "遥控", "喷剂", "弹药", "黏胶", "螺旋",
            "擒拿", "物物", "防盗", "警犬", "留守", "留存"]:
    print(f"  {sub:10s} -> {[n for n in idx if sub in n][:12]}")
