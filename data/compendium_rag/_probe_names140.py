# -*- coding: utf-8 -*-
"""只读探针：核对候选实体名是否已在 graph.json 中，并打印既有 type/desc 供复用判断。"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
graph = json.loads((ROOT / "graph.json").read_text(encoding="utf-8"))
idx = {e["name"]: e for e in graph["entities"]}

CANDIDATES = [
    # 人物
    "X", "37", "6", "爱兹拉", "兔毛手袋", "小梅斯梅尔", "店主", "苏菲亚",
    # 组织 / 地点
    "拉普拉斯科算中心", "科算中心", "拉普拉斯博物馆", "拉普拉斯", "机灵蛋筒家",
    # 物品 / 概念
    "冰淇淋", "十二角星", "正十二边形", "施莱夫利符号", "柏拉图立体", "对数表",
    "费马大定理", "教典", "避电膏", "血月水母", "仙人掌猫", "人工梦游治疗室",
    "宇宙的奥秘", "特别展览", "笔记本", "记号笔", "草稿纸", "蛋筒",
    "客单价", "进店人数", "营业额", "假说", "课题",
]

print("=== already in graph ===")
for c in CANDIDATES:
    e = idx.get(c)
    if e:
        print(f"  YES  {c:16s} type={e['type']:4s} m={e['mentions']:4d} "
              f"aliases={e['aliases']} desc={e['desc']!r}")

print()
print("=== NOT in graph (candidates to create) ===")
for c in CANDIDATES:
    if c not in idx:
        print(f"  no   {c}")

print()
print("=== fuzzy: names containing key substrings ===")
for sub in ["爱兹拉", "兔毛", "梅斯梅尔", "冰淇淋", "拉普拉斯", "苏菲亚", "店主",
            "十二角", "柏拉图", "费马", "开普勒", "对数"]:
    hits = [n for n in idx if sub in n]
    print(f"  {sub:8s} -> {hits}")
