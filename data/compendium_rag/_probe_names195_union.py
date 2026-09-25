# -*- coding: utf-8 -*-
"""权威探针（batch195 起改用）：把 graph.json 与**全部 batch 文件**取并集。

原因：抽取期间按铁律不 rebuild，graph.json 会滞后于 cache。
只查 graph.json 会误判"新建"，导致同一对象被二次命名。
本脚本是后续所有探针的基线。
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent

# 1) 图谱已有
graph = json.loads((ROOT / "graph.json").read_text(encoding="utf-8"))
known = {}          # name -> 来源标记
alias_owner = {}    # alias -> owner name
for e in graph["entities"]:
    known[e["name"]] = "graph"
    for a in e["aliases"]:
        alias_owner.setdefault(a, e["name"])

# 2) 全部 batch 文件声明的实体（含 graph 尚未 rebuild 的）
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
            print(f"  EXISTS {n:20s}  ← {tag}")
        elif n in alias_owner:
            print(f"  ALIAS  {n:20s}  → {alias_owner[n]}")
        else:
            print(f"  new    {n}")


def fuzzy(sub, limit=12):
    hits = [n for n in known if sub in n]
    if hits:
        print(f"  {sub:10s} -> {hits[:limit]}")


CAND = [
    # 本批拟复用/新建
    "帕特里基大叔", "奇肯恩", "基基图克", "霍伊图克", "基基图克异种",
    "奥尔加海峡", "工人节", "罐头园", "劳动食堂", "来亚什基会议室",
    "来亚什基生产工厂", "理线学社", "视界线公约", "芝诺卫兵",
    "理线师Ⅰ", "理线师Ⅱ", "理线师Ⅲ", "洛伦兹蝴蝶", "理线拟态仪",
    "考评员Ⅰ", "考评员Ⅱ", "工程小组", "魔药恢复小组", "垦荒队",
    "尼基塔", "瓦列里娅", "谢尔吉", "尤里", "普通镇民",
    "Э-050型挖掘机", "СК-1562型起重机", "驯鹿的断角",
    "胡闹桦木的黏液", "金齿海豹的胡须", "推荐信", "开菲尔",
    "帕特里基", "拟态仪", "调查队",
]
report(CAND, "候选名判定")

print("\n=== 近似名（防重复命名）===")
for sub in ["帕特里基", "奇肯", "基基", "霍伊", "奥尔加", "工人节",
            "罐头园", "食堂", "会议室", "工厂", "理线学社", "视界",
            "卫兵", "理线师", "洛伦兹", "拟态", "考评", "小组",
            "垦荒", "尼基塔", "瓦列", "谢尔", "尤里", "普通镇民",
            "挖掘机", "起重机", "驯鹿", "桦木", "海豹", "推荐信"]:
    fuzzy(sub)
