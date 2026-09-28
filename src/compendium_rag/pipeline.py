# -*- coding: utf-8 -*-
"""构建与加载编排：语料 → 分块 → 云端抽取 → 图谱 → 向量索引。

每步都有独立落盘产物与指纹，支持断点续跑（抽取缓存命中即跳过）。
"""
from __future__ import annotations

import asyncio
import json
import logging
import re
import time
from dataclasses import dataclass, field
from pathlib import Path

from .chunker import Chunk, chunk_corpus, chunks_stats
from .config import Settings, get_settings
from .corpus import (corpus_fingerprint, corpus_stats, load_corpus,
                     load_corpus_json, save_corpus)
from .embedder import OllamaEmbedder
from .extract import (PROMPT_VERSION, Extraction, ExtractionCache, cache_key,
                      extract_chunk_raw, normalize)
from .graph_store import GraphStore, fingerprint_of
from .llm import CloudLLM
from .retriever import ChunkIndex, EntityVectorIndex, GraphRetriever

logger = logging.getLogger(__name__)

# 整批失败的致命错误特征：命中后停止后续调用（额度耗尽 / 网关不可达）
FATAL_MARKERS_RE = re.compile(r"额度已用尽|网关不可达|LLMQuotaExhausted|"
                              r"LLMGatewayUnreachable")


@dataclass
class BuildReport:
    chunks: int = 0
    extracted: int = 0
    cache_hits: int = 0
    failed: int = 0
    entities: int = 0
    edges: int = 0
    seconds: float = 0.0
    usage: dict = field(default_factory=dict)
    stages: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {"chunks": self.chunks, "extracted": self.extracted,
                "cache_hits": self.cache_hits, "failed": self.failed,
                "entities": self.entities, "edges": self.edges,
                "seconds": round(self.seconds, 1), "usage": self.usage,
                "stages": self.stages}


# ── 阶段 1：语料 ──

def build_corpus(settings: Settings, write: bool = True) -> tuple[list, dict]:
    chapters = load_corpus(settings.source_dir, settings.categories)
    stats = corpus_stats(chapters)
    if write:
        settings.ensure_dirs()
        save_corpus(chapters, settings.corpus_path)
    return chapters, stats


def load_chapters(settings: Settings) -> list:
    if settings.corpus_path.exists():
        return load_corpus_json(settings.corpus_path)
    return load_corpus(settings.source_dir, settings.categories)


def load_chunks(settings: Settings) -> list[Chunk]:
    """重建分块（确定性，无需落盘；如需落盘见 save_chunks）。"""
    return chunk_corpus(load_chapters(settings), settings)


def save_chunks(chunks: list[Chunk], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(
        {"schema": "compendium_rag.chunks/v1",
         "stats": chunks_stats(chunks),
         "chunks": [c.to_dict() for c in chunks]},
        ensure_ascii=False), encoding="utf-8")
    tmp.replace(path)


def load_chunks_json(path: Path) -> list[Chunk]:
    d = json.loads(path.read_text(encoding="utf-8"))
    return [Chunk.from_dict(c) for c in d.get("chunks", [])]


# ── 阶段 2：云端抽取 ──

async def extract_all(settings: Settings, chunks: list[Chunk],
                      limit: int | None = None,
                      progress_every: int = 50) -> tuple[dict[str, Extraction],
                                                         BuildReport]:
    """并发抽取全部块。缓存命中直接复用**模型原始输出**并本地归一化。

    关键设计：缓存存 raw、归一化在读取时做 —— 调整去噪规则不需要重新问模型
    （见 ``ExtractionCache`` 的说明）。
    """
    settings.ensure_dirs()
    cache = ExtractionCache(settings.cache_dir)
    report = BuildReport(chunks=len(chunks))
    work = chunks[:limit] if limit else chunks

    if not settings.llm_api_key:
        raise RuntimeError("缺少 CMPRAG_LLM_API_KEY / ROLEPLAY_LLM_API_KEY，无法调用云端")

    results: dict[str, Extraction] = {}
    todo: list[tuple[Chunk, str]] = []
    for c in work:
        key = cache_key(c, settings.llm_model, PROMPT_VERSION)
        raw = cache.get_raw(key)
        if raw is not None:
            results[c.chunk_id] = normalize(c, raw)
            report.cache_hits += 1
        else:
            todo.append((c, key))

    logger.info("抽取：总块=%d 缓存命中=%d 待抽取=%d 模型=%s 并发=%d",
                len(work), report.cache_hits, len(todo),
                settings.llm_model, settings.llm_concurrency)

    t0 = time.time()
    llm_usage: dict = {}
    if todo:
        async with CloudLLM(
            base_url=settings.llm_base_url, api_key=settings.llm_api_key,
            model=settings.llm_model, temperature=settings.llm_temperature,
            max_tokens=settings.llm_max_tokens, timeout=settings.llm_timeout,
            concurrency=settings.llm_concurrency,
            max_retries=settings.llm_max_retries,
        ) as llm:
            done = 0
            quota_stop = False
            lock = asyncio.Lock()

            async def one(chunk: Chunk, key: str) -> None:
                nonlocal done, quota_stop
                if quota_stop:
                    # 额度已耗尽：剩余块直接跳过，不再发起调用
                    async with lock:
                        results[chunk.chunk_id] = Extraction(
                            ok=False, error="quota_exhausted")
                        done += 1
                    return
                raw, err = await extract_chunk_raw(llm, chunk)
                ex = normalize(chunk, raw) if raw is not None \
                    else Extraction(ok=False, error=err)
                async with lock:
                    results[chunk.chunk_id] = ex
                    if raw is not None:
                        cache.put_raw(key, raw)
                    if not ex.ok and FATAL_MARKERS_RE.search(ex.error or ""):
                        quota_stop = True
                    done += 1
                    if progress_every and done % progress_every == 0:
                        el = time.time() - t0
                        rate = done / el if el else 0
                        eta = (len(todo) - done) / rate if rate else 0
                        logger.info("  抽取进度 %d/%d（%.1f 块/秒，剩余约 %.0f 秒）",
                                    done, len(todo), rate, eta)

            await asyncio.gather(*(one(c, k) for c, k in todo))
            llm_usage = llm.usage_summary()
            if quota_stop:
                report.stages["quota_exhausted"] = True
                ok_n = sum(1 for c, _ in todo if results.get(c.chunk_id)
                           and results[c.chunk_id].ok)
                logger.error(
                    "抽取因**整批性故障**提前结束（额度耗尽或网关不可达）："
                    "本次成功 %d / 待抽取 %d。已成功部分已落缓存，"
                    "排除故障后重跑 build 可**续传**（已完成块零成本跳过）。",
                    ok_n, len(todo))

    report.extracted = sum(1 for c, _ in todo if results.get(c.chunk_id, None)
                           and results[c.chunk_id].ok)
    report.failed = sum(1 for c, _ in todo
                        if not (results.get(c.chunk_id) and results[c.chunk_id].ok))
    report.seconds = time.time() - t0
    report.usage = llm_usage
    report.stages["extract"] = {"todo": len(todo), "cache_hits": report.cache_hits}
    return results, report


def extraction_summary(results: dict[str, Extraction]) -> dict:
    ok = sum(1 for e in results.values() if e.ok)
    ents = sum(len(e.entities) for e in results.values())
    rels = sum(len(e.relations) for e in results.values())
    empty = sum(1 for e in results.values()
                if e.ok and not e.entities and not e.relations)
    return {"chunks": len(results), "ok": ok, "failed": len(results) - ok,
            "entities_raw": ents, "relations_raw": rels, "empty": empty,
            "avg_entities": round(ents / max(1, ok), 2),
            "avg_relations": round(rels / max(1, ok), 2)}


# ── 阶段 3：图谱 ──

def build_graph(settings: Settings, chunks: list[Chunk],
                results: dict[str, Extraction]) -> tuple[GraphStore, dict]:
    fp = fingerprint_of(corpus_fingerprint(load_chapters(settings)),
                        settings.llm_model, PROMPT_VERSION, settings.chunk_chars)
    g = GraphStore(fingerprint=fp)
    per_chunk = [(c.chunk_id, results.get(c.chunk_id)) for c in chunks]
    stats = g.build_from_extractions(
        per_chunk, min_confidence=settings.edge_min_confidence)
    return g, stats


def safe_save_graph(graph: GraphStore, path: Path,
                    existing: Path | None = None) -> tuple[bool, str]:
    """**拒绝用空图覆盖已有非空图谱**。

    事故背景：一次 `build` 在抽取缓存为空（额度耗尽/缓存被清）的情况下，
    仍然走到构图阶段并以 0 实体覆盖了之前 2096 实体的 `graph.json`。
    构建链路的任何一环失败都不应毁掉已有产物，因此这里做最后一道保护：
    新图为空而旧图非空时，**不写盘**并返回原因。
    """
    existing = existing or path
    if not graph.entities and existing.exists():
        try:
            prev = json.loads(existing.read_text(encoding="utf-8"))
            n_prev = len(prev.get("entities") or [])
        except (OSError, ValueError):
            n_prev = 0
        if n_prev > 0:
            return False, (f"拒绝写入：新图谱为 0 实体，而现有图谱有 {n_prev} "
                           f"个实体（很可能是抽取缓存为空导致的空图）")
    graph.save(path)
    return True, "ok"


# ── 阶段 4：向量索引 ──

async def build_indexes(settings: Settings, chunks: list[Chunk],
                        graph: GraphStore) -> dict:
    """块向量索引 + 实体名向量索引（本地 bge-m3）。"""
    out: dict = {}
    async with OllamaEmbedder(settings.embed_base_url, settings.embed_model,
                              settings.embed_timeout, concurrency=4) as emb:
        dim = await emb.probe()
        out["embed_dim"] = dim
        out["embed_model"] = settings.embed_model

        # 块向量：文本前缀章节语境，提升语义区分度
        texts = [f"{c.chapter_title}｜{c.scene_title}\n{c.text}" if c.scene_title
                 else f"{c.chapter_title}\n{c.text}" for c in chunks]
        t0 = time.time()
        vecs = await emb.embed(texts)
        out["chunk_vectors"] = len(vecs)
        out["chunk_embed_seconds"] = round(time.time() - t0, 1)
        ChunkIndex.build([c.chunk_id for c in chunks], vecs).save(settings.index_path)

        # 实体名向量
        eids = list(graph.entities.keys())
        names = [graph.entities[e].name for e in eids]
        t0 = time.time()
        evecs = await emb.embed(names) if names else []
        out["entity_vectors"] = len(evecs)
        out["entity_embed_seconds"] = round(time.time() - t0, 1)
        if evecs:
            EntityVectorIndex.build(eids, names, evecs).save(
                settings.data_dir / "entity_index.npz")
    return out


def rebuild_from_cache(settings: Settings,
                       chunks: list[Chunk]) -> tuple[GraphStore, dict, dict]:
    """**只用本地缓存**重建图谱（零云端调用）。

    因为 ``ExtractionCache`` 存的是模型原始输出，归一化与构图都是本地后处理，
    所以调整去噪规则 / 实体归并规则后，可以用这个函数立即重建图谱，
    无需重新调用模型。返回 (graph, 图谱统计, 缓存命中统计)。
    """
    cache = ExtractionCache(settings.cache_dir)
    results: dict[str, Extraction] = {}
    missing = 0
    for c in chunks:
        raw = cache.get_raw(cache_key(c, settings.llm_model, PROMPT_VERSION))
        if raw is None:
            missing += 1
            continue
        results[c.chunk_id] = normalize(c, raw)
    graph, stats = build_graph(settings, chunks, results)
    info = {"chunks": len(chunks), "cached": len(results),
            "missing": missing, "cache_hits": cache.hits}
    return graph, stats, info


# ── 加载（查询侧）──

class KnowledgeBase:
    """已构建库的查询入口。"""

    def __init__(self, settings: Settings, graph: GraphStore, chunks: list[Chunk],
                 chunk_index: ChunkIndex | None, entity_index: EntityVectorIndex | None):
        self.settings = settings
        self.graph = graph
        self.chunks = chunks
        self.retriever = GraphRetriever(graph, chunks, chunk_index, entity_index)

    @property
    def chunk_index(self) -> ChunkIndex | None:
        return self.retriever.chunk_index

    @property
    def entity_index(self) -> EntityVectorIndex | None:
        return self.retriever.entity_index

    async def retrieve(self, query: str, top_k: int | None = None,
                       use_vector: bool = True) -> dict:
        """异步检索（需要嵌入时用本地 Ollama）。"""
        s = self.settings
        qvec = None
        ent_hits = None
        if use_vector:
            try:
                async with OllamaEmbedder(s.embed_base_url, s.embed_model,
                                          s.embed_timeout) as emb:
                    qvec = await emb.embed_one(query)
                    if self.entity_index is not None:
                        ent_hits = self.entity_index.search(qvec, s.entity_link_top)
            except Exception as exc:  # noqa: BLE001
                logger.warning("嵌入不可用，退化为纯符号检索：%s", exc)
                qvec = None
                ent_hits = None
        res = self.retriever.retrieve(
            query, qvec, top_k=top_k or s.top_k,
            entity_link_top=s.entity_link_top,
            seed_threshold=s.seed_score_threshold,
            entity_vec_hits=ent_hits,
            weights={"graph": s.graph_weight, "mention": 1.0,
                     "vector": s.vector_weight},
            lex_weight=s.lex_weight, lex_top=s.lex_top, lex_first=s.lex_first,
            rrf_k=s.rrf_k)
        return res.to_dict()

    def context(self, query_res: dict, top_k: int | None = None) -> str:
        from .retriever import RetrievalResult, Seed
        rr = RetrievalResult(query=query_res.get("query", ""))
        rr.seeds = [Seed(s["eid"], s["name"], s["score"], s["how"])
                    for s in query_res.get("seeds", [])]
        rr.edges = [(e["src"], e["relation"], e["dst"], e["ppr"])
                    for e in query_res.get("edges", [])]
        from .retriever import Evidence
        rr.evidence = [Evidence(e["chunk_id"], e["score"], e.get("channels", {}),
                                e.get("ppr", 0.0), e.get("reasons", []))
                       for e in query_res.get("evidence", [])]
        s = self.settings
        return self.retriever.context(rr, top_k=top_k or s.top_k,
                                      max_chars=s.context_max_chars)


def load_kb(settings: Settings | None = None) -> KnowledgeBase:
    """加载已构建的库。缺图谱/索引时给出明确报错。"""
    s = settings or get_settings()
    if not s.graph_path.exists():
        raise FileNotFoundError(
            f"图谱不存在：{s.graph_path}（先运行 build）")
    graph = GraphStore.load(s.graph_path)
    chunks = load_chunks(s)
    ci = ChunkIndex.load(s.index_path) if s.index_path.exists() else None
    ep = s.data_dir / "entity_index.npz"
    ei = EntityVectorIndex.load(ep) if ep.exists() else None
    return KnowledgeBase(s, graph, chunks, ci, ei)


def verify_fingerprint(settings: Settings, graph: GraphStore) -> tuple[bool, str]:
    chunks = load_chunks(settings)
    fp = fingerprint_of(corpus_fingerprint(load_chapters(settings)),
                        settings.llm_model, PROMPT_VERSION, settings.chunk_chars)
    ok, why = graph.check_fingerprint(fp)
    if ok and chunks:
        pass
    return ok, why
