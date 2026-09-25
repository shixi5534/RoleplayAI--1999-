# -*- coding: utf-8 -*-
"""并集探针（23101_圣火纪行_东区黎明 收官轮，batch216）。"""
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
    "笃笃骨", "夏洛特·奥黑根", "夏洛特", "纸信圈儿", "利伯蒂", "卡洛琳",
    "牙仙", "宽檐帽", "宽檐帽先生", "福葛先生", "雾行者", "威尔",
    "小丽莎", "淘气鬼弗洛狄", "乌鸦教练", "安娜", "Z", "Z女士",
    "丽娜婆婆", "威廉叔叔", "康蒂婶婶", "小玛丽", "老汉斯",
    "裁判组成员Ⅰ", "裁判组成员Ⅱ", "志愿者Ⅰ", "观众Ⅰ", "观众Ⅱ",
    "观众Ⅲ", "观众Ⅳ", "观众Ⅴ", "参赛选手Ⅰ", "参赛选手Ⅱ",
    "广播声", "无线电广播", "2401号选手", "2402号选手", "2406号选手",
    # 地点
    "十字街", "十字街古宅", "练习室", "第五准备区", "证件补办处",
    "运动会场", "观众席", "澳洲", "伦敦", "澳大利亚", "冥府",
    # 组织 / 事件
    "圣洛夫基金会", "乌卢鲁运动会", "乌卢鲁伦敦预选赛", "自由祭祀",
    "伦敦分部", "应急管理局", "安保局", "管理局",
    # 物品 / 概念
    "迪吉里木", "传声花", "白被单", "应急指南", "奖牌", "邀请函",
    "门票", "瓦尔普吉斯", "西欧罗斯", "莱伊", "黑雾", "魔精",
    "神秘术", "祭祀", "太阳神", "雾中爵士", "行李箱", "文件袋",
    "小被单", "乳牙", "煤灰",
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
for sub in ["瓦尔普", "西欧", "莱伊", "传声", "安娜", "丽娜", "威廉叔叔",
            "康蒂", "小玛丽", "老汉斯", "裁判组", "志愿者", "观众",
            "参赛选手", "广播声", "准备区", "补办处", "应急管理",
            "安保", "爵士", "邀请函", "奖牌", "行李箱", "太阳神"]:
    hits = sorted(x for x in known if sub in x)
    if hits:
        print(f"  {sub:10s} -> {hits[:10]}")
