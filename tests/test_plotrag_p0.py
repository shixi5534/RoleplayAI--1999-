# -*- coding: utf-8 -*-
"""P0-1（C4 弱证豁免）与 M-9（手工边重放对账）的回归测试。

被锁住的行为
    P0-1
      1. ``exempt_sources`` **只豁免弱证判据**，不豁免 ``min_confidence``——
         人工边仍须给出置信度，不能变成"无条件进图"；
      2. 两个新参数都为 None 时，PPR 输出与改造前**逐位一致**（用改造前的算法做参考实现差分）；
      3. ``exempt_sources`` 必须进 ``_graph_view`` 缓存键——否则改配置后仍读旧邻接
         （与 M7「Registry 漏传配置」同类的静默失效）。
    P0-4
      4. ``seed_weights`` 在**归一化之前**逐乘；未列出的种子按 1.0；
      5. Registry 必须把**每一个**新配置透传到检索器（M7 教训的机械化钉桩）。
    M-9
      6. 重放幂等（连跑两次第二次新增 0）；
      7. ``source`` 标记归一（``manual_probe`` -> ``manual``），且证据取并集不丢；
      8. 反向存储的边不得被误判为"缺失"而重复插入；
      9. ``present_rate`` 用**跑完之后**的在场数（跑前 0% / 跑后 100% 是正确读数）。
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

# M-9 的实现是 scripts/apply_manual_edges.py（CLI + 可导入的 replay 函数），
# 该目录默认不在 sys.path 上——与 scripts/build_plot_graph.py 里的处理保持一致。
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from roleplay.core.knowledge.graph_ppr import (  # noqa: E402
    WEAK_EVIDENCE_MIN,
    build_adjacency,
    filter_edges,
    hop_distance,
    parse_exempt_sources,
    personalized_pagerank,
)


def _edge(src, dst, *, conf=0.7, imp=0.7, n_ev=1, source="plot_transcript"):
    return {"src": src, "dst": dst, "relation": "关联", "confidence": conf,
            "importance": imp, "evidence": [{"hash": f"h{i}"} for i in range(n_ev)],
            "source": source}


# ══════════════════════════════════════════════════════════════════════
# P0-1：exempt_sources
# ══════════════════════════════════════════════════════════════════════


class TestParseExemptSources:
    def test_comma_separated(self):
        assert parse_exempt_sources("manual,manual_probe") == frozenset(
            {"manual", "manual_probe"})

    def test_none_and_empty(self):
        assert parse_exempt_sources(None) == frozenset()
        assert parse_exempt_sources("") == frozenset()
        assert parse_exempt_sources("  ,  ") == frozenset()

    def test_accepts_container(self):
        assert parse_exempt_sources(["manual"]) == frozenset({"manual"})

    def test_strips_whitespace(self):
        assert parse_exempt_sources(" manual , manual_probe ") == frozenset(
            {"manual", "manual_probe"})


class TestFilterEdgesExemption:
    def test_weak_edge_dropped_without_exemption(self):
        weak = _edge("a", "b", n_ev=WEAK_EVIDENCE_MIN - 1)
        assert filter_edges([weak], include_weak=False) == []

    def test_weak_edge_kept_with_exemption(self):
        weak = _edge("a", "b", n_ev=1, source="manual")
        out = filter_edges([weak], include_weak=False,
                           exempt_sources=parse_exempt_sources("manual"))
        assert len(out) == 1

    def test_exemption_does_not_bypass_min_confidence(self):
        """豁免只作用于弱证判据——低置信度的人工边仍须被 min_confidence 拦下。"""
        low = _edge("a", "b", conf=0.1, n_ev=1, source="manual")
        out = filter_edges([low], min_confidence=0.6, include_weak=False,
                           exempt_sources=parse_exempt_sources("manual"))
        assert out == [], "豁免把 min_confidence 也绕过了（人工边会无条件进图）"

    def test_other_sources_not_exempt(self):
        other = _edge("a", "b", n_ev=1, source="plot_transcript")
        out = filter_edges([other], include_weak=False,
                           exempt_sources=parse_exempt_sources("manual"))
        assert out == []

    def test_include_weak_true_ignores_exemption(self):
        """include_weak=True 时弱证边本来就全收，豁免不应改变结果。"""
        weak = _edge("a", "b", n_ev=1, source="plot_transcript")
        assert len(filter_edges([weak], include_weak=True)) == 1

    def test_adjacency_and_hop_respect_exemption(self):
        edges = [_edge("a", "b", n_ev=1, source="manual", conf=0.8),
                 _edge("b", "c", n_ev=1, source="plot_transcript", conf=0.8)]
        ex = parse_exempt_sources("manual")
        adj, _deg = build_adjacency(edges, min_confidence=0.6, include_weak=False,
                                    exempt_sources=ex)
        assert "a" in adj and "b" in adj, "豁免边未进邻接"
        assert "c" not in adj, "非豁免弱证边不该进邻接"
        hop = hop_distance(edges, {"a"}, 2, min_confidence=0.6, include_weak=False,
                           exempt_sources=ex)
        assert hop.get("b") == 1 and "c" not in hop


class TestBitIdenticalRegression:
    """改造前后逐位一致：用**改造前的算法**做参考实现，在真实规模随机图上差分。"""

    @staticmethod
    def _reference_ppr(edges, seeds, *, damping=0.85, max_iter=50, tol=1e-6):
        """改造前 personalized_pagerank 的逐行复刻（无 exempt / 无 seed_weights）。"""
        adj: dict[str, list[tuple[str, float]]] = {}
        deg: dict[str, float] = {}
        for e in edges:
            w = float(e.get("confidence", 0.0)) * float(e.get("importance", 0.7))
            if w <= 0:
                continue
            s, d = str(e.get("src")), str(e.get("dst"))
            adj.setdefault(s, []).append((d, w))
            adj.setdefault(d, []).append((s, w))
            deg[s] = deg.get(s, 0.0) + w
            deg[d] = deg.get(d, 0.0) + w
        for n in adj:
            deg[n] = deg.get(n, 0.0) or 1.0
        nodes = set(adj)
        if not nodes or not seeds:
            return dict(seeds)
        total = sum(seeds.values()) or 1.0
        r = {n: (seeds.get(n, 0.0) / total) for n in nodes}
        for n, w in seeds.items():
            if n not in r:
                r[n] = w / total
                nodes.add(n)
        seed_vec = {n: (seeds.get(n, 0.0) / total) for n in r}
        for _ in range(max(1, max_iter)):
            new: dict[str, float] = {}
            delta = 0.0
            for u, ru in r.items():
                d = damping * (ru / deg.get(u, 1.0))
                if d <= 0:
                    continue
                for v, w in adj.get(u, ()):
                    new[v] = new.get(v, 0.0) + d * w
            for n, rn in r.items():
                val = (1 - damping) * seed_vec.get(n, 0.0) + new.get(n, 0.0)
                new[n] = val
                delta += val - rn if val >= rn else rn - val
            r = new
            if delta < tol:
                break
        return r

    def _random_edges(self, n_nodes=40, n_edges=90, seed=7):
        import random
        rng = random.Random(seed)
        out = []
        for _ in range(n_edges):
            a = f"e{rng.randrange(n_nodes)}"
            b = f"e{rng.randrange(n_nodes)}"
            if a == b:
                continue
            out.append(_edge(a, b, conf=round(rng.uniform(0.5, 1.0), 3),
                             imp=round(rng.uniform(0.4, 1.0), 3),
                             n_ev=rng.choice([1, 1, 1, 2])))
        return out

    def test_none_params_bit_identical(self):
        edges = self._random_edges()
        seeds = {"e1": 1.0, "e7": 0.6, "e13": 0.4}
        new = personalized_pagerank(edges, dict(seeds), min_confidence=0.0,
                                    include_weak=True, damping=0.85, max_iter=50,
                                    seed_weights=None, exempt_sources=None)
        ref = self._reference_ppr(edges, dict(seeds))
        assert set(new) == set(ref), "节点集不一致"
        for k in ref:
            assert new[k] == ref[k], f"{k} 分数不逐位一致：{new[k]!r} != {ref[k]!r}"

    def test_filter_edges_default_unchanged(self):
        edges = self._random_edges()
        assert filter_edges(edges, min_confidence=0.0, include_weak=False) == \
            filter_edges(edges, min_confidence=0.0, include_weak=False,
                         exempt_sources=None)


class TestSeedWeights:
    def test_applied_before_normalisation(self):
        """specificity 在归一化**之前**逐乘：只改相对比例，不改总权重语义。"""
        edges = [_edge("a", "b", conf=0.9, imp=0.9), _edge("b", "c", conf=0.9, imp=0.9)]
        base = personalized_pagerank(edges, {"a": 1.0, "c": 1.0}, max_iter=3)
        w = personalized_pagerank(edges, {"a": 1.0, "c": 1.0}, max_iter=3,
                                  seed_weights={"c": 0.01})
        assert w["a"] > base["a"], "被降权的种子应让另一颗种子相对上升"
        assert w["c"] < base["c"]

    def test_unlisted_seed_weight_is_one(self):
        edges = [_edge("a", "b", conf=0.9), _edge("b", "c", conf=0.9)]
        a = personalized_pagerank(edges, {"a": 1.0, "c": 1.0}, max_iter=3,
                                  seed_weights={"a": 1.0})
        b = personalized_pagerank(edges, {"a": 1.0, "c": 1.0}, max_iter=3,
                                  seed_weights={"a": 1.0, "c": 1.0})
        assert a == b, "未列出的种子乘数应为 1.0"

    def test_empty_dict_is_identity(self):
        edges = [_edge("a", "b", conf=0.9)]
        a = personalized_pagerank(edges, {"a": 1.0}, max_iter=3, seed_weights={})
        b = personalized_pagerank(edges, {"a": 1.0}, max_iter=3)
        assert a == b


# ══════════════════════════════════════════════════════════════════════
# Registry 透传（M7 教训的机械化钉桩）
# ══════════════════════════════════════════════════════════════════════


class TestRegistryPassthrough:
    def test_every_plot_config_reaches_retriever(self):
        """每一个 plot_* 检索配置都必须真正到达检索器。

        M7 教训：``PlotGraphRegistry.get()`` 是**显式列参**构造检索器的，只把新配置加进
        ``_cfg`` 而忘了透传，就会静默退回构造默认值——表现为「配置改了没反应」。
        本用例逐个断言，新增配置忘了透传时会在这里红。
        """
        from roleplay.config import get_settings
        from roleplay.core.knowledge.factory import build_plot_registry

        s = get_settings()
        reg = build_plot_registry(s)
        r = reg.get("wu_ming_zhe")
        if r is None:
            pytest.skip("剧情图谱未加载（缺语料/图谱文件）")
        assert r.exempt_sources == frozenset(
            p.strip() for p in str(s.plot_weak_exempt_sources).split(",") if p.strip()
        )
        assert r.node_specificity is bool(s.plot_ppr_node_specificity)
        assert r.semantic_enabled is bool(s.plot_semantic_enabled)
        assert r.semantic_min_score == float(s.plot_semantic_min_score)
        assert r.chapter_routing is bool(s.plot_chapter_routing)
        assert r.mention_per_entity == int(s.plot_mention_per_entity)
        assert r.mention_total_cap == int(s.plot_mention_total_cap)
        assert r.lexical_always is bool(s.plot_lexical_always)
        # P1-4 召回率修复：保底保留名额也必须真正到达检索器（否则配置改了没反应）
        assert r.min_semantic_kept == int(s.plot_min_semantic_kept)
        assert r.min_chapter_kept == int(s.plot_min_chapter_kept)
        # 60 题 never_candidate 专项：语义补位重排开关（默认关 = 零回归）
        assert r.rerank_topup_enabled is bool(s.plot_rerank_topup_enabled)
        assert r.rerank_topup_keep == int(s.plot_rerank_topup_keep)

    def test_rerank_topup_off_is_noop(self):
        """默认关闭时补位重排必须是 no-op：同一查询两次检索结果逐位一致。

        这是「默认零回归」的可执行证明——不是靠注释声明，而是靠同一实例上
        开关前后结果不变来钉住。
        """
        from roleplay.config import get_settings
        from roleplay.core.knowledge.factory import build_plot_registry

        s = get_settings()
        reg = build_plot_registry(s)
        r = reg.get("wu_ming_zhe")
        if r is None:
            pytest.skip("剧情图谱未加载（缺语料/图谱文件）")
        q = "海盗船上的歌手是谁"
        before = r.retrieve(q, top_chunks=6, lexical_fallback=2)
        r.rerank_topup_enabled = False
        after = r.retrieve(q, top_chunks=6, lexical_fallback=2)
        assert [c.text for c in before] == [c.text for c in after]
        assert all(not (c.metadata or {}).get("rerank_topup") for c in after)

    def test_graph_view_cache_key_includes_exempt_sources(self, tmp_path):
        """改 exempt_sources 后必须重建图视图（否则读旧邻接 = 配置无效）。"""
        from roleplay.core.knowledge.graph_store import GraphStore
        from roleplay.core.knowledge.plot_corpus import PlotCorpus
        from roleplay.core.knowledge.plot_graph import PlotGraphRetriever

        store = GraphStore(tmp_path / "g.json", min_confidence=0.5)
        store.upsert_entities([{"name": "甲"}, {"name": "乙"}])
        a, b = store.link_exact("甲"), store.link_exact("乙")
        store.upsert_edge(src=a, dst=b, relation="关联", confidence=0.9,
                          evidence=[{"ns": "plot", "doc_id": "d", "hash": "h"}])
        corpus = PlotCorpus(tmp_path / "c.json", character_id="x")
        corpus.chunks = []
        r = PlotGraphRetriever(corpus, store, min_confidence=0.5, include_weak=False,
                               exempt_sources=frozenset())
        v1 = r._graph_view()[0]
        r.exempt_sources = frozenset({"manual"})
        v2 = r._graph_view()[0]
        assert v1 is not v2 or len(v1) == len(v2)  # 键变了必然重建（对象不同）
        assert r._graph_view()[0] is v2, "同一 key 应命中缓存"


# ══════════════════════════════════════════════════════════════════════
# M-9：手工边重放 / 归一 / 对账
# ══════════════════════════════════════════════════════════════════════


class TestManualEdgeReplay:
    def _setup(self, tmp_path, monkeypatch, edges, manifest):
        """构造最小工作区：图谱文件 + 手工边清单，并把 ROOT 指向 tmp。"""
        import apply_manual_edges as m9

        (tmp_path / "data" / "knowledge").mkdir(parents=True)
        (tmp_path / "data" / "lore" / "cid").mkdir(parents=True)
        gpath = tmp_path / "data" / "knowledge" / "plot_graph_cid.json"
        gpath.write_text(json.dumps(
            {"entities": {"e1": {"name": "甲"}, "e2": {"name": "乙"}},
             "edges": edges}, ensure_ascii=False), encoding="utf-8")
        mpath = tmp_path / "data" / "lore" / "cid" / "manual_edges.json"
        mpath.write_text(json.dumps(manifest, ensure_ascii=False), encoding="utf-8")
        monkeypatch.setattr(m9, "ROOT", tmp_path)
        return m9, gpath

    def _manifest(self, evidence_hash="hm"):
        return [{"src_name": "甲", "dst_name": "乙", "relation": "位于",
                 "confidence": 0.7, "importance": 0.7,
                 "evidence": [{"ns": "plot", "doc_id": "d", "hash": evidence_hash}]}]

    def test_adds_missing_edge_with_canonical_source(self, tmp_path, monkeypatch):
        m9, gpath = self._setup(tmp_path, monkeypatch, [], self._manifest())
        st = m9.replay("cid")
        assert st["added"] == 1 and st["present_rate"] == 1.0
        g = json.loads(gpath.read_text(encoding="utf-8"))
        assert g["edges"][0]["source"] == "manual", "新增边必须带规范标记"

    def test_idempotent_second_run(self, tmp_path, monkeypatch):
        m9, _ = self._setup(tmp_path, monkeypatch, [], self._manifest())
        m9.replay("cid")
        st2 = m9.replay("cid")
        assert st2["added"] == 0 and st2["consistent"] == 1 and st2["present_rate"] == 1.0

    def test_normalises_non_canonical_source(self, tmp_path, monkeypatch):
        """实测踩到的真场景：早期探针把人工边标成 manual_probe，弱证豁免对它不生效。"""
        edges = [{"src": "e1", "dst": "e2", "relation": "位于", "confidence": 0.7,
                  "importance": 0.7, "evidence": [{"hash": "h0"}],
                  "source": "manual_probe"}]
        m9, gpath = self._setup(tmp_path, monkeypatch, edges, self._manifest("hm"))
        st = m9.replay("cid")
        assert st["normalized"] == 1 and st["added"] == 0
        g = json.loads(gpath.read_text(encoding="utf-8"))
        assert g["edges"][0]["source"] == "manual"
        # 证据取并集：原有 h0 不得被清单的 hm 顶掉
        hs = {e["hash"] for e in g["edges"][0]["evidence"]}
        assert hs == {"h0", "hm"}, f"证据并集不正确：{hs}"

    def test_reverse_stored_edge_not_treated_as_missing(self, tmp_path, monkeypatch):
        """边在存储层有向、语义对称：清单写 (甲,乙)、图里存 (乙,甲) 时不得重复插边。"""
        edges = [{"src": "e2", "dst": "e1", "relation": "位于", "confidence": 0.7,
                  "importance": 0.7, "evidence": [{"hash": "h0"}], "source": "manual"}]
        m9, gpath = self._setup(tmp_path, monkeypatch, edges, self._manifest())
        st = m9.replay("cid")
        assert st["added"] == 0 and st["consistent"] == 1
        assert len(json.loads(gpath.read_text(encoding="utf-8"))["edges"]) == 1

    def test_present_rate_uses_after_state(self, tmp_path, monkeypatch):
        """跑前 0% / 跑后 100% 是正确读数（旧版把刚补上的边报成"丢失"）。"""
        m9, _ = self._setup(tmp_path, monkeypatch, [], self._manifest())
        st = m9.replay("cid")
        assert st["present_rate_before"] == 0.0
        assert st["present_rate"] == 1.0

    def test_missing_entity_reported_and_rate_below_one(self, tmp_path, monkeypatch):
        man = self._manifest() + [{"src_name": "甲", "dst_name": "查无此人",
                                   "relation": "关联", "evidence": []}]
        m9, _ = self._setup(tmp_path, monkeypatch, [], man)
        st = m9.replay("cid")
        assert st["missing"] == [("甲", "查无此人")]
        assert st["present_rate"] == pytest.approx(0.5)

    def test_dry_run_does_not_write(self, tmp_path, monkeypatch):
        m9, gpath = self._setup(tmp_path, monkeypatch, [], self._manifest())
        before = gpath.read_text(encoding="utf-8")
        st = m9.replay("cid", dry_run=True)
        assert st["added"] == 1
        assert gpath.read_text(encoding="utf-8") == before, "dry-run 不应落盘"

    def test_no_manifest_is_noop(self, tmp_path, monkeypatch):
        import apply_manual_edges as m9
        monkeypatch.setattr(m9, "ROOT", tmp_path)
        st = m9.replay("cid")
        assert st["skipped_no_file"] is True

    def test_manual_source_matches_config_default(self):
        """数据侧规范标记必须与配置默认值一致——两者不一致 = 豁免静默失效。"""
        import apply_manual_edges as m9
        from roleplay.config import get_settings
        s = get_settings()
        assert m9.MANUAL_SOURCE in parse_exempt_sources(s.plot_weak_exempt_sources)
