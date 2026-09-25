# -*- coding: utf-8 -*-
"""只读探针（batch175）：核对 15101 候选实体名是否已在 graph.json 中。

重点：`沙丝绒`/`可燃点`/`兔毛手袋`/`爱兹拉`/`乌卢鲁运动会` 疑似已在图中，
但 15101 尚未抽取 → 必须查清它们的来源（哪一章建立的），以决定复用/限定名。
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
graph = json.loads((ROOT / "graph.json").read_text(encoding="utf-8"))
idx = {e["name"]: e for e in graph["entities"]}

CANDIDATES = [
    # 人物
    "沙丝绒", "可燃点", "兔毛手袋", "爱兹拉", "维尔汀", "和平乌鲁",
    "马科尔", "琼斯", "多萝西", "本特莉施提", "坎贝尔",
    # 地点/组织
    "澳大利亚", "拉普拉斯科算中心", "科算中心", "拉普拉斯澳大利亚分部",
    "圣洛夫基金会", "墨尔本", "爱丽丝泉", "乌卢鲁岩", "乌卢鲁运动场",
    "翻滚鳄", "翻滚鳄书籍专卖店", "桉树兄弟会",
    # 事件/概念
    "乌卢鲁运动会", "轮回者", "神秘学家", "人类", "暴雨",
    # 物品/生物
    "幽灵蘑菇", "金格", "蜜环菌", "澳大利亚蜜环菌", "本耶普",
    "寻水杖", "鼠尾草", "鼠尾草佐匹克隆贴剂", "火苗", "圣火",
    "答录机", "好朋友徽章", "相册", "鸸鹋",
]

print("=== already in graph ===")
for c in CANDIDATES:
    e = idx.get(c)
    if e:
        print(f"  YES  {c:22s} type={e['type']:4s} m={e['mentions']:4d} "
              f"aliases={e['aliases']}")
        print(f"        desc={e['desc']!r}")

print()
print("=== NOT in graph ===")
for c in CANDIDATES:
    if c not in idx:
        print(f"  no   {c}")

print()
print("=== fuzzy (substring) ===")
for sub in ["乌卢鲁", "拉普拉斯", "本耶普", "蘑菇", "金格", "轮回",
            "翻滚", "袋鼠", "运动", "墨尔本", "爱丽丝", "桉树",
            "科算", "澳大利亚", "鼠尾草", "寻水"]:
    hits = [n for n in idx if sub in n]
    print(f"  {sub:10s} -> {hits[:15]}")
