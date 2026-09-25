# -*- coding: utf-8 -*-
"""第 12 会话：23101 命名落点复核（rebuild 后用 resolve() 实测）。"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT.parent.parent / "src"))
from compendium_rag.graph_store import GraphStore  # noqa: E402

g = GraphStore.load(ROOT / "graph.json")

print("=== 23101 关键实体落点 ===")
for n in ["笃笃骨", "利伯蒂", "卡洛琳", "牙仙", "雾行者", "宽檐帽先生",
          "瓦尔普吉斯", "西欧罗斯", "莱伊", "迪吉里木", "传声花",
          "乌鸦教练", "小丽莎", "淘气鬼弗洛狄", "威尔",
          "十字街", "十字街古宅", "伦敦清洁大气委员会",
          "奇索斯的军备工厂", "蓝手帕", "无名者", "农场女孩凯拉",
          "一等列兵安德烈", "公路司机", "伦敦的司机", "镜中幽灵"]:
    e = g.entities.get(n)
    if e:
        print(f"  ✅ {n:16s} {e.type:4s} m={e.mentions:3d} aliases={e.aliases[:4]}")
    else:
        print(f"  ⚠ {n:16s} resolve={g.resolve(n)!r}")

print("\n=== 别名实测（应为可解析或已知 None）===")
for n in ["夏洛特·奥黑根", "纸信圈儿", "福葛", "宽檐帽", "侍应生", "莉莉娅",
          "史蒂文·加西亚", "温馨之家", "圣保罗荣军院", "伊戈尔将军",
          "淑女格蕾丝", "凯拉", "卡邦克鲁"]:
    print(f"  {n:14s} -> {g.resolve(n)!r}")
