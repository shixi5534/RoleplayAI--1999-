# -*- coding: utf-8 -*-
"""WP2 —— L2 检索质量审查（compendium_rag，v8 冻结口径）。

题源与指标：
  * 300cn-answerable 196 / blind206 / gen120 —— 集合级 Recall@10、MRR@10、
    NDCG@10（二元相关，IDCG 按 |R_q| 截断）、hit@10（对表 v8）、oracle 天花板；
  * 题集i T1 185（_gold_eid 为名字，经本图 alias 解析，实测 100% 可解）
    —— 子图完整性 / 最小性 / 连通性；
  * 角色域题 —— 跨角色知识泄漏率（符号口径：character 类证据块不含被问角色
    名/别名，text/speakers 均不含 → 泄漏候选）。

R_q（全语料相关集）= evidence 并集关键词在块 blob（text+chapter+scene+part）
中任一子串命中的块集合 —— 与 eval300 判分口径同源，只是扩到全语料以支撑
集合级 Recall 与 IDCG。

运行：
    PYTHONHASHSEED=0 .venv/Scripts/python.exe scripts/audit_l2.py
"""
from __future__ import annotations

import argparse
import asyncio
import json
import sys
from pathlib import Path

import audit_common as AC

AC.apply_v8_env()

AUDIT_DIR = AC.ROOT / "data" / "knowledge" / "_audit"
REPORTS_DIR = AC.ROOT / "data" / "compendium_rag" / "reports"
OUT = REPORTS_DIR / "audit_l2.json"
TOP_K = 10


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def diagnose_recall(rows: list[dict]) -> dict:
    """集合级 Recall@10 的可达性诊断：R_q 是按关键词子串在全语料扩出来的，
    |R_q| 远大于 10 时，Recall@10 的上限就是 10/|R_q| —— 与检索好坏无关。
    单列读数，不改判（gate 仍按用户标准 ≥0.85 如实判负）。"""
    import statistics as stats
    nq = [r["n_relevant"] for r in rows if r.get("n_relevant")]
    if not nq:
        return {}
    ceil = [min(r["n_relevant"], 10) / r["n_relevant"] for r in rows
            if r.get("n_relevant")]
    by_set = {}
    for name in sorted({r["set"] for r in rows}):
        m = [r["n_relevant"] for r in rows if r["set"] == name and r.get("n_relevant")]
        if m:
            by_set[name] = {"median_Rq": stats.median(m),
                            "mean_Rq": round(stats.mean(m), 1),
                            "share_Rq_gt_10": round(
                                sum(1 for x in m if x > 10) / len(m), 4)}
    return {
        "median_Rq": stats.median(nq), "mean_Rq": round(stats.mean(nq), 1),
        "share_Rq_gt_10": round(sum(1 for x in nq if x > 10) / len(nq), 4),
        "n_questions_over_10_relevant": sum(1 for x in nq if x > 10),
        "recall_at_10_hard_ceiling": round(stats.mean(ceil), 4),
        "measured_recall_at_10": round(
            sum(r["recall@10"] for r in rows) / len(rows), 4),
        "hit_at_10": round(sum(r["hit@10"] for r in rows) / len(rows), 4),
        "per_set": by_set,
        "reading": "天花板 <0.85 ⇒ 该 gate 在本 R_q 口径下不可达；"
                   "读数差值归金标口径（关键词子串把相关集扩到几十上百块），"
                   "不归检索排序。排序质量看 MRR@10 与 hit@10。",
    }


def main_loop(use_vector: bool, sample_n: int) -> int:
    from compendium_rag import pipeline as P
    from compendium_rag.config import get_settings
    E300 = AC.eval300_module()

    async def run() -> int:
        s = get_settings()
        rep = AC.new_report("WP2", s)
        AC.assert_frozen_graph(rep)
        kb = P.load_kb(s)
        graph = kb.graph
        wl = load_json(AUDIT_DIR / "audit_qid_whitelist.json")["lists"]
        blob_by_cid = {c.chunk_id: AC.blob_of(c) for c in kb.chunks}
        corpus_blob = "\n".join(blob_by_cid.values())

        def relevant_set(keywords: list[str]) -> set[str]:
            keys = [k for k in keywords if k]
            return {cid for cid, blob in blob_by_cid.items()
                    if any(k in blob for k in keys)}

        # ── 检索指标（196 + 206 + 120）──
        sets_cfg = [
            ("300cn", AUDIT_DIR / "rag_testset_300_cn.json",
             set(wl["300cn_answerable"])),
            ("blind", AUDIT_DIR / "blind_v1" / "questions_strict.json",
             set(wl["blind_all"])),
            ("gen", AUDIT_DIR / "rag_testset_gen_r1r2.json",
             set(wl["gen_all"])),
        ]
        q_rows: list[dict] = []
        cmeta = {c.chunk_id: c for c in kb.chunks}
        leak_rows: list[dict] = []
        for name, path, qids in sets_cfg:
            cases = [c for c in E300.load_cases(path) if c.qid in qids]
            if sample_n:
                cases = cases[:sample_n]
            for c in cases:
                r_q = relevant_set(c.keywords)
                res = await kb.retrieve(c.query, top_k=TOP_K,
                                       use_vector=use_vector)
                top_ids = [ev["chunk_id"] for ev in
                           res.get("evidence", [])[:TOP_K]]
                rel = [cid in r_q for cid in top_ids]
                n_rq = len(r_q)
                q_rows.append({
                    "set": name, "qid": c.qid,
                    "hit@10": any(rel), "hit@6": any(rel[:6]),
                    "recall@10": AC.recall_at_k(rel, n_rq),
                    "mrr@10": AC.mrr_at_k(rel),
                    "ndcg@10": AC.ndcg_at_k(rel, n_rq),
                    "n_relevant": n_rq,
                    "oracle_recall@10": min(n_rq, TOP_K) / n_rq if n_rq else 0.0,
                    "answerable": any(k in corpus_blob for k in c.keywords),
                })
                lk = leak_check(res, graph, cmeta)
                if lk is not None:
                    leak_rows.append({"set": name, "qid": c.qid, **lk})
                if len(q_rows) % 50 == 0:
                    print(f"  …{len(q_rows)} 题", flush=True)

        def agg(rows: list[dict]) -> dict:
            n = len(rows) or 1
            return {
                "n": len(rows),
                "hit@10": round(sum(r["hit@10"] for r in rows) / n, 4),
                "recall@10": round(sum(r["recall@10"] for r in rows) / n, 4),
                "mrr@10": round(sum(r["mrr@10"] for r in rows) / n, 4),
                "ndcg@10": round(sum(r["ndcg@10"] for r in rows) / n, 4),
                "oracle_recall@10": round(
                    sum(r["oracle_recall@10"] for r in rows) / n, 4),
            }

        metrics = {
            "all3": agg(q_rows),
            "300cn": agg([r for r in q_rows if r["set"] == "300cn"]),
            "blind": agg([r for r in q_rows if r["set"] == "blind"]),
            "gen": agg([r for r in q_rows if r["set"] == "gen"]),
        }
        rep["metrics"]["retrieval"] = metrics

        g = rep["gate_verdicts"]
        g.append(AC.gate_verdict(
            "L2.1 Recall@10（集合级，主口径=三集合并）", "≥0.85",
            metrics["all3"]["recall@10"],
            "PASS" if metrics["all3"]["recall@10"] >= 0.85 else "FAIL",
            f"oracle 天花板 {metrics['all3']['oracle_recall@10']}：与天花板之差"
            "归语料/金标缺口，不记检索失败（本行为读数说明，不改判）", "检索层"))
        g.append(AC.gate_verdict(
            "L2.1 MRR@10", "≥0.70", metrics["all3"]["mrr@10"],
            "PASS" if metrics["all3"]["mrr@10"] >= 0.70 else "FAIL",
            "", "检索层"))
        g.append(AC.gate_verdict(
            "L2.1 NDCG@10", "≥0.65", metrics["all3"]["ndcg@10"],
            "PASS" if metrics["all3"]["ndcg@10"] >= 0.65 else "FAIL",
            "", "检索层"))

        # ── 子图三指标（题集i T1 185）──
        ti = load_json(AUDIT_DIR / "rag_testset_i.json")
        t1 = [r for r in (ti if isinstance(ti, list) else ti.get("cases", []))
              if r.get("_pool") == "T1" and r.get("_gold_eid")]
        if sample_n:
            t1 = t1[:sample_n]
        unmatched_gold = 0
        aq_gold_pairs: list[tuple[set, set]] = []
        for r in t1:
            gold_names = ([r["_gold_eid"]] if isinstance(r["_gold_eid"], str)
                          else (r["_gold_eid"] or []))
            gold_eids = set()
            for nm in gold_names:
                eid = graph.alias_index.get(str(nm))
                if eid:
                    gold_eids.add(eid)
                else:
                    unmatched_gold += 1
            if not gold_eids:
                continue
            res = await kb.retrieve(r["q"], top_k=TOP_K, use_vector=use_vector)
            # 激活集 A_q：检索命中边上的实体，边分≥0.1，按边分降序截 top30
            # （字段 2026-10-09 起叫 edge_score；旧名 ppr 是误标，值没变，口径不变）
            scored: dict[str, float] = {}
            for e in res.get("edges", []):
                p = float(e.get("edge_score") or 0.0)
                if p >= 0.1:
                    for side in (e["src"], e["dst"]):
                        scored[side] = max(scored.get(side, 0.0), p)
            a_q = set(sorted(scored, key=lambda k: (-scored[k], k))[:30])
            if not a_q:
                anchor = graph.alias_index.get(r.get("_anchor_eid") or "")
                a_q = {anchor} if anchor else set()
            if not a_q:
                continue
            aq_gold_pairs.append((a_q, gold_eids))

        adj = AC.build_adjacency(graph)
        completeness, minimality, connectivity = [], [], []
        for a_q, gold_eids in aq_gold_pairs:
            completeness.append(len(a_q & gold_eids) / len(gold_eids))
            g1 = set(gold_eids)
            for e in gold_eids:
                g1 |= adj.get(e, set())
            minimality.append(len(a_q & g1) / len(a_q))
            connectivity.append(AC.subgraph_connectivity(adj, a_q))

        def mean(xs):
            return round(sum(xs) / len(xs), 4) if xs else None
        sub = {"n": len(completeness), "unmatched_gold_names": unmatched_gold,
               "completeness": mean(completeness),
               "minimality": mean(minimality),
               "connectivity": mean(connectivity)}
        rep["metrics"]["subgraph"] = sub
        for key, target in (("completeness", 0.80), ("minimality", 0.75),
                            ("connectivity", 0.85)):
            v = sub[key]
            g.append(AC.gate_verdict(
                f"L2.2 子图{key}", f"≥{target}", v,
                "PASS" if v is not None and v >= target else "FAIL",
                "题源=题集i T1（gold 名经本图 alias 解析；"
                "A_q=检索边 ppr≥0.1 top30）", "检索层"))

        # ── 跨角色泄漏率（符号口径，角色域题 top-10 证据块）──
        n_role_q = len(leak_rows)
        n_leak_q = sum(1 for r in leak_rows if r["leak"])
        rate = round(n_leak_q / n_role_q, 4) if n_role_q else None
        leak = {"role_domain_questions": n_role_q, "leak_candidates": n_leak_q,
                "rate": rate,
                "examples": [r for r in leak_rows if r["leak"]][:20]}
        rep["metrics"]["role_leak"] = leak
        g.append(AC.gate_verdict(
            "L2.3 跨角色知识泄漏率", "≤0.03", rate,
            "PASS" if rate is not None and rate <= 0.03 else "FAIL",
            "符号口径：角色域题（首 seed 为角色实体）的 top-10 证据块中，"
            "category=='character' 且块 text/speakers 均不含被问角色名/别名 "
            "记一次泄漏候选；judge 精裁在 WP5-confuse 交叉验证", "检索层"))

        rep["per_case"] = q_rows
        out_path = AC.write_report(OUT, rep)
        print(f"WP2 → {out_path}")
        for gv in g:
            print(f"  [{gv['verdict']}] {gv['gate']}: {gv['actual']}")
        return 0

    return asyncio.run(run())


def leak_check(res: dict, graph, cmeta) -> dict | None:
    """角色域题返回 {role, leak, leaked_chunks}；非角色域返回 None。"""
    seeds = res.get("seeds", [])
    if not seeds:
        return None
    ent = graph.entities.get(seeds[0]["eid"])
    if not ent or ent.type != "角色":
        return None
    names = {n for n in (ent.name, *ent.aliases) if n}
    leaked: list[str] = []
    for ev in res.get("evidence", [])[:TOP_K]:
        ch = cmeta.get(ev["chunk_id"])
        if not ch or ch.category != "character":
            continue
        hay = ch.text + "\n" + "\n".join(ch.speakers or [])
        if not any(nm in hay for nm in names):
            leaked.append(ch.chunk_id)
    return {"role": ent.name, "leak": bool(leaked), "leaked_chunks": leaked}


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--sample", type=int, default=0, help="调试：每集只跑前 N 题")
    ap.add_argument("--no-vector", action="store_true",
                    help="graph_only 副口径（Ollama 不可用时；禁与 v8 full 混表）")
    args = ap.parse_args()
    sys.exit(main_loop(use_vector=not args.no_vector, sample_n=args.sample))
