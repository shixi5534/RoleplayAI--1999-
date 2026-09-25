# -*- coding: utf-8 -*-
"""只读探针（batch166）：核对候选实体名是否已在 graph.json 中。"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
idx = {e["name"]: e for e in json.loads(
    (ROOT / "graph.json").read_text(encoding="utf-8"))["entities"]}

CANDIDATES = [
    "牙仙", "维尔汀", "十四行诗", "恐怖通", "金蜜儿", "安妮", "杰森",
    "学生迈克尔", "弗莱迪", "屠夫", "巨大魔精", "怪物集群", "罗德",
    "木屋", "阁楼", "苔藓山洞", "洞穴", "森林", "绿湖营地", "湖",
    "卡邦克鲁增生原液", "太妃糖", "校医室", "秘密笔记本", "采集袋",
    "陷阱", "木板", "椅子", "沙发", "苔藓", "魔药", "钥匙",
    "戒指盒", "婚戒", "布偶", "通灵板", "录音带", "日记本",
    "维多利亚", "日记", "摄影机", "剧本", "神秘术", "神秘学家",
    "最后的女孩", "芝诺少年军", "芝诺军备学院", "太妃糖",
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
for sub in ["卡邦克鲁", "太妃", "校医", "采集袋", "陷阱", "木板",
            "苔藓", "魔药", "戒指", "布偶", "通灵", "录音带", "日记",
            "维多利亚", "最后的女孩", "巢穴", "湖"]:
    print(f"  {sub:10s} -> {[n for n in idx if sub in n][:12]}")
