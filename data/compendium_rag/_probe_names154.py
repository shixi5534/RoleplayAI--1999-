# -*- coding: utf-8 -*-
"""只读探针（batch154）：核对候选实体名是否已在 graph.json 中。"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
idx = {e["name"]: e for e in json.loads(
    (ROOT / "graph.json").read_text(encoding="utf-8"))["entities"]}

CANDIDATES = [
    "图图石子", "芭卡洛儿", "维尔汀", "十四行诗", "槲寄生", "塞洛尼",
    "卡穆塔", "托阿", "苏芙比", "新巴别塔", "X", "司辰",
    "努库泰澳岛", "克雷莫纳", "箱庭贸易节", "箱庭卧室", "露营地",
    "湖畔", "荒原", "自由海风号",
    "罗盘草", "罗盘灼灼", "贝壳项链", "独木舟", "海螺吹哨", "编织手杖",
    "棕榈树皮", "动物油脂", "颜料", "荧树枝", "细颈花瓶", "树皮面具",
    "手账本", "魔药箱", "惊愕跳跳虫", "提丰挂件", "魔精",
    "无纸打印机", "魔精足迹转印分析器", "像素转换镜片",
    "钟表的维修（进阶篇）", "诗歌韵律之美", "高效沟通：谈话技巧艺术",
    "神秘术", "人工梦游", "安眠", "德鲁伊", "海风", "暴风雨",
]

print("=== already in graph ===")
for c in CANDIDATES:
    e = idx.get(c)
    if e:
        print(f"  YES  {c:24s} type={e['type']:4s} m={e['mentions']:4d} "
              f"aliases={e['aliases']} desc={e['desc']!r}")

print()
print("=== NOT in graph ===")
for c in CANDIDATES:
    if c not in idx:
        print(f"  no   {c}")

print()
print("=== fuzzy ===")
for sub in ["罗盘", "荧树", "花瓶", "手账", "魔药", "跳跳", "提丰",
            "魔精", "打印机", "分析器", "镜片", "克雷莫纳", "自由海风",
            "苏芙比", "新巴别", "槲寄生", "德鲁伊", "海螺", "手杖"]:
    print(f"  {sub:10s} -> {[n for n in idx if sub in n][:12]}")
