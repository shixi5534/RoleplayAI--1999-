# -*- coding: utf-8 -*-
"""并集探针（21101_77号往事 第 1 轮，batch205）。

口径：graph.json ∪ 全部 _agent_batch*.json（红线 2）。
用途：判定 21101 新出现的人物/地点是复用既有节点还是新建。
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent

graph = json.loads((ROOT / "graph.json").read_text(encoding="utf-8"))
known = {}          # name -> 来源标记
alias_owner = {}    # alias -> owner name
for e in graph["entities"]:
    known[e["name"]] = "graph"
    for a in e["aliases"]:
        alias_owner.setdefault(a, e["name"])

batch_files = sorted(ROOT.glob("_agent_batch*.json"))
for bf in batch_files:
    try:
        data = json.loads(bf.read_text(encoding="utf-8"))
    except Exception:
        continue
    for key, blk in data.items():
        for e in blk.get("entities", []):
            n = e.get("name")
            if n and n not in known:
                known[n] = bf.name
            for a in (e.get("aliases") or []):
                alias_owner.setdefault(a, n)

print(f"图谱实体 {len(graph['entities'])}｜"
      f"batch 文件 {len(batch_files)} 个｜并集实体 {len(known)}")


def report(cands, label):
    print(f"\n=== {label} ===")
    for n in cands:
        if n in known:
            src = known[n]
            tag = "图谱" if src == "graph" else src
            print(f"  EXISTS {n:24s}  ← {tag}")
        elif n in alias_owner:
            print(f"  ALIAS  {n:24s}  → {alias_owner[n]}")
        else:
            print(f"  new    {n}")


def fuzzy(sub, limit=14):
    hits = [n for n in known if sub in n]
    if hits:
        print(f"  {sub:12s} -> {hits[:limit]}")


CAND = [
    # 21101 本批人物
    "阿尔古斯", "凯拉", "数羊羔", "蓝手帕", "维尔汀", "红弩箭",
    "穆姆", "司机", "侍应生",
    "“启明会”信众Ⅰ", "“启明会”信众Ⅱ",
    # 组织 / 地点 / 物品
    "启明会", "圣洛夫基金会", "UTTU", "芝诺", "芝诺基地",
    "77号公路", "蓝手帕旅馆", "德克萨斯", "奇索斯镇", "德州",
    "牧马人越野车", "红色38", "Su-01ве", "通讯器", "司辰",
    "神秘学家", "魔精", "兀尔德", "蓝手帕旅馆",
]

report(CAND, "候选名判定")

print("\n=== 近似名（防重复命名）===")
for sub in ["阿尔古", "凯拉", "羊羔", "手帕", "维尔汀", "红弩箭",
            "穆姆", "司机", "侍应", "启明", "基金会", "UTTU",
            "芝诺", "77", "公路", "德克萨斯", "奇索斯", "牧马人",
            "红色", "通讯", "司辰", "神秘学", "魔精", "兀尔德"]:
    fuzzy(sub)
