# -*- coding: utf-8 -*-
"""把「词面通道」(BM25) 作为**第 4 个 RRF 通道**并入 **full** 生产路径（含向量）。

纪律（避免自证）：
  - 权重只在 **300cn** 上选；
  - 盲测 206 题为**留出集**，选定后才评（结果无论好坏都如实报）。

判据（预注册）：
  1. 300cn 上 bare hit@6 上升；
  2. 留出盲测集上 bare hit@6 上升（泛化）；
  3. down 题数尽量少；若盲测下降则否决该改动。
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
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

from compendium_rag import pipeline as P                      # noqa: E402
from compendium_rag.config import get_settings                # noqa: E402
from compendium_rag.retriever import RetrievalResult          # noqa: E402
from _r5_variant_scan import clear_ppr_cache, install_fast_ppr  # noqa: E402


def grams(s: str) -> list[str]:
    s = s.lower()
    toks = re.findall(r"[a-z0-9]+", s)
    zh = re.findall(r"[\u4e00-\u9fff]", s)
    toks += ["".join(zh[i:i + 2]) for i in range(len(zh) - 1)]
    return toks


class LexIndex:
    def __init__(self, chunks):
        self.N = len(chunks)
        self.df = Counter()
        self.tf = {}
        self.L = {}
        for c in chunks:
            t = Counter(grams(f"{c.text}\n{c.chapter_title}\n{c.scene_title}\n{c.part_title}"))
            self.tf[c.chunk_id] = t
            self.L[c.chunk_id] = sum(t.values()) or 1
            for g in set(t):
                self.df[g] += 1
        self.avg = sum(self.L.values()) / self.N

    def search(self, q: str, top_k: int = 30, k1=1.2, b=0.6):
        qt = grams(q)
        out = []
        for cid, d in self.tf.items():
            sc = 0.0
            L = self.L[cid]
            for g in qt:
                f = d.get(g, 0)
                if not f:
                    continue
                idf = math.log(1 + (self.N - self.df[g] + 0.5) / (self.df[g] + 0.5))
                sc += idf * (f * (k1 + 1)) / (f + k1 * (1 - b + b * L / self.avg))
            if sc > 0:
                out.append((cid, sc))
        out.sort(key=lambda kv: -kv[1])
        return out[:top_k]


def load_cases(p: Path):
    d = json.loads(p.read_text(encoding="utf-8"))
    rows = d if isinstance(d, list) else d.get("cases", [])
    out = []
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
            out.append({"qid": str(r.get("id", "")), "q": r.get("q", ""), "keywords": kws})
    return out


def retrieve(rets, query, qvec, top_k, lex, w_lex, lex_top, entity_vec_hits=None):
    """复刻 retrieve()（含向量），并并入 lex 通道。"""
    res = RetrievalResult(query=query)
    seeds = rets.link(query, top_k=6)
    if entity_vec_hits:
        seeds = rets.merge_vector_seeds(seeds, entity_vec_hits, 0.34, 6)
    seeds = [s for s in seeds if s.score >= 0.34] or seeds[:2]
    res.seeds = seeds
    channels = {"lex": dict(lex.search(query, lex_top))}
    if seeds:
        gc, edges = rets.graph_channel(seeds)
        res.edges = edges
        channels["graph"] = gc
        channels["mention"] = rets.mention_channel(seeds)
    if qvec is not None:
        channels["vector"] = rets.vector_channel(qvec, 30)
    evs = rets.rrf_fuse(channels, weights={"lex": w_lex}, top_n=max(top_k * 4, 24))
    res.evidence = evs
    return res


def evaluate(kb, cases, lex, w_lex, lex_top, qvecs, top_k=6, ent_hits=None):
    chunks = kb.retriever.chunks
    hits, rrs, perq = 0, 0.0, {}
    for c in cases:
        clear_ppr_cache()
        qv = qvecs.get(c["qid"]) if qvecs else None
        ev = (ent_hits or {}).get(c["qid"])
        res = retrieve(kb.retriever, c["q"], qv, top_k, lex, w_lex, lex_top, ev)
        rr, hit = 0.0, False
        for rank, e in enumerate(res.evidence[:top_k], start=1):
            ch = chunks.get(e.chunk_id)
            if not ch:
                continue
            blob = f"{ch.text}\n{ch.chapter_title}\n{ch.scene_title}\n{ch.part_title}"
            if any(k in blob for k in c["keywords"]):
                hit, rr = True, 1.0 / rank
                break
        hits += hit
        rrs += rr
        perq[c["qid"]] = (hit, rr)
    return hits, rrs, perq


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--weights", default="0,0.5,1.0,1.5,2.0")
    ap.add_argument("--lex-top", type=int, default=30)
    args = ap.parse_args()

    s = get_settings()
    kb = P.load_kb(s)
    print("[build] lex index …")
    lex = LexIndex(kb.chunks)
    install_fast_ppr()

    # 300cn（调参集）——用其采集文件的 qvecs 复现向量通道
    c300 = json.loads((ROOT / "data/compendium_rag/reports/rank_collect_r5_top30.json")
                      .read_text(encoding="utf-8"))
    qv300 = c300.get("qvecs") or {}
    cases300 = load_cases(ROOT / "data/knowledge/_audit/rag_testset_300_cn.json")
    ans300 = "\n".join(c.text for c in kb.chunks)
    cases300 = [c for c in cases300 if any(k in ans300 for k in c["keywords"])]

    best = None
    print("\n=== 300cn（调参集）===")
    res300 = {}
    for w in [float(x) for x in args.weights.split(",")]:
        h, m, perq = evaluate(kb, cases300, lex, w, args.lex_top, qv300)
        n = len(cases300)
        res300[w] = {"hit": h, "n": n, "perq": perq}
        print(f"  w_lex={w:<4} hit@6 {h}/{n} = {h / n:.4f}  MRR {m / n:.4f}")
        if best is None or h > best[1] or (h == best[1] and m > best[2]):
            best = (w, h, m)
    print(f"  -> 300cn 最优 w_lex = {best[0]}  (hit={best[1]})")

    # 盲测（留出集）
    cblind = json.loads((ROOT / "data/compendium_rag/reports/rank_collect_blindfinal_top30.json")
                        .read_text(encoding="utf-8"))
    qvb = cblind.get("qvecs") or {}
    casesb = load_cases(ROOT / "data/knowledge/_audit/blind_v1/questions_strict.json")
    print("\n=== 盲测 206（**留出集**，仅在 300cn 选权重后评）===")
    outb = {}
    for w in (0.0, best[0]):
        h, m, perq = evaluate(kb, casesb, lex, w, args.lex_top, qvb)
        n = len(casesb)
        outb[w] = {"hit": h, "n": n, "perq": perq}
        tag = "（现状）" if w == 0.0 else "（采用 300cn 选出的权重）"
        print(f"  w_lex={w:<4} hit@6 {h}/{n} = {h / n:.4f}  MRR {m / n:.4f} {tag}")

    base = outb[0.0]
    new = outb[best[0]]
    up = [q for q in base["perq"] if not base["perq"][q][0] and new["perq"][q][0]]
    dn = [q for q in base["perq"] if base["perq"][q][0] and not new["perq"][q][0]]
    print(f"\n  [留出集泛化] up={len(up)} down={len(dn)}")
    print(f"  up 样例: {sorted(up)[:12]}")
    print(f"  down 样例: {sorted(dn)[:12]}")
    delta = (new["hit"] - base["hit"]) / base["n"] * 100
    print(f"  Δhit@6 = {delta:+.2f}pt -> {'泛化成立' if delta > 0 else '不成立（否决）'}")

    p = ROOT / "data/compendium_rag/reports/_lex_channel_full_scan.json"
    p.write_text(json.dumps({
        "selected_on_300cn": {"w_lex": best[0], "hit": best[1], "n": best[2]},
        "holdout_blind": {str(w): {"hit": v["hit"], "n": v["n"]} for w, v in outb.items()},
        "holdout_delta_pt": round(delta, 2),
        "holdout_up": sorted(up), "holdout_down": sorted(dn),
    }, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\n-> {p}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
