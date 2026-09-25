# -*- coding: utf-8 -*-
"""并集探针（25101_唐人街影话 第 2 轮，batch225）。"""
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
    "梁月", "波蒂埃", "棍骗约翰", "老警察", "青年警察", "男子",
    "人质", "奇星", "艾瑞克·黄", "丽莲·刘", "民间侦探", "女子",
    "医生", "值班医生", "医护人员", "玛蒂尔达", "菲林士多",
    "神秘学警察Ⅰ", "神秘学警察Ⅱ", "埃尔登警长",
    # 地点
    "市政大厅", "医院", "病房", "拉普拉斯康复中心合作医院",
    "唐人街", "洛杉矶", "蔬菜店", "神秘学犯罪科", "警长办公室",
    # 组织
    "圣洛夫基金会", "夜巡特遣管理局", "神秘学藏品管理部",
    "夜巡特遣", "拉普拉斯康复中心", "神秘学犯罪科",
    # 物品 / 概念
    "强梁", "银针神秘术", "飞针神秘术", "度朔节", "社火游行",
    "金属变色龙通信器", "自动贩卖机", "徽章", "手铐", "利刃",
    "神秘术", "橙汁", "硬币", "变身术", "仓鼠骑听诊器",
    "神秘学警探C07", "C07", "针人", "基础神秘学警情",
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
for sub in ["奇星", "艾瑞克", "丽莲", "民间侦探", "玛蒂尔达", "医生",
            "值班", "病房", "医院", "康复中心", "度朔", "社火", "银针",
            "变色龙", "贩卖机", "徽章", "藏品管理", "蔬菜", "仓鼠"]:
    hits = sorted(x for x in known if sub in x)
    if hits:
        print(f"  {sub:10s} -> {hits[:10]}")
