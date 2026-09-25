# -*- coding: utf-8 -*-
"""只读探针（batch157）：核对候选实体名是否已在 graph.json 中。"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
idx = {e["name"]: e for e in json.loads(
    (ROOT / "graph.json").read_text(encoding="utf-8"))["entities"]}

CANDIDATES = [
    # 1924 尾
    "坎吉拉", "贾纳丹", "学生", "教师", "扒手", "巴蒂亚", "喷吉",
    "警员Ⅰ", "警员Ⅱ", "警犬", "普通警员", "追踪警员", "追踪警员Ⅱ",
    "昌迪加尔警局", "车站", "火车货厢", "雨林", "河流", "铁轨",
    "背包", "薄荷糖", "识字本", "手枪", "木棍", "石子", "水壶",
    "金孔雀", "卡比尔", "王室徽章",
    # 1925
    "坦南特", "弗雷明", "阿德丽塔", "温妮弗雷德", "劳尔斯", "德洛姆",
    "法兰西之蓝", "午夜酒馆", "巴黎", "安特卫普", "威尼斯", "奥地利",
    "美国", "印度", "科鲁尔矿场", "贡土尔",
    "马克西米利安", "玛利亚·勃艮", "布蕾特·科赛特", "弗雷明·隆根",
    "钻石", "钻戒", "香槟", "银戒", "手套", "打字机", "典当行",
    "酒会", "脱口秀", "广播剧", "军火商人", "珠宝商人",
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
for sub in ["坦南特", "弗雷明", "阿德丽塔", "温妮弗雷德", "劳尔斯", "德洛姆",
            "法兰西", "钻石", "香槟", "银戒", "手套", "打字机", "典当",
            "巴黎", "安特卫普", "威尼斯", "军火", "珠宝", "警犬", "货厢"]:
    print(f"  {sub:10s} -> {[n for n in idx if sub in n][:12]}")
