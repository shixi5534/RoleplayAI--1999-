# -*- coding: utf-8 -*-
"""只读探针（batch158）：核对候选实体名是否已在 graph.json 中。"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
idx = {e["name"]: e for e in json.loads(
    (ROOT / "graph.json").read_text(encoding="utf-8"))["entities"]}

CANDIDATES = [
    "坦南特", "弗雷明", "阿德丽塔", "德洛姆", "酒保", "？？？",
    "法兰西之蓝", "南非盒子", "慈祥的玛利亚", "午夜酒馆",
    "午夜酒馆贵宾室", "人造钻石实验室", "典当行大厅", "旅馆房间",
    "巴黎", "美国", "南非", "意大利", "印度", "帕纳矿区", "科洛马",
    "钻石", "钻戒", "香槟", "血腥落日", "保险箱", "珠宝盒", "冲锋枪",
    "手枪", "左轮手枪", "打字机", "烧杯", "木炭", "手绢", "天鹅绒垫",
    "马歇尔", "锯木厂", "黑手党", "神秘学家", "法郎", "美元",
    "地下工厂", "别墅", "圣勒梅兹", "海洛薇兹", "走私",
]

print("=== already in graph ===")
for c in CANDIDATES:
    e = idx.get(c)
    if e:
        print(f"  YES  {c:18s} type={e['type']:4s} m={e['mentions']:4d} "
              f"aliases={e['aliases']} desc={e['desc']!r}")

print()
print("=== NOT in graph ===")
for c in CANDIDATES:
    if c not in idx:
        print(f"  no   {c}")

print()
print("=== fuzzy ===")
for sub in ["南非", "玛利亚", "血腥", "保险箱", "烧杯", "木炭", "天鹅绒",
            "马歇尔", "黑手党", "法郎", "工厂", "别墅", "圣勒梅兹",
            "帕纳", "科洛马", "酒保", "手枪", "左轮"]:
    print(f"  {sub:10s} -> {[n for n in idx if sub in n][:12]}")
