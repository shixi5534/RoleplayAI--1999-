# -*- coding: utf-8 -*-
"""并集探针（24101_地球上最后的夜晚 第 4 轮，batch220）。"""
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
    "无名者", "淑女格蕾丝", "图图石子", "卡穆塔", "托阿", "塞洛尼",
    "芭卡洛儿", "星锑", "维尔汀", "十四行诗", "客人Ⅰ", "客人Ⅱ",
    "客人Ⅲ", "客人Ⅳ", "客人众", "马修先生", "重塑·门徒",
    "助手小姐", "舵手伊萨姆", "舵手老查理", "舵手乔瓦尼",
    # 地点
    "船长室", "克雷莫纳", "努库泰澳岛", "麦黎", "柏林", "伦敦",
    "格拉茨", "费拉拉", "乌普萨拉", "自由海风号", "机械室",
    "舞台帘幕", "下层甲板", "甲板",
    # 组织
    "重塑之手", "圣洛夫基金会", "司辰小队", "科算中心", "游轮乐队",
    # 物品 / 概念
    "诺亚方舟", "象形贝壳", "啪唧匣子", "唱片机", "星锑的唱片",
    "罗盘灼灼", "怀表", "面具", "古铜色面具", "船员守则",
    "叩门飞匙赛", "暴雨", "大筛选", "面具试炼", "乡愁",
    "非对称核素R", "非对称核素R检测仪", "声波频率", "竹制利箭",
    "毒箭", "敲击锤", "信号灯", "扫帚", "抛绳", "琴颈",
    "小东西", "唱片", "游轮宣传传单",
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
for sub in ["克雷莫纳", "马修", "门徒", "助手", "诺亚", "怀表", "面具",
            "守则", "叩门", "试炼", "乡愁", "检测仪", "声波", "利箭",
            "毒箭", "敲击", "信号灯", "扫帚", "抛绳", "机械室", "甲板",
            "柏林", "格拉茨", "费拉拉", "乌普萨拉", "客人"]:
    hits = sorted(x for x in known if sub in x)
    if hits:
        print(f"  {sub:10s} -> {hits[:10]}")
