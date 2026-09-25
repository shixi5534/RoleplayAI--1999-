# -*- coding: utf-8 -*-
"""只读探针（batch153）：核对候选实体名是否已在 graph.json 中。"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
idx = {e["name"]: e for e in json.loads(
    (ROOT / "graph.json").read_text(encoding="utf-8"))["entities"]}

CANDIDATES = [
    # 1922 尾
    "贝蒂", "琼斯", "护士劳拉", "女性职员I", "梅根",
    "圣洛夫基金会", "病房", "摄影机", "胶片", "剧本", "礼盒",
    "玻璃棺", "墓地", "储藏室",
    # 1923
    "图图石子", "卡穆塔", "托阿", "塞洛尼", "芭卡洛儿", "维尔汀",
    "十四行诗", "小梅斯梅尔", "司辰",
    "努库泰澳岛", "以提提", "米缇", "维布那", "麦黎",
    "拉普拉斯康复中心", "箱中客厅", "箱中一隅", "拉普拉斯康复中心病房",
    "拉普拉斯康复中心走廊", "图书馆",
    "贝壳项链", "罗盘草", "罗盘", "独木舟", "贝壳", "梦魇", "梦魇之声",
    "海妖之歌", "人工梦游疗法", "人工梦游", "船商贸易节", "箱庭贸易节",
    "宝石闪闪节", "水果秀场", "湖畔市场", "二手沙滩",
    "申请书", "安眠", "药物", "药品", "烟草", "颜料", "陶瓷小花",
    "铁片蝴蝶", "热水澡", "热牛奶", "海风",
]

print("=== already in graph ===")
for c in CANDIDATES:
    e = idx.get(c)
    if e:
        print(f"  YES  {c:22s} type={e['type']:4s} m={e['mentions']:4d} "
              f"aliases={e['aliases']} desc={e['desc']!r}")

print()
print("=== NOT in graph ===")
for c in CANDIDATES:
    if c not in idx:
        print(f"  no   {c}")

print()
print("=== fuzzy ===")
for sub in ["图图", "卡穆塔", "托阿", "塞洛尼", "芭卡", "梅根", "努库",
            "以提提", "米缇", "维布", "麦黎", "贝壳", "罗盘", "独木舟",
            "梦魇", "海妖", "贸易节", "申请书", "安眠", "箱庭", "司辰"]:
    print(f"  {sub:10s} -> {[n for n in idx if sub in n][:12]}")
