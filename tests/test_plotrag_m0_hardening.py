"""M0（观测性与安全网）+ N0（入库前置）加固测试。

覆盖范围（对应 scripts/ 与 src/roleplay/core/knowledge/ 的本轮改动）：
- N0-1：标题版本号的三种实测形态 + 误判边界
- N0-2：source_kind 打标规则 + 老语料缺字段时的默认值兼容
- N0-3：by_hash / upsert_edge 索引加速（语义不变）
- M0-2：图谱文件损坏 → 拒绝落盘（防空图覆盖）
- M0-5：别名表类型防御 + 丢弃统计 + 冲突计数
"""
from __future__ import annotations

import asyncio
import json
from pathlib import Path

from roleplay.core.knowledge.graph_extract import GraphCache
from roleplay.core.knowledge.graph_store import GraphStore, entity_id
from roleplay.core.knowledge.plot_corpus import (
    SOURCE_KIND_ANALYSIS,
    SOURCE_KIND_CANON,
    SOURCE_KIND_OFFICIAL,
    PlotChunk,
    PlotCorpus,
    classify_source_kind,
    parse_title_meta,
)
from roleplay.core.knowledge.plot_graph import (
    build_plot_graph,
    load_alias_table,
    load_alias_table_with_stats,
)

ROOT = Path(__file__).resolve().parents[1]


class _PassThroughExtractor:
    """恒定返回同一抽取结果的假抽取器（不走 LLM）。"""

    def __init__(self, payload: dict) -> None:
        self.payload = payload

    async def extract(self, text: str, system: str | None = None) -> dict:
        return self.payload


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _trans_md(title: str, body: str, *, uploader: str = "缺德的德鲁伊") -> str:
    return (
        f"# {title}\n\n"
        "- 来源：B站 <https://www.bilibili.com/video/BV1TEST00000?p=1>\n"
        f"- UP主：{uploader} ｜ 发布：2026-09-01 ｜ 时长：10:00\n"
        "- 提取方式：whisper语音转写（机器提取，可能存在少量识别误差）\n"
        "- 抓取时间：2026-09-06\n\n---\n\n" + body
    )


# ── N0-1：版本号解析的三种实测形态 ──────────────────────────────────────────
def test_version_three_title_forms():
    """① 3.8版本  ② 【1.1-活动】  ③ 中配1.6 —— 三种形态都要能提出来。"""
    # ① 旧形态（592/726）：小数 + 「版本」
    t1 = "【重返未来：1999】3.8版本「世纪末尺度」全剧情流程 - Reverse: 1999｜4K（01.世纪末的忧郁）"
    # ② 公测合集（76/726）：【N.N-主线/活动/角色/剧情】
    t2 = "《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.1-活动】雷米特杯失窃案｜1~4）"
    t2b = "《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第四章.老虎的金黄｜11~16）"
    t2c = "《重返未来：1999》公测 全剧情（【1.1-角色】以盗制盗1-都灵圆盘、缅因齿儿｜梅兰妮个人剧情）"
    # ③ 中配分节（24/726）：中配N.N【篇章】
    t3 = "《重返未来1999》中配1.6【朔日手记】全剧情【4K】（10【异乡人关怀】中英配）"

    assert parse_title_meta(t1)["version"] == "3.8"
    assert parse_title_meta(t2)["version"] == "1.1"
    assert parse_title_meta(t2b)["version"] == "1.0"
    assert parse_title_meta(t2c)["version"] == "1.1"
    assert parse_title_meta(t3)["version"] == "1.6"


def test_version_does_not_misread_duration_or_year():
    """边界：时长 / 年份 / 裸小数不能误判成版本号。"""
    cases = [
        "【重返未来：1999】全剧情合集（时长1.5小时，一次性看完）",
        "【重返未来：1999】2024.10 更新说明与版本回顾",
        "《重返未来：1999》无名者PV：无名无我 A Stranger Under Every Name",
        "【重返未来：1999】剧情合集 第1.5期（无版本号标题）",
    ]
    for title in cases:
        assert parse_title_meta(title)["version"] == "", title


def test_version_other_fields_untouched():
    """改正则不能顺带打乱 arc / chapter 的解析。"""
    meta = parse_title_meta(
        "【重返未来：1999】3.8版本「世纪末尺度」全剧情流程 - Reverse: 1999｜4K（01.世纪末的忧郁）"
    )
    assert meta["arc"] == "世纪末尺度"
    assert meta["chapter_no"] == 1
    assert meta["chapter"] == "世纪末的忧郁"


# ── N0-2：source_kind ──────────────────────────────────────────────────────
def test_source_kind_classification():
    """官方号 > 主线白名单 > 考据白名单 > 标题关键词 > canon。"""
    assert (
        classify_source_kind(uploader="重返未来1999", title="无名者PV")
        == SOURCE_KIND_OFFICIAL
    )
    assert (
        classify_source_kind(uploader="缺德的德鲁伊", title="3.8版本全剧情")
        == SOURCE_KIND_CANON
    )
    # 考据向 UP 主白名单
    assert (
        classify_source_kind(uploader="薯条小叔叔", title="某个标题")
        == SOURCE_KIND_ANALYSIS
    )
    # 标题关键词兜底（UP 主不在任何白名单里）
    assert (
        classify_source_kind(uploader="不认识的UP", title="万字解析！一口气看完主线")
        == SOURCE_KIND_ANALYSIS
    )
    assert classify_source_kind(uploader="不认识的UP", title="实况录像") == SOURCE_KIND_CANON
    # 主线白名单优先于标题关键词：实录标题里带「解析」也不降级
    assert (
        classify_source_kind(uploader="缺德的德鲁伊", title="3.8版本全剧情解析")
        == SOURCE_KIND_CANON
    )
    assert classify_source_kind() == SOURCE_KIND_CANON


def test_source_kind_default_for_legacy_corpus(tmp_path):
    """老语料 JSON 没有 source_kind 键 → 默认 canon，读取不报错。"""
    p = tmp_path / "plot_corpus_legacy.json"
    legacy = {
        "schema": "plot-corpus-v1",
        "character_id": "legacy",
        "count": 1,
        "docs": {},
        "chunks": [
            {
                "hash": "abc123",
                "text": "这是旧格式语料块，没有 source_kind 字段。",
                "doc_id": "BVOLD00001",
                "bv": "BVOLD00001",
                "page": 1,
                "title": "老标题",
                "uploader": "缺德的德鲁伊",
            }
        ],
    }
    _write(p, json.dumps(legacy, ensure_ascii=False))
    corpus = PlotCorpus(p, character_id="legacy")
    assert len(corpus.chunks) == 1
    assert corpus.chunks[0].source_kind == SOURCE_KIND_CANON
    # 显式给了非法取值 → 兜回 canon，不抛错
    chunk = PlotChunk.from_dict({"hash": "x", "text": "t", "doc_id": "d", "bv": "b",
                                 "page": 1, "source_kind": "unknown_kind"})
    assert chunk.source_kind == SOURCE_KIND_CANON
    # 正常取值原样保留
    assert PlotChunk.from_dict(
        {"hash": "x", "text": "t", "doc_id": "d", "bv": "b", "page": 1,
         "source_kind": SOURCE_KIND_ANALYSIS}
    ).source_kind == SOURCE_KIND_ANALYSIS
    # to_dict 带出字段（供后续落盘）
    assert chunk.to_dict()["source_kind"] == SOURCE_KIND_CANON


def test_source_kind_tagged_on_ingest(tmp_path):
    """入库时按 UP 主打标，并能在统计里看到分布。"""
    root = tmp_path / "lore" / "wu_ming_zhe" / "视频文案"
    _write(
        root / "BV1TEST00001_p1_主线.md",
        _trans_md("【重返未来：1999】3.8版本「世纪末尺度」（01.开篇）", "主线正文。" * 120),
    )
    _write(
        root / "BV1TEST00002_p1_考据.md",
        _trans_md("万字解析！一口气看完主线", "考据正文。" * 120, uploader="薯条小叔叔"),
    )
    corpus = PlotCorpus(tmp_path / "corpus.json", character_id="wu_ming_zhe")
    stat = corpus.build(root)
    by_kind = {c.uploader: c.source_kind for c in corpus.chunks}
    assert set(by_kind.values()) == {SOURCE_KIND_CANON, SOURCE_KIND_ANALYSIS}
    assert by_kind["缺德的德鲁伊"] == SOURCE_KIND_CANON
    assert by_kind["薯条小叔叔"] == SOURCE_KIND_ANALYSIS
    assert stat["by_source_kind"][SOURCE_KIND_CANON] > 0
    assert stat["by_source_kind"][SOURCE_KIND_ANALYSIS] > 0


# ── N0-3：索引加速 ─────────────────────────────────────────────────────────
def test_corpus_by_hash_is_indexed(tmp_path):
    """by_hash 走 O(1) 索引；手动改 chunks 后也能正确命中。"""
    root = tmp_path / "视频文案"
    _write(root / "BV1TEST00003_p1_a.md", _trans_md("标题A｜无版本", "正文甲。" * 120))
    corpus = PlotCorpus(tmp_path / "c.json", character_id="x")
    corpus.build(root)
    assert corpus.chunks
    h = corpus.chunks[0].hash
    assert corpus.by_hash(h) is corpus.chunks[0]
    assert corpus.by_hash("不存在的hash") is None
    assert corpus.by_hash("") is None
    # 手动往 chunks 里塞一块（绕过 build/load）：惰性重建索引后仍能查到
    extra = PlotChunk(hash="newhash", text="新块", doc_id="d", bv="b", page=1)
    corpus.chunks.append(extra)
    assert corpus.by_hash("newhash") is extra


def test_edge_upsert_merge_semantics_unchanged(tmp_path):
    """_edge_idx 加速后合并语义不变：evidence 并集、conf/imp 取 max。"""
    p = tmp_path / "graph.json"
    store = GraphStore(p)
    a = store.upsert_entities([{"name": "无名者"}])[0]
    b = store.upsert_entities([{"name": "维尔汀"}])[0]
    assert store.upsert_edge(
        src=a, dst=b, relation="同行", confidence=0.6, importance=0.5,
        evidence=[{"ns": "plot_x", "doc_id": "d1", "hash": "h1"}],
    )
    assert store.upsert_edge(
        src=a, dst=b, relation="同行", confidence=0.9, importance=0.4,
        evidence=[
            {"ns": "plot_x", "doc_id": "d1", "hash": "h1"},
            {"ns": "plot_x", "doc_id": "d2", "hash": "h2"},
        ],
    )
    edges = [e for e in store.all_edges() if e["src"] == a and e["dst"] == b]
    assert len(edges) == 1  # 合并成一条，没有重复
    assert edges[0]["confidence"] == 0.9  # max
    assert edges[0]["importance"] == 0.5  # max
    assert [e["hash"] for e in edges[0]["evidence"]] == ["h1", "h2"]  # 并集且保序

    # 落盘再读回：_edge_idx 重建后仍只合并出一条
    store.save()
    reloaded = GraphStore(p)
    assert len(reloaded.all_edges()) == 1
    assert reloaded.upsert_edge(
        src=a, dst=b, relation="同行", confidence=0.7,
        evidence=[{"ns": "plot_x", "doc_id": "d1", "hash": "h1"}],
    )
    assert len(reloaded.all_edges()) == 1
    assert [e["hash"] for e in reloaded.all_edges()[0]["evidence"]] == ["h1", "h2"]

    # 不同 relation 不合并（键仍是 (src, dst, relation) 三元组）
    assert reloaded.upsert_edge(src=a, dst=b, relation="对立", confidence=0.8)
    assert len(reloaded.all_edges()) == 2


def test_edge_index_not_persisted(tmp_path):
    """_edge_idx 只是运行时结构，不落盘（save 的 payload 不含它）。"""
    p = tmp_path / "g2.json"
    store = GraphStore(p)
    a = store.upsert_entities([{"name": "A"}])[0]
    b = store.upsert_entities([{"name": "B"}])[0]
    store.upsert_edge(src=a, dst=b, relation="认识", confidence=0.9)
    store.save()
    raw = json.loads(p.read_text(encoding="utf-8"))
    assert "_edge_idx" not in raw
    assert set(raw) == {"fingerprint", "entities", "edges", "alias_index", "anchored"}


def test_edge_index_rebuilt_after_remove_by_doc(tmp_path):
    """remove_by_doc 换过边表后，索引要跟着重建（不能指向已删的边）。"""
    p = tmp_path / "g3.json"
    store = GraphStore(p)
    a = store.upsert_entities([{"name": "A"}])[0]
    b = store.upsert_entities([{"name": "B"}])[0]
    store.upsert_edge(
        src=a, dst=b, relation="认识", confidence=0.9,
        evidence=[{"ns": "ns1", "doc_id": "doc1", "hash": "h1"}],
    )
    assert len(store.all_edges()) == 1
    store.remove_by_doc("ns1", "doc1")
    assert store.all_edges() == []
    # 索引若没重建，这里会复活一条已删的边
    store.upsert_edge(
        src=a, dst=b, relation="认识", confidence=0.9,
        evidence=[{"ns": "ns2", "doc_id": "doc2", "hash": "h2"}],
    )
    edges = store.all_edges()
    assert len(edges) == 1
    assert edges[0]["evidence"][0]["doc_id"] == "doc2"


# ── M0-2：空图覆盖保护 ─────────────────────────────────────────────────────
def test_missing_file_is_not_an_error(tmp_path):
    """文件不存在 = 首次构建：无 load_error，save 照常可写。"""
    p = tmp_path / "new_graph.json"
    store = GraphStore(p)
    assert store.load_error is None
    store.upsert_entities([{"name": "无名者"}])
    store.save()
    assert p.is_file()
    assert GraphStore(p).stats()["entities"] == 1


def test_corrupt_file_blocks_save(tmp_path):
    """文件存在但解析失败 → load_error 非空 + save 拒绝落盘（防固化成空图）。"""
    p = tmp_path / "graph.json"
    _write(p, '{"entities": {"e_1": {"name": "无名者"}}, "edges": [')  # 截断的坏 JSON
    store = GraphStore(p)
    assert store.load_error is not None
    store.save()
    # 源文件必须原样保留
    assert p.read_text(encoding="utf-8").startswith('{"entities"')
    assert "e_1" in p.read_text(encoding="utf-8")


def test_non_dict_root_blocks_save(tmp_path):
    """顶层不是 object（如 `[]` / 2 字节的 `{}` 之外的非法内容）→ 拒绝落盘。"""
    p = tmp_path / "graph2.json"
    _write(p, "[]")
    store = GraphStore(p)
    assert store.load_error is not None
    store.save()
    assert p.read_text(encoding="utf-8").strip() == "[]"


def test_entity_wipe_blocks_save(tmp_path):
    """加载时有实体、落盘时内存实体为 0 → 拒绝落盘。"""
    p = tmp_path / "graph3.json"
    store = GraphStore(p)
    store.upsert_entities([{"name": "无名者"}, {"name": "维尔汀"}])
    store.save()
    assert p.is_file()

    store2 = GraphStore(p)
    assert store2.stats()["entities"] == 2
    store2._entities.clear()  # 模拟异常清空
    store2.save()
    # 盘上仍是 2 个实体，没被空图覆盖
    assert GraphStore(p).stats()["entities"] == 2


def test_legit_empty_graph_file_can_still_save(tmp_path):
    """合法空图（{}）不算损坏：不拦 save，避免把正常首次构建卡死。"""
    p = tmp_path / "graph4.json"
    _write(p, "{}")
    store = GraphStore(p)
    assert store.load_error is None
    store.upsert_entities([{"name": "无名者"}])
    store.save()
    assert GraphStore(p).stats()["entities"] == 1


# ── M0-5：别名表类型防御 ───────────────────────────────────────────────────
def test_alias_table_str_value_not_split_into_chars(tmp_path):
    """value 是字符串时当单个别名，不能逐字符切（旧实现的坑）。"""
    p = tmp_path / "aliases.json"
    _write(p, json.dumps({"露西": "Madam Lucy"}, ensure_ascii=False))
    table = load_alias_table(p)
    assert table == {"露西": ["Madam Lucy"]}


def test_alias_table_stats_drop_cases(tmp_path):
    """_ 开头元数据键跳过、非法类型丢弃，且都体现在统计里。"""
    p = tmp_path / "aliases.json"
    _write(
        p,
        json.dumps(
            {
                "_meta": {"schema": "v1"},  # 元数据键 → dropped_underscore
                "_note": "说明",  # 元数据键 → dropped_underscore
                "露西": ["Madam Lucy", "Lucy"],  # 正常 → 2 条别名
                "维尔汀": "Vertin",  # str → 1 条别名
                "重塑之手": {"en": "Manus"},  # dict → dropped_bad_type
                "暴雨": 3,  # int → dropped_bad_type
                "鸽子屋": [],  # 空列表 → 保留条目（正名仍要锚定）
                "": ["空正名"],  # 空 key → dropped_empty
            },
            ensure_ascii=False,
        ),
    )
    table, stats = load_alias_table_with_stats(p)
    assert table == {
        "露西": ["Madam Lucy", "Lucy"],
        "维尔汀": ["Vertin"],
        "鸽子屋": [],
    }
    assert stats["dropped_underscore"] == 2
    assert stats["dropped_bad_type"] == 2
    assert stats["dropped_empty"] == 1
    assert stats["kept"] == 3
    assert stats["aliases"] == 3
    # 老签名只返回 dict，行为不变
    assert load_alias_table(p) == table


def test_alias_table_missing_or_broken(tmp_path):
    """文件缺失 / 坏 JSON / 顶层非 dict → 空表 + 零统计，不抛异常。"""
    assert load_alias_table(tmp_path / "nope.json") == {}
    _, stats = load_alias_table_with_stats(tmp_path / "nope.json")
    assert stats["total"] == 0

    bad = tmp_path / "bad.json"
    _write(bad, "{not json")
    assert load_alias_table(bad) == {}

    arr = tmp_path / "arr.json"
    _write(arr, "[]")
    assert load_alias_table(arr) == {}


def test_alias_conflict_counted(tmp_path):
    """bind_alias_table 遇到别名冲突时计数，可通过属性读出。"""
    p = tmp_path / "g5.json"
    store = GraphStore(p)
    store.upsert_entities([{"name": "露西娅", "aliases": ["露西"]}])
    assert store.alias_ambiguous_dropped == 0
    # 「露西」已被 露西娅 占有，绑定给 露西女士 时会被跳过
    store.bind_alias_table({"露西女士": ["露西", "Lucy"]})
    assert store.alias_ambiguous_dropped == 1
    # 冲突不抢占：索引仍指向首注册实体
    assert store.link_exact("露西") == entity_id("露西娅")
    assert store.link_exact("Lucy") == entity_id("露西女士")


# ── 缺陷 1：结构合法性不只查顶层类型 ────────────────────────────────────────
def test_object_without_graph_keys_blocks_save(tmp_path):
    """合法 JSON object 但一个图谱键都没有 → 结构非法，拒绝覆盖。"""
    p = tmp_path / "g.json"
    p.write_text('{"foo": 1}', encoding="utf-8")
    before = p.read_text(encoding="utf-8")
    store = GraphStore(p)
    assert store.load_error is not None
    assert "结构非法" in store.load_error
    store.upsert_entities([{"name": "无名者"}])
    store.save()
    assert p.read_text(encoding="utf-8") == before


def test_empty_object_still_treated_as_empty_graph(tmp_path):
    """``{}`` 仍属合法空图（防误伤首次构建路径，空图不能被永久锁死）。"""
    p = tmp_path / "g.json"
    p.write_text("{}", encoding="utf-8")
    store = GraphStore(p)
    assert store.load_error is None
    store.upsert_entities([{"name": "无名者"}])
    store.save()
    assert json.loads(p.read_text(encoding="utf-8"))["entities"]


def test_any_single_graph_key_makes_file_valid(tmp_path):
    """含任一个已知图谱键即视为合法文件（收紧校验不能误伤正常图谱）。"""
    for payload in (
        '{"entities": {}}',
        '{"edges": []}',
        '{"fingerprint": {"schema": "v1"}}',
        '{"alias_index": {}}',
        '{"anchored": []}',
    ):
        p = tmp_path / f"g_{abs(hash(payload))}.json"
        p.write_text(payload, encoding="utf-8")
        store = GraphStore(p)
        assert store.load_error is None, payload
        store.upsert_entities([{"name": "A"}])
        store.save()
        assert json.loads(p.read_text(encoding="utf-8"))["entities"], payload


# ── 缺陷 2：save() 被拒必须浮出来，不能静默假成功 ─────────────────────────
def test_build_plot_graph_surfaces_save_error_in_stats(tmp_path):
    """库函数 build_plot_graph：save() 被拒时写 stats["save_error"]，不静默。"""
    gpath = tmp_path / "graph.json"
    gpath.write_text('{"entities": {"e_x": {"name": "旧实体"}}, "edges": [', encoding="utf-8")
    before = gpath.read_text(encoding="utf-8")

    corpus = PlotCorpus(tmp_path / "corpus.json", character_id="x")
    corpus.chunks = [
        PlotChunk(hash="h1", text="正文内容。", doc_id="d1", bv="b1", page=1, lang="zh")
    ]
    cache = GraphCache(tmp_path / "cache")
    payload = {
        "entities": [{"name": "维尔汀", "aliases": ["Vertin"]}],
        "relations": [],
    }
    cache.put("h1", payload)
    store = GraphStore(gpath)
    assert store.load_error is not None  # 前提：图谱文件已损坏

    stats = asyncio.run(
        build_plot_graph(
            corpus, store, _PassThroughExtractor(payload), cache, namespace="plot_x"
        )
    )
    assert stats.get("save_error"), "拒绝落盘没有浮出来，运维会误以为建图成功"
    assert store.load_error in stats["save_error"]
    assert gpath.read_text(encoding="utf-8") == before  # 一个字节都没写


def test_build_plot_graph_stats_has_no_save_error_on_success(tmp_path):
    """正常路径不产生 save_error（不能把健康构建也标成失败）。"""
    corpus = PlotCorpus(tmp_path / "corpus.json", character_id="x")
    corpus.chunks = [
        PlotChunk(hash="h1", text="正文内容。", doc_id="d1", bv="b1", page=1, lang="zh")
    ]
    cache = GraphCache(tmp_path / "cache")
    payload = {"entities": [{"name": "维尔汀", "aliases": ["Vertin"]}], "relations": []}
    cache.put("h1", payload)
    store = GraphStore(tmp_path / "graph.json")
    stats = asyncio.run(
        build_plot_graph(
            corpus, store, _PassThroughExtractor(payload), cache, namespace="plot_x"
        )
    )
    assert "save_error" not in stats
    assert json.loads((tmp_path / "graph.json").read_text(encoding="utf-8"))["entities"]


def test_lore_build_graph_cli_checks_load_error():
    """lore 侧 CLI（scripts/build_graph.py）：save() 后必须检查 load_error 并返回 1。"""
    source = (ROOT / "scripts" / "build_graph.py").read_text(encoding="utf-8")
    assert "store.save()" in source
    assert "store.load_error" in source, "lore 建图未检查 load_error（安静的假成功）"
    assert source.index("store.save()") < source.index("store.load_error"), (
        "检查必须发生在 save() 之后"
    )
    tail = source[source.index("store.load_error"):]
    assert "拒绝落盘" in tail[:300]
    assert "return 1" in tail[:300]


def test_plot_build_graph_cli_checks_both_channels():
    """剧情侧 CLI：store.load_error 与 stats["save_error"] 两道口径都看。"""
    source = (ROOT / "scripts" / "build_plot_graph.py").read_text(encoding="utf-8")
    assert source.count("store.load_error") >= 2
    assert 'stats.get("save_error")' in source


# ── 缺陷 3：索引回退分支回填（自愈）────────────────────────────────────────
def test_edge_index_self_heals_after_fallback(tmp_path):
    """_edge_idx miss 后回退线性扫描命中 → 回填索引，后续查找回到 O(1)。"""
    p = tmp_path / "g.json"
    store = GraphStore(p)
    a = store.upsert_entities([{"name": "A"}])[0]
    b = store.upsert_entities([{"name": "B"}])[0]
    store.upsert_edge(src=a, dst=b, relation="认识", confidence=0.9)
    store._edge_idx.clear()  # 模拟索引与边表不同步的极端情况
    assert not store._edge_idx

    store.upsert_edge(
        src=a, dst=b, relation="认识", confidence=0.6,
        evidence=[{"ns": "n", "doc_id": "d", "hash": "h"}],
    )
    edges = store.all_edges()
    assert len(edges) == 1, "回退路径没有正确合并，产生了重复边"
    assert edges[0]["confidence"] == 0.9  # max 语义不变
    assert len(edges[0]["evidence"]) == 1
    assert (a, b, "认识") in store._edge_idx, "回退命中后索引未回填，无法自愈"
    assert store._edge_idx[(a, b, "认识")] is edges[0]
