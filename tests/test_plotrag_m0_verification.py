"""M0/N0 改动的**独立验证**测试（QA 复核，与实现者自测互为补充）。

与 ``test_plotrag_m0_hardening.py`` 的定位差别：那份是实现者的「功能存在性」
自测；本文件走**错误路径 / 边界条件 / 差分对照**，重点回答「改完之后行为和
改之前是否逐字节一致」，以及「安全网在真实故障形态下是否真的拦得住」。

覆盖：
- N0-3  ``_edge_idx`` 边索引：与线性扫描参考实现随机差分、remove_by_doc 后
        索引一致性、连续 upsert 的 evidence 并集顺序、索引不落盘
- M0-2  空图覆盖保护：损坏 / 结构不符 / 文件不存在 / 内存清空四种落盘决策
- N0-1  版本号三分支解析：正例 + 反例不误判
- N0-2  source_kind：老语料向后兼容、非法值兜底、分级优先级、检索路径未改
- M0-3  ``--strict`` 门禁：默认恒 0（不破既有调用方）+ 各项不达标均能拦下
- M0-4  no-op 检测：``_graph_snapshot`` 四情形 + ``_is_noop`` + --rebuild 豁免
- M0-1  归档脚本：实跑一次，独立复算 sha256 校验 INDEX.md 且源文件零改动
"""
from __future__ import annotations

import hashlib
import importlib.util
import json
import random
import re
import subprocess
import sys
from collections import Counter
from pathlib import Path

import pytest

from roleplay.core.knowledge.graph_store import GraphStore
from roleplay.core.knowledge.plot_corpus import (
    RE_VERSION,
    SOURCE_KIND_ANALYSIS,
    SOURCE_KIND_CANON,
    SOURCE_KIND_OFFICIAL,
    SOURCE_KINDS,
    PlotChunk,
    PlotCorpus,
    classify_source_kind,
    parse_title_meta,
)
from roleplay.core.knowledge.plot_graph import (
    _coerce_aliases,
    load_alias_table_with_stats,
)

ROOT = Path(__file__).resolve().parent.parent


def _load_script(name: str):
    """按文件路径加载 scripts/ 下的脚本（它们不是包，无法 import）。"""
    spec = importlib.util.spec_from_file_location(f"_qa_{name}", ROOT / "scripts" / name)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)  # type: ignore[union-attr]
    return mod


def _sha256(path: Path) -> str:
    """独立复算文件 sha256（不复用被测脚本自己的实现，避免自证）。"""
    digest = hashlib.sha256()
    with Path(path).open("rb") as fp:
        for block in iter(lambda: fp.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


# ══════════════════════════════════════════════════════════════════════════
# N0-3：_edge_idx 边索引（最高优先级：O(1) 化最容易出静默 bug）
# ══════════════════════════════════════════════════════════════════════════


def _ref_dedupe_evidence(evidence: list[dict]) -> list[dict]:
    """参考实现的 evidence 归一化：去重 + 去空 hash + 保持插入顺序。"""
    seen: set[tuple] = set()
    out: list[dict] = []
    for ev in evidence:
        key = (ev.get("ns"), ev.get("doc_id"), ev.get("hash"))
        if not key[2] or key in seen:
            continue
        seen.add(key)
        out.append({"ns": key[0], "doc_id": key[1], "hash": key[2]})
    return out


def _ref_upsert(edges, *, src, dst, relation, confidence, importance, evidence):
    """改造前的线性扫描版 upsert_edge（作为语义黄金参考）。"""
    evidence = _ref_dedupe_evidence(evidence)
    for e in edges:
        if e["src"] == src and e["dst"] == dst and e["relation"] == relation:
            e["confidence"] = max(e["confidence"], confidence)
            e["importance"] = max(e.get("importance", 0.7), importance)
            seen = {(x["ns"], x["doc_id"], x["hash"]) for x in e["evidence"]}
            e["evidence"] = e["evidence"] + [
                x
                for x in evidence
                if (x["ns"], x["doc_id"], x["hash"]) not in seen
            ]
            return
    edges.append(
        {
            "src": src,
            "dst": dst,
            "relation": relation,
            "confidence": round(confidence, 4),
            "importance": importance,
            "evidence": evidence,
            "ts": 0.0,
            "source": "lore",
        }
    )


def _ref_remove(edges, ns: str, doc_id: str) -> list[dict]:
    """改造前的 remove_by_doc 边表部分（作为语义黄金参考）。"""
    kept = []
    for e in edges:
        ev = e["evidence"]
        if ev and all(x["ns"] == ns and x["doc_id"] == doc_id for x in ev):
            continue
        e["evidence"] = [
            x for x in ev if not (x["ns"] == ns and x["doc_id"] == doc_id)
        ]
        kept.append(e)
    return kept


class TestN03EdgeIndex:
    """边索引 O(1) 化的语义等价性与一致性。"""

    def test_index_matches_linear_scan_reference_random_differential(self, tmp_path):
        """随机差分：索引实现与线性扫描参考实现在 40 轮 × 100 次操作后逐边一致。

        这是本轮改动风险最高的一项——索引一旦与边表不同步，症状是「边悄悄
        不再合并 / evidence 丢失」，不会报错，只能靠差分对照发现。
        """
        rng = random.Random(20260911)
        compared = 0
        for trial in range(40):
            path = tmp_path / f"g{trial}.json"
            store = GraphStore(path, min_confidence=0.0)
            ref: list[dict] = []
            for _ in range(100):
                src = f"e_{rng.randint(0, 7)}"
                dst = f"e_{rng.randint(0, 7)}"
                relation = rng.choice(["r1", "r2", "r3"])
                if src == dst:
                    continue
                confidence = round(rng.uniform(0.0, 1.0), 3)
                importance = round(rng.uniform(0.0, 1.0), 3)
                evidence = [
                    {
                        "ns": "ns",
                        "doc_id": f"d{rng.randint(0, 4)}",
                        "hash": f"h{rng.randint(0, 9)}",
                    }
                    for _ in range(rng.randint(0, 3))
                ]
                store.upsert_edge(
                    src=src,
                    dst=dst,
                    relation=relation,
                    confidence=confidence,
                    importance=importance,
                    evidence=evidence,
                    ts=0.0,
                )
                _ref_upsert(
                    ref,
                    src=src,
                    dst=dst,
                    relation=relation,
                    confidence=confidence,
                    importance=importance,
                    evidence=evidence,
                )
            for _ in range(rng.randint(0, 4)):
                doc = f"d{rng.randint(0, 4)}"
                store.remove_by_doc("ns", doc)
                ref = _ref_remove(ref, "ns", doc)

            got = store.all_edges()
            assert len(got) == len(ref), f"trial {trial}: 边数 {len(got)} != {len(ref)}"
            for a, b in zip(got, ref):
                assert (a["src"], a["dst"], a["relation"]) == (
                    b["src"],
                    b["dst"],
                    b["relation"],
                )
                assert a["confidence"] == pytest.approx(b["confidence"])
                assert a["importance"] == pytest.approx(b["importance"])
                # evidence 既要不重复，也要不丢失，还要保持插入顺序
                assert a["evidence"] == b["evidence"], (
                    f"trial {trial}: evidence 不一致\n索引实现 {a['evidence']}\n"
                    f"参考实现 {b['evidence']}"
                )
            compared += len(got)
        assert compared > 0

    def test_index_points_to_same_object_as_linear_first_match(self, tmp_path):
        """索引里每个键指向的对象，必须与线性扫描「首现」的那条边是同一个。"""
        store = GraphStore(tmp_path / "g.json", min_confidence=0.0)
        for i in range(30):
            store.upsert_edge(
                src=f"a{i % 5}",
                dst=f"b{i % 4}",
                relation=f"r{i % 3}",
                confidence=0.9,
                evidence=[{"ns": "x", "doc_id": "d", "hash": f"h{i}"}],
                ts=0.0,
            )
        linear: dict[tuple[str, str, str], dict] = {}
        for e in store.all_edges():
            linear.setdefault((e["src"], e["dst"], e["relation"]), e)

        assert set(store._edge_idx) == set(linear)
        for key, edge in linear.items():
            assert store._edge_idx[key] is edge, f"索引与线性首现不是同一对象：{key}"

    def test_index_stays_correct_after_remove_by_doc(self, tmp_path):
        """remove_by_doc 换掉边表后，索引重建必须与剩余边表完全对应。"""
        store = GraphStore(tmp_path / "g.json", min_confidence=0.0)
        # e1 的证据全部来自 doomed → 会被整条删掉；e2 有跨文档证据 → 保留
        store.upsert_edge(
            src="A", dst="B", relation="r", confidence=0.9,
            evidence=[{"ns": "ns", "doc_id": "doomed", "hash": "h1"}], ts=0.0,
        )
        store.upsert_edge(
            src="C", dst="D", relation="r", confidence=0.9,
            evidence=[
                {"ns": "ns", "doc_id": "doomed", "hash": "h2"},
                {"ns": "ns", "doc_id": "keeper", "hash": "h3"},
            ],
            ts=0.0,
        )
        assert len(store.all_edges()) == 2

        removed = store.remove_by_doc("ns", "doomed")
        assert removed == 1
        assert len(store.all_edges()) == 1

        # 索引不能残留已删边，且必须与线性首现同对象
        linear: dict[tuple[str, str, str], dict] = {}
        for e in store.all_edges():
            linear.setdefault((e["src"], e["dst"], e["relation"]), e)
        assert set(store._edge_idx) == set(linear)
        for key, edge in linear.items():
            assert store._edge_idx[key] is edge
        assert ("A", "B", "r") not in store._edge_idx

        # 删完还能继续正确合并：不应因索引陈旧而新建一条重复边
        store.upsert_edge(
            src="C", dst="D", relation="r", confidence=0.95,
            evidence=[{"ns": "ns", "doc_id": "keeper", "hash": "h4"}], ts=0.0,
        )
        assert len(store.all_edges()) == 1, "索引陈旧导致同键边重复插入"
        edge = store.all_edges()[0]
        assert edge["confidence"] == pytest.approx(0.95)
        assert [x["hash"] for x in edge["evidence"]] == ["h3", "h4"]

    def test_repeated_upsert_keeps_evidence_union_and_insertion_order(self, tmp_path):
        """连续 upsert 同一条边：evidence 取并集、不重复、顺序稳定、confidence 取 max。"""
        store = GraphStore(tmp_path / "g.json", min_confidence=0.0)
        for i, (conf, imp) in enumerate([(0.6, 0.5), (0.9, 0.2), (0.7, 0.95)]):
            store.upsert_edge(
                src="A", dst="B", relation="r",
                confidence=conf, importance=imp,
                evidence=[{"ns": "ns", "doc_id": f"d{i}", "hash": f"h{i}"}],
                ts=0.0,
            )
        assert len(store.all_edges()) == 1
        edge = store.all_edges()[0]
        assert [x["hash"] for x in edge["evidence"]] == ["h0", "h1", "h2"]

        # 重复灌入已存在的证据 → 不重复追加
        store.upsert_edge(
            src="A", dst="B", relation="r", confidence=0.6,
            evidence=[
                {"ns": "ns", "doc_id": "d1", "hash": "h1"},
                {"ns": "ns", "doc_id": "d2", "hash": "h2"},
                {"ns": "ns", "doc_id": "d9", "hash": "h9"},
            ],
            ts=0.0,
        )
        assert len(store.all_edges()) == 1
        assert [x["hash"] for x in store.all_edges()[0]["evidence"]] == [
            "h0", "h1", "h2", "h9",
        ]
        # confidence / importance 取 max
        assert store.all_edges()[0]["confidence"] == pytest.approx(0.9)
        assert store.all_edges()[0]["importance"] == pytest.approx(0.95)

    def test_duplicate_evidence_within_single_call_is_deduped(self, tmp_path):
        """同一次调用里传入重复 evidence，应只保留一条（与参考实现同口径）。"""
        store = GraphStore(tmp_path / "g.json", min_confidence=0.0)
        store.upsert_edge(
            src="A", dst="B", relation="r", confidence=0.9,
            evidence=[
                {"ns": "ns", "doc_id": "d", "hash": "h1"},
                {"ns": "ns", "doc_id": "d", "hash": "h1"},
                {"ns": "ns", "doc_id": "d", "hash": ""},  # 空 hash 证据应被丢弃
            ],
            ts=0.0,
        )
        assert [x["hash"] for x in store.all_edges()[0]["evidence"]] == ["h1"]

    def test_edge_index_is_not_persisted(self, tmp_path):
        """_edge_idx 只活在内存：落盘 JSON 仍只有原来 5 个键。"""
        path = tmp_path / "g.json"
        store = GraphStore(path, min_confidence=0.0)
        store.upsert_entities([{"name": "A"}, {"name": "B"}])
        store.upsert_edge(
            src=store.link_exact("A"), dst=store.link_exact("B"),
            relation="r", confidence=0.9,
            evidence=[{"ns": "ns", "doc_id": "d", "hash": "h"}], ts=0.0,
        )
        assert len(store._edge_idx) == 1
        store.save()

        raw = json.loads(path.read_text(encoding="utf-8"))
        assert sorted(raw.keys()) == [
            "alias_index", "anchored", "edges", "entities", "fingerprint",
        ]
        assert "_edge_idx" not in raw
        # 重新加载后索引自动重建，边不丢
        reloaded = GraphStore(path, min_confidence=0.0)
        assert len(reloaded.all_edges()) == 1
        assert set(reloaded._edge_idx) == {
            (store.link_exact("A"), store.link_exact("B"), "r")
        }

    def test_save_load_roundtrip_preserves_merge_semantics(self, tmp_path):
        """落盘→重载→再 upsert 同键边，仍然合并而不是新增。"""
        path = tmp_path / "g.json"
        store = GraphStore(path, min_confidence=0.0)
        store.upsert_edge(
            src="A", dst="B", relation="r", confidence=0.7,
            evidence=[{"ns": "ns", "doc_id": "d1", "hash": "h1"}], ts=0.0,
        )
        store.save()

        again = GraphStore(path, min_confidence=0.0)
        again.upsert_edge(
            src="A", dst="B", relation="r", confidence=0.8,
            evidence=[{"ns": "ns", "doc_id": "d2", "hash": "h2"}], ts=0.0,
        )
        assert len(again.all_edges()) == 1
        edge = again.all_edges()[0]
        assert edge["confidence"] == pytest.approx(0.8)
        assert [x["hash"] for x in edge["evidence"]] == ["h1", "h2"]

    def test_duplicate_keys_in_file_keep_first_after_reload(self, tmp_path):
        """文件里存在同键重复边时，重载后索引保留首条（与旧线性扫描一致）。"""
        path = tmp_path / "g.json"
        payload = {
            "fingerprint": {},
            "entities": {},
            "edges": [
                {"src": "A", "dst": "B", "relation": "r", "confidence": 0.9,
                 "importance": 0.7, "evidence": [{"ns": "n", "doc_id": "d", "hash": "first"}],
                 "ts": 1.0, "source": "lore"},
                {"src": "A", "dst": "B", "relation": "r", "confidence": 0.5,
                 "importance": 0.7, "evidence": [{"ns": "n", "doc_id": "d", "hash": "second"}],
                 "ts": 2.0, "source": "lore"},
            ],
            "alias_index": {},
            "anchored": [],
        }
        path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")

        store = GraphStore(path, min_confidence=0.0)
        assert store._edge_idx[("A", "B", "r")] is store._edges[0]
        # 合并必须落到首条上，而不是被索引选中之外的另一条
        store.upsert_edge(
            src="A", dst="B", relation="r", confidence=0.95,
            evidence=[{"ns": "n", "doc_id": "d", "hash": "third"}], ts=0.0,
        )
        assert len(store.all_edges()) == 2
        assert [x["hash"] for x in store._edges[0]["evidence"]] == ["first", "third"]
        assert [x["hash"] for x in store._edges[1]["evidence"]] == ["second"]


# ══════════════════════════════════════════════════════════════════════════
# M0-2：空图覆盖保护（防数据丢失的最后一道闸）
# ══════════════════════════════════════════════════════════════════════════


class TestM02EmptyGraphGuard:
    """加载异常 / 空图覆盖时的落盘拒绝逻辑。"""

    def _snapshot(self, path: Path) -> tuple[str, int, int]:
        st = path.stat()
        return _sha256(path), st.st_size, st.st_mtime_ns

    def test_corrupt_json_array_refuses_to_save(self, tmp_path):
        """模拟 data/knowledge 下那 4 个 2 字节文件（内容 ``[]``）的形态。"""
        path = tmp_path / "g.json"
        path.write_text("[]", encoding="utf-8")
        before = self._snapshot(path)

        store = GraphStore(path)
        assert store.load_error, "损坏文件必须记录 load_error"
        assert "顶层结构非法" in store.load_error
        store.save()

        assert self._snapshot(path) == before, "损坏文件上 save() 竟然写盘了"

    def test_malformed_json_text_refuses_to_save(self, tmp_path):
        """截断/非法的 JSON 文本同样必须拒绝落盘。"""
        path = tmp_path / "g.json"
        path.write_text('{"entities": {"a": {"name": "A"', encoding="utf-8")
        before = self._snapshot(path)

        store = GraphStore(path)
        assert store.load_error and "JSON 解析失败" in store.load_error
        store.save()
        assert self._snapshot(path) == before

    def test_missing_file_is_first_build_path_and_saves_normally(self, tmp_path):
        """文件不存在属首次构建：绝不能被安全网误伤，否则图谱根本建不起来。"""
        path = tmp_path / "not_exists.json"
        store = GraphStore(path)
        assert store.load_error is None, "文件不存在不应记 load_error"
        assert store.entities() == []

        store.upsert_entities([{"name": "A", "type": "角色"}])
        store.upsert_edge(
            src=store.link_exact("A"), dst=store.link_exact("A"),
            relation="r", confidence=0.9, ts=0.0,
        )
        store.save()

        assert path.exists(), "首次构建路径被误伤，图谱将永远建不起来"
        reloaded = GraphStore(path)
        assert reloaded.load_error is None
        assert [e["name"] for e in reloaded.entities()] == ["A"]

    def test_empty_object_file_is_treated_as_empty_graph_not_error(self, tmp_path):
        """``{}`` 是合法空图：必须允许继续 save，否则空图会永久锁死。"""
        path = tmp_path / "g.json"
        path.write_text("{}", encoding="utf-8")
        store = GraphStore(path)
        assert store.load_error is None
        store.upsert_entities([{"name": "A"}])
        store.save()
        assert json.loads(path.read_text(encoding="utf-8"))["entities"], "空图被锁死"

    def test_cleared_entities_refuses_to_save(self, tmp_path):
        """加载时有 N 个实体、落盘时内存实体为 0 → 拒绝写入。"""
        path = tmp_path / "g.json"
        store = GraphStore(path, min_confidence=0.0)
        store.upsert_entities([{"name": "A"}, {"name": "B"}])
        store.save()
        before = self._snapshot(path)

        reloaded = GraphStore(path)
        assert len(reloaded.entities()) == 2
        reloaded._entities.clear()
        reloaded.save()

        assert self._snapshot(path) == before, "内存实体被清空后仍然写盘了"

    def test_remove_by_doc_wiping_all_entities_refuses_to_save(self, tmp_path):
        """真实故障链：doc 重导入把实体清空 → save 必须拦住，不能固化成空图。"""
        path = tmp_path / "g.json"
        store = GraphStore(path, min_confidence=0.0)
        store.upsert_entities([{"name": "A"}, {"name": "B"}])
        store.upsert_edge(
            src=store.link_exact("A"), dst=store.link_exact("B"),
            relation="r", confidence=0.9,
            evidence=[{"ns": "ns", "doc_id": "d1", "hash": "h1"}], ts=0.0,
        )
        store.save()
        before = self._snapshot(path)

        reloaded = GraphStore(path, min_confidence=0.0)
        reloaded.remove_by_doc("ns", "d1")
        assert reloaded.entities() == []
        reloaded.save()
        assert self._snapshot(path) == before

    def test_anchored_entities_survive_and_save_allowed(self, tmp_path):
        """别名表锚定的零度实体不会被清，图非空时 save 应正常放行。"""
        path = tmp_path / "g.json"
        store = GraphStore(path, min_confidence=0.0)
        store.bind_alias_table({"无名者": ["Ms. Stranger"]})
        store.remove_by_doc("ns", "nonexistent")
        assert [e["name"] for e in store.entities()] == ["无名者"]
        store.save()
        assert json.loads(path.read_text(encoding="utf-8"))["entities"]

    def test_build_plot_graph_surfaces_load_error(self):
        """build_plot_graph 必须把「拒绝落盘」显式报出来，不能静默成功。

        （注意：scripts/build_graph.py 与 src/.../plot_graph.py:742 这两个
        save() 调用点当前**没有**检查 load_error，见 QA 报告「缺陷 2」。）
        """
        source = (ROOT / "scripts" / "build_plot_graph.py").read_text(encoding="utf-8")
        assert source.count("store.load_error") >= 2, (
            "build_plot_graph 未在建图前后检查 load_error，拒绝落盘会变成静默 no-op"
        )

    def test_object_without_graph_keys_is_rejected_as_structurally_invalid(self, tmp_path):
        """缺陷 1 修复后：合法 JSON object 但缺图谱键 → 记 load_error 且拒绝落盘。

        原用例（``..._is_currently_treated_as_empty_graph``）固化的是修复**前**
        的缺口行为：``{"foo": 1}`` 被当成空图，save() 把它覆盖成空图谱。
        现在 ``_load()`` 除顶层类型外还校验是否含 fingerprint/entities/edges/
        alias_index/anchored 任一已知键，故此处改为断言新行为。
        """
        path = tmp_path / "g.json"
        path.write_text('{"foo": 1}', encoding="utf-8")
        before = path.read_text(encoding="utf-8")
        store = GraphStore(path)
        assert store.load_error is not None, "缺图谱键的 object 必须判为结构非法"
        assert "结构非法" in store.load_error
        store.upsert_entities([{"name": "A"}])
        store.save()
        assert path.read_text(encoding="utf-8") == before, "结构非法文件被覆盖了"

    def test_object_with_one_graph_key_is_accepted(self, tmp_path):
        """只要含任一个图谱键即视为合法图谱文件（避免误伤正常文件）。"""
        for payload in (
            '{"entities": {}}',
            '{"edges": []}',
            '{"fingerprint": {"schema": "v1"}}',
            '{"alias_index": {}}',
            '{"anchored": []}',
        ):
            path = tmp_path / f"g_{abs(hash(payload))}.json"
            path.write_text(payload, encoding="utf-8")
            store = GraphStore(path)
            assert store.load_error is None, payload
            store.upsert_entities([{"name": "A"}])
            store.save()
            assert json.loads(path.read_text(encoding="utf-8"))["entities"], payload


# ══════════════════════════════════════════════════════════════════════════
# N0-1：版本号三分支解析
# ══════════════════════════════════════════════════════════════════════════


class TestN01VersionParsing:
    """标题版本号的三种实测形态 + 反向不误判。"""

    @pytest.mark.parametrize(
        "title,expected",
        [
            # ① 「N.N版本」
            ("【重返未来：1999】3.8版本「世纪末尺度」全剧情流程", "3.8"),
            ("1999_2.6版本主线「疯狂与文明」四剧情", "2.6"),
            ("3.8 版本「带空格」", "3.8"),
            # ② 「【N.N-…】」
            ("…全剧情【4K英配】（【1.1-活动】雷米特杯失窃案｜1~4）", "1.1"),
            ("【2.1-角色】Something", "2.1"),
            ("【1.0-主线】序章", "1.0"),
            ("【1.1－全角横线】", "1.1"),
            # ③ 「中配N.N」/「英配N.N」
            ("《重返未来1999》中配1.6【朔日手记】全剧情【4K】", "1.6"),
            ("英配2.6【xx】", "2.6"),
            ("日配3.1【xx】", "3.1"),
            ("韩配1.2【xx】", "1.2"),
        ],
    )
    def test_three_branches_parse(self, title, expected):
        assert parse_title_meta(title)["version"] == expected

    @pytest.mark.parametrize(
        "title",
        [
            "1.5小时",
            "2024.10 更新",
            "第1.2节",
            "p1.5",
            "时长 2.5小时",
            "共 3.5 集",
            "版本说明 1.0",
            "UP主闲聊 4.2 万粉",
            "随便一个标题",
            "",
        ],
    )
    def test_negative_cases_do_not_produce_version(self, title):
        """没有「小数 + 强上下文」的数字一律不能硬凑出版本号。"""
        assert parse_title_meta(title)["version"] == "", f"误判出版本号：{title!r}"

    def test_three_branches_are_mutually_exclusive_groups(self):
        """交替分支只会命中一个命名分组，便于取实际命中的那一条。"""
        cases = {
            "3.8版本": "v_tag",
            "【1.1-活动】": "v_bracket",
            "中配1.6": "v_dub",
        }
        for title, group in cases.items():
            m = RE_VERSION.search(title)
            assert m is not None, title
            assert m.group(group), f"{title} 应命中 {group}"
            matched = [g for g in ("v_tag", "v_bracket", "v_dub") if m.group(g)]
            assert matched == [group], f"{title} 命中了多个分组：{matched}"

    def test_real_corpus_version_distribution_has_no_anomalies(self):
        """拿真实 726 份转写标题跑一遍：无异常值、无小数当版本。"""
        root = ROOT / "data" / "lore" / "wu_ming_zhe" / "视频文案"
        if not root.is_dir():
            pytest.skip(f"缺少真实语料目录：{root}")

        titles: list[str] = []
        for p in sorted(root.rglob("*.md")):
            head = p.read_text(encoding="utf-8").partition("\n---\n")[0]
            for line in head.splitlines():
                if line.startswith("# "):
                    titles.append(line[2:].strip())
                    break
        if not titles:
            pytest.skip("未解析到任何标题")

        versions = [parse_title_meta(t)["version"] for t in titles]
        non_empty = [v for v in versions if v]
        # 每个解析出的版本号都必须是 N.N 形态
        for v in non_empty:
            assert re.fullmatch(r"\d+\.\d+", v), f"异常版本号：{v!r}"
            assert len(v) <= 6, f"版本号过长：{v!r}"
        # 不允许出现「全 0」这种明显是硬凑出来的值
        assert "0.0" not in non_empty

        # 实测分布（2026 全量审计）：592 + 76 + 24 命中，34 无小数
        branch = Counter()
        for t in titles:
            m = RE_VERSION.search(t)
            if not m:
                branch["none"] += 1
            elif m.group("v_tag"):
                branch["tag"] += 1
            elif m.group("v_bracket"):
                branch["bracket"] += 1
            elif m.group("v_dub"):
                branch["dub"] += 1
        assert sum(branch.values()) == len(titles)
        # 分支② 与 ③ 是这次新加的，必须真的有命中（否则等于没生效）
        assert branch["bracket"] > 0, "分支②【N.N-】零命中，改动未生效"
        assert branch["dub"] > 0, "分支③中英配零命中，改动未生效"


# ══════════════════════════════════════════════════════════════════════════
# N0-2：source_kind 向后兼容
# ══════════════════════════════════════════════════════════════════════════


class TestN02SourceKind:
    """来源分级字段：老语料兼容 + 非法值兜底 + 优先级 + 检索路径未改。"""

    def test_legacy_corpus_without_source_kind_defaults_to_canon(self):
        """真实老语料 2477 块没有 source_kind 字段：不报错、不丢块、全 canon。"""
        path = ROOT / "data" / "knowledge" / "plot_corpus_wu_ming_zhe.json"
        if not path.is_file():
            pytest.skip(f"缺少真实语料：{path}")
        raw = json.loads(path.read_text(encoding="utf-8"))
        chunks = raw.get("chunks") or []
        if not any("source_kind" in c for c in chunks):
            # 确认这确实是一份「老」语料，否则本用例失去意义
            corpus = PlotCorpus(path, character_id="wu_ming_zhe")
            assert len(corpus.chunks) == len(chunks), "加载丢块"
            assert all(c.source_kind == SOURCE_KIND_CANON for c in corpus.chunks)
            counts = corpus.source_kind_counts()
            assert counts[SOURCE_KIND_CANON] == len(chunks)
            assert counts[SOURCE_KIND_ANALYSIS] == 0
            assert counts[SOURCE_KIND_OFFICIAL] == 0

    @pytest.mark.parametrize(
        "bad", ["xyz", None, 123, "", "CANON", "Canon", [], {}, 3.5, True]
    )
    def test_invalid_source_kind_falls_back_to_canon(self, bad):
        base = {
            "hash": "h", "text": "t", "doc_id": "d", "bv": "BV1", "page": 1,
        }
        assert PlotChunk.from_dict({**base, "source_kind": bad}).source_kind == SOURCE_KIND_CANON

    def test_valid_source_kinds_are_preserved(self):
        for kind in SOURCE_KINDS:
            chunk = PlotChunk.from_dict(
                {
                    "hash": "h", "text": "t", "doc_id": "d", "bv": "BV1",
                    "page": 1, "source_kind": kind,
                }
            )
            assert chunk.source_kind == kind
            assert PlotChunk.from_dict(chunk.to_dict()).source_kind == kind

    def test_classify_priority_official_over_canon_over_analysis(self):
        """官方号 > 主线白名单 > 考据白名单 > 标题关键词 > canon。"""
        # 官方号最高优先级（哪怕标题带「解析」也不降级）
        assert classify_source_kind(
            uploader="重返未来1999", title="剧情解析"
        ) == SOURCE_KIND_OFFICIAL
        assert classify_source_kind(
            uploader="重返未来：1999", title="随便"
        ) == SOURCE_KIND_OFFICIAL
        # 主线白名单 > 标题关键词（避免实录标题含「解析」被误降级）
        assert classify_source_kind(
            uploader="缺德的德鲁伊", title="某某考据解析"
        ) == SOURCE_KIND_CANON
        # 考据白名单
        assert classify_source_kind(
            uploader="薯条小叔叔", title="随便"
        ) == SOURCE_KIND_ANALYSIS
        # 标题关键词兜底
        assert classify_source_kind(
            uploader="未知UP", title="五分钟带你看懂剧情"
        ) == SOURCE_KIND_ANALYSIS
        assert classify_source_kind(
            uploader="未知UP", title="主线实录"
        ) == SOURCE_KIND_CANON
        # 空输入
        assert classify_source_kind() == SOURCE_KIND_CANON
        assert classify_source_kind(uploader="", title="") == SOURCE_KIND_CANON

    def test_retrieval_path_has_no_source_kind_coupling(self):
        """检索路径完全没被改：src 下除 plot_corpus.py 外不得出现 source_kind。"""
        hits = []
        for py in (ROOT / "src").rglob("*.py"):
            if py.name == "plot_corpus.py":
                continue
            if "source_kind" in py.read_text(encoding="utf-8"):
                hits.append(str(py.relative_to(ROOT)))
        assert hits == [], f"检索/其它模块出现了 source_kind 耦合：{hits}"

    def test_real_corpus_labeling_matches_whitelist_intent(self, tmp_path):
        """端到端打标（真实 726 份转写）：白名单 UP 主的归属必须与常量表一致。

        存储态老语料全是 canon（无 source_kind 字段），只有重跑 build() 才会
        真正打标——本用例守护这条真实打标路径。
        """
        src = ROOT / "data" / "lore" / "wu_ming_zhe" / "视频文案"
        if not src.is_dir():
            pytest.skip(f"缺少真实语料目录：{src}")

        corpus = PlotCorpus(tmp_path / "c.json", character_id="wu_ming_zhe")
        stat = corpus.build(src)
        assert stat["files"] > 0 and stat["chunks"] > 0

        counts = corpus.source_kind_counts()
        assert sum(counts.values()) == stat["chunks"]
        # 三个取值都必须落在受控集合内，不能出现第 4 种
        assert set(counts) == set(SOURCE_KINDS)

        kind_by_up: dict[str, set[str]] = {}
        for chunk in corpus.chunks:
            kind_by_up.setdefault(chunk.uploader, set()).add(chunk.source_kind)
        # 同一 UP 主的打标必须唯一（白名单判定不依赖标题，故不会摇摆）
        assert all(len(v) == 1 for v in kind_by_up.values())

        # 白名单优先级：主线实录不能被标题关键词降级
        for up in ("缺德的德鲁伊",):
            assert kind_by_up.get(up, {SOURCE_KIND_CANON}) == {SOURCE_KIND_CANON}
        # 考据白名单必须真的被识别出来（否则等于改动没生效）
        analysis_ups = {u for u, k in kind_by_up.items() if k == {SOURCE_KIND_ANALYSIS}}
        assert analysis_ups, "真实语料里没有识别出任何考据向 UP 主"
        official_ups = {u for u, k in kind_by_up.items() if k == {SOURCE_KIND_OFFICIAL}}
        # 官方号是可选命中（本语料里只有 2 块），有则校验，无则不强求
        for up in official_ups:
            assert up in ("重返未来1999", "重返未来：1999")

    def test_by_hash_index_matches_linear_scan_on_real_corpus(self):
        """N0-3 的 _by_hash：索引结果与线性首现完全一致（真实 2477 块全量比对）。"""
        path = ROOT / "data" / "knowledge" / "plot_corpus_wu_ming_zhe.json"
        if not path.is_file():
            pytest.skip(f"缺少真实语料：{path}")
        corpus = PlotCorpus(path, character_id="wu_ming_zhe")
        linear: dict[str, PlotChunk] = {}
        for chunk in corpus.chunks:
            linear.setdefault(chunk.hash, chunk)
        assert len(corpus._by_hash) == len(linear)
        for h, chunk in linear.items():
            assert corpus.by_hash(h) is chunk
        assert corpus.by_hash("__nonexistent__") is None
        assert corpus.by_hash("") is None


# ══════════════════════════════════════════════════════════════════════════
# M0-3：--strict 门禁
# ══════════════════════════════════════════════════════════════════════════


class TestM03StrictGate:
    """默认行为必须与旧版一致（恒 0）；--strict 时各项不达标的确能拦下。"""

    def test_healthy_metrics_pass_all_checks(self):
        mod = _load_script("audit_full_corpus.py")
        checks = mod._strict_checks(
            chunks=1000,
            relations_total=2083,
            parse_failed=0,
            per_flag_chunks=Counter({"empty": 7}),
        )
        assert len(checks) == 7
        assert all(ok for _n, _t, _v, _s, ok in checks)

    @pytest.mark.parametrize(
        "kwargs,expect_fail",
        [
            ({"parse_failed": 3}, "缓存解析失败块数"),
            ({"per_flag_chunks": Counter({"empty": 300})}, "空块占比 empty/chunks"),
            ({"relations_total": 100}, "平均每块关系数"),
            (
                {"per_flag_chunks": Counter({"hallucinated_entity": 300})},
                "臆造实体块占比",
            ),
            (
                {"per_flag_chunks": Counter({"dangling_relation": 300})},
                "悬空关系块占比",
            ),
            ({"per_flag_chunks": Counter({"self_loop": 100})}, "自环边块占比"),
            (
                {"per_flag_chunks": Counter({"non_cn_predicate": 100})},
                "非中文谓语块占比",
            ),
        ],
    )
    def test_each_gate_fails_when_threshold_violated(self, kwargs, expect_fail):
        mod = _load_script("audit_full_corpus.py")
        base = dict(
            chunks=1000, relations_total=2083, parse_failed=0,
            per_flag_chunks=Counter(),
        )
        base.update(kwargs)
        checks = mod._strict_checks(**base)
        failed = [name for name, _t, _v, _s, ok in checks if not ok]
        assert failed == [expect_fail], f"期望只卡 {expect_fail}，实际 {failed}"

    def test_zero_chunks_does_not_crash(self):
        """空语料不应 ZeroDivisionError（_ratio/rel_per_chunk 都做了 chunks 判空）。"""
        mod = _load_script("audit_full_corpus.py")
        checks = mod._strict_checks(
            chunks=0, relations_total=0, parse_failed=0, per_flag_chunks=Counter()
        )
        assert len(checks) == 7

    def test_default_invocation_returns_zero(self):
        """回归硬要求：不加 --strict 必须仍 return 0（有既有调用方依赖）。"""
        proc = subprocess.run(
            [sys.executable, "-X", "utf8", "scripts/audit_full_corpus.py"],
            cwd=str(ROOT),
            capture_output=True,
            text=True,
            encoding="utf-8",
            timeout=600,
        )
        assert proc.returncode == 0, (
            f"默认调用返回 {proc.returncode}（破坏了既有调用方）\n"
            f"STDOUT tail: {proc.stdout[-800:]}\nSTDERR tail: {proc.stderr[-800:]}"
        )
        # 防「空跑也返回 0」的假通过：真实语料下必须确实扫到了块
        m = re.search(r'"chunks":\s*(\d+)', proc.stdout)
        if m:
            assert int(m.group(1)) > 0, "审计扫描到 0 块，退出码 0 不能作为有效证据"

    def test_strict_flag_is_off_by_default_in_source(self):
        """源码层面确认 --strict 默认关闭（store_true，不是 store_false）。"""
        source = (ROOT / "scripts" / "audit_full_corpus.py").read_text(encoding="utf-8")
        assert '"--strict"' in source
        assert 'action="store_true"' in source
        # 默认路径必须显式 return 0
        assert re.search(r"if not args\.strict:\s*\n\s*return 0", source)


# ══════════════════════════════════════════════════════════════════════════
# M0-4：no-op 检测
# ══════════════════════════════════════════════════════════════════════════


class TestM04NoopDetection:
    """建图 no-op 检测（端到端需真 LLM，这里做函数级验证）。"""

    def test_snapshot_missing_file(self, tmp_path):
        mod = _load_script("build_plot_graph.py")
        snap = mod._graph_snapshot(tmp_path / "nope.json")
        assert snap == {
            "exists": False, "sha256": "", "entities": 0, "edges": 0, "size": 0,
        }

    def test_snapshot_normal_graph(self, tmp_path):
        mod = _load_script("build_plot_graph.py")
        p = tmp_path / "g.json"
        p.write_text(
            json.dumps(
                {
                    "fingerprint": {},
                    "entities": {"a": {"name": "A"}, "b": {"name": "B"}},
                    "edges": [{"src": "a", "dst": "b", "relation": "r"}],
                    "alias_index": {},
                    "anchored": [],
                }
            ),
            encoding="utf-8",
        )
        snap = mod._graph_snapshot(p)
        assert snap["exists"] is True
        assert snap["entities"] == 2
        assert snap["edges"] == 1
        assert len(snap["sha256"]) == 64
        assert snap["size"] == p.stat().st_size

    def test_snapshot_broken_json_still_returns_valid_sha256(self, tmp_path):
        """坏 JSON 也要给出有效 sha256（注释说要防 no-op 判定被带偏）。"""
        mod = _load_script("build_plot_graph.py")
        p = tmp_path / "bad.json"
        p.write_text("{not json", encoding="utf-8")
        snap = mod._graph_snapshot(p)
        assert snap["exists"] is True
        assert len(snap["sha256"]) == 64
        assert snap["entities"] == 0 and snap["edges"] == 0

        # 2 字节 [] 的真实故障形态
        p2 = tmp_path / "two.json"
        p2.write_text("[]", encoding="utf-8")
        snap2 = mod._graph_snapshot(p2)
        assert snap2["exists"] is True
        assert snap2["size"] == 2
        assert snap2["entities"] == 0

    def test_is_noop_true_only_when_identical(self, tmp_path):
        mod = _load_script("build_plot_graph.py")
        p = tmp_path / "g.json"
        p.write_text(json.dumps({"entities": {"a": {}}, "edges": []}), encoding="utf-8")
        before = mod._graph_snapshot(p)

        assert mod._is_noop(before, before) is True

        p.write_text(
            json.dumps({"entities": {"a": {}, "b": {}}, "edges": []}), encoding="utf-8"
        )
        after = mod._graph_snapshot(p)
        assert mod._is_noop(before, after) is False

    def test_is_noop_false_when_file_absent(self, tmp_path):
        """前后都不存在（首次构建）不能判成 no-op。"""
        mod = _load_script("build_plot_graph.py")
        missing = {"exists": False, "sha256": "", "entities": 0, "edges": 0, "size": 0}
        assert mod._is_noop(missing, missing) is False

    def test_rebuild_path_is_exempt_from_noop(self):
        """--rebuild / --rebuild-graph-only 都是先删图再建，同内容属正常。

        源码守卫必须豁免**两者**：
          - ``not rebuild``               （--rebuild 清缓存 + 删图）
          - ``not rebuild_graph_only``    （--rebuild-graph-only 只删图、保缓存）
        否则重建后同内容会被误判成 no-op 并返回退出码 2。
        """
        mod = _load_script("build_plot_graph.py")
        source = (ROOT / "scripts" / "build_plot_graph.py").read_text(encoding="utf-8")
        assert re.search(
            r"if not rebuild and not rebuild_graph_only and _is_noop\(before, after\)",
            source,
        ), (
            "no-op 检测缺少 --rebuild / --rebuild-graph-only 豁免守卫，"
            "重建后同内容会被误判成 no-op"
        )
        assert mod.NOOP_EXIT_CODE == 2
        # before 快照必须在删图之前取，否则永远判不出来
        before_idx = source.index("before = _graph_snapshot(gpath)")
        unlink_idx = source.index("gpath.unlink()")
        assert before_idx < unlink_idx, "no-op 前快照取晚了（在删图之后）"

    def test_allow_noop_flag_exists(self):
        source = (ROOT / "scripts" / "build_plot_graph.py").read_text(encoding="utf-8")
        assert '"--allow-noop"' in source


# ══════════════════════════════════════════════════════════════════════════
# M0-5：别名表类型防御（与 M0-5 计数器一并复核）
# ══════════════════════════════════════════════════════════════════════════


class TestM05AliasCoercion:
    """_coerce_aliases / load_alias_table_with_stats / alias_ambiguous_dropped。"""

    @pytest.mark.parametrize(
        "value,expected_aliases,expected_bad",
        [
            ("Lucy", ["Lucy"], False),
            ("  Lucy  ", ["Lucy"], False),
            (["A", "B"], ["A", "B"], False),
            (("A", "B"), ["A", "B"], False),
            (["A", "", "  B  ", None], ["A", "B"], False),
            (["A", 1, None, "B"], ["A", "1", "B"], False),
            ([], [], False),
            ("   ", [], False),
            (None, [], True),
            (123, [], True),
            ({"a": 1}, [], True),
            (True, [], True),
        ],
    )
    def test_coerce_aliases(self, value, expected_aliases, expected_bad):
        assert _coerce_aliases(value) == (expected_aliases, expected_bad)

    def test_string_value_is_not_iterated_per_character(self, tmp_path):
        """回归核心：str 必须当单个别名，不能逐字符拆成 m/a/d/a/m。"""
        p = tmp_path / "a.json"
        p.write_text(json.dumps({"Lucy": "Madam Lucy"}), encoding="utf-8")
        table, stats = load_alias_table_with_stats(p)
        assert table == {"Lucy": ["Madam Lucy"]}
        assert stats["aliases"] == 1
        assert stats["dropped_bad_type"] == 0

    def test_stats_accounting(self, tmp_path):
        p = tmp_path / "a.json"
        p.write_text(
            json.dumps(
                {
                    "Lucy": "Madam Lucy",
                    "Doris": ["Doris", "多莉丝"],
                    "_meta": {"x": 1},
                    "_note": "zzz",
                    "Bad": {"k": 1},
                    "Num": 42,
                    "": ["x"],
                    "NoneV": None,
                    "Sp": "  A  ",
                    "EmptyList": [],
                }
            ),
            encoding="utf-8",
        )
        table, stats = load_alias_table_with_stats(p)
        assert table == {
            "Lucy": ["Madam Lucy"],
            "Doris": ["Doris", "多莉丝"],
            "Sp": ["A"],
            "EmptyList": [],
        }
        assert stats["total"] == 10
        assert stats["kept"] == 4
        assert stats["aliases"] == 4
        assert stats["dropped_underscore"] == 2
        assert stats["dropped_bad_type"] == 3
        assert stats["dropped_empty"] == 1

    def test_missing_and_broken_alias_files(self, tmp_path):
        assert load_alias_table_with_stats(tmp_path / "nope.json") == (
            {},
            {"total": 0, "kept": 0, "aliases": 0, "dropped_underscore": 0,
             "dropped_bad_type": 0, "dropped_empty": 0},
        )
        (tmp_path / "bad.json").write_text("{xx", encoding="utf-8")
        assert load_alias_table_with_stats(tmp_path / "bad.json")[0] == {}
        (tmp_path / "arr.json").write_text("[1,2]", encoding="utf-8")
        assert load_alias_table_with_stats(tmp_path / "arr.json")[0] == {}

    def test_real_alias_table_has_no_bad_types(self):
        p = ROOT / "data" / "lore" / "wu_ming_zhe" / "plot_aliases.json"
        if not p.is_file():
            pytest.skip(f"缺少真实别名表：{p}")
        table, stats = load_alias_table_with_stats(p)
        assert stats["dropped_bad_type"] == 0, "真实别名表里存在非法类型条目"
        assert stats["total"] == stats["kept"] + stats["dropped_underscore"] + stats["dropped_empty"]
        assert table, "真实别名表被整体丢弃"

    def test_alias_ambiguous_dropped_counter(self, tmp_path):
        store = GraphStore(tmp_path / "g.json", min_confidence=0.0)
        store.upsert_entities([{"name": "A", "aliases": ["共享别名"]}])
        store.upsert_entities([{"name": "B"}])
        assert store.alias_ambiguous_dropped == 0

        bound = store.bind_alias_table({"B": ["共享别名"], "C": ["全新别名C"]})
        assert store.alias_ambiguous_dropped == 1
        assert bound == 1, "只有未被占用的那条应计入绑定数"
        # 冲突的别名没有被抢占
        assert "共享别名" not in [
            e["aliases"] for e in store.entities() if e["name"] == "B"
        ][0]
        # 原实体仍然持有该别名
        assert "共享别名" in [
            e["aliases"] for e in store.entities() if e["name"] == "A"
        ][0]


# ══════════════════════════════════════════════════════════════════════════
# M0-1：归档脚本实跑
# ══════════════════════════════════════════════════════════════════════════


class TestM01ArchiveBackup:
    """实跑一次归档：只复制不删除，且 INDEX.md 的 sha256 可独立复算校验。"""

    def test_archive_run_does_not_touch_sources_and_index_is_verifiable(self, tmp_path):
        """端到端实跑（归档到 tmp 目录），独立复算 sha256 与源文件指纹。"""
        sys.path.insert(0, str(ROOT / "src"))
        try:
            from roleplay.config import get_settings
        except Exception as exc:  # pragma: no cover - 环境缺依赖时跳过
            pytest.skip(f"无法读取配置：{exc}")

        settings = get_settings()
        lore_dir = Path(settings.plot_lore_dir) / "wu_ming_zhe"
        sources = [
            Path(settings.plot_graph_dir) / "plot_graph_wu_ming_zhe.json",
            Path(settings.plot_corpus_dir) / "plot_corpus_wu_ming_zhe.json",
            lore_dir / "plot_aliases.json",
            lore_dir / "plot_glossary.json",
            lore_dir / "wiki_zh_en.json",
        ]
        present = [p for p in sources if p.is_file()]
        if not present:
            pytest.skip("没有任何源文件可归档（数据目录为空）")

        def snap(p: Path) -> tuple[str, int, int]:
            st = p.stat()
            return _sha256(p), st.st_size, st.st_mtime_ns

        before = {str(p): snap(p) for p in present}

        proc = subprocess.run(
            [
                sys.executable, "-X", "utf8", "scripts/archive_backup.py",
                "--archive-dir", str(tmp_path / "_archive"),
            ],
            cwd=str(ROOT),
            capture_output=True,
            text=True,
            encoding="utf-8",
            timeout=300,
        )
        assert proc.returncode == 0, f"归档失败：{proc.stdout}\n{proc.stderr}"

        # ① 源文件 mtime 与内容必须完全没变（"只复制不删除"的硬要求）
        for p in present:
            assert snap(p) == before[str(p)], f"源文件被改动：{p}"

        # ② 目标目录必须是 <archive-dir>/<YYYYmmdd_HHMMSS>/
        stamp_dirs = [d for d in (tmp_path / "_archive").iterdir() if d.is_dir()]
        assert len(stamp_dirs) == 1, f"归档目录数量异常：{stamp_dirs}"
        archive = stamp_dirs[0]
        assert re.fullmatch(r"\d{8}_\d{6}", archive.name), archive.name

        # ③ INDEX.md 里的 sha256 由本测试独立复算，不信脚本自报
        index_md = (archive / "INDEX.md").read_text(encoding="utf-8")
        rows = re.findall(
            r"\| `([^`]+)` \| ok \| (\d+) \| `([0-9a-f]{64})` \| `([^`]+)` \|", index_md
        )
        assert len(rows) == len(present), f"INDEX 条目数 {len(rows)} != 源文件数 {len(present)}"
        for name, size, digest, src in rows:
            copy = archive / name
            assert copy.is_file(), f"副本缺失：{copy}"
            assert int(size) == copy.stat().st_size, f"{name} 字节数不符"
            assert _sha256(Path(src)) == digest, f"{name} 的 sha256 与源文件不符"
            assert _sha256(copy) == digest, f"{name} 的 sha256 与副本不符"
            assert Path(src).read_bytes() == copy.read_bytes(), f"{name} 副本与源文件不一致"

        # ④ 缺失项要被标注，而不是静默略过
        missing = len(present) - len(rows)
        if missing:
            assert "缺失" in index_md
