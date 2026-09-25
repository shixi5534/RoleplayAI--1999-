# -*- coding: utf-8 -*-
"""batch211 预演：确认 23101 的候选名落点（含 利伯蒂/纸信圈儿 归并）。"""
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

# 注入本批候选（name 侧）
CAND_NAMES = [
    "利伯蒂", "奇奇比翁", "威尔", "雾行者", "宽檐帽先生", "牙仙",
    "伦敦的司机", "十字街", "伦敦清洁大气委员会", "古宅",
    "煤炭肺结核", "雾中鬼婆", "金丝绵雀", "有声信", "伦敦分部",
    "乌卢鲁伦敦预选赛", "乌卢鲁欢庆集市",
]
for n in CAND_NAMES:
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
for t in CAND_NAMES + ["纸信圈儿", "卡邦克鲁", "魔精", "司机", "Z女士", "Z",
                       "奥利弗·福葛", "福葛", "宽檐帽"]:
    if t not in obs:
        print(f"  {t:22s} [未观测]")
        continue
    root = dsu.find(t)
    mem = sorted(groups[root])
    canon = canonical_pick(mem, cnt)
    mark = "✅" if canon == t else "❌"
    line = f"  {mark} {t:22s} canon={canon!r}"
    if t != canon:
        line += f"  组{len(mem)}: {[(m, cnt[m]) for m in sorted(mem, key=lambda x: -cnt[x])[:5]]}"
    print(line)
