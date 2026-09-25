# -*- coding: utf-8 -*-
"""并集探针（21101_77号往事 第 3 轮，batch207）。"""
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
    "阿尔古斯", "维尔汀", "金伯利女郎", "蓝手帕", "史蒂文", "红弩箭",
    "数羊羔", "农场女孩凯拉", "酒吧老板",
    # 地点
    "蓝手帕旅馆", "214房", "蓝手帕旅馆214房", "蓝手帕旅馆207房",
    "奇索斯酒吧", "德克萨斯", "奇索斯",
    # 物品 / 概念
    "羊皮手册", "炼金术", "术阵", "血痂", "飞矢M1903式手枪",
    "飞矢M1903手枪", "手枪", "吼狮", "垃圾桶", "信纸", "信",
    "真空弹", "神秘术", "重力术式", "电话机", "客房电话",
    "蜘蛛", "水渍", "手掌", "红色门扉", "红色的门扉", "请勿打扰",
    "受苦者", "启明会", "重塑之手", "圣洛夫基金会", "基金会",
    "芝诺", "行李箱", "手提箱", "门铃", "猫眼", "地毯", "枕头",
]
print("\n=== 候选名判定 ===")
for n in CAND:
    if n in known:
        print(f"  EXISTS {n:20s} resolve={g.resolve(n)!r}")
    elif n in alias_owner:
        print(f"  ALIAS  {n:20s} → {alias_owner[n]}")
    else:
        print(f"  new    {n:20s}")

print("\n=== 近似名 ===")
for sub in ["羊皮", "手册", "炼金", "血痂", "手枪", "飞矢", "吼狮",
            "垃圾桶", "信纸", "真空弹", "蜘蛛", "水渍", "手掌", "门扉",
            "214", "207", "203", "手提箱", "行李箱", "猫眼"]:
    hits = sorted(x for x in known if sub in x)
    if hits:
        print(f"  {sub:8s} -> {hits[:8]}")
