# -*- coding: utf-8 -*-
"""第 14 会话：25101 命名落点复核（rebuild 后用 resolve() 实测）。"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT.parent.parent / "src"))
from compendium_rag.graph_store import GraphStore  # noqa: E402

g = GraphStore.load(ROOT / "graph.json")

print("=== 25101 关键实体落点 ===")
ok = True
for n in ["梁月", "波蒂埃", "埃尔登警长", "菲林士多", "奇星", "何日君",
          "斯考特", "空脑袋", "黑鹮", "黑鹮的副手", "泥鯭的士", "Lily",
          "民间侦探", "艾瑞克·黄", "丽莲·刘", "神秘学犯罪科",
          "神秘学藏品管理部", "夜巡特遣管理局", "三燕归巢", "被诅咒的胶片",
          "强梁", "险道兽", "胶片领域", "生魂", "三魂七魄", "邪祟",
          "传信术", "水晶花瓶", "幕后黑手", "勿忘我", "卡戎",
          "暴雨小组组长乌尔里希", "黑鹮的副手"]:
    e = g.entities.get(n)
    if e:
        print(f"  ✅ {n:22s} {e.type:4s} m={e.mentions:3d} aliases={e.aliases[:3]}")
    else:
        ok = False
        print(f"  ⚠ {n:22s} resolve={g.resolve(n)!r}")

print("\n=== 关键别名实测（应可解析或已知 None）===")
for n in ["淑女格蕾丝", "莱瑟姆", "天使娜娜", "佩德拉", "纸信圈儿",
          "夏洛特·奥黑根", "福葛", "宽檐帽", "乌尔里希", "唱片", "拉普拉斯"]:
    r = g.resolve(n)
    print(f"  {n:16s} -> {r!r}")

print("\n结论:", "全部通过" if ok else "有缺失，需检查")
