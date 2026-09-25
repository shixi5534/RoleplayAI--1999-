# -*- coding: utf-8 -*-
"""只读探针（batch148）：核对候选实体名是否已在 graph.json 中。"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
idx = {e["name"]: e for e in json.loads(
    (ROOT / "graph.json").read_text(encoding="utf-8"))["entities"]}

CANDIDATES = [
    # 1920 尾部
    "星锑", "APPLe", "莱莉", "“四指”强尼", "“闪光”莱安娜", "绅士约翰尼",
    "城镇警卫Ⅰ", "城镇警卫Ⅱ", "城镇警卫Ⅲ", "观众Ⅰ", "观众Ⅱ", "观众Ⅲ",
    "观众们", "十四行诗", "维尔汀", "司辰", "启明会", "阿派朗学派",
    "广播剧院", "甲壳虫旅馆", "甲壳虫舞厅", "淘金镇", "77号公路", "西海岸",
    "泰晤士河", "爱琴海", "麦克风", "唱片机", "吉他", "贝斯", "鼓",
    "APPLe号", "自治法令", "禁令", "摇滚乐", "黑名单", "注册信息",
    "口香糖", "朵", "报纸", "手写信", "邀请函",
    "查尔斯·明格斯", "埃尔维斯·普雷斯利", "佛莱迪·摩克瑞",
    # 1921
    "恐怖通", "约书亚", "泥鯭的士", "李安安", "阿猴", "大只佬",
    "包租婆", "圣洛夫基金会职员Ⅰ", "圣洛夫基金会职员Ⅱ", "米莉", "威廉",
    "鬼魂治理协会", "西区灯塔", "旧城寨", "深夜走廊", "事务所",
    "调查许可", "桃木剑", "符纸", "保鲜膜", "清洁剂", "木头剑",
    "天斩煞", "闹鬼", "鬼影", "绿湖事件", "烛", "纸堆", "缴费单",
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
for sub in ["恐怖通", "约书亚", "泥鯭", "李安安", "阿猴", "大只佬", "包租婆",
            "米莉", "威廉", "鬼魂治理", "西区", "城寨", "桃木", "天斩",
            "绿湖", "司辰", "阿派朗", "明格斯", "普雷斯利", "摩克瑞", "职员"]:
    print(f"  {sub:10s} -> {[n for n in idx if sub in n][:12]}")
