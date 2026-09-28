# -*- coding: utf-8 -*-
"""关键发现深挖：**词面通道单独 0.9320 > 融合 0.8301（盲测 206）**。

为什么会这样（机理）：
  RRF 给每个通道的前 1 名都是同样的 1/(60+1)。
  当 graph/mention/vector 把**大量**候选排到各自前列（它们各自的前 6 都在 top-6 里拿高分），
  融合后的 top-6 会被这些通道"分票"，把词面通道真正命中的块挤出前 6。
  实测权重扫描（1→16）无法解决（各档均 ≤ 融合现状）。

本脚本测试**不靠权重**的三种结构性改法（均在 300cn 选，盲测留出）：
  M1 **lex 优先闸门**：若 lex top-1 与 top-2 分差显著（>τ），直接采用 lex 序；
     否则回落到融合序（保守：只在"词面很确定"时才覆盖）。
  M2 **两段式**：取融合序与 lex 序的**并集**，先 lex 前 L，再补融合其余。
  M3 **lex 主导 + 融合兜底**：lex 前 L 占位，其余位置用融合序补足（去重）。

判据：300cn 选参；盲测**不降**才可采纳。
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

from compendium_rag import pipeline as P                       # noqa: E402
from compendium_rag.config import get_settings                 # noqa: E402
from compendium_rag.retriever import RetrievalResult           # noqa: E402
from _r5_variant_scan import clear_ppr_cache, install_fast_ppr  # noqa: E402
from _lex_channel_full import LexIndex, load_cases             # noqa: E402


def channels_for(rets, query, qvec):
    seeds = rets.link(query, top_k=6)
    seeds = [s for s in seeds if s.score >= 0.34] or seeds[:2]
    ch = {}
    if seeds:
        gc, _ = rets.graph_channel(seeds)
        ch["graph"] = gc
        ch["mention"] = rets.mention_channel(seeds)
    if qvec is not None:
        ch["vector"] = rets.vector_channel(qvec, 30)
    return ch, seeds


def ranked_ids(scored: dict, n: int):
    return [cid for cid, _ in sorted(scored.items(), key=lambda kv: (-kv[1], kv[0]))][:n]


def build(lex_scored: dict, fused_order: list, mode: str, param, top_n=24):
    """返回候选 chunk_id 列表（按最终次序）。fused_order 已是有序 chunk_id 列表。"""
    lex_order = ranked_ids(lex_scored, top_n)
    if mode == "fused":
        return fused_order
    if mode == "lexonly":
        return lex_order
    if mode == "m1_gate":
        vals = [v for _, v in sorted(lex_scored.items(), key=lambda kv: -kv[1])][:2]
        ratio = ((vals[0] - vals[1]) / vals[0]) if (len(vals) == 2 and vals[0] > 0) else 1.0
        return lex_order if ratio >= param else fused_order
    if mode == "m2_union":
        L = int(param)
        out, seen = [], set()
        for cid in lex_order[:L] + fused_order:
            if cid not in seen:
                seen.add(cid)
                out.append(cid)
        return out
    if mode == "m3_lexfirst":
        L = int(param)
        out, seen = [], set()
        for cid in lex_order[:L]:
            if cid not in seen:
                seen.add(cid)
                out.append(cid)
        for cid in fused_order:
            if cid not in seen:
                seen.add(cid)
                out.append(cid)
        return out
    raise ValueError(mode)


def collect_case(kb, lex, c, qvec, top_n=24):
    """每题只算**一次**通道（通道与最终决策规则无关）—— 避免按 config 重算。"""
    clear_ppr_cache()
    lex_scored = dict(lex.search(c["q"], 30))
    ch, _seeds = channels_for(kb.retriever, c["q"], qvec)
    ch["lex"] = lex_scored
    fused = kb.retriever.rrf_fuse(ch, weights={"lex": 1.0}, top_n=top_n)
    chunks = kb.retriever.chunks
    blobs = {}
    for cid in set(list(lex_scored) + [e.chunk_id for e in fused]):
        ck = chunks.get(cid)
        blobs[cid] = (f"{ck.text}\n{ck.chapter_title}\n{ck.scene_title}\n{ck.part_title}"
                      if ck else "")
    return {"lex_scored": lex_scored,
            "fused_order": [e.chunk_id for e in fused],
            "blobs": blobs,
            "kws": c["keywords"],
            "qid": c["qid"]}


def hit_for(cached, config, top_k=6):
    ids = build(cached["lex_scored"], cached["fused_order"], *config, top_n=24)
    blobs, kws = cached["blobs"], cached["kws"]
    for cid in ids[:top_k]:
        b = blobs.get(cid)
        if b and any(k in b for k in kws):
            return True
    return False


def ev_cached(caches, config, top_k=6):
    per = {c["qid"]: hit_for(c, config, top_k) for c in caches}
    return sum(per.values()), len(per), per


def ev(kb, lex, cases, qvecs, config, top_k=6):
    caches = [collect_case(kb, lex, c, qvecs.get(c["qid"])) for c in cases]
    return ev_cached(caches, config, top_k)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=0)
    args = ap.parse_args()

    s = get_settings()
    kb = P.load_kb(s)
    print("[build] lex index …")
    lex = LexIndex(kb.chunks)
    install_fast_ppr()

    q300 = (json.loads((ROOT / "data/compendium_rag/reports/rank_collect_v6c300_top30.json")
                       .read_text(encoding="utf-8")).get("qvecs") or {})
    qb = (json.loads((ROOT / "data/compendium_rag/reports/rank_collect_v6cblind_top30.json")
                     .read_text(encoding="utf-8")).get("qvecs") or {})
    ans = "\n".join(c.text for c in kb.chunks)
    c300 = [c for c in load_cases(ROOT / "data/knowledge/_audit/rag_testset_300_cn.json")
            if any(k in ans for k in c["keywords"])]
    blind = [c for c in load_cases(ROOT / "data/knowledge/_audit/blind_v1/questions_strict.json")
             if any(k in ans for k in c["keywords"])]
    if args.limit:
        c300, blind = c300[:args.limit], blind[:args.limit]
    print(f"[tset] 300cn n={len(c300)}  盲测 n={len(blind)}")

    cfgs = ([("fused", 0)] + [("lexonly", 0)]
            + [("m1_gate", t) for t in (0.05, 0.15, 0.3)]
            + [("m2_union", L) for L in (3, 6, 9)]
            + [("m3_lexfirst", L) for L in (3, 6, 9)])

    t0 = __import__("time").time()
    print("\n[collect] 每题只算一次通道（消除按 config 重算）…")
    cache300 = [collect_case(kb, lex, c, q300.get(c["qid"])) for c in c300]
    print(f"  done {__import__('time').time()-t0:.0f}s")
    print("\n=== 300cn（调参集）===")
    scored = []
    for cfg in cfgs:
        h, n, per = ev_cached(cache300, cfg)
        scored.append((h, cfg, per))
        print(f"  {str(cfg):26} {h}/{n} = {h/n:.4f}")
    scored.sort(key=lambda x: (-x[0], str(x[1])))
    best_h, best_cfg, _ = scored[0]
    print(f"\n  300cn 最优: {best_cfg} hit={best_h}")

    print("\n[collect] 盲测通道…")
    cacheb = [collect_case(kb, lex, c, qb.get(c["qid"])) for c in blind]
    print("\n=== 盲测 206（留出集）===")
    show = [("fused", 0), ("lexonly", 0), best_cfg]
    for cfg in cfgs:
        if cfg not in show:
            show.append(cfg)
    for cfg in show:
        h, n, per = ev_cached(cacheb, cfg)
        star = "  <- 300cn 选出" if cfg == best_cfg else ""
        print(f"  {str(cfg):26} {h}/{n} = {h/n:.4f}{star}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
