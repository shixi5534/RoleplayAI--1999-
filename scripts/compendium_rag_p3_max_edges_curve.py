# -*- coding: utf-8 -*-
"""v9-P3 · `graph_max_edges` 截断实测曲线（只读，零 LLM/零嵌入）。

背景：图通道把边硬截到 30（`retriever.py:405-428`），此前**从未被观测过**。
P3 步骤1 的 A/B 顺带量出：24 题样本里 23 题有种子，这 23 题返回的边数**全部正好
等于 30**——触顶率 100%。所以这一刀每题都在切东西，问题是切掉的是内容还是噪声。

判据已在 `docs/compendium-rag/优化计划_v9_2026-10-08.md` §P3 **先于跑数登记**：
1. **主判据是结构**：对「30 档 miss、更高档 hit」的翻转题，找出命中块所依边在
   **无上限**边序里的名次；名次多数 >30 才算「切掉了内容」。
2. 读数（hit@6 / MRR）只报告，**不用来选档**——不许拿涨幅当改默认值的理由
   （[[fix-data-not-metrics]]）。改默认值属口径变更，要按 §4bis 冷启动重校准。

口径：`graph_only`（`use_vector=False`，向量通道与本次改动无关，关掉是为了不依赖
Ollama）+ 冻结融合 `CMPRAG_LEX_WEIGHT=1.0 CMPRAG_RRF_K=1 CMPRAG_LEX_FIRST=0
PYTHONHASHSEED=0`。判分函数直接用 `scripts/compendium_rag_eval300.py` 的
`load_cases/score_case/summarize`，与 P1 闸门同一把尺子。

用法（务必脱离会话生命周期）：
    PYTHONPATH=src .venv/Scripts/python.exe -X utf8 \\
        scripts/compendium_rag_p3_max_edges_curve.py
产物：``data/compendium_rag/reports/p3_max_edges_curve.{json,md}``
      逐题中间产物 ``reports/p3_me/{tag}_me{档}.jsonl``（中断也留得下读数，可按 qid 续跑）
"""
from __future__ import annotations

import asyncio
import dataclasses
import hashlib
import importlib.util
import json
import os
import sys
import time
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

for _k, _v in {"CMPRAG_LEX_WEIGHT": "1.0", "CMPRAG_RRF_K": "1",
               "CMPRAG_LEX_FIRST": "0", "PYTHONHASHSEED": "0"}.items():
    os.environ.setdefault(_k, _v)      # 必须在 import config 之前

from compendium_rag import pipeline as P  # noqa: E402
from compendium_rag.config import get_settings  # noqa: E402
from compendium_rag.retriever import personalized_pagerank  # noqa: E402

EXPECTED_SHA = "7cac5867e8c80879"
R = ROOT / "data" / "compendium_rag" / "reports"
# 冒烟用：P3_CURVE_LIMIT=3 只跑每集前 3 题。冒烟的逐题产物落在**另一个目录**、
# 报告另起文件名——否则按 qid 续跑时 3 题会混进全量，冒充全量读数。
LIMIT = int(os.environ.get("P3_CURVE_LIMIT", "0"))
JSONL = R / ("p3_me_smoke" if LIMIT else "p3_me")
SUFFIX = "_smoke" if LIMIT else ""
SETS = {
    "300cn": ROOT / "data" / "knowledge" / "_audit" / "rag_testset_300_cn.json",
    "blind206": ROOT / "data" / "knowledge" / "_audit" / "blind_v1" / "questions_strict.json",
    "gen120": ROOT / "data" / "knowledge" / "_audit" / "rag_testset_gen_r1r2.json",
}
CAP = 10 ** 9                       # 「无上限」档
ARMS = [20, 30, 50, 80, CAP]
BASE = 30
HITF = "hit@k"


def _load_eval():
    spec = importlib.util.spec_from_file_location(
        "ev300", ROOT / "scripts" / "compendium_rag_eval300.py")
    mod = importlib.util.module_from_spec(spec)
    # 必须先注册再 exec：eval300 里有 @dataclass，dataclasses 会按
    # ``cls.__module__`` 回查 sys.modules，查不到就 AttributeError。
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


def sha16(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()[:16]


def run_arm(kb, ev, me: int, tag: str, cases) -> list[dict]:
    """一个档 × 一个集：逐题 append 到 jsonl，判分复用评测器；按 qid 续跑。"""
    kb.settings = dataclasses.replace(kb.settings, graph_max_edges=me)
    out = JSONL / f"{tag}_me{me}.jsonl"
    done: dict[str, dict] = {}
    if out.exists():
        for line in out.read_text(encoding="utf-8").splitlines():
            if line.strip():
                r = json.loads(line)
                done[r["qid"]] = r
    rows = [done[c.qid] for c in cases if c.qid in done]
    with out.open("a", encoding="utf-8") as fh:
        for i, c in enumerate(cases, 1):
            if c.qid in done:
                continue
            r = asyncio.run(ev.score_case(kb, c, 6, False))
            r["me"] = me
            r["answerable"] = bool(c.dims.get("_answerable"))
            rows.append(r)
            fh.write(json.dumps(r, ensure_ascii=False) + "\n")
            fh.flush()
            if i % 50 == 0:
                acc = sum(1 for x in rows if x["hit"]) / len(rows)
                print(f"  [{tag} me={me}] {i}/{len(cases)} hit={acc:.4f}",
                      flush=True)
    return rows


def uncapped_edge_order(retr, seeds, damping: float, max_iter: int):
    """复刻 `graph_channel` 的打分与排序（含同分按 `_edges` 原序的稳定序），
    返回**不截断**的边序，用于查「命中块所依边排在第几名」。"""
    seed_map = {s.eid: s.score for s in seeds}
    ppr = personalized_pagerank(retr._adj, seed_map, damping, max_iter)
    scored = []
    for e in retr._edges:
        sc = (ppr.get(e.src, 0.0) + ppr.get(e.dst, 0.0)) * max(0.1, e.confidence)
        if sc > 0:
            scored.append((sc, e))
    scored.sort(key=lambda kv: -kv[0])
    return scored


def flip_structure(retr, s, query: str, chunk_id: str) -> dict:
    seeds = retr.link(query, top_k=s.entity_link_top)
    seeds = [x for x in seeds if x.score >= s.seed_score_threshold] or seeds[:2]
    if not seeds:
        return {"status": "no_seeds"}
    scored = uncapped_edge_order(retr, seeds, s.ppr_damping, s.ppr_max_iter)
    for idx, (_sc, e) in enumerate(scored, 1):
        if chunk_id in e.chunk_ids:
            return {"status": "ok", "edge_rank": idx, "pool_n": len(scored),
                    "edge": f"{e.src}—{e.relation}→{e.dst}"}
    return {"status": "hit_chunk_not_carried_by_any_edge", "pool_n": len(scored)}


def main() -> int:
    s0 = get_settings()
    sha = sha16(s0.graph_path)
    if sha != EXPECTED_SHA:
        raise SystemExit(f"图指纹漂移：期望 {EXPECTED_SHA}，实际 {sha}，中止")
    JSONL.mkdir(parents=True, exist_ok=True)
    ev = _load_eval()
    kb = P.load_kb(s0)
    base_settings = kb.settings
    stats = kb.graph.stats()
    cases_by_set, blob = {}, "\n".join(c.text for c in kb.chunks)
    for tag, path in SETS.items():
        cs = ev.load_cases(path)
        if LIMIT:
            cs = cs[:LIMIT]
        for c in cs:
            c.dims["_answerable"] = any(k in blob for k in c.keywords)
        cases_by_set[tag] = cs
    print(f"graph={sha} 实体={stats['entities']} 边={stats['edges']} "
          f"题={sum(len(v) for v in cases_by_set.values())} 档={ARMS}", flush=True)

    per: dict[str, dict[int, dict]] = {}
    raw: dict[str, dict[int, list[dict]]] = {}
    for tag, cs in cases_by_set.items():
        for me in ARMS:
            t0 = time.time()
            rows = run_arm(kb, ev, me, tag, cs)
            raw.setdefault(tag, {})[me] = rows
            ans = [r for r in rows if r["answerable"]]
            per.setdefault(tag, {})[me] = {
                "all": ev.summarize(rows),
                "answerable": ev.summarize(ans),
                "n_edges_hist": {str(k): v for k, v in
                                 Counter(r["n_edges"] for r in rows).items()},
                "answerable_cases": len(ans),
                "seconds_total": round(time.time() - t0, 1),
            }
            a = per[tag][me]["answerable"]
            print(f"[{tag} me={me}] answerable n={a['cases']} "
                  f"hit={a[HITF]:.4f} MRR={a['MRR']:.4f} "
                  f"用时 {per[tag][me]['seconds_total']}s", flush=True)
    kb.settings = base_settings

    # ── 结构判据：30 档 miss、更高档 hit 的翻转题，命中块所依边排第几名 ──
    flips: list[dict] = []
    for tag, cs in cases_by_set.items():
        by_qid = {c.qid: c for c in cs}
        base_rows = {r["qid"]: r for r in raw[tag][BASE]}
        for me in ARMS:
            if me == BASE:
                continue
            for r in raw[tag][me]:
                b = base_rows.get(r["qid"])
                if not b or b["hit"] or not r["hit"]:
                    continue
                c = by_qid[r["qid"]]
                kb.settings = dataclasses.replace(base_settings, graph_max_edges=me)
                res_arm = asyncio.run(kb.retrieve(c.query, top_k=6, use_vector=False))
                kb.settings = dataclasses.replace(base_settings, graph_max_edges=BASE)
                res_base = asyncio.run(kb.retrieve(c.query, top_k=6, use_vector=False))
                base_ids = [e["chunk_id"] for e in res_base["evidence"][:6]]
                hit_cid, arm_rank = "", 0
                for rank, e in enumerate(res_arm["evidence"][:6], 1):
                    ch = kb.retriever.chunks.get(e["chunk_id"])
                    if not ch:
                        continue
                    bb = (f"{ch.text}\n{ch.chapter_title}\n"
                          f"{ch.scene_title}\n{ch.part_title}")
                    if any(k in bb for k in c.keywords) and e["chunk_id"] not in base_ids:
                        hit_cid, arm_rank = e["chunk_id"], rank
                        break
                kb.settings = base_settings
                struct = (flip_structure(kb.retriever, base_settings, c.query, hit_cid)
                          if hit_cid else {"status": "hit_chunk_was_already_in_base_top6"})
                struct.update({"arm_edge_limit": me, "hit_in_arm_rank": arm_rank})
                flips.append({"set": tag, "qid": c.qid, "me": me, "query": c.query,
                              "rr_base": b["rr"], "rr_arm": r["rr"],
                              "hit_chunk": hit_cid, **struct})
                print(f"  flip {tag}/{c.qid} me={me} "
                      f"rank={struct.get('edge_rank', struct.get('status'))}", flush=True)

    pool_by_set = {}
    for tag in SETS:
        hist = {int(k): v for k, v in per[tag][CAP]["n_edges_hist"].items()}
        vals = sorted(hist)
        n = sum(hist.values())
        pool_by_set[tag] = {
            "median": vals[len(vals) // 2], "max": vals[-1],
            "p90": vals[max(0, min(len(vals) - 1, int(n * 0.9)))],
            "share_pool_gt_30": round(sum(v for k, v in hist.items() if k > 30) / n, 4),
            "share_pool_gt_80": round(sum(v for k, v in hist.items() if k > 80) / n, 4),
        }
    structural = {
        "pool_n_by_set": pool_by_set,
        "flip_cases": len(flips),
        "flip_edge_rank_gt_30": sum(1 for f in flips if f.get("edge_rank", 0) > 30),
        "flip_edge_rank_le_30": sum(1 for f in flips if 0 < f.get("edge_rank", 0) <= 30),
        "flip_no_seeds": sum(1 for f in flips if f.get("status") == "no_seeds"),
        "flip_hit_chunk_not_edge_carried": sum(
            1 for f in flips
            if f.get("status") == "hit_chunk_not_carried_by_any_edge"),
        "flips": flips,
    }
    rep = {
        "done_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "graph_sha256_16": sha,
        "graph_stats": {k: stats.get(k) for k in ("entities", "edges", "chunks")},
        "caliber": {"mode": "graph_only", "use_vector": False, "top_k": 6,
                    "CMPRAG_LEX_WEIGHT": os.environ.get("CMPRAG_LEX_WEIGHT"),
                    "CMPRAG_RRF_K": os.environ.get("CMPRAG_RRF_K"),
                    "CMPRAG_LEX_FIRST": os.environ.get("CMPRAG_LEX_FIRST"),
                    "PYTHONHASHSEED": os.environ.get("PYTHONHASHSEED"),
                    "arms": ARMS, "baseline_arm": BASE,
                    "limit_per_set": LIMIT or None,
                    "judge": "scripts/compendium_rag_eval300.py::score_case/summarize"},
        "pre_registered_rule": "主判据是结构（翻转题命中块所依边在无上限边序里的名次），"
                               "读数只报告不选档；改默认值需 §4bis 冷启动重校准"
                               "且独立量（L2.3/confuse/双盲）不回退",
        "by_set_arm": per,
        "structural": structural,
    }
    (R / f"p3_max_edges_curve{SUFFIX}.json").write_text(
        json.dumps(rep, ensure_ascii=False, indent=2), encoding="utf-8")

    md = ["# v9-P3 · `graph_max_edges` 截断实测曲线"
          + ("（**冒烟样本，不是全量**）" if LIMIT else ""), "",
          f"- 图谱 `{sha}`，边 {stats['edges']}，实体 {stats['entities']}；口径 "
          f"`graph_only / use_vector=False / top_k=6`，融合 "
          f"`{rep['caliber']['CMPRAG_LEX_WEIGHT']}/"
          f"{rep['caliber']['CMPRAG_RRF_K']}/{rep['caliber']['CMPRAG_LEX_FIRST']}`",
          f"- 判据**先于跑数**登记：{rep['pre_registered_rule']}", "",
          "| 集 | 档 | answerable n | hit@6 | Δ vs 30 | MRR | Δ MRR | 全量 hit@6 | 用时 s |",
          "| --- | --- | --- | --- | --- | --- | --- | --- | --- |"]
    for tag in SETS:
        b = per[tag][BASE]["answerable"]
        for me in ARMS:
            a = per[tag][me]["answerable"]
            md.append(f"| {tag} | {me}{'（无上限）' if me == CAP else ''} "
                      f"| {a['cases']} | {a[HITF]:.4f} "
                      f"| {a[HITF] - b[HITF]:+.4f} | {a['MRR']:.4f} "
                      f"| {a['MRR'] - b['MRR']:+.4f} | "
                      f"{per[tag][me]['all'][HITF]:.4f} "
                      f"| {per[tag][me]['seconds_total']} |")
    md += ["", "## 结构判据（主判据）", "",
           "无上限档的边池 `pool_n`（每题分数>0 的边数分布）：",
           ""]
    for tag, v in pool_by_set.items():
        md.append(f"- `{tag}`：中位 {v['median']}、p90 {v['p90']}、最大 {v['max']}；"
                  f"池子 >30 的题占 {v['share_pool_gt_30']:.2%}，"
                  f">80 的占 {v['share_pool_gt_80']:.2%}")
    md += ["",
           f"- 30 档 miss、更高档 hit 的翻转题 **{structural['flip_cases']}** 题："
           f"命中块所依边在无上限边序里 **名次>30 的 "
           f"{structural['flip_edge_rank_gt_30']}**、名次≤30 的 "
           f"{structural['flip_edge_rank_le_30']}（≤30 说明翻转不是放宽截断带来的，"
           f"而是保留边相对次序变化的副作用）、零种子 {structural['flip_no_seeds']}、"
           f"块不由边携带 {structural['flip_hit_chunk_not_edge_carried']}",
           "", "## 读数怎么读（预先写死，不许事后改口）", "",
           "1. 「名次>30」占多数 → 30 确在切内容，可提案改默认值，但必须走 §4bis "
           "冷启动重校准 + 独立量不回退；",
           "2. 少数或样本太小 → 维持 30，completeness 0.2054 的缺口归到数据侧；",
           "3. 无论读数涨跌都**不构成改默认值的理由**，理由只能是第 1 条。",
           ""]
    if flips:
        md += ["## 翻转题逐条", "",
               "| 集 | qid | 档 | 命中块 | 所依边名次 | 池子 | 边 |",
               "| --- | --- | --- | --- | --- | --- | --- |"]
        for f in flips:
            md.append(f"| {f['set']} | {f['qid']} | {f['me']} | {f.get('hit_chunk') or '—'} "
                      f"| {f.get('edge_rank', f.get('status'))} | {f.get('pool_n', '—')} "
                      f"| {f.get('edge') or '—'} |")
        md.append("")
    md.append("> 只读脚本：不写图谱、不重建索引、不触 LLM/嵌入。逐题中间产物在 `p3_me/*.jsonl`。")
    md.append("")
    (R / f"p3_max_edges_curve{SUFFIX}.md").write_text("\n".join(md), encoding="utf-8")
    print(f"[done] p3_max_edges_curve{SUFFIX}.{{json,md}} 落盘；翻转题 "
          f"{structural['flip_cases']}，其中名次>30 的 "
          f"{structural['flip_edge_rank_gt_30']}", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
