# -*- coding: utf-8 -*-
"""管线测试：语料→分块→图谱→索引的编排、指纹校验、加载。

全部离线：不调用云端 LLM，也不依赖 Ollama（向量索引部分用构造向量）。
"""
from __future__ import annotations

import json

import pytest

from compendium_rag import pipeline as P
from compendium_rag.chunker import chunk_corpus
from compendium_rag.extract import ExtractedEntity, ExtractedRelation, Extraction
from compendium_rag.graph_store import GraphStore, fingerprint_of


def _ex(ents, rels):
    return Extraction(entities=[ExtractedEntity(n, t, a, d)
                                for n, t, a, d in ents],
                      relations=[ExtractedRelation(s, r, d, ev, c)
                                 for s, r, d, ev, c in rels])


# ── 语料阶段 ──

def test_build_corpus_writes_and_reloads(isolated_settings, all_chapters):
    chapters, stats = P.build_corpus(isolated_settings, write=True)
    assert isolated_settings.corpus_path.exists()
    assert stats["chapters"] == 151
    back = P.load_chapters(isolated_settings)
    assert len(back) == len(chapters)


def test_load_chapters_falls_back_to_source(isolated_settings):
    """corpus.json 不存在时直接从 Compendium 源解析（不依赖落盘产物）。"""
    assert not isolated_settings.corpus_path.exists()
    chapters = P.load_chapters(isolated_settings)
    assert len(chapters) == 151


# ── 分块阶段 ──

def test_load_chunks_deterministic(isolated_settings, all_chapters, all_chunks):
    a = all_chunks
    b = all_chunks
    assert [c.chunk_id for c in a] == [c.chunk_id for c in b]


def test_save_and_load_chunks(isolated_settings, all_chapters, all_chunks):
    chunks = all_chunks[:50]
    p = isolated_settings.data_dir / "chunks.json"
    P.save_chunks(chunks, p)
    back = P.load_chunks_json(p)
    assert len(back) == len(chunks)
    assert [c.chunk_id for c in back] == [c.chunk_id for c in chunks]
    assert [c.text for c in back] == [c.text for c in chunks]


def test_save_chunks_atomic(isolated_settings, all_chapters, all_chunks):
    chunks = all_chunks[:10]
    p = isolated_settings.data_dir / "chunks.json"
    P.save_chunks(chunks, p)
    assert p.exists()
    assert not (isolated_settings.data_dir / "chunks.json.tmp").exists()


# ── 图谱阶段 ──

def test_build_graph_sets_fingerprint(isolated_settings, all_chapters, all_chunks):
    chapters = all_chapters
    chunks = chunk_corpus(chapters, isolated_settings)[:5]
    results = {
        chunks[0].chunk_id: _ex(
            [("维尔汀", "角色", [], ""), ("基金会", "组织", [], "")],
            [("维尔汀", "隶属于", "基金会", "证据", 0.9)]),
    }
    graph, stats = P.build_graph(isolated_settings, chunks, results)
    assert graph.fingerprint
    assert stats["entities"] >= 2
    assert stats["edges"] == 1


def test_build_graph_fingerprint_matches_verify(isolated_settings, all_chapters, all_chunks):
    chapters = all_chapters
    chunks = chunk_corpus(chapters, isolated_settings)[:5]
    graph, _ = P.build_graph(isolated_settings, chunks, {})
    graph.save(isolated_settings.graph_path)
    ok, why = P.verify_fingerprint(isolated_settings, graph)
    assert ok, why


def test_verify_fingerprint_detects_model_change(isolated_settings, all_chapters, all_chunks):
    chapters = all_chapters
    chunks = chunk_corpus(chapters, isolated_settings)[:5]
    graph, _ = P.build_graph(isolated_settings, chunks, {})
    # 换模型 → 指纹应失配
    other = isolated_settings.with_(llm_model="another-model")
    ok, why = P.verify_fingerprint(other, graph)
    assert not ok
    assert "不匹配" in why


def test_missing_graph_raises_clear_error(isolated_settings, all_chapters, all_chunks):
    with pytest.raises(FileNotFoundError) as ei:
        P.load_kb(isolated_settings)
    assert "图谱不存在" in str(ei.value)


# ── 空图保护（防「缓存为空 → 覆盖已有图谱」事故）──

def test_safe_save_refuses_empty_overwrite(isolated_settings, all_chapters, all_chunks):
    """新图为空而旧图非空时，必须拒绝写盘。

    事故背景：一次 build 在抽取缓存为空的情况下走到构图阶段，
    以 0 实体覆盖了 2096 实体的 graph.json。任何一环失败都不该毁掉已有产物。
    """
    chunks = all_chunks[:5]
    good, _ = P.build_graph(isolated_settings, chunks, {
        chunks[0].chunk_id: _ex(
            [("维尔汀", "角色", [], ""), ("基金会", "组织", [], "")],
            [("维尔汀", "隶属于", "基金会", "证据", 0.9)])})
    good.save(isolated_settings.graph_path)
    assert len(GraphStore.load(isolated_settings.graph_path).entities) == 2

    empty, _ = P.build_graph(isolated_settings, chunks, {})
    ok, why = P.safe_save_graph(empty, isolated_settings.graph_path)
    assert ok is False
    assert "0 实体" in why
    assert len(GraphStore.load(isolated_settings.graph_path).entities) == 2


def test_safe_save_allows_when_no_existing(isolated_settings, all_chapters, all_chunks):
    """首次构建（无旧图）时，空图也应正常写入。"""
    empty, _ = P.build_graph(isolated_settings, all_chunks[:3], {})
    ok, why = P.safe_save_graph(empty, isolated_settings.graph_path)
    assert ok is True and why == "ok"
    assert isolated_settings.graph_path.exists()


def test_safe_save_allows_nonempty_overwrite(isolated_settings, all_chapters, all_chunks):
    chunks = all_chunks[:5]
    old, _ = P.build_graph(isolated_settings, chunks, {
        chunks[0].chunk_id: _ex([("A", "角色", [], "")], [])})
    old.save(isolated_settings.graph_path)
    new, _ = P.build_graph(isolated_settings, chunks, {
        chunks[0].chunk_id: _ex(
            [("A", "角色", [], ""), ("B", "组织", [], "")],
            [("A", "隶属于", "B", "证据", 0.9)])})
    ok, _ = P.safe_save_graph(new, isolated_settings.graph_path)
    assert ok is True
    assert len(GraphStore.load(isolated_settings.graph_path).entities) == 2


def test_rebuild_does_not_clobber_graph_when_cache_empty(
        isolated_settings, all_chapters, all_chunks):
    """rebuild 在缓存为空时不得把已有图谱清空（回归事故）。"""
    chunks = all_chunks[:5]
    keep, _ = P.build_graph(isolated_settings, chunks, {
        chunks[0].chunk_id: _ex(
            [("维尔汀", "角色", [], ""), ("基金会", "组织", [], "")],
            [("维尔汀", "隶属于", "基金会", "证据", 0.9)])})
    keep.save(isolated_settings.graph_path)

    graph, stats, info = P.rebuild_from_cache(isolated_settings, chunks)
    assert info["cached"] == 0
    ok, why = P.safe_save_graph(graph, isolated_settings.graph_path)
    assert ok is False, "缓存为空时不应覆盖已有图谱"
    assert len(GraphStore.load(isolated_settings.graph_path).entities) == 2


# ── 抽取汇总 ──

def test_extraction_summary_counts():
    ok = _ex([("A", "角色", [], "")], [("A", "认识", "B", "", 0.9)])
    empty = Extraction()
    bad = Extraction(ok=False, error="x")
    s = P.extraction_summary({"c1": ok, "c2": empty, "c3": bad})
    assert s["chunks"] == 3
    assert s["ok"] == 2
    assert s["failed"] == 1
    assert s["empty"] == 1
    assert s["entities_raw"] == 1
    assert s["relations_raw"] == 1


def test_extract_all_requires_api_key(isolated_settings, all_chapters, all_chunks):
    import asyncio

    s = isolated_settings.with_(llm_api_key="")
    chunks = all_chunks[:2]
    with pytest.raises(RuntimeError) as ei:
        asyncio.run(P.extract_all(s, chunks))
    assert "API_KEY" in str(ei.value)


# ── 缓存重建（零云端调用）──

def test_rebuild_from_cache_uses_raw_cache(isolated_settings, all_chunks):
    """改归一化/归并规则后，应能用缓存零成本重建图谱。

    这是 raw-cache 设计的直接收益：规则迭代不必重跑云端抽取。
    """
    from compendium_rag.extract import PROMPT_VERSION, ExtractionCache, cache_key

    chunks = all_chunks[:6]
    chunks = [c.__class__.from_dict(c.to_dict()) for c in chunks]  # 避免改共享对象
    cache = ExtractionCache(isolated_settings.cache_dir)
    cache.put_raw(cache_key(chunks[0], isolated_settings.llm_model,
                            PROMPT_VERSION),
                  {"entities": [{"name": "维尔汀", "type": "角色"},
                                {"name": "高个子", "type": "角色"}],
                   "relations": [{"src": "维尔汀", "relation": "隶属于",
                                  "dst": "基金会", "confidence": 0.9}]})
    cache.put_raw(cache_key(chunks[1], isolated_settings.llm_model,
                            PROMPT_VERSION),
                  {"entities": [{"name": "十四行诗", "type": "角色"}],
                   "relations": []})

    graph, stats, info = P.rebuild_from_cache(isolated_settings, chunks)
    assert info["cached"] == 2
    assert info["missing"] == len(chunks) - 2
    assert "维尔汀" in graph.entities
    assert "高个子" not in graph.entities, "归一化规则应在重建时生效"
    assert "十四行诗" in graph.entities


def test_rebuild_from_cache_without_any_cache(isolated_settings, all_chunks):
    graph, stats, info = P.rebuild_from_cache(isolated_settings, all_chunks[:4])
    assert info["cached"] == 0
    assert stats["entities"] == 0


# ── 加载与查询入口 ──

def _seed_kb(settings, chunks, graph, chunk_ids, vecs, evecs):
    from compendium_rag.retriever import ChunkIndex, EntityVectorIndex

    graph.save(settings.graph_path)
    ChunkIndex.build(chunk_ids, vecs).save(settings.index_path)
    if evecs:
        eids = list(graph.entities.keys())
        EntityVectorIndex.build(eids, eids, evecs).save(
            settings.data_dir / "entity_index.npz")


def test_load_kb_and_retrieve_symbolic(isolated_settings, all_chapters, all_chunks):
    import asyncio

    chapters = all_chapters
    chunks = chunk_corpus(chapters, isolated_settings)[:3]
    results = {
        chunks[0].chunk_id: _ex(
            [("维尔汀", "角色", [], ""), ("十四行诗", "角色", [], "")],
            [("维尔汀", "认识", "十四行诗", "证据", 0.9)]),
    }
    graph, _ = P.build_graph(isolated_settings, chunks, results)
    graph.save(isolated_settings.graph_path)

    kb = P.load_kb(isolated_settings)
    assert kb.chunk_index is None
    assert kb.entity_index is None

    res = asyncio.run(kb.retrieve("维尔汀和十四行诗", use_vector=False))
    assert res["seeds"]
    assert res["evidence"]


def test_load_kb_with_indexes(isolated_settings, all_chapters, all_chunks):
    chapters = all_chapters
    chunks = chunk_corpus(chapters, isolated_settings)[:3]
    results = {chunks[0].chunk_id: _ex([("A", "角色", [], "")], [])}
    graph, _ = P.build_graph(isolated_settings, chunks, results)
    ids = [c.chunk_id for c in chunks]
    _seed_kb(isolated_settings, chunks, graph, ids,
             [[1.0, 0.0]] * len(ids), [[1.0, 0.0]])

    kb = P.load_kb(isolated_settings)
    assert kb.chunk_index is not None
    assert kb.chunk_index.size == len(ids)
    assert kb.entity_index is not None


def test_kb_context_renders(isolated_settings, all_chapters, all_chunks):
    chapters = all_chapters
    chunks = chunk_corpus(chapters, isolated_settings)[:3]
    results = {
        chunks[0].chunk_id: _ex(
            [("维尔汀", "角色", [], "主角"), ("十四行诗", "角色", [], "")],
            [("维尔汀", "认识", "十四行诗", "证据句", 0.9)]),
    }
    graph, _ = P.build_graph(isolated_settings, chunks, results)
    graph.save(isolated_settings.graph_path)
    kb = P.load_kb(isolated_settings)
    import asyncio
    res = asyncio.run(kb.retrieve("维尔汀", use_vector=False))
    ctx = kb.context(res)
    assert "【图谱实体】" in ctx
    assert "维尔汀" in ctx


def test_kb_context_respects_budget(isolated_settings, all_chapters, all_chunks):
    chapters = all_chapters
    chunks = chunk_corpus(chapters, isolated_settings)[:3]
    results = {c.chunk_id: _ex([("A", "角色", [], "")], []) for c in chunks}
    graph, _ = P.build_graph(isolated_settings, chunks, results)
    graph.save(isolated_settings.graph_path)
    small = isolated_settings.with_(context_max_chars=120)
    kb = P.load_kb(small)
    import asyncio
    res = asyncio.run(kb.retrieve("A", use_vector=False))
    assert len(kb.context(res)) <= 120


# ── 报告结构 ──

def test_build_report_serializable():
    r = P.BuildReport(chunks=5, extracted=4, cache_hits=1, failed=1,
                      entities=10, edges=7, seconds=12.5,
                      usage={"calls": 4}, stages={"extract": {"todo": 4}})
    d = r.to_dict()
    json.dumps(d, ensure_ascii=False)
    assert d["chunks"] == 5
    assert d["seconds"] == 12.5
