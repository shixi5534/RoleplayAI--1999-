# -*- coding: utf-8 -*-
"""并集探针（25101_唐人街影话 第 4 轮，batch227）。"""
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
    "梁月", "波蒂埃", "斯考特", "空脑袋", "莱瑟姆", "佩德拉",
    "天使娜娜", "菲林士多", "王琳", "老板娘", "演员", "演员Ⅰ",
    "演员Ⅱ", "工作人员", "龙套演员", "阿琳", "凯斯", "刘老师",
    "肇事司机", "维尔汀", "梁家", "Z",
    # 地点
    "旅店房间", "星光大道", "广府饭店", "片场", "更衣间",
    "神秘学藏品管理部", "唐人街", "洛杉矶", "香港", "启明会",
    # 组织
    "圣洛夫基金会", "夜巡特遣", "夜巡特遣管理局", "拉普拉斯科算中心",
    "重塑之手", "第一防线学校",
    # 物品 / 概念
    "记忆胶片", "三燕归巢", "被诅咒的胶片", "发条玩具",
    "神秘学管理品", "NO.066", "SPF-I型便携联络装置",
    "金属变色龙通信器", "徽章", "强梁", "险道兽", "社火游行",
    "度朔节", "神偶", "神轿", "剧本", "台词", "龙虎武师",
    "映像事件", "神秘术", "暴雨", "莱瑟姆环路", "封印物",
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
for sub in ["空脑袋", "莱瑟姆", "娜娜", "启明会", "发条", "NO.066",
            "记忆胶片", "星光大道", "旅店", "更衣", "凯斯", "刘老师",
            "肇事", "阿琳", "环路", "封印", "神偶", "神轿", "剧本",
            "龙虎", "仓鼠", "歪头", "仓鼠骑"]:
    hits = sorted(x for x in known if sub in x)
    if hits:
        print(f"  {sub:10s} -> {hits[:10]}")
