"""RAG / GraphRAG 审计套件（2026-09-08）。

定位：本文件是**检验**而非功能测试——它把审计中确认的行为固化为可执行断言，
其中「已确认缺陷」用 ``xfail`` 标记（当前失败即为已知问题，修复后会自动转为 XPASS）。

- 通过项 = 当前正确实现的回归护栏；
- xfail 项 = 已复现的缺陷，reason 指向 ``deliverables/rag_graphrag_audit.md`` 编号。

运行：python -m pytest tests/test_rag_graphrag_audit.py -v
"""
from __future__ import annotations

import asyncio
import inspect
import json
import re
from pathlib import Path

import pytest

from roleplay.core.knowledge.embedder import HashingEmbedder
from roleplay.core.knowledge.graph_extract import GraphCache, build_graph_from_chunks, normalize_extraction
from roleplay.core.knowledge.graph_search import GraphSearcher
from roleplay.core.knowledge.graph_store import (
    GraphStore,
    build_local_endpoint_map,
    chunk_text_hash,
    entity_id,
    norm_name,
    resolve_endpoint,
)
from roleplay.core.knowledge.plot_corpus import PlotCorpus, plot_namespace
from roleplay.core.knowledge.plot_graph import (
    PlotGraphRegistry,
    PlotGraphRetriever,
    build_plot_graph,
    is_noise_entity,
)
from roleplay.core.knowledge.vector_store import KnowledgeBase, _BM25, _cosine, _tokenize
from roleplay.core.persona_prompt import (
    RELATIVE_SCORE_GATE,
    _filter_chunks,
    build_graph_context,
    build_plot_context,
    build_rag_context,
    build_roleplay_prompt,
    resolve_knowledge_namespaces,
)
from roleplay.core.rag.base import RetrievedChunk
from roleplay.models.character import CharacterCard

ROOT = Path(__file__).resolve().parent.parent


def _chunk(text: str, score: float, ns: str) -> RetrievedChunk:
    return RetrievedChunk(text=text, score=score, metadata={"namespace": ns})


def _trans_md(title: str, body: str) -> str:
    return (
        f"# {title}\n\n"
        "- 来源：B站 <https://www.bilibili.com/video/BV1AUDIT0001?p=1>\n"
        "- 提取方式：whisper语音转写（机器提取，可能存在少量识别误差）\n\n---\n\n" + body
    )


# ══════════════════════════════════════════════════════════════════════════════
# 一、通过项：当前实现的回归护栏
# ══════════════════════════════════════════════════════════════════════════════

def test_bm25_matches_reference_formula():
    """BM25 分数与 Okapi 公式手算一致（k1=1.5, b=0.75）。"""
    bm = _BM25(["a b c", "a a a", "x y z"])
    scores = bm.scores("a")
    # 手算：N=3，df(a)=2，idf=ln(1+(3-2+0.5)/(2+0.5))=ln(1.6)
    import math

    idf = math.log(1.6)
    avgdl = (3 + 3 + 3) / 3
    exp_doc0 = idf * (1 * 2.5) / (1 + 1.5 * (1 - 0.75 + 0.75 * 3 / avgdl))
    exp_doc1 = idf * (3 * 2.5) / (3 + 1.5 * (1 - 0.75 + 0.75 * 3 / avgdl))
    assert scores[0] == pytest.approx(exp_doc0)
    assert scores[1] == pytest.approx(exp_doc1)
    assert scores[2] == 0.0


def test_tokenize_splits_cjk_chars_and_latin_words():
    assert _tokenize("hello 世界") == ["hello", "世", "界"]
    assert _tokenize("GPT-4 模型") == ["gpt", "4", "模", "型"]


def test_kb_hybrid_rerank_promotes_keyword_hit():
    """混合重排能把含专名的目标块提到首位（稠密分被常见词带偏时）。"""
    kb = KnowledgeBase(HashingEmbedder(dim=512))
    kb.add(
        [
            "维尔汀的司辰徽章是反转者的信物。",
            "请解释一下含义，这个东西有什么用，它有什么意义，请解释一下。",
            "请解释一下含义，这个东西有什么用，它有什么意义，你说一下是什么意思。",
        ],
        namespace="lore_x",
    )
    q = "维尔汀的司辰徽章有什么含义？请解释一下。"
    assert "司辰徽章" not in kb.search(q, top_k=1, namespaces=["lore_x"], hybrid=False)[0].text
    assert "司辰徽章" in kb.search(
        q, top_k=1, namespaces=["lore_x"], hybrid=True, hybrid_alpha=0.7
    )[0].text


def test_kb_bm25_cache_invalidated_on_write():
    """写入后版本号递增、BM25 缓存失效，检索结果包含新条目。"""
    kb = KnowledgeBase(HashingEmbedder(dim=128))
    kb.add(["苹果 香蕉 橙子", "汽车 轮胎 发动机"], namespace="ns")
    kb.search("轮胎", top_k=2, namespaces=["ns"], hybrid=True, hybrid_alpha=0.9)
    v1 = kb._version
    kb.add(["轮胎 刹车片 机油"], namespace="ns")
    assert kb._version == v1 + 1
    hits = kb.search("轮胎", top_k=3, namespaces=["ns"], hybrid=True, hybrid_alpha=0.9)
    assert any("刹车片" in c.text for c in hits)


def test_kb_persist_roundtrip_and_meta(tmp_path):
    kb = KnowledgeBase(HashingEmbedder(dim=64), persist_dir=tmp_path / "kb")
    kb.add(["发条装置令大脑自动生成人格。"], namespace="lore_x")
    kb2 = KnowledgeBase(HashingEmbedder(dim=64), persist_dir=tmp_path / "kb")
    assert kb2.count()["lore_x"] == 1
    hits = kb2.search("发条装置", top_k=1, namespaces=["lore_x"])
    assert hits and "发条装置" in hits[0].text


def test_kb_load_ignores_graph_and_corpus_json(tmp_path):
    """同目录下的图谱/语料 JSON（dict 结构）不得被当成命名空间载入。"""
    d = tmp_path / "kb"
    d.mkdir(parents=True)
    (d / "lore_x.json").write_text(
        json.dumps([{"id": "lore_x-1", "text": "t", "vec": [1.0], "meta": {}, "ts": 1.0}]),
        encoding="utf-8",
    )
    (d / "plot_corpus_x.json").write_text(json.dumps({"schema": "plot-corpus-v1", "chunks": []}), encoding="utf-8")
    (d / "graph_x.json").write_text(json.dumps({"entities": {}, "edges": []}), encoding="utf-8")
    kb = KnowledgeBase(HashingEmbedder(dim=8), persist_dir=d)
    counts = kb.count()
    assert counts["lore_x"] == 1
    assert counts.get("plot_corpus_x", 0) == 0 and counts.get("graph_x", 0) == 0


def test_graph_store_edge_merge_and_dedup():
    """同 (src,dst,relation) 边合并：confidence 取 max、证据去重。"""
    st = GraphStore(":memory:", min_confidence=0.5)
    st.bind_alias_table({"A": [], "B": []})
    a, b = st.link_exact("A"), st.link_exact("B")
    ev1 = [{"ns": "n", "doc_id": "d1", "hash": "h1"}]
    ev2 = [{"ns": "n", "doc_id": "d1", "hash": "h1"}, {"ns": "n", "doc_id": "d2", "hash": "h2"}]
    assert st.upsert_edge(src=a, dst=b, relation="持有", confidence=0.7, evidence=ev1)
    assert st.upsert_edge(src=a, dst=b, relation="持有", confidence=0.9, evidence=ev2)
    edges = st.all_edges()
    assert len(edges) == 1
    assert edges[0]["confidence"] == 0.9
    assert sorted(x["hash"] for x in edges[0]["evidence"]) == ["h1", "h2"]
    # 低于 min_confidence 的边被拒绝
    assert not st.upsert_edge(src=b, dst=a, relation="弱", confidence=0.2)


def test_graph_store_roundtrip_and_atomic_save(tmp_path):
    p = tmp_path / "graph_x.json"
    st = GraphStore(p, min_confidence=0.5)
    st.bind_alias_table({"无名者": ["Ms. Stranger"]})
    e1, e2 = st.link_exact("无名者"), st.link_exact("Ms. Stranger")
    assert e1 == e2  # 别名归一到同一实体
    st.upsert_edge(src=e1, dst=entity_id("凯拉"), relation="失去", confidence=0.9,
                   evidence=[{"ns": "n", "doc_id": "d", "hash": "h"}])
    st.set_fingerprint(embedder="ollama:nomic-embed-text", embed_dim=768, extract_llm="m")
    st.save()
    assert not (tmp_path / "graph_x.tmp").exists()  # 原子写：无残留临时文件
    st2 = GraphStore(p, min_confidence=0.5)
    assert len(st2.all_edges()) == 1
    assert st2.check_fingerprint("ollama:nomic-embed-text", 768) is True
    assert st2.check_fingerprint("hashing", 64) is False


def test_graph_store_remove_by_doc_cleans_orphans():
    st = GraphStore(":memory:", min_confidence=0.5)
    st.bind_alias_table({"A": [], "B": []})
    a, b = st.link_exact("A"), st.link_exact("B")
    st.upsert_edge(src=a, dst=b, relation="r1", confidence=0.9,
                   evidence=[{"ns": "n", "doc_id": "d1", "hash": "h1"}])
    st.upsert_edge(src=a, dst=b, relation="r2", confidence=0.9,
                   evidence=[{"ns": "n", "doc_id": "d1", "hash": "h1"},
                             {"ns": "n", "doc_id": "d2", "hash": "h2"}])
    assert st.remove_by_doc("n", "d1") == 1
    remaining = st.all_edges()
    assert [e["relation"] for e in remaining] == ["r2"]
    assert [x["doc_id"] for x in remaining[0]["evidence"]] == ["d2"]


def test_plot_retriever_ppr_prefers_seed_neighbourhood(tmp_path):
    """PPR 激活：与种子直连的节点得分高于远端节点。"""
    root = tmp_path / "视频文案"
    root.mkdir(parents=True)
    for i in range(3):
        (root / f"BV1AUDIT000{i}_p1_x.md").write_text(
            _trans_md("x", f"凯拉在雨里死去。发条装置停在那一刻。第{i}段。"), encoding="utf-8"
        )
    corpus = PlotCorpus(tmp_path / "c.json", character_id="x")
    corpus.build(root, chunk_size=200)
    st = GraphStore(tmp_path / "g.json", min_confidence=0.5)
    st.bind_alias_table({"无名者": [], "凯拉": [], "发条装置": []})
    ev = [{"ns": "plot_x", "doc_id": "d", "hash": c.hash} for c in corpus.chunks]
    st.upsert_edge(src=st.link_exact("无名者"), dst=st.link_exact("凯拉"),
                   relation="失去", confidence=0.9, importance=0.6, evidence=ev)
    st.upsert_edge(src=st.link_exact("凯拉"), dst=st.link_exact("发条装置"),
                   relation="象征", confidence=0.9, importance=0.6, evidence=ev)
    retr = PlotGraphRetriever(corpus, st, namespace="plot_x", min_confidence=0.5,
                              include_weak=True)
    seeds = retr.link("无名者")
    ranks = retr._ppr(seeds)
    assert ranks[st.link_exact("凯拉")] > ranks[st.link_exact("发条装置")]


def test_plot_retriever_link_longest_match_and_word_boundary(tmp_path):
    st = GraphStore(":memory:", min_confidence=0.5)
    st.upsert_entities([{"name": "露西娅"}, {"name": "露西"}])
    corpus = PlotCorpus(tmp_path / "empty.json")
    retr = PlotGraphRetriever(corpus, st, namespace="plot_x")
    assert retr.link("露西娅在哪") == {st.link_exact("露西娅"): 1.0}
    # 拉丁名按词边界：ania 不得命中 mania
    st2 = GraphStore(":memory:", min_confidence=0.5)
    st2.upsert_entities([{"name": "Ania"}])
    retr2 = PlotGraphRetriever(corpus, st2, namespace="plot_x")
    assert retr2.link("mania") == {}


def test_plot_corpus_whitelist_rejects_manual_files(tmp_path):
    root = tmp_path / "lore" / "c"
    (root / "视频文案").mkdir(parents=True)
    (root / "视频文案" / "BV1AUDIT0001_p1_x.md").write_text(_trans_md("x", "正文。" * 50), encoding="utf-8")
    (root / "手工整理.md").write_text("# 手工\n内容", encoding="utf-8")
    (root / "视频文案" / "BV1FAKE0001_p1_y.md").write_text("# 伪造\n没有元数据头", encoding="utf-8")
    corpus = PlotCorpus(tmp_path / "c.json")
    stat = corpus.build(root / "视频文案", chunk_size=200)
    assert stat["kept"] == 1 and stat["rejected"] == 1


def test_noise_entity_filter_keeps_real_names():
    for bad in ["ma'am", "Senorita", "An exorcist", "the eyes hiding in the shadows", "A", ""]:
        assert is_noise_entity(bad), bad
    for good in ["Madam Lucy", "Ms. Stranger", "St. Pavlov Foundation", "无名者"]:
        assert not is_noise_entity(good), good


def test_graph_build_is_idempotent_via_cache(tmp_path):
    """同一 chunk 重跑走缓存，不再调用抽取器。"""
    root = tmp_path / "视频文案"
    root.mkdir(parents=True)
    (root / "BV1AUDIT0001_p1_x.md").write_text(_trans_md("x", "凯拉在雨里死去。" * 40), encoding="utf-8")
    corpus = PlotCorpus(tmp_path / "c.json", character_id="x")
    corpus.build(root, chunk_size=200)
    cache = GraphCache(tmp_path / "cache")

    class _Counting:
        def __init__(self) -> None:
            self.calls = 0

        async def extract(self, text, system=None):  # noqa: ANN001
            self.calls += 1
            return {"entities": [{"name": "凯拉", "aliases": []}], "relations": []}

    ex = _Counting()

    async def _run():
        st = GraphStore(tmp_path / "g.json", min_confidence=0.5)
        await build_plot_graph(corpus, st, ex, cache, namespace="plot_x")
        first = ex.calls
        st2 = GraphStore(tmp_path / "g2.json", min_confidence=0.5)
        stats2 = await build_plot_graph(corpus, st2, ex, cache, namespace="plot_x")
        return first, ex.calls, stats2

    first, total, stats2 = asyncio.run(_run())
    assert first == len(corpus.chunks) > 0
    assert total == first, "缓存命中后不应再调用抽取器"
    assert stats2["cached"] == len(corpus.chunks) and stats2["extracted"] == 0


def test_resolve_knowledge_namespaces_isolates_events():
    assert resolve_knowledge_namespaces(None) == ["events", "web", "episodic"]
    assert resolve_knowledge_namespaces(None, "c1") == ["events:c1", "web", "episodic"]
    card = CharacterCard(name="x", knowledge_scope=["lore_x", "events"])
    assert resolve_knowledge_namespaces(card, "c1") == ["lore_x", "events:c1"]


# ══════════════════════════════════════════════════════════════════════════════
# 二、缺陷修复回归（原为 xfail，修复后转为必过用例）
# ══════════════════════════════════════════════════════════════════════════════

def test_memory_survives_relative_gate_with_strong_lore_hits():
    """AUDIT-F1：相对门按分数尺度分组后，长期记忆不再被强 lore 命中整段丢弃。"""
    chunks = [
        _chunk("发条装置定义", 0.9688, "lore_wu_ming_zhe"),
        _chunk("凯拉之死", 0.9515, "lore_wu_ming_zhe"),
        _chunk("用户说自己最喜欢的颜色是克莱因蓝。", 0.6339, "events:wu_ming_zhe"),
    ]
    kept = _filter_chunks(chunks)
    assert any(c.metadata["namespace"].startswith("events") for c in kept), (
        "长期记忆条目应能与 lore 条目共存，而不是被相对门整段滤掉"
    )


def test_plot_graph_chunk_survives_lexical_fallback(tmp_path):
    """AUDIT-F2：图谱块不再被词法兜底的 BM25 原始分挤掉。

    - 默认 ``topup=False``：图谱命中即不触发词法兜底 → 无关噪声不注入；
    - 显式 ``topup=True``：两路同时在场时，分组相对门让图谱块保留。
    """
    root = tmp_path / "视频文案"
    root.mkdir(parents=True)
    # doc0 命中图谱证据；doc1 与查询词高度重合（词法兜底高分）
    (root / "BV1AUDIT0001_p1_x.md").write_text(_trans_md("x", "发条装置停在那一刻。"), encoding="utf-8")
    (root / "BV1AUDIT0002_p1_y.md").write_text(_trans_md("y", "天气天气天气天气天气天气天气。"), encoding="utf-8")
    corpus = PlotCorpus(tmp_path / "c.json", character_id="x")
    corpus.build(root, chunk_size=200)
    st = GraphStore(tmp_path / "g.json", min_confidence=0.5)
    st.bind_alias_table({"无名者": [], "发条装置": []})
    ev = [{"ns": "plot_x", "doc_id": "d", "hash": c.hash} for c in corpus.chunks]
    st.upsert_edge(src=st.link_exact("无名者"), dst=st.link_exact("发条装置"),
                   relation="持有", confidence=0.9, importance=0.6, evidence=ev)
    retr = PlotGraphRetriever(corpus, st, namespace="plot_x", min_confidence=0.5,
                              include_weak=True)

    # 默认：图谱命中 → 不触发词法兜底，图谱证据进入提示词
    out = retr.retrieve("无名者 天气", top_chunks=2, lexical_fallback=1)
    assert [c.metadata.get("via") for c in out] == ["plot_graph"]
    assert "发条装置停在那一刻" in build_plot_context(out, max_chars=1000)

    # 显式 topup：两路共存，图谱块仍能进入提示词（分组相对门）
    out2 = retr.retrieve("无名者 天气", top_chunks=2, lexical_fallback=1, topup=True)
    vias = {c.metadata.get("via") for c in out2}
    assert vias == {"plot_graph", "plot_lexical"}
    ctx2 = build_plot_context(out2, max_chars=1000)
    assert "发条装置停在那一刻" in ctx2, "图谱证据应能进入提示词，而不是被词法块的高分挤掉"


def test_lore_graph_search_is_wired_into_runtime():
    """AUDIT-F3：lore 图谱已接入在线链路（配置 + 注册表 + 编排器第三路 + CLI）。"""
    from roleplay.config import Settings
    from roleplay.core.knowledge.factory import build_graph_registry  # noqa: F401

    assert hasattr(Settings(), "graph_enabled"), "缺少 graph_enabled 总开关"
    assert Settings().graph_enabled is False, "默认必须关闭（零回归）"

    src_text = "\n".join(
        p.read_text(encoding="utf-8") for p in (ROOT / "src").rglob("*.py")
    )
    assert "GraphSearchRegistry(" in src_text, "src 内应构造 lore 图谱注册表"
    assert (ROOT / "scripts" / "build_graph.py").is_file(), "缺少离线构建 CLI"

    from roleplay.core.orchestrator import ChatOrchestrator

    assert hasattr(ChatOrchestrator, "_graph_retrieve"), "编排器应具备图谱第三路检索"


def test_relation_endpoint_resolves_within_chunk_entities():
    """AUDIT-F4：同 chunk 内别名歧义的关系被丢弃，不再挂到首注册实体上。"""
    entities, relations = normalize_extraction(
        {
            "entities": [
                {"name": "Madam Lucy", "aliases": ["露西"]},
                {"name": "Doris", "aliases": ["露西"]},
            ],
            "relations": [{"src": "露西", "dst": "Doris", "relation": "认识", "confidence": 0.9}],
        }
    )
    st = GraphStore(":memory:", min_confidence=0.5)
    st.upsert_entities(entities)
    local = build_local_endpoint_map(st, entities)
    assert local["露西"] is None, "同 chunk 内别名指向多个实体 → 标记为歧义"
    assert resolve_endpoint(st, local, "露西") is None, "歧义端点应解析为 None（丢弃该关系）"
    # 无歧义的端点仍正常解析
    assert resolve_endpoint(st, local, "Doris") == st.link_exact("Doris")
    assert resolve_endpoint(st, local, "Madam Lucy") == st.link_exact("Madam Lucy")


def test_build_graph_from_chunks_drops_ambiguous_relations(tmp_path):
    """AUDIT-F4（端到端）：歧义关系不落图，无歧义关系正常落图。"""
    from roleplay.core.knowledge.graph_extract import GraphCache, build_graph_from_chunks

    payload = {
        "entities": [
            {"name": "Madam Lucy", "aliases": ["露西"]},
            {"name": "Doris", "aliases": ["露西"]},
        ],
        "relations": [
            {"src": "露西", "dst": "Doris", "relation": "认识", "confidence": 0.9},
            {"src": "Doris", "dst": "Madam Lucy", "relation": "同伴", "confidence": 0.9},
        ],
    }

    class _Extractor:
        async def extract(self, text, system=None):  # noqa: ANN001
            return payload

    st = GraphStore(tmp_path / "g.json", min_confidence=0.5)
    stats = asyncio.run(
        build_graph_from_chunks(
            [("凯拉在雨里死去。", {"doc_id": "d1", "ns": "lore_x"})],
            st,
            _Extractor(),
            GraphCache(tmp_path / "cache"),
        )
    )
    assert stats["extracted"] == 1
    relations = {e["relation"] for e in st.all_edges()}
    assert "同伴" in relations, "无歧义关系应正常落图"
    assert "认识" not in relations, "歧义关系（src 与 dst 同属 Doris）应被丢弃"


def test_plot_registry_defaults_match_settings():
    """AUDIT-F6：注册表默认 include_weak 与 Settings 一致（否则图谱路被 99.7% 孤证边门控掉）。"""
    from roleplay.config import Settings

    default = inspect.signature(PlotGraphRegistry.__init__).parameters["include_weak"].default
    assert default == Settings().plot_include_weak


def test_rag_context_respects_budget_for_single_oversized_chunk():
    """AUDIT-F7：单块超预算时截断（与 build_plot_context 行为一致）。"""
    out = build_rag_context([_chunk("长" * 900, 0.9, "lore_x")], max_chars=200)
    body = out.splitlines()[-1]
    assert len(body) <= 200 + len("（角色设定资料）") + 1, f"单块正文 {len(body)} 字符未截断"
    assert body.endswith("…")


def test_cosine_rejects_dimension_mismatch():
    """AUDIT-F8：维度不一致返回 0（不再用截断点积/全范数给出伪分数）。"""
    assert _cosine([1.0, 0.0, 0.0], [1.0, 0.0, 0.0, 5.0, 5.0]) == 0.0


def test_hybrid_alpha_default_matches_settings():
    """AUDIT-F9：混合检索默认参数与 Settings 一致（调试接口 = 生产路径）。"""
    from roleplay.config import Settings

    s = Settings()
    params = inspect.signature(KnowledgeBase.search).parameters
    assert params["hybrid_alpha"].default == s.rag_hybrid_alpha
    assert params["candidate_mult"].default == s.rag_hybrid_candidates


def test_plot_registry_cache_key_normalized(tmp_path):
    """AUDIT-F10：character_id 含空白时也能清掉缓存条目。"""
    reg = PlotGraphRegistry(corpus_dir=tmp_path, graph_dir=tmp_path)
    reg._cache["x"] = (1.0, 1.0, object())  # 预置缓存
    assert reg.get(" x ") is None
    assert "x" not in reg._cache, "文件缺失时应清除该角色的缓存条目"


def test_new_entity_mentions_counts_first_occurrence():
    """AUDIT-F11：首现实体也计 1 次 mentions。"""
    st = GraphStore(":memory:", min_confidence=0.5)
    st.upsert_entities([{"name": "凯拉"}, {"name": "凯拉"}, {"name": "发条装置"}])
    mentions = {e["name"]: e["mentions"] for e in st.entities()}
    assert mentions == {"凯拉": 2, "发条装置": 1}


def test_no_duplicate_test_function_names():
    """AUDIT-F12：测试文件内不得重复定义同名测试函数（后者会静默覆盖前者）。"""
    dupes: list[str] = []
    for p in (ROOT / "tests").glob("test_*.py"):
        names = re.findall(r"^def (test_\w+)", p.read_text(encoding="utf-8"), re.M)
        seen: set[str] = set()
        for n in names:
            if n in seen:
                dupes.append(f"{p.name}::{n}")
            seen.add(n)
    assert not dupes, f"存在重复定义的测试函数（后者覆盖前者）：{dupes}"


def test_edge_evidence_order_is_deterministic():
    """AUDIT-F15：证据去重保序（旧实现用 set，代表证据块每次运行可能不同）。"""
    st = GraphStore(":memory:", min_confidence=0.5)
    st.bind_alias_table({"A": [], "B": []})
    a, b = st.link_exact("A"), st.link_exact("B")
    ev = [
        {"ns": "n", "doc_id": "d3", "hash": "h3"},
        {"ns": "n", "doc_id": "d1", "hash": "h1"},
        {"ns": "n", "doc_id": "d3", "hash": "h3"},  # 重复项
    ]
    st.upsert_edge(src=a, dst=b, relation="r", confidence=0.9, evidence=ev)
    assert [x["hash"] for x in st.all_edges()[0]["evidence"]] == ["h3", "h1"]


# ══════════════════════════════════════════════════════════════════════════════
# 三、lore 图谱（GraphRAG）新增能力的回归护栏
# ══════════════════════════════════════════════════════════════════════════════

def _graph_fixture(tmp_path):
    """小图谱：无名者 —持有→ 发条装置 ←象征— 凯拉，证据指向 KB 原文块。"""
    kb = KnowledgeBase(HashingEmbedder(dim=64), persist_dir=tmp_path / "kb")
    kb.add(
        ["发条装置停在那一刻，无名者的身份随之切换。", "凯拉在雨里死去。"],
        metadatas=[{"doc_id": "d1"}, {"doc_id": "d2"}],
        namespace="lore_x",
    )
    items = kb.list_items("lore_x")
    st = GraphStore(tmp_path / "graph_x.json", min_confidence=0.5)
    st.bind_alias_table({"无名者": ["Ms. Stranger"], "发条装置": [], "凯拉": ["Kayla"]})
    ev = [
        {"ns": "lore_x", "doc_id": "d1", "hash": chunk_text_hash(items[0]["text"])},
        {"ns": "lore_x", "doc_id": "d2", "hash": chunk_text_hash(items[1]["text"])},
    ]
    st.upsert_edge(src=st.link_exact("无名者"), dst=st.link_exact("发条装置"),
                   relation="持有", confidence=0.9, importance=0.7, evidence=ev)
    st.upsert_edge(src=st.link_exact("凯拉"), dst=st.link_exact("发条装置"),
                   relation="象征", confidence=0.9, importance=0.7, evidence=ev)
    return kb, st


def test_graph_searcher_links_and_resolves_evidence(tmp_path):
    """实体链接 → PPR → 证据回查：命中知识库原文块并带出关系行。"""
    kb, st = _graph_fixture(tmp_path)
    searcher = GraphSearcher(st, kb, namespace="graph_x", min_confidence=0.5, top_chunks=2)
    out = searcher.retrieve("发条装置是什么")
    assert out, "实体链接应命中并回查到证据块"
    assert all(c.metadata["namespace"] == "lore_x" for c in out)
    assert all(c.metadata["via"] == "graph" for c in out)
    assert any("持有" in (c.metadata.get("edge") or "") for c in out)
    # 别名同样可链接
    assert searcher.link("Kayla 怎么了") == searcher.link("凯拉怎么了")
    # 零命中查询 → 空（静默降级）
    assert searcher.retrieve("完全无关的词组xyz") == []


def test_graph_searcher_evidence_index_invalidates_on_kb_write(tmp_path):
    kb, st = _graph_fixture(tmp_path)
    searcher = GraphSearcher(st, kb, namespace="graph_x", min_confidence=0.5, top_chunks=2)
    assert searcher.retrieve("发条装置")
    v1 = searcher._evidence_index_version
    kb.add(["新块"], metadatas=[{"doc_id": "d3"}], namespace="lore_x")
    assert searcher.retrieve("发条装置")  # 触发重建
    assert searcher._evidence_index_version != v1


def test_graph_context_block_rendering():
    """【关系脉络】块：空结果零注入；有结果时带关系行且独立预算。"""
    assert build_graph_context([]) == ""
    chunks = [
        RetrievedChunk(
            text="发条装置停在那一刻。",
            score=0.2,
            metadata={"namespace": "graph_x", "via": "graph",
                      "edge": "无名者 —持有→ 发条装置"},
        )
    ]
    out = build_graph_context(chunks, max_chars=200)
    assert out.startswith("【关系脉络")
    assert "（关系脉络）发条装置停在那一刻。" in out
    assert "（关系）无名者 —持有→ 发条装置" in out
    # 独立预算：超长文本被截断
    long_chunk = [RetrievedChunk(text="长" * 900, score=0.2, metadata={"namespace": "graph_x"})]
    assert len(build_graph_context(long_chunk, max_chars=100).splitlines()[-1]) <= 101


def test_roleplay_prompt_includes_graph_block():
    chunks = [
        RetrievedChunk(text="发条装置停在那一刻。", score=0.2,
                       metadata={"namespace": "graph_x", "via": "graph",
                                 "edge": "无名者 —持有→ 发条装置"})
    ]
    base = build_roleplay_prompt(card_json=None, fallback_prompt="你是无名者。",
                                 default_card=None, message="发条装置呢", chunks=[], card=None)
    with_graph = build_roleplay_prompt(card_json=None, fallback_prompt="你是无名者。",
                                       default_card=None, message="发条装置呢", chunks=[],
                                       card=None, graph_chunks=chunks)
    assert "【关系脉络" not in base, "未提供图谱块时零注入"
    assert "【关系脉络" in with_graph and "发条装置停在那一刻。" in with_graph


def test_orchestrator_graph_path_off_by_default_and_optional():
    """图谱层开关语义：关闭 → 零成本空列表；开启 → 注入独立块，且不影响 lore 检索。"""
    from roleplay.core.emotion.detector import KeywordEmotionDetector
    from roleplay.core.llm.mock import MockLLMProvider
    from roleplay.core.orchestrator import ChatOrchestrator
    from roleplay.core.rag.memory import InMemoryVectorStore
    from roleplay.models.chat import ChatRequest

    chunk = RetrievedChunk(text="发条装置停在那一刻。", score=0.2,
                           metadata={"namespace": "graph_x", "via": "graph",
                                     "edge": "无名者 —持有→ 发条装置"})

    class _StubRegistry:
        def get(self, character_id):  # noqa: ANN001
            return self

        def retrieve(self, query: str):  # noqa: ANN001
            return [chunk]

    def _orch(enabled: bool) -> ChatOrchestrator:
        return ChatOrchestrator(
            llm=MockLLMProvider(),
            emotion=KeywordEmotionDetector(enabled=True),
            rag=InMemoryVectorStore(),
            knowledge_base=None,
            graph_registry=_StubRegistry(),
            graph_enabled=enabled,
        )

    req = ChatRequest(session_id="s1", message="发条装置是什么", character_id="x")
    off = asyncio.run(_orch(False)._graph_retrieve("发条装置是什么", "x"))
    on = asyncio.run(_orch(True)._graph_retrieve("发条装置是什么", "x"))
    assert off == []
    assert on == [chunk]
    prompt, _, _ = asyncio.run(_orch(True)._prepare(req))
    assert "【关系脉络" in prompt
