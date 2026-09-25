# -*- coding: utf-8 -*-
"""并集探针（24101_地球上最后的夜晚 第 5 轮，batch221）。"""
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
    "无名者", "淑女格蕾丝", "勿忘我", "图图石子", "卡穆塔", "托阿",
    "塞洛尼", "芭卡洛儿", "星锑", "维尔汀", "十四行诗",
    "暴雨小组组长乌尔里希", "客人Ⅰ", "客人Ⅱ", "客人Ⅲ", "客人Ⅳ",
    "客人Ⅴ", "客人众", "尤金先生", "马修先生", "艾琳娜小姐",
    "卡米拉女士", "惶恐的客人", "愤怒的客人", "犹豫的客人",
    "激进的客人", "胆怯的孩子", "成功的选民Ⅰ", "成功的选民Ⅱ",
    "失败的选民Ⅰ", "失败的选民Ⅱ", "无知的孩子", "痛苦的母亲",
    "惶恐的船员", "惊讶的船员", "舵手伊萨姆", "舵手老查理",
    "舵手乔瓦尼", "舵手Ⅳ",
    # 地点
    "克雷莫纳", "热那亚", "鹿特丹", "哥本哈根", "比雷埃夫斯",
    "悉尼港", "意大利", "暗礁区", "冷库", "临时监牢",
    "船员休息室", "电力供应室", "船长室", "机械室",
    # 组织 / 概念
    "重塑之手", "圣洛夫基金会", "科算中心", "司辰小队",
    "意识唤醒者", "时代病", "暴雨", "大筛选", "面具试炼",
    "象形贝壳", "重塑仪式", "传送术阵", "平衡伞", "箱子",
    # 物品
    "采集仪", "非对称核素R采集仪", "数据箱", "反应堆",
    "纸莎草毛虫溶剂", "安睡芦苇", "古铜色面具", "面具",
    "手表", "怀表", "啪唧匣子", "小提琴", "通讯器", "船舱广播",
    "托尔塔蛋糕", "奶酪烩饭",
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
for sub in ["勿忘我", "尤金", "艾琳娜", "卡米拉", "选民", "舵手",
            "热那亚", "鹿特丹", "哥本哈根", "比雷埃夫斯", "暗礁",
            "冷库", "监牢", "休息室", "时代病", "采集仪", "数据箱",
            "反应堆", "毛虫", "安睡", "手表", "小提琴", "广播",
            "托尔塔", "奶酪", "箱子", "平衡伞", "意识唤醒者"]:
    hits = sorted(x for x in known if sub in x)
    if hits:
        print(f"  {sub:10s} -> {hits[:10]}")
