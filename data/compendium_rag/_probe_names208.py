# -*- coding: utf-8 -*-
"""并集探针（21101_77号往事 第 4 轮，batch208）。"""
import json
import sys
from pathlib import Path

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
    for blk in data.values():
        for e in blk.get("entities", []):
            n = e.get("name")
            if n:
                known.add(n)
            for a in (e.get("aliases") or []):
                alias_owner.setdefault(a, n)

print(f"图谱实体 {len(g.entities)}｜batch {len(batch_files)}｜并集 {len(known)}")

CAND = [
    # 角色
    "士兵", "安德烈", "一等列兵安德烈", "看守军备工厂的士兵",
    "红弩箭", "维尔汀", "阿尔古斯", "金伯利女郎", "蓝手帕", "史蒂文",
    "玛蒂尔达", "数羊羔", "伊戈尔将军", "迈克·柯里昂",
    # 地点
    "蓝手帕旅馆", "707房", "蓝手帕旅馆707房", "蓝手帕旅馆盥洗室",
    "奇索斯", "军备工厂", "奇索斯的军备工厂", "德克萨斯",
    # 物品 / 概念
    "苦目糖", "猎枪", "告示牌", "账单", "药物清单", "重力术式",
    "血腥玛丽", "镜子里的幽灵", "幽灵", "镜中幽灵", "镜子",
    "《教父》", "教父", "二部曲式", "酒壶", "纸条", "糖果包装纸",
    "摩斯电码", "传送仪式", "黑烟", "术阵", "神秘术",
    "受苦者", "启明会", "重塑之手", "圣洛夫基金会", "芝诺",
    "红色38", "襁褓", "客房电话", "电话",
]
print("\n=== 候选名判定 ===")
for n in CAND:
    if n in known:
        print(f"  EXISTS {n:22s} resolve={g.resolve(n)!r}")
    elif n in alias_owner:
        print(f"  ALIAS  {n:22s} → {alias_owner[n]}")
    else:
        print(f"  new    {n:22s}")

print("\n=== 近似名 ===")
for sub in ["士兵", "安德烈", "列兵", "苦目", "猎枪", "告示", "账单",
            "药物", "血腥", "幽灵", "镜子", "教父", "柯里昂", "酒壶",
            "糖果", "传送", "707", "盥洗", "玛蒂尔达", "伊戈尔"]:
    hits = sorted(x for x in known if sub in x)
    if hits:
        print(f"  {sub:8s} -> {hits[:8]}")
