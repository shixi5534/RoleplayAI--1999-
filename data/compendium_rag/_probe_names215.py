# -*- coding: utf-8 -*-
"""并集探针（23101_圣火纪行_东区黎明 第 5 轮，batch215）。"""
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
    "笃笃骨", "纸信圈儿", "利伯蒂", "卡洛琳", "牙仙", "宽檐帽",
    "宽檐帽先生", "福葛先生", "雾行者", "威尔", "淘气鬼弗洛狄",
    "巡逻警察Ⅰ", "街坊Ⅰ", "街坊Ⅱ", "工人Ⅰ", "工人Ⅱ",
    "基金会分部成员Ⅰ", "基金会分部成员Ⅱ", "格里戈尔", "护士",
    "病人Ⅰ", "病人Ⅱ", "路人Ⅰ", "路人Ⅱ", "路人Ⅲ", "伦纳德",
    # 地点
    "十字街", "十字街古宅", "会场", "运动场", "办公室",
    "老钟塔", "塔楼", "十字街塔楼", "医护站", "澳洲",
    "伦敦", "商业街", "东区",
    # 组织 / 事件
    "圣洛夫基金会", "乌卢鲁运动会", "乌卢鲁伦敦预选赛",
    "乌卢鲁联合组委会", "乌卢鲁国际联合组委会", "自由祭祀",
    "贝尔丹火焰节", "民间运动会", "十字街运动会",
    "伦敦清洁大气委员会", "管理局",
    # 物品 / 概念
    "雾气净化器", "机械肺", "黑雾", "魔精", "煤炭肺结核",
    "培养皿", "玻璃瓶", "笔记本", "白被单", "请愿信", "赔偿申请表",
    "乳牙", "金鱼", "术杖", "假肢", "润滑脂", "广告牌",
    "开幕会舞台", "观众席", "望远镜", "话筒",
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
for sub in ["钟塔", "塔楼", "医护", "工作站", "格里戈尔", "伦纳德",
            "路人", "工人", "管理局", "民间", "机械肺", "培养皿",
            "玻璃瓶", "被单", "请愿", "赔偿", "乳牙", "金鱼",
            "广告牌", "舞台", "观众席", "话筒", "商业街"]:
    hits = sorted(x for x in known if sub in x)
    if hits:
        print(f"  {sub:10s} -> {hits[:10]}")
