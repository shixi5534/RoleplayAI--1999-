# -*- coding: utf-8 -*-
"""剧情 RAG 优化护栏（P1 性能 / P2 排序 / P3 门控 / P4 语义修复）。

本文件是审计（docs/plot-graph-rag/CHRONICLE.md §2026-09-12·plot 检索层审计）里每一项优化的**正确性护栏**：

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
        """可选 idf 模式：命中**稀有别名**的块排在"同一实体被反复复述"的块之前。

        注：别名须经人工别名表登记（P1 之后未登记的抽取别名会被判可疑并降权，
        见 TestP1AliasTrust）——本用例走人工表路径，验证的才是 idf 打分本身。
        """
        recap = "阿甲" + "。废话" * 30 + "阿甲" * 6
        answer = "阿甲 的真名是 Zeta。" + "。旁白" * 30
        retr = _retriever_with_corpus(
            tmp_path, [recap, answer], mention_scoring="idf", cooccurrence_bonus=False
        )
        store = retr.store
        store.bind_alias_table({"阿甲": ["Zeta"]}, on_conflict="merge")
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

    # ── 负样本护栏的**已知残余**（有界技术债，不是豁免）─────────────────────
    # 背景：2026-09-13 把负样本从 10 条扩到 57 条（分类见 eval_plot_rag.NEGATIVE_CASES），
    # 原本"10 条全绿"的护栏立刻失守 15 条——**10 条样本从未覆盖到这些问法**。
    # 本轮修掉 10 条（问候/感叹 + 抽象泛化名词入泛词表；代词/敬称别名在链接期剔除），
    # 剩这 5 条**修不动**：它们的种子（苹果 度2 / Paris 度31 / President 度6 /
    # our nation / 泰坦尼克号）都是**作品内真实实体**，仅凭结构判据无法与"离题引用"
    # 区分——必须靠 B3（reranker 安全间隔）的语义相关度。
    #
    # 两条被**数据否决**的粗暴修法（勿再试）：
    #   ① 要求"至少一个锚定种子" → 短路 111/300 正样本（正是别名桥缺失主战场）；
    #   ② 孤立实体（度 0）不做种子 → 短路 23/288（滚鳄书店/菲林士多/Nuku Teow 等
    #      真实体只是零度节点，其提及块仍有价值）。
    #
    # 本清单的作用：**新增泄漏仍然会让用例失败**（只放行这 5 条已知项），
    # 避免"把护栏改松"变成静默通过。清零后请删除本清单。
    KNOWN_RESIDUAL_NEGATIVES = {
        "哈利波特是谁": "种子 哈利/Harry（度0 mentions1）——跨作品专名，待 B3",
        "苹果公司的 CEO 是谁": "种子 苹果（度2）/公司（度1）——作品内有苹果实体，待 B3",
        "巴黎在哪个国家": "种子 Paris（度31，作品内真实地点）——结构性判据无法区分，待 B3",
        "泰坦尼克号是哪一年沉没的": "种子 泰坦尼克号（度0 mentions1）——跨作品专名，待 B3",
        "who is the president of the united states":
            "种子 President（度6）——作品内有该实体，待 B3",
    }

    def test_offtopic_queries_inject_nothing(self, real_retriever):
        """离题问句必须零注入；**已知残余**单列登记，新增泄漏一律失败。

        判据（两条）：
          ① `bad - KNOWN_RESIDUAL` 必须为空 —— 不得出现**新的**泄漏；
          ② 残余集合必须 ⊆ 登记表 —— 登记表不得被当成"随便放过"的白名单。
        """
        import importlib.util

        # 负样本清单以评测台为单一来源（scripts/ 不是包，只能按路径加载）
        spec = importlib.util.spec_from_file_location(
            "_eval_plot_rag", ROOT / "scripts" / "eval_plot_rag.py"
        )
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)  # type: ignore[union-attr]
        bad = {}
        for q in mod.NEGATIVE_QUERIES:
            out = real_retriever.retrieve(q, top_chunks=3, lexical_fallback=2)
            if out:
                bad[q] = (len(out), [c.metadata.get("path") for c in out])
        new_leaks = {q: v for q, v in bad.items()
                     if q not in self.KNOWN_RESIDUAL_NEGATIVES}
        assert not new_leaks, (
            f"出现**新的**离题注入（不在已知残余清单内）：{new_leaks}\n"
            f"修掉后再决定是否登记；不得直接往 KNOWN_RESIDUAL_NEGATIVES 里加。"
        )
        # 残余台账：数量与内容都要可核（防止它悄悄长大）
        assert set(bad) <= set(self.KNOWN_RESIDUAL_NEGATIVES)
        assert len(mod.NEGATIVE_QUERIES) >= 50, "负样本量不足 50，护栏覆盖面会退化"


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
# P1（真实对话诊断）：别名可信度分层 —— 防抽取脏别名劫持提及通道
# ══════════════════════════════════════════════════════════════════════════


class TestP1AliasTrust:
    """实测背景：实体「牙仙」的抽取别名含 doll(df=21)/Campbell(df=13)，等权计数下
    提及 top-3 全是这些词的块、一块都不含 Tooth Fairy；「阿尔卡纳」含 Arkanist
    （=神秘学家，另一个实体）。本类锁住"人工名/正名/其变体可信，其余降权"的语义。
    """

    def test_human_alias_and_canonical_are_trusted(self, tmp_path):
        retr = _retriever_with_corpus(tmp_path, ["无关正文。"])
        store = retr.store
        store.bind_alias_table({"牙仙": ["Tooth Fairy"]}, on_conflict="merge")
        eid = store.link_exact("牙仙")
        ent = store.get_entity(eid)
        trusted = retr._trusted_names(eid, [ent["name"]] + list(ent.get("aliases") or []))
        assert "牙仙" in trusted and "tooth fairy" in trusted

    def test_variant_of_trusted_name_is_trusted(self, tmp_path):
        """ASR 变体（包含/编辑距离/共享词元）必须留在可信集，否则真名的最常见写法进不来。"""
        retr = _retriever_with_corpus(tmp_path, ["无关正文。"])
        store = retr.store
        store.upsert_entities(
            [{"name": "芭卡洛儿", "aliases": ["Barcarola", "Baccarola", "Miss Barcarola", "musical star"]}]
        )
        store.bind_alias_table({"芭卡洛儿": ["Barcarola"]}, on_conflict="merge")
        eid = store.link_exact("芭卡洛儿")
        ent = store.get_entity(eid)
        trusted = retr._trusted_names(eid, [ent["name"]] + list(ent.get("aliases") or []))
        assert "baccarola" in trusted, "编辑距离 1 的 ASR 变体被误杀"
        assert "miss barcarola" in trusted, "包含关系的变体被误杀"
        assert "musical star" not in trusted, "与正名无关的抽取别名不应可信"

    def test_chain_drift_is_blocked(self, tmp_path):
        """称谓片段不得成为锚点后把无关人名链式拖进可信集（实测踩过的真 bug）。"""
        from roleplay.core.knowledge.plot_graph import _is_name_variant

        anchors = {"miss tooth fairy", "tooth fairy", "牙仙"}
        assert _is_name_variant("miss", anchors) is False, "光杆称谓不应算变体"
        assert _is_name_variant("miss campbell", anchors) is False, "无关人名不应链式可信"
        assert _is_name_variant("ms.tooth fairy", anchors) is True
        # 短 CJK 名不得因编辑距离 ≤2 互相误判（玩偶↔牙仙）
        assert _is_name_variant("玩偶", {"牙仙"}) is False

    def test_hijacking_alias_no_longer_wins(self, tmp_path):
        """脏别名命中更多的块，不应压过正名块。"""
        junk = "Campbell" * 8 + "。" + "填充" * 20      # 脏别名反复出现
        good = "牙仙 就是 Tooth Fairy。" + "。填充" * 20
        retr = _retriever_with_corpus(tmp_path, [junk, good])
        store = retr.store
        store.upsert_entities(
            [{"name": "牙仙", "aliases": ["Tooth Fairy", "Campbell", "doll"]}]
        )
        store.bind_alias_table({"牙仙": ["Tooth Fairy"]}, on_conflict="merge")
        eid = store.link_exact("牙仙")
        got = retr._mention_channel({eid: 1.0})
        assert got and "Tooth Fairy" in got[0][1].text, "脏别名仍然劫持了提及通道"
        assert got[0][1].text != junk

    def test_real_data_tooth_fairy_wins(self, real_retriever):
        """真实数据回归：牙仙的提及 top-1 必须是**可信名**块，不得是脏别名块。

        2026-09 修订（中文正典层入库）：原先断言 top-1 含 ``tooth fairy``，
        那是因为当时语料只有 B 站**英文 ASR**——中文正名「牙仙」在语料里近乎零命中，
        英文名是唯一通路。canon_zh（灰机小径 + compendium 全本）入库后，中文正典块
        天然含「**牙仙**：」且排名更高，把断言写死英文名等于**要求中文正典让位**，
        与「中文查询 ↔ 中文正文」的建层目的相悖。
        故判据改为：top-1 必须含**中文正名或英文正名之一**；
        真正要防的回归（脏别名 doll/Campbell 劫持）仍然锁死。
        """
        r = real_retriever
        eid = r.store.link_exact("牙仙")
        if not eid:
            pytest.skip("真实图谱里没有「牙仙」实体")
        got = r._mention_channel({eid: 1.0})
        assert got, "提及通道应有结果"
        top = got[0][1].text.lower()
        assert ("tooth fairy" in top) or ("牙仙" in top), (
            f"top-1 既非中文正名也非英文正名，疑似脏别名块：{got[0][1].text[:60]!r}"
        )
        # 脏别名不得成为 top-1（原测试的核心意图，保持不变）
        junk = [str(a).lower() for a in (r.store.get_entity(eid).get("aliases") or [])
                if str(a).lower() in {"doll", "campbell", "miss", "ms.campbell",
                                      "miss campbell", "玩偶"}]
        assert not any(j in top for j in junk), (
            f"top-1 是脏别名块（{junk}）：{got[0][1].text[:60]!r}"
        )

    def test_untrusted_alias_still_gets_one_slot(self, tmp_path):
        """可疑名不应被完全封杀：每实体仍保留 1 条补位块（防漏召回）。"""
        retr = _retriever_with_corpus(tmp_path, ["无关。"])
        store = retr.store
        store.upsert_entities([{"name": "甲", "aliases": ["乙", "丙"]}])
        store.bind_alias_table({"甲": []}, on_conflict="merge")
        eid = store.link_exact("甲")
        assert retr.untrusted_extra_per_entity == 1
        assert retr._trusted_names(eid, ["甲", "乙", "丙"]) >= {"甲"}


class TestP2EntityQueryBoost:
    def test_entity_boost_mechanism_and_measured_default(self, real_retriever):
        """实体查询提权机制可用，但**默认关闭**——这是 300 题消融测出来的决策。

        实测：开启（2.0）严格通过率 45.3%→44.67%（−0.6pt），而真实对话验收 A1
        在关闭时同样 7/7。故默认 1.0（不启用），机制保留为质量取向的可选档。
        """
        from roleplay.config import Settings

        assert Settings().plot_weight_mention_entity == 1.0, (
            "把默认改回 >1 会让 300 题回退，必须重跑 eval_plot_rag.py"
        )
        # 机制本身可用：显式提高到 2.0 后，短实体查询的提及通道权重确实被抬高
        boosted = _clone_with(real_retriever, weight_mention_entity=2.0)
        assert boosted.weight_mention_entity == 2.0
        out = boosted.retrieve("芭卡洛儿", top_chunks=3, lexical_fallback=2)
        assert out, "实体查询应有结果"
        # 2026-09 修订（中文正典层入库）：原断言死写英文名 "barcarola"，理由同
        # TestP1AliasTrust.test_real_data_tooth_fairy_wins——当时只有英文 ASR，
        # 中文正名无可召回；canon_zh 入库后中文正典块（含「**芭卡洛儿**」）排名更高，
        # 死写英文名会反过来要求中文正典让位。判据改为中/英正名命中其一即可。
        top2 = " ".join(c.text.lower() for c in out[:2])
        assert ("barcarola" in top2) or ("芭卡洛儿" in top2), (
            f"前两块既无中文正名也无英文正名：{[c.text[:40] for c in out[:2]]}"
        )


def _clone_with(retr, **overrides):
    """按需复制一个检索器并覆盖参数（保持共享同一 corpus/store，避免重复加载）。"""
    kwargs = dict(
        namespace=retr.namespace,
        min_confidence=retr.min_confidence,
        include_weak=retr.include_weak,
        max_edges=retr.max_edges,
        max_hops=retr.max_hops,
        damping=retr.damping,
        link_threshold=retr.link_threshold,
        fuse_k=retr.fuse_k,
        weight_edge=retr.weight_edge,
        weight_mention=retr.weight_mention,
        weight_lexical=retr.weight_lexical,
        diversity_per_doc=retr.diversity_per_doc,
        mention_scoring=retr.mention_scoring,
        cooccurrence_bonus=retr.cooccurrence_bonus,
        mention_group_by_entity=retr.mention_group_by_entity,
        alias_trust_ratio=retr.alias_trust_ratio,
        untrusted_extra_per_entity=retr.untrusted_extra_per_entity,
        weight_mention_entity=retr.weight_mention_entity,
        entity_query_max_len=retr.entity_query_max_len,
        alias_trust_chained_min_df=retr.alias_trust_chained_min_df,
        name_salience=retr.name_salience,
    )
    kwargs.update(overrides)
    return PlotGraphRetriever(retr.corpus, retr.store, **kwargs)


class TestP3BudgetedGateExemption:
    def test_plot_chunks_survive_relative_gate(self):
        """剧情通道豁免 0.85 相对门：5 块必须全数保留（此前只剩 2 块，答案块被丢）。"""
        from roleplay.core.persona_prompt import _filter_chunks
        from roleplay.core.rag.base import RetrievedChunk

        chunks = [
            RetrievedChunk(text=f"片段{i}", score=s, metadata={"via": "plot_graph", "path": "edge"})
            for i, s in enumerate([1.0, 0.9, 0.84, 0.8, 0.76])
        ]
        assert len(_filter_chunks(chunks)) == 5, "剧情通道仍被相对门砍掉"

    def test_lore_chunks_still_gated(self):
        """非限量通道（向量库）行为不变：相对门继续生效。"""
        from roleplay.core.persona_prompt import _filter_chunks
        from roleplay.core.rag.base import RetrievedChunk

        chunks = [
            RetrievedChunk(text="强相关", score=1.0, metadata={"namespace": "lore_x"}),
            RetrievedChunk(text="弱噪声", score=0.3, metadata={"namespace": "lore_x"}),
        ]
        kept = _filter_chunks(chunks)
        assert [c.text for c in kept] == ["强相关"]


# ══════════════════════════════════════════════════════════════════════════
# P1：真实语料上的端到端延迟（性能回归护栏）
# ══════════════════════════════════════════════════════════════════════════


class TestP1LatencyBudget:
    def test_retrieve_p95_under_budget_on_real_corpus(self, real_retriever):
        """真实语料上热态检索 p95 必须远低于旧实现（旧实测 p50 7.1s / p90 14.9s）。

        本用例是**回归护栏**：预算取 1500ms（旧实现 7000ms+，回退必然被抓到），
        留足 CI/并行负载的抖动空间——权威的 A1 数字由
        ``scripts/eval_plot_rag.py --check-targets`` 在空载下测量。
        冷启动的 BM25 倒排构建（约 0.7s）单独预热，不计入统计。

        ⚠️ 预算沿革（2026-09-20，**已知性能代价，非遗漏**）：
            500ms → 1500ms。图谱从 7 582 边涨到 23 345 边（3.1 倍）、
            语料 9 021 → 14 247 块（compendium 中文正典入库）。
            cProfile 实测：``personalized_pagerank`` 占检索耗时 **89%**
            （8.94s / 10.05s，6 次调用；9.66M 次 dict.get），
            空载 p95 由 178ms 升到约 **640ms**，满负载 pytest 下 683–878ms。
            已尝试并把结论记录在此：把 ``dict.get`` 绑到局部变量做热路径微优化
            —— 实测**无收益**（638ms vs 636ms），瓶颈是 20 轮 × 2.3 万边的
            Python 级图遍历本身。
            **未擅自下调 ``plot_ppr_max_iter``**：config 注释记载该值由
            300 题实测标定（20 与 40 轮质量逐位一致），而本机语义索引不可用
            （``嵌入模型不符``），无法复跑那次权威消融——**无据不调参**。
            后续应做其一：① 用 numpy/稀疏矩阵重写 PPR；② 复跑 300 题消融后
            把 max_iter 降到 10（本次实测 8 条查询 top-3 与 50 轮逐位一致）。
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
        assert p95 <= 1500.0, f"检索 p95 {p95:.0f}ms 超出回归护栏 1500ms：{lat}"
