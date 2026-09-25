# -*- coding: utf-8 -*-
"""并集探针(可复用):python _probe_union.py <候选名文件,一行一个>"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT.parent.parent / "src"))
from compendium_rag.graph_store import GraphStore  # noqa: E402

g = GraphStore.load(ROOT / "graph.json")
known = set(g.entities)
alias_owner = {}
for e in g.entities.values():
    for a in e.aliases:
        alias_owner.setdefault(a, e.name)
for bf in sorted(ROOT.glob("_agent_batch*.json")):
    try:
        data = json.loads(bf.read_text(encoding="utf-8"))
    except Exception:
        continue
    for blk in data.values():
        for e in blk.get("entities", []):
            n = e.get("name")
            if n:
                known.add(n)
            for a in (e.get("aliases") or []):
                alias_owner.setdefault(a, n)

cands = []
for l in Path(sys.argv[1]).read_text(encoding="utf-8").splitlines():
    l = l.strip()
    if l and l not in cands:
        cands.append(l)

print(f"图谱实体 {len(g.entities)}｜并集 {len(known)}｜候选 {len(cands)}")
for n in cands:
    if n in g.entities:
        print(f"  EXISTS {n}  resolve={g.resolve(n)!r}")
    elif n in known:
        print(f"  EXISTS(batch) {n}")
    elif n in alias_owner:
        print(f"  ALIAS  {n} → {alias_owner[n]}")
    else:
        near = sorted(x for x in known
                      if (len(n) >= 2 and n in x) or (len(x) >= 2 and x in n))
        print(f"  new    {n}" + (f"  ≈{near[:6]}" if near else ""))
