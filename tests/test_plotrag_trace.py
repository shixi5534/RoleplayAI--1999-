# -*- coding: utf-8 -*-
"""M-11 检索链路埋点（P0-5 / F8a）的回归测试。

被锁住的行为（每条都对应架构 §7.6 的硬约束）
    1. **六通道每轮必有一条记录**，顺序固定——瀑布图与"每通道必记录"契约的载体；
    2. ``hit_count == 0`` 时 ``skip_reason`` **必填**，且 9 值枚举封闭；
    3. ``kept_in_final`` 归因把桶 4（融合层稀释）第一次变成可测量；
    4. ``entity_link_margin`` 的 ``margin`` 在只有一个候选时为 **None**（不是 0——
       0 会被误读成"两个候选分数相同"）；
    5. **埋点失败绝不影响检索**：落盘失败/异常都只告警；
    6. **不写查询原文**，只写 ``query_hash``；
    7. 默认关：关时不构造 trace、不算计时。
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from roleplay.core.knowledge.retrieval_trace import (
    ABLATION_SCHEMA,
    CHANNEL_ORDER,
    SKIP_REASONS,
    TRACE_SCHEMA,
    ChannelRecord,
    ChannelSkipReason,
    EntityLinkMargin,
    RetrievalTrace,
    TraceCollector,
    append_jsonl,
    config_hash,
    query_hash,
    trace_path,
)


class _Chunk:
    def __init__(self, paths):
        self.metadata = {"paths": list(paths)}


class TestSchemaConstants:
    def test_six_channels_fixed_order(self):
        assert CHANNEL_ORDER == ("别名精确", "BM25 兜底", "语义向量", "图传播",
                                 "篇章路由", "扩展查询")

    def test_nine_skip_reasons_exact(self):
        assert set(SKIP_REASONS) == {
            "not_enabled", "index_missing", "fingerprint_stale", "embed_failed",
            "no_seed", "gate_rejected", "no_candidate", "rerank_unavailable",
            "budget_exhausted"}
        assert len(SKIP_REASONS) == 9

    def test_schema_versions(self):
        assert TRACE_SCHEMA == "retrieval-trace-v1"
        assert ABLATION_SCHEMA == "ablation-v1"


class TestPrivacyAndFingerprints:
    def test_query_hash_never_contains_raw(self):
        q = "洞穴的囚徒篇里海盗船上的歌手是谁？"
        h = query_hash(q)
        assert len(h) == 16 and all(c in "0123456789abcdef" for c in h)
        assert q not in h

    def test_config_hash_only_plot_keys(self):
        a = config_hash({"plot_max_chunks": 6, "llm_model": "x"})
        b = config_hash({"plot_max_chunks": 6, "llm_model": "y"})
        assert a == b, "非 plot_* 配置不应影响检索指纹"
        c = config_hash({"plot_max_chunks": 7, "llm_model": "x"})
        assert a != c


class TestChannelRecord:
    def test_hit_zero_requires_skip_reason(self):
        rec = ChannelRecord(channel="语义向量", enabled=True)
        rec.finish()
        assert rec.skip_reason == ChannelSkipReason.NO_CANDIDATE.value

    def test_hit_positive_clears_skip_reason(self):
        rec = ChannelRecord(channel="语义向量", enabled=True, hit_count=3)
        rec.finish(ChannelSkipReason.NO_SEED)
        assert rec.skip_reason is None, "有命中就不该带跳过原因"

    def test_finish_accepts_enum(self):
        rec = ChannelRecord(channel="图传播", enabled=True)
        rec.finish(ChannelSkipReason.GATE_REJECTED)
        assert rec.skip_reason == "gate_rejected"


class TestEntityLinkMargin:
    def test_two_candidates_margin(self):
        m = EntityLinkMargin()
        m.fill([0.82, 0.61], threshold=0.5, linked=True)
        assert m.triggered and m.candidates == 2
        assert m.top1_score == 0.82 and m.top2_score == 0.61
        assert m.margin == pytest.approx(0.21, abs=1e-9)

    def test_single_candidate_margin_is_none(self):
        """只有一个候选时 margin 无定义——必须是 None，不能是 0。"""
        m = EntityLinkMargin()
        m.fill([0.77], threshold=0.5, linked=True)
        assert m.margin is None, "单候选的 margin 必须是 None（0 会被误读成并列）"
        assert m.top2_score is None

    def test_empty_candidates(self):
        m = EntityLinkMargin()
        m.fill([], threshold=0.5, linked=False, reject_reason="below_threshold")
        assert m.candidates == 0 and m.margin is None and m.top1_score is None


class TestTraceFinish:
    def test_all_six_channels_present_by_default(self):
        t = RetrievalTrace()
        assert [c.channel for c in t.channels] == list(CHANNEL_ORDER)

    def test_kept_in_final_attribution(self):
        t = RetrievalTrace()
        t.mark("图传播", hit_count=10)
        t.mark("语义向量", hit_count=4)
        t.finish(query="q", final_chunks=[_Chunk(["edge"]), _Chunk(["semantic"]),
                                          _Chunk(["edge", "semantic"])])
        assert t.channel("图传播").kept_in_final == 2
        assert t.channel("语义向量").kept_in_final == 2
        # 桶 4 量化：hit - kept 即"有货没进"
        assert t.channel("图传播").hit_count - t.channel("图传播").kept_in_final == 8

    def test_mention_grouped_by_seed_path(self):
        """mention 块按种子来源归组——本契约最易被搞错的一点。"""
        t = RetrievalTrace()
        t.finish(query="q", final_chunks=[
            _Chunk(["mention"]),                      # 无 seed_path -> 别名精确
        ])
        assert t.channel("别名精确").kept_in_final == 1
        t2 = RetrievalTrace()
        t2.finish(query="q", final_chunks=[_Chunk(["mention"])])
        assert t2.channel("BM25 兜底").kept_in_final == 0

    def test_finish_sets_hash_not_raw(self):
        t = RetrievalTrace()
        t.finish(query="牙仙是谁", final_chunks=[])
        assert t.query_hash == query_hash("牙仙是谁")
        assert "牙仙" not in json.dumps(t.to_dict(), ensure_ascii=False)

    def test_to_dict_is_json_serialisable(self):
        t = RetrievalTrace()
        t.mark("图传播", hit_count=2)
        t.finish(query="q", final_chunks=[_Chunk(["edge"])])
        s = json.dumps(t.to_dict(), ensure_ascii=False)
        back = json.loads(s)
        assert back["trace_schema"] == TRACE_SCHEMA
        assert len(back["channels"]) == 6


class TestCollectorDegradation:
    def test_disabled_collector_is_noop(self):
        tc = TraceCollector(enabled=False)
        assert tc.trace is None
        with tc.stage("link_ms"):
            pass
        assert tc.mark("图传播", hit_count=1) is None
        tc.fallback("embed_failed")
        assert tc.finish(query="q", final_chunks=[]) is None

    def test_enabled_collector_records_latency(self):
        tc = TraceCollector(enabled=True, character_id="cid",
                            config={"plot_max_chunks": 6})
        with tc.stage("link_ms"):
            pass
        t = tc.finish(query="q", final_chunks=[])
        assert "link_ms" in t.latency and "total_ms" in t.latency
        assert t.character_id == "cid" and len(t.config_hash) == 16

    def test_jsonl_write_failure_is_swallowed(self, tmp_path):
        """落盘失败绝不抛到检索主链路。"""
        bad = tmp_path / "afile"
        bad.write_text("x", encoding="utf-8")  # 父路径是文件 -> mkdir 必失败
        t = RetrievalTrace()
        t.finish(query="q", final_chunks=[])
        assert append_jsonl(bad / "sub" / "a.jsonl", t) is False

    def test_jsonl_appends_lines(self, tmp_path):
        p = tmp_path / "t.jsonl"
        for i in range(3):
            t = RetrievalTrace()
            t.finish(query=f"q{i}", final_chunks=[])
            assert append_jsonl(p, t) is True
        lines = p.read_text(encoding="utf-8").strip().splitlines()
        assert len(lines) == 3
        assert json.loads(lines[0])["event"] == "retrieval_trace"

    def test_fallback_dedup(self):
        tc = TraceCollector(enabled=True)
        tc.fallback("embed_failed")
        tc.fallback("embed_failed")
        assert tc.trace.fallbacks == ["embed_failed"]

    def test_seeds_recorded_with_gate_flag(self):
        tc = TraceCollector(enabled=True)
        tc.set_seeds({
            "e1": {"name": "牙仙", "path": "exact", "weight": 1.0, "gate_passed": True},
            "e2": {"name": "天气", "path": "exact", "weight": 1.0, "gate_passed": False},
        })
        assert tc.trace.seeds_total == 2
        flags = {s["name"]: s["gate_passed"] for s in tc.trace.seeds}
        assert flags == {"牙仙": True, "天气": False}, "被门控拒的种子也必须留痕"


class TestTracePath:
    def test_path_matches_contract(self):
        p = trace_path("data/knowledge", "wu_ming_zhe")
        assert p.as_posix().endswith("data/knowledge/_audit/retrieval_trace/wu_ming_zhe.jsonl")
