# -*- coding: utf-8 -*-
"""目标① 落地测试：**放宽池 (top_n=60) + 冻结重排** 能否把新进池的 6 道救进 top-6？

依据（scripts/_p3_pool_widen.py）：
  放宽 RRF 池到 60 后，6 道此前完全不可达的 gold 进入池（排名 34–51），
  全量池覆盖 0.9184 -> 0.9643。但 RRF 是排名制，排名 34–51 者仍进不了 top-6；
  需靠**打分制重排器**（其 cos/lex 特征可把语义强相关候选顶上来）。

判据（预注册）：
  - 全量 hit@6 **不低于**现状（163~164/196），且 down 尽量 0；
  - 6 道新进池题中至少救回若干；
  - 若全量下降超过 1 题则否决。

注：本脚本用 lab 的特征构造器 + v6 冻结权重，模拟真实重排路径。
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

from compendium_rag import pipeline as P                      # noqa: E402
from compendium_rag.config import get_settings                # noqa: E402

spec = importlib.util.spec_from_file_location("lab", ROOT / "scripts/_rank_rerank_lab.py")
lab = importlib.util.module_from_spec(spec)
spec.loader.exec_module(lab)

from _lex_channel_full import LexIndex, load_cases            # noqa: E402
from _r5_variant_scan import clear_ppr_cache, install_fast_ppr  # noqa: E402

NEW6 = ["R180", "R244", "R248", "R273", "R292", "R298"]
MISS = ["R001", "R005", "R012", "R094", "R127", "R170", "R171",
        "R180", "R244", "R248", "R273", "R292", "R297", "R298"]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--collect", default=str(ROOT / "data/compendium_rag/reports/rank_collect_v6c300_top30.json"))
    ap.add_argument("--pool", type=int, default=60)
    args = ap.parse_args()

    s = get_settings()
    kb = P.load_kb(s)
    print("[build] lex index …")
    lex = LexIndex(kb.chunks)
    install_fast_ppr()
    qvecs = (json.loads(Path(args.collect).read_text(encoding="utf-8")).get("qvecs") or {})
    cases = load_cases(ROOT / "data/knowledge/_audit/rag_testset_300_cn.json")
    ans = "\n".join(c.text for c in kb.chunks)
    cases = [c for c in cases if any(k in ans for k in c["keywords"])]

    # v6 冻结重排权重
    prod = json.loads((ROOT / "data/compendium_rag/reports/rank_rerank_lab_300cn_v6.json")
                      .read_text(encoding="utf-8"))["chosen"]
    feats = lab.BASE_FEATURES
    w = np.array([float(prod["weights"].get(f, 0.0)) for f in feats])
    a = float(prod["params"]["a"])
    fb = lab.FeatureBuilder(kb)
    print(f"[frozen] {prod['policy']} a={a}")

    pool = args.pool
    ev_pool, gold, qids, kws = [], [], [], []
    for c in cases:
        clear_ppr_cache()
        seeds = kb.retriever.link(c["q"], top_k=6)
        seeds = [x for x in seeds if x.score >= 0.34] or seeds[:2]
        channels = {"lex": dict(lex.search(c["q"], 30))}
        if seeds:
            gc, _ = kb.retriever.graph_channel(seeds)
            channels["graph"] = gc
            channels["mention"] = kb.retriever.mention_channel(seeds)
        qv = qvecs.get(c["qid"])
        if qv is not None:
            channels["vector"] = kb.retriever.vector_channel(qv, 50)
        evs = kb.retriever.rrf_fuse(channels, weights={"lex": 1.0}, top_n=pool)
        ids = [e.chunk_id for e in evs]
        if len(ids) < pool:
            # 池不足 pool 时补足（用末尾重复会污染；改为跳过该题）
            ids = ids + [None] * (pool - len(ids))  # type: ignore
        ev_pool.append(ids)
        qids.append(c["qid"])
        kws.append(c["keywords"])
        gold.append(None)

    # 构造 Z（盲特征）与 G（金标）
    Zs, Gs = [], []
    for c, ids in zip(cases, ev_pool):
        qv = qvecs.get(c["qid"])
        evlist = [{"chunk_id": cid} for cid in ids if cid]
        if len(evlist) < pool:
            evlist += [{"chunk_id": ids[-1]}] * (pool - len(evlist))
        Z1, _dt = fb.question(c["q"], qv, evlist, kb.retriever.link)
        Zs.append(Z1)
        row = []
        for e in evlist:
            ch = kb.retriever.chunks.get(e["chunk_id"])
            b = (f"{ch.text}\n{ch.chapter_title}\n{ch.scene_title}\n{ch.part_title}"
                 if ch else "")
            row.append(any(k in b for k in c["keywords"]))
        Gs.append(row)
    Z = np.stack(Zs)
    G = np.array(Gs, dtype=bool)

    base_perm = np.tile(np.arange(pool), (len(cases), 1))
    S = Z @ w
    perm = lab.apply_policy(prod["policy"], a, S, pool)

    def score(perm_):
        out = {}
        hit6, _h10, _r6, _r10 = lab.eval_perm(perm_, G, pool)
        for i, q in enumerate(qids):
            out[q] = bool(hit6[i])
        return out

    b = score(base_perm)
    n = score(perm)
    hb = sum(1 for q in qids if b[q])
    hn = sum(1 for q in qids if n[q])
    up = sorted(q for q in qids if n[q] and not b[q])
    dn = sorted(q for q in qids if b[q] and not n[q])
    print(f"\n=== 放宽池 top_n={pool} 后（RRF 序 vs 冻结重排）===")
    print(f"  RRF 基线 hit@6   = {hb}/{len(qids)} = {hb/len(qids):.4f}")
    print(f"  冻结重排 hit@6   = {hn}/{len(qids)} = {hn/len(qids):.4f}")
    print(f"  up={len(up)} {up[:10]}")
    print(f"  down={len(dn)} {dn[:10]}")
    print(f"\n  6 道新进池题命中: RRF={sum(1 for q in NEW6 if b[q])}/6  "
          f"重排={sum(1 for q in NEW6 if n[q])}/6")
    print(f"  14 道 miss 命中: RRF={sum(1 for q in MISS if b[q])}/14  "
          f"重排={sum(1 for q in MISS if n[q])}/14")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
