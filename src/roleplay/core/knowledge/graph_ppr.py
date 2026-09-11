"""个性化 PageRank（PPR）——GraphRAG 展开激活的共享实现。

被 lore 层（``graph_search``）与剧情层（``plot_graph``）共用，避免两套算法漂移。

设计（吸收 HippoRAG 2 的思路）：以链接命中的实体为种子集合、边权
``confidence × importance`` 为转移权重做无向化传播，多跳关联自然浮到前排；
迭代至收敛或达到 max_iter。纯 Python，数百至数千条边时毫秒级。
"""
from __future__ import annotations

# 证据条数 < 2 的边视为「孤证」（抽取噪声风险高），默认不参与传播。
WEAK_EVIDENCE_MIN = 2


def personalized_pagerank(
    edges: list[dict],
    seeds: dict[str, float],
    *,
    min_confidence: float = 0.0,
    include_weak: bool = True,
    damping: float = 0.85,
    max_iter: int = 50,
    tol: float = 1e-6,
) -> dict[str, float]:
    """返回 ``{node: ppr_score}``。

    - ``edges``：``[{src, dst, confidence, importance, evidence}]``；
    - ``seeds``：``{node: weight}``，权重无需归一（内部按总和归一）；
    - 边过滤：``confidence >= min_confidence``；``include_weak=False`` 时丢弃
      evidence 少于 ``WEAK_EVIDENCE_MIN`` 的边；
    - 无可用边 / 无种子时原样返回 ``seeds``（调用方据此判断图谱路是否可用）。
    """
    if not edges or not seeds:
        return dict(seeds)
    nodes: set[str] = set()
    adj: dict[str, list[tuple[str, float]]] = {}
    for e in edges:
        if float(e.get("confidence", 0.0)) < min_confidence:
            continue
        if not include_weak and len(e.get("evidence") or []) < WEAK_EVIDENCE_MIN:
            continue
        w = float(e.get("confidence", 0.0)) * float(e.get("importance", 0.7))
        if w <= 0:
            continue
        s, d = str(e.get("src")), str(e.get("dst"))
        if not s or not d:
            continue
        nodes.update((s, d))
        adj.setdefault(s, []).append((d, w))
        adj.setdefault(d, []).append((s, w))  # 无向化：关系是对称的语义关联
    if not nodes:
        return dict(seeds)

    deg = {n: sum(w for _, w in adj.get(n, [])) or 1.0 for n in nodes}
    total = sum(seeds.values()) or 1.0
    r: dict[str, float] = {n: (seeds.get(n, 0.0) / total) for n in nodes}
    for n, w in seeds.items():
        if n not in r:
            r[n] = w / total
            nodes.add(n)
    seed_vec = {n: (seeds.get(n, 0.0) / total) for n in r}
    for _ in range(max(1, max_iter)):
        new: dict[str, float] = {}
        delta = 0.0
        for u in r:
            share = r[u] / deg.get(u, 1.0)
            if share <= 0:
                continue
            for v, w in adj.get(u, []):
                new[v] = new.get(v, 0.0) + damping * share * w
        for n in r:
            new[n] = (1 - damping) * seed_vec.get(n, 0.0) + new.get(n, 0.0)
            delta += abs(new[n] - r[n])
        r = new
        if delta < tol:
            break
    return r


def hop_distance(
    edges: list[dict],
    seeds: set[str],
    max_hops: int,
    *,
    min_confidence: float = 0.0,
    include_weak: bool = True,
) -> dict[str, int]:
    """从种子做 BFS 得到节点跳距（约束证据边离种子不过远）。

    过滤口径必须与 ``personalized_pagerank`` 一致，否则会出现
    「有跳距但零 PPR 分」的节点，令筛选逻辑难以解释。
    """
    adj: dict[str, list[str]] = {}
    for e in edges:
        if float(e.get("confidence", 0.0)) < min_confidence:
            continue
        if not include_weak and len(e.get("evidence") or []) < WEAK_EVIDENCE_MIN:
            continue
        s, d = str(e.get("src")), str(e.get("dst"))
        if not s or not d:
            continue
        adj.setdefault(s, []).append(d)
        adj.setdefault(d, []).append(s)
    dist: dict[str, int] = {s: 0 for s in seeds}
    frontier = list(seeds)
    hop = 0
    while frontier and hop < max_hops:
        hop += 1
        nxt: list[str] = []
        for u in frontier:
            for v in adj.get(u, []):
                if v not in dist:
                    dist[v] = hop
                    nxt.append(v)
        frontier = nxt
    return dist
