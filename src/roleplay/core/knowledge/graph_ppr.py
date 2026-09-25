"""个性化 PageRank（PPR）——GraphRAG 展开激活的共享实现。

被 lore 层（``graph_search``）与剧情层（``plot_graph``）共用，避免两套算法漂移。

设计（吸收 HippoRAG 2 的思路）：以链接命中的实体为种子集合、边权
``confidence × importance`` 为转移权重做无向化传播，多跳关联自然浮到前排；
迭代至收敛或达到 max_iter。纯 Python，数百至数千条边时毫秒级。
"""
from __future__ import annotations

# 证据条数 < 2 的边视为「孤证」（抽取噪声风险高），默认不参与传播。
WEAK_EVIDENCE_MIN = 2

# 无向化邻接表：{节点: [(邻居, 边权)]} + {节点: 加权度}
Adjacency = tuple[dict[str, list[tuple[str, float]]], dict[str, float]]


def parse_exempt_sources(raw: object) -> frozenset[str]:
    """把配置值解析为「豁免弱证过滤」的 source 集合（逗号分隔；空/None -> 空集）。

    为什么是配置而不是硬编码：人工事实边在不同时期由不同脚本写入，实测图内同时存在
    ``manual``（apply_manual_edges.py 的规范标记）与 ``manual_probe``（早期探针写入）。
    写死一个值会让另一类人工边被弱证过滤**静默清掉**——而 R8 红线要求「手工边零丢失」，
    静默丢失正是这条红线要防的事。故做成可配置集合，默认仍是 Spec 锁定的 ``"manual"``。
    """
    if raw is None:
        return frozenset()
    if isinstance(raw, str):
        parts = [p.strip() for p in raw.split(",")]
    elif isinstance(raw, (set, frozenset, list, tuple)):
        parts = [str(p).strip() for p in raw]
    else:
        parts = [str(raw).strip()]
    return frozenset(p for p in parts if p)


def _is_exempt(edge: dict, exempt_sources: frozenset[str] | None) -> bool:
    """该边是否豁免「孤证」过滤（只看 source，不看 confidence —— 见 filter_edges 注）。"""
    if not exempt_sources:
        return False
    return str(edge.get("source") or "") in exempt_sources


def filter_edges(
    edges: list[dict],
    *,
    min_confidence: float = 0.0,
    include_weak: bool = True,
    exempt_sources: frozenset[str] | None = None,
) -> list[dict]:
    """按检索口径过滤边：``confidence >= min_confidence`` 且（``include_weak`` 或证据数达标）。

    与 :func:`build_adjacency` / :func:`hop_distance` 共用同一份判断——旧实现把这套
    条件在三个地方各写了一遍（PPR、hop、retrieve 边循环），任何一处改动都可能造成
    「邻接里有、边表里没有」的口径漂移。这里收敛成唯一来源。

    **P0-1（C4）新增 ``exempt_sources``**：``source`` 命中该集合的边**不受
    ``WEAK_EVIDENCE_MIN`` 约束**。依据：人工事实边（``manual``）天然只有 1 条证据——
    它是人写的、可溯源的，不是抽取噪声；旧口径会把它们与「孤证噪声」一视同仁地丢掉，
    造成图谱重建后手工事实静默消失（R8 红线）。**注意豁免只作用于弱证判据**：
    ``min_confidence`` 仍然照常生效（人工边也要给出置信度，不能豁免成"无条件进图"）。

    注：本函数**不含** ``confidence × importance > 0`` 的权重判断（旧 retrieve 的边循环
    同样不判它）；零权边由 :func:`build_adjacency` 在构建邻接时另行丢弃。
    """
    out: list[dict] = []
    for e in edges:
        if float(e.get("confidence", 0.0)) < min_confidence:
            continue
        if not include_weak and len(e.get("evidence") or []) < WEAK_EVIDENCE_MIN:
            if not _is_exempt(e, exempt_sources):
                continue
        out.append(e)
    return out


def build_adjacency(
    edges: list[dict],
    *,
    min_confidence: float = 0.0,
    include_weak: bool = True,
    exempt_sources: frozenset[str] | None = None,
) -> Adjacency:
    """把边表无向化为 ``(邻接表, 加权度)``（PPR 与 hop 共用的过滤口径）。

    单独抽出来是为了让调用方（剧情图谱检索）能按 store 版本**缓存**过滤结果——
    旧实现每次检索都要重扫全部边并重建邻接表（实测 5719 边 × 每查询 3 次）。
    过滤语义与 ``personalized_pagerank`` 内联版本逐条一致。

    ``exempt_sources`` 见 :func:`filter_edges`。**缓存键必须包含它**：调用方按
    (revision, min_confidence, include_weak, exempt_sources) 缓存，否则改配置后仍读旧邻接。
    """
    adj: dict[str, list[tuple[str, float]]] = {}
    deg: dict[str, float] = {}
    for e in filter_edges(
        edges, min_confidence=min_confidence, include_weak=include_weak,
        exempt_sources=exempt_sources,
    ):
        w = float(e.get("confidence", 0.0)) * float(e.get("importance", 0.7))
        if w <= 0:
            continue
        s, d = str(e.get("src")), str(e.get("dst"))
        if not s or not d:
            continue
        adj.setdefault(s, []).append((d, w))
        adj.setdefault(d, []).append((s, w))  # 无向化：关系是对称的语义关联
        deg[s] = deg.get(s, 0.0) + w
        deg[d] = deg.get(d, 0.0) + w
    for n in adj:
        deg[n] = deg.get(n, 0.0) or 1.0
    return adj, deg


def personalized_pagerank(
    edges: list[dict],
    seeds: dict[str, float],
    *,
    min_confidence: float = 0.0,
    include_weak: bool = True,
    damping: float = 0.85,
    max_iter: int = 50,
    tol: float = 1e-6,
    adjacency: Adjacency | None = None,
    seed_weights: dict[str, float] | None = None,
    exempt_sources: frozenset[str] | None = None,
) -> dict[str, float]:
    """返回 ``{node: ppr_score}``。

    - ``edges``：``[{src, dst, confidence, importance, evidence}]``；
    - ``seeds``：``{node: weight}``，权重无需归一（内部按总和归一）；
    - 边过滤：``confidence >= min_confidence``；``include_weak=False`` 时丢弃
      evidence 少于 ``WEAK_EVIDENCE_MIN`` 的边（``source`` 命中 ``exempt_sources``
      的人工边豁免此条，见 :func:`filter_edges`）；
    - ``adjacency``：可选的预建邻接表（见 :func:`build_adjacency`）。**提供时不再过滤
      ``edges``**，调用方须保证它已按同一口径过滤（剧情图谱检索按 store 版本缓存它，
      缓存键须含 ``exempt_sources``）；
    - ``seed_weights``（P0-4/D1，默认 ``None``）：``{node: specificity}``，在**归一化之前**
      逐乘到种子上。用于压制高频泛种子（如「洞穴」「海盗」）对传播质量的稀释；
      未列出的种子乘数按 1.0 处理。``None`` 时不做任何加权；
    - 无可用边 / 无种子时原样返回 ``seeds``（调用方据此判断图谱路是否可用）。

    **回归契约**：``seed_weights=None`` 且 ``exempt_sources=None`` 时，输出与改造前逐位一致
    （由 ``tests/test_plotrag_p0.py`` 用全量真实边表做差分锁定）。
    """
    if not edges or not seeds:
        return dict(seeds)
    if adjacency is not None:
        adj, deg = adjacency
        nodes: set[str] = set(adj)
    else:
        adj, deg = build_adjacency(
            edges, min_confidence=min_confidence, include_weak=include_weak,
            exempt_sources=exempt_sources,
        )
        nodes = set(adj)
    if not nodes:
        return dict(seeds)

    # D1：种子在归一化前逐乘 specificity（未列出的按 1.0）。None 时完全跳过——保证逐位一致。
    if seed_weights:
        seeds = {n: w * float(seed_weights.get(n, 1.0)) for n, w in seeds.items()}

    total = sum(seeds.values()) or 1.0
    r: dict[str, float] = {n: (seeds.get(n, 0.0) / total) for n in nodes}
    for n, w in seeds.items():
        if n not in r:
            r[n] = w / total
            nodes.add(n)
    seed_vec = {n: (seeds.get(n, 0.0) / total) for n in r}
    # 热路径微优化（2026-09-20，compendium 入库后图谱 7.6k→23.3k 边、检索 p95 破 500ms 护栏）：
    # 把 `dict.get` 绑定到局部变量，省掉每次调用的属性查找。实测本层 dict.get 占
    # 单次 PPR 的 ~57%（cProfile：9.66M 次 / 6 次调用）。
    # **语义逐位不变**：查表次数、顺序、算式与旧写法完全一致，仅去掉属性查找开销
    # （P0 回归契约要求 seed_weights=None 时输出与改造前一致）。
    deg_get = deg.get
    adj_get = adj.get
    for _ in range(max(1, max_iter)):
        new: dict[str, float] = {}
        new_get = new.get
        delta = 0.0
        # 内层热循环：`.items()` 免一次查表、`adj_get(u, ())` 免建空列表、
        # `damping*share` 提到邻居循环外——算式与结果与旧写法逐位一致（仅是少做重复工作）。
        for u, ru in r.items():
            d = damping * (ru / deg_get(u, 1.0))
            if d <= 0:
                continue
            for v, w in adj_get(u, ()):
                new[v] = new_get(v, 0.0) + d * w
        seed_get = seed_vec.get
        new_get = new.get
        for n, rn in r.items():
            val = (1 - damping) * seed_get(n, 0.0) + new_get(n, 0.0)
            new[n] = val
            delta += val - rn if val >= rn else rn - val
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
    adjacency: dict[str, list[str]] | None = None,
    exempt_sources: frozenset[str] | None = None,
) -> dict[str, int]:
    """从种子做 BFS 得到节点跳距（约束证据边离种子不过远）。

    过滤口径必须与 ``personalized_pagerank`` 一致，否则会出现
    「有跳距但零 PPR 分」的节点，令筛选逻辑难以解释。
    ``adjacency`` 提供时不再过滤 ``edges``（同 PPR，由调用方保证口径一致）。
    """
    if adjacency is None:
        adj: dict[str, list[str]] = {}
        for e in filter_edges(
            edges, min_confidence=min_confidence, include_weak=include_weak,
            exempt_sources=exempt_sources,
        ):
            s, d = str(e.get("src")), str(e.get("dst"))
            if not s or not d:
                continue
            adj.setdefault(s, []).append(d)
            adj.setdefault(d, []).append(s)
    else:
        adj = adjacency
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
