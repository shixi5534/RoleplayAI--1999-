# -*- coding: utf-8 -*-
"""只读探针（batch165）：核对候选实体名是否已在 graph.json 中。"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
idx = {e["name"]: e for e in json.loads(
    (ROOT / "graph.json").read_text(encoding="utf-8"))["entities"]}

CANDIDATES = [
    "牙仙", "维尔汀", "十四行诗", "恐怖通", "金蜜儿", "安妮", "杰森",
    "学生迈克尔", "弗莱迪", "屠夫", "巨大魔精", "魔精群", "罗德",
    "安娜", "芝诺军备学院", "绿湖营地", "森林", "木屋", "木屋大厅",
    "地下电源", "发电设施", "电箱", "州立青藤大学", "Lugus",
    "记录者CCD-TR57", "摄影机", "剧本", "毛毯", "扫除工具", "柜子",
    "玻璃罐", "牙仙（小精灵）", "鳞粉", "惠霏芬", "止痛药", "医疗箱",
    "钥匙", "汽车", "雨", "神秘学家", "人类", "恐惧诅咒",
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
for sub in ["罗德", "青藤", "Lugus", "毛毯", "柜子", "玻璃罐", "鳞粉",
            "惠霏芬", "止痛", "医疗箱", "钥匙", "魔精群", "木屋", "电箱",
            "发电", "破伤风", "薄荷", "话梅"]:
    print(f"  {sub:10s} -> {[n for n in idx if sub in n][:12]}")
