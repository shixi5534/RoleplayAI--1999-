# -*- coding: utf-8 -*-
"""并集探针（24101_地球上最后的夜晚 第 6 轮，batch222）。"""
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
    "星锑", "维尔汀", "十四行诗", "暴雨小组组长乌尔里希", "芭卡洛儿",
    "舵手伊萨姆", "舵手老查理", "舵手乔瓦尼", "舵手众", "托阿", "塞洛尼",
    "图图石子", "卡穆塔", "客人Ⅰ", "客人Ⅱ", "客人Ⅲ", "船员Ⅰ", "船员Ⅱ",
    "琼斯先生", "基蒂欧纳", "小皮塔", "努库泰澳信徒Ⅰ", "努库泰澳信徒Ⅱ",
    "APPLe", "27岁俱乐部",
    # 地点
    "广播室", "监控室", "游轮大厅", "船长室", "舷窗", "海岸基站",
    # 组织
    "重塑之手", "科算中心", "圣洛夫基金会", "国际海事组织",
    "科算中心澳大利亚分部", "暴雨专项研究小组",
    # 物品 / 概念
    "毛毛虫溶剂", "纸莎草毛虫溶剂", "反应堆", "平衡伞", "玻璃缸",
    "前行者Ⅰ号卫星定位系统", "前行者Ⅰ号", "昏睡幻剂", "广播室",
    "思维电流", "时代病", "人工暴雨", "非对称核素R", "声波催化频率",
    "超自然现象发生地", "铂金通灵板", "幼龙舌管", "火蛾脂粉",
    "复制唱片", "星锑的唱片", "棕色噪音", "试炼", "面具",
    "古铜面具", "象形贝壳", "救生艇", "救生", "备用锚",
    "那不勒斯", "二氧化硅", "碳酸钙镁", "氧化铝", "海上",
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
for sub in ["琼斯", "基蒂", "皮塔", "信徒", "广播室", "监控室",
            "海岸", "海事", "昏睡", "幻剂", "思维电流", "通灵板",
            "舌管", "脂粉", "复制唱片", "棕色噪音", "救生", "备用锚",
            "那不勒斯", "前行者", "定位系统", "玻璃缸", "毛毛虫",
            "27岁", "俱乐部"]:
    hits = sorted(x for x in known if sub in x)
    if hits:
        print(f"  {sub:10s} -> {hits[:10]}")
