# -*- coding: utf-8 -*-
"""并集探针（21101_77号往事 第 2 轮，batch206）。"""
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT.parent.parent / "src"))
from compendium_rag.graph_store import GraphStore  # noqa: E402

g = GraphStore.load(ROOT / "graph.json")
known = set(g.entities)
alias_owner = {}
for e in g.entities.values():
    for a in e.aliases:
        alias_owner.setdefault(a, e.name)

batch_files = sorted(ROOT.glob("_agent_batch*.json"))
for bf in batch_files:
    try:
        data = json.loads(bf.read_text(encoding="utf-8"))
    except Exception:
        continue
    for key, blk in data.items():
        for e in blk.get("entities", []):
            n = e.get("name")
            if n:
                known.add(n)
            for a in (e.get("aliases") or []):
                alias_owner.setdefault(a, n)

print(f"图谱实体 {len(g.entities)}｜batch {len(batch_files)}｜并集 {len(known)}")

CAND = [
    # 角色
    "史蒂文", "史蒂文先生", "金伯利女郎", "女房客", "Z女士",
    "十四行诗", "教员", "莉莉娅", "阿尔古斯", "维尔汀", "红弩箭",
    "蓝手帕", "奇索斯镇的凯拉", "酒吧老板", "奇索斯酒吧老板",
    "客人Ⅰ", "客人Ⅱ", "酒吧客人Ⅰ", "酒吧客人Ⅱ", "众",
    # 地点
    "第一防线学校", "奇索斯的军备工厂", "军备工厂", "奇索斯",
    "蓝手帕旅馆", "奇索斯酒吧", "酒吧", "走廊", "前台", "207房",
    # 物品/概念
    "电话机", "客房电话", "电话", "密电", "摩斯电码", "术阵",
    "神秘术", "受苦者", "重力术式", "红色38", "地图", "护照",
    "通讯器", "信号塔", "戒指", "襁褓", "魔精", "数羊羔", "UTTU",
    "启明会", "芝诺士兵", "圣洛夫基金会", "德克萨斯", "77号公路",
]
print("\n=== 候选名判定 ===")
for n in CAND:
    if n in known:
        print(f"  EXISTS {n:16s} resolve={g.resolve(n)!r}")
    elif n in alias_owner:
        print(f"  ALIAS  {n:16s} → {alias_owner[n]}")
    else:
        print(f"  new    {n:16s}")

print("\n=== 近似名 ===")
for sub in ["史蒂文", "金伯利", "Z女士", "女房客", "莉莉", "凯拉",
            "酒吧", "客人", "电话", "密电", "摩斯", "重力", "术阵",
            "受苦", "军备", "客房"]:
    hits = sorted(x for x in known if sub in x)
    if hits:
        print(f"  {sub:8s} -> {hits[:10]}")
