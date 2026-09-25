# -*- coding: utf-8 -*-
"""并集探针（25101_唐人街影话 第 7 轮，batch230）。"""
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
    "梁月", "波蒂埃", "空脑袋", "菲林士多", "奇星", "何日君",
    "泥鯭的士", "民间侦探", "埃尔登警长", "神秘学警察Ⅰ",
    "神秘学警察Ⅱ", "詹姆斯", "警员詹姆斯", "斯考特", "游客",
    "唐人街居民", "孩童", "Lily", "香港小姑娘",
    # 地点
    "唐人街", "洛杉矶", "巷", "广府饭店", "荷里活", "香港",
    "胶片领域", "神秘学犯罪科", "餐馆",
    # 组织
    "神秘学犯罪科", "夜巡特遣", "夜巡特遣管理局", "圣洛夫基金会",
    "神秘学藏品管理部", "A组", "B组", "C组", "梁家",
    # 物品 / 概念
    "三燕归巢", "被诅咒的胶片", "放映", "重摄", "社火游行",
    "神秘学管理品", "银针神秘术", "强梁", "险道兽", "神秘术",
    "金属蜥蜴通信器", "SPF-I型便携联络装置", "特制子弹",
    "生魂", "三魂七魄", "诱饵", "谈判技巧", "雨", "诅咒",
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
for sub in ["Lily", "百合", "胶片领域", "生魂", "三魂", "七魄",
            "特制子弹", "蜥蜴", "诱饵", "谈判", "A组", "B组", "C组",
            "詹姆斯", "香港小姑娘"]:
    hits = sorted(x for x in known if sub in x)
    if hits:
        print(f"  {sub:12s} -> {hits[:10]}")
