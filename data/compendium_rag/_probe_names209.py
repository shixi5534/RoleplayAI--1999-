# -*- coding: utf-8 -*-
"""并集探针（21101_77号往事 第 5 轮，batch209）。"""
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
    "维尔汀", "阿尔古斯", "数羊羔", "蓝手帕", "凯拉", "农场女孩凯拉",
    "镜中幽灵", "伊莎贝拉", "圈环", "“圈环”", "镇民Ⅰ", "镇民Ⅱ",
    "丹尼斯", "丹尼斯叔叔", "玛丽", "玛丽姨妈", "爱丽丝", "谢弗先生",
    "阿尔古斯的教练", "百眼巨人",
    # 地点
    "蓝手帕旅馆", "707房", "蓝手帕旅馆707房", "蓝手帕旅馆红房间",
    "红房间", "底特律", "奇索斯", "德州", "德克萨斯", "东部",
    "礼拜堂", "第一防线学校", "洛杉矶",
    # 物品 / 概念
    "襁褓", "苦目糖", "猎枪", "伞", "平衡伞", "请柬", "婴儿床",
    "布帘", "麦酒", "鹰嘴豆泥", "唱诗班", "联合收获机", "收获机",
    "神秘术", "术阵", "都市怪谈", "蛛网", "蜘蛛", "暴雨",
    "UTTU", "圣洛夫基金会", "重塑之手", "受苦者", "启明会",
    "兀尔德", "传记作家兀尔德", "摩斯电码", "客房电话", "电话",
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
for sub in ["镇民", "丹尼斯", "玛丽", "爱丽丝", "谢弗", "伊莎", "圈环",
            "百眼", "底特律", "红房间", "707", "婴儿床", "请柬",
            "收获机", "伞", "暴雨", "都市怪谈", "蜘蛛"]:
    hits = sorted(x for x in known if sub in x)
    if hits:
        print(f"  {sub:8s} -> {hits[:10]}")
