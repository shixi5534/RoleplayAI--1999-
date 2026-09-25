# -*- coding: utf-8 -*-
"""只读探针（batch169）：核对候选实体名是否已在 graph.json 中。"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
idx = {e["name"]: e for e in json.loads(
    (ROOT / "graph.json").read_text(encoding="utf-8"))["entities"]}

CANDIDATES = [
    "玛蒂尔达", "坎吉拉", "阿贾尔", "伽菈波那", "库玛尔", "夏尔贾",
    "鬃毛沙砾", "辛哈大叔", "达恩", "施密特博士", "勒诺曼",
    "摩卢旁卡村", "摩卢旁卡火车站", "昌迪加尔", "德里", "摩卢旁卡神庙",
    "北窟", "野草地", "街道", "石窟", "新城",
    "灵摆", "黄水晶", "水晶球", "电动三轮", "望远镜", "钱夹",
    "烛星节", "毗因陀神", "彗首", "壁画", "浮雕壁画", "资料",
    "宣传海报", "地图", "藏宝图", "石像", "石雕", "宝伞",
    "曼咔", "小蛇", "神秘学家", "占卜", "冥想", "类星体",
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
for sub in ["玛蒂尔达", "坎吉拉", "阿贾尔", "伽菈", "库玛尔", "鬃毛",
            "毗因陀", "烛星", "彗", "灵摆", "水晶球", "三轮", "石窟",
            "北窟", "类星体", "占卜", "冥想", "曼咔"]:
    print(f"  {sub:10s} -> {[n for n in idx if sub in n][:12]}")
