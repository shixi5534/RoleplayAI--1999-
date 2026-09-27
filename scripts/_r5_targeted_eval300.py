# -*- coding: utf-8 -*-
"""R5(丙) 候选边集的 eval300 graph_only 影响评估（复用 _r5_variant_scan 的 harness）。

判据（预注册）：定向补桥必须**无回归**（hit@6 不低于 base，无 down 题）。
"""
from __future__ import annotations

import json
import sys
from collections import Counter, defaultdict
from itertools import combinations
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

from compendium_rag import pipeline as P                      # noqa: E402
from compendium_rag.config import get_settings                # noqa: E402
from compendium_rag.graph_store import Edge                   # noqa: E402
from compendium_rag.retriever import GraphRetriever           # noqa: E402
from _r5_variant_scan import (                                # noqa: E402
    clear_ppr_cache, install_fast_ppr, load_cases, score)

SCENE_REL = "同场"


def main() -> int:
    s = get_settings()
    kb = P.load_kb(s)
    chunks = {c.chunk_id: c for c in kb.chunks}

    mt = json.loads((ROOT / "data/compendium_rag/reports/meetability_test_20260927.json")
                    .read_text(encoding="utf-8"))
    groups = [[m["eid"] for m in gp["members"]] for gp in mt["groups"]]
    verdicts = [gp["verdict"] for gp in mt["groups"]]
    probe = [m["eid"] for m in mt["probe_group"]["members"]]
    probe_deg = {m["eid"]: m["degree"] for m in mt["probe_group"]["members"]}
    gap = set()
    for gi, ms in enumerate(groups):
        if verdicts[gi] == "不可达":
            gap |= set(ms)
    gap |= {m for m in probe if probe_deg.get(m, 99) < 15}

    # 共现对
    chunk2chars: dict[str, set[str]] = defaultdict(set)
    for eid, e in kb.graph.entities.items():
        if e.type == "角色":
            for cid in e.chunk_ids:
                chunk2chars[cid].add(eid)
    pair_ev: dict[tuple[str, str], str] = {}
    for cid, members in chunk2chars.items():
        ms = sorted(members)
        for i in range(len(ms)):
            for j in range(i + 1, len(ms)):
                pair_ev.setdefault((ms[i], ms[j]), cid)

    designs = {
        "S0_base": [],
        "S2_one_end_gap": [p for p in pair_ev if p[0] in gap or p[1] in gap],
        "S3_both_in_scope": None,
    }
    g1hop = set()
    for e in kb.graph.edges:
        if e.src in gap:
            g1hop.add(e.dst)
        if e.dst in gap:
            g1hop.add(e.src)
    scope = gap | g1hop
    designs["S3_both_in_scope"] = [p for p in pair_ev if p[0] in scope and p[1] in scope]

    cases = load_cases(Path(ROOT / "data/knowledge/_audit/rag_testset_300_cn.json"))
    blob = "\n".join(c.text for c in kb.chunks)
    cases = [c for c in cases if any(k in blob for k in c["keywords"])]
    print(f"[tset] answerable n={len(cases)}")

    install_fast_ppr()
    res = {}
    for name, pairs in designs.items():
        clear_ppr_cache()
        if not pairs:
            retr = GraphRetriever(kb.graph, kb.chunks)
            extra = 0
        else:
            g2 = P.load_kb.__self__ if False else None
            import copy
            g2 = copy.deepcopy(kb.graph)
            add = []
            for a, b in pairs:
                add.append(Edge(src=a, dst=b, relation=SCENE_REL, confidence=0.30,
                                evidence=f"同场：{pair_ev[(a, b)]}",
                                chunk_ids=[pair_ev[(a, b)]], count=1))
            g2.edges = list(g2.edges) + add
            g2._edge_index = {e.key: e for e in g2.edges}
            retr = GraphRetriever(g2, kb.chunks)
            extra = len(add)
        hits, rrs, perq = 0, 0.0, {}
        for c in cases:
            h, rr = score(kb, retr, chunks, c, 6)
            hits += h
            rrs += rr
            perq[c["qid"]] = (h, rr)
        n = len(cases)
        res[name] = {"extra": extra, "hit": hits, "n": n, "rate": hits / n,
                     "mrr": rrs / n, "perq": perq}
        print(f"[{name:18}] +{extra:6,} edges  hit@6 {hits}/{n} = {hits / n:.4f}  MRR {rrs / n:.4f}")

    base = res["S0_base"]
    print("\n=== vs base 逐题翻题 ===")
    for name, r in res.items():
        if name == "S0_base":
            continue
        up = [q for q in base["perq"] if not base["perq"][q][0] and r["perq"][q][0]]
        dn = [q for q in base["perq"] if base["perq"][q][0] and not r["perq"][q][0]]
        print(f"[{name:18}] up={len(up)} {up[:6]}  down={len(dn)} {dn[:6]}")

    out = ROOT / "data/compendium_rag/reports/_r5_targeted_eval300.json"
    out.write_text(json.dumps({k: {kk: vv for kk, vv in v.items() if kk != "perq"}
                               for k, v in res.items()}, ensure_ascii=False, indent=2),
                   encoding="utf-8")
    print(f"\n-> {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
