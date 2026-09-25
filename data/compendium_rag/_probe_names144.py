# -*- coding: utf-8 -*-
"""只读探针（batch144）：核对候选实体名是否已在 graph.json 中。"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
idx = {e["name"]: e for e in json.loads(
    (ROOT / "graph.json").read_text(encoding="utf-8"))["entities"]}

CANDIDATES = [
    # 1918 尾部
    "小梅斯梅尔", "多萝西娅", "兔毛手袋", "铅玻璃", "牙仙", "杰瑞·威尔逊",
    "康复中心职员丹尼", "康复中心职员威尔", "助理希曼",
    "父亲", "母亲", "姐姐", "本杰明", "马克", "伊莎贝拉", "Z", "红弩箭",
    "哀歌", "杰弗里·梅斯梅尔", "维尔汀", "勿忘我", "露西", "佩德拉",
    "拉普拉斯康复中心", "拉普拉斯科算中心", "第一防线学校", "圣洛夫基金会",
    "梅斯梅尔家族", "中心广场", "柏林", "乔治橡树",
    "软盘", "人工梦游仪器", "人工梦游", "捕梦网", "胸章", "医学院徽章",
    "梅斯梅尔基金", "希波克拉底誓言", "二级治疗师", "拉普拉斯康复中心职员",
    # 1919
    "环状水星", "洋葱头", "槲寄生", "十四行诗", "皮克勒斯", "阿尔古斯",
    "亨特利尔高墙监狱", "电玩餐馆", "箱中客厅", "颂钵", "迷迭香",
    "白茅花", "小刀", "麦高芬", "翻译器", "灵体", "仪式", "黄金",
    "headonion", "ONiON", "加油站", "面包车",
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
for sub in ["父亲", "母亲", "姐姐", "哀歌", "杰弗里", "伊莎贝拉", "红弩箭",
            "环状水星", "洋葱", "槲寄生", "皮克勒斯", "阿尔古斯", "亨特利尔",
            "电玩", "乔治", "曼德拉", "捕梦", "胸章", "基金", "治疗师"]:
    print(f"  {sub:8s} -> {[n for n in idx if sub in n][:12]}")
