# -*- coding: utf-8 -*-
"""只读探针（batch146）：核对候选实体名是否已在 graph.json 中。"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
idx = {e["name"]: e for e in json.loads(
    (ROOT / "graph.json").read_text(encoding="utf-8"))["entities"]}

CANDIDATES = [
    # 1919 尾部
    "环状水星", "皮克勒斯", "洋葱头", "潘佐", "阿乔", "“断指”", "\"小刀\"麦高芬",
    "“断指”的小弟", "阿尔古斯", "老大", "迪亚哥家族", "柴豆郡后街帮",
    "亨特利尔高墙监狱", "黑铁森林", "箱中客厅", "海滨长街", "警局", "警员",
    "莱茵黄金", "旧照片", "红气球", "冲锋枪", "呼叫机", "福利院",
    "神秘术", "术式", "软盘", "灵摆", "薰香", "饮剂", "打火机",
    "广告Ⅰ", "广告Ⅱ", "广告Ⅲ", "通缉令", "临终日记", "电视节目",
    "超范围红外感知定位仪", "夜盲症", "蜡烛", "灵体", "能量",
    # 1920
    "星锑", "APPLe", "莱莉", "淘金镇", "西海岸", "洛杉矶", "加州一号公路",
    "传送软盘", "威斯敏斯特桥", "基金会", "唱片收藏", "背包客",
    "约翰·列侬", "摇滚乐", "音乐", "水", "塑料瓶", "汽车",
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
for sub in ["莱莉", "淘金", "西海岸", "洛杉矶", "列侬", "APPLe", "星锑",
            "传送软盘", "威斯敏斯特", "迪亚哥", "老大", "广告", "灵摆",
            "薰香", "福利院", "夜盲", "定位仪", "日记", "警员"]:
    print(f"  {sub:10s} -> {[n for n in idx if sub in n][:12]}")
