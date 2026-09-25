# -*- coding: utf-8 -*-
"""并集探针（23101_圣火纪行_东区黎明 第 3 轮，batch213）。"""
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
    "笃笃骨", "夏洛特·奥黑根", "牙仙", "纸信圈儿", "利伯蒂", "卡洛琳",
    "宽檐帽", "宽檐帽先生", "福葛先生", "雾行者", "威尔",
    "无线电广播", "广播员", "巡逻警察Ⅰ", "巡逻警察Ⅱ", "街坊Ⅰ", "街坊Ⅱ",
    "摊贩", "小丽莎", "护士", "马蒂姑姑", "零零七号穆尔森", "穆尔森",
    "苏利丝", "白天鹅", "水手", "巴拉奈婆婆", "病人Ⅰ", "病人Ⅱ",
    # 地点
    "十字街", "十字街古宅", "临时医院", "花园", "南约克郡",
    "蒂尔伯里码头", "伦敦", "贝尔丹", "治安局",
    # 组织 / 事件
    "圣洛夫基金会", "乌卢鲁运动会", "乌卢鲁伦敦预选赛", "自由祭祀",
    "巡逻警察", "清洁大气委员会", "伦敦清洁大气委员会",
    "贝尔丹火焰节", "沙漠祭祀公开赛", "极光杯世界锦标赛",
    # 物品 / 概念
    "假肢", "润滑脂", "坩埚", "蜗牛", "羊脂蜗牛", "金丝绵雀",
    "神秘术", "黑雾", "煤炭肺结核", "魔精", "花园魔精",
    "吸尘器", "伦敦煤烟污染勘察与清除大使", "雾气净化器",
    "麻绳", "夜壶", "大喇叭", "玻璃鱼缸", "黑雨伞", "彩带",
    "油画", "火车票",
]
print("\n=== 候选名判定 ===")
for n in CAND:
    if n in known:
        print(f"  EXISTS {n:30s} resolve={g.resolve(n)!r}")
    elif n in alias_owner:
        print(f"  ALIAS  {n:30s} → {alias_owner[n]}")
    else:
        print(f"  new    {n:30s}")

print("\n=== 近似名 ===")
for sub in ["警察", "街坊", "摊贩", "丽莎", "护士", "马蒂", "穆尔森",
            "苏利丝", "白天鹅", "水手", "巴拉奈", "约克郡", "蒂尔伯里",
            "贝尔丹", "治安", "吸尘器", "麻绳", "夜壶", "雨伞", "彩带",
            "油画", "使者"]:
    hits = sorted(x for x in known if sub in x)
    if hits:
        print(f"  {sub:10s} -> {hits[:10]}")
