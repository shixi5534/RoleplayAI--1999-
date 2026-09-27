# -*- coding: utf-8 -*-
"""实验：把「词面通道」(BM25-like) 作为**第 4 个 RRF 通道**并入检索。

动机：14 道池内 miss 中，有 3 道（R018 rank1 / R231 rank3 / R251 rank3）的 gold
块在纯词面通道里是**可达且靠前**的，而现有三通道（graph/mention/vector）全部漏掉。
词面通道不依赖实体链接（可救种子为空的题），也不依赖嵌入。

设计（严格对齐现有架构）：
  - 与 graph/mention 通道并列，参与同一个 rrf_fuse（k=60）
  - 权重可调（默认 1.0）
  - **只增候选**：不改变 graph/mention 通道自身排序

判据（预注册）：
  - 主判据：bare hit@6 上升且无回归（down=0 优先）
  - 副判据：hit@30（池上限）上升 -> 重排天花板抬高
  - 若 hit@30 不升且 hit@6 下降 -> 放弃
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
from _r5_variant_scan import clear_ppr_cache, install_fast_ppr, load_cases  # noqa: E402


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


def retrieve_lex(retr, query, top_k, lex, w_lex, lex_top, weights=None):
    res = RetrievalResult(query=query)
    seeds = retr.link(query, top_k=6)
    seeds = [s for s in seeds if s.score >= 0.34] or seeds[:2]
    res.seeds = seeds
    channels = {"lex": dict(lex.search(query, lex_top))}
    if seeds:
        gc, edges = retr.graph_channel(seeds)
        res.edges = edges
        channels["graph"] = gc
        channels["mention"] = retr.mention_channel(seeds)
    evs = retr.rrf_fuse(channels, weights={"lex": w_lex}, top_n=max(top_k * 4, 24))
    res.evidence = evs
    return res


def eval_with(retr_or_none, cases, chunks, blob, lex, w_lex, lex_top, top_k=6,
              base_retr=None, use_base_channels=True):
    hits, rrs, perq = 0, 0.0, {}
    for c in cases:
        clear_ppr_cache()
        if use_base_channels:
            res = retrieve_lex(base_retr, c["q"], top_k, lex, w_lex, lex_top)
        else:
            res = lex_only(lex, c["q"], top_k)
        rr, hit = 0.0, False
        for rank, ev in enumerate(res.evidence[:top_k], start=1):
            ch = chunks.get(ev.chunk_id)
            if not ch:
                continue
            bl = blob[ev.chunk_id]
            if any(k in bl for k in c["keywords"]):
                hit, rr = True, 1.0 / rank
                break
        hits += hit
        rrs += rr
        perq[c["qid"]] = (hit, rr)
    return hits, rrs, perq


def lex_only(lex, q, top_k):
    res = RetrievalResult(query=q)
    from compendium_rag.retriever import Evidence
    res.evidence = [Evidence(chunk_id=cid, score=sc) for cid, sc in lex.search(q, top_k)]
    return res


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--weights", default="0,0.5,1.0,2.0")
    ap.add_argument("--lex-top", type=int, default=30)
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--set", default=str(ROOT / "data/knowledge/_audit/rag_testset_300_cn.json"))
    args = ap.parse_args()

    s = get_settings()
    kb = P.load_kb(s)
    chunks = {c.chunk_id: c for c in kb.chunks}
    blob = {cid: f"{c.text}\n{c.chapter_title}\n{c.scene_title}\n{c.part_title}"
            for cid, c in chunks.items()}
    cases = load_cases(Path(args.set))
    ans = "\n".join(c.text for c in kb.chunks)
    cases = [c for c in cases if any(k in ans for k in c["keywords"])]
    if args.limit:
        cases = cases[:args.limit]
    print(f"[tset] {Path(args.set).name} answerable n={len(cases)} lex_top={args.lex_top}")

    print("[build] lex index …")
    lex = LexIndex(kb.chunks)
    install_fast_ppr()

    results = {}
    for w in [float(x) for x in args.weights.split(",")]:
        h, m, perq = eval_with(None, cases, chunks, blob, lex, w, args.lex_top,
                               base_retr=kb.retriever, use_base_channels=True)
        n = len(cases)
        results[w] = {"hit": h, "n": n, "rate": h / n, "mrr": m / n, "perq": perq}
        print(f"[w_lex={w:<4}] hit@6 {h}/{n} = {h / n:.4f}  MRR {m / n:.4f}")

    b = results[0.0] if 0.0 in results else results[min(results)]
    print("\n=== vs w=0（现有三通道）逐题翻题 ===")
    for w, r in results.items():
        if w == 0.0:
            continue
        up = [q for q in b["perq"] if not b["perq"][q][0] and r["perq"][q][0]]
        dn = [q for q in b["perq"] if b["perq"][q][0] and not r["perq"][q][0]]
        print(f"[w={w:<4}] up={len(up)} {up[:8]}  down={len(dn)} {dn[:8]}")

    # 池上限：lex-only 能否救回 miss（仅 300cn 口径有意义）
    MISS = ["R005", "R012", "R018", "R094", "R127", "R170", "R171",
            "R231", "R244", "R248", "R251", "R273", "R297", "R298"]
    miss_cases = [c for c in cases if c["qid"] in MISS]
    reach = []
    if miss_cases:
        print(f"\n=== {len(miss_cases)} 道池内 miss 在纯词面通道 top-30 的可达性 ===")
        for c in miss_cases:
            top = lex.search(c["q"], 30)
            got = [cid for cid, _ in top if any(k in blob[cid] for k in c["keywords"])]
            if got:
                reach.append(c["qid"])
        print(f"  可达: {len(reach)}/{len(miss_cases)} -> {reach}")

    out = ROOT / "data/compendium_rag/reports/_lex_channel_scan.json"
    out.write_text(json.dumps({str(k): {kk: vv for kk, vv in v.items() if kk != "perq"}
                               for k, v in results.items()} | {"miss_reachable": reach},
                              ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\n-> {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
