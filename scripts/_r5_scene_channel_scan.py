# -*- coding: utf-8 -*-
"""R5 备选设计评估：把「同场」作为**独立 RRF 通道**，而非注入 PPR 的边。

动机（来自 _r5_variant_scan 的实测）：
  把同场边注入 PPR 的代价是 +43%~123% 边数，收益却只有 +1 题（R009），
  且 chain 变体出现 MRR 下降（0.5328→0.5271）—— 正是作战书预判的 **PPR 稀释**：
  PPR 转移用 w/wsum 归一，给高枢纽（维尔汀度 1524→5103）加边会摊薄其既有邻居。

独立通道设计不需要改图（零 dilution）：
  同场证据直接从 `chunk2chars` 取 —— 若某 chunk 内共现了「本轮已命中的种子实体」
  ≥2 个，则该 chunk 获得一个分数，作为独立通道参与 RRF。
  这样只**增加候选**，不改变既有任何通道的排序。

对比：
  A) base（现有三通道）
  B) scene 通道，不同权重 w
  C) 对照：把同场边注入 PPR（等价先前 star 变体）——用于确认"通道法"确实避开稀释
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from compendium_rag import pipeline as P                    # noqa: E402
from compendium_rag.config import get_settings              # noqa: E402
from compendium_rag.retriever import GraphRetriever, Evidence  # noqa: E402
from _r5_variant_scan import (                              # noqa: E402
    clear_ppr_cache, install_fast_ppr, load_cases, build_variant)


def scene_channel(seed_eids: set[str], chunk2chars: dict[str, set[str]],
                  top_n: int = 30) -> dict[str, float]:
    """同场通道：chunk 内与种子实体共现的角色数越多，分越高。

    只用**本轮种子**判定共现，因此是"查询条件化"的，不会给无关 chunk 加分。
    """
    out: dict[str, float] = {}
    for cid, chars in chunk2chars.items():
        j = len(chars & seed_eids)
        if j >= 2:
            # 共现数归一：2 个共现 = 0.5，越多越高但饱和
            out[cid] = j / (j + 1.0)
    if not out:
        return {}
    top = sorted(out.items(), key=lambda kv: -kv[1])[:top_n]
    return dict(top)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--set", default=str(ROOT / "data/knowledge/_audit/rag_testset_300_cn.json"))
    ap.add_argument("--top-k", type=int, default=6)
    ap.add_argument("--weights", default="0,0.5,1.0,2.0")
    ap.add_argument("--limit", type=int, default=0)
    args = ap.parse_args()

    s = get_settings()
    kb = P.load_kb(s)
    chunks = {c.chunk_id: c for c in kb.chunks}

    # 角色 -> chunk 共现表
    chunk2chars: dict[str, set[str]] = defaultdict(set)
    for eid, e in kb.graph.entities.items():
        if e.type == "角色":
            for cid in e.chunk_ids:
                chunk2chars[cid].add(eid)
    print(f"[load] entities={len(kb.graph.entities)} edges={len(kb.graph.edges)} "
          f"chunk2chars={len(chunk2chars)}")

    cases = load_cases(Path(args.set))
    blob = "\n".join(c.text for c in kb.chunks)
    cases = [c for c in cases if any(k in blob for k in c["keywords"])]
    if args.limit:
        cases = cases[:args.limit]
    print(f"[tset] answerable n={len(cases)}")

    install_fast_ppr()
    base_retr = GraphRetriever(kb.graph, kb.chunks)

    def evaluate(w: float):
        hits, rrs, perq = 0, 0.0, {}
        for c in cases:
            clear_ppr_cache()
            if w <= 0:
                res = base_retr.retrieve(c["q"], None, top_k=args.top_k)
            else:
                res = run_with_scene(base_retr, c["q"], args.top_k, w, chunk2chars)
            rr, hit = 0.0, False
            for rank, ev in enumerate(res.evidence[:args.top_k], start=1):
                ch = chunks.get(ev.chunk_id)
                if not ch:
                    continue
                b = f"{ch.text}\n{ch.chapter_title}\n{ch.scene_title}\n{ch.part_title}"
                if any(k in b for k in c["keywords"]):
                    hit, rr = True, 1.0 / rank
                    break
            hits += hit
            rrs += rr
            perq[c["qid"]] = (hit, rr)
        return hits, rrs, perq

    results = {}
    for w in [float(x) for x in args.weights.split(",")]:
        t = time.time()
        h, m, perq = evaluate(w)
        n = len(cases)
        results[w] = {"hit": h, "n": n, "rate": h / n, "mrr": m / n, "perq": perq}
        print(f"[w={w:<4}] hit@6 {h}/{n} = {h / n:.4f}  MRR {m / n:.4f}  ({time.time() - t:.0f}s)")

    print()
    print("=== vs w=0（现有通道）逐题翻题 ===")
    b0 = results[0.0] if 0.0 in results else results[min(results)]
    for w, r in results.items():
        if w == 0.0:
            continue
        up = [q for q in b0["perq"] if not b0["perq"][q][0] and r["perq"][q][0]]
        dn = [q for q in b0["perq"] if b0["perq"][q][0] and not r["perq"][q][0]]
        print(f"[w={w:<4}] up={len(up)} {up[:8]}  down={len(dn)} {dn[:8]}")

    out = ROOT / "data/compendium_rag/reports/_r5_scene_channel_scan.json"
    out.write_text(json.dumps({str(k): {kk: vv for kk, vv in v.items() if kk != "perq"}
                               for k, v in results.items()}, ensure_ascii=False, indent=2),
                   encoding="utf-8")
    print(f"\n-> {out}")
    return 0


def run_with_scene(retr: GraphRetriever, query: str, top_k: int, w: float,
                   chunk2chars):
    """复刻 retriever.retrieve()（qvec=None 路径），额外并入 scene 通道。

    与原实现的唯一差异：channels 字典多一项 "scene"，并给 RRF 传 weights。
    其余（种子过滤、graph/mention 通道、RRF top_n、ppr 回填）逐行保持一致。
    """
    from compendium_rag.retriever import RetrievalResult

    res = RetrievalResult(query=query)
    seeds = retr.link(query, top_k=6)
    seeds = [s for s in seeds if s.score >= 0.34] or seeds[:2]
    res.seeds = seeds
    if not seeds:
        res.graph_ok = False
        res.note = "实体链接零命中，图谱通道为空"
        return res

    g_chunks, edges = retr.graph_channel(seeds, damping=0.85, max_iter=50)
    res.edges = edges
    channels = {
        "graph": g_chunks,
        "mention": retr.mention_channel(seeds),
        "scene": scene_channel({s.eid for s in seeds}, chunk2chars),
    }
    evs = retr.rrf_fuse(channels, weights={"scene": w},
                        top_n=max(top_k * 4, 24))
    ppr_map, _ = retr.graph_channel(seeds)
    for e in evs:
        e.ppr = ppr_map.get(e.chunk_id, 0.0)
    res.evidence = evs
    return res


if __name__ == "__main__":
    raise SystemExit(main())
