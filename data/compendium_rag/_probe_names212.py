# -*- coding: utf-8 -*-
"""并集探针（23101_圣火纪行_东区黎明 第 2 轮，batch212）。"""
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
    # 人物（重点：笃笃骨 / 夏洛特·奥黑根 的归并现状）
    "笃笃骨", "夏洛特·奥黑根", "夏洛特", "卡洛琳", "卡洛琳女士",
    "淘气鬼弗洛狄", "弗洛狄", "广播员", "十字街居民", "威尔森太太",
    "莱恩父子商店", "店主", "牙仙", "宽檐帽", "宽檐帽先生",
    "福葛先生", "雾行者", "纸信圈儿", "利伯蒂", "乌鸦教练",
    "德鲁伊", "格拉斯顿伯里", "病人Ⅰ", "病人Ⅱ",
    # 地点
    "十字街", "十字街古宅", "维多利亚古宅", "临时医院",
    "伦敦特殊煤炭肺结核患者应急救助与管理中心", "河岸步道",
    "泰晤士河", "伦敦", "乌卢鲁之岩", "巴黎", "开罗", "伊斯坦布尔",
    "格拉斯顿伯里森林", "爱尔兰",
    # 物品 / 概念
    "假肢", "假腿", "润滑脂", "坩埚", "羊脂蜗牛", "金丝绵雀",
    "自由祭祀", "女巫之舞", "乌卢鲁预选赛", "乌卢鲁运动会",
    "铜牌", "奖牌", "金牌", "花种", "黑雾", "煤炭肺结核",
    "魔精", "花园魔精", "神秘术", "夏末节",
]
print("\n=== 候选名判定 ===")
for n in CAND:
    if n in known:
        print(f"  EXISTS {n:28s} resolve={g.resolve(n)!r}")
    elif n in alias_owner:
        print(f"  ALIAS  {n:28s} → {alias_owner[n]}")
    else:
        print(f"  new    {n:28s}")

print("\n=== 近似名 ===")
for sub in ["笃笃骨", "夏洛特", "卡洛琳", "弗洛狄", "广播员", "居民",
            "威尔森", "莱恩", "乌鸦", "德鲁伊", "格拉斯顿", "假肢",
            "润滑脂", "坩埚", "自由祭祀", "奖牌", "花种", "泰晤士"]:
    hits = sorted(x for x in known if sub in x)
    if hits:
        print(f"  {sub:10s} -> {hits[:10]}")
