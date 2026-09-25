# -*- coding: utf-8 -*-
"""并集探针（21101_77号往事 收官轮，batch210）。"""
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
    # 人物
    "维尔汀", "阿尔古斯", "凯拉", "农场女孩凯拉", "镜中幽灵", "蓝手帕",
    "数羊羔", "红弩箭", "金伯利女郎", "无名者", "淑女格蕾丝",
    "丹尼斯叔叔", "玛丽姨妈", "Z女士", "Z", "史蒂文", "伊戈尔将军",
    "伊戈尔", "基金会职员Ⅰ", "基金会职员Ⅱ", "阿尔卡纳",
    # 地点
    "蓝手帕旅馆", "蓝手帕旅馆203房", "圣洛夫基金会办公室",
    "圣保罗荣军院", "荣军院", "奇索斯", "德克萨斯", "军备工厂",
    "奇索斯的军备工厂", "温馨之家",
    # 物品 / 概念
    "襁褓", "手提箱", "传送术式", "传送软盘", "笔记本",
    "请柬", "猎枪", "苦目糖", "伞", "平衡伞", "真空弹",
    "神秘学意识", "都市怪谈", "术阵", "启明会", "重塑之手",
    "圣洛夫基金会", "UTTU", "兀尔德", "传记作家兀尔德", "受苦者",
    "暴雨", "镜子",
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
for sub in ["职员", "温馨", "203", "办公室", "圣保罗", "荣军院",
            "传送", "笔记本", "阿尔卡纳", "伊戈尔", "史蒂文"]:
    hits = sorted(x for x in known if sub in x)
    if hits:
        print(f"  {sub:8s} -> {hits[:10]}")
