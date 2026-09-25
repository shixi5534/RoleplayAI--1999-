# -*- coding: utf-8 -*-
"""并集探针（24101_地球上最后的夜晚 第 2 轮，batch218）。"""
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
    "康斯坦丁", "会长", "洛佩拉", "伊戈尔", "金伯利女郎", "维尔汀",
    "十四行诗", "星锑", "乌尔里希", "暴雨小组组长乌尔里希",
    "芭卡洛儿", "图图石子", "卡穆塔", "托阿", "塞洛尼", "格蕾丝",
    "无名者", "淑女格蕾丝", "客人Ⅰ", "客人Ⅱ", "客人Ⅲ",
    "弗兰克先生", "亨利先生", "特里波德罗",
    # 地点
    "克罗纳拉发射场旧址", "克罗纳拉", "圭亚那航天中心",
    "普列谢茨克航天发射场", "奥尔德堡", "伦敦", "悉尼港", "雪梨港",
    "箱中一隅", "船长室", "基金会高层办公室", "鸽子屋", "火地岛",
    "南美分部", "大洋洲", "努库泰澳", "努库泰澳岛", "数字岛",
    # 组织
    "圣洛夫基金会", "拉普拉斯", "科算中心", "司辰小队", "重塑之手",
    "芝诺", "芝诺军备学院", "暴雨专项研究小组", "人工暴雨项目",
    "美国航空航天局", "基金会高层",
    # 物品 / 概念
    "星锑空间望远镜", "天文望远镜卫星", "唱片", "小东西",
    "神秘学唱片机", "太空种子", "龙血树脂罗盘", "黑曜石晶体",
    "广域照相机", "天体摄谱仪", "非对称核素R", "人工暴雨",
    "象形贝壳", "迪吉里杜", "啪唧匣子", "游轮宣传传单", "传单",
    "免疫回溯", "大筛选", "暴雨", "陨石坑音乐节", "面具",
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
for sub in ["康斯坦丁", "会长", "洛佩拉", "伊戈尔", "金伯利", "十四行诗",
            "克罗纳拉", "圭亚那", "普列谢茨克", "奥尔德堡", "船长室",
            "高层", "鸽子屋", "火地岛", "南美", "大洋洲", "数字岛",
            "望远镜", "唱片", "核素", "人工暴雨", "迪吉里杜", "免疫",
            "大筛选", "陨石坑", "面具", "特里波德罗", "客人"]:
    hits = sorted(x for x in known if sub in x)
    if hits:
        print(f"  {sub:12s} -> {hits[:10]}")
