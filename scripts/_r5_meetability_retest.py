# -*- coding: utf-8 -*-
"""R5 落盘后的相遇测试复测（复现 meetability_test_20260927.json 的口径）。

口径来源：reports/meetability_test_20260927.json 的 meta.definitions
  同场相遇  = 组内全成员 chunk_ids 交集非空
  多跳相遇  = 两两无向最短距离 ≤2
本脚本用**相同群组与相同 seed**重测，比较 R5 前后。
"""
from __future__ import annotations

import json
import sys
from collections import defaultdict, deque
from itertools import combinations
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

from compendium_rag import pipeline as P                     # noqa: E402
from compendium_rag.config import get_settings               # noqa: E402
from compendium_rag.graph_store import GraphStore            # noqa: E402


def build_adj(g):
    adj = defaultdict(set)
    for e in g.edges:
        adj[e.src].add(e.dst)
        adj[e.dst].add(e.src)
    return adj


def bfs(adj, a, b, cutoff=6):
    if a == b:
        return 0
    seen, q = {a}, deque([(a, 0)])
    while q:
        n, d = q.popleft()
        if d >= cutoff:
            continue
        for m in adj.get(n, ()):
            if m == b:
                return d + 1
            if m not in seen:
                seen.add(m)
                q.append((m, d + 1))
    return None


def stats(g, groups, probe, chunk_ids):
    adj = build_adj(g)
    rows = []
    for members in groups:
        ds = [bfs(adj, a, b) for a, b in combinations(members, 2)]
        rows.append({"members": members, "dists": ds,
                     "verdict": _verdict(ds)})
    probe_ds = [bfs(adj, a, b) for a, b in combinations(probe, 2)]
    same = 0
    for members in groups:
        if not members:
            continue
        inter = set(chunk_ids[members[0]])
        for m in members[1:]:
            inter &= chunk_ids[m]
        if inter:
            same += 1
    return rows, probe_ds, same


def _verdict(ds):
    if all(d is not None and d <= 2 for d in ds):
        return "全员可遇"
    if all(d is None for d in ds):
        return "不可达"
    if any(d is not None and d <= 2 for d in ds):
        return "部分可遇"
    return "不可达"


def main() -> int:
    s = get_settings()
    mt = json.loads((ROOT / "data/compendium_rag/reports/meetability_test_20260927.json")
                    .read_text(encoding="utf-8"))
    groups = [[m["eid"] for m in gp["members"]] for gp in mt["groups"]]
    probe = [m["eid"] for m in mt["probe_group"]["members"]]

    before = GraphStore.load(ROOT / "data/compendium_rag/backups/graph.json.prev.r5")
    after = GraphStore.load(s.graph_path)
    print(f"[before prev.r5] 实体={len(before.entities)} 边={len(before.edges)}")
    print(f"[after  r5     ] 实体={len(after.entities)} 边={len(after.edges)}")

    def chunkmap(g):
        return {eid: set(e.chunk_ids) for eid, e in g.entities.items()}

    r0, p0, s0 = stats(before, groups, probe, chunkmap(before))
    r1, p1, s1 = stats(after, groups, probe, chunkmap(after))

    def summarize(rows, probe_ds, same):
        bad = sum(1 for r in rows for d in r["dists"] if d is None or d > 2)
        tot = sum(len(r["dists"]) for r in rows)
        vd = defaultdict(int)
        for r in rows:
            vd[r["verdict"]] += 1
        return bad, tot, sum(1 for d in probe_ds if d is None or d > 2), len(probe_ds), dict(vd), same

    b = summarize(r0, p0, s0)
    a = summarize(r1, p1, s1)
    print()
    print(f"  组内 ≥3跳/不可达 : {b[0]}/{b[1]}  ->  {a[0]}/{a[1]}   （改善 {b[0]-a[0]}）")
    print(f"  probe ≥3跳/不可达: {b[2]}/{b[3]}  ->  {a[2]}/{a[3]}")
    print(f"  verdict 分布     : {b[4]} -> {a[4]}")
    print(f"  同场组数         : {b[5]} -> {a[5]}")
    print()
    for i, (x, y) in enumerate(zip(r0, r1), 1):
        if x["dists"] != y["dists"]:
            print(f"  group{i}: {x['verdict']} -> {y['verdict']}   {x['dists']} -> {y['dists']}")

    out = ROOT / "data/compendium_rag/reports/meetability_test_after_r5.json"
    out.write_text(json.dumps({
        "meta": {"test": "相遇测试复测（R5 落盘后）", "date": "2026-09-27",
                 "note": "复用 meetability_test_20260927.json 的群组与口径",
                 "before": {"edges": len(before.edges)}, "after": {"edges": len(after.edges)}},
        "summary": {"before_group_bad": b[0], "after_group_bad": a[0],
                    "groups_total_pairs": b[1],
                    "before_probe_bad": b[2], "after_probe_bad": a[2],
                    "probe_pairs": b[3],
                    "before_verdicts": b[4], "after_verdicts": a[4],
                    "before_same_scene_groups": b[5], "after_same_scene_groups": a[5]},
        "groups_after": [{"members": r["members"], "dists": r["dists"], "verdict": r["verdict"]}
                         for r in r1],
        "probe_dists_after": p1,
    }, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\n-> {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
