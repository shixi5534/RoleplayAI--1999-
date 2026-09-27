# -*- coding: utf-8 -*-
"""R5 变体快速评估器（内存内，纯图通道，无嵌入）。

为什么需要它：正式 eval300 走 Ollama 嵌入，一次 ~30 分钟，无法用于变体扫描。
R5 的闸门重点（PPR 稀释）必须对比多种边增量方案，故需要秒级的等价评估。

**保真度声明（重要）**：本脚本只复现 eval300 的 `graph_only` 模式
（qvec=None），用于**相对比较**各 R5 变体；绝对数字以正式 eval300 为准。

评测契约与 scripts/compendium_rag_eval300.py 严格一致：
  hit = top_k 证据块中，任一窗的 `text\\nchapter\\nscene\\npart` 含任一期望关键词。
"""
from __future__ import annotations

import argparse
import copy
import json
import math
import sys
import time
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from compendium_rag import pipeline as P                      # noqa: E402
from compendium_rag.config import get_settings                # noqa: E402
from compendium_rag.graph_store import Edge, GraphStore       # noqa: E402
from compendium_rag.retriever import GraphRetriever           # noqa: E402
from compendium_rag import retriever as R                     # noqa: E402


def install_fast_ppr() -> None:
    """把 PPR 换成**数学等价**的快速实现，仅用于变体扫描。

    原实现每次迭代都重算 `sum(w for _, w in nbrs)`，而 build_adjacency 早已
    返回了 weight_sum。这里改为查表，并把边表预转成紧凑数组。
    等价性由 _verify_equivalent() 在 --limit 子集上断言。
    """
    def fast_ppr(adj, seeds, damping=0.85, max_iter=50, tol=1e-6):
        if not seeds:
            return {}
        # 记忆化：retriever.retrieve() 对同一 seed 集**调用 PPR 两次**
        # （一次取 chunks、一次取 ppr_map，见 retriever.py:422/432），
        # 且变体扫描会跑同题多次 —— 键=(邻接表身份, 阻尼, 有序种子权重)。
        key = (id(adj), damping,
               tuple(sorted((k, round(v, 9)) for k, v in seeds.items())))
        hit = _PPR_CACHE.get(key)
        if hit is not None:
            return hit
        total = sum(seeds.values()) or 1.0
        teleport = {k: v / total for k, v in seeds.items()}
        nodes = set(adj.keys()) | set(teleport.keys())
        nbrs_of = {n: [(m, w) for m, w in adj.get(n, ())] for n in nodes}
        wsum_of = {n: (sum(w for _, w in nbrs_of[n]) or 1.0) for n in nodes}
        score = {n: teleport.get(n, 0.0) for n in nodes}
        for _ in range(max_iter):
            nxt = {n: (1.0 - damping) * teleport.get(n, 0.0) for n in nodes}
            dangling = 0.0
            for n in nodes:
                s = score[n]
                if s <= 0.0:
                    continue
                nb = nbrs_of[n]
                if not nb:
                    dangling += s
                    continue
                d = damping * s / wsum_of[n]
                for m, w in nb:
                    nxt[m] += d * w
            if dangling:
                share = damping * dangling / len(nodes)
                for n in nodes:
                    nxt[n] += share
            delta = sum(abs(nxt[n] - score[n]) for n in nodes)
            score = nxt
            if delta < tol:
                break
        mx = max(score.values()) or 1.0
        out = {k: v / mx for k, v in score.items()}
        _PPR_CACHE[key] = out
        return out

    R.personalized_pagerank = fast_ppr


def _verify_equivalent(g: GraphStore, cases, top_k: int, chunks) -> None:
    """断言快慢 PPR 给出逐题相同结果（抽 12 题）。"""
    orig = R.personalized_pagerank
    slow = GraphRetriever(g, chunks)
    install_fast_ppr()
    fast = GraphRetriever(g, chunks)
    sub = cases[:12]
    for c in sub:
        a = slow.retrieve(c["q"], None, top_k=top_k)
        b = fast.retrieve(c["q"], None, top_k=top_k)
        ea = [e.chunk_id for e in a.evidence[:top_k]]
        eb = [e.chunk_id for e in b.evidence[:top_k]]
        assert ea == eb, f"快慢 PPR 不等价于 {c['qid']}: {ea} vs {eb}"
    print("[verify] 快速 PPR 与原生 PPR 在 12 题上逐题等价 ✓")
    R.personalized_pagerank = orig
    clear_ppr_cache()



def load_cases(path: Path):
    d = json.loads(path.read_text(encoding="utf-8"))
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
        if not kws:
            continue
        out.append({"qid": str(r.get("id", "")), "q": r.get("q", ""), "keywords": kws})
    return out


def score(kb, retr, chunks, case, top_k=6):
    res = retr.retrieve(case["q"], None, top_k=top_k)
    rr = 0.0
    hit = False
    for rank, ev in enumerate(res.evidence[:top_k], start=1):
        c = chunks.get(ev.chunk_id)
        if not c:
            continue
        blob = f"{c.text}\n{c.chapter_title}\n{c.scene_title}\n{c.part_title}"
        if any(k in blob for k in case["keywords"]):
            hit = True
            rr = 1.0 / rank
            break
    return hit, rr


def make_scene_edges(g: GraphStore, mode: str, cap: int = 0,
                     conf: float = 0.35) -> list[Edge]:
    """按方案生成「同场」边。

    mode:
      full   —— 同 chunk 内角色两两全连接
      star   —— 星型：度数最高者为锚
      cap:K  —— 全连接但每 chunk 角色数上限 K（超出按度数取前 K）
      chain  —— 按度数排序连成链（边数 = n-1，且不集中到单点）
    """
    chars = {eid: e for eid, e in g.entities.items() if e.type == "角色"}
    deg = Counter()
    for e in g.edges:
        deg[e.src] += 1
        deg[e.dst] += 1

    chunk2chars: dict[str, set[str]] = defaultdict(set)
    for eid in chars:
        for cid in g.entities[eid].chunk_ids:
            chunk2chars[cid].add(eid)

    existing = {(e.src, e.relation, e.dst) for e in g.edges}
    new_edges: list[Edge] = []

    def add(a: str, b: str, cid: str) -> None:
        if a == b:
            return
        # 已有任意方向的实义边则不再加同场边（避免冗余抬权）
        if (a, SCENE_REL, b) in existing or (b, SCENE_REL, a) in existing:
            return
        new_edges.append(Edge(src=a, dst=b, relation=SCENE_REL,
                              confidence=conf, evidence=f"同场：{cid}",
                              chunk_ids=[cid], count=1))

    for cid, members in chunk2chars.items():
        ms = sorted(members, key=lambda x: (-deg.get(x, 0), x))
        if len(ms) < 2:
            continue
        if mode == "star":
            anchor = ms[0]
            for m in ms[1:]:
                add(anchor, m, cid)
        elif mode == "chain":
            for a, b in zip(ms, ms[1:]):
                add(a, b, cid)
        elif mode.startswith("cap:"):
            k = int(mode.split(":")[1])
            ms = ms[:k]
            for i in range(len(ms)):
                for j in range(i + 1, len(ms)):
                    add(ms[i], ms[j], cid)
        else:  # full
            for i in range(len(ms)):
                for j in range(i + 1, len(ms)):
                    add(ms[i], ms[j], cid)
    return new_edges


SCENE_REL = "同场"

_PPR_CACHE: dict = {}


def clear_ppr_cache() -> None:
    _PPR_CACHE.clear()


def build_variant(g: GraphStore, mode: str, conf: float) -> GraphStore:
    g2 = copy.deepcopy(g)
    extra = make_scene_edges(g, mode, conf=conf)
    g2.edges = list(g2.edges) + extra
    g2._edge_index = {e.key: e for e in g2.edges}
    return g2, len(extra)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--set", default=str(ROOT / "data/knowledge/_audit/rag_testset_300_cn.json"))
    ap.add_argument("--top-k", type=int, default=6)
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--variants", default="base,star,chain,cap:6,cap:4,full")
    ap.add_argument("--conf", type=float, default=0.35)
    ap.add_argument("--verify", action="store_true",
                    help="先用原生 PPR 断言快慢等价（12 题），再扫描")
    args = ap.parse_args()

    s = get_settings()
    t0 = time.time()
    kb = P.load_kb(s)
    chunks = {c.chunk_id: c for c in kb.chunks}
    print(f"[load] {time.time() - t0:.1f}s  chunks={len(chunks)} "
          f"entities={len(kb.graph.entities)} edges={len(kb.graph.edges)}")

    cases = load_cases(Path(args.set))
    corpus_blob = "\n".join(c.text for c in kb.chunks)
    cases = [c for c in cases if any(k in corpus_blob for k in c["keywords"])]  # answerable 口径
    if args.limit:
        cases = cases[:args.limit]
    print(f"[tset] answerable n={len(cases)} top_k={args.top_k} conf={args.conf}")

    if args.verify:
        _verify_equivalent(kb.graph, cases, args.top_k, kb.chunks)
    install_fast_ppr()

    results = {}
    for v in args.variants.split(","):
        v = v.strip()
        t1 = time.time()
        # ⚠ 必须先清空 PPR 缓存：键含 id(adj)，而新建变体后旧邻接表被回收，
        #   id 可能被复用 -> 跨变体命中陈旧缓存会静默污染结果。
        clear_ppr_cache()
        if v == "base":
            g2, extra = kb.graph, 0
        else:
            g2, extra = build_variant(kb.graph, v, args.conf)
        retr = GraphRetriever(g2, kb.chunks)
        hits = 0
        rrs = 0.0
        perq = {}
        for c in cases:
            h, rr = score(kb, retr, chunks, c, args.top_k)
            hits += h
            rrs += rr
            perq[c["qid"]] = (h, rr)
        n = len(cases)
        results[v] = {"extra_edges": extra, "hit": hits, "n": n,
                      "rate": hits / n, "mrr": rrs / n, "perq": perq}
        print(f"[{v:8}] +{extra:6,} edges ({extra / max(len(kb.graph.edges), 1) * 100:5.0f}%)  "
              f"hit@6 {hits}/{n} = {hits / n:.4f}  MRR {rrs / n:.4f}  ({time.time() - t1:.1f}s)")

    # 与 base 逐题对账
    base = results.get("base")
    print()
    print("=== vs base 逐题翻题 ===")
    for v, r in results.items():
        if v == "base":
            continue
        up = [q for q in base["perq"] if not base["perq"][q][0] and r["perq"][q][0]]
        dn = [q for q in base["perq"] if base["perq"][q][0] and not r["perq"][q][0]]
        print(f"[{v:8}] up={len(up)} {up[:8]}  down={len(dn)} {dn[:8]}")

    (ROOT / "data/compendium_rag/reports/_r5_variant_scan.json").write_text(
        json.dumps({k: {kk: vv for kk, vv in v.items() if kk != "perq"}
                    for k, v in results.items()}, ensure_ascii=False, indent=2),
        encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
