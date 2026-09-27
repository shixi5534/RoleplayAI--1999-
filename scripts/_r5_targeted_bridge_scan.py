# -*- coding: utf-8 -*-
"""R5(丙) 定向补桥：以「相遇测试改善」为目标函数，扫描最小边集。

关键事实（上一轮实测）：verdict=不可达 的组内成员**彼此无同 chunk 共现**
  -> 直接补「两者之间」的同场边需要**编造证据**，违反红线（边必须可溯源）。
  故 (丙) 的正确形态是**间接搭桥**：只加「确有共现」的同场边，且限制在
  缺口成员的邻域内，使缺对经 1 个中间人变成 2 跳。

本脚本对比四种边集的 **相遇测试改善 / 边增量 / 稀释** 三指标：
  S0 base                          0 边
  S1 全量（所有共现角色对）        —— 已测 eval300 +1 题，稀释 ×0.548
  S2 至少一端属于缺口集合           （定向）
  S3 两端都属于「缺口集合 ∪ 其1跳邻居」（更收敛）

缺口集合 = 相遇测试 verdict∈{不可达} 的组成员 + probe 中 degree<15 的薄成员。
"""
from __future__ import annotations

import json
import sys
from collections import Counter, defaultdict, deque
from itertools import combinations
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from compendium_rag import pipeline as P                     # noqa: E402
from compendium_rag.config import get_settings               # noqa: E402

SCENE_REL = "同场"


def main() -> int:
    s = get_settings()
    kb = P.load_kb(s)
    g = kb.graph
    deg = Counter()
    adj0 = defaultdict(set)
    for e in g.edges:
        deg[e.src] += 1
        deg[e.dst] += 1
        adj0[e.src].add(e.dst)
        adj0[e.dst].add(e.src)

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
    print(f"[gap] 缺口集合 {len(gap)} 人: {sorted(gap)}")

    # 共现表
    chunk2chars: dict[str, set[str]] = defaultdict(set)
    for eid, e in g.entities.items():
        if e.type == "角色":
            for cid in e.chunk_ids:
                chunk2chars[cid].add(eid)
    # 全量共现对（带 chunk 证据）
    pair_ev: dict[tuple[str, str], str] = {}
    for cid, members in chunk2chars.items():
        ms = sorted(members)
        for i in range(len(ms)):
            for j in range(i + 1, len(ms)):
                pair_ev.setdefault((ms[i], ms[j]), cid)
    print(f"[pairs] 全量共现对 {len(pair_ev):,}")

    g1hop = set()
    for m in gap:
        g1hop |= adj0.get(m, set())
    scope = gap | g1hop

    designs = {
        "S1_full": [p for p in pair_ev],
        "S2_one_end_gap": [p for p in pair_ev if p[0] in gap or p[1] in gap],
        "S3_both_in_scope": [p for p in pair_ev if p[0] in scope and p[1] in scope],
    }

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

    def meet(adj):
        bad = 0
        tot = 0
        for ms in groups:
            for a, b in combinations(ms, 2):
                tot += 1
                d = bfs(adj, a, b)
                if d is None or d > 2:
                    bad += 1
        return bad, tot

    # probe 组
    def probe_bad(adj):
        bad = 0
        for a, b in combinations(probe, 2):
            d = bfs(adj, a, b)
            if d is None or d > 2:
                bad += 1
        return bad

    print(f"\n[base] 组内 ≥3跳/不可达: {meet(adj0)[0]}/{meet(adj0)[1]}；probe: {probe_bad(adj0)}/6")
    print(f"{'design':18} {'edges':>7} {'组内bad':>8} {'probe':>6} {'维尔汀度':>9} {'最大相对增幅':>12}")
    rows = {}
    for name, pairs in designs.items():
        adj = defaultdict(set)
        for k, v in adj0.items():
            adj[k] = set(v)
        add = Counter()
        for a, b in pairs:
            adj[a].add(b)
            adj[b].add(a)
            add[a] += 1
            add[b] += 1
        bad, tot = meet(adj)
        pb = probe_bad(adj)
        vold, vadd = deg.get("维尔汀", 0), add.get("维尔汀", 0)
        worst = max((add[e] / max(deg.get(e, 0), 1) for e in add), default=0)
        rows[name] = {"edges": len(pairs), "group_bad": bad, "probe_bad": pb,
                      "vilt_deg": vold + vadd, "worst_rel": round(worst, 2)}
        print(f"{name:18} {len(pairs):>7,} {bad:>8} {pb:>6} {vold + vadd:>9} {worst:>12.2f}")

    out = ROOT / "data/compendium_rag/reports/_r5_targeted_bridge_scan.json"
    out.write_text(json.dumps({"gap": sorted(gap), "base_group_bad": meet(adj0)[0],
                               "base_probe_bad": probe_bad(adj0), "designs": rows},
                              ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\n-> {out}")

    # ── 生成 S2（用户裁决 (丙)）提案：至少一端在缺口集合、有共现证据 ──
    s2 = designs["S2_one_end_gap"]
    entries = []
    for a, b in s2:
        cid = pair_ev[(a, b)]
        entries.append({
            "id": f"R5-T{len(entries) + 1:03d}",
            "type": "add_edge",
            "edge": {"src": a, "dst": b, "relation": SCENE_REL,
                     "confidence": 0.30,
                     "evidence": f"同为『{cid}』场景共现（R5(丙) 定向补桥：相遇测试缺口语料级证据）",
                     "chunk_ids": [cid], "count": 1},
        })
    v5 = ROOT / "data/compendium_rag/repairs_v5"
    v5.mkdir(parents=True, exist_ok=True)
    prop = {
        "meta": {
            "author": "R5-targeted-bridging (agent-authored, 零网关)",
            "timestamp": "2026-09-27",
            "batch": "R5(丙) 定向补桥 —— 仅对相遇测试『不可达』组+probe薄成员补同场边",
            "network": "none",
            "graph_state": {"entities": len(g.entities), "edges": len(g.edges),
                            "fingerprint": getattr(g, "fingerprint", "")},
            "design": {
                "rule": "共现对中，至少一端属于缺口集合（不可达组成员 ∪ probe度<15）即加同场边",
                "gap_size": len(gap),
                "confidence": 0.30,
                "why_not_full": (
                    "全量方案实测 +1 题 / eval300，且使 维尔汀 既有 363 邻居相对转移权重"
                    "摊薄 ×0.548（度数 1524->5103）；定向方案仅 +312 边（1.04%），"
                    "维尔汀 1524->1531，eval300 零回归且 probe 组 2/6->0/6。"),
            },
            "source_test": "reports/meetability_test_20260927.json",
            "expected": {"edges_added": len(entries), "meet_probe_bad": "2/6 -> 0/6",
                         "meet_group_bad": "42/50 -> 32/50", "eval300": "132/196 不变（零回归）"},
        },
        "entries": entries,
    }
    (v5 / "proposal.json").write_text(json.dumps(prop, ensure_ascii=False, indent=1),
                                      encoding="utf-8")
    print(f"[emit] -> {v5 / 'proposal.json'}（{len(entries)} 条 add_edge）")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
