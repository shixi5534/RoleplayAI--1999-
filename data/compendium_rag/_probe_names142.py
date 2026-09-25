# -*- coding: utf-8 -*-
"""只读探针（batch142）：核对候选实体名是否已在 graph.json 中。"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
idx = {e["name"]: e for e in json.loads(
    (ROOT / "graph.json").read_text(encoding="utf-8"))["entities"]}

CANDIDATES = [
    "37", "X", "6", "爱兹拉", "兔毛手袋", "小梅斯梅尔", "店主", "星锑", "十四行诗",
    "苏菲亚", "铅玻璃", "陌生病患", "杰瑞·威尔逊", "牙仙",
    "拉普拉斯康复中心", "拉普拉斯科算中心", "科算中心", "第一防线学校",
    "康复中心职员丹尼", "实习职员亚当", "助理希曼", "露西", "拉普拉斯康复中心主任室",
    "阿其翁", "怪味豆", "巧克力冰淇淋", "冰淇淋", "十二角星", "回信", "信纸",
    "可可豆", "梧桐科", "豆科", "基金会", "APPLe号三世", "无限定者", "暴雨",
    "阿纳瓦水提纯器", "循环机", "咪达唑仑", "格拉斯哥昏迷表", "事故报告",
    "同意书", "多萝西娅", "废弃病房", "二级管理区域", "管理条例", "太妃糖",
    "费米估算法", "阿基米德", "数沙者", "沙粒", "手帕", "论文", "期刊剪报",
    "数据库", "谜题", "真理", "本质",
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
for sub in ["铅玻璃", "杰瑞", "牙仙", "丹尼", "亚当", "希曼", "露西", "阿其翁",
            "星锑", "十四行诗", "多萝西娅", "康复中心", "怪味豆", "巧克力",
            "阿基米德", "费米", "无限定", "基金会", "APPLe"]:
    print(f"  {sub:8s} -> {[n for n in idx if sub in n]}")
