# -*- coding: utf-8 -*-
"""只读探针（batch145）：核对候选实体名是否已在 graph.json 中。"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
idx = {e["name"]: e for e in json.loads(
    (ROOT / "graph.json").read_text(encoding="utf-8"))["entities"]}

CANDIDATES = [
    "环状水星", "皮克勒斯", "洋葱头", "槲寄生", "十四行诗",
    "\"小刀\"麦高芬", "“断指”", "潘佐", "阿乔", "狱警", "小弟",
    "柴豆郡后街帮", "亨特利尔高墙监狱", "黑铁森林", "起司大街", "探监室",
    "监狱前厅", "郊野", "休格镇", "废弃露营地", "电视节目", "ONiON",
    "莱茵黄金", "黄金", "三明治", "牛奶", "呼叫机", "催眠枪", "冲锋枪",
    "旧照片", "照片", "小帐篷", "垃圾桶", "红气球", "狗绳",
    "神秘术", "梦想", "能量", "灵体", "仪式", "颂钵", "迷迭香",
    "马克·吐温", "幽默故事", "文学", "广告", "商业主义", "药",
    "边境牧羊犬", "吉娃娃", "流浪狗", "狗", "莱茵",
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
for sub in ["断指", "潘佐", "阿乔", "麦高芬", "莱茵", "黑铁", "起司", "休格",
            "监狱", "狱警", "小弟", "帮", "吐温", "幽默", "催眠", "冲锋枪",
            "三明治", "气球", "牧羊", "吉娃娃", "柴豆"]:
    print(f"  {sub:8s} -> {[n for n in idx if sub in n][:12]}")
