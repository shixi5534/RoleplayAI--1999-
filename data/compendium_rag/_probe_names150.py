# -*- coding: utf-8 -*-
"""只读探针（batch150）：核对候选实体名是否已在 graph.json 中。"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
idx = {e["name"]: e for e in json.loads(
    (ROOT / "graph.json").read_text(encoding="utf-8"))["entities"]}

CANDIDATES = [
    "泥鯭的士", "李安安", "陈半仙", "Lily", "盲眼算命师", "鲁尼小子",
    "鬼魂治理协会", "协会成员托尼", "协会成员鲁特", "街边算命师",
    "护士Ⅰ", "护士Ⅱ", "鬼注人", "阴阳眼", "除灵", "天师",
    "除灵十三法", "三清铃", "百合花", "红丝线百合花", "桃木剑", "符纸",
    "符咒", "护身符", "招魂幡", "八卦镜", "天命", "天通洞", "旧城寨",
    "鬼宅", "出租屋", "街边酒吧", "洛杉矶", "唐人街", "灯塔", "西区灯塔",
    "圣洛夫基金会", "拉普拉斯", "俄罗斯方块游戏机", "探灵器", "七星禹步",
    "招魂", "引魂", "鬼", "能量", "恐惧", "阴宅", "除灵事务所",
    "新科学除灵驱鬼事务所", "黄符纸", "猪大腿骨", "假发", "黄衣师兵",
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
for sub in ["托尼", "鲁特", "街边", "护士", "护身", "招魂", "八卦",
            "鬼宅", "出租", "酒吧", "唐人街", "探灵", "禹步", "事务",
            "黄符", "假发", "恐惧", "除掉"]:
    print(f"  {sub:10s} -> {[n for n in idx if sub in n][:12]}")
