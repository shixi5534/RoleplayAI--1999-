# -*- coding: utf-8 -*-
"""第 13 会话：24101 命名落点复核（rebuild 后用 resolve() 实测）。"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT.parent.parent / "src"))
from compendium_rag.graph_store import GraphStore  # noqa: E402

g = GraphStore.load(ROOT / "graph.json")

print("=== 24101 关键实体落点 ===")
for n in ["图图石子", "卡穆塔", "托阿", "塞洛尼", "芭卡洛儿", "星锑",
          "维尔汀", "十四行诗", "勿忘我", "无名者", "暴雨小组组长乌尔里希",
          "舵手伊萨姆", "舵手老查理", "舵手乔瓦尼", "小丽莎",
          "克雷莫纳", "自由海风号", "星锑空间望远镜", "瓦尔普吉斯",
          "西欧罗斯", "象形贝壳", "啪唧匣子", "罗盘灼灼", "巨齿飞鳐",
          "诺亚方舟", "乡愁", "小提琴", "时代病", "重塑·门徒"]:
    e = g.entities.get(n)
    if e:
        print(f"  ✅ {n:18s} {e.type:4s} m={e.mentions:3d} aliases={e.aliases[:3]}")
    else:
        print(f"  ⚠ {n:18s} resolve={g.resolve(n)!r}")

print("\n=== 别名实测 ===")
for n in ["淑女格蕾丝", "夏洛特·奥黑根", "纸信圈儿", "福葛", "宽檐帽",
          "侍应生", "莉莉娅", "史蒂文·加西亚", "温馨之家",
          "乌尔里希", "唱片", "拉普拉斯", "琼斯", "通灵板", "前行者"]:
    print(f"  {n:14s} -> {g.resolve(n)!r}")
