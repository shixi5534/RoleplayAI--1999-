# -*- coding: utf-8 -*-
"""只读探针（batch152）：核对候选实体名是否已在 graph.json 中。"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
idx = {e["name"]: e for e in json.loads(
    (ROOT / "graph.json").read_text(encoding="utf-8"))["entities"]}

CANDIDATES = [
    "贝蒂", "琼斯", "护士劳拉", "女性职员I", "女性职员II", "汤姆",
    "年轻的女子", "餐馆老板", "贝蒂的男装形象",
    "圣洛夫基金会", "圣洛夫基金会客房", "病房", "电视机", "失物保管处",
    "电影院", "溪木镇", "储物室", "放映厅", "西部",
    "摄影机", "相机", "胶片", "剧本", "礼盒", "手链", "假胡子道具",
    "玻璃棺", "虫形底座", "贝雷帽", "钓鱼马甲", "时尚杂志",
    "暴雨", "神秘术", "替身演员", "意识唤醒者", "时代",
    "空礼盒", "苹果核", "法老之夜", "最后的电影", "牛仔", "威廉",
]

print("=== already in graph ===")
for c in CANDIDATES:
    e = idx.get(c)
    if e:
        print(f"  YES  {c:20s} type={e['type']:4s} m={e['mentions']:4d} "
              f"aliases={e['aliases']} desc={e['desc']!r}")

print()
print("=== NOT in graph ===")
for c in CANDIDATES:
    if c not in idx:
        print(f"  no   {c}")

print()
print("=== fuzzy ===")
for sub in ["汤姆", "威廉", "溪木", "摄影机", "胶片", "剧本", "礼盒",
            "手链", "虫", "底座", "贝雷", "马甲", "保管", "电影院",
            "唤醒者", "牛仔", "苹果核", "法老"]:
    print(f"  {sub:10s} -> {[n for n in idx if sub in n][:12]}")
