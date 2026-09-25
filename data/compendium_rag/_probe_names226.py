# -*- coding: utf-8 -*-
"""并集探针（25101_唐人街影话 第 3 轮，batch226）。"""
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
    "玛蒂尔达", "斯考特", "康斯坦丝·斯考特", "佩德拉", "莱瑟姆",
    "何日君", "王琳", "琳·王", "菲林士多", "梁月", "波蒂埃",
    "奇星", "老板娘", "助理", "演员Ⅰ", "演员Ⅱ", "工作人员",
    "围观群众", "龙套演员", "群众演员", "系统音", "商贩", "游客",
    "唐人街居民", "孩童", "Z", "维尔汀", "民间侦探", "傀儡师",
    # 地点
    "神秘学藏品管理部", "神秘学藏品管理室", "唐人街", "洛杉矶",
    "香港", "旧金山", "广府饭店", "片场", "牌坊", "荷里活",
    "唐人街小巷", "唐人街小巷·昼",
    # 组织
    "圣洛夫基金会", "夜巡特遣", "夜巡特遣管理局", "拉普拉斯",
    "第一防线学校", "新科学事务所", "除灵事务所",
    # 物品 / 概念
    "沛霖川", "三燕归巢", "映像事件", "被诅咒的胶片", "超8毫米胶片",
    "神秘学管理品", "AN-003", "SPF-I型便携联络装置",
    "金属变色龙通信器", "徽章", "威胁信", "银针神秘术", "飞针神秘术",
    "强梁", "度朔节", "社火游行", "暴雨", "神秘术", "诅咒",
    "大白鸟", "中药铺", "洋娃娃", "轮椅",
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
for sub in ["斯考特", "佩德拉", "莱瑟姆", "何日君", "王琳", "香港",
            "旧金山", "广府", "片场", "牌坊", "荷里活", "第一防线",
            "新科学", "除灵", "沛霖", "三燕", "映像", "胶片", "管理品",
            "联络装置", "威胁信", "老板娘", "助理", "傀儡", "大白鸟",
            "中药铺", "轮椅", "社火"]:
    hits = sorted(x for x in known if sub in x)
    if hits:
        print(f"  {sub:10s} -> {hits[:10]}")
