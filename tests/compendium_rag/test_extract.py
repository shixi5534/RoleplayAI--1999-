# -*- coding: utf-8 -*-
"""抽取归一化测试：受控词表、噪声剔除、端点合法性、缓存幂等。

全部离线——直接构造模型输出喂给 normalize()，不调用云端。
"""
from __future__ import annotations

import json

import pytest

from compendium_rag.chunker import Chunk
from compendium_rag.extract import (ENTITY_TYPES, PROMPT_VERSION, Extraction,
                                    ExtractionCache, build_user_prompt,
                                    cache_key, is_noise_name, normalize)
from compendium_rag.corpus import Turn


def _chunk(text="**维尔汀**：你好，十四行诗。", speakers=("维尔汀", "十四行诗")):
    return Chunk(chunk_id="c1", content_key="k1", doc_id="d",
                 chapter_title="篇", category="mainline", part_title="P",
                 scene_title="S", script_id="1", chapter_id="1",
                 turns=[Turn("dialogue", "维尔汀", text)],
                 speakers=list(speakers), text=text)


def _raw(ents=None, rels=None):
    return {"entities": ents or [], "relations": rels or []}


# ── 类型受控 ──

@pytest.mark.parametrize("raw_type,expected", [
    ("角色", "角色"), ("人物", "角色"), ("人名", "角色"),
    ("组织", "组织"), ("家族", "组织"), ("势力", "组织"),
    ("地点", "地点"), ("地名", "地点"),
    ("物品", "物品"), ("道具", "物品"),
    ("概念", "概念"), ("术语", "概念"),
    ("事件", "事件"),
    ("乱七八糟", "概念"),
])
def test_type_mapping(raw_type, expected):
    ex = normalize(_chunk(), _raw([{"name": "A", "type": raw_type}]))
    assert ex.entities[0].type == expected
    assert ex.entities[0].type in ENTITY_TYPES


# ── 噪声剔除 ──

@pytest.mark.parametrize("name", [
    "？？？", "众人", "人们", "路人甲", "市民观众Ⅰ", "旁白", "系统",
])
def test_generic_names_dropped(name):
    ex = normalize(_chunk(), _raw([{"name": name, "type": "角色"}]))
    assert all(e.name != name for e in ex.entities)


@pytest.mark.parametrize("name", [
    "高个子", "被捆绑住的女孩", "那个持枪的男人", "一位神秘学家",
    "其他研究员", "某个士兵",
])
def test_descriptive_phantom_entities_dropped(name):
    """描述性短语不是「名字」——实测某模型大量产出，必须挡在归一化层。"""
    ex = normalize(_chunk(), _raw([{"name": name, "type": "角色"}]))
    assert all(e.name != name for e in ex.entities)


@pytest.mark.parametrize("name", [
    "J收起博伊刀", "玛蒂尔达夸奖J", "幻象飘散而去",
])
def test_sentence_paraphrase_events_dropped(name):
    """句子复述不是事件实体——事件类型只收有专名的重大事件。"""
    ex = normalize(_chunk(), _raw([{"name": name, "type": "事件"}]))
    assert all(e.name != name for e in ex.entities)


def test_person_leading_paraphrase_dropped_via_normalize():
    """两遍扫描生效：先收集角色，再据此剔除 `<角色><动作>` 型事件复述。"""
    ex = normalize(_chunk(speakers=("使徒米修斯", "J")), _raw([
        {"name": "使徒米修斯", "type": "角色"},
        {"name": "J", "type": "角色"},
        {"name": "使徒米修斯划手心流血", "type": "事件"},
        {"name": "新纪元集市·祭坛", "type": "地点"},
    ]))
    kept = {e.name for e in ex.entities}
    assert "使徒米修斯划手心流血" not in kept
    assert {"使徒米修斯", "J", "新纪元集市·祭坛"} <= kept


@pytest.mark.parametrize("name,ok", [
    ("暴雨", True), ("决斗", True), ("船商贸易节", True), ("圣火纪行", True),
    ("公开审讯", True), ("弃船准备", True), ("海风的往事", True),
    ("J收起博伊刀", False), ("他打了他", False), ("玛蒂尔达夸奖J", False),
    ("杰洛击打J肚子", False), ("幻象飘散而去", False),
])
def test_is_noise_name_event_rule(name, ok):
    assert is_noise_name(name, "事件") is (not ok)


def test_person_leading_event_needs_context():
    """`<角色名><动作>` 型复述依赖已确认角色集才能判定（两遍扫描的原因）。

    无上下文时 ``使徒米修斯划手心流血`` 看起来像专名（不含标点/虚词），
    只有知道 ``使徒米修斯`` 是角色后，才能识别出它是动作复述。
    这是 normalize 必须先收集角色、再过滤事件的直接理由。
    """
    n = "使徒米修斯划手心流血"
    assert is_noise_name(n, "事件") is False, "无上下文时无法判定"
    assert is_noise_name(n, "事件", {"使徒米修斯"}) is True, "有上下文应剔除"


def test_true_event_names_survive_with_person_context():
    """真正的专名事件在角色上下文下不能被误删。"""
    persons = {"使徒米修斯", "J", "维尔汀"}
    for n in ("暴雨", "决斗", "船商贸易节", "圣火纪行", "公开审讯"):
        assert is_noise_name(n, "事件", persons) is False, f"{n} 被误删"


def test_compound_place_name_not_treated_as_person_prefix():
    """`新纪元集市·祭坛` 以地名开头，是合法复合地名，不得误删（只对角色前缀生效）。"""
    assert is_noise_name("新纪元集市·祭坛", "地点",
                         {"新纪元集市"}) is False


def test_real_names_kept():
    """真实角色名（含单字符/数字名）必须保留。"""
    for n in ("维尔汀", "星锑", "X", "J", "Z", "37", "APPLe", "十四行诗",
              "圣洛夫基金会", "1966英国伦敦"):
        assert not is_noise_name(n, "角色"), f"{n} 被误判为噪声"


def test_long_name_dropped():
    assert is_noise_name("笃信万物皆数的一座位于爱琴海上的小岛", "地点")


# ── 别名与去重 ──

def test_aliases_captured():
    ex = normalize(_chunk(), _raw([
        {"name": "维尔汀", "type": "角色", "aliases": ["司辰", "汀汀"]}]))
    assert set(ex.entities[0].aliases) == {"司辰", "汀汀"}


def test_duplicate_entities_deduped():
    ex = normalize(_chunk(), _raw([
        {"name": "维尔汀", "type": "角色"},
        {"name": "维尔汀", "type": "角色", "aliases": ["司辰"]}]))
    assert len(ex.entities) == 1
    assert "司辰" in ex.entities[0].aliases


def test_self_alias_removed():
    ex = normalize(_chunk(), _raw([
        {"name": "维尔汀", "type": "角色", "aliases": ["维尔汀"]}]))
    assert ex.entities[0].aliases == []


def test_noise_alias_removed():
    ex = normalize(_chunk(), _raw([
        {"name": "维尔汀", "type": "角色", "aliases": ["？？？", "高个子", "司辰"]}]))
    assert ex.entities[0].aliases == ["司辰"]


def test_desc_captured():
    ex = normalize(_chunk(), _raw([
        {"name": "A", "type": "角色", "desc": "  一位主角  "}]))
    assert ex.entities[0].desc == "一位主角"


# ── 关系合法性 ──

def test_relation_endpoints_must_resolve():
    ex = normalize(_chunk(), _raw(
        [{"name": "A", "type": "角色"}],
        [{"src": "A", "relation": "认识", "dst": "未声明的路人甲", "confidence": 0.9}]))
    # 未声明端点且不是可靠说话人 → 丢弃
    assert ex.relations == []


def test_relation_endpoint_resolved_via_alias():
    ex = normalize(_chunk(), _raw(
        [{"name": "维尔汀", "type": "角色", "aliases": ["司辰"]},
         {"name": "十四行诗", "type": "角色"}],
        [{"src": "司辰", "relation": "认识", "dst": "十四行诗", "confidence": 0.9}]))
    assert len(ex.relations) == 1
    assert ex.relations[0].src == "维尔汀"


def test_speaker_endpoint_added():
    """可靠说话人作为端点时自动补实体，保证边可解析。"""
    ex = normalize(_chunk(speakers=("维尔汀", "十四行诗")), _raw(
        [{"name": "维尔汀", "type": "角色"}],
        [{"src": "维尔汀", "relation": "认识", "dst": "十四行诗",
          "confidence": 0.9}]))
    assert len(ex.relations) == 1
    assert any(e.name == "十四行诗" for e in ex.entities)


def test_self_relation_dropped():
    ex = normalize(_chunk(), _raw(
        [{"name": "A", "type": "角色"}],
        [{"src": "A", "relation": "认识", "dst": "A", "confidence": 0.9}]))
    assert ex.relations == []


def test_duplicate_relations_deduped():
    ex = normalize(_chunk(), _raw(
        [{"name": "A", "type": "角色"}, {"name": "B", "type": "角色"}],
        [{"src": "A", "relation": "认识", "dst": "B", "confidence": 0.8},
         {"src": "A", "relation": "认识", "dst": "B", "confidence": 0.9}]))
    assert len(ex.relations) == 1


def test_confidence_clamped():
    ex = normalize(_chunk(), _raw(
        [{"name": "A", "type": "角色"}, {"name": "B", "type": "角色"}],
        [{"src": "A", "relation": "认识", "dst": "B", "confidence": 5.0}]))
    assert ex.relations[0].confidence == 1.0


def test_bad_confidence_defaults_zero():
    ex = normalize(_chunk(), _raw(
        [{"name": "A", "type": "角色"}, {"name": "B", "type": "角色"}],
        [{"src": "A", "relation": "认识", "dst": "B", "confidence": "??"}]))
    assert ex.relations[0].confidence == 0.0


def test_evidence_truncated():
    ex = normalize(_chunk(), _raw(
        [{"name": "A", "type": "角色"}, {"name": "B", "type": "角色"}],
        [{"src": "A", "relation": "认识", "dst": "B",
          "evidence": "字" * 200, "confidence": 0.9}]))
    assert len(ex.relations[0].evidence) <= 80


def test_relation_via_descriptive_endpoint_dropped():
    ex = normalize(_chunk(), _raw(
        [{"name": "A", "type": "角色"}],
        [{"src": "A", "relation": "攻击", "dst": "被捆绑住的女孩",
          "confidence": 0.9}]))
    assert ex.relations == []


# ── 结构健壮性 ──

def test_empty_payload():
    ex = normalize(_chunk(), _raw())
    assert ex.entities == [] and ex.relations == []


def test_non_dict_entries_ignored():
    ex = normalize(_chunk(), {"entities": ["字符串", 123, None],
                              "relations": ["x", 4]})
    assert ex.entities == [] and ex.relations == []


def test_missing_keys_tolerated():
    ex = normalize(_chunk(), {"entities": [{"name": "A"}],
                              "relations": [{"src": "A", "dst": "A"}]})
    assert isinstance(ex.entities, list)


def test_overlong_name_dropped():
    ex = normalize(_chunk(), _raw([{"name": "字" * 60, "type": "角色"}]))
    assert ex.entities == []


def test_extraction_roundtrip():
    ex = normalize(_chunk(), _raw(
        [{"name": "A", "type": "角色", "aliases": ["a"], "desc": "d"},
         {"name": "B", "type": "组织"}],
        [{"src": "A", "relation": "隶属于", "dst": "B",
          "evidence": "e", "confidence": 0.9}]))
    back = Extraction.from_dict(ex.to_dict())
    assert len(back.entities) == len(ex.entities)
    assert len(back.relations) == len(ex.relations)
    assert back.relations[0].relation == "隶属于"


# ── 提示词与缓存 ──

def test_user_prompt_contains_context():
    c = _chunk()
    p = build_user_prompt(c)
    assert c.chapter_title in p
    assert c.scene_title in p
    assert "维尔汀" in p
    assert c.text in p


def test_cache_key_varies_by_model_and_prompt():
    c = _chunk()
    base = cache_key(c, "m1", "v1")
    assert cache_key(c, "m2", "v1") != base
    assert cache_key(c, "m1", "v2") != base
    assert cache_key(c, "m1", "v1") == base


def test_cache_stores_raw_and_normalizes_on_read(tmp_path):
    """缓存必须存**模型原始输出**，而不是归一化结果。

    理由（实测教训）：存归一化结果时，一旦调整去噪规则，缓存里全是旧规则
    产物，必须整库重跑云端抽取。存 raw 后改规则零成本。
    """
    cache = ExtractionCache(tmp_path)
    key = "abcdef123456"
    raw = _raw([{"name": "高个子", "type": "角色"},   # 噪声名，当前规则会剔除
                {"name": "维尔汀", "type": "角色"}])
    cache.put_raw(key, raw)

    got_raw = cache.get_raw(key)
    assert got_raw == raw, "读出的必须是原始输出（含噪声名）"

    # 归一化发生在读取之后，按当前规则过滤
    ex = normalize(_chunk(), got_raw)
    assert all(e.name != "高个子" for e in ex.entities)
    assert any(e.name == "维尔汀" for e in ex.entities)


def test_cache_roundtrip(tmp_path):
    cache = ExtractionCache(tmp_path)
    ex = normalize(_chunk(), _raw([{"name": "A", "type": "角色"}]))
    key = "abcdef123456"
    assert cache.get_raw(key) is None
    assert cache.misses == 1
    cache.put(key, ex)
    assert cache.get_raw(key) is not None
    assert cache.hits == 1


def test_cache_rejects_legacy_format(tmp_path):
    """旧格式（直接存归一化结果）必须视为未命中，避免新旧规则混用。"""
    cache = ExtractionCache(tmp_path)
    key = "legacy123456"
    p = cache.root / key[:2] / f"{key}.json"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps({"entities": [], "relations": []}), encoding="utf-8")
    assert cache.get_raw(key) is None
    assert cache.misses == 1


def test_cache_key_ignores_normalizer_version(tmp_path):
    """缓存键不含归一化版本——这是「改归一化免费生效」的前提。"""
    c = _chunk()
    assert cache_key(c, "m", "v3") == cache_key(c, "m", "v3")


def test_cache_corrupt_file_is_miss(tmp_path):
    cache = ExtractionCache(tmp_path)
    key = "badbadbadbad"
    p = cache.root / key[:2] / f"{key}.json"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text("{not json", encoding="utf-8")
    assert cache.get_raw(key) is None


def test_prompt_version_is_v3():
    assert PROMPT_VERSION.startswith("v3")
