# -*- coding: utf-8 -*-
"""检查 R4 声称救回的三题在「显式次级键」修复后的 seeds，作为归因收尾证据。"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from compendium_rag.graph_store import GraphStore      # noqa: E402
from compendium_rag.retriever import GraphRetriever    # noqa: E402


def main() -> int:
    g = GraphStore.load(ROOT / "data/compendium_rag/graph.json")
    r = GraphRetriever(g, [])
    ts = json.loads((ROOT / "data/knowledge/_audit/rag_testset_300_cn.json")
                    .read_text(encoding="utf-8"))["cases"]
    byid = {str(c.get("id")): c for c in ts}
    for qid in ["R163", "R248", "R299", "R009", "R018"]:
        c = byid.get(qid)
        if not c:
            print(f"{qid}: NOT FOUND")
            continue
        seeds = [f"{s.eid}({s.how})" for s in r.link(c["q"])]
        kw = c.get("keywords") or c.get("keys") or []
        print(f"{qid}: seeds={seeds}")
        print(f"       q={c['q'][:72]}")
        print(f"       keywords={kw}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
