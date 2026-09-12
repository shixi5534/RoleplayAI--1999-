# -*- coding: utf-8 -*-
"""按返工要求清理 batch_020.jsonl 的「概念」类实体。"""
import json, unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parent
P = ROOT / "batch_020.jsonl"

def norm(s):
    return unicodedata.normalize("NFKC", s or "").strip().lower()

# 保留的概念（设定专有具名术语 / 核心世界机制）
KEEP = {
    "咒语",          # 核心机制：咒语/incantation
    "显化",          # 设定专有：emanation
    "神识",          # Gnosis（规则示例专名）
    "努玛",          # Numa（设定专有）
    "戈尔工流",      # Gorgon current（设定专有）
    "神识之光",      # Divine Light of Gnosis（专有）
    "Pyrron",        # 设定专有（阿派朗误听）
    "乌洛波罗斯",    # Ouroboros（神话专名）
    "丰饶之角",      # Horn of Plenty（神话专名）
    "风暴免疫",      # 免疫（核心机制）
    "放逐圈",        # Exile Circle（专有仪式）
    "风暴综合征",    # Storm Syndrome（设定专有病症）
}

lines = P.read_text(encoding="utf-8").splitlines()
out = []
dropped_ident = set()          # 被删概念的所有标识符（name+alias 归一）
for ln in lines:
    if not ln.strip():
        continue
    o = json.loads(ln)
    ents = o.get("entities", [])
    new_ents = []
    for e in ents:
        if e.get("type") == "概念" and e.get("name") not in KEEP:
            # 记录被删概念的标识符，供清理关系/别名
            dropped_ident.add(norm(e.get("name", "")))
            for a in (e.get("aliases") or []):
                dropped_ident.add(norm(a))
            continue
        # 清理挂在被删概念上的别名
        if "aliases" in e and e["aliases"]:
            e["aliases"] = [a for a in e["aliases"] if norm(a) not in dropped_ident]
        new_ents.append(e)
    rels = o.get("relations", [])
    new_rels = []
    for r in rels:
        if norm(r.get("src", "")) in dropped_ident or norm(r.get("dst", "")) in dropped_ident:
            continue
        new_rels.append(r)
    out.append(json.dumps({"hash": o["hash"], "entities": new_ents, "relations": new_rels}, ensure_ascii=False))

P.write_text("\n".join(out) + "\n", encoding="utf-8")

# 统计类型分布
from collections import Counter
c = Counter()
for ln in out:
    o = json.loads(ln)
    for e in o["entities"]:
        c[e["type"]] += 1
types = ["角色", "组织", "地点", "概念", "物品", "事件", "时间"]
print("类型分布:", {t: c.get(t, 0) for t in types})
print("概念 distinct 数:", len(KEEP))
print("总实体:", sum(c.values()), " 总行数:", len(out))
