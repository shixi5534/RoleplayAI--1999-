# -*- coding: utf-8 -*-
"""batch211 关键归并判定：纸信圈儿 / 卡邦克鲁 / 司机 / 雾行者 / 宽檐帽先生。"""
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

for t in ["纸信圈儿", "卡邦克鲁", "司机", "公路司机", "雾行者", "福葛",
          "宽檐帽先生", "宽檐帽", "牙仙", "黑雾", "魔精", "羊脂蜗牛",
          "十字街", "阿卡迪亚的十字街", "维多利亚"]:
    if t not in obs:
        print(f"  {t:18s} [未观测]")
        continue
    root = dsu.find(t)
    mem = sorted(groups[root])
    canon = canonical_pick(mem, cnt)
    mark = "✅" if canon == t else "❌"
    print(f"  {mark} {t:18s} 组{len(mem):2d} canon={canon!r:18s} cnt={cnt[t]}")
    if len(mem) > 1:
        top = sorted(mem, key=lambda x: -cnt[x])[:6]
        print(f"        {[(m, cnt[m]) for m in top]}")
