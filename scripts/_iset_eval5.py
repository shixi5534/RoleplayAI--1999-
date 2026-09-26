# -*- coding: utf-8 -*-
"""题集 i · 阶段 3：五臂对照评测（预注册口径）。

五臂（同时跑）：
  empty   空映射（零档自检：q'=q）
  random  随机补名（从候选名随机取 1–3，固定 seed）
  alias   仅补已知实体别名（link 到的 seed 实体的其他 aliases）
  vector  向量候选补名（entity_index 向量最近名，纯嵌入、无图邻域）
  strong  强模型补名（盲识别子代理产出 entity_map_i.json）

统一打分器（同口径横切所有臂）：
  每题调 kb.retrieve(q', top_k=10) → 取有序 evidence，
  按 rank 派生 hit@6 / hit@10 / rr@10 / grounded。
  两种检索模式：full（use_vector=True）、graph_only（False）。

主口径：L1 = 全量 _pool==T1（非 miss 子集）。
闸门（计划书/用户预注册）：
  L1 全量 hit@10 ≥ 0.70；
  strong 相对 empty 提升 ≥ +5pt 且 McNemar p<0.05；
  strong 同时优于 empty 与 random；
  grounded = 1.000；
  报 up/down 具体题号。
"""
from __future__ import annotations

import argparse
import asyncio
import json
import math
import random
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

from compendium_rag import pipeline as P  # noqa: E402
from compendium_rag.config import get_settings  # noqa: E402
from compendium_rag.embedder import OllamaEmbedder  # noqa: E402

TESTSET = ROOT / "data" / "knowledge" / "_audit" / "rag_testset_i.json"
CANDS = ROOT / "data" / "compendium_rag" / "entity_candidates_i.json"
MAP_I = ROOT / "data" / "compendium_rag" / "entity_map_i.json"
ARMS = ("empty", "random", "alias", "vector", "strong")
RANDOM_SEED = 20260926
MAX_PICK = 3


def flatten(ev):
    out = []
    for grp in (ev or []):
        if isinstance(grp, str):
            out.append(grp)
        elif isinstance(grp, (list, tuple)):
            out.extend(str(x) for x in grp if x)
    seen, res = set(), []
    for k in out:
        k = k.strip()
        if k and k not in seen:
            seen.add(k); res.append(k)
    return res


def load_cases():
    d = json.loads(TESTSET.read_text(encoding="utf-8"))
    rows = d if isinstance(d, list) else d.get("cases", [])
    out = []
    for r in rows:
        kws = flatten(r.get("evidence"))
        if not kws:
            continue
        out.append({"qid": str(r.get("id", "")), "query": r.get("q", ""),
                    "keywords": kws, "gold_eid": r.get("_gold_eid"),
                    "pool": r.get("_pool", ""), "dims": r.get("dims") or {}})
    return out


def build_arm_maps(kb, cases, cands, arm):
    maps = {}
    g = kb.graph
    ret = kb.retriever
    if arm == "empty":
        return {c["qid"]: [] for c in cases}
    if arm == "strong":
        m = json.loads(MAP_I.read_text(encoding="utf-8"))["map"]
        return {c["qid"]: list(m.get(c["qid"], [])) for c in cases}
    if arm == "random":
        rng = random.Random(RANDOM_SEED)
        for c in cases:
            pool = cands.get(c["qid"], {}).get("candidates", [])
            k = min(len(pool), rng.randint(1, MAX_PICK)) if pool else 0
            maps[c["qid"]] = rng.sample(pool, k) if k else []
        return maps
    if arm == "alias":
        for c in cases:
            seen, picks = set(), []
            for s in ret.link(c["query"], top_k=6):
                ent = g.entities.get(s.eid)
                if not ent:
                    continue
                for a in ent.aliases:
                    if a and a not in seen and a not in c["query"]:
                        seen.add(a); picks.append(a)
                    if len(picks) >= MAX_PICK:
                        break
                if len(picks) >= MAX_PICK:
                    break
            maps[c["qid"]] = picks
        return maps
    raise ValueError(arm)


async def build_vector_map(kb, cases, top_n=MAX_PICK):
    """向量候选补名：对每题嵌入原始 query，取实体向量最近 top_n 名。"""
    s = kb.settings
    maps = {c["qid"]: [] for c in cases}
    if kb.entity_index is None:
        print("  [vector] 无实体向量索引，向量臂退化为空")
        return maps
    async with OllamaEmbedder(s.embed_base_url, s.embed_model,
                              s.embed_timeout) as emb:
        for c in cases:
            try:
                qvec = await emb.embed_one(c["query"])
            except Exception as exc:  # noqa: BLE001
                print(f"  [vector] {c['qid']} 嵌入失败: {exc}")
                continue
            hits = kb.entity_index.search(qvec, top_n)
            maps[c["qid"]] = [name for _eid, name, _sc in hits]
    return maps


async def score_arm(kb, cases, names_by_qid, use_vector):
    rows = []
    for c in cases:
        names = names_by_qid.get(c["qid"]) or []
        q = c["query"] + (" " + " ".join(names) if names else "")
        t0 = time.time()
        res = await kb.retrieve(q, top_k=10, use_vector=use_vector)
        ev = res.get("evidence", [])
        hit6 = hit10 = False
        rr = 0.0
        for rank, e in enumerate(ev[:10], start=1):
            ch = kb.retriever.chunks.get(e["chunk_id"])
            if not ch:
                continue
            blob = f"{ch.text}\n{ch.chapter_title}\n{ch.scene_title}\n{ch.part_title}"
            if any(k in blob for k in c["keywords"]):
                if rank <= 6:
                    hit6 = True
                hit10 = True
                if rr == 0.0:
                    rr = 1.0 / rank
                break
        grounded = all(e["chunk_id"] in kb.retriever.chunks for e in ev[:10])
        rows.append({"qid": c["qid"], "pool": c["pool"], "hit6": hit6,
                     "hit10": hit10, "rr": rr, "grounded": grounded,
                     "n_pick": len(names), "sec": round(time.time() - t0, 3)})
    return rows


def rate(rows, key):
    return round(sum(1 for r in rows if r[key]) / len(rows), 4) if rows else None


def mrr(rows):
    return round(sum(r["rr"] for r in rows) / len(rows), 4) if rows else None


def grp(rows, pool=None):
    sub = [r for r in rows if pool is None or r["pool"] == pool]
    return {"n": len(sub), "hit@6": rate(sub, "hit6"), "hit@10": rate(sub, "hit10"),
            "MRR": mrr(sub), "grounded": rate(sub, "grounded")}


def mcnemar(rows_a, rows_b, key):
    """配对精确二项检验（对称性）。rows keyed by qid."""
    ba = {r["qid"]: r[key] for r in rows_a}
    bb = {r["qid"]: r[key] for r in rows_b}
    b = sum(1 for q in ba if ba[q] and not bb.get(q))   # a hit, b miss
    c = sum(1 for q in ba if not ba[q] and bb.get(q))   # a miss, b hit
    n = b + c
    if n == 0:
        return {"b": b, "c": c, "p": 1.0}
    # 双侧精确符号检验 p = 2 * sum_{i<=min(b,c)} C(n,i) 0.5^n, capped 1
    m = min(b, c)
    tail = sum(math.comb(n, i) for i in range(m + 1)) * (0.5 ** n)
    p = min(1.0, 2 * tail)
    return {"b": b, "c": c, "p": round(p, 6)}


def flips(rows_a, rows_b, key):
    ba = {r["qid"]: r[key] for r in rows_a}
    bb = {r["qid"]: r[key] for r in rows_b}
    up = sorted(q for q in ba if ba[q] and not bb.get(q))
    down = sorted(q for q in ba if not ba[q] and bb.get(q))
    return up, down


async def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--arms", default=",".join(ARMS))
    ap.add_argument("--modes", default="full,graph_only")
    ap.add_argument("--out", default=str(ROOT / "data/compendium_rag/reports/eval5_set_i.json"))
    args = ap.parse_args()
    arms = [a for a in args.arms.split(",") if a]
    modes = [m for m in args.modes.split(",") if m]

    kb = P.load_kb(get_settings())
    cases = load_cases()
    cands = json.loads(CANDS.read_text(encoding="utf-8"))
    print(f"题集 i: {len(cases)} 题  arms={arms} modes={modes}", flush=True)

    # 预构建各臂补名映射一次（vector 只嵌一次 287 题），full/graph_only 复用
    nmaps: dict[str, dict] = {}
    for arm in arms:
        if arm == "vector":
            nmaps[arm] = await build_vector_map(kb, cases)
        else:
            nmaps[arm] = build_arm_maps(kb, cases, cands, arm)
        print(f"  [map:{arm:6s}] 非空题数={sum(1 for v in nmaps[arm].values() if v)}",
              flush=True)

    results = {a: {} for a in arms}
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)

    def dump(partial: bool):
        payload = {"testset": str(TESTSET.relative_to(ROOT)), "n_cases": len(cases),
                   "arms": arms, "modes": modes, "partial": partial,
                   "summary": {a: {m: {"L1_T1": grp(results[a][m], "T1"),
                                       "ALL": grp(results[a][m], None)}
                                   for m in results[a]} for a in arms if results[a]},
                               "rows": {a: results[a] for a in arms if results[a]}}
        if not partial and "strong" in results and "full" in results["strong"]:
            payload["gates"] = compute_gates(results, arms)
        Path(args.out).write_text(json.dumps(payload, ensure_ascii=False, indent=1),
                                  encoding="utf-8")

    # 模式外层：先跑完全部 full（主口径 + 闸门），再 graph_only 对照
    for mode in modes:
        uv = (mode == "full")
        for arm in arms:
            t0 = time.time()
            rows = await score_arm(kb, cases, nmaps[arm], uv)
            results[arm][mode] = rows
            g = grp(rows, "T1"); ga = grp(rows, None)
            print(f"  [{arm:6s}/{mode:10s}] L1(T1) n={g['n']} hit@10={g['hit@10']} "
                  f"hit@6={g['hit@6']} MRR={g['MRR']} grounded={g['grounded']}  "
                  f"ALL hit@10={ga['hit@10']}  ({time.time()-t0:.0f}s)", flush=True)
            dump(partial=True)

    # 汇总 + 闸门
    summary = {arm: {m: {"L1_T1": grp(results[arm][m], "T1"),
                         "ALL": grp(results[arm][m], None)} for m in modes}
               for arm in arms}
    print("\n== 分组（graph_only）==")
    for arm in arms:
        go = results[arm].get("graph_only")
        if go:
            print(f"  {arm:6s} graph_only L1={grp(go,'T1')}", flush=True)

    gates = compute_gates(results, arms)
    out = {"testset": str(TESTSET.relative_to(ROOT)), "n_cases": len(cases),
           "arms": arms, "modes": modes, "partial": False, "summary": summary,
           "gates": gates,
           "rows": {a: {m: results[a][m] for m in modes} for a in arms}}
    Path(args.out).write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    print("\n== 闸门 ==")
    print(json.dumps(gates, ensure_ascii=False, indent=1), flush=True)
    print(f"\n报告 → {args.out}")
    return 0


def compute_gates(results, arms):
    gates = {}
    t1 = lambda rows: [r for r in rows if r["pool"] == "T1"]  # 主口径 L1
    if "strong" in results and "full" in results["strong"]:
        strong = t1(results["strong"]["full"])
        sl1 = grp(strong, "T1")
        gates["caliber"] = "L1 = 全量 _pool==T1（hit@10 主指标）"
        gates["L1_hit10_ge_0.70"] = (sl1["hit@10"] or 0) >= 0.70
        if "empty" in results and "full" in results["empty"]:
            empty = t1(results["empty"]["full"])
            e = grp(empty, "T1")
            gates["strong_minus_empty_pt"] = round((sl1["hit@10"] - e["hit@10"]) * 100, 2)
            gates["gain_ge_5pt"] = gates["strong_minus_empty_pt"] >= 5
            gates["mcnemar_vs_empty"] = mcnemar(strong, empty, "hit10")
            up, down = flips(strong, empty, "hit10")
            gates["up_qids"] = up; gates["down_qids"] = down
        if "random" in results and "full" in results["random"]:
            rand = t1(results["random"]["full"])
            r = grp(rand, "T1")
            gates["strong_minus_random_pt"] = round((sl1["hit@10"] - r["hit@10"]) * 100, 2)
            gates["beats_random"] = sl1["hit@10"] > r["hit@10"]
            gates["mcnemar_vs_random"] = mcnemar(strong, rand, "hit10")
        gates["grounded_1"] = all((grp(results[a]["full"], "T1")["grounded"] or 0) >= 1.0
                                  for a in arms if "full" in results.get(a, {}))
    return gates


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
