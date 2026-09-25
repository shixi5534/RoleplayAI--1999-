# -*- coding: utf-8 -*-
"""只读探针（batch155）：核对候选实体名是否已在 graph.json 中。"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
idx = {e["name"]: e for e in json.loads(
    (ROOT / "graph.json").read_text(encoding="utf-8"))["entities"]}

CANDIDATES = [
    # 1923 尾
    "图图石子", "塞洛尼", "卡穆塔", "维尔汀", "露西", "芭卡洛儿",
    "努库泰澳人Ⅰ", "努库泰澳人Ⅱ", "箱庭贸易节", "罗盘灼灼", "贝壳项链",
    "荧树枝", "细颈花瓶", "提丰小灯", "司辰的藏书", "湖畔", "图书馆",
    "努库泰澳岛", "音符勋章", "复古迷你唱片", "拼贴邮票", "银质怀表",
    # 1924
    "坎吉拉", "贾纳丹", "阿贾尔", "孩子Ⅰ", "孩子Ⅱ", "夏尔贾",
    "乔普拉", "苏塔莉娅", "农夫拉胡尔", "陶工塔拉", "萨尔曼少爷",
    "萨尔曼老爷", "仆人Ⅰ", "仆人Ⅱ", "警员Ⅰ", "警员Ⅱ", "喷吉",
    "昌迪加尔警局", "摩卢旁卡村", "大篷车", "秘密基地", "审讯室",
    "拉胡尔家", "种植园", "蓝陶作坊", "象牙", "蛇形足环", "寻人启事",
    "卢比", "蓝陶", "馕饼", "匕首", "手枪", "报纸", "神秘术",
    "辛哈大叔", "萨尔曼", "蓝陶作坊",
]

print("=== already in graph ===")
for c in CANDIDATES:
    e = idx.get(c)
    if e:
        print(f"  YES  {c:18s} type={e['type']:4s} m={e['mentions']:4d} "
              f"aliases={e['aliases']} desc={e['desc']!r}")

print()
print("=== NOT in graph ===")
for c in CANDIDATES:
    if c not in idx:
        print(f"  no   {c}")

print()
print("=== fuzzy ===")
for sub in ["坎吉拉", "贾纳丹", "阿贾尔", "夏尔贾", "乔普拉", "苏塔莉娅",
            "拉胡尔", "塔拉", "萨尔曼", "喷吉", "摩卢旁卡", "昌迪加尔",
            "大篷车", "蓝陶", "足环", "寻人", "卢比", "仆人", "警员",
            "秘密基地", "审讯"]:
    print(f"  {sub:10s} -> {[n for n in idx if sub in n][:12]}")
