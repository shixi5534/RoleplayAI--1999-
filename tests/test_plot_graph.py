"""剧情图谱层（PlotGraph）测试：语料隔离 / 语言处理 / 图谱检索 / 编排器零回归。

对应 docs/GRAPHRAG加强计划书.md §16：新 GraphRAG 与现有 lore 向量 RAG 相互独立，
故重点验证「隔离」与「关闭时不回退/不污染」两件事。
"""
from __future__ import annotations

import asyncio
import json
from pathlib import Path
from types import SimpleNamespace

import pytest

from roleplay.core.knowledge.graph_store import GraphStore
from roleplay.core.knowledge.plot_corpus import (
    PlotCorpus,
    detect_lang,
    parse_title_meta,
    plot_namespace,
)
from roleplay.core.knowledge.plot_graph import (
    PlotGraphRetriever,
    PlotGraphRegistry,
    build_plot_graph,
    is_noise_entity,
    load_alias_table,
    mine_entity_candidates,
    rescue_noise_entity,
    prompt_for_lang,
)
from roleplay.core.persona_prompt import build_plot_context, build_roleplay_prompt
from roleplay.core.rag.base import RetrievedChunk


# ── 语料：三重白名单（严禁手工整理 md 混入） ──
def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _trans_md(title: str, body: str) -> str:
    return (
        f"# {title}\n\n"
        "- 来源：B站 <https://www.bilibili.com/video/BV1TEST00000?p=1>\n"
        "- UP主：测试UP ｜ 发布：2026-09-01 ｜ 时长：10:00\n"
        "- 提取方式：whisper语音转写（机器提取，可能存在少量识别误差）\n"
        "- 抓取时间：2026-09-06\n\n---\n\n" + body
    )


def test_corpus_rejects_manual_and_foreign_files(tmp_path):
    """只有「视频文案目录 + BV 命名 + B站机器提取头」三关全过才入库。"""
    root = tmp_path / "lore" / "wu_ming_zhe"
    (root / "视频文案").mkdir(parents=True)
    # ① 合规转写
    _write(
        root / "视频文案" / "BV1TEST00000_p1_测试.md",
        _trans_md("【重返未来：1999】3.8版本「世纪末尺度」（01.世纪末的忧郁）", "正文一。" * 200),
    )
    # ② 手工整理 md（在角色目录根，不在视频文案目录）
    _write(root / "世界观_暴雨与阵营.md", "# 世界观\n\n手工整理的权威资料。")
    # ③ 名字像转写但缺机器提取头（伪造/串味文件）
    _write(root / "视频文案" / "BV1FAKE00001_p1_伪造.md", "# 伪造\n\n没有元数据头。")

    corpus = PlotCorpus(tmp_path / "plot_corpus.json", character_id="wu_ming_zhe")
    stat = corpus.build(root / "视频文案", chunk_size=200)
    assert stat["kept"] == 1, stat
    assert stat["rejected"] == 1, stat  # ③ 被元数据头白名单拦下
    assert all(c.bv == "BV1TEST00000" for c in corpus.chunks)
    # 手工文件在目录外，根本没被扫到
    assert stat["files"] == 2


def test_corpus_meta_and_lang(tmp_path):
    root = tmp_path / "视频文案"
    _write(
        root / "BV1TEST00000_p2_测试.md",
        _trans_md("【重返未来：1999】3.8版本「世纪末尺度」（02.阿里阿德涅之线）", "中文正文。" * 120),
    )
    _write(
        root / "BV1TEST00001_p1_测试.md",
        _trans_md("Reverse 1999 3.8", "The world did not end that night. " * 40),
    )
    corpus = PlotCorpus(tmp_path / "c.json")
    corpus.build(root, chunk_size=300)
    langs = {c.lang for c in corpus.chunks}
    assert "zh" in langs and "en" in langs
    zh = [c for c in corpus.chunks if c.lang == "zh"][0]
    assert zh.version == "3.8" and zh.arc == "世纪末尺度" and zh.chapter_no == 2
    assert zh.page == 2 and zh.doc_id == "BV1TEST00000_p2"
    assert detect_lang("这是一个中文句子" * 5) == "zh"
    assert detect_lang("The rain fell upward and the city dissolved." * 3) == "en"
    assert parse_title_meta("3.8版本「世纪末尺度」（01.世纪末的忧郁）")["version"] == "3.8"


def test_corpus_persist_roundtrip(tmp_path):
    root = tmp_path / "视频文案"
    _write(root / "BV1ABC00000_p1_x.md", _trans_md("标题", "正文二。" * 100))
    c1 = PlotCorpus(tmp_path / "c.json", character_id="x")
    c1.build(root, chunk_size=200)
    c1.save()
    c2 = PlotCorpus(tmp_path / "c.json", character_id="x")
    assert [c.hash for c in c2.chunks] == [c.hash for c in c1.chunks]
    assert c2.stats()["docs"] == 1
    hit = c2.search("正文二", top_k=2)
    assert hit and hit[0][1] > 0


def test_prompt_selected_by_language():
    assert "英文语音转写" in prompt_for_lang("en")
    assert "机器转写" in prompt_for_lang("zh")
    assert prompt_for_lang("other") == prompt_for_lang("zh")


def test_mine_entity_candidates_filters_sentence_noise(tmp_path):
    root = tmp_path / "视频文案"
    body = (
        "Just let it go. Maybe we should leave. Laplace called again and Timekeeper "
        "answered, Manus Vindictae is moving. Igor said the Foundation knows.\n\n"
    )
    _write(root / "BV1MINE00001_p1_x.md", _trans_md("x", body * 3))
    corpus = PlotCorpus(tmp_path / "c.json")
    corpus.build(root, chunk_size=200)
    names = {n for n, _ in mine_entity_candidates(corpus)}
    assert "Laplace" in names and "Timekeeper" in names
    assert "Just" not in names and "Maybe" not in names


# ── 图谱检索 ──
def _build_mini(tmp_path) -> tuple[PlotCorpus, GraphStore]:
    """三角关系小图谱：凯拉 —死亡→ 触发 —象征→ 发条装置（A→B→C，无直达边）。"""
    root = tmp_path / "视频文案"
    _write(root / "BV1G0000001_p1_x.md", _trans_md("x", "凯拉在雨里死去。" * 60))
    _write(root / "BV1G0000002_p1_x.md", _trans_md("x", "发条装置停在那一刻。" * 60))
    corpus = PlotCorpus(tmp_path / "corpus.json", character_id="x")
    corpus.build(root, chunk_size=200)
    store = GraphStore(tmp_path / "graph.json", min_confidence=0.5)
    store.bind_alias_table(
        {"凯拉": ["Kayla"], "发条装置": ["Clockwork Device"], "无名者": ["Ms. Stranger"]}
    )
    e_kayla = store.link_exact("凯拉")
    e_dev = store.link_exact("发条装置")
    e_self = store.link_exact("无名者")
    h1 = corpus.chunks[0].hash
    h2 = corpus.chunks[1].hash
    ev = [{"ns": "plot_x", "doc_id": "d1", "hash": h1}, {"ns": "plot_x", "doc_id": "d2", "hash": h2}]
    store.upsert_edge(src=e_self, dst=e_kayla, relation="失去", confidence=0.9,
                      importance=0.6, evidence=ev)
    store.upsert_edge(src=e_kayla, dst=e_dev, relation="象征", confidence=0.85,
                      importance=0.6, evidence=ev)
    store.save()
    return corpus, store


def test_retriever_multihop_and_alias(tmp_path):
    corpus, store = _build_mini(tmp_path)
    retr = PlotGraphRetriever(
        corpus, store, namespace=plot_namespace("x"), min_confidence=0.5, max_edges=10
    )
    # 中文别名 / 英文别名都能链接到同一实体
    assert retr.link("凯拉怎么样了") == retr.link("What about Kayla")
    # 查询「发条装置」→ 经两跳带回「凯拉」的证据（多跳可达性）
    out = retr.retrieve("发条装置", top_chunks=2)
    assert out, "多跳检索应有结果"
    assert all(c.metadata["namespace"] == "plot_x" for c in out)
    assert any("凯拉" in c.text for c in out), [c.text[:20] for c in out]


def test_retriever_weak_edge_gated(tmp_path):
    """孤证边（evidence < 2）默认不参与检索，开启 include_weak 才出现。"""
    corpus, store = _build_mini(tmp_path)
    store.upsert_edge(
        src=store.link_exact("无名者"),
        dst=store.link_exact("发条装置"),
        relation="持有",
        confidence=0.95,
        importance=0.6,
        # 用一条其它边都没引用的证据，避免与强边共用证据块而被去重吃掉
        evidence=[{"ns": "plot_x", "doc_id": "d1", "hash": corpus.chunks[-1].hash}],
    )
    strict = PlotGraphRetriever(corpus, store, namespace="plot_x", min_confidence=0.5)
    loose = PlotGraphRetriever(corpus, store, namespace="plot_x", min_confidence=0.5,
                               include_weak=True)
    edges_strict = {e["relation"] for e in store.all_edges()}
    assert "持有" in edges_strict  # 边已入库，只是检索时被门控
    hits_strict = strict.retrieve("发条装置", top_chunks=3)
    hits_loose = loose.retrieve("发条装置", top_chunks=3)
    assert any("持有" in (h.metadata.get("edge") or "") for h in hits_loose)
    assert not any("持有" in (h.metadata.get("edge") or "") for h in hits_strict)


def test_registry_missing_files_returns_none(tmp_path):
    reg = PlotGraphRegistry(corpus_dir=tmp_path / "no", graph_dir=tmp_path / "no")
    assert reg.get("nobody") is None
    info = reg.peek("nobody")
    assert info["corpus_exists"] is False and info["graph_exists"] is False


def test_alias_table_loaded(tmp_path):
    p = tmp_path / "plot_aliases.json"
    p.write_text(json.dumps({"露西": ["Madam Lucy", "Lucy"]}), encoding="utf-8")
    assert load_alias_table(p) == {"露西": ["Madam Lucy", "Lucy"]}
    assert load_alias_table(tmp_path / "missing.json") == {}


# ── 提示词与编排器：零回归 ──
def test_build_plot_context_budget_and_empty():
    assert build_plot_context([]) == ""
    chunks = [
        RetrievedChunk(text="剧情片段" * 300, score=1.0,
                       metadata={"namespace": "plot_x", "chapter": "世纪末的忧郁",
                                 "version": "3.8", "section": "3.8版本·世纪末的忧郁",
                                 "edge": "无名者 —失去→ 凯拉"}),
        RetrievedChunk(text="第二条" * 300, score=0.9, metadata={"namespace": "plot_x"}),
    ]
    out = build_plot_context(chunks, max_chars=500)
    assert out.startswith("【剧情记忆")
    assert "（剧情记忆·3.8版本·世纪末的忧郁）" in out
    assert "（关系）无名者 —失去→ 凯拉" in out
    assert len(out) < 900  # 预算截断生效（含块头约 200 字）


def test_prompt_unchanged_without_plot_chunks():
    base = build_roleplay_prompt(card_json=None, fallback_prompt="你是无名者。",
                                 default_card=None, message="你好",
                                 chunks=[], card=None)
    with_plot = build_roleplay_prompt(card_json=None, fallback_prompt="你是无名者。",
                                      default_card=None, message="你好",
                                      chunks=[], card=None, plot_chunks=[])
    assert base == with_plot
    assert "【剧情记忆" not in base


def test_prompt_includes_plot_block_when_provided():
    chunks = [RetrievedChunk(text="凯拉在雨里死去。", score=1.0,
                             metadata={"namespace": "plot_x", "chapter": "世纪末的忧郁"})]
    out = build_roleplay_prompt(card_json=None, fallback_prompt="你是无名者。",
                                default_card=None, message="凯拉呢",
                                chunks=[], card=None, plot_chunks=chunks)
    assert "【剧情记忆" in out and "凯拉在雨里死去。" in out


def test_orchestrator_plot_path_isolated_and_optional():
    """剧情层关闭 → 不注入；开启 → 注入；且 lore 检索结果不受影响。"""
    from roleplay.core.orchestrator import ChatOrchestrator
    from roleplay.core.llm.mock import MockLLMProvider
    from roleplay.core.rag.memory import InMemoryVectorStore
    from roleplay.core.emotion.detector import KeywordEmotionDetector
    from roleplay.core.knowledge.plot_corpus import PlotCorpus
    from roleplay.core.knowledge.graph_store import GraphStore
    from roleplay.models.chat import ChatRequest
    import tempfile

    tmp = Path(tempfile.mkdtemp(prefix="plot_orch_"))
    root = tmp / "视频文案"
    _write(root / "BV1O0000001_p1_x.md", _trans_md("x", "凯拉在雨里死去。" * 60))
    _write(root / "BV1O0000002_p1_x.md", _trans_md("x", "发条装置停在那一刻。" * 60))
    corpus = PlotCorpus(tmp / "plot_corpus_x.json", character_id="x")
    corpus.build(root, chunk_size=200)
    corpus.save()
    store = GraphStore(tmp / "plot_graph_x.json", min_confidence=0.5)
    store.bind_alias_table({"凯拉": ["Kayla"], "发条装置": ["Clockwork Device"], "无名者": ["Ms. Stranger"]})
    h = [c.hash for c in corpus.chunks]
    ev = [{"ns": "plot_x", "doc_id": "d", "hash": h[0]}, {"ns": "plot_x", "doc_id": "d", "hash": h[1]}]
    store.upsert_edge(src=store.link_exact("无名者"), dst=store.link_exact("凯拉"),
                      relation="失去", confidence=0.9, importance=0.6, evidence=ev)
    store.upsert_edge(src=store.link_exact("凯拉"), dst=store.link_exact("发条装置"),
                      relation="象征", confidence=0.85, importance=0.6, evidence=ev)
    store.save()

    reg = PlotGraphRegistry(corpus_dir=tmp, graph_dir=tmp, alias_dir=tmp)

    # 角色 id 由 character_store 解析（character_store 为空时恒为 None），
    # 这里给个最小替身，让剧情层能按 character_id="x" 找到自己的图谱文件。
    store_proxy = SimpleNamespace(get_active_id=lambda: "x", get=lambda cid: None)

    def _orch(enabled: bool) -> ChatOrchestrator:
        return ChatOrchestrator(
            llm=MockLLMProvider(),
            emotion=KeywordEmotionDetector(enabled=True),
            rag=InMemoryVectorStore(),
            knowledge_base=None,
            character_store=store_proxy,
            enable_profile=False,
            plot_graph=reg,
            plot_graph_enabled=enabled,
            plot_max_chunks=2,
        )

    # character_id 决定图谱文件名（plot_corpus_x.json / plot_graph_x.json）
    req = ChatRequest(session_id="s1", message="发条装置和凯拉有什么关系？", character_id="x")
    off = asyncio.run(_orch(False)._prepare(req))
    on = asyncio.run(_orch(True)._prepare(req))
    assert "【剧情记忆" not in off[0]
    assert "【剧情记忆" in on[0]
    assert "发条装置" in on[0]


# ── 图谱质量修复：别名抢占 / 噪声实体 / 链接收紧 ──
def test_ensure_entity_does_not_steal_alias():
    """合并路径不得抢占已被其他实体占有的别名（首注册优先）。"""
    store = GraphStore(":memory:", min_confidence=0.5)
    store.upsert_entities([{"name": "Madam Lucy", "aliases": ["露西"]}])
    owner = store.link_exact("露西")
    assert owner == store.link_exact("Madam Lucy")
    # 后到的抽取把「露西」挂到别的正名下 → 不得改写索引归属
    store.upsert_entities([{"name": "Doris", "aliases": ["露西"]}])
    assert store.link_exact("露西") == owner
    # Doris 实体存在，但其别名列表里没有「露西」
    doris = store.get_entity(store.link_exact("Doris"))
    assert "露西" not in (doris or {}).get("aliases", [])


def test_noise_entity_filter():
    """转写噪声正名（称谓/句子片段）被识别；正常名不受影响。"""
    for bad in ["ma'am", "senora", "Senorita", "An exorcist",
                "the eyes hiding in the shadows", "It's alright, truly.",
                "Find out what happened to him", "A", ""]:
        assert is_noise_entity(bad), bad
    for good in ["Madam Lucy", "Ms. Stranger", "St. Pavlov Foundation",
                 "Manus Vindictae", "Singular Louisa", "无名者", "圣洛夫基金会"]:
        assert not is_noise_entity(good), good


def test_rescue_noise_entity_via_alias():
    """5 类误杀：name 命中噪声但有干净别名时，别名升为正名、原 name 降为别名。"""
    cases = [
        # 句点误杀
        ({"name": "T.Kettler", "aliases": ["T Kettler"]}, "T Kettler"),
        # the 前缀误杀
        ({"name": "the Sixes", "aliases": ["Sixes"]}, "Sixes"),
        # 常用词同形误杀
        ({"name": "mine", "aliases": ["Mine (Ida)"]}, "Mine (Ida)"),
        # 首个别名也是噪声时跳过，取第二个
        ({"name": "mine", "aliases": ["it", "Ida's gun"]}, "Ida's gun"),
    ]
    for entity, expected in cases:
        rescued = rescue_noise_entity(entity)
        assert rescued is not None, entity
        assert rescued["name"] == expected, (entity, rescued)
        assert entity["name"] in rescued["aliases"], (entity, rescued)
    # 全噪声别名 / 无别名 → 不打捞
    assert rescue_noise_entity({"name": "mine", "aliases": ["it"]}) is None
    assert rescue_noise_entity({"name": "Z", "aliases": []}) is None
    # 契约：rescue 仅在 name 已判噪声时由调用方触发，本函数只做别名交换，
    # 不重复判定 name 是否噪声（干净名的短路在调用方）。


def test_build_graph_filters_noise_entities(tmp_path):
    """建图时纯噪声（无干净别名）被丢弃；带干净别名的误杀实体被打捞，
    且旧 name 降为别名后关系端点仍可解析。"""
    from roleplay.core.knowledge.graph_extract import GraphCache

    corpus, _store = _build_mini(tmp_path)
    cache = GraphCache(tmp_path / "cache")
    payload = {
        "entities": [
            {"name": "ma'am", "aliases": ["Madam Lucy"]},   # 误杀 → 打捞
            {"name": "An exorcist", "aliases": []},          # 纯噪声 → 丢弃
            {"name": "凯拉", "aliases": []},
        ],
        "relations": [{"src": "ma'am", "dst": "凯拉", "relation": "遇见",
                       "confidence": 0.9}],
    }
    for c in corpus.chunks[:1]:
        cache.put(c.hash, payload)

    async def _run():
        store2 = GraphStore(tmp_path / "fg.json", min_confidence=0.5)
        stats = await build_plot_graph(
            corpus, store2, _PassThroughExtractor(payload), cache, namespace="plot_x"
        )
        store2.save()
        return stats, store2

    stats, store2 = asyncio.run(_run())
    assert stats["noise_rescued"] >= 1  # ma'am → Madam Lucy 打捞
    assert stats["noise_filtered"] >= 1  # An exorcist（无干净别名）丢弃
    names = {e["name"] for e in store2.entities()}
    assert "凯拉" in names and "Madam Lucy" in names
    assert "ma'am" not in names and "An exorcist" not in names
    # 旧 name 降为别名后，src="ma'am" 的关系端点仍解析成功 → 建边
    assert stats["edges"] >= 1


class _PassThroughExtractor:
    """恒定返回同一抽取结果的假抽取器。"""

    def __init__(self, payload: dict):
        self.payload = payload

    async def extract(self, text: str, system: str | None = None):
        return self.payload


def test_link_tie_break_caps_seeds(tmp_path):
    """同长并列种子按「正名命中 > mentions」排序且至多 3 个。"""
    store = GraphStore(":memory:", min_confidence=0.5)
    store.upsert_entities([{"name": "Madam Lucy", "aliases": ["露西"]}])
    # 模拟多个实体共享别名「露西」（历史上被噪声实体抢占的形态）
    store.upsert_entities([{"name": "Doris", "aliases": []}])
    store.upsert_entities([{"name": "Muriel", "aliases": []}])
    doris = store.link_exact("Doris")
    muriel = store.link_exact("Muriel")
    # 直改内部状态，复刻旧数据形态：别名挂在实体列表上但索引仍指向首注册者
    for eid in (doris, muriel):
        store._entities[eid]["aliases"].append("露西")
    ml = store.link_exact("Madam Lucy")
    corpus, _ = _build_mini(tmp_path)
    retr = PlotGraphRetriever(corpus, store, namespace="plot_x",
                              link_threshold=0.5)
    seeds = retr.link("露西女士是谁")
    assert len(seeds) <= 3
    assert ml in seeds  # 正名不是「露西」但 mentions 最高时也参与并列排序
    # 「Madam Lucy」精确命中 → 单一种子，不再带出共享别名的其他实体
    seeds2 = retr.link("Madam Lucy")
    assert seeds2 == {ml: 1.0}


def test_link_lexical_ignores_single_cjk_overlap(tmp_path):
    """词法兜底弃用 CJK 单字：「发生了什么」不再命中含「生」的实体。"""
    store = GraphStore(":memory:", min_confidence=0.5)
    store.upsert_entities([{"name": "estudiantes", "aliases": ["学生"]}])
    corpus, _ = _build_mini(tmp_path)
    retr = PlotGraphRetriever(corpus, store, namespace="plot_x",
                              link_threshold=0.5)
    assert retr.link("3.8版本 世纪末尺度 发生了什么") == {}


def test_plot_include_weak_defaults_to_true():
    """孤证边默认必须启用：真实语料 99.7% 边只有 1 条证据。

    4302 条边里 4289 条 evidence<2（每块独立抽取，谓语措辞差异导致无法自然累积）。
    若默认 False，图谱检索只剩 13 条边可用，退化成纯词法兜底，补抽内容也全部不可达。
    """
    from roleplay.config import Settings

    assert Settings().plot_include_weak is True
