# -*- coding: utf-8 -*-
"""并集探针（24101_地球上最后的夜晚 第 1 轮，batch217）。"""
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
    "图图石子", "卡穆塔", "托阿", "塞洛尼", "淑女格蕾丝", "无名者",
    "星锑", "APPLe", "爱兹拉", "维尔汀", "无线电小姐", "乌尔里希",
    "芭卡洛儿", "汉米西", "宣传船员", "圆滑的船员", "忧心的船员",
    "街头商人", "街头艺术家", "37", "苏芙比", "布莱恩·梅",
    "吉姆·莫里森", "弗兰克·扎帕",
    # 地点
    "努库泰澳", "麦黎", "马拉尼亚环礁", "以提提", "米缇", "维布那",
    "雪梨港", "悉尼港", "澳大利亚", "拉普拉斯科算中心", "科算中心",
    "箱中一隅", "自由海风号", "丰收满满号", "克赖斯特彻奇",
    # 组织 / 事件
    "拉普拉斯", "司辰小队", "阿派朗学派", "重塑之手", "军方",
    "暴雨专项研究小组", "船商贸易节", "独木舟环岛比赛",
    # 物品 / 概念
    "象形贝壳", "啪唧匣子", "磁流体", "无影无踪雾", "月相招潮蟹",
    "鬼脸螃蟹", "风暴猫", "提克蜗", "魔精", "暴雨", "鱼雷试验场",
    "白皮书", "船票", "传单", "人工泪滴", "计算机", "数独",
    "拉普拉斯命名法", "哈雷彗星", "柯伊伯带阋神星",
]
print("\n=== 候选名判定 ===")
for n in CAND:
    if n in known:
        print(f"  EXISTS {n:24s} resolve={g.resolve(n)!r}")
    elif n in alias_owner:
        print(f"  ALIAS  {n:24s} → {alias_owner[n]}")
    else:
        print(f"  new    {n:24s}")

print("\n=== 近似名 ===")
for sub in ["图图", "卡穆塔", "托阿", "塞洛尼", "格蕾丝", "星锑",
            "APPLe", "爱兹拉", "乌尔里希", "芭卡", "汉米西", "船员",
            "努库", "麦黎", "马拉尼亚", "以提提", "米缇", "维布那",
            "雪梨", "悉尼", "拉普拉斯", "海风", "丰收", "阿派朗",
            "象形", "啪唧", "磁流体", "无影无踪", "招潮", "鬼脸",
            "风暴猫", "提克", "鱼雷", "数独", "哈雷", "阋神"]:
    hits = sorted(x for x in known if sub in x)
    if hits:
        print(f"  {sub:10s} -> {hits[:10]}")
