# -*- coding: utf-8 -*-
"""图谱存储测试：实体归一、边合并、来源溯源、指纹、落盘往返。"""
from __future__ import annotations

import json

import pytest

from compendium_rag.extract import ExtractedEntity, ExtractedRelation, Extraction
from compendium_rag.graph_store import (SCHEMA_VERSION, Edge, Entity, GraphStore,
                                        canonical_pick, fingerprint_of)


def _ex(ents, rels):
    return Extraction(
        entities=[ExtractedEntity(n, t, a, d) for n, t, a, d in ents],
        relations=[ExtractedRelation(s, r, d, ev, c) for s, r, d, ev, c in rels])


def _store():
    return GraphStore(fingerprint="fp-test")


def test_build_basic():
    g = _store()
    per = [
        ("c1", _ex([("维尔汀", "角色", [], "主角"), ("基金会", "组织", [], "")],
                   [("维尔汀", "隶属于", "基金会", "她是基金会的", 0.9)])),
    ]
    st = g.build_from_extractions(per)
    assert st["entities"] == 2
    assert st["edges"] == 1
    assert g.resolve("维尔汀")


def test_edge_carries_evidence_and_chunks():
    """边必须可溯源到原文块——图谱不产生幻觉的底线。"""
    g = _store()
    g.build_from_extractions([
        ("c1", _ex([("A", "角色", [], ""), ("B", "角色", [], "")],
                   [("A", "杀死", "B", "A捅了B", 0.9)])),
    ])
    e = g.edges[0]
    assert e.chunk_ids == ["c1"]
    assert e.evidence == "A捅了B"


def test_same_triple_merges_and_counts():
    g = _store()
    g.build_from_extractions([
        ("c1", _ex([("A", "角色", [], ""), ("B", "角色", [], "")],
                   [("A", "杀死", "B", "证据1", 0.8)])),
        ("c2", _ex([("A", "角色", [], ""), ("B", "角色", [], "")],
                   [("A", "杀死", "B", "证据2", 0.95)])),
    ])
    assert len(g.edges) == 1
    e = g.edges[0]
    assert e.count == 2
    assert sorted(e.chunk_ids) == ["c1", "c2"]
    assert e.confidence == 0.95, "置信度取最大值"


def test_self_loop_dropped():
    g = _store()
    g.build_from_extractions([
        ("c1", _ex([("A", "角色", [], "")],
                   [("A", "认识", "A", "", 0.9)])),
    ])
    assert g.edges == []


def test_alias_declaration_merges_entities():
    g = _store()
    g.build_from_extractions([
        ("c1", _ex([("维尔汀", "角色", ["汀汀"], "")], [])),
        ("c2", _ex([("汀汀", "角色", [], "")], [])),
    ])
    assert g.resolve("维尔汀") == g.resolve("汀汀")
    assert len(g.entities) == 1


def test_fullname_shortname_merge():
    """`伊索尔德` 与 `伊索尔德·冯·迪塔斯多夫` 应归并为同一实体。"""
    g = _store()
    g.build_from_extractions([
        ("c1", _ex([("伊索尔德", "角色", [], "")], [])),
        ("c2", _ex([("伊索尔德·冯·迪塔斯多夫", "角色", [], "")], [])),
    ])
    assert len(g.entities) == 1
    e = next(iter(g.entities.values()))
    assert e.name == "伊索尔德·冯·迪塔斯多夫", "应保留更完整的全名"
    assert "伊索尔德" in e.aliases or g.resolve("伊索尔德") == e.eid


def test_no_false_merge_on_prefix():
    """`星锑` 与 `星锑号` 只共享前缀、无分隔符，不应强行合并。"""
    g = _store()
    g.build_from_extractions([
        ("c1", _ex([("星锑", "角色", [], ""), ("星锑号", "物品", [], "")], [])),
    ])
    assert len(g.entities) == 2


def test_entity_type_majority_vote():
    g = _store()
    g.build_from_extractions([
        ("c1", _ex([("X", "角色", [], "")], [])),
        ("c2", _ex([("X", "角色", [], "")], [])),
        ("c3", _ex([("X", "概念", [], "")], [])),
    ])
    e = next(iter(g.entities.values()))
    assert e.type == "角色"


def test_mentions_counted():
    g = _store()
    g.build_from_extractions([
        ("c1", _ex([("A", "角色", [], "")], [])),
        ("c2", _ex([("A", "角色", [], "")], [])),
    ])
    e = next(iter(g.entities.values()))
    assert e.mentions == 2
    assert sorted(e.chunk_ids) == ["c1", "c2"]


def test_failed_extraction_skipped():
    g = _store()
    bad = Extraction(ok=False, error="boom")
    g.build_from_extractions([("c1", bad)])
    assert g.entities == {} and g.edges == []


def test_min_confidence_filter():
    g = _store()
    g.build_from_extractions([
        ("c1", _ex([("A", "角色", [], ""), ("B", "角色", [], "")],
                   [("A", "弱关系", "B", "", 0.2)])),
    ], min_confidence=0.5)
    assert g.edges == []


def test_relations_mentioning_speaker_add_entity():
    """关系端点是可靠说话人、但未在 entities 声明时，应自动补实体保证边可解析。"""
    g = _store()
    g.build_from_extractions([
        ("c1", _ex([("A", "角色", [], "")],
                   [("A", "认识", "B", "", 0.9)])),
    ])
    assert g.resolve("B") is not None
    assert len(g.edges) == 1


# ── G3：关系端点算提及（契约对称性修复，2026-10-21）──
#
# 旧实现只看 `ex.entities`（块内显式声明）。「在某块里只作为关系 src/dst
# 出现、却没被该块声明」的实体，其 chunk_ids 里没有那个块 —— `mention_channel`
# 于是永久取不到它。这三条用例把修复钉死；**不得**把它们写成「召回提升」。

def test_endpoint_entity_counts_as_mention():
    """只作关系端点出现的实体，其出现块必须被记进 chunk_ids。"""
    g = _store()
    g.build_from_extractions([
        # c1：B 只作关系端点，未被声明
        ("c1", _ex([("A", "角色", [], "")], [("A", "认识", "B", "", 0.9)])),
    ])
    eid = g.resolve("B")
    assert eid is not None, "端点应被补成实体（既有行为）"
    b = g.entities[eid]
    assert "c1" in b.chunk_ids, "端点出现块是提及盲区（G3 未修复）"


def test_endpoint_mention_deduped_against_declaration():
    """同块内既声明又作端点 → 只计一次提及（不重复计数）。"""
    g = _store()
    g.build_from_extractions([
        ("c1", _ex([("A", "角色", [], ""), ("B", "角色", [], "")],
                   [("A", "认识", "B", "", 0.9)])),
    ])
    for name in ("A", "B"):
        eid = g.resolve(name)
        assert eid is not None
        e = g.entities[eid]
        assert e.mentions == 1, f"{name} 提及被重复计数：{e.mentions}"
        assert e.chunk_ids == ["c1"]


def test_mention_chunk_ids_order_is_deterministic():
    """chunk_ids 必须按**语料块序**排，而非「先声明块、后端点块」的追加序。

    ② 关系端点在① 全部声明之后才追加，若不排序，端点块会一律排到声明块
    之后（这里会得到 ['c1','c3','c2']），而 `mention_channel` 取
    `cids[:per_entity]`，截断结果就会与语料顺序无关地漂移。
    """
    g = _store()
    g.build_from_extractions([
        ("c1", _ex([("A", "角色", [], "")], [])),                       # 声明
        ("c2", _ex([("X", "角色", [], "")],
                   [("A", "认识", "X", "", 0.9)])),                     # 仅端点
        ("c3", _ex([("A", "角色", [], "")], [])),                       # 声明
    ])
    eid = g.resolve("A")
    assert eid is not None
    assert g.entities[eid].chunk_ids == ["c1", "c2", "c3"], \
        f"chunk_ids 未按语料块序确定化：{g.entities[eid].chunk_ids}"

    # 同一语料重复构建必须逐位相同（暖进程/冷启动恒等）
    g2 = _store()
    g2.build_from_extractions([
        ("c1", _ex([("A", "角色", [], "")], [])),
        ("c2", _ex([("X", "角色", [], "")],
                   [("A", "认识", "X", "", 0.9)])),
        ("c3", _ex([("A", "角色", [], "")], [])),
    ])
    eid2 = g2.resolve("A")
    assert eid2 is not None
    assert g2.entities[eid2].chunk_ids == g.entities[eid].chunk_ids


# ── 查询 ──

def test_neighbors_both_directions():
    g = _store()
    g.build_from_extractions([
        ("c1", _ex([("A", "角色", [], ""), ("B", "角色", [], "")],
                   [("A", "认识", "B", "", 0.9)])),
    ])
    a, b = g.resolve("A"), g.resolve("B")
    assert len(g.neighbors(a)) == 1
    assert len(g.neighbors(b)) == 1, "邻居应双向可见"
    assert len(g.out_edges(b)) == 0, "出边应保持方向性"


def test_resolve_unknown_returns_none():
    assert _store().resolve("不存在") is None
    assert _store().resolve("") is None


def test_edge_chunk_ids_index():
    g = _store()
    g.build_from_extractions([
        ("c1", _ex([("A", "角色", [], ""), ("B", "角色", [], "")],
                   [("A", "认识", "B", "", 0.9)])),
    ])
    idx = g.edge_chunk_ids()
    assert "c1" in idx and idx["c1"] == [0]


# ── 持久化 ──

def test_roundtrip(tmp_path):
    g = _store()
    g.build_from_extractions([
        ("c1", _ex([("维尔汀", "角色", ["汀汀"], "主角")],
                   [("维尔汀", "隶属于", "基金会", "证据", 0.9)])),
    ])
    p = tmp_path / "graph.json"
    g.save(p)
    back = GraphStore.load(p)
    assert back.fingerprint == g.fingerprint
    assert len(back.entities) == len(g.entities)
    assert len(back.edges) == len(g.edges)
    assert back.resolve("汀汀") == g.resolve("汀汀")
    assert back.entities[g.resolve("维尔汀")].desc == "主角"


def test_saved_schema_and_fingerprint(tmp_path):
    g = _store()
    g.build_from_extractions([])
    p = tmp_path / "g.json"
    g.save(p)
    d = json.loads(p.read_text(encoding="utf-8"))
    assert d["schema"] == f"compendium_rag.graph/v{SCHEMA_VERSION}"
    assert d["fingerprint"] == "fp-test"


def test_atomic_write_no_tmp_left(tmp_path):
    g = _store()
    g.build_from_extractions([])
    p = tmp_path / "g.json"
    g.save(p)
    assert p.exists()
    assert not (tmp_path / "g.json.tmp").exists()


# ── 指纹 ──

def test_fingerprint_changes_on_every_input():
    base = fingerprint_of("corpusA", "modelX", "v2", 900)
    assert fingerprint_of("corpusB", "modelX", "v2", 900) != base
    assert fingerprint_of("corpusA", "modelY", "v2", 900) != base
    assert fingerprint_of("corpusA", "modelX", "v3", 900) != base
    assert fingerprint_of("corpusA", "modelX", "v2", 800) != base


def test_fingerprint_stable():
    assert fingerprint_of("c", "m", "v", 1) == fingerprint_of("c", "m", "v", 1)


def test_check_fingerprint(tmp_path):
    g = _store()
    ok, why = g.check_fingerprint("fp-test")
    assert ok and why == "ok"
    ok, why = g.check_fingerprint("other")
    assert not ok and "不匹配" in why
    assert not GraphStore().check_fingerprint("x")[0], "空指纹应拒绝"


# ── 统计 ──

def test_stats_shape_and_isolation():
    g = _store()
    g.build_from_extractions([
        ("c1", _ex([("A", "角色", [], ""), ("B", "组织", [], ""),
                    ("孤岛", "概念", [], "")],
                   [("A", "隶属于", "B", "", 0.9)])),
    ])
    st = g.stats()
    assert st["entities"] == 3
    assert st["edges"] == 1
    assert st["isolated_entities"] == 1
    assert st["entity_types"]["角色"] == 1
    assert 0 <= st["isolated_ratio"] <= 1


def test_canonical_pick_prefers_full_name():
    assert canonical_pick(["伊索尔德", "伊索尔德·冯·迪塔斯多夫"]) == \
        "伊索尔德·冯·迪塔斯多夫"


def test_canonical_pick_stable():
    members = ["A", "B"]
    assert canonical_pick(members) == canonical_pick(list(reversed(members)))


def test_canonical_pick_prefers_most_frequent():
    """出现次数优先于形态规则。

    回归：`重塑之手`（组织，语料 37 次）曾被选成 `重塑·信徒`（杂兵标签），
    因为旧实现只看"含分隔符 + 更长"。次数是最可靠的规范化依据。
    """
    got = canonical_pick(["重塑·信徒", "重塑之手"],
                         {"重塑·信徒": 3, "重塑之手": 37})
    assert got == "重塑之手"


# ── 「组织·成员角色」不得合并（实测语义错误）──

def test_org_member_construct_not_merged():
    """`重塑` + `·信徒` 是"某组织的一名信徒"，不是 `名·姓` 全名。

    实测该构造把敌对组织「重塑之手」与其无名杂兵合并成同一实体，
    是语义错误（一个组织 ≠ 它的士兵）。GENERIC_ROLE_SUFFIX 挡掉这类尾词。
    """
    g = _store()
    g.build_from_extractions([
        ("c1", _ex([("重塑之手", "组织", [], ""),
                    ("重塑·信徒", "角色", [], "")], [])),
    ])
    assert len(g.entities) == 2, "组织与其杂兵不应合并"
    assert g.resolve("重塑之手") != g.resolve("重塑·信徒")


@pytest.mark.parametrize("member", [
    "重塑·信徒", "重塑·门徒", "重塑·暴徒", "重塑·坏蛋", "重塑·手下",
    "重塑·门徒Ⅰ", "重塑·门徒Ⅳ", "重塑·士兵2",   # 带编号的同构造（实测漏判）
])
def test_all_org_member_variants_kept_separate(member):
    g = _store()
    g.build_from_extractions([
        ("c1", _ex([("重塑", "组织", [], ""), (member, "角色", [], "")], [])),
    ])
    assert g.resolve("重塑") != g.resolve(member)


def test_real_full_name_still_merges_after_fix():
    """修 `组织·成员` 的同时，不能破坏真正的 `名·姓` 全名归并。"""
    g = _store()
    g.build_from_extractions([
        ("c1", _ex([("伊索尔德", "角色", [], ""),
                    ("伊索尔德·冯·迪塔斯多夫", "角色", [], "")], [])),
    ])
    assert len(g.entities) == 1
    assert g.resolve("伊索尔德") == g.resolve("伊索尔德·冯·迪塔斯多夫")


def test_partial_containment_never_merges():
    """部分包含（A ⊂ B，中间无分隔符）绝不合并——实测确认的行为。"""
    g = _store()
    g.build_from_extractions([
        ("c1", _ex([("决斗", "事件", [], ""),
                    ("决斗观赏赛", "事件", [], ""),
                    ("切尔西", "地点", [], ""),
                    ("切尔西花展", "事件", [], ""),
                    ("瞭望塔", "地点", [], ""),
                    ("中心瞭望塔", "地点", [], "")], [])),
    ])
    assert len(g.entities) == 6, "部分包含不得合并"


def test_all_edges_have_evidence_and_chunks():
    """图谱的硬要求：每条边都可溯源（无 evidence/chunk 的边不允许存在）。"""
    g = _store()
    g.build_from_extractions([
        ("c1", _ex([("A", "角色", [], ""), ("B", "角色", [], "")],
                   [("A", "认识", "B", "证据一", 0.9)])),
        ("c2", _ex([("A", "角色", [], ""), ("C", "角色", [], "")],
                   [("A", "认识", "C", "证据二", 0.9)])),
    ])
    assert g.edges
    assert all(e.evidence for e in g.edges)
    assert all(e.chunk_ids for e in g.edges)
