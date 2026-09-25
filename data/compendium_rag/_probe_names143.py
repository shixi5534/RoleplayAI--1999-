# -*- coding: utf-8 -*-
"""只读探针（batch143）：核对候选实体名是否已在 graph.json 中。"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
idx = {e["name"]: e for e in json.loads(
    (ROOT / "graph.json").read_text(encoding="utf-8"))["entities"]}

CANDIDATES = [
    "多萝西娅", "杰瑞·威尔逊", "小梅斯梅尔", "康复中心职员丹尼", "康复中心职员威尔",
    "拉普拉斯护士", "病人柯布", "约瑟夫", "露西", "助理希曼", "铅玻璃", "牙仙",
    "拉普拉斯康复中心", "拉普拉斯科算中心", "第一防线学校", "圣洛夫基金会",
    "梅斯梅尔家族", "拉普拉斯管理委员", "拉普拉斯总负责人办公室",
    "康复中心走廊", "康复中心手术室", "康复中心病房", "静养区",
    "体外膜肺氧合器", "磁流疗法", "人工梦游机器", "软盘", "记录簿",
    "酒精消毒液", "苦喉腥消毒液", "医疗废弃箱", "求助铃", "梦游机器",
    "暴雨症候群", "补墙匠", "守钟人", "全科医生", "神秘学家", "神秘术",
    "消毒液", "纸团", "针管", "勺子", "麻醉剂", "尼古丁", "石子",
    "佩德拉", "费舍", "莉亚", "柯布先生", "老柯布",
    "康复中心条例", "医疗废弃物处置细则", "禁闭措施", "安保人员",
    "三只踏入同一条河流", "信仰", "理性", "梦境", "小马", "日记",
    "多萝西娅的日记", "签名", "同意书",
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
for sub in ["多萝西娅", "威尔", "柯布", "约瑟夫", "费舍", "莉亚", "佩德拉",
            "梅斯梅尔", "膜肺", "磁流", "梦游", "消毒液", "梦", "信仰",
            "康复中心", "静养"]:
    print(f"  {sub:8s} -> {[n for n in idx if sub in n][:12]}")
