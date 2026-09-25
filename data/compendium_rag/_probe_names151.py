# -*- coding: utf-8 -*-
"""只读探针（batch151）：核对候选实体名是否已在 graph.json 中。"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
idx = {e["name"]: e for e in json.loads(
    (ROOT / "graph.json").read_text(encoding="utf-8"))["entities"]}

CANDIDATES = [
    # 1921 尾
    "泥鯭的士", "恐怖通", "Z", "马库斯", "包租婆", "租客", "租客Ⅱ",
    "圣洛夫基金会", "基金会办公室", "基金会走廊", "唐人街",
    "新科学除灵驱鬼事务所", "红包", "信封",
    # 1922
    "贝蒂", "琼斯", "劳拉", "女性职员I", "女性职员II", "餐馆老板",
    "魔术师", "护士", "剧组", "1930年代",
    "圣洛夫基金会客房", "基金会会议室", "病房", "储物间", "议事厅",
    "好莱坞", "希尔顿",
    "摄影机", "玻璃棺", "表格", "文件夹", "防护绳", "高帽", "文明棍",
    "胡佛炖菜", "假胡子", "面具", "盐酸氯丙嗪", "保险丝",
    "暴雨", "暴雨症候", "神秘术", "替身演员", "铜吊坠", "收容流程",
    "说明会", "幸存者", "时代",
]

print("=== already in graph ===")
for c in CANDIDATES:
    e = idx.get(c)
    if e:
        print(f"  YES  {c:20s} type={e['type']:4s} m={e['mentions']:4d} "
              f"aliases={e['aliases']} desc={e['desc']!r}")

print()
print("=== NOT in graph ===")
for c in CANDIDATES:
    if c not in idx:
        print(f"  no   {c}")

print()
print("=== fuzzy ===")
for sub in ["贝蒂", "琼斯", "劳拉", "马库斯", "职员", "租客", "餐馆",
            "摄影机", "玻璃棺", "表格", "胡佛", "氯丙嗪", "保险丝",
            "替身", "吊坠", "收容", "说明会", "幸存", "好莱坞", "希尔顿"]:
    print(f"  {sub:10s} -> {[n for n in idx if sub in n][:12]}")
