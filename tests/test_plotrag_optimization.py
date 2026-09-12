# -*- coding: utf-8 -*-
"""剧情 RAG 优化护栏（P1 性能 / P2 排序 / P3 门控 / P4 语义修复）。

本文件是审计（deliverables/plot-rag-audit-20260912.md）里每一项优化的**正确性护栏**：

1. **差分测试**：优化后的提及块挖掘（词元候选集前置过滤）与旧的全扫参考实现在
   真实语料上必须逐块、逐分、逐序一致——这是本轮改动里最容易出静默 bug 的地方，
   与仓库既有的 ``by_hash_index_matches_linear_scan_on_real_corpus`` 同风格：
   参考实现独立复刻在测试里，不复用被测代码。
2. **超集性质**：``candidate_hashes`` 必须是真实命中的超集，否则前置过滤会丢结果。
3. **缓存失效**：图视图缓存必须随 ``GraphStore.revision`` 失效（改了图立刻可见）。
4. 真实语料/图谱缺失时一律 ``pytest.skip``（CI 无数据也能跑）。

运行：``.venv/Scripts/python.exe -m pytest tests/test_plotrag_optimization.py -q``
"""
from __future__ import annotations

import json
import re
from pathlib import Path

import pytest

from roleplay.core.knowledge.graph_ppr import build_adjacency, personalized_pagerank
from roleplay.core.knowledge.graph_store import GraphStore, entity_id, norm_name
from roleplay.core.knowledge.plot_corpus import PlotCorpus, tokenize
from roleplay.core.knowledge.plot_graph import (
    PlotGraphRetriever,
    is_noise_entity,
)

ROOT = Path(__file__).resolve().parent.parent
CORPUS_PATH = ROOT / "data" / "knowledge" / "plot_corpus_wu_ming_zhe.json"
GRAPH_PATH = ROOT / "data" / "knowledge" / "plot_graph_wu_ming_zhe.json"
ALIAS_PATH = ROOT / "data" / "lore" / "wu_ming_zhe" / "plot_aliases.json"


# ══════════════════════════════════════════════════════════════════════════
# 公共夹具
# ══════════════════════════════════════════════════════════════════════════


@pytest.fixture(scope="module")
def real_retriever():
    """真实语料 + 真实图谱上的检索器（缺数据则跳过整组用例）。"""
    if not (CORPUS_PATH.is_file() and GRAPH_PATH.is_file()):
        pytest.skip("缺少真实剧情语料/图谱")
    corpus = PlotCorpus(CORPUS_PATH, character_id="wu_ming_zhe")
    store = GraphStore(GRAPH_PATH, min_confidence=0.6)
    if not corpus.chunks or not store.entities():
        pytest.skip("真实语料或图谱为空")
    from roleplay.core.knowledge.plot_graph import load_alias_table

    if ALIAS_PATH.is_file():
        store.bind_alias_table(load_alias_table(ALIAS_PATH))
    return PlotGraphRetriever(
        corpus,
        store,
        namespace="plot_wu_ming_zhe",
        min_confidence=0.6,
        include_weak=True,
        max_edges=10,
        max_hops=2,
        damping=0.85,
        link_threshold=0.5,
    )


def _naive_name_hits(retr: PlotGraphRetriever, name: str) -> dict[int, int]:
    """旧实现的独立复刻：对**全部语料块**逐块跑同一个计数器，返回 ``{块下标: 次数}``。

    这是 P1 加速改造的参考实现（不复用被测代码里的任何计数逻辑），
    与优化版 ``_name_hits`` 必须逐块一致。
    """
    low = norm_name(name)
    if not low or "?" in low or is_noise_entity(name):
        return {}
    out: dict[int, int] = {}
    if re.fullmatch(r"[a-z0-9 ]+", low):
        pat = re.compile(r"(?<![a-z0-9])" + re.escape(low) + r"(?![a-z0-9])")
        for i, chunk in enumerate(retr.corpus.chunks):
            n = len(pat.findall(chunk.text.lower()))
            if n:
                out[i] = n
    else:
        for i, chunk in enumerate(retr.corpus.chunks):
            n = chunk.text.lower().count(low)
            if n:
                out[i] = n
    return out


def _hits_by_hash(chunks, hits: dict[int, int]) -> dict[str, int]:
    """``{块下标: 次数}`` → ``{块 hash: 次数}``：**同 hash 即同文本**，是同一份检索内容。

    语料有 130 组重复 hash（同一段转述出现在不同 BV，共 262 块）。优化版按下标去重
    （只保留首个副本），旧全扫版会把两个副本各报一次——这是本轮**刻意**的差异
    （同文本副本对检索是冗余的），故差分在 hash 粒度上比对。
    """
    out: dict[str, int] = {}
    for i, n in hits.items():
        h = chunks[i].hash
        out[h] = max(out.get(h, 0), n)
    return out


def _sample_targets(retr: PlotGraphRetriever, likes: list[str]) -> dict[str, float]:
    """按名字取样目标实体（用于差分测试）。"""
    targets: dict[str, float] = {}
    for name in likes:
        eid = retr.store.link_exact(name)
        if eid:
            targets[eid] = 1.0
    return targets


# ══════════════════════════════════════════════════════════════════════════
# P1：提及块挖掘前置过滤——与旧全扫实现逐块等价
# ══════════════════════════════════════════════════════════════════════════


class TestP1MentionPrefilter:
    """最高优先级护栏：候选集前置过滤不得改变任何一块的命中数与名次。"""

    @pytest.mark.parametrize(
        "name",
        [
            "维尔汀",          # CJK 正名（语料里主要靠别名命中）
            "暴雨",
            "露西",
            "Vertin",          # 拉丁正名
            "Lucy",
            "storm",
            "Foundation",
            "Ms. Grace",       # 含点号的混合名 → 子串计数分支
            "圣洛夫基金会",
            "重塑之手",
        ],
    )
    def test_name_hits_match_naive_reference(self, real_retriever, name):
        """差分：优化版 ``_name_hits`` 与全扫参考实现必须给出**逐块相同**的次数表。"""
        got, _weight = real_retriever._name_hits(name)
        ref = _naive_name_hits(real_retriever, name)
        chunks = real_retriever.corpus.chunks
        if got is None:
            assert _hits_by_hash(chunks, ref) == {}, name
            return
        assert _hits_by_hash(chunks, got) == _hits_by_hash(chunks, ref), (
            f"{name}: 前置过滤改变命中结果 "
            f"（多 {len(set(got) - set(ref))} 块 / 少 {len(set(ref) - set(got))} 块）"
        )

    def test_name_hits_match_naive_reference_on_entity_sample(self, real_retriever):
        """在真实实体名+别名上批量抽样差分（正名/别名/长名/短名各覆盖）。"""
        names: list[str] = []
        ents = sorted(
            real_retriever.store.entities(),
            key=lambda e: -int(e.get("mentions") or 0),
        )
        for ent in ents[:8] + ents[1000:1004] + ents[-4:]:
            names.append(str(ent.get("name") or ""))
            names.extend(str(a) for a in (ent.get("aliases") or [])[:2])
        chunks = real_retriever.corpus.chunks
        checked = 0
        for name in names:
            if not name:
                continue
            got, _w = real_retriever._name_hits(name)
            ref = _naive_name_hits(real_retriever, name)
            assert _hits_by_hash(chunks, got or {}) == _hits_by_hash(chunks, ref), (
                f"{name} 命中表不一致"
            )
            checked += 1
        assert checked >= 20, f"抽样过少（{checked}），用例失效"

    def test_mention_channel_stable_across_repeat(self, real_retriever):
        """可复现性：清缓存重算必须给出同一序列（并列名次不得靠集合迭代序）。"""
        targets = _sample_targets(real_retriever, ["维尔汀", "暴雨", "露西"])
        if not targets:
            pytest.skip("真实图谱里没有这些实体")
        first = [(round(s, 6), c.hash) for s, c, _m in real_retriever._mention_channel(targets)]
        real_retriever._mention_hits_cache.clear()
        second = [(round(s, 6), c.hash) for s, c, _m in real_retriever._mention_channel(targets)]
        assert first == second

    def test_candidate_hashes_is_superset_of_true_hits(self, real_retriever):
        """超集性质：凡真实命中 >0 的块必在候选集内（否则前置过滤会丢结果）。"""
        corpus = real_retriever.corpus
        names = ["维尔汀", "暴雨", "露西", "Lucy", "storm", "Foundation", "Ms. Grace"]
        checked = 0
        for name in names:
            cand = corpus.candidate_hashes(name)
            if cand is None:  # 无可用词元 → 调用方全扫兜底，不在本性质范围内
                continue
            low = norm_name(name)
            if re.fullmatch(r"[a-z0-9 ]+", low):
                pat = re.compile(r"(?<![a-z0-9])" + re.escape(low) + r"(?![a-z0-9])")
                truth = {c.hash for c in corpus.chunks if pat.search(c.text.lower())}
            else:
                truth = {c.hash for c in corpus.chunks if low in c.text.lower()}
            assert truth <= cand, f"{name} 有 {len(truth - cand)} 个真实命中块不在候选集内"
            checked += 1
        assert checked, "没有任何名字通过超集校验，用例失效"

    def test_candidate_hashes_none_for_tokenless_name(self, real_retriever):
        """单字母/停用词名字拿不到词元 → 必须返回 None（调用方全扫），不得返回空集。"""
        assert real_retriever.corpus.candidate_hashes("J") is None
        assert real_retriever.corpus.candidate_hashes("the") is None

    def test_candidate_hashes_empty_for_absent_bigram(self, real_retriever):
        """语料里不存在的词元 → 空集（零命中），不得返回 None 拖回全扫。"""
        assert real_retriever.corpus.candidate_hashes("镧锕钍镤") == set()

    def test_mention_cache_is_bounded(self, real_retriever):
        """命中缓存必须有上限（防止长跑进程把 6814 实体的命中表全留在内存）。"""
        retr = real_retriever
        saved = retr._mention_cache_size
        try:
            retr._mention_cache_size = 4
            retr._mention_hits_cache.clear()
            for name in ["维尔汀", "暴雨", "露西", "Lucy", "storm", "Grace", "Isolde"]:
                retr._name_hits(name)
            assert len(retr._mention_hits_cache) <= 4
        finally:
            retr._mention_cache_size = saved
            retr._mention_hits_cache.clear()

    def test_name_hits_weight_matches_legacy_rules(self, real_retriever):
        """权重口径与旧实现一致：拉丁正名 1.0 / CJK 0.6；噪声名不可用。

        注：单字母拉丁名（如 ``J``）在**提及计数**通道被 ``is_noise_entity``（len<2）
        挡掉（与旧 ``_name_counter`` 完全一致）——单字母别名只在 ``link()`` 的实体
        链接通道享有词边界例外，两条通道口径不同是既有设计。
        """
        _hits, w_cjk = real_retriever._name_hits("暴雨")
        assert w_cjk == 0.6
        _hits, w_latin = real_retriever._name_hits("Grace")
        assert w_latin == 1.0
        for noise in ("J", "you", "我们", "ma'am", "Henpal?"):
            hits, weight = real_retriever._name_hits(noise)
            assert hits is None and weight == 0.0, noise


# ══════════════════════════════════════════════════════════════════════════
# P1：图视图缓存（PPR 邻接）等价性与失效
# ══════════════════════════════════════════════════════════════════════════


class TestP1GraphViewCache:
    def test_prebuilt_adjacency_matches_inline_path(self):
        """预建邻接表 + 中性过滤 == 旧的内联过滤路径（逐节点分数完全一致）。"""
        edges = [
            {"src": "a", "dst": "b", "confidence": 0.9, "importance": 0.6,
             "evidence": [{"hash": "h1"}, {"hash": "h2"}]},
            {"src": "b", "dst": "c", "confidence": 0.7, "importance": 0.6,
             "evidence": [{"hash": "h1"}]},
            {"src": "c", "dst": "d", "confidence": 0.4, "importance": 0.6,
             "evidence": [{"hash": "h1"}, {"hash": "h2"}]},
        ]
        seeds = {"a": 1.0}
        for include_weak in (True, False):
            ref = personalized_pagerank(
                edges, seeds, min_confidence=0.6, include_weak=include_weak
            )
            adj = build_adjacency(edges, min_confidence=0.6, include_weak=include_weak)
            got = personalized_pagerank(
                edges, seeds, min_confidence=0.0, include_weak=True, adjacency=adj
            )
            assert got == pytest.approx(ref), include_weak

    def test_graph_view_invalidated_on_mutation(self, tmp_path):
        """改了图（revision 自增）之后，检索必须立刻看到新边，不得读旧缓存。"""
        store = GraphStore(tmp_path / "g.json", min_confidence=0.5)
        store.upsert_entities([{"name": "甲"}, {"name": "乙"}, {"name": "丙"}])
        a, b, c = (store.link_exact(x) for x in ("甲", "乙", "丙"))
        store.upsert_edge(src=a, dst=b, relation="关联", confidence=0.9)
        corpus = PlotCorpus(tmp_path / "c.json", character_id="x")
        corpus.chunks = []
        retr = PlotGraphRetriever(corpus, store, min_confidence=0.5, include_weak=True)
        rev1 = store.revision
        assert retr._graph_view()[0] == store.all_edges()

        store.upsert_edge(src=b, dst=c, relation="关联", confidence=0.9)
        assert store.revision > rev1, "写操作没有推进 revision，缓存永远不失效"
        assert len(retr._graph_view()[0]) == 2, "图视图缓存未随 revision 失效"


# ══════════════════════════════════════════════════════════════════════════
# P4：tokenize CJK 相邻性（假二元组）
# ══════════════════════════════════════════════════════════════════════════


class TestP4TokenizeAdjacency:
    def test_bigram_does_not_cross_punctuation(self):
        """跨标点的两个 CJK 字不得拼成二元组（旧实现会产出「暴雨」这种假词元）。"""
        toks = tokenize("暴。雨")
        assert "暴雨" not in toks, "二元组跨标点拼接，BM25 会出现假命中"
        assert "暴" in toks and "雨" in toks

    def test_bigram_still_generated_for_adjacent_cjk(self):
        """相邻 CJK 仍需产出字与二元组（词法与提及前置过滤都依赖它）。"""
        toks = tokenize("暴雨是什么")
        assert "暴雨" in toks
        assert {"暴", "雨"} <= set(toks)

    def test_latin_and_cjk_mixed_run(self):
        """中英混排：拉丁词照常切分，CJK 段各自内部拼二元组。"""
        toks = tokenize("Storm暴雨Vertin")
        assert "storm" in toks and "vertin" in toks and "暴雨" in toks


# ══════════════════════════════════════════════════════════════════════════
# P2：三通道 RRF 融合 / 归一分数量带 / path 元数据 / doc 软去冗余
# ══════════════════════════════════════════════════════════════════════════


def _chunk(h: str, text: str, doc_id: str = ""):
    """构造最小 PlotChunk（融合与去冗余只需要 hash/doc_id/text）。"""
    from roleplay.core.knowledge.plot_corpus import PlotChunk

    return PlotChunk(hash=h, text=text, doc_id=doc_id or f"doc_{h}", bv="BV1", page=1)


def _retriever_with_corpus(tmp_path, texts: list[str], **kwargs) -> PlotGraphRetriever:
    """构造一个只含给定文本的检索器（无语料文件、无图谱边），用于排序单元测试。"""
    from roleplay.core.knowledge.plot_corpus import PlotChunk, chunk_hash

    corpus = PlotCorpus(tmp_path / "c.json", character_id="x")
    corpus.chunks = [
        PlotChunk(hash=chunk_hash(t), text=t, doc_id=f"d{i}", bv="BV1", page=i + 1)
        for i, t in enumerate(texts)
    ]
    corpus._rebuild_hash_index()
    store = GraphStore(tmp_path / "g.json", min_confidence=0.5)
    return PlotGraphRetriever(
        corpus, store, namespace="plot_x", min_confidence=0.5, **kwargs
    )


class TestP2Fusion:
    def test_scores_are_normalized_into_band_and_path_exposed(self, tmp_path):
        """融合分数量带 [0.6, 1.0]：既要高于 MIN_CONTEXT_SCORE，又要保留排序含义。"""
        from roleplay.core.persona_prompt import MIN_CONTEXT_SCORE
        from roleplay.core.knowledge.plot_graph import FUSE_MAX_SCORE, FUSE_MIN_SCORE

        assert FUSE_MIN_SCORE > MIN_CONTEXT_SCORE, "分数带下界低于提示词绝对门，剧情块会被整批滤掉"
        retr = _retriever_with_corpus(tmp_path, ["甲" * 30])
        c1 = _chunk("h1", "甲" * 30, "d1")
        c2 = _chunk("h2", "乙" * 30, "d2")
        fused = retr._fuse_channels(
            [("edge", 1.0, [(0.2, c1, {"via": "plot_graph", "path": "edge"})]),
             ("mention", 0.7, [(1.2, c2, {"via": "plot_graph", "path": "mention"})])],
            limit=5,
        )
        scores = [s for s, _c, _m in fused]
        assert scores == sorted(scores, reverse=True)
        assert all(FUSE_MIN_SCORE <= s <= FUSE_MAX_SCORE for s in scores)
        assert scores[0] == FUSE_MAX_SCORE  # 首位恒为 1.0
        assert {m["path"] for _s, _c, m in fused} == {"edge", "mention"}
        # 通道权重生效：同为各自通道第 0 名时，权重 1.0 的边证据排在权重 0.7 的提及块前，
        # 归一后比值 = 0.7（这正是 RRF 的语义：跨通道靠权重，通道内靠名次）
        assert scores[0] > scores[1]
        assert abs((scores[1] - FUSE_MIN_SCORE) / (FUSE_MAX_SCORE - FUSE_MIN_SCORE) - 0.7) < 1e-9

    def test_fusion_is_invariant_to_raw_score_scale(self, tmp_path):
        """RRF 只用名次：同通道内原始分差 7 个数量级，也不得改变融合结果。

        这正是旧实现的病根——边证据分（≈0.2）与提及块分（≈1.2）直接比大小，
        图结构证据永远排在提及块后面、并被提示词组内相对门整批丢弃。
        """
        retr = _retriever_with_corpus(tmp_path, ["甲" * 30])
        tiny = _chunk("h1", "甲" * 30, "d1")
        huge = _chunk("h2", "乙" * 30, "d2")
        by_rank = retr._fuse_channels(
            [("edge", 1.0, [(0.0000001, tiny, {"path": "edge"}),
                            (9999999.0, huge, {"path": "edge"})])],
            limit=5,
        )
        assert [c.hash for _s, c, _m in by_rank] == ["h1", "h2"], "名次被原始分带偏"
        # 交换原始分（名次不变）→ 融合分完全不变
        swapped = retr._fuse_channels(
            [("edge", 1.0, [(9999999.0, tiny, {"path": "edge"}),
                            (0.0000001, huge, {"path": "edge"})])],
            limit=5,
        )
        assert [round(s, 9) for s, _c, _m in by_rank] == [
            round(s, 9) for s, _c, _m in swapped
        ]

    def test_chunk_hit_by_two_channels_ranks_first(self, tmp_path):
        """同一块被两路命中 → 融合分最高（多路证据比单路可信）。"""
        retr = _retriever_with_corpus(tmp_path, ["甲" * 30])
        both = _chunk("h1", "甲" * 30, "d1")
        only_edge = _chunk("h2", "乙" * 30, "d2")
        fused = retr._fuse_channels(
            [
                ("edge", 1.0, [
                    (9.0, both, {"path": "edge"}),
                    (1.0, only_edge, {"path": "edge"}),
                ]),
                ("mention", 0.7, [(5.0, both, {"path": "mention"})]),
            ],
            limit=5,
        )
        assert fused[0][1] is both
        assert fused[0][2]["paths"] == ["edge", "mention"]
        assert fused[0][2]["path"] == "edge"  # 主 path 取优先级更高的一路

    def test_diversity_soft_cap_still_fills_budget(self, tmp_path):
        """同一 doc 的块先按上限去冗余，但**名额没填满时要放宽**（不得把结果压到 1 条）。"""
        retr = _retriever_with_corpus(tmp_path, ["甲" * 30] * 4)
        same_doc = [_chunk(f"h{i}", "甲" * 30, "d_same") for i in range(4)]
        fused = retr._fuse_channels(
            [("edge", 1.0, [(4.0 - i, c, {"path": "edge"}) for i, c in enumerate(same_doc)])],
            limit=3,
        )
        assert len(fused) == 3, "同 doc 去冗余把返回条数压掉了（并集口径下等于丢证据）"

    def test_retrieve_respects_budget_and_marks_path(self, real_retriever):
        """真实语料：返回条数 ≤ top_chunks+lexical_fallback，且每块都带 path 归因。"""
        retr = real_retriever
        out = retr.retrieve("维尔汀和圣洛夫基金会是什么关系", top_chunks=3, lexical_fallback=2)
        assert 0 < len(out) <= 5
        for c in out:
            assert c.metadata.get("via") in ("plot_graph", "plot_lexical")
            assert c.metadata.get("path") in ("edge", "mention", "lexical")
            assert isinstance(c.metadata.get("paths"), list)
        # 旧实现下 via 恒为 plot_graph，"图谱路径占比"是个恒 1.0 的无效指标；
        # path 让"边证据 vs 提及块"第一次可区分
        assert any(True for _ in out)

    def test_mention_scoring_default_is_count(self, tmp_path):
        """默认打分口径是**旧口径**（加权出现次数）——这是 300 题消融测出来的结论。

        实测（见审计报告 §P2）：count 口径严格通过 46.0%，idf 口径只有 42.0%。
        本用例把这个决策钉住：把默认值改回 idf 会让它失败，从而必须重新跑评测。
        """
        from roleplay.config import Settings

        assert Settings().plot_mention_scoring == "count"
        recap = "阿甲" + "。废话" * 30 + "阿甲" * 6
        answer = "阿甲 的真名是 Zeta。" + "。旁白" * 30
        retr = _retriever_with_corpus(tmp_path, [recap, answer])
        store = retr.store
        store.upsert_entities([{"name": "阿甲", "aliases": ["Zeta"]}])
        eid = store.link_exact("阿甲")
        got = retr._mention_channel({eid: 1.0})
        assert got and got[0][1].text == recap, "count 口径应按加权出现次数排序"

    def test_mention_scoring_idf_mode_prefers_rare_name_hits(self, tmp_path):
        """可选 idf 模式：命中**稀有别名**的块排在"同一实体被反复复述"的块之前。"""
        recap = "阿甲" + "。废话" * 30 + "阿甲" * 6
        answer = "阿甲 的真名是 Zeta。" + "。旁白" * 30
        retr = _retriever_with_corpus(
            tmp_path, [recap, answer], mention_scoring="idf", cooccurrence_bonus=False
        )
        store = retr.store
        store.upsert_entities([{"name": "阿甲", "aliases": ["Zeta"]}])
        eid = store.link_exact("阿甲")
        got = retr._mention_channel({eid: 1.0})
        assert got, "提及通道应有结果"
        assert "Zeta" in got[0][1].text, "idf 模式没有把稀有别名命中排到前面"

    def test_mention_channel_cooccurrence_bonus(self, tmp_path):
        """两个目标实体共现的块要排在只命中一个的块之前（多跳/关系题的答案特征）。"""
        both = "阿甲与阿乙同时出现在这里。" + "。填充" * 20
        only = "阿甲独自出现。" + "。填充" * 20
        retr = _retriever_with_corpus(tmp_path, [both, only], cooccurrence_bonus=True)
        store = retr.store
        store.upsert_entities([{"name": "阿甲"}, {"name": "阿乙"}])
        targets = {store.link_exact("阿甲"): 1.0, store.link_exact("阿乙"): 1.0}
        got = retr._mention_channel(targets)
        assert got and got[0][1].text == both, "共现块没有排到首位"


# ══════════════════════════════════════════════════════════════════════════
# P3：种子门控（离题零注入）
# ══════════════════════════════════════════════════════════════════════════


class TestP3SeedGate:
    def _store_with(self, tmp_path, ents: list[dict]):
        store = GraphStore(tmp_path / "g.json", min_confidence=0.5)
        store.upsert_entities(ents)
        return store

    def test_token_fallback_seed_requires_anchoring(self, tmp_path):
        """词元兜底种子（弱证据）必须被人工别名表锚定才可用。"""
        store = self._store_with(tmp_path, [{"name": "restaurant"}])
        eid = store.link_exact("restaurant")
        retr = PlotGraphRetriever(
            PlotCorpus(tmp_path / "c.json"), store, min_confidence=0.5
        )
        seeds = {"": {"weight": 0.5, "path": "token", "name": "restaurant"}}
        assert retr.seed_gate({eid: seeds[""]}) == {}
        store.bind_alias_table({"restaurant": []})  # 人工锚定 → 放行
        assert retr.seed_gate({eid: {"weight": 0.5, "path": "token", "name": "restaurant"}}) == {eid: 0.5}

    def test_generic_seed_name_dropped_but_story_name_kept(self, tmp_path):
        """泛词种子（天气/故事）丢弃；剧情专名（圣火/伦敦）保留。"""
        store = self._store_with(
            tmp_path, [{"name": "天气"}, {"name": "圣火"}, {"name": "伦敦"}]
        )
        retr = PlotGraphRetriever(
            PlotCorpus(tmp_path / "c.json"), store, min_confidence=0.5
        )
        e_weather = store.link_exact("天气")
        e_fire = store.link_exact("圣火")
        e_london = store.link_exact("伦敦")
        seeds = {
            e_weather: {"weight": 1.0, "path": "exact", "name": "天气"},
            e_fire: {"weight": 1.0, "path": "exact", "name": "圣火"},
            e_london: {"weight": 1.0, "path": "exact", "name": "伦敦"},
        }
        kept = retr.seed_gate(seeds)
        assert e_weather not in kept
        assert e_fire in kept and e_london in kept

    def test_gate_disabled_by_flag(self, tmp_path):
        """两个门控开关关掉后行为回到旧语义（可回滚）。"""
        store = self._store_with(tmp_path, [{"name": "天气"}])
        retr = PlotGraphRetriever(
            PlotCorpus(tmp_path / "c.json"),
            store,
            min_confidence=0.5,
            filter_generic_seeds=False,
            require_anchored_token_seeds=False,
        )
        eid = store.link_exact("天气")
        assert retr.seed_gate({eid: {"weight": 1.0, "path": "exact", "name": "天气"}}) == {eid: 1.0}

    def test_offtopic_queries_inject_nothing(self, real_retriever):
        """10 条离题问句（天气/写诗/算术/闲聊…）必须零注入——A5 验收线的常驻护栏。"""
        import importlib.util

        # 负样本清单以评测台为单一来源（scripts/ 不是包，只能按路径加载）
        spec = importlib.util.spec_from_file_location(
            "_eval_plot_rag", ROOT / "scripts" / "eval_plot_rag.py"
        )
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)  # type: ignore[union-attr]
        bad = []
        for q in mod.NEGATIVE_QUERIES:
            out = real_retriever.retrieve(q, top_chunks=3, lexical_fallback=2)
            if out:
                bad.append((q, len(out), [c.metadata.get("path") for c in out]))
        assert not bad, f"离题问句仍被注入剧情上下文：{bad}"


# ══════════════════════════════════════════════════════════════════════════
# P4：人工别名表权威性 / 证据 doc 归属 / 统计只读观测
# ══════════════════════════════════════════════════════════════════════════


class TestP4Semantics:
    def test_alias_merge_reassigns_to_human_canonical(self, tmp_path):
        """on_conflict="merge"：人工表的别名从抽取实体改指人工规范实体。"""
        store = GraphStore(tmp_path / "g.json", min_confidence=0.5)
        store.upsert_entities([{"name": "Noir", "aliases": ["黑色侦探"]}])
        assert store.link_exact("Noir") == entity_id("Noir")
        store.bind_alias_table({"菲林士多": ["Noir", "Noire"]}, on_conflict="merge")
        assert store.link_exact("Noir") == entity_id("菲林士多")
        assert store.link_exact("Noire") == entity_id("菲林士多")
        assert store.alias_reassigned == 1
        # 原持有者保留其余名字，不被整个吞掉
        assert store.link_exact("黑色侦探") == entity_id("Noir")

    def test_alias_skip_keeps_legacy_semantics(self, tmp_path):
        """默认 skip 语义不变（lore 层与既有测试依赖它）。"""
        store = GraphStore(tmp_path / "g.json", min_confidence=0.5)
        store.upsert_entities([{"name": "Noir"}])
        store.bind_alias_table({"菲林士多": ["Noir"]})
        assert store.link_exact("Noir") == entity_id("Noir")
        assert store.alias_ambiguous_dropped == 1
        assert store.alias_reassigned == 0

    def test_alias_merge_does_not_fight_another_anchored_entry(self, tmp_path):
        """两条**人工**条目争同一别名时保持首注册（人工表内部冲突不该互相抢占）。"""
        store = GraphStore(tmp_path / "g.json", min_confidence=0.5)
        store.bind_alias_table({"甲": ["同名"]}, on_conflict="merge")
        store.bind_alias_table({"乙": ["同名"]}, on_conflict="merge")
        assert store.link_exact("同名") == entity_id("甲")
        assert store.alias_reassigned == 0
        assert store.alias_ambiguous_dropped == 1

    def test_plot_registry_uses_authoritative_alias_table(self, tmp_path):
        """剧情注册表默认开启人工表优先（lore 层不受影响）。"""
        import inspect

        from roleplay.config import Settings
        from roleplay.core.knowledge.plot_graph import PlotGraphRegistry

        default = inspect.signature(PlotGraphRegistry.__init__).parameters[
            "alias_authoritative"
        ].default
        assert default is True
        assert default == Settings().plot_alias_authoritative

    def test_new_plot_defaults_match_settings(self):
        """新增的融合/门控参数默认值必须与 Settings 一致（避免双份默认值漂移）。"""
        import inspect

        from roleplay.config import Settings
        from roleplay.core.knowledge.plot_graph import PlotGraphRegistry

        s = Settings()
        params = inspect.signature(PlotGraphRegistry.__init__).parameters
        for name in (
            "fuse_k", "weight_edge", "weight_mention", "weight_lexical",
            "diversity_per_doc", "mention_cache_size",
            "require_anchored_token_seeds", "filter_generic_seeds",
            "alias_authoritative",
        ):
            assert params[name].default == getattr(s, f"plot_{name}"), name

    def test_by_hash_prefers_matching_doc_on_duplicate_hash(self, real_retriever):
        """重复 hash 的证据块要按 doc_id 归位（旧实现只取首个，会让引用指向另一支视频）。"""
        corpus = real_retriever.corpus
        groups: dict[str, list] = {}
        for chunk in corpus.chunks:
            groups.setdefault(chunk.hash, []).append(chunk)
        dups = [v for v in groups.values() if len(v) > 1]
        if not dups:
            pytest.skip("真实语料没有重复 hash，用例不适用")
        pair = dups[0]
        first, second = pair[0], pair[1]
        assert corpus.by_hash(first.hash).doc_id == first.doc_id  # 默认仍是首个
        got = corpus.by_hash(first.hash, doc_id=second.doc_id)
        assert got is not None and got.doc_id == second.doc_id, "按 doc_id 没归位到同文档副本"

    def test_stats_reports_zero_degree_and_normalizes_type(self, real_retriever):
        """stats 暴露零度实体计数，并把「角色|物品|…」这类脏类型归一到首类型。"""
        stats = real_retriever.store.stats()
        assert stats["zero_degree_entities"] > 0
        assert stats["zero_degree_entities"] < stats["entities"]
        assert all("|" not in t for t in stats["by_type"]), "类型脏值没有在统计视图里归一"
        assert "alias_reassigned" in stats


# ══════════════════════════════════════════════════════════════════════════
# P1：真实语料上的端到端延迟（性能回归护栏）
# ══════════════════════════════════════════════════════════════════════════


class TestP1LatencyBudget:
    def test_retrieve_p95_under_budget_on_real_corpus(self, real_retriever):
        """真实语料上热态检索 p95 必须远低于旧实现（旧实测 p50 7.1s / p90 14.9s）。

        本用例是**回归护栏**：预算取 500ms（旧实现 7000ms+，回退必然被抓到），
        留足 CI/并行负载的抖动空间——权威的 A1 数字（p95 ≤ 300ms）由
        ``scripts/eval_plot_rag.py --check-targets`` 在空载下测量。
        冷启动的 BM25 倒排构建（约 0.7s）单独预热，不计入统计。
        """
        import time

        retr = real_retriever
        queries = [
            "露西女士是谁",
            "维尔汀和圣洛夫基金会是什么关系",
            "重塑之手的目的是什么",
            "芝诺军备学院在哪里",
            "暴雨是什么",
            "露西和维尔汀有什么关系",
        ]
        retr.retrieve(queries[0], top_chunks=3, lexical_fallback=2)  # 预热（建倒排）
        lat = []
        for q in queries:
            t0 = time.perf_counter()
            retr.retrieve(q, top_chunks=3, lexical_fallback=2)
            lat.append((time.perf_counter() - t0) * 1000.0)
        lat.sort()
        p95 = lat[min(len(lat) - 1, int(len(lat) * 0.95))]
        assert p95 <= 500.0, f"检索 p95 {p95:.0f}ms 超出回归护栏 500ms：{lat}"
