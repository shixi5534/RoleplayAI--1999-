# -*- coding: utf-8 -*-
"""只读辅助:打印候选名在 graph.json ∪ 全部 batch 里的 desc/type(§4.6 语义核对用)。
用法: python _probe259_desc.py <名字文件>   (纯只读,不改任何文件)
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT.parent.parent / "src"))
from compendium_rag.graph_store import GraphStore  # noqa: E402

names = [l.strip() for l in Path(sys.argv[1]).read_text(encoding="utf-8").splitlines() if l.strip()]
g = GraphStore.load(ROOT / "graph.json")
for n in names:
    e = g.entities.get(n)
    if e is None:
        # resolve 到的 canonical 节点
        r = g.resolve(n)
        if r and r in g.entities:
            e = g.entities[r]
            print(f"[graph-via-resolve {n} -> {r}] type={e.type} desc={e.desc} aliases={list(e.aliases)[:8]}")
    else:
        print(f"[graph {n}] type={e.type} desc={e.desc} members={len(getattr(e,'members',[]) or [])} aliases={list(e.aliases)[:8]}")

for bf in sorted(ROOT.glob("_agent_batch*.json")):
    try:
        data = json.loads(bf.read_text(encoding="utf-8"))
    except Exception:
        continue
    for k, blk in data.items():
        for ent in blk.get("entities", []):
            if ent.get("name") in names:
                print(f"[{bf.name} {k}] {ent['name']} type={ent.get('type')} desc={ent.get('desc')} aliases={ent.get('aliases')}")
