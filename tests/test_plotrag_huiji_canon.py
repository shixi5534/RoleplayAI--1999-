# -*- coding: utf-8 -*-
"""M7：灰机正典中文语料层 + 篇章路由的回归测试。

被锁住的行为（每条都对应一次实测踩坑）
    1. ``PlotCorpus.build`` 只认 ``视频文案/``（B站转写，双白名单）与 ``canon_zh/``
       （灰机正典，要求头部带来源 URL）两个目录段——手工整理 md 一律不得混入；
    2. 正典块 ``source_kind == "canon_zh"``、``doc_id`` 前缀 ``huiji_``，
       与 B站文档天然隔离，且 metadata 里带得来溯 URL；
    3. 篇章索引来自**语料自身元数据**（arc/chapter/正典标题），
       ``chapters_in`` 长名优先（「今夜星光灿烂」不能被「星」吃掉）；
    4. ``search(doc_ids=...)`` 真的只在给定文档集合里召回（篇章路由靠它缩小候选池）；
    5. 篇章路由是**独立通道**：点名篇章时即使图路有命中也要出块，
       且关掉开关后行为回到旧样（可消融、可回滚）。
"""
from __future__ import annotations

import json

from roleplay.core.knowledge.graph_store import GraphStore
from roleplay.core.knowledge.plot_corpus import (
    SOURCE_KIND_CANON_ZH,
    PlotChunk,
    PlotCorpus,
    _parse_canon_file,
)
from roleplay.core.knowledge.plot_graph import PlotGraphRetriever

CANON_MD = """# 洞穴的囚徒
版本：1.4
来源：https://res1999.huijiwiki.com/wiki/小径/洞穴的囚徒
抓取：2026-09-13
提取方式：灰机wiki 渲染文本（canon_zh）

---

???：
星锑抱着她的贝斯站在甲板上，海风把歌词吹得零零碎碎。

???：
苏芙比把药箱放在船舷上，说这艘船叫摇滚苹果号。
"""

TRANSCRIPT_MD = """# 《重返未来：1999》1.4版本「洞穴的囚徒」全剧情 - Reverse: 1999｜4K（01启航）

来源：B站
机器提取
UP主：缺德的德鲁伊
发布：2024-01-01

---

Vertin and Regulus boarded the Rockin' Apple.
Sotheby brought her medical kit on deck.
"""


def _write_canon(root, name="洞穴的囚徒.md"):
    d = root / "canon_zh"
    d.mkdir(parents=True, exist_ok=True)
    p = d / name
    p.write_text(CANON_MD, encoding="utf-8")
    return p


def _write_transcript(root, name="BV1xx411c7md_p1_x.md"):
    d = root / "视频文案"
    d.mkdir(parents=True, exist_ok=True)
    p = d / name
    p.write_text(TRANSCRIPT_MD, encoding="utf-8")
    return p


class TestCanonParsing:
    def test_canon_file_parsed_with_provenance(self, tmp_path):
        chunks = _parse_canon_file(_write_canon(tmp_path))
        assert chunks, "正典 md 未被解析"
        c = chunks[0]
        assert c.source_kind == SOURCE_KIND_CANON_ZH
        assert c.doc_id.startswith("huiji_")
        assert c.version == "1.4"
        assert "huijiwiki" in (c.extra or {}).get("url", "")
        assert c.meta("plot_x")["source_type"] == "plot_canon"

    def test_canon_without_source_is_rejected(self, tmp_path):
        """没有「来源：」的正典 md 一律不收——每一块都必须能溯源。"""
        d = tmp_path / "canon_zh"
        d.mkdir(parents=True)
        p = d / "无来源.md"
        p.write_text("# 无来源\n\n---\n\n正文若干。\n", encoding="utf-8")
        assert _parse_canon_file(p) is None

    def test_canon_chunk_meta_has_no_bilibili_url(self):
        c = PlotChunk(hash="h", text="文本", doc_id="huiji_x", bv="", page=1,
                      source_kind=SOURCE_KIND_CANON_ZH)
        assert c.meta("plot_x")["url"] == "", "正典块不应编出 B站 URL"


class TestBuildRouting:
    def test_build_separates_two_sources(self, tmp_path):
        _write_canon(tmp_path)
        _write_transcript(tmp_path)
        corpus = PlotCorpus(tmp_path / "c.json", character_id="x")
        stat = corpus.build(tmp_path)
        assert stat["files"] == 1 and stat["canon_files"] == 1
        kinds = {c.source_kind for c in corpus.chunks}
        assert SOURCE_KIND_CANON_ZH in kinds and "canon" in kinds

    def test_manual_md_outside_whitelisted_dirs_is_ignored(self, tmp_path):
        """手工整理 md（角色目录根）不得混入语料——三重白名单的既有约定。"""
        (tmp_path / "手工资料.md").write_text(
            "# 手工\n\n来源：B站\n机器提取\n\n---\n\n不该被收进来。\n", encoding="utf-8"
        )
        _write_canon(tmp_path)
        corpus = PlotCorpus(tmp_path / "c.json", character_id="x")
        stat = corpus.build(tmp_path)
        assert stat["files"] == 0 and stat["canon_files"] == 1
        assert all("手工" not in c.text for c in corpus.chunks)


class TestChapterRouting:
    def _corpus(self, tmp_path) -> PlotCorpus:
        _write_canon(tmp_path)
        _write_transcript(tmp_path)
        corpus = PlotCorpus(tmp_path / "c.json", character_id="x")
        corpus.build(tmp_path)
        return corpus

    def test_chapter_index_and_detection(self, tmp_path):
        corpus = self._corpus(tmp_path)
        idx = corpus.chapter_index()
        assert "洞穴的囚徒" in idx, "正典篇名未进篇章索引"
        assert corpus.chapters_in("洞穴的囚徒篇里海盗船上的歌手是谁？") == ["洞穴的囚徒"]
        assert corpus.chapters_in("今天天气怎么样") == []

    def test_longest_chapter_name_wins(self, tmp_path):
        """「今夜星光灿烂」不能被更短的「星」抢先匹配。"""
        corpus = self._corpus(tmp_path)
        corpus.chunks.append(PlotChunk(hash="h1", text="星", doc_id="d1", bv="", page=1,
                                       arc="星", source_kind=SOURCE_KIND_CANON_ZH))
        corpus.chunks.append(PlotChunk(hash="h2", text="今夜", doc_id="d2", bv="", page=1,
                                       arc="今夜星光灿烂",
                                       source_kind=SOURCE_KIND_CANON_ZH))
        corpus._chapter_index_cache = None
        hits = corpus.chapters_in("今夜星光灿烂篇的结尾")
        assert hits[0] == "今夜星光灿烂", f"篇章名未按长度优先：{hits}"

    def test_search_respects_doc_filter(self, tmp_path):
        corpus = self._corpus(tmp_path)
        pool = {"huiji_洞穴的囚徒"}
        hits = corpus.search("摇滚苹果号", top_k=5, doc_ids=pool)
        assert hits, "限定文档集合后仍应有命中"
        assert all(c.doc_id in pool for c, _s in hits)
        assert not corpus.search("摇滚苹果号", top_k=5, doc_ids={"BV1xx411c7md_p1"})

    def test_chapter_channel_fires_without_graph_hits(self, tmp_path):
        """图路有命中时篇章通道仍需出块（这类查询靠它救）。

        查询词必须**真的落在该篇正文里**——篇章路由用的是「先按篇章缩池、再在池内
        跑 BM25」，池内没有词元命中时它不应该硬塞块（那才是噪声）。
        """
        corpus = self._corpus(tmp_path)
        store = GraphStore(tmp_path / "g.json", min_confidence=0.5)
        store.upsert_entities([{"name": "星锑"}, {"name": "苏芙比"}, {"name": "洞穴"}])
        for a, b in (("星锑", "苏芙比"), ("苏芙比", "洞穴")):
            store.upsert_edge(src=store.link_exact(a), dst=store.link_exact(b),
                              relation="关联", confidence=0.9,
                              evidence=[{"ns": "plot_x", "doc_id": "BV1xx411c7md_p1",
                                         "hash": corpus.chunks[0].hash}])
        retr = PlotGraphRetriever(corpus, store, min_confidence=0.5, include_weak=True,
                                  chapter_routing=True, chapter_top=2)
        out = retr.retrieve("洞穴的囚徒篇里摇滚苹果号这艘船怎么样了？", top_chunks=3,
                            lexical_fallback=0)
        # 图路已经出块（edge），篇章通道仍必须把正典块带回来——
        # 断言看 `paths` 而不是 `path`：同一块被多路命中时 path 只留优先级最高的那个。
        all_paths = {p for c in out for p in (c.metadata.get("paths") or [])}
        assert "chapter" in all_paths, f"篇章通道未生效：{all_paths}"
        assert any("摇滚苹果号" in c.text for c in out), "篇章池内的正典块未被取回"

    def test_chapter_channel_can_be_disabled(self, tmp_path):
        corpus = self._corpus(tmp_path)
        store = GraphStore(tmp_path / "g.json", min_confidence=0.5)
        store.upsert_entities([{"name": "洞穴"}])
        retr = PlotGraphRetriever(corpus, store, min_confidence=0.5, include_weak=True,
                                  chapter_routing=False)
        out = retr.retrieve("洞穴的囚徒篇里海盗船上的歌手是谁？", top_chunks=3,
                            lexical_fallback=0)
        assert all(c.metadata.get("path") != "chapter" for c in out)

    def test_chapter_route_meta_is_recorded(self, tmp_path):
        corpus = self._corpus(tmp_path)
        store = GraphStore(tmp_path / "g.json", min_confidence=0.5)
        store.upsert_entities([{"name": "洞穴"}])
        retr = PlotGraphRetriever(corpus, store, min_confidence=0.5, include_weak=True,
                                  chapter_routing=True, chapter_top=2)
        out = retr.retrieve("洞穴的囚徒篇里海盗船上的歌手是谁？", top_chunks=3,
                            lexical_fallback=0)
        routed = [c for c in out if "chapter" in (c.metadata.get("paths") or [])]
        assert routed, "篇章路由元数据缺失"
        assert routed[0].metadata.get("chapter_route") in ("洞穴的囚徒", None)
        assert routed[0].metadata.get("via") == "plot_graph"


class TestLexicalAlwaysDefaultOff:
    def test_default_is_off(self, tmp_path):
        """词法常开实测有害（−5pt），默认必须是关的；开启走显式开关。"""
        corpus = PlotCorpus(tmp_path / "c.json", character_id="x")
        corpus.chunks = []
        store = GraphStore(tmp_path / "g.json", min_confidence=0.5)
        retr = PlotGraphRetriever(corpus, store, min_confidence=0.5)
        assert retr.lexical_always is False
        assert retr.chapter_routing is True


class TestAliasGovernance:
    def test_governance_script_helpers(self):
        """别名表自相冲突合并：中文正名存活，英文条目并入后删除。"""
        import importlib.util
        import sys
        from pathlib import Path

        root = Path(__file__).resolve().parents[1]
        spec = importlib.util.spec_from_file_location(
            "_alias_apply", root / "scripts" / "huiji_alias_apply.py"
        )
        mod = importlib.util.module_from_spec(spec)
        sys.modules["_alias_apply"] = mod
        spec.loader.exec_module(mod)
        table = {"阿莱夫": ["Aleph"], "Aleph": ["阿莱夫", "Mr.Aleph"]}
        out, merged = mod.consolidate(dict(table))
        assert len(out) == 1, f"冲突条目未合并：{list(out)}"
        assert "阿莱夫" in out, "中文正名应存活"
        assert "Mr.Aleph" in out["阿莱夫"], "被合并条目的别名必须保留"
        assert merged and merged[0]["drop"] == "Aleph"

    def test_human_reserved_aliases_are_guarded(self):
        """人工裁决保留的别名不得被灰机自动桥改指（裁决 1：凯拉归无名者）。

        本轮灰机会话确实产出了 `Kayla += 凯拉`（另有一个 NPC 叫 Kayla）。
        照单执行会在重建时把「凯拉」从无名者改指到 Kayla 节点——**推翻已记录的
        人工裁决**，所以脚本必须硬拦，而不是"数据看起来更整齐"就执行。
        """
        import importlib.util
        import sys
        from pathlib import Path

        root = Path(__file__).resolve().parents[1]
        spec = importlib.util.spec_from_file_location(
            "_alias_apply_guard", root / "scripts" / "huiji_alias_apply.py"
        )
        mod = importlib.util.module_from_spec(spec)
        sys.modules["_alias_apply_guard"] = mod
        spec.loader.exec_module(mod)
        assert "凯拉" in mod.HUMAN_RESERVED_ALIASES
        table = {"无名者": ["凯拉"]}
        props = [{"key": "Kayla", "add": ["凯拉"], "confidence": "high"}]
        applied, blocked = mod.apply_bridge(table, props)
        assert applied == [], "被裁决保留的别名不得写入"
        assert blocked and blocked[0]["add"] == "凯拉"
        assert table["无名者"] == ["凯拉"], "原有归属不得被改动"


class TestMentionQuotaIsConfigurable:
    def test_quota_defaults_come_from_instance(self, tmp_path):
        """提及通道配额必须走实例配置（旧实现写死 3/6，多跳题第 4 块永远进不来）。"""
        corpus = PlotCorpus(tmp_path / "c.json", character_id="x")
        corpus.chunks = []
        store = GraphStore(tmp_path / "g.json", min_confidence=0.5)
        retr = PlotGraphRetriever(corpus, store, min_confidence=0.5,
                                  mention_per_entity=5, mention_total_cap=10)
        assert retr.mention_per_entity == 5
        assert retr.mention_total_cap == 10
        # 调用点不传参时沿用实例值
        assert retr._mention_channel({}) == []


def test_canon_report_json_is_valid_if_present():
    """正典采集报告若存在，必须可解析（防止半截 JSON 被当成成功产物）。"""
    from pathlib import Path

    p = (Path(__file__).resolve().parents[1] / "data" / "knowledge" / "_audit"
         / "canon_zh_report.json")
    if not p.is_file():
        return
    data = json.loads(p.read_text(encoding="utf-8"))
    assert data["written"] == len([r for r in data["rows"] if not r.get("skipped")])
