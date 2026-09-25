# -*- coding: utf-8 -*-
"""并集探针（23101_圣火纪行_东区黎明 第 1 轮，batch211）。"""
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
    "牙仙", "纸信圈儿", "奇奇比翁", "福葛先生", "福葛", "威尔",
    "宽檐帽", "宽檐帽先生", "司机", "Z女士", "Z", "伦敦雾行者",
    "“麻布袋”", "麻布袋", "“老帽儿”", "老帽儿", "维多利亚",
    # 地点
    "伦敦", "十字街", "东区", "伦敦清洁大气委员会", "古宅",
    "女巫的古宅", "十字街古宅", "基金会办公室", "第一防线学校",
    "伦敦分部", "圣洛夫基金会伦敦分部", "贝克街221号", "澳洲",
    "澳大利亚", "乌卢鲁", "巴黎",
    # 组织
    "圣洛夫基金会", "基金会", "乌卢鲁运动会", "乌卢鲁伦敦预选赛",
    "乌卢鲁预选赛", "乌卢鲁欢庆集市", "十字街集市",
    # 物品 / 概念
    "黑雾", "黑色的雾气", "煤炭肺结核", "肺结核", "雾中鬼婆",
    "煤烟卡邦克鲁", "花园卡邦克鲁", "卡邦克鲁", "魔精",
    "金丝绵雀", "羊脂蜗牛", "蜗牛", "有声信", "神秘学家集市信息报备表",
    "报备表", "传单", "乌卢鲁传单", "药膏", "太妃糖", "奶糖",
    "棍马", "帽针", "炼金术士", "炼金术", "神秘术", "暴雨",
    "爱尔兰威士忌", "地铁", "印度红茶",
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
for sub in ["牙仙", "纸信", "奇奇", "福葛", "威尔", "宽檐帽", "司机",
            "十字街", "乌卢鲁", "卡邦克鲁", "黑雾", "肺结核", "鬼婆",
            "金丝绵", "蜗牛", "有声信", "报备", "麻布袋", "老帽",
            "大气委员会", "雾行者", "维多利亚"]:
    hits = sorted(x for x in known if sub in x)
    if hits:
        print(f"  {sub:10s} -> {hits[:10]}")
