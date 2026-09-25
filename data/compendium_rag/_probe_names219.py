# -*- coding: utf-8 -*-
"""并集探针（24101_地球上最后的夜晚 第 3 轮，batch219）。"""
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
    "芭卡洛儿", "星锑", "图图石子", "托阿", "塞洛尼", "十四行诗",
    "维尔汀", "无名者", "淑女格蕾丝", "乌尔里希", "暴雨小组组长乌尔里希",
    "舵手伊萨姆", "舵手老查理", "舵手乔瓦尼", "通讯员", "船员Ⅰ", "船员Ⅱ",
    "客人Ⅰ", "客人Ⅱ", "客人Ⅲ", "乔纳森", "佩内洛普", "卢卡斯",
    "哑谜", "兔毛手袋", "希曼", "与会人员Ⅰ", "与会人员Ⅱ", "与会人员Ⅲ",
    "与会人员Ⅳ", "与会人员Ⅴ", "露西", "X", "伊丽莎白女士",
    "佩纽奶奶", "塔雷克叔叔", "纳塔诺爷爷",
    # 地点
    "游轮大厅", "科算中心议事厅", "客房", "电力供应室", "拉普拉斯病房",
    "新斯科舍", "意大利", "莫阿纳", "巨齿飞鳐聚集区", "普列谢茨克航天基地",
    # 组织
    "科算中心", "圣洛夫基金会", "重塑之手", "洛伦兹研究所", "生物技术组",
    # 物品 / 概念
    "罗盘灼灼", "巨齿飞鳐", "口琴", "扩音喇叭", "蹦蹦跳弹力灯泡",
    "通讯器", "唱片机", "星锑的唱片", "象形贝壳", "啪唧匣子",
    "非对称核素R", "太空种子", "天体摄谱仪", "高速光度计", "黑曜石晶体",
    "泽兰护符", "声波发生器", "人工暴雨", "免疫回溯", "解压弹力球",
    "蝴蝶纹样信封", "挑衅信", "工牌", "洛伦兹研究所",
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
for sub in ["舵手", "通讯员", "船员", "客人", "乔纳森", "佩内洛普", "卢卡斯",
            "哑谜", "兔毛", "希曼", "与会", "露西", "佩纽", "塔雷克",
            "纳塔诺", "议事厅", "客房", "电力", "病房", "新斯科舍",
            "意大利", "莫阿纳", "飞鳐", "罗盘", "口琴", "喇叭",
            "灯泡", "通讯器", "光度计", "泽兰", "声波", "洛伦兹"]:
    hits = sorted(x for x in known if sub in x)
    if hits:
        print(f"  {sub:10s} -> {hits[:10]}")
