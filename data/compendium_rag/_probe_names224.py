# -*- coding: utf-8 -*-
"""并集探针（25101_唐人街影话 第 1 轮，batch224）。"""
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
    "梁月", "梁父", "强梁", "险道兽", "方相氏", "侲子", "梁家",
    "波蒂埃", "艾丽娅·波蒂埃", "神秘学警察Ⅰ", "神秘学警察Ⅱ",
    "埃尔登警长", "埃尔登", "针人", "棍骗约翰", "C07", "菲林士多",
    "乔什", "调度中心", "市民Ⅰ", "市民Ⅱ", "老警察", "男子", "人质",
    "夜巡特遣管理局", "见习执夜人", "新巴别塔",
    # 地点
    "洛杉矶", "唐人街", "市政大厅", "警长办公室", "餐馆",
    "洛杉矶·神秘学犯罪科", "洛杉矶·街道", "神秘学犯罪科",
    "东亚分部", "圣洛夫基金会东亚分部",
    # 组织 / 概念
    "圣洛夫基金会", "夜巡特遣", "夜巡特遣管理局", "科算中心",
    "拉普拉斯科算中心", "慢慢吞", "提线魔咒", "拟影魔咒",
    "飞针神秘术", "基础神秘学警情", "神秘学警探C07",
]
print("\n=== 候选名判定 ===")
for n in CAND:
    if n in known:
        print(f"  EXISTS {n:26s} resolve={g.resolve(n)!r}")
    elif n in alias_owner:
        print(f"  ALIAS  {n:26s} → {alias_owner[n]}")
    else:
        print(f"  new    {n:26s}")

print("\n=== 近似名 ===")
for sub in ["梁月", "梁父", "强梁", "险道", "方相", "波蒂埃", "埃尔登",
            "针人", "棍骗", "C07", "菲林", "乔什", "夜巡", "见习",
            "慢慢吞", "洛杉矶", "唐人街", "市政", "警长", "餐馆",
            "新巴别塔", "提线", "拟影", "飞针", "东亚分部"]:
    hits = sorted(x for x in known if sub in x)
    if hits:
        print(f"  {sub:10s} -> {hits[:10]}")
