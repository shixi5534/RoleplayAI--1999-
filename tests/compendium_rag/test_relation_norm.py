# -*- coding: utf-8 -*-
"""谓语受控化策略测试（P1）：方向优先于合规。

全部离线。核心不变量有三条：
1. **不写反事实**——方向敏感谓语没有人工裁决时保留原形，宁缺合规率；
2. **不销毁证据**——只有否定式/黑名单才丢边，长尾未映射一律保留原谓语；
3. **裁决可追溯**——被阻断的边照实记录「本该并成什么」，好生成待办清单。
"""
from __future__ import annotations

import json

import pytest

from compendium_rag.relation_norm import (DIRECTION_POLICY_PATH, DROP_REASONS,
                                          INVERSE_MAP_PATH, OVERRIDES_PATH,
                                          DirectionPolicy, Mapped, VocabTables,
                                          default_tables, map_relation)


def _t(**kw) -> VocabTables:
    return VocabTables(**kw)


# ── 基本判定 ──

def test_canonical_passthrough():
    m = map_relation("甲", "杀死", "乙", tables=_t())
    assert m == Mapped("甲", "杀死", "乙", "canonical", "杀死")


def test_synonym_merge_keeps_direction():
    # 「相关」不在方向敏感表里 → 直接并成 canonical「关联」
    m = map_relation("甲", "相关", "乙", tables=_t())
    assert (m.relation, m.code) == ("关联", "synonym")
    assert (m.src, m.dst) == ("甲", "乙")


def test_override_table_used_when_vocab_gives_up():
    m = map_relation("甲", "自陈", "乙", tables=_t(overrides={"自陈": "告知"}))
    assert (m.relation, m.code) == ("告知", "override")


def test_unmapped_long_tail_keeps_original_predicate():
    """长尾不丢、不改哨兵：删边等于销毁证据。"""
    m = map_relation("甲", "追杀于城中", "乙", tables=_t())
    assert m.relation == "追杀于城中"
    assert m.code == "kept:review:unmapped"
    assert m.intended == ""


@pytest.mark.parametrize("rel,code", [("不是朋友", "drop:negation"),
                                      ("不隶属于", "drop:junk")])
def test_only_unsound_predicates_are_dropped(rel, code):
    m = map_relation("甲", rel, "乙", tables=_t())
    assert m.relation == ""
    assert m.code == code
    assert code in DROP_REASONS


# ── 方向闸 ──

def test_direction_sensitive_merge_blocked_without_adjudication():
    t = _t(watch=frozenset({"隶属于"}))
    m = map_relation("甲", "隶属于", "乙", tables=t)
    assert (m.src, m.relation, m.dst) == ("甲", "隶属于", "乙")
    assert m.code == "kept:direction_blocked"
    assert m.intended == "隶属"      # 待办清单靠这个字段


def test_inverse_pair_alone_triggers_block():
    t = _t(inverse_pairs=frozenset({frozenset(("隶属于", "隶属"))}))
    assert map_relation("甲", "隶属于", "乙", tables=t).code == "kept:direction_blocked"


def test_same_direction_adjudication_releases_block():
    t = _t(watch=frozenset({"隶属于"}),
           policy=DirectionPolicy(same_direction=frozenset({"隶属于"})))
    m = map_relation("甲", "隶属于", "乙", tables=t)
    assert (m.relation, m.code) == ("隶属", "same_direction")
    assert (m.src, m.dst) == ("甲", "乙")


def test_swap_adjudication_flips_endpoints():
    """「甲 师从 乙」= 「乙 指导 甲」：合并必须换端点，否则事实写反。"""
    t = _t(watch=frozenset({"师从"}),
           policy=DirectionPolicy(swap={"师从": "指导"}))
    m = map_relation("甲", "师从", "乙", tables=t)
    assert (m.src, m.relation, m.dst) == ("乙", "指导", "甲")
    assert m.code == "swap"


def test_swap_to_a_different_canonical_does_not_apply():
    t = _t(watch=frozenset({"隶属于"}), policy=DirectionPolicy(swap={"隶属于": "指导"}))
    m = map_relation("甲", "隶属于", "乙", tables=t)
    assert m.code == "kept:direction_blocked"
    assert (m.src, m.dst) == ("甲", "乙")


def test_watch_predicate_unmappable_by_vocab_stays_untouched():
    """「死于」在方向敏感表里，但词表映射不到 → 不进 override 就保留原谓语。"""
    t = _t(watch=frozenset({"死于"}))
    m = map_relation("甲", "死于", "乙", tables=t)
    assert (m.relation, m.code) == ("死于", "kept:review:unmapped")


# ── 表加载 ──

def test_missing_table_files_degrade_to_empty(tmp_path):
    t = VocabTables.load(tmp_path / "no1.json", tmp_path / "no2.json",
                         tmp_path / "no3.json")
    assert t.overrides == {} and t.watch == frozenset()
    assert t.inverse_pairs == frozenset() and t.policy.swap == {}
    # 词表本身仍然生效，只是没有 sidecar 与人工裁决
    assert map_relation("甲", "隶属于", "乙", tables=t).relation == "隶属"


def test_load_reads_sidecar_and_policy(tmp_path):
    (tmp_path / "g.json").write_text(json.dumps(
        {"mapping": {"自陈": {"canonical": "告知"}, "无对应": {"canonical": None}}},
        ensure_ascii=False), encoding="utf-8")
    (tmp_path / "i.json").write_text(json.dumps(
        {"direction_loss_watch": ["师从"], "inverse_pairs": [["师从", "指导"]]},
        ensure_ascii=False), encoding="utf-8")
    (tmp_path / "d.json").write_text(json.dumps(
        {"swap": {"师从": "指导"}, "same_direction": ["属于"]},
        ensure_ascii=False), encoding="utf-8")
    t = VocabTables.load(tmp_path / "g.json", tmp_path / "i.json", tmp_path / "d.json")
    assert t.overrides == {"自陈": "告知"}          # canonical=None 的不收
    assert t.watch == frozenset({"师从"})
    assert t.inverse_pairs == frozenset({frozenset({"师从", "指导"})})
    assert map_relation("甲", "师从", "乙", tables=t) == Mapped(
        "乙", "指导", "甲", "swap", "指导")


def test_default_tables_is_process_singleton():
    assert default_tables() is default_tables()


def test_real_table_files_are_present_and_adjudicated():
    """数据文件跟着包走（D1：vendored）。丢了这条就该红。"""
    for p in (OVERRIDES_PATH, INVERSE_MAP_PATH, DIRECTION_POLICY_PATH):
        assert p.exists(), p
    t = default_tables()
    assert len(t.overrides) > 1000
    assert t.policy.swap == {"师从": "指导"}
    assert "隶属于" in t.policy.same_direction


def test_real_tables_block_only_adjudicated_leftovers():
    """现网三张表下，方向闸只剩「被称为」这一条待人工看原文。"""
    t = default_tables()
    assert map_relation("甲", "被称为", "乙", tables=t).code == "kept:direction_blocked"
    for rel in ("师从", "隶属于", "属于", "从属", "代表", "源自"):
        assert map_relation("甲", rel, "乙", tables=t).code != "kept:direction_blocked"
