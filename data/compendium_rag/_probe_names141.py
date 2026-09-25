# -*- coding: utf-8 -*-
"""只读探针（batch141）：核对候选实体名是否已在 graph.json 中。"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
idx = {e["name"]: e for e in json.loads(
    (ROOT / "graph.json").read_text(encoding="utf-8"))["entities"]}

CANDIDATES = [
    "37", "X", "6", "爱兹拉", "兔毛手袋", "小梅斯梅尔", "店主", "苏菲亚",
    "沙丝绒", "可燃点", "210", "奇迹之星", "奇迹之石", "旅行者2号", "海王星",
    "天王星", "航天中心", "拉普拉斯博物馆", "科算中心", "冰淇淋", "十二角星",
    "进店率", "进店人数", "客单价", "营业额", "盈亏平衡分析", "参观者",
    "体验区", "展区", "演讲", "特别展览", "圆桌", "实时星图", "教典",
    "传道厅", "乘法轴", "加法轴", "格子", "假设", "点数", "委托",
    "砂金石榴子石", "等轴晶系", "钻石", "神秘学术式", "空间传送",
    "第一防线学校", "满天星", "宣传海报", "信纸", "笔记本", "蛋筒",
    "糖渍柠檬皮", "海王星的发现", "引力理论", "海王星的故事",
]

print("=== already in graph ===")
for c in CANDIDATES:
    e = idx.get(c)
    if e:
        print(f"  YES  {c:14s} type={e['type']:4s} m={e['mentions']:4d} "
              f"aliases={e['aliases']} desc={e['desc']!r}")

print()
print("=== NOT in graph ===")
for c in CANDIDATES:
    if c not in idx:
        print(f"  no   {c}")

print()
print("=== fuzzy ===")
for sub in ["沙丝绒", "可燃点", "210", "旅行者", "海王星", "天王星", "航天",
            "奇迹", "第一防线", "信纸", "糖渍", "参观者", "传道"]:
    print(f"  {sub:8s} -> {[n for n in idx if sub in n]}")
