# -*- coding: utf-8 -*-
"""检索测试：实体链接、PPR、三通道融合、证据收集、上下文渲染。

全部离线：向量通道用构造的假索引，不调用 Ollama。
"""
from __future__ import annotations

import numpy as np
import pytest

from compendium_rag.chunker import Chunk
from compendium_rag.corpus import Turn
from compendium_rag.extract import ExtractedEntity, ExtractedRelation, Extraction
from compendium_rag.graph_store import GraphStore
from compendium_rag.retriever import (ChunkIndex, EntityVectorIndex, Evidence,
                                      FALLBACK_MARK, GraphRetriever,
                                      build_adjacency, default_pool_top_n,
                                      personalized_pagerank,
                                      resolve_pool_top_n)


# ── 构造 ──

def _mk_chunk(cid, text, speakers=("A",), scene="场景"):
    return Chunk(chunk_id=cid, content_key=cid, doc_id="d", chapter_title="篇",
                 category="mainline", part_title="Part 1", scene_title=scene,
                 script_id="1", chapter_id="1", turns=[],
                 speakers=list(speakers), text=text)


def _mk_graph(spec, entities=None):
    """spec: [(src, rel, dst, chunk_id, conf)] —— 每个 chunk_id 单独成一次抽取。"""
    g = GraphStore(fingerprint="fp")
    ents = {}
    by_chunk: dict[str, list] = {}
    for s, r, d, cid, c in spec:
        ents.setdefault(s, ExtractedEntity(s, "角色", [], ""))
        ents.setdefault(d, ExtractedEntity(d, "角色", [], ""))
        by_chunk.setdefault(cid, []).append(ExtractedRelation(s, r, d, "证据", c))
    for n, t in (entities or {}).items():
        ents[n] = ExtractedEntity(n, t, [], "")
    # 实体声明放在第一个 chunk（保证所有实体都被观察到）
    first = next(iter(by_chunk)) if by_chunk else "c0"
    per = [(cid, Extraction(entities=list(ents.values()) if cid == first else [],
                            relations=rels))
           for cid, rels in by_chunk.items()]
    if not per:
        per = [("c0", Extraction(entities=list(ents.values()), relations=[]))]
    g.build_from_extractions(per)
    return g


def _retriever(spec, chunks, entities=None, vec_map=None, ent_vecs=None):
    g = _mk_graph(spec, entities)
    ci = None
    if vec_map:
        ids = list(vec_map.keys())
        ci = ChunkIndex.build(ids, [vec_map[i] for i in ids])
    ei = None
    if ent_vecs:
        eids = list(ent_vecs.keys())
        ei = EntityVectorIndex.build(eids, eids, [ent_vecs[e] for e in eids])
    return GraphRetriever(g, chunks, ci, ei)


def _onehot(dim, i):
    v = [0.0] * dim
    v[i] = 1.0
    return v


# ── 邻接表与 PPR ──

def test_adjacency_undirected():
    g = _mk_graph([("A", "认识", "B", "c1", 0.9)])
    adj, wsum, edges = build_adjacency(g)
    assert any(m == "B" for m, _ in adj["A"])
    assert any(m == "A" for m, _ in adj["B"])


def test_ppr_scores_seed_highest():
    g = _mk_graph([("A", "认识", "B", "c1", 0.9)])
    adj, _, _ = build_adjacency(g)
    ppr = personalized_pagerank(adj, {"A": 1.0})
    assert ppr["A"] == pytest.approx(1.0)
    assert 0 < ppr["B"] < 1.0


def test_ppr_empty_seeds():
    g = _mk_graph([("A", "认识", "B", "c1", 0.9)])
    adj, _, _ = build_adjacency(g)
    assert personalized_pagerank(adj, {}) == {}


def test_ppr_propagates_multi_hop():
    """A-B-C 链：以 A 为种子时 C 应获得非零分数（多跳可达）。"""
    g = _mk_graph([("A", "认识", "B", "c1", 0.9),
                   ("B", "认识", "C", "c2", 0.9)])
    adj, _, _ = build_adjacency(g)
    ppr = personalized_pagerank(adj, {"A": 1.0})
    assert ppr["C"] > 0, "二跳节点必须被激活"


def test_ppr_two_seeds_beat_one_hop():
    """种子相关节点的分数应高于无关孤立节点。"""
    g = _mk_graph([("A", "认识", "B", "c1", 0.9),
                   ("X", "认识", "Y", "c2", 0.9)])
    adj, _, _ = build_adjacency(g)
    ppr = personalized_pagerank(adj, {"A": 1.0})
    assert ppr["B"] > ppr.get("X", 0.0)


def test_ppr_deterministic():
    g = _mk_graph([("A", "认识", "B", "c1", 0.9), ("B", "认识", "C", "c2", 0.8)])
    adj, _, _ = build_adjacency(g)
    a = personalized_pagerank(adj, {"A": 1.0})
    b = personalized_pagerank(adj, {"A": 1.0})
    assert a == b


def test_ppr_damping_effect():
    g = _mk_graph([("A", "认识", "B", "c1", 0.9)])
    adj, _, _ = build_adjacency(g)
    low = personalized_pagerank(adj, {"A": 1.0}, damping=0.1)
    high = personalized_pagerank(adj, {"A": 1.0}, damping=0.99)
    assert high["B"] > low["B"]


# ── G4：dangling 质量回流 teleport（2026-10-21）──
#
# 旧实现把悬挂质量 `damping*dangling/len(nodes)` **均摊给全图**。真实工件上
# 7033 实体里 1133 个孤立，于是一个孤立种子查询会让全图 5901 个节点全部非零、
# 27110 条边全部 sc>0，graph_channel 产出 91 个无关块。下面三条用例把这个
# 行为钉死；**不得**写成「召回提升」。

def test_ppr_isolated_seed_keeps_mass_on_seed():
    """孤立种子：质量不得泄漏给图里其他任何节点。"""
    g = _mk_graph([("X", "认识", "Y", "c1", 0.9)])   # A 不在图里 → 孤立
    adj, _, _ = build_adjacency(g)
    ppr = personalized_pagerank(adj, {"A": 1.0})
    assert ppr["A"] == pytest.approx(1.0)
    assert ppr.get("X", 0.0) == 0.0, "孤立种子的质量被均摊给了无关节点（G4 未修复）"
    assert ppr.get("Y", 0.0) == 0.0


def test_ppr_dangling_mass_follows_teleport():
    """悬挂质量按 teleport 权重回流：两个种子按 3:1 分，不是均分给全图。"""
    # A 是叶子（悬挂），种子只有 A 与 D；B/C 为 A 的邻居
    g = _mk_graph([("A", "认识", "B", "c1", 0.9),
                   ("A", "认识", "C", "c2", 0.9),
                   ("D", "认识", "E", "c3", 0.9)])
    adj, _, _ = build_adjacency(g)
    ppr = personalized_pagerank(adj, {"A": 3.0, "D": 1.0})
    # A 的邻居拿到的转移质量必须大于完全无关的 E（E 只可能通过 D 到达）
    assert ppr["B"] > ppr.get("E", 0.0)
    assert ppr["A"] == pytest.approx(1.0), "归一化语义必须保持（seed_score=1.0）"


def test_ppr_single_seed_no_leak_to_disconnected_component():
    """连通分量隔离：A 所在分量之外的所有节点必须严格为 0。"""
    g = _mk_graph([("A", "认识", "B", "c1", 0.9),
                   ("X", "认识", "Y", "c2", 0.9),
                   ("Y", "认识", "Z", "c3", 0.9)])
    adj, _, _ = build_adjacency(g)
    ppr = personalized_pagerank(adj, {"A": 1.0})
    for name in ("X", "Y", "Z"):
        assert ppr.get(name, 0.0) == 0.0, f"{name} 位于不相连分量，却被激活"


# ── 实体链接 ──

def test_link_exact_name():
    r = _retriever([("阿黛拉", "认识", "洛佩拉", "c1", 0.9)], [])
    seeds = r.link("阿黛拉是谁")
    assert seeds and seeds[0].eid == "阿黛拉"
    assert seeds[0].how == "exact"


def test_link_via_alias():
    g = GraphStore(fingerprint="fp")
    g.build_from_extractions([
        ("c1", Extraction(
            entities=[ExtractedEntity("维尔汀", "角色", ["汀汀"], ""),
                      ExtractedEntity("基金会", "组织", [], "")],
            relations=[ExtractedRelation("维尔汀", "隶属于", "基金会", "", 0.9)])),
    ])
    r = GraphRetriever(g, [])
    seeds = r.link("汀汀加入了什么组织")
    assert seeds and seeds[0].eid == "维尔汀"
    assert seeds[0].how == "alias"


def test_link_no_match():
    r = _retriever([("A", "认识", "B", "c1", 0.9)], [])
    assert r.link("完全无关的问题") == []


def test_link_longest_name_wins():
    """`星锑` 与 `星锑号` 同时存在时，长名优先匹配，避免短名抢匹配。"""
    g = GraphStore(fingerprint="fp")
    g.build_from_extractions([
        ("c1", Extraction(
            entities=[ExtractedEntity("星锑", "角色", [], ""),
                      ExtractedEntity("星锑号", "物品", [], "")],
            relations=[ExtractedRelation("星锑", "驾驶", "星锑号", "", 0.9)])),
    ])
    r = GraphRetriever(g, [])
    seeds = r.link("星锑号在哪里")
    assert seeds[0].eid == "星锑号"


def test_link_top_k_respected():
    g = GraphStore(fingerprint="fp")
    ents = [ExtractedEntity(f"角色{i}", "角色", [], "") for i in range(10)]
    g.build_from_extractions([("c1", Extraction(entities=ents, relations=[]))])
    r = GraphRetriever(g, [])
    q = "".join(f"角色{i}" for i in range(10))
    assert len(r.link(q, top_k=3)) == 3


def test_vector_seed_merge_below_threshold_rejected():
    r = _retriever([("A", "认识", "B", "c1", 0.9)], [])
    merged = r.merge_vector_seeds([], [("A", "A", 0.2)], threshold=0.8, top_k=5)
    assert merged == []


def test_vector_seed_merge_accepts_high_similarity():
    r = _retriever([("A", "认识", "B", "c1", 0.9)], [])
    merged = r.merge_vector_seeds([], [("A", "A", 0.95)], threshold=0.8, top_k=5)
    assert merged and merged[0].how == "vector"


# ── 通道与融合 ──

def test_mention_channel_returns_seed_chunks():
    g = GraphStore(fingerprint="fp")
    g.build_from_extractions([
        ("cX", Extraction(entities=[ExtractedEntity("A", "角色", [], "")],
                          relations=[])),
    ])
    r = GraphRetriever(g, [_mk_chunk("cX", "A在说话")])
    seeds = r.link("A")
    ch = r.mention_channel(seeds)
    assert "cX" in ch


def test_rrf_fuse_prefers_multi_channel():
    """同时被两个通道命中的块应排在仅单通道命中之前。"""
    evs = GraphRetriever.rrf_fuse({
        "graph": {"both": 1.0, "g_only": 0.9},
        "mention": {"both": 1.0},
    })
    assert evs[0].chunk_id == "both"
    assert set(evs[0].channels) == {"graph", "mention"}


def test_rrf_weights_applied():
    a = GraphRetriever.rrf_fuse({"graph": {"x": 1.0}}, weights={"graph": 10.0})
    b = GraphRetriever.rrf_fuse({"graph": {"x": 1.0}}, weights={"graph": 1.0})
    assert a[0].score > b[0].score


def test_rrf_handles_empty_channels():
    assert GraphRetriever.rrf_fuse({}) == []
    assert GraphRetriever.rrf_fuse({"graph": {}}) == []


def test_graph_channel_returns_evidence_chunks():
    r = _retriever([("A", "认识", "B", "c1", 0.9)], [])
    seeds = r.link("A")
    chunk_scores, edges = r.graph_channel(seeds)
    assert "c1" in chunk_scores
    assert edges and edges[0][1] == "认识"


# ── 端到端 ──

def test_retrieve_returns_seeds_and_evidence():
    chunks = [_mk_chunk("c1", "A与B相识")]
    r = _retriever([("A", "认识", "B", "c1", 0.9)], chunks)
    res = r.retrieve("A和B什么关系")
    assert res.seeds
    assert res.evidence
    assert res.evidence[0].chunk_id == "c1"


def test_retrieve_no_seed_falls_back():
    chunks = [_mk_chunk("c1", "无关内容")]
    vec = {"c1": _onehot(4, 0)}
    r = _retriever([("A", "认识", "B", "c1", 0.9)], chunks, vec_map=vec)
    res = r.retrieve("完全无关的问题", qvec=_onehot(4, 0))
    assert not res.graph_ok
    assert "零命中" in res.note
    assert res.evidence, "应回落向量通道而非空手而归"


def test_retrieve_without_vector_still_works():
    r = _retriever([("A", "认识", "B", "c1", 0.9)], [_mk_chunk("c1", "A与B")])
    res = r.retrieve("A")
    assert res.evidence


def test_retrieve_result_serializable():
    import json
    r = _retriever([("A", "认识", "B", "c1", 0.9)], [_mk_chunk("c1", "A与B")])
    d = r.retrieve("A").to_dict()
    json.dumps(d, ensure_ascii=False)   # 不应抛异常
    assert "seeds" in d and "evidence" in d and "edges" in d


def test_vector_channel_ranks_by_similarity():
    chunks = [_mk_chunk("c1", "x"), _mk_chunk("c2", "y")]
    vec = {"c1": _onehot(4, 0), "c2": _onehot(4, 1)}
    r = _retriever([("A", "认识", "B", "c1", 0.9)], chunks, vec_map=vec)
    ch = r.vector_channel(_onehot(4, 1), top_k=2)
    assert ch and max(ch, key=ch.get) == "c2"


# ── G1：池宽 vs 输出宽（2026-10-21）──
#
# 旧实现把两者绑死在同一个 `top_k` 上（`top_n=max(top_k*4,24)` 又把结果原样
# 返回），于是「top_k 只控输出条数」名不副实。拆成 rank_window_size / size
# 两个参数（Elasticsearch RRF 同款）。

def test_default_pool_top_n_matches_legacy_formula():
    """默认公式必须与改造前逐位等价：max(top_k*4, 24)。"""
    for tk in (1, 2, 5, 6, 10, 20):
        assert default_pool_top_n(tk) == max(tk * 4, 24)
    assert resolve_pool_top_n(6) == 24
    assert resolve_pool_top_n(10) == 40


def test_top_k_truncates_evidence():
    """`top_k` 只控输出条数：evidence 长度恰为 top_k（池里有更多）。"""
    chunks = [_mk_chunk(f"c{i}", f"文本{i}") for i in range(1, 13)]
    g = _mk_graph([(f"E{i}", "认识", f"E{i+1}", f"c{i}", 0.9)
                   for i in range(1, 12)])
    r = GraphRetriever(g, chunks)
    res = r.retrieve("E1", top_k=3, want_pool=True)
    assert len(res.evidence) == 3, f"evidence 未截断到 top_k：{len(res.evidence)}"
    assert res.evidence_pool is not None
    assert len(res.evidence_pool) > len(res.evidence), "池应比窗口宽"
    # 窗口必须是池的前缀（同序，不是另一批块）
    assert [e.chunk_id for e in res.evidence] == \
        [e.chunk_id for e in res.evidence_pool[:3]]


def test_pool_top_n_decoupled_from_top_k():
    """显式池宽只改池，不改窗口；默认路径与显式传默认值逐位等价。"""
    chunks = [_mk_chunk(f"c{i}", f"文本{i}") for i in range(1, 13)]
    g = _mk_graph([(f"E{i}", "认识", f"E{i+1}", f"c{i}", 0.9)
                   for i in range(1, 12)])
    r = GraphRetriever(g, chunks)

    wide = r.retrieve("E1", top_k=3, want_pool=True)
    narrow = r.retrieve("E1", top_k=3, pool_top_n=4, want_pool=True)
    assert len(narrow.evidence) == 3, "改池宽不得影响窗口宽度"
    assert len(narrow.evidence_pool) == 4
    assert len(wide.evidence_pool) >= len(narrow.evidence_pool)

    # 默认（None）与显式传默认公式必须完全一致 —— 这是「行为不变的硬门」
    a = r.retrieve("E1", top_k=3, want_pool=True)
    b = r.retrieve("E1", top_k=3, pool_top_n=default_pool_top_n(3), want_pool=True)
    assert [e.chunk_id for e in a.evidence_pool] == \
        [e.chunk_id for e in b.evidence_pool]
    assert [e.score for e in a.evidence] == [e.score for e in b.evidence]


def test_evidence_pool_optional_and_not_serialized_by_default():
    """`evidence_pool` 默认不填、`to_dict()` 不输出该键（避免工件膨胀 4 倍）。"""
    r = _retriever([("A", "认识", "B", "c1", 0.9)], [_mk_chunk("c1", "A与B")])
    res = r.retrieve("A", top_k=6)
    assert res.evidence_pool is None
    assert "evidence_pool" not in res.to_dict()

    res2 = r.retrieve("A", top_k=6, want_pool=True)
    assert res2.evidence_pool is not None
    assert "evidence_pool" in res2.to_dict()


# ── G2：向量相似度阈值（2026-10-21）──
#
# 阈值是**可选过滤**，默认 `None` = 完全关闭。理由：bge-m3 中文语料实测
# cos 分布 0.32–0.67 / 中位 0.50，硬套模型卡的 [0.6,1] 会把证据砍空
# （LightRAG 就因为该副作用撤掉过 cosine threshold）。

def test_vector_min_score_filters():
    ci = ChunkIndex.build(["a", "b", "c"],
                          [[1.0, 0.0], [0.6, 0.8], [0.0, 1.0]])
    q = [1.0, 0.0]
    assert [cid for cid, _ in ci.search(q, top_k=3)] == ["a", "b", "c"]
    kept = ci.search(q, top_k=3, min_score=0.5)
    assert [cid for cid, _ in kept] == ["a", "b"], "阈值应砍掉 cos=0 的块"
    assert ci.search(q, top_k=3, min_score=1.01) == [], "全砍光时应空手而非报错"


def test_zero_cosine_block_excluded():
    """零相关（正交）块在阈值开启后不得进入向量通道。"""
    ci = ChunkIndex.build(["hit", "ortho"], [[1.0, 0.0], [0.0, 1.0]])
    r = GraphRetriever(_mk_graph([("A", "认识", "B", "c1", 0.9)]), [])
    r.chunk_index = ci
    ch_off = r.vector_channel([1.0, 0.0], top_k=2)
    assert "ortho" in ch_off
    ch_on = r.vector_channel([1.0, 0.0], top_k=2, min_score=0.01)
    assert "ortho" not in ch_on, "cos=0 的块不应拿到 RRF 分"


def test_vector_min_score_none_is_legacy():
    """`None` 必须与改造前逐结果一致（同序、同分、同长度）。"""
    ci = ChunkIndex.build(["a", "b", "c"],
                          [[1.0, 0.0], [0.6, 0.8], [0.0, 1.0]])
    q = [1.0, 0.0]
    legacy = ci.search(q, top_k=3)          # 位置参数、不传阈值
    explicit = ci.search(q, top_k=3, min_score=None)
    assert legacy == explicit


def test_vector_min_score_filters_before_truncation():
    """过滤必须在截断**之前**：否则 top_k 全是低分块时过滤后空手。"""
    ci = ChunkIndex.build(["hi", "lo"], [[1.0, 0.0], [0.0, 1.0]])
    # top_k=1 且阈值为 0.5：若先截断会先取到 hi 再过滤，结果看似正常；
    # 换成查询正交于 hi 时才暴露顺序问题。
    hits = ci.search([1.0, 0.0], top_k=1, min_score=0.5)
    assert [cid for cid, _ in hits] == ["hi"]
    # 阈值把唯一命中砍掉 → 空列表，而不是「先截断后剩 0 个再报错」
    assert ci.search([1.0, 0.0], top_k=1, min_score=2.0) == []


def test_retrieve_passes_vector_min_score_through():
    """端到端：`retrieve(vector_min_score=…)` 必须传到向量通道。"""
    chunks = [_mk_chunk("c1", "A与B"), _mk_chunk("c2", "无关")]
    vec = {"c1": _onehot(4, 0), "c2": _onehot(4, 1)}
    r = _retriever([("A", "认识", "B", "c1", 0.9)], chunks, vec_map=vec)
    res = r.retrieve("A和B什么关系", qvec=_onehot(4, 0), vector_min_score=0.99)
    ids = {e.chunk_id for e in res.evidence}
    assert "c2" not in ids, "低相似块应被阈值挡在融合之外"


# ── ChunkIndex ──

def test_chunk_index_roundtrip(tmp_path):
    ci = ChunkIndex.build(["a", "b"], [[1.0, 0.0], [0.0, 1.0]])
    p = tmp_path / "idx.npz"
    ci.save(p)
    back = ChunkIndex.load(p)
    assert back.chunk_ids == ["a", "b"]
    assert back.size == 2


def test_chunk_index_search_ordering():
    ci = ChunkIndex.build(["a", "b"], [[1.0, 0.0], [0.0, 1.0]])
    hits = ci.search([1.0, 0.0], top_k=2)
    assert hits[0][0] == "a"
    assert hits[0][1] == pytest.approx(1.0)


def test_chunk_index_empty():
    ci = ChunkIndex.build([], [])
    assert ci.search([1.0, 0.0], top_k=3) == []


def test_chunk_index_zero_query():
    ci = ChunkIndex.build(["a"], [[1.0, 0.0]])
    assert ci.search([0.0, 0.0], top_k=1) == []


def test_entity_index_search():
    ei = EntityVectorIndex.build(["A", "B"], ["A", "B"],
                                 [[1.0, 0.0], [0.0, 1.0]])
    hits = ei.search([0.0, 1.0], top_k=1)
    assert hits[0][0] == "B"


# ── 上下文渲染 ──

def test_context_contains_entities_edges_and_evidence():
    chunks = [_mk_chunk("c1", "A与B相识于伦敦")]
    r = _retriever([("A", "认识", "B", "c1", 0.9)], chunks)
    res = r.retrieve("A")
    ctx = r.context(res)
    assert "【图谱实体】" in ctx
    assert "【关系脉络】" in ctx
    assert "【原文证据】" in ctx
    assert "A —认识→ B" in ctx


def test_context_tags_evidence_with_citable_provenance():
    """P4 的引用契约：每条证据块带可解析的 `S{i}` 溯源头（chunk/doc/category）。"""
    chunks = [_mk_chunk("c1", "A与B相识于伦敦"),
              _mk_chunk("c2", "C在柏林目击了同一幕")]
    r = _retriever([("A", "认识", "B", "c1", 0.9), ("C", "目击", "B", "c2", 0.8)],
                   chunks)
    ctx = r.context(r.retrieve("A"), top_k=2)
    assert "[S1 chunk=c1 doc=d cat=mainline] " in ctx
    assert "[S2 chunk=c2 doc=d cat=mainline] " in ctx
    # 编号跟排序走，不跟 chunk_id 走——P4 提示词里「引用 S2」必须能回查到第 2 块
    assert ctx.index("[S1 ") < ctx.index("[S2 ")


def test_context_respects_max_chars():
    chunks = [_mk_chunk("c1", "内容" * 2000)]
    r = _retriever([("A", "认识", "B", "c1", 0.9)], chunks)
    res = r.retrieve("A")
    assert len(r.context(res, max_chars=300)) <= 300


def test_context_empty_result():
    r = _retriever([("A", "认识", "B", "c1", 0.9)], [])
    from compendium_rag.retriever import RetrievalResult
    assert r.context(RetrievalResult(query="q")) == ""


# ── P4.0 按块预算分配（禁止半块）──
#
# v1 是 `out[:max_chars]` 整体尾切：最后一块会被**从中间切断**，模型拿到半块。
# 下面这些用例把 v2 的四条预登记规则钉死：R1 禁止半块、R2 头段先扣、
# R3 均分+余量回收、R4 保底可见、R5 编号跟窗口顺序。

def _mk_long_chunks(spec):
    """spec: [(cid, text_len)] → chunk 列表（正文用可判别的定长串）。"""
    return [_mk_chunk(cid, f"<{cid}>" + "字" * (n - len(cid) - 2))
            for cid, n in spec]


def _evidence_blocks_of(ctx):
    """从渲染串里取每条证据块的 (编号, 溯源头, 正文)，供零半块判定。"""
    out = []
    for seg in ctx.split("\n\n"):
        if not seg.startswith("[S"):
            continue
        head, _, body = seg.partition("] ")
        _, _, body = body.partition("] ")      # 去掉 [篇名 / 场景]
        num = int(head.split()[0][2:])
        out.append((num, head, body))
    return out


def test_context_never_emits_half_block():
    """R1：入选块必须**整段逐字**出现；任何截断都算失败（核心回归）。"""
    spec = [(f"c{i}", 700) for i in range(1, 6)]
    chunks = _mk_long_chunks(spec)
    g = _mk_graph([("A", "认识", "B", "c1", 0.9)])
    r = GraphRetriever(g, chunks)
    from compendium_rag.retriever import Evidence, RetrievalResult
    res = RetrievalResult(query="q")
    res.evidence = [Evidence(cid, 1.0 - i * 0.1, {}, 0.0, [])
                    for i, (cid, _) in enumerate(spec)]
    ctx = r.context(res, top_k=5, max_chars=3000)
    assert FALLBACK_MARK not in ctx
    blocks = _evidence_blocks_of(ctx)
    assert blocks, "至少应有一块进窗"
    for _num, _head, body in blocks:
        assert body in [c.text for c in chunks], "出现半块（正文被切断）"
    assert len(ctx) <= 3000


def test_context_head_counts_against_budget():
    """R2：头段（实体卡+关系脉络）占用预算，证据段只能用余量。"""
    chunks = _mk_long_chunks([("c1", 2000)])
    long_desc = "描" * 300
    g = _mk_graph([("A", "认识", "B", "c1", 0.9)], entities={"A": "角色"})
    g.entities["A"].desc = long_desc
    r = GraphRetriever(g, chunks)
    from compendium_rag.retriever import Evidence, RetrievalResult
    res = RetrievalResult(query="q")
    res.evidence = [Evidence("c1", 1.0, {}, 0.0, [])]
    tight = r.context(res, top_k=1, max_chars=500)
    assert len(tight) <= 500
    # 头段吃掉大半预算 → 2000 字的块装不下 → 走 R4 保底并打标
    assert FALLBACK_MARK in tight
    roomy = r.context(res, top_k=1, max_chars=3000)
    assert chunks[0].text in roomy and FALLBACK_MARK not in roomy


def test_context_skips_oversized_block_and_recycles_share():
    """R3：超份额的长块整块跳过，其份额回收给后面的短块。

    1 块 1400 字 + 4 块 300 字、预算 2000：均分份额 400 → 长块跳过，
    释放的份额让后面至少 3 块短块进窗（v1 尾切只会给 1 全 + 1 半）。
    """
    spec = [("c1", 1400)] + [(f"c{i}", 300) for i in range(2, 6)]
    chunks = _mk_long_chunks(spec)
    g = _mk_graph([("A", "认识", "B", "c1", 0.9)])
    r = GraphRetriever(g, chunks)
    from compendium_rag.retriever import Evidence, RetrievalResult
    res = RetrievalResult(query="q")
    res.evidence = [Evidence(cid, 1.0, {}, 0.0, []) for cid, _ in spec]
    ctx = r.context(res, top_k=5, max_chars=2000)
    blocks = _evidence_blocks_of(ctx)
    kept = {head.split("chunk=")[1].split("]")[0] for _n, head, _b in blocks}
    assert "c1" not in kept, "1400 字长块超出份额应整块跳过"
    assert len(kept) >= 3, f"短块份额未被回收：{kept}"
    for _num, _head, body in blocks:
        assert body in [c.text for c in chunks], "出现半块"


def test_context_costs_use_final_window_width():
    """R1/边界：编号位宽变化（S1→S10）不得把最后一块挤出或切半。"""
    spec = [(f"c{i}", 120) for i in range(1, 13)]
    chunks = _mk_long_chunks(spec)
    g = _mk_graph([("A", "认识", "B", "c1", 0.9)])
    r = GraphRetriever(g, chunks)
    from compendium_rag.retriever import Evidence, RetrievalResult
    res = RetrievalResult(query="q")
    res.evidence = [Evidence(cid, 1.0, {}, 0.0, []) for cid, _ in spec]
    ctx = r.context(res, top_k=12, max_chars=1600)
    blocks = _evidence_blocks_of(ctx)
    assert len(blocks) >= 5
    assert [n for n, _h, _b in blocks] == list(range(1, len(blocks) + 1))
    for _num, _head, body in blocks:
        assert body in [c.text for c in chunks], "出现半块"
    assert len(ctx) <= 1600


def test_context_numbers_follow_window_order_no_gaps():
    """R5：编号从 1 连续、跟窗口顺序走，跳过的块不留空号。"""
    spec = [("c1", 1400)] + [(f"c{i}", 300) for i in range(2, 6)]
    chunks = _mk_long_chunks(spec)
    g = _mk_graph([("A", "认识", "B", "c1", 0.9)])
    r = GraphRetriever(g, chunks)
    from compendium_rag.retriever import Evidence, RetrievalResult
    res = RetrievalResult(query="q")
    res.evidence = [Evidence(cid, 1.0, {}, 0.0, []) for cid, _ in spec]
    ctx = r.context(res, top_k=5, max_chars=2000)
    nums = [n for n, _h, _b in _evidence_blocks_of(ctx)]
    assert nums == list(range(1, len(nums) + 1)), f"编号有空洞：{nums}"


def test_plan_block_window_is_order_preserving_and_bounded():
    """分配器纯函数：入选下标升序、总成本不超预算、拒绝负预算。"""
    from compendium_rag.retriever import plan_block_window
    # 6 块争 900 字：均分份额 150 谁也放不下 1200 的长块与 300 的短块，
    # 首轮直接落空 → 零头贪心把 3 块短块装满（长块整块跳过，绝不切半）。
    picked, left = plan_block_window([1200, 300, 300, 300, 300, 300], 900)
    assert 0 not in picked, "1200 字长块超出可用预算应整块跳过"
    assert picked == [1, 2, 3], picked
    assert left == 0
    assert sum([1200, 300, 300, 300, 300, 300][i] for i in picked) <= 900
    assert plan_block_window([100, 100], 50) == ([], 50)
    assert plan_block_window([], 500) == ([], 500)
    assert plan_block_window([100], -10) == ([], 0)


def test_context_allocator_version_is_declared():
    """R7：版本标必须可读，报告据此分表（v1_tailcut / v2_perblock）。"""
    from compendium_rag.retriever import (CONTEXT_ALLOCATOR,
                                          CONTEXT_ALLOCATOR_LEGACY)
    assert CONTEXT_ALLOCATOR == "v2_perblock"
    assert CONTEXT_ALLOCATOR_LEGACY == "v1_tailcut"
