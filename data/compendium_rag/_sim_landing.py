# -*- coding: utf-8 -*-
"""落地模拟(可复用)简化版:python _sim_landing.py <新名文件>"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT.parent.parent / "src"))
from compendium_rag.graph_store import _merge_candidates, canonical_pick  # noqa: E402

obs = {}
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

cnt = {}
for n, o in obs.items():
    cnt[n] = sum(o["types"].values()) + sum(o["descs"].values())

bad = 0
ae = [(n, a) for n, o in obs.items() for a in o["aliases"] if a != n]
for line in Path(sys.argv[1]).read_text(encoding="utf-8").splitlines():
    t = line.strip()
    if not t:
        continue
    if t in obs:
        print(f"EXISTS {t} (已在并集)")
        continue
    obs[t] = {"types": {"角色": 1}, "aliases": set(), "descs": {}}
    cnt[t] = 1
    ae2 = ae + [(n, a) for n, o in obs.items() for a in o["aliases"] if a != n]
    dsu = _merge_candidates(sorted(obs), ae2)
    root = dsu.find(t)
    grp = [n for n in obs if dsu.find(n) == root]
    canon = canonical_pick(grp, cnt)
    if canon != t:
        bad += 1
        print(f"MERGE {t} -> {canon}  组员计数={[(m, cnt.get(m, 0)) for m in sorted(grp)][:8]}")
    else:
        print(f"OK    {t}")
print(f"需改写 {bad} 个")
