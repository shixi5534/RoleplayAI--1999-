# -*- coding: utf-8 -*-
"""只读探针（batch147）：核对候选实体名是否已在 graph.json 中。"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
idx = {e["name"]: e for e in json.loads(
    (ROOT / "graph.json").read_text(encoding="utf-8"))["entities"]}

CANDIDATES = [
    "星锑", "APPLe", "莱莉", "维尔汀", "十四行诗", "启明会", "绅士约翰尼",
    "“四指”强尼", "“闪光”莱安娜", "“战锤”尤尼", "“章鱼”德米特里",
    "城镇警卫Ⅰ", "吵闹的年轻人", "年轻人", "街头少年", "停车小子",
    "埃尔维登", "淘金镇", "甲壳虫旅馆", "甲壳虫舞厅", "广播剧院", "广播台",
    "发电厂", "医院", "旅店", "西海岸", "旧金山", "洛杉矶", "伦敦",
    "普利茅斯", "莫斯科", "唐人街", "圣洛夫基金会", "自治法令", "入境登记",
    "公共区域安全法", "摇滚乐", "神秘术", "软盘", "唱片机", "唱片", "音箱",
    "X光片", "骨碟", "巧克力", "生理盐水", "植物营养液", "急救手册",
    "光学迷彩", "手写信", "邀请函", "麦克风", "贝斯", "吉他", "鼓", "键盘",
    "绳子", "玩具手枪", "彩带", "酒店侍从", "议员", "受苦者", "颂赞歌会",
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
for sub in ["莱莉", "强尼", "莱安娜", "尤尼", "德米特里", "启明", "约翰尼",
            "警卫", "埃尔维登", "甲壳虫", "广播", "自治法令", "骨碟", "X光",
            "受苦", "议员", "旧金山", "莫斯科", "维尔汀"]:
    print(f"  {sub:10s} -> {[n for n in idx if sub in n][:12]}")
