# -*- coding: utf-8 -*-
"""batch214 落点预演。"""
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
    "十字街联合协会", "迪吉里木", "基金会分部成员Ⅰ", "基金会分部成员Ⅱ",
    "艾丽卡婆婆", "基顿小子", "基顿闹腾商店", "煤灰魔精", "雾气净化器",
    "计量仪", "报名表", "挑战书", "起司蛋糕", "天竺葵", "众人",
    "组委会", "乌卢鲁运动场", "海报", "术杖", "码头工人",
    "伦敦煤烟污染勘察与清除大使", "巴特利家",
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
for t in CAND:
    root = dsu.find(t)
    mem = sorted(groups[root])
    canon = canonical_pick(mem, cnt)
    mark = "✅" if canon == t else "❌"
    line = f"  {mark} {t:26s} canon={canon!r}"
    if t != canon:
        line += f"  组{len(mem)}: {[(m, cnt[m]) for m in sorted(mem, key=lambda x: -cnt[x])[:5]]}"
    print(line)
