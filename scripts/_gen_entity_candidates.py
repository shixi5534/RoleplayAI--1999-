# -*- coding: utf-8 -*-
"""阶段 1：图邻域候选生成器（零网关、零模型、只读图谱）。

对每题：现有 link() 取 seed → seed 的 1-hop 图邻域正名 → 扁平候选名表。
超过 CAP 时按 PPR 分截断。只输出**名字**，绝不输出边/关系/度数
（计划书 §3.3：给边=字符串匹配作弊）。

产物：
  data/compendium_rag/entity_candidates_<set>.json   —— 识别视图 {qid: {query, candidates}}
  data/compendium_rag/entity_candidates_stats_<set>.json —— 覆盖率与规模统计（闸门用）
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from compendium_rag import pipeline as P  # noqa: E402
from compendium_rag.config import get_settings  # noqa: E402
from compendium_rag.retriever import personalized_pagerank  # noqa: E402

CAP = 200
RE_CN = re.compile(r"[\u4e00-\u9fff]")

SETS = {
    "native": ROOT / "data" / "knowledge" / "_audit" / "rag_testset_native.json",
    "300_cn": ROOT / "data" / "knowledge" / "_audit" / "rag_testset_300_cn.json",
    "i": ROOT / "data" / "knowledge" / "_audit" / "rag_testset_i.json",
}


def flatten_evidence(ev) -> list[str]:
    out: list[str] = []
    for grp in (ev or []):
        if isinstance(grp, str):
            out.append(grp)
        elif isinstance(grp, (list, tuple)):
            out.extend(str(x) for x in grp if x)
    seen, res = set(), []
    for k in out:
        k = k.strip()
        if k and k not in seen:
            seen.add(k)
            res.append(k)
    return res


def load_cases(path: Path) -> list[dict]:
    d = json.loads(path.read_text(encoding="utf-8"))
    rows = d if isinstance(d, list) else d.get("cases", [])
    return [{"qid": str(r.get("id", "")), "query": r.get("q", ""),
             "keywords": flatten_evidence(r.get("evidence")),
             "pool": r.get("_pool", ""), "dims": r.get("dims") or {},
             "gold_eid": r.get("_gold_eid")}
            for r in rows if flatten_evidence(r.get("evidence"))]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--set", choices=list(SETS), default="native")
    ap.add_argument("--cap", type=int, default=CAP)
    args = ap.parse_args()

    kb = P.load_kb(get_settings())
    g = kb.graph
    ret = kb.retriever
    adj = ret._adj

    cases = load_cases(SETS[args.set])
    payload: dict[str, dict] = {}
    stats: list[dict] = []

    for c in cases:
        seeds = ret.link(c["query"], top_k=6)
        seed_eids = [s.eid for s in seeds]
        # 候选池 = seed 自身 ∪ seed 的 1-hop 邻域（seed 也是合法白名单项）
        cand_eids: dict[str, None] = {}
        for eid in seed_eids:
            cand_eids.setdefault(eid, None)
            for nb, _w in adj.get(eid, []):
                cand_eids.setdefault(nb, None)
        cand_eids = list(cand_eids)
        truncated = False
        if len(cand_eids) > args.cap:
            seed_map = {s.eid: s.score for s in seeds}
            ppr = personalized_pagerank(adj, seed_map)
            cand_eids.sort(key=lambda e: -ppr.get(e, 0.0))
            cand_eids = cand_eids[:args.cap]
            truncated = True
        names = sorted({g.entities[e].name for e in cand_eids
                        if e in g.entities})

        gold_eids = {c.get("gold_eid")} | {g.resolve(k) for k in c["keywords"]}
        gold_eids.discard(None)
        gold_names_in_cands = bool(set(names) & set(c["keywords"]))
        covered = bool(gold_eids & set(cand_eids)) or gold_names_in_cands

        payload[c["qid"]] = {"query": c["query"], "candidates": names,
                             "n_seeds": len(seed_eids),
                             "seeds": [s.name for s in seeds]}
        stats.append({"qid": c["qid"], "pool": c["pool"], "seeded": bool(seed_eids),
                      "n_cands": len(names), "truncated": truncated,
                      "covered": covered, "answerable_kw_in_corpus": None,
                      "dims": c["dims"]})

    out_dir = get_settings().data_dir
    tag = args.set
    (out_dir / f"entity_candidates_{tag}.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=1), encoding="utf-8")

    def agg(rows: list[dict]) -> dict:
        n = len(rows)
        seeded = [r for r in rows if r["seeded"]]
        return {"n": n, "seeded": len(seeded),
                "cov_overall": round(sum(r["covered"] for r in rows) / n, 4) if n else None,
                "cov_seeded": round(sum(r["covered"] for r in seeded) / len(seeded), 4) if seeded else None,
                "cands_median": (lambda v: v[len(v) // 2] if v else 0)(sorted(r["n_cands"] for r in seeded)),
                "cands_p90": (lambda v: v[min(len(v) - 1, int(len(v) * 0.9))] if v else 0)(sorted(r["n_cands"] for r in seeded)),
                "cands_max": max((r["n_cands"] for r in seeded), default=0),
                "truncated": sum(r["truncated"] for r in rows)}

    by_pool: dict[str, dict] = {}
    pools = {r["pool"] or r["dims"].get("type", "?") for r in stats}
    for p in sorted(pools):
        by_pool[p] = agg([r for r in stats if (r["pool"] or r["dims"].get("type", "?")) == p])

    report = {"set": tag, "cap": args.cap, "overall": agg(stats),
              "by_pool": by_pool,
              "per_q": stats}
    (out_dir / f"entity_candidates_stats_{tag}.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=1), encoding="utf-8")

    print(f"[{tag}] overall={agg(stats)}")
    for p, v in by_pool.items():
        print(f"  pool {p}: {v}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
