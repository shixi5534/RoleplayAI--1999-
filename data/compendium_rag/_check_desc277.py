# -*- coding: utf-8 -*-
"""只读 desc 核对(277 号位专用):python _check_desc277.py <名字文件>
打印 graph.json 与全部 batch 并集中每个名字的 desc 出处,用于 §4.6 语义判定。
"""
import json
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT.parent.parent / "src"))
from compendium_rag.graph_store import GraphStore  # noqa: E402

g = GraphStore.load(ROOT / "graph.json")
targets = [l.strip() for l in Path(sys.argv[1]).read_text(encoding="utf-8").splitlines() if l.strip()]

agg = defaultdict(lambda: defaultdict(set))
for e in g.entities.values():
    if e.name in targets:
        agg[e.name][f"GRAPH|{e.type}|{e.desc}"].add("-")
for bf in sorted(ROOT.glob("_agent_batch*.json")):
    try:
        data = json.loads(bf.read_text(encoding="utf-8"))
    except Exception:
        continue
    tag = bf.stem.replace("_agent_batch", "")
    for blk in data.values():
        for en in blk.get("entities", []):
            if en.get("name") in targets:
                agg[en["name"]][f"b{tag}|{en.get('type')}|{en.get('desc')}"].add("-")
for n in targets:
    descs = agg.get(n)
    if not descs:
        print(f"-- {n}: (无既有 desc)")
        continue
    print(f"== {n}")
    for d in sorted(descs):
        print(f"   {d}")
