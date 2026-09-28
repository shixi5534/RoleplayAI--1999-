# -*- coding: utf-8 -*-
"""P3 第二方案：**语料自举的同义桥**（corpus-derived synonym bridging）。

动机（为什么不用 RM3）：RM3 在 300cn 上 +1、盲测 −1（过拟合），已否决。
换一个**更保守**的查询侧供给：只在**桥接已证实有效**时才对查询做扩展。

方法（受限的查询扩展）：
  1. 先用**原查询**取词面 top-P（P=30）；
  2. 在 top-P 里找**语料级共现**反复出现的「查询词 ↔ 新词」对：
     若某词 g 在 top-P 的**多数**文档中共现，且不在原查询里，则视为该查询的
     语义扩展候选（这是"用检索到的相关性去补词"，但**不过度**）；
  3. 只把 top-K 个扩展词以**小权重**加入查询（保留原词权重 1.0）。

与 RM3 的差别：RM3 用**整个伪相关集的词分布**（易漂移）；
本方案只看**高频共现的少数词**，且权重受限 -> 更稳。

判据（预注册，与 RM3 相同）：
  - 300cn 选参；盲测留出；
  - 要求**盲测不下降**才可采纳（RM3 因盲测下降被否）。
"""
from __future__ import annotations

import argparse
import json
import math
import re
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from _p3_prf_rm3 import PrfLexIndex, grams, load_cases  # noqa: E402


def expand_terms(idx: PrfLexIndex, query: str, pool: int = 30,
                 min_df_frac: float = 0.5, top_k: int = 5):
    """返回 {term: weight}：原词权重 1.0 + 受限扩展词。"""
    q_toks = set(grams(query))
    base = {g: 1.0 for g in q_toks}
    docs = idx.bm25(base, top_k=pool)
    if not docs:
        return base
    id2i = {cid: i for i, cid in enumerate(idx.ids)}
    n_doc = len(docs)
    # 统计"出现在多少篇伪相关文档里"
    seen: Counter = Counter()
    for cid, _sc in docs:
        for g in set(idx.tf[id2i[cid]]):
            seen[g] += 1
    cands = [(g, c / n_doc) for g, c in seen.items()
             if g not in q_toks and c / n_doc >= min_df_frac and len(g) >= 2
             and not g.isdigit()]
    # 用 idf 排序（越特异越好），取 top_k
    cands.sort(key=lambda kv: (-idx._idf(kv[0]), kv[0]))
    out = dict(base)
    for g, _f in cands[:top_k]:
        out[g] = 0.35        # 受限权重：不压过原词
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--frac", default="0.4,0.5,0.6")
    ap.add_argument("--topk", default="3,5")
    ap.add_argument("--w", default="0.25,0.35")
    args = ap.parse_args()

    chunks = json.loads((ROOT / "data/compendium_rag/chunks.json").read_text(encoding="utf-8"))["chunks"]
    ids = [c["chunk_id"] for c in chunks]
    blob = {c["chunk_id"]: f"{c['text']}\n{c['chapter_title']}\n{c.get('scene_title','')}\n{c.get('part_title','')}"
            for c in chunks}
    print("[build] index …")
    idx = PrfLexIndex(ids, [blob[i] for i in ids])

    t300 = load_cases(ROOT / "data/knowledge/_audit/rag_testset_300_cn.json")
    ans = "\n".join(c["text"] for c in chunks)
    t300 = [c for c in t300 if any(k in ans for k in c["keywords"])]
    blind = load_cases(ROOT / "data/knowledge/_audit/blind_v1/questions_strict.json")
    blind = [c for c in blind if any(k in ans for k in c["keywords"])]

    def ev(cases, frac, topk, wt, pool=60):
        hit6, per = 0, {}
        for c in cases:
            terms = expand_terms(idx, c["q"], pool=30, min_df_frac=frac, top_k=topk) \
                if frac > 0 else {g: 1.0 for g in set(grams(c["q"]))}
            if wt != 0.35:      # 便于扫权重
                for g in list(terms):
                    if g not in set(grams(c["q"])):
                        terms[g] = wt
            ranked = idx.bm25(terms, top_k=pool)
            h = any(any(k in blob[cid] for k in c["keywords"]) for cid, _ in ranked[:6])
            hit6 += h
            per[c["qid"]] = h
        return hit6, len(cases), per

    print("\n=== 300cn（调参集）===")
    base_h, n, base = ev(t300, 0, 0, 0.35)
    print(f"  基线（无扩展）: {base_h}/{n} = {base_h/n:.4f}")
    best = None
    for frac in [float(x) for x in args.frac.split(",")]:
        for tk in [int(x) for x in args.topk.split(",")]:
            for wt in [float(x) for x in args.w.split(",")]:
                h, _n, per = ev(t300, frac, tk, wt)
                up = sum(1 for q in per if per[q] and not base[q])
                dn = sum(1 for q in base if base[q] and not per[q])
                if best is None or h > best[0]:
                    best = (h, frac, tk, wt)
                print(f"  frac={frac} K={tk} w={wt}: {h}/{n} = {h/n:.4f}  up={up} down={dn}")

    print(f"\n  最优: hit={best[0]} frac={best[1]} K={best[2]} w={best[3]}")
    print("\n=== 盲测 206（留出集）===")
    h0, n0, p0 = ev(blind, 0, 0, 0.35)
    h1, n1, p1 = ev(blind, best[1], best[2], best[3])
    up = sorted(q for q in p1 if p1[q] and not p0[q])
    dn = sorted(q for q in p0 if p0[q] and not p1[q])
    print(f"  无扩展: {h0}/{n0} = {h0/n0:.4f}")
    print(f"  有扩展: {h1}/{n1} = {h1/n1:.4f}")
    print(f"  up={len(up)} {up[:8]}  down={len(dn)} {dn[:8]}  Δ={(h1-h0)/n0*100:+.2f}pt")
    print("\n判定: " + ("盲测不降 -> 可采纳" if h1 >= h0 else "盲测下降 -> 否决"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
