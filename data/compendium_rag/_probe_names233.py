# -*- coding: utf-8 -*-
"""并集探针（27101_1987宇宙组曲 第 1 轮，batch233）。"""
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
    "指针", "冷周六", "库珀花环", "北方哨歌", "科兹洛夫", "娜塔莉亚",
    "医疗职员", "拉普拉斯研究员", "接待员", "电台节目", "马戏团员",
    "小蛇Ⅰ", "小蛇Ⅴ", "海伦娜", "迪布瓦家族", "露西", "路德维希",
    "阿涅娅", "小冷周六", "冷周六的九个兄弟姐妹", "冷周六的父亲",
    "维拉", "阿夫西维",
    # 地点
    "普列谢茨克", "普列谢茨克发射基地", "发射基地病房", "温室办公室",
    "发射基地走廊", "拉普拉斯专用办公楼", "乌特恩亚亚", "米尔内",
    "北方哨歌",
    # 组织
    "拉普拉斯", "科算中心", "圣洛夫基金会", "乌特恩亚亚马戏团",
    # 概念 / 物品
    "理线学", "传送术式", "金唱片", "旅行者一号", "旅行者二号",
    "暴雨", "意识共享", "遗体捐献协议书", "生态缸", "留影设备",
    "苦目糖", "监测器", "神秘术", "神秘学与科技的结合", "库珀花环的烟花",
    "大熊座", "小熊座", "极光", "钢丝", "空中飞人", "库珀花环名片",
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
for sub in ["指针", "冷周六", "库珀", "北方", "科兹洛夫", "娜塔莉亚",
            "医疗", "拉普拉斯研究员", "接待", "电台", "马戏", "小蛇",
            "海伦娜", "迪布瓦", "露西", "路德维希", "阿涅娅", "维拉",
            "阿夫西维", "普列谢茨克", "乌特恩", "米尔内", "理线",
            "传送", "金唱片", "旅行者", "苦目糖", "生态缸", "监测器",
            "钢丝", "飞人"]:
    hits = sorted(x for x in known if sub in x)
    if hits:
        print(f"  {sub:12s} -> {hits[:10]}")
