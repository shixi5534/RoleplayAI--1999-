# -*- coding: utf-8 -*-
"""batch213 落点预演：确认新名不被吸入他组。"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT.parent.parent / "src"))
from compendium_rag.graph_store import _merge_candidates, canonical_pick  # noqa: E402

obs: dict[str, dict] = {}
for p in sorted((ROOT / "cache").rglob("*.json")):
    try:
        o = json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        continue
    raw = o.get("raw") or {}
    for e in raw.get("entities") or []:
        n = e.get("name")
        if not n:
            continue
        d = obs.setdefault(n, {"types": {}, "aliases": set(), "descs": {}})
        d["types"][e.get("type")] = d["types"].get(e.get("type"), 0) + 1
        if e.get("desc"):
            d["descs"][e["desc"]] = d["descs"].get(e["desc"], 0) + 1
        for a in e.get("aliases") or []:
            if a:
                d["aliases"].add(a)
    for r in raw.get("relations") or []:
        for s in ("src", "dst"):
            if r.get(s):
                obs.setdefault(r[s], {"types": {}, "aliases": set(), "descs": {}})

CAND = [
    "巡逻警察Ⅰ", "巡逻警察Ⅱ", "街坊Ⅰ", "街坊Ⅱ", "摊贩", "小丽莎",
    "马蒂姑姑", "零零七号穆尔森", "穆尔森", "白天鹅", "巴拉奈婆婆",
    "无线电广播", "苏利丝", "护士", "临时医院的护士", "南约克郡",
    "蒂尔伯里码头", "贝尔丹", "治安局", "贝尔丹火焰节",
    "沙漠祭祀公开赛", "极光杯世界锦标赛", "吸尘器", "黑雨伞",
    "夜壶", "玻璃鱼缸", "大喇叭", "十字街古宅", "临时医院",
    "十字街", "煤炭肺结核", "花园魔精", "金丝绵雀",
]
for n in CAND:
    d = obs.setdefault(n, {"types": {}, "aliases": set(), "descs": {}})
    d["types"]["角色"] = d["types"].get("角色", 0) + 1

names = sorted(obs)
ae = []
for n, o in obs.items():
    for a in o["aliases"]:
        if a != n:
            ae.append((n, a))
dsu = _merge_candidates(names, ae)
groups: dict[str, list[str]] = {}
for n in names:
    groups.setdefault(dsu.find(n), []).append(n)
cnt = {n: sum(obs[n]["types"].values()) + sum(obs[n]["descs"].values())
       for n in names}

print("=== 注入后落点 ===")
bad = 0
for t in CAND:
    root = dsu.find(t)
    mem = sorted(groups[root])
    canon = canonical_pick(mem, cnt)
    mark = "✅" if canon == t else "❌"
    if canon != t:
        bad += 1
    line = f"  {mark} {t:20s} canon={canon!r}"
    if t != canon:
        line += f"  组{len(mem)}: {[(m, cnt[m]) for m in sorted(mem, key=lambda x: -cnt[x])[:5]]}"
    print(line)
print(f"\n被吸入他组: {bad} 个")
