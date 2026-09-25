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
                                      GraphRetriever, build_adjacency,
                                      personalized_pagerank)


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


def test_context_respects_max_chars():
    chunks = [_mk_chunk("c1", "内容" * 2000)]
    r = _retriever([("A", "认识", "B", "c1", 0.9)], chunks)
    res = r.retrieve("A")
    assert len(r.context(res, max_chars=300)) <= 300


def test_context_empty_result():
    r = _retriever([("A", "认识", "B", "c1", 0.9)], [])
    from compendium_rag.retriever import RetrievalResult
    assert r.context(RetrievalResult(query="q")) == ""
