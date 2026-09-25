# -*- coding: utf-8 -*-
"""并集探针（25101_唐人街影话 第 6 轮，batch229）。"""
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
    "梁父", "阿星", "老板", "混混Ⅰ", "混混Ⅱ", "癞皮狗",
    "神秘学警察Ⅰ", "神秘学警察Ⅱ", "埃尔登警长", "民间侦探",
    "泥鯭的士", "周叔", "老周", "詹姆斯", "卡特", "男子", "女子",
    "鉴识科", "行为分析科",
    # 地点
    "广府饭店", "香港", "唐人街", "洛杉矶", "社火游行现场",
    # 组织
    "神秘学犯罪科", "夜巡特遣", "圣洛夫基金会", "神秘学藏品管理部",
    "新艺术公司", "电影学院", "逐疫队",
    # 物品 / 概念
    "三燕归巢", "被诅咒的胶片", "神秘学管理品", "C07", "神秘学警探C07",
    "威胁信", "初版剧本", "社火游行", "度朔节", "宣传海报",
    "三人合照", "文件袋", "糊涂", "奇星的真实身份",
    "银针神秘术", "强梁", "险道兽", "祭器", "神秘术", "暴雨",
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
for sub in ["阿星", "混混", "泥鯭", "周叔", "老周", "詹姆斯", "卡特",
            "鉴识", "行为分析", "新艺术", "电影学院", "逐疫", "糊涂",
            "合照", "文件袋", "初版", "宣传海报", "CLOSE", "老板"]:
    hits = sorted(x for x in known if sub in x)
    if hits:
        print(f"  {sub:10s} -> {hits[:10]}")
