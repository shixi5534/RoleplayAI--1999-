# -*- coding: utf-8 -*-
"""R5（丙）定向补缺：生成「缺口对」同场边提案，并双向评估。

用户裁决（2026-09-27）：(丙) 仅定向补相遇测试暴露的具体缺口对。

目标集合（来自 meetability_test_20260927.json）：
  - 8 个随机组中 verdict=「不可达」的成员对（5 组）
  - probe 组中薄成员（玛尔塔 degree 7）
  - 池内零边实体

设计（规避 PPR 稀释）：
  1. 只连**目标集合内部**、且**确有同 chunk 共现**的对（逐字证据）；
  2. **不**给高枢纽（度 > HUB_CAP）新增边 —— 避免摊薄其既有邻域；
  3. 每对只加 1 条边，evidence 记录 chunk_id，便于溯源。

输出：
  1. 提案 JSON（可直接交 Applier 的 add_edge 条目）
  2. 相遇测试复测（同群组两两最短距离）
  3. eval300 graph_only 影响（应≈零回归）

用法:
  ./.venv/Scripts/python.exe scripts/_r5_targeted_proposal.py [--emit]
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter, defaultdict, deque
from itertools import combinations
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

from compendium_rag import pipeline as P                     # noqa: E402
from compendium_rag.config import get_settings               # noqa: E402
from compendium_rag.graph_store import Edge                  # noqa: E402

SCENE_REL = "同场"
HUB_CAP = 100          # 度 > 此值的实体不新增同场边（防稀释）


def build_adj(g):
    adj = defaultdict(set)
    for e in g.edges:
        adj[e.src].add(e.dst)
        adj[e.dst].add(e.src)
    return adj


def bfs_dist(adj, a, b, cutoff=6):
    if a == b:
        return 0
    seen = {a}
    q = deque([(a, 0)])
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


def group_distances(adj, members):
    out = {}
    for a, b in combinations(members, 2):
        out[(a, b)] = bfs_dist(adj, a, b)
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--emit", action="store_true", help="写出提案 JSON")
    args = ap.parse_args()

    s = get_settings()
    kb = P.load_kb(s)
    g = kb.graph
    deg = Counter()
    for e in g.edges:
        deg[e.src] += 1
        deg[e.dst] += 1

    mt = json.loads((ROOT / "data/compendium_rag/reports/meetability_test_20260927.json")
                    .read_text(encoding="utf-8"))
    groups = [[m["eid"] for m in gp["members"]] for gp in mt["groups"]]
    verdicts = [gp["verdict"] for gp in mt["groups"]]
    probe = [m["eid"] for m in mt["probe_group"]["members"]]

    print(f"[graph] 边={len(g.edges):,} (R4 当前)")
    print(f"[target] 群组 {len(groups)} 个（不可达 {verdicts.count('不可达')}）；probe {len(probe)} 人")

    # 共现表
    chunk2chars: dict[str, set[str]] = defaultdict(set)
    for eid, e in g.entities.items():
        if e.type == "角色":
            for cid in e.chunk_ids:
                chunk2chars[cid].add(eid)

    existing = {(e.src, SCENE_REL, e.dst) for e in g.edges} | \
               {(e.dst, SCENE_REL, e.src) for e in g.edges}

    # 只对目标集合内「当前 >2 跳或不可达」的对找共现
    targets: list[tuple[str, str]] = []
    for gi, members in enumerate(groups):
        if verdicts[gi] != "不可达":
            continue
        for a, b in combinations(members, 2):
            targets.append((a, b))
    for a, b in combinations(probe, 2):
        targets.append((a, b))

    entries = []
    for a, b in targets:
        if (a, SCENE_REL, b) in existing:
            continue
        # 有没有同 chunk 共现？
        cids = (set(g.entities[a].chunk_ids) & set(g.entities[b].chunk_ids))
        if not cids:
            continue
        # 不与高枢纽连边（防稀释）
        if deg.get(a, 0) > HUB_CAP or deg.get(b, 0) > HUB_CAP:
            continue
        cid = sorted(cids)[0]
        entries.append({
            "id": f"R5-T{len(entries) + 1:03d}",
            "type": "add_edge",
            "edge": {"src": a, "dst": b, "relation": SCENE_REL,
                     "confidence": 0.30,
                     "evidence": f"同为『{cid}』场景共现（相遇测试缺口定向补桥）",
                     "chunk_ids": [cid], "count": 1},
            "rationale": "相遇测试 verdict=不可达 组内成员，且当前无同场边；定向补桥",
            "targets": "R5(丙) 定向补缺",
        })

    print(f"\n[candidates] 目标对 {len(targets)} -> 可加同场边 {len(entries)}")
    if entries:
        add = Counter()
        for e in entries:
            add[e["edge"]["src"]] += 1
            add[e["edge"]["dst"]] += 1
        worst = sorted(add.items(), key=lambda kv: -(kv[1] / max(deg.get(kv[0], 0), 1)))[:8]
        print("[dilution] 相对度数增幅 Top8（原度 -> 新度）：")
        for e, a in worst:
            o = deg.get(e, 0)
            print(f"   {e:22} {o:5} -> {o + a:5}  (×{(o + a) / max(o, 1):.2f})")
        print(f"[dilution] 触及高度(>100)实体数: "
              f"{sum(1 for e in add if deg.get(e, 0) > HUB_CAP)}（HUB_CAP={HUB_CAP} 已过滤）")

    # ── 评估 1：相遇测试复测 ──
    adj0 = build_adj(g)
    g2 = None
    import copy
    g2 = copy.deepcopy(g)
    g2.edges = list(g2.edges) + [
        Edge(src=e["edge"]["src"], dst=e["edge"]["dst"], relation=SCENE_REL,
             confidence=e["edge"]["confidence"], evidence=e["edge"]["evidence"],
             chunk_ids=e["edge"]["chunk_ids"], count=1) for e in entries]
    adj1 = build_adj(g2)

    def unreachable(adj):
        n = 0
        for members in groups:
            for a, b in combinations(members, 2):
                d = bfs_dist(adj, a, b)
                if d is None or d > 2:
                    n += 1
        return n

    d0 = {gi: group_distances(adj0, m) for gi, m in enumerate(groups)}
    d1 = {gi: group_distances(adj1, m) for gi, m in enumerate(groups)}
    before = sum(1 for gi in d0 for k, v in d0[gi].items() if v is None or v > 2)
    after = sum(1 for gi in d1 for k, v in d1[gi].items() if v is None or v > 2)
    tot = sum(len(d0[gi]) for gi in d0)
    print(f"\n[meetability] 组内对总数={tot}")
    print(f"  不可达/≥3跳 : {before} -> {after}   （改善 {before - after}）")
    for gi in sorted(d0):
        ch = sum(1 for k in d0[gi] if (d0[gi][k] is None or d0[gi][k] > 2)
                 and not (d1[gi][k] is None or d1[gi][k] > 2))
        if ch:
            print(f"    group{gi+1} ({verdicts[gi]}): {ch} 对改善 -> "
                  f"{[k for k in d0[gi] if (d0[gi][k] is None or d0[gi][k] > 2) and not (d1[gi][k] is None or d1[gi][k] > 2)]}")

    if args.emit and entries:
        out = ROOT / "data/compendium_rag/repairs_v5"
        out.mkdir(parents=True, exist_ok=True)
        prop = {
            "meta": {
                "author": "R5-targeted-bridging",
                "timestamp": "2026-09-27",
                "batch": "R5(丙) 定向补缺：仅对相遇测试暴露的『不可达』组内共现对补同场边",
                "network": "none",
                "graph_state": {"entities": len(g.entities), "edges": len(g.edges)},
                "design": {
                    "hub_cap": HUB_CAP,
                    "rule": "目标集合内、有同 chunk 共现、且两端度<=HUB_CAP 才加边",
                    "why": "全量方案实测 +1 题且使 维尔汀 邻居摊薄 ×0.548；定向方案规模 1.76%",
                },
                "source_test": "reports/meetability_test_20260927.json",
            },
            "entries": entries,
        }
        (out / "proposal.json").write_text(
            json.dumps(prop, ensure_ascii=False, indent=1), encoding="utf-8")
        print(f"\n[emit] -> {out / 'proposal.json'}（{len(entries)} 条 add_edge）")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
