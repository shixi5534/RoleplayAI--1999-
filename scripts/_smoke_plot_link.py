# ruff: noqa: T201
"""冒烟：复现冒烟测试暴露的实体链接问题（临时诊断脚本）。

用法：
    .venv/Scripts/python.exe scripts/_smoke_plot_link.py
"""
import logging
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

logging.basicConfig(level=logging.WARNING, format="%(levelname)s %(name)s: %(message)s")

from roleplay.core.knowledge.plot_graph import PlotGraphRegistry  # noqa: E402

CID = "wu_ming_zhe"
registry = PlotGraphRegistry(
    corpus_dir=ROOT / "data" / "knowledge",
    graph_dir=ROOT / "data" / "knowledge",
    alias_dir=ROOT / "data" / "lore",
    min_confidence=0.6,
    include_weak=False,
    max_edges=10,
    max_hops=2,
    damping=0.85,
    link_threshold=0.35,
)

retr = registry.get(CID)
if retr is None:
    print("!! 图谱未加载")
    raise SystemExit(1)

print(f"graph entities={len(retr.store.entities())} edges={len(retr.store.all_edges())}")


def name_of(eid: str) -> str:
    ent = retr.store.get_entity(eid)
    return str((ent or {}).get("name") or eid)


QUERIES = [
    "露西女士是谁",
    "Madam Lucy",
    "露西",
    "3.8版本 世纪末尺度 发生了什么",
    "无名者的发条装置",
    "维尔汀和基金会的关系",
    "暴雨是什么",
]

for q in QUERIES:
    seeds = retr.link(q)
    print(f"\n=== link({q!r}) -> {len(seeds)} seeds ===")
    for eid, w in sorted(seeds.items(), key=lambda kv: -kv[1]):
        ent = retr.store.get_entity(eid) or {}
        print(f"  {w:.2f}  {ent.get('name')!r}  aliases={ent.get('aliases')}")

    chunks = retr.retrieve(q, top_chunks=3, lexical_fallback=2)
    via = {}
    for c in chunks:
        v = str(c.metadata.get("via"))
        via[v] = via.get(v, 0) + 1
    print(f"  retrieve -> {len(chunks)} chunks, via={via}")
    for c in chunks[:2]:
        m = c.metadata
        print(f"    [{m.get('via')}] {m.get('section')} | {str(c.text)[:60]!r}")
