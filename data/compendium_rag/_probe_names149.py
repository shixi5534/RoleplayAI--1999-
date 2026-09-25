# -*- coding: utf-8 -*-
"""只读探针（batch149）：核对候选实体名是否已在 graph.json 中。"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
idx = {e["name"]: e for e in json.loads(
    (ROOT / "graph.json").read_text(encoding="utf-8"))["entities"]}

CANDIDATES = [
    "李安安", "泥鯭的士", "陈半仙", "盲眼算命师", "鲁尼小子", "阿珍妹",
    "Lily", "床底的黑影", "僵尸Ⅰ", "僵尸Ⅱ", "陌生男人",
    "神秘学犯罪科警员Ⅰ", "神秘学犯罪科警员Ⅱ", "收音机",
    "九龙", "旧城寨", "天通洞", "天命", "废旧木屋", "警局", "墓园",
    "兴街", "儿童福利院", "天通洞的桥洞", "深井",
    "除灵十三法", "三清铃", "锈铜锁链", "铁桶", "劫卦", "木卦",
    "桃木剑", "符纸", "符咒", "百合花", "红丝线", "纸人", "帐篷",
    "阴阳眼", "除灵师", "天师", "鬼注人", "怨鬼", "能量", "神秘学犯罪",
    "俄罗斯练胆大法", "约法三章", "封印", "符箓竹简", "东汉墓葬群",
    "大哥大", "泔水", "墨镜", "铁皮柜子", "乌鸦血", "旧教室",
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
for sub in ["陈半仙", "半仙", "盲眼", "鲁尼", "阿珍", "Lily", "僵尸",
            "天通", "天命", "城寨", "兴街", "除灵", "阴阳眼", "三清",
            "劫卦", "百合", "警员", "福利院", "墓"]:
    print(f"  {sub:10s} -> {[n for n in idx if sub in n][:12]}")
