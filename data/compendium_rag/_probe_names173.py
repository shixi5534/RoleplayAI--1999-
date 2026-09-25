# -*- coding: utf-8 -*-
"""只读探针（batch173）：核对候选实体名是否已在 graph.json 中。"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
idx = {e["name"]: e for e in json.loads(
    (ROOT / "graph.json").read_text(encoding="utf-8"))["entities"]}

CANDIDATES = [
    "伽菈波那", "库玛尔", "鬃毛沙砾", "玛蒂尔达", "坎吉拉", "阿贾尔",
    "夏尔贾", "夏尔贾老师", "吉娜", "卡塔尔", "希玛妮教授",
    "摩卢旁卡村", "昌迪加尔", "昌迪加尔夜市", "摩卢旁卡神庙",
    "沙尔玛旧宅", "地下空间", "北窟", "石窟", "街道", "后山森林",
    "地下室", "旧屋", "鬃毛沙砾的旧屋",
    "湿婆", "湿婆神像", "毗湿奴神像", "幻境", "特殊天体", "宇宙之卵",
    "观测技巧", "重塑之手", "重塑·门徒", "圣洛夫基金会",
    "入职介绍信", "烛星节", "星烛", "流星雨", "剪刀", "望远镜",
    "寻星镜", "相片", "信", "库玛尔的信", "老式望远镜",
    "《地下生存手册》", "《犊牛的饲养与管理》", "演算纸",
    "神秘学家", "人类", "小鹿手偶", "地图", "星盘", "水晶球",
]

print("=== already in graph ===")
for c in CANDIDATES:
    e = idx.get(c)
    if e:
        print(f"  YES  {c:22s} type={e['type']:4s} m={e['mentions']:4d} "
              f"aliases={e['aliases']} desc={e['desc']!r}")

print()
print("=== NOT in graph ===")
for c in CANDIDATES:
    if c not in idx:
        print(f"  no   {c}")

print()
print("=== fuzzy ===")
for sub in ["湿婆", "宇宙之卵", "观测技巧", "地下空间", "地下室", "夜市",
            "入职介绍", "流式", "剪刀", "演算纸", "手册", "犊牛",
            "寻星", "旧宅", "夜空", "流星", "烛星"]:
    print(f"  {sub:10s} -> {[n for n in idx if sub in n][:12]}")
