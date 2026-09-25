# -*- coding: utf-8 -*-
"""只读探针（batch164）：核对候选实体名是否已在 graph.json 中。"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
idx = {e["name"]: e for e in json.loads(
    (ROOT / "graph.json").read_text(encoding="utf-8"))["entities"]}

CANDIDATES = [
    "恐怖通", "牙仙", "维尔汀", "十四行诗", "金蜜儿", "安妮", "杰森",
    "迈克尔", "弗莱迪", "屠夫", "巨大魔精", "变异魔精", "疯癫的老人",
    "男性调查员", "女性调查员", "基金会女职员", "安洁", "道夫", "Z女士",
    "芝诺军备学院", "绿湖营地", "第一防线学校", "圣洛夫基金会",
    "坎贝尔先生", "布鲁诺", "安娜奎尼", "小德利斯", "珍妮弗",
    "车载广播", "小说", "术杖", "绒袋", "蛛网子弹", "粘着子弹",
    "记录者CCD-TR57", "摄影机", "剧本", "樱桃糖浆", "血味素",
    "自制道具", "神秘生物学", "魔精", "恒牙缺失", "诅咒",
    "俄亥俄州", "森林", "营地", "电影", "恐怖电影", "年度突出贡献",
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
for sub in ["牙仙", "坎贝尔", "芝诺", "绿湖", "安妮", "杰森", "迈克尔",
            "弗莱迪", "屠夫", "魔精", "珍妮弗", "金蜜儿", "安洁", "道夫",
            "血味素", "糖浆", "术杖", "绒袋", "子弹", "CCD", "记录者"]:
    print(f"  {sub:10s} -> {[n for n in idx if sub in n][:12]}")
