# -*- coding: utf-8 -*-
"""需要**真实外部依赖**的集成测试（默认跳过）。

运行方式：
    pytest tests/compendium_rag/ -m online -v

前置条件：
- 云端 LLM 网关可用（``CMPRAG_LLM_BASE_URL`` / ``CMPRAG_LLM_API_KEY``）
- 本地 Ollama 提供 ``bge-m3``（向量索引与查询侧嵌入）

这些用例**不进默认 CI 路径**，因为它们依赖网络与配额；
但它们是"提示词改动没有把抽取质量改坏"的唯一真实信号，
因此在需要评估抽取质量时必须显式跑。
"""
from __future__ import annotations

import asyncio
import os

import pytest

from compendium_rag.config import get_settings
from compendium_rag.extract import (SYSTEM_PROMPT, build_user_prompt,  # noqa: F401
                                    normalize)
from compendium_rag.llm import CloudLLM
from compendium_rag import pipeline as P

pytestmark = pytest.mark.online


def _settings():
    s = get_settings()
    if not s.llm_api_key:
        pytest.skip("未配置云端 API Key")
    return s


def _sample_chunks(n=4):
    s = get_settings()
    chunks = P.load_chunks(s)
    step = max(1, len(chunks) // n)
    return [chunks[i * step] for i in range(n)]


async def _extract_raw(chunk, max_retries=3):
    s = _settings()
    async with CloudLLM(base_url=s.llm_base_url, api_key=s.llm_api_key,
                        model=s.llm_model, temperature=s.llm_temperature,
                        max_tokens=s.llm_max_tokens, timeout=s.llm_timeout,
                        concurrency=2, max_retries=max_retries) as llm:
        return await llm.complete_json(SYSTEM_PROMPT, build_user_prompt(chunk))


def test_cloud_llm_returns_parseable_json():
    """云端模型必须返回可解析的实体/关系信封。"""
    chunk = _sample_chunks(1)[0]
    raw, meta = asyncio.run(_extract_raw(chunk))
    assert isinstance(raw, dict)
    assert "entities" in raw
    assert meta.model


def test_cloud_extraction_yields_entities():
    """抽取结果必须非空——这是 v1 裸数组塌缩（12 实体→0）的回归守卫。"""
    chunk = _sample_chunks(1)[0]
    raw, _ = asyncio.run(_extract_raw(chunk))
    ex = normalize(chunk, raw)
    assert ex.entities, f"抽取为空：{chunk.chunk_id}"
    assert ex.relations or len(ex.entities) >= 3


def test_extraction_quality_on_several_chunks():
    """多样本质量门槛：平均实体数、空结果率、噪声形态。"""
    chunks = _sample_chunks(4)
    total_e = total_r = 0
    empties = 0
    for c in chunks:
        raw, _ = asyncio.run(_extract_raw(c))
        ex = normalize(c, raw)
        total_e += len(ex.entities)
        total_r += len(ex.relations)
        if not ex.entities and not ex.relations:
            empties += 1
        for e in ex.entities:
            # 噪声形态不应出现（提示词 + 归一化双重防线）
            assert not e.name.startswith(("那个", "被捆绑", "一位", "某个")), \
                f"描述性伪实体漏网：{e.name}"
            assert len(e.name) <= 16, f"实体名过长（疑似句子）：{e.name}"
    assert empties == 0, "出现空抽取块"
    assert total_e / len(chunks) >= 3, "平均实体数过低"
    assert total_r / len(chunks) >= 2, "平均关系数过低"


def test_relations_have_evidence():
    """关系必须带原文证据（可溯源）。"""
    chunk = _sample_chunks(1)[0]
    raw, _ = asyncio.run(_extract_raw(chunk))
    ex = normalize(chunk, raw)
    assert ex.relations, "该样本应有关系"
    with_ev = [r for r in ex.relations if r.evidence]
    assert len(with_ev) / len(ex.relations) >= 0.8, \
        "证据覆盖率低于 80%"


def test_entity_names_are_grounded_in_text():
    """实体名（或其别名）应能在片段文本/说话人里找到，防止模型凭空编造。"""
    chunk = _sample_chunks(1)[0]
    raw, _ = asyncio.run(_extract_raw(chunk))
    ex = normalize(chunk, raw)
    blob = chunk.text + "".join(chunk.speakers)
    grounded = 0
    for e in ex.entities:
        if e.name in blob or any(a in blob for a in e.aliases):
            grounded += 1
    ratio = grounded / max(1, len(ex.entities))
    assert ratio >= 0.6, f"实体原文接地率过低：{ratio:.2f}"


def test_ollama_embedder_available():
    """本地 bge-m3 可用性（向量通道的前置条件）。"""
    from compendium_rag.embedder import OllamaEmbedder

    s = get_settings()
    async def probe():
        async with OllamaEmbedder(s.embed_base_url, s.embed_model,
                                  s.embed_timeout) as emb:
            return await emb.probe()
    try:
        dim = asyncio.run(probe())
    except Exception as exc:  # noqa: BLE001
        pytest.skip(f"Ollama 不可用：{exc}")
    assert dim > 0
    assert dim == s.embed_dim, f"维度 {dim} 与配置 {s.embed_dim} 不一致"


def test_end_to_end_retrieval_on_built_graph():
    """已构建库上的端到端检索（需先跑 build）。"""
    s = _settings()
    if not s.graph_path.exists():
        pytest.skip("图谱未构建，先运行 build")
    kb = P.load_kb(s)
    assert len(kb.chunks) > 1000
    assert kb.graph.entities

    async def run():
        return await kb.retrieve("维尔汀是谁", top_k=5)

    res = asyncio.run(run())
    assert res["seeds"], "实体链接零命中"
    assert res["evidence"], "无证据块返回"
    # 证据必须出自真实语料
    for ev in res["evidence"]:
        assert ev["chunk_id"] in kb.retriever.chunks
