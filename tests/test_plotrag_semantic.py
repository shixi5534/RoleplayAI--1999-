# -*- coding: utf-8 -*-
"""M8：语义向量检索层（跨语言）的回归测试。

被锁住的行为
    1. **指纹校验四项**（schema / 嵌入模型 / 维度 / 语料指纹）任一不符即判过期——
       拿旧向量配新模型会静默产出垃圾结果，比"没有这一层"危险得多；
    2. **静默降级**：索引缺失 / 文件损坏 / 嵌入服务不可用 / 通道开关关闭，
       四条路径都必须不抛异常、不改变其余通道的行为；
    3. **检索正确性**：向量已 L2 归一化时点积即余弦，名次必须与余弦一致；
    4. **默认关闭**：当前可用嵌入器（nomic-embed-text，英文单语）做中文→英文
       跨语言是**净负收益**（300 题实测 −3.7pt），默认必须是 False。

测试**不依赖 Ollama**：用一个确定性的假嵌入器，避免 CI 里因为本地服务没起而飘。
"""
from __future__ import annotations

import json

import numpy as np
import pytest

from roleplay.core.knowledge.graph_store import GraphStore
from roleplay.core.knowledge.plot_corpus import PlotChunk, PlotCorpus
from roleplay.core.knowledge.plot_graph import PlotGraphRegistry, PlotGraphRetriever
from roleplay.core.knowledge.plot_semantic import (
    INDEX_SCHEMA,
    SemanticIndex,
    corpus_sha16,
)


class FakeEmbedder:
    """确定性假嵌入器：把文本映射到固定维度的小向量（按字符哈希）。"""

    def __init__(self, dim: int = 8) -> None:
        self._dim = dim
        self.fail = False

    @property
    def dim(self) -> int:
        return self._dim

    @property
    def name(self) -> str:
        return "fake"

    def _vec(self, text: str) -> list[float]:
        v = np.zeros(self._dim, dtype=np.float32)
        for ch in text or " ":
            v[ord(ch) % self._dim] += 1.0
        n = np.linalg.norm(v) or 1.0
        return (v / n).tolist()

    def embed(self, texts):
        if self.fail:
            raise RuntimeError("嵌入服务不可用")
        return [self._vec(t) for t in texts]

    def embed_query(self, text):
        if self.fail:
            raise RuntimeError("嵌入服务不可用")
        return self._vec(text)


def _write_index(tmp_path, *, embedder="fake", dim=8, csha="abc123", n=3,
                 corrupt=False):
    npz = tmp_path / "plot_index_x.npz"
    meta = tmp_path / "plot_index_x.json"
    vecs = np.eye(dim, dtype=np.float32)[:n]
    if corrupt:
        npz.write_bytes(b"not-an-npz")
    else:
        np.savez_compressed(npz, vectors=vecs,
                            hashes=np.array([f"h{i}" for i in range(n)], dtype="U16"))
    meta.write_text(json.dumps({
        "schema": INDEX_SCHEMA, "embedder": embedder, "dim": dim,
        "count": n, "corpus_sha16": csha,
    }, ensure_ascii=False), encoding="utf-8")
    return npz, meta


class TestFingerprintGate:
    def test_valid_index_passes(self, tmp_path):
        npz, meta = _write_index(tmp_path)
        idx = SemanticIndex(npz, meta, embedder=FakeEmbedder())
        assert idx.load() and idx.available
        ok, why = idx.check_fresh(embedder_name="fake", dim=8, corpus_sha16="abc123")
        assert ok and why == "ok"

    @pytest.mark.parametrize(
        "kwargs,field",
        [
            ({"embedder": "other"}, "嵌入模型"),
            ({"dim": 16}, "维度"),
            ({"csha": "zzz"}, "语料指纹"),
        ],
    )
    def test_each_mismatch_rejects(self, tmp_path, kwargs, field):
        """索引里存的值与**运行时**的值不符 → 必须判过期。

        运行时一律用规范值 ("fake", 8, "abc123")；索引按参数写成错的值。
        """
        npz, meta = _write_index(tmp_path, **kwargs)
        idx = SemanticIndex(npz, meta, embedder=FakeEmbedder())
        assert idx.load()
        ok, why = idx.check_fresh(embedder_name="fake", dim=8, corpus_sha16="abc123")
        assert not ok, f"{field} 不符却判为新鲜"
        assert field in why

    def test_schema_mismatch_rejects(self, tmp_path):
        npz, meta = _write_index(tmp_path)
        m = json.loads(meta.read_text(encoding="utf-8"))
        m["schema"] = "plot-index-v0"
        meta.write_text(json.dumps(m), encoding="utf-8")
        idx = SemanticIndex(npz, meta, embedder=FakeEmbedder())
        idx.load()
        ok, why = idx.check_fresh(embedder_name="fake", dim=8, corpus_sha16="abc123")
        assert not ok and "schema" in why

    def test_corrupt_file_degrades_without_raising(self, tmp_path):
        npz, meta = _write_index(tmp_path, corrupt=True)
        idx = SemanticIndex(npz, meta, embedder=FakeEmbedder())
        assert idx.load() is False
        assert idx.available is False
        assert "读取失败" in idx.disabled_reason

    def test_missing_file_degrades(self, tmp_path):
        idx = SemanticIndex(tmp_path / "nope.npz", tmp_path / "nope.json",
                            embedder=FakeEmbedder())
        assert idx.load() is False and not idx.available


class TestSearchCorrectness:
    def test_ranking_matches_cosine(self, tmp_path):
        npz, meta = _write_index(tmp_path, n=3, dim=4)
        idx = SemanticIndex(npz, meta, embedder=FakeEmbedder(dim=4))
        idx.load()
        hits = idx.search(np.array([1.0, 0, 0, 0], dtype=np.float32), top_k=3)
        assert [h for h, _s in hits][0] == "h0", "余弦最高的应是 h0"
        assert hits[0][1] == pytest.approx(1.0, abs=1e-6)

    def test_top_k_respected(self, tmp_path):
        npz, meta = _write_index(tmp_path, n=3, dim=4)
        idx = SemanticIndex(npz, meta, embedder=FakeEmbedder(dim=4))
        idx.load()
        assert len(idx.search(np.ones(4, dtype=np.float32), top_k=2)) == 2

    def test_dim_mismatch_returns_empty_not_crash(self, tmp_path):
        npz, meta = _write_index(tmp_path, n=3, dim=4)
        idx = SemanticIndex(npz, meta, embedder=FakeEmbedder(dim=4))
        idx.load()
        assert idx.search(np.ones(9, dtype=np.float32), top_k=3) == []

    def test_embed_failure_returns_none(self, tmp_path):
        npz, meta = _write_index(tmp_path)
        emb = FakeEmbedder()
        idx = SemanticIndex(npz, meta, embedder=emb)
        idx.load()
        emb.fail = True
        assert idx.embed_query("任意") is None


class TestLanguageMask:
    """候选池语言限制（M8 反击"语言匹配压过语义匹配"的实验手段）。"""

    def _idx(self, tmp_path):
        npz, meta = _write_index(tmp_path, n=3, dim=4)
        idx = SemanticIndex(npz, meta, embedder=FakeEmbedder(dim=4))
        idx.load()
        return idx

    def test_mask_restricts_candidates(self, tmp_path):
        idx = self._idx(tmp_path)
        # h0 余弦最高，但被掩掉后必须只能从 h1/h2 里出
        idx.set_row_mask(np.array([False, True, True]))
        hits = idx.search(np.array([1.0, 0, 0, 0], dtype=np.float32), top_k=3)
        assert "h0" not in [h for h, _s in hits]
        assert len(hits) == 2

    def test_empty_mask_returns_empty(self, tmp_path):
        idx = self._idx(tmp_path)
        idx.set_row_mask(np.array([False, False, False]))
        assert idx.search(np.ones(4, dtype=np.float32), top_k=3) == []

    def test_wrong_length_mask_is_ignored_not_crash(self, tmp_path):
        """长度不符的掩码必须被安全忽略（配置错不该让检索崩掉）。"""
        idx = self._idx(tmp_path)
        idx.set_row_mask(np.array([True, False]))
        hits = idx.search(np.ones(4, dtype=np.float32), top_k=3)
        assert len(hits) == 3, "掩码长度不符时应回退到全量候选"

    def test_mask_none_clears(self, tmp_path):
        idx = self._idx(tmp_path)
        idx.set_row_mask(np.array([False, False, False]))
        idx.set_row_mask(None)
        assert len(idx.search(np.ones(4, dtype=np.float32), top_k=3)) == 3


def _corpus_with_two_chunks(tmp_path):
    corpus = PlotCorpus(tmp_path / "c.json", character_id="x")
    corpus.chunks = [
        PlotChunk(hash="h0", text="海盗船上的歌手是苏芙比。", doc_id="d1", bv="", page=1),
        PlotChunk(hash="h1", text="火车在黎明时分出发。", doc_id="d2", bv="", page=1),
    ]
    return corpus


class TestRetrieverIntegration:
    def test_disabled_by_default_keeps_behaviour(self, tmp_path):
        """默认关闭：即使索引可加载，也不产生 semantic 块。"""
        corpus = _corpus_with_two_chunks(tmp_path)
        store = GraphStore(tmp_path / "g.json", min_confidence=0.5)
        store.upsert_entities([{"name": "苏芙比"}])
        npz, meta = _write_index(tmp_path, n=2)
        idx = SemanticIndex(npz, meta, embedder=FakeEmbedder())
        idx.load()
        retr = PlotGraphRetriever(corpus, store, min_confidence=0.5, include_weak=True,
                                  semantic_index=idx, semantic_enabled=False)
        out = retr.retrieve("海盗船上的歌手是谁？", top_chunks=3, lexical_fallback=0)
        assert all(c.metadata.get("path") != "semantic" for c in out)

    def test_enabled_emits_semantic_path(self, tmp_path):
        corpus = _corpus_with_two_chunks(tmp_path)
        store = GraphStore(tmp_path / "g.json", min_confidence=0.5)
        store.upsert_entities([{"name": "苏芙比"}])
        emb = FakeEmbedder()
        npz, meta = _write_index(tmp_path, n=2)
        idx = SemanticIndex(npz, meta, embedder=emb)
        idx.load()
        # 让查询向量恰好等于 h0（余弦 1.0），保证语义通道一定把 h0 带回来
        idx.vectors = np.array([[1.0] + [0.0] * 7, [0.0] * 8], dtype=np.float32)
        emb._vec = lambda text: [1.0] + [0.0] * 7
        retr = PlotGraphRetriever(corpus, store, min_confidence=0.5, include_weak=True,
                                  semantic_index=idx, semantic_enabled=True,
                                  semantic_top=1)
        # 查询必须能链上实体——语义通道**过种子门控**（见下一条测试的理由）
        out = retr.retrieve("苏芙比 任意问句", top_chunks=3, lexical_fallback=0)
        assert any("semantic" in (c.metadata.get("paths") or []) for c in out), \
            f"语义通道未生效：{[c.metadata.get('paths') for c in out]}"

    def test_no_seed_blocks_semantic_channel(self, tmp_path):
        """**离题问句不得注入**：语义通道必须与词法兜底同口径地过种子门控。

        这条是实测事故的护栏：第一版语义通道放在门控之前，结果 10 条离题负样本
        从 0 块炸到 **49 块**（「今天天气怎么样」「用 Python 写一个快速排序」
        各被注入 5 块无关转写）——语义检索什么都不看就能返回"最像"的 top-K。
        """
        corpus = _corpus_with_two_chunks(tmp_path)
        store = GraphStore(tmp_path / "g.json", min_confidence=0.5)
        store.upsert_entities([{"name": "苏芙比"}])
        emb = FakeEmbedder()
        npz, meta = _write_index(tmp_path, n=2)
        idx = SemanticIndex(npz, meta, embedder=emb)
        idx.load()
        idx.vectors = np.array([[1.0] + [0.0] * 7, [0.0] * 8], dtype=np.float32)
        emb._vec = lambda text: [1.0] + [0.0] * 7
        retr = PlotGraphRetriever(corpus, store, min_confidence=0.5, include_weak=True,
                                  semantic_index=idx, semantic_enabled=True,
                                  semantic_top=2)
        # 与剧情毫无关系、且链不上任何实体的问句
        out = retr.retrieve("用 Python 写一个快速排序", top_chunks=3, lexical_fallback=0)
        assert all(c.metadata.get("path") != "semantic" for c in out), \
            "离题问句被语义通道注入——负样本零注入的护栏被破坏"

    def test_min_score_threshold_filters(self, tmp_path):
        """余弦低于阈值的语义块不得入选（第二道防线）。"""
        corpus = _corpus_with_two_chunks(tmp_path)
        store = GraphStore(tmp_path / "g.json", min_confidence=0.5)
        store.upsert_entities([{"name": "苏芙比"}])
        emb = FakeEmbedder()
        npz, meta = _write_index(tmp_path, n=2)
        idx = SemanticIndex(npz, meta, embedder=emb)
        idx.load()
        idx.vectors = np.array([[0.10] + [0.0] * 7, [0.0] * 8], dtype=np.float32)
        emb._vec = lambda text: [1.0] + [0.0] * 7
        retr = PlotGraphRetriever(corpus, store, min_confidence=0.5, include_weak=True,
                                  semantic_index=idx, semantic_enabled=True,
                                  semantic_top=2, semantic_min_score=0.5)
        out = retr.retrieve("苏芙比 任意问句", top_chunks=3, lexical_fallback=0)
        assert all(c.metadata.get("path") != "semantic" for c in out)

    def test_embedder_down_degrades_silently(self, tmp_path):
        """嵌入服务挂掉：通道跳过，其余通道照常出块（绝不能拖垮主链路）。"""
        corpus = _corpus_with_two_chunks(tmp_path)
        store = GraphStore(tmp_path / "g.json", min_confidence=0.5)
        store.upsert_entities([{"name": "苏芙比"}])
        emb = FakeEmbedder()
        npz, meta = _write_index(tmp_path, n=2)
        idx = SemanticIndex(npz, meta, embedder=emb)
        idx.load()
        emb.fail = True
        retr = PlotGraphRetriever(corpus, store, min_confidence=0.5, include_weak=True,
                                  semantic_index=idx, semantic_enabled=True)
        out = retr.retrieve("海盗船上的歌手是谁？", top_chunks=3, lexical_fallback=0)
        assert all(c.metadata.get("path") != "semantic" for c in out)

    def test_no_index_means_no_channel(self, tmp_path):
        corpus = _corpus_with_two_chunks(tmp_path)
        store = GraphStore(tmp_path / "g.json", min_confidence=0.5)
        store.upsert_entities([{"name": "苏芙比"}])
        retr = PlotGraphRetriever(corpus, store, min_confidence=0.5, include_weak=True,
                                  semantic_index=None, semantic_enabled=True)
        out = retr.retrieve("海盗船上的歌手是谁？", top_chunks=3, lexical_fallback=0)
        assert all(c.metadata.get("path") != "semantic" for c in out)


class TestRegistryStatus:
    def test_missing_index_reports_reason(self, tmp_path):
        reg = PlotGraphRegistry(corpus_dir=tmp_path, graph_dir=tmp_path,
                                embedder=FakeEmbedder())
        cpath = tmp_path / "plot_corpus_x.json"
        assert reg._load_semantic("x", cpath) is None
        assert "未构建" in reg.semantic_status["x"]

    def test_stale_index_reports_reason(self, tmp_path):
        cpath = tmp_path / "plot_corpus_x.json"
        cpath.write_text("{}", encoding="utf-8")
        _write_index(tmp_path, csha="stale000")
        reg = PlotGraphRegistry(corpus_dir=tmp_path, graph_dir=tmp_path,
                                embedder=FakeEmbedder())
        assert reg._load_semantic("x", cpath) is None
        assert "过期" in reg.semantic_status["x"]

    def test_fresh_index_loads(self, tmp_path):
        cpath = tmp_path / "plot_corpus_x.json"
        cpath.write_text("{}", encoding="utf-8")
        _write_index(tmp_path, csha=corpus_sha16(cpath))
        reg = PlotGraphRegistry(corpus_dir=tmp_path, graph_dir=tmp_path,
                                embedder=FakeEmbedder())
        idx = reg._load_semantic("x", cpath)
        assert idx is not None and idx.count == 3
        assert "ok" in reg.semantic_status["x"]
