# -*- coding: utf-8 -*-
"""desc 探针(仅读 graph.json ∪ _agent_batch*.json,与并集探针同源):python _probe_desc292.py <名文件>"""
import json
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT.parent.parent / "src"))
from compendium_rag.graph_store import GraphStore  # noqa: E422

names = [l.strip() for l in Path(sys.argv[1]).read_text(encoding="utf-8").splitlines() if l.strip()]
hits = defaultdict(set)
g = GraphStore.load(ROOT / "graph.json")
for n in names:
    e = g.entities.get(n)
    if e is not None:
        hits[n].add((e.type, e.desc, "graph"))
    for a, owner in ((a, x.name) for x in g.entities.values() for a in x.aliases):
        if a == n:
            hits[f"alias:{n}->{owner}"].add((owner, g.entities[owner].desc, "graph"))
for bf in sorted(ROOT.glob("_agent_batch*.json")):
    try:
        data = json.loads(bf.read_text(encoding="utf-8"))
    except Exception:
        continue
    for blk in data.values():
        for e in blk.get("entities", []):
            if e.get("name") in names:
                hits[e["name"]].add((e.get("type"), e.get("desc"), bf.name))
for n in names:
    print(f"== {n}")
    for t, d, src in sorted(hits.get(n, ()), key=lambda x: str(x[1]))[:6]:
        print(f"   {t} | {d} | {src}")
    if n not in hits:
        print("   (未找到)")
