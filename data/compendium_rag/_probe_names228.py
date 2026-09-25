# -*- coding: utf-8 -*-
"""并集探针（25101_唐人街影话 第 5 轮，batch228）。"""
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
    "梁月", "波蒂埃", "斯考特", "空脑袋", "菲林士多", "奇星",
    "癞皮狗", "泰瑞莎", "何日君", "记者", "男子", "女孩", "男孩",
    "黑檀木戒尺", "小猪存钱罐", "梁父", "录像厅",
    # 地点
    "唐人街", "洛杉矶", "小巷", "唐人街小巷", "警车", "录像厅",
    "神秘学犯罪科", "广府饭店",
    # 组织
    "圣洛夫基金会", "神秘学藏品管理部", "神秘学犯罪科", "夜巡特遣",
    "夜巡特遣管理局", "梁家",
    # 物品 / 概念
    "三燕归巢", "被诅咒的胶片", "超8毫米胶片", "放映", "重摄",
    "神秘学管理品", "发条玩具", "银针神秘术", "强梁", "险道兽",
    "祭器", "静谧无声", "神秘术", "SPF-I型便携联络装置",
    "金属变色龙通信器", "片盘", "映像事件", "暴雨", "社火游行",
    "C07", "神秘学警探C07", "诅咒", "封印物",
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
for sub in ["癞皮狗", "泰瑞莎", "记者", "存钱罐", "戒尺", "录像厅",
            "放映", "重摄", "祭器", "静谧", "癞皮", "片盘", "雪佛兰",
            "斯考特", "奇星", "空脑袋"]:
    hits = sorted(x for x in known if sub in x)
    if hits:
        print(f"  {sub:10s} -> {hits[:10]}")
