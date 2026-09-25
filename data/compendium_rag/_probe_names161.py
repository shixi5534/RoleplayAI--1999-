# -*- coding: utf-8 -*-
"""只读探针（batch161）：核对候选实体名是否已在 graph.json 中。"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
idx = {e["name"]: e for e in json.loads(
    (ROOT / "graph.json").read_text(encoding="utf-8"))["entities"]}

CANDIDATES = [
    "挖掘艺术", "星锑", "APPLe", "梅兰妮", "艾西", "查尔顿", "皮克勒斯",
    "温迪", "艾弗森", "威廉警长", "报童", "警察", "警员",
    "拉米雷斯", "汤米", "流浪汉",
    "新人类", "机车酒吧", "卡纳比街", "摄政街", "伦敦", "警局",
    "雷米特杯", "伦敦之心", "拉米雷斯安保", "安保指南", "安保机器人",
    "消防车", "镜面肥皂泡", "镭射肥皂泡", "空想肥皂泡", "泡泡装置",
    "今日足球", "魔精", "瞌睡跳跳豆", "信封", "黑色册子", "相机",
    "墓碑", "摩托车", "翻译器", "泡泡", "洒水车", "唐宁街10号",
    "大本钟", "伦敦塔", "雷米特杯展厅", "序厅", "通风口",
    "足球", "世界杯", "噪音",
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
for sub in ["泡泡", "洒水", "唐宁", "大本钟", "伦敦塔", "展厅", "通风",
            "跳跳豆", "册子", "墓碑", "摩托", "翻译", "世界杯", "汤米"]:
    print(f"  {sub:10s} -> {[n for n in idx if sub in n][:12]}")
