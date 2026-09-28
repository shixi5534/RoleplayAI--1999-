# -*- coding: utf-8 -*-
"""P3 查询侧供给：**伪相关反馈（RM3）** 提升词面通道的深层 gold 排名。

问题定位（前几轮已实证）：
  - 14 道池内 miss 中 13 道的 gold **在词面通道里但排名 8–1214**；
  - RRF 是排名制 -> 深排名进不了 top-6；
  - 题干常「描述答案而不含其词」（语义鸿沟）。
  => 这正是**查询侧供给**的经典适用场景：用伪相关文档扩展查询词分布。

方法（RM3，标准 IR 技术）：
  1. BM25 取 top-N 伪相关文档；
  2. P(w|R) ∝ Σ_d tf(w,d)·score(d)（在伪相关集上）；
  3. P(w|q') = (1-λ)·P(w|q) + λ·P(w|R)，取 top-M 词；
  4. 用该加权词分布重新打分（BM25 逐词加权）。

纪律：
  - 参数（λ, N, M）**只在 300cn 上选**；
  - 盲测 206 题为**留出集**，选定后才评；
  - 判据：全量 hit@6 上升且 down 尽量 0。
"""
from __future__ import annotations

import argparse
import json
import math
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def grams(s: str) -> list[str]:
    s = (s or "").lower()
    toks = re.findall(r"[a-z0-9]+", s)
    zh = re.findall(r"[\u4e00-\u9fff]", s)
    toks += ["".join(zh[i:i + 2]) for i in range(len(zh) - 1)]
    return toks


class PrfLexIndex:
    def __init__(self, chunk_ids, texts, k1=1.2, b=0.6):
        self.ids = list(chunk_ids)
        self.k1, self.b = k1, b
        self.N = len(self.ids)
        self.tf: list[Counter] = []
        self.L: list[int] = []
        self.df: Counter = Counter()
        for t in texts:
            c = Counter(grams(t))
            self.tf.append(c)
            self.L.append(sum(c.values()) or 1)
            for g in c:
                self.df[g] += 1
        self.avg = sum(self.L) / self.N if self.N else 1.0

    def _idf(self, g: str) -> float:
        return math.log(1 + (self.N - self.df[g] + 0.5) / (self.df[g] + 0.5))

    def bm25(self, terms: dict[str, float], top_k: int = 30):
        out = []
        for i in range(self.N):
            d = self.tf[i]
            L = self.L[i]
            sc = 0.0
            for g, qw in terms.items():
                f = d.get(g, 0)
                if not f:
                    continue
                sc += qw * self._idf(g) * (f * (self.k1 + 1)) / (
                    f + self.k1 * (1 - self.b + self.b * L / self.avg))
            if sc > 0:
                out.append((self.ids[i], sc))
        out.sort(key=lambda kv: (-kv[1], kv[0]))
        return out[:top_k]

    def prf_terms(self, query: str, n_docs: int = 10, m_terms: int = 25,
                  lam: float = 0.5):
        """RM3：返回加权词分布 P(w|q')。"""
        q_toks = grams(query)
        q_tf = Counter(q_toks)
        q_tot = sum(q_tf.values()) or 1
        p_q = {g: c / q_tot for g, c in q_tf.items()}

        docs = self.bm25({g: 1.0 for g in p_q}, top_k=n_docs)
        if not docs:
            return {g: 1.0 for g in p_q}
        id2i = {cid: i for i, cid in enumerate(self.ids)}
        acc: Counter = Counter()
        for cid, sc in docs:
            i = id2i[cid]
            d = self.tf[i]
            tot = self.L[i] or 1
            for g, c in d.items():
                acc[g] += (c / tot) * sc
        z = sum(acc.values()) or 1.0
        p_r = {g: v / z for g, v in acc.items()}

        merged: dict[str, float] = {}
        for g, v in p_q.items():
            merged[g] = (1 - lam) * v
        for g, v in p_r.items():
            merged[g] = merged.get(g, 0.0) + lam * v
        top = sorted(merged.items(), key=lambda kv: (-kv[1], kv[0]))[:m_terms]
        # 归一化，便于作为 BM25 逐词权重
        mx = max((v for _, v in top), default=1.0) or 1.0
        return {g: v / mx for g, v in top}


def load_cases(p: Path):
    d = json.loads(p.read_text(encoding="utf-8"))
    out = []
    for r in (d if isinstance(d, list) else d.get("cases", [])):
        kws = []
        for g in (r.get("evidence") or []):
            if isinstance(g, str):
                kws.append(g)
            elif isinstance(g, (list, tuple)):
                kws.extend(str(x) for x in g if x)
        kws = [k.strip() for k in kws]
        kws = [k for i, k in enumerate(kws) if k and k not in kws[:i]]
        if kws:
            out.append({"qid": str(r.get("id", "")), "q": r.get("q", ""), "keywords": kws})
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--grid", default="0,0.3,0.5,0.7")
    ap.add_argument("--ndocs", default="10")
    ap.add_argument("--mterms", default="25")
    args = ap.parse_args()

    chunks = json.loads((ROOT / "data/compendium_rag/chunks.json").read_text(encoding="utf-8"))["chunks"]
    ids = [c["chunk_id"] for c in chunks]
    blob = {c["chunk_id"]: f"{c['text']}\n{c['chapter_title']}\n{c.get('scene_title','')}\n{c.get('part_title','')}"
            for c in chunks}
    print("[build] PRF index …")
    idx = PrfLexIndex(ids, [blob[i] for i in ids])

    def evaluate(cases, lam, ndocs, mterms, pool=60):
        hit6 = 0
        inpool = 0
        per = {}
        for c in cases:
            if lam <= 0:
                ranked = idx.bm25({g: 1.0 for g in set(grams(c["q"]))}, top_k=pool)
            else:
                terms = idx.prf_terms(c["q"], n_docs=ndocs, m_terms=mterms, lam=lam)
                ranked = idx.bm25(terms, top_k=pool)
            h = any(any(k in blob[cid] for k in c["keywords"]) for cid, _ in ranked[:6])
            p = any(any(k in blob[cid] for k in c["keywords"]) for cid, _ in ranked)
            hit6 += h
            inpool += p
            per[c["qid"]] = (h, p)
        n = len(cases)
        return hit6, inpool, n, per

    t300 = load_cases(ROOT / "data/knowledge/_audit/rag_testset_300_cn.json")
    ans = "\n".join(c["text"] for c in chunks)
    t300 = [c for c in t300 if any(k in ans for k in c["keywords"])]
    blind = load_cases(ROOT / "data/knowledge/_audit/blind_v1/questions_strict.json")
    blind = [c for c in blind if any(k in ans for k in c["keywords"])]
    print(f"[tset] 300cn n={len(t300)}  盲测 n={len(blind)}")

    print("\n=== 300cn（调参集）：lex 通道单独口径 ===")
    base = None
    best = None
    for lam in [float(x) for x in args.grid.split(",")]:
        for nd in [int(x) for x in args.ndocs.split(",")]:
            for mt in [int(x) for x in args.mterms.split(",")]:
                h, ip, n, per = evaluate(t300, lam, nd, mt)
                if base is None:
                    base = per
                up = sum(1 for q in per if per[q][0] and not base[q][0])
                dn = sum(1 for q in per if base[q][0] and not per[q][0])
                mark = ""
                if best is None or h > best[0]:
                    best = (h, lam, nd, mt)
                    mark = "  <- best"
                print(f"  lam={lam:<4} N={nd:<3} M={mt:<3} hit@6 {h}/{n} = {h/n:.4f} "
                      f"池 {ip}/{n}  up={up} down={dn}{mark}")

    print(f"\n  300cn 最优: hit={best[0]} lam={best[1]} N={best[2]} M={best[3]}")
    print("\n=== 盲测 206（留出集，用 300cn 选出的参数）===")
    h0, ip0, n0, per0 = evaluate(blind, 0.0, 0, 0)
    h1, ip1, n1, per1 = evaluate(blind, best[1], best[2], best[3])
    up = sorted(q for q in per1 if per1[q][0] and not per0[q][0])
    dn = sorted(q for q in per0 if per0[q][0] and not per1[q][0])
    print(f"  无 PRF : hit@6 {h0}/{n0} = {h0/n0:.4f}  池 {ip0}/{n0}")
    print(f"  PRF    : hit@6 {h1}/{n1} = {h1/n1:.4f}  池 {ip1}/{n1}")
    print(f"  up={len(up)} {up[:10]}  down={len(dn)} {dn[:10]}")
    print(f"  Δ = {(h1-h0)/n0*100:+.2f}pt")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
