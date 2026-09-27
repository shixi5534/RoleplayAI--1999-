# -*- coding: utf-8 -*-
"""召回上限诊断：gold 证据块在候选池中的**最深排名**决定瓶颈性质。

判据（先于结果固定）：
  - 若 gold 在 top-30 池内命中率 >> hit@6 -> 瓶颈是**排序**（reranker 可解决）
  - 若 gold 在 top-30 池内命中率 ≈ hit@6 -> 瓶颈是**召回**（需改检索/图谱/查询侧）
  - 若 gold 在 top-100 仍不可达 -> 图谱/语料层缺口

用 rank_collect（含每题的 top-30 证据块与 gold 关键词）直接计算。
"""
from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from compendium_rag.config import get_settings               # noqa: E402


def load_cases(p: Path):
    d = json.loads(p.read_text(encoding="utf-8"))
    rows = d if isinstance(d, list) else d.get("cases", [])
    out = {}
    for r in rows:
        kws = []
        for grp in (r.get("evidence") or []):
            if isinstance(grp, str):
                kws.append(grp)
            elif isinstance(grp, (list, tuple)):
                kws.extend(str(x) for x in grp if x)
        kws = [k.strip() for k in kws]
        kws = [k for i, k in enumerate(kws) if k and k not in kws[:i]]
        if kws:
            out[str(r.get("id"))] = kws
    return out


def main() -> int:
    s = get_settings()
    from compendium_rag import pipeline as P
    kb = P.load_kb(s)
    chunks = {c.chunk_id: c for c in kb.chunks}

    collect = json.loads((ROOT / "data/compendium_rag/reports/rank_collect_r5_top30.json")
                         .read_text(encoding="utf-8"))
    cases = load_cases(ROOT / "data/knowledge/_audit/rag_testset_300_cn.json")

    blob = {cid: f"{c.text}\n{c.chapter_title}\n{c.scene_title}\n{c.part_title}"
            for cid, c in chunks.items()}

    # rows 里已有 rank（首命中排名，0/None 表示池内无命中）与 evidence
    first_rank = {"full": {}, "graph_only": {}}
    ans = {"full": set(), "graph_only": set()}
    for r in collect["rows"]:
        qid = str(r.get("qid"))
        mode = r.get("mode")
        if mode not in first_rank:
            continue
        if r.get("answerable"):
            ans[mode].add(qid)
        rk = r.get("rank")
        first_rank[mode][qid] = rk if rk else None

    print("=" * 78)
    for mode in ("full", "graph_only"):
        fr = {q: first_rank[mode].get(q) for q in ans[mode]}
        n = len(fr)
        print(f"\n[{mode}]  answerable 题数={n}")
        for k in (6, 10, 20, 30):
            hit = sum(1 for v in fr.values() if v is not None and v <= k)
            print(f"   hit@{k:<3} = {hit}/{n} = {hit / n:.4f}")
        none = sum(1 for v in fr.values() if v is None)
        print(f"   池内(30)完全无命中 = {none}/{n} = {none / n:.4f}   <- 召回硬缺口")
        dist = Counter(v for v in fr.values() if v is not None)
        print(f"   首命中排名直方图（1-10）: "
              f"{[(k, dist.get(k, 0)) for k in range(1, 11)]}")
        miss = sorted([q for q, v in fr.items() if v is None])
        print(f"   池内 miss 题号（{len(miss)}）: {miss}")
    print("=" * 78)
    print("\n解读：hit@30 与 hit@6 的差 = reranker 可兑现空间；")
    print("      1 - hit@30 = 需靠**检索侧/图谱/查询侧**解决的召回缺口。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
