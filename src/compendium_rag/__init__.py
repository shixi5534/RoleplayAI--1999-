# -*- coding: utf-8 -*-
"""Compendium GraphRAG —— 基于《重返未来：1999》官方剧情档案的独立图谱 RAG。

**独立性声明**：本包不 import 任何 ``roleplay.*``，不读写既有
``data/knowledge`` / ``data/lore``，配置走 ``CMPRAG_`` 前缀，
数据落 ``data/compendium_rag/``，测试落 ``tests/compendium_rag/``。
原有的 ``plot_*`` / ``graph_*`` 体系完全不受影响。
"""
from .chunker import Chunk, chunk_corpus, chunks_stats
from .config import Settings, get_settings
from .corpus import Chapter, Turn, load_corpus, corpus_stats
from .embedder import OllamaEmbedder, cosine
from .extract import Extraction, extract_chunk
from .graph_store import Entity, Edge, GraphStore, fingerprint_of
from .llm import CloudLLM, LLMError
from .retriever import (ChunkIndex, EntityVectorIndex, Evidence, GraphRetriever,
                        RetrievalResult, Seed, personalized_pagerank)

__all__ = [
    "Settings", "get_settings",
    "Chapter", "Turn", "load_corpus", "corpus_stats",
    "Chunk", "chunk_corpus", "chunks_stats",
    "CloudLLM", "LLMError", "OllamaEmbedder", "cosine",
    "Extraction", "extract_chunk",
    "GraphStore", "Entity", "Edge", "fingerprint_of",
    "GraphRetriever", "ChunkIndex", "EntityVectorIndex",
    "Evidence", "RetrievalResult", "Seed", "personalized_pagerank",
]

__version__ = "0.1.0"
