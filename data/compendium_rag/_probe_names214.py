# -*- coding: utf-8 -*-
"""并集探针（23101_圣火纪行_东区黎明 第 4 轮，batch214）。"""
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
    "笃笃骨", "夏洛特·奥黑根", "纸信圈儿", "利伯蒂", "卡洛琳", "牙仙",
    "宽檐帽", "宽檐帽先生", "福葛先生", "雾行者", "威尔",
    "淘气鬼弗洛狄", "艾丽卡婆婆", "基顿小子", "基金会分部成员Ⅰ",
    "基金会分部成员Ⅱ", "码头工人", "众人", "无线电广播",
    # 地点
    "十字街", "十字街古宅", "十字街联合协会", "运动场", "会场",
    "伦敦", "澳洲总会场", "澳洲", "爱尔兰", "基顿闹腾商店",
    "巴特利家", "水龙头",
    # 组织 / 事件
    "圣洛夫基金会", "乌卢鲁运动会", "乌卢鲁伦敦预选赛",
    "乌卢鲁联合组委会", "自由祭祀", "运动会",
    # 物品 / 概念
    "术杖", "假肢", "坩埚", "润滑脂", "迪吉里木", "天竺葵",
    "报名表", "挑战书", "起司蛋糕", "煤灰魔精", "魔精", "黑雾",
    "神秘术", "神秘学", "黑雾", "机器", "雾气净化器",
    "伦敦煤烟污染勘察与清除大使", "计量仪", "玻璃丝塞子",
    "拖车", "海报", "彩带", "油画", "壁钟", "面包总管",
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
for sub in ["联合协会", "迪吉", "分部成员", "艾丽卡", "基顿", "码头工人",
            "众人", "运动场", "会场", "组委会", "总会场", "术杖",
            "天竺葵", "报名表", "挑战书", "起司", "煤灰", "计量仪",
            "塞子", "拖车", "海报", "壁钟", "面包"]:
    hits = sorted(x for x in known if sub in x)
    if hits:
        print(f"  {sub:10s} -> {hits[:10]}")
