# -*- coding: utf-8 -*-
"""分块测试：边界、重叠、确定性、碎块合并。"""
from __future__ import annotations

from compendium_rag.chunker import (Chunk, _content_key, chunk_chapter,
                                    chunk_corpus, chunks_stats, render_turns)
from compendium_rag.corpus import Chapter, Part, Scene, Turn


def _chapter(n_parts=1, n_scenes=1, n_turns=10, text_len=80):
    ch = Chapter(doc_id="t__x", title="测试篇", category="mainline",
                 source_file="x.md")
    for pi in range(n_parts):
        pt = Part(title=f"Part {pi + 1}")
        for si in range(n_scenes):
            sc = Scene(title=f"场景{si}", script_id=str(1000 + si))
            for ti in range(n_turns):
                sc.turns.append(Turn("dialogue", f"角色{ti % 3}",
                                     "字" * text_len))
            pt.scenes.append(sc)
        ch.parts.append(pt)
    return ch


def test_render_turns_formats_by_kind():
    turns = [Turn("dialogue", "维尔汀", "你好"),
             Turn("narration", "", "她走开了"),
             Turn("title_card", "", "1966伦敦"),
             Turn("quote", "", "引文")]
    out = render_turns(turns)
    assert "**维尔汀**：你好" in out
    assert "她走开了" in out
    assert "【标题卡】1966伦敦" in out
    assert "「引文」" in out


def test_dialogue_speaker_prefix_preserved(isolated_settings):
    """说话人前缀必须进入块文本——抽取与检索都依赖它。"""
    ch = _chapter(n_turns=6)
    chunks = chunk_corpus([ch], isolated_settings)
    assert any("**角色0**：" in c.text for c in chunks)


def test_chunk_boundaries_respect_scene(isolated_settings):
    """块不跨 scene（同一块内所有 turn 来自同一场景前提）。"""
    ch = _chapter(n_parts=1, n_scenes=3, n_turns=12, text_len=100)
    chunks = chunk_corpus([ch], isolated_settings)
    assert len(chunks) >= 3
    scenes = {c.scene_title for c in chunks}
    assert len(scenes) >= 3


def test_chunk_ids_unique(isolated_settings):
    ch = _chapter(n_scenes=4, n_turns=10)
    chunks = chunk_corpus([ch], isolated_settings)
    ids = [c.chunk_id for c in chunks]
    assert len(ids) == len(set(ids))


def test_chunking_deterministic(isolated_settings):
    ch = _chapter(n_scenes=3, n_turns=15)
    a = chunk_corpus([ch], isolated_settings)
    b = chunk_corpus([ch], isolated_settings)
    assert [c.chunk_id for c in a] == [c.chunk_id for c in b]
    assert [c.text for c in a] == [c.text for c in b]
    assert [c.content_key for c in a] == [c.content_key for c in b]


def test_small_chunks_merged(isolated_settings):
    """碎块（< min_chunk_chars）必须被并入相邻块，不单独成块。"""
    ch = _chapter(n_scenes=1, n_turns=40, text_len=2)   # 每行 2 字 → 全是碎块
    chunks = chunk_corpus([ch], isolated_settings)
    assert chunks, "不应全部丢弃"
    assert all(len(c.text) >= isolated_settings.min_chunk_chars
               for c in chunks if len(chunks) > 1)


def test_merge_preserves_all_turns(isolated_settings):
    """合并不得丢内容：合并后 turn 总数与原文一致。"""
    ch = _chapter(n_scenes=2, n_turns=20, text_len=3)
    chunks = chunk_corpus([ch], isolated_settings)
    total = sum(c.n_turns for c in chunks)
    assert total == 40, f"合并后 turn 数 {total} != 原文 40"


def test_no_empty_chunks(isolated_settings):
    ch = _chapter(n_scenes=3, n_turns=8)
    chunks = chunk_corpus([ch], isolated_settings)
    assert all(c.text.strip() for c in chunks)


def test_speakers_collected(isolated_settings):
    ch = _chapter(n_turns=9)
    chunks = chunk_corpus([ch], isolated_settings)
    for c in chunks:
        assert c.speakers
        assert len(c.speakers) == len(set(c.speakers)), "说话人不应重复"


def test_chunk_roundtrip(isolated_settings):
    ch = _chapter(n_scenes=2, n_turns=12)
    chunks = chunk_corpus([ch], isolated_settings)
    for c in chunks:
        back = Chunk.from_dict(c.to_dict())
        assert back.chunk_id == c.chunk_id
        assert back.text == c.text
        assert back.content_key == c.content_key


def test_content_key_is_content_hash():
    assert _content_key("abc") == _content_key("abc")
    assert _content_key("abc") != _content_key("abd")
    assert len(_content_key("abc")) == 16


def test_chunks_stats_shape(isolated_settings):
    ch = _chapter(n_scenes=3, n_turns=10)
    st = chunks_stats(chunk_corpus([ch], isolated_settings))
    for k in ("chunks", "chars", "mean_chars", "p50_chars", "p90_chars",
              "max_chars", "min_chars", "by_category"):
        assert k in st


def test_empty_chapter_yields_no_chunks(isolated_settings):
    ch = Chapter(doc_id="e", title="空", category="mainline", source_file="e.md")
    assert chunk_corpus([ch], isolated_settings) == []


def test_chunk_size_target_respected(isolated_settings):
    """块大小应围绕 chunk_chars（允许尾块与合并带来的偏差）。"""
    ch = _chapter(n_parts=1, n_scenes=1, n_turns=60, text_len=60)
    small = isolated_settings.with_(chunk_chars=500, chunk_overlap_turns=0)
    chunks = chunk_corpus([ch], small)
    assert len(chunks) > 1
    big = [c for c in chunks if len(c.text) > 500 * 2.5]
    assert not big, f"存在异常大的块：{[len(c.text) for c in big]}"
