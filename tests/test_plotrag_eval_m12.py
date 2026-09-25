# -*- coding: utf-8 -*-
"""M-12（eval 报告扩展）单测：trace_agg / ablation / diff / bucket 归因。

契约来源（逐字）：架构 §7.6.4 顶层表 + 表 7.6.4-a（trace_agg）+ 表 7.6.4-b（ablation）
+ §7.6.6 阴性证据通则。本文件只测**纯函数**（不加载图谱/模型），因此可在 CI 里秒级跑完：

  1. `trace_agg`：六通道固定顺序、`kept_rate` 分母 0 → null（不是 0）、`squeezed_total`
     与 `graph_hit_total` 成对产出、margin 直方图桶边界显式落盘、fallback 计数与
     cases/total_ms 同期；
  2. `ablation`：11 字段齐备、`m == 0` → `mcnemar_p is None`（**不是 1.0**）、
     `b+c<25` → `exact`、`b+c>=25` → `chi2_approx_corrected` 且与卡方上尾解析式一致、
     `delta_pt` 方向不可反、`case_ids_flipped` 与 `diff_vs_baseline` 同源；
  3. 失分桶：优先级与"未命中进 unattributed"、失分题才归桶；
  4. 执行计数（§7.6.6）：未登记的开关 `cases_executed` 不撒谎。
"""
from __future__ import annotations

import sys
from math import erfc, sqrt
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

from eval_plot_rag import (  # noqa: E402
    ACTIVATION_KEYS,
    MARGIN_BUCKET_EDGES,
    aggregate_traces,
    bucket_attribution,
    cases_executed_for,
    classify_bucket,
    compute_flipped,
    mcnemar_ablation,
    trace_invariance,
)
from roleplay.core.knowledge.retrieval_trace import (  # noqa: E402
    ABLATION_SCHEMA,
    CHANNEL_ORDER,
    ChannelSkipReason,
    RetrievalTrace,
    channel_of_block,
    query_hash,
)


# ── 造 trace 的小工具（不依赖真实检索器）────────────────────────────────
def make_trace(*, seeds=1, channels=None, margin=None, fallbacks=(), final=None,
               total_ms=500.0, lang="zh", kept=None):
    """``kept`` 必须在 ``finish()`` **之后**注入：``finish()`` 会按 final_chunks
    重新归因 kept_in_final（传空列表即全部清零），先设会被覆盖。"""
    t = RetrievalTrace(character_id="wu_ming_zhe", query_lang=lang)
    t.seeds_total = seeds
    for name, kw in (channels or {}).items():
        t.mark(name, **kw)
    if margin is not None:
        scores, thr, linked = margin
        t.entity_link_margin.fill(scores, threshold=thr, linked=linked)
    for f in fallbacks:
        t.fallback(f)
    t.finish(query="q", final_chunks=final or [], latency={"total_ms": total_ms})
    for name, n in (kept or {}).items():
        t.channel(name).kept_in_final = int(n)
    return t.to_dict()


def trace_with_blocks(*, executed=True, hit=4, blocks=4, kept=2, skip=None):
    """只给「图传播」一条记录的 trace（其余通道自动补齐为 not_enabled 六条）。"""
    ch = {}
    for name in CHANNEL_ORDER:
        if name == "图传播":
            ch[name] = dict(enabled=True, executed=executed, hit_count=hit,
                            hit_blocks=blocks, skip_reason=skip)
        else:
            ch[name] = dict(enabled=False, executed=False, hit_count=0)
    return make_trace(channels=ch, kept={"图传播": kept} if executed else None)


# ── 1. trace_agg ───────────────────────────────────────────────────────
def test_trace_agg_six_channels_fixed_order():
    agg = aggregate_traces([trace_with_blocks() for _ in range(3)], cases=3)
    assert [c["channel"] for c in agg["channels"]] == list(CHANNEL_ORDER)
    assert agg["cases"] == 3 and agg["traced_cases"] == 3


def test_trace_agg_kept_rate_null_when_denominator_zero():
    """§7.6.6 硬条文：分母 0 → null。填 0 会把"未跑"污染成"跑了但全被挤出"。"""
    agg = aggregate_traces([trace_with_blocks(executed=False, hit=0, blocks=0, kept=0)
                            for _ in range(2)], cases=2)
    graph = next(c for c in agg["channels"] if c["channel"] == "图传播")
    assert graph["cases_executed"] == 0
    assert graph["kept_rate"] is None
    assert graph["hit_rate"] is None and graph["hit_avg"] is None
    # 未执行也必须留下原因（9 值枚举之一）
    assert graph["skip_reason_dist"]
    assert all(r in {v.value for v in ChannelSkipReason}
               for r in graph["skip_reason_dist"])


def test_trace_agg_kept_rate_uses_block_unit_for_alias_channel():
    """「别名精确」是种子来源维度：hit_count 是种子数，保留率必须用块级分母。

    回归一个真实踩到的缺陷：用 hit_count 当分母得到 kept_rate=2.29（>100% 不可能值）。
    """
    ch = {name: dict(enabled=True, executed=True, hit_count=0, hit_blocks=0)
          for name in CHANNEL_ORDER}
    ch["别名精确"] = dict(enabled=True, executed=True, hit_count=2, hit_blocks=7)
    agg = aggregate_traces([make_trace(channels=ch, kept={"别名精确": 3})], cases=1)
    alias = next(c for c in agg["channels"] if c["channel"] == "别名精确")
    assert alias["unit"] == "seed"
    assert alias["hit_avg"] == 2.0            # 种子数
    assert alias["hit_blocks_avg"] == 7.0     # 块数
    assert alias["kept_rate"] == round(3 / 7, 4)
    assert 0.0 <= alias["kept_rate"] <= 1.0


def test_trace_agg_squeezed_pairs_with_graph_hit_total():
    """squeezed_total 必须与 graph_hit_total 同段（阴性读数的适用性前提）。"""
    agg = aggregate_traces([trace_with_blocks(hit=4, blocks=4, kept=1)
                            for _ in range(5)], cases=5)
    assert agg["squeezed_total"] == 15
    assert agg["graph_hit_total"] == 20
    assert agg["squeezed_total_graph_only"] == 15
    # 「别名精确」是种子来源维度（种子量纲），不得混进块量纲求和
    assert "别名精确" not in agg["squeezed_total_block_channels"]
    # 规格原文公式的复算值必须落盘（口径改动必须可审计）
    assert "squeezed_total_literal_spec_formula" in agg


def test_trace_agg_squeezed_total_zero_still_reports_premise():
    agg = aggregate_traces([trace_with_blocks(hit=0, blocks=0, kept=0)], cases=1)
    assert agg["squeezed_total"] == 0
    assert agg["graph_hit_total"] == 0        # 成对：0 稀释的前提是图通道也没产出
    assert agg["graph_hit_total_basis"]


def test_trace_agg_margin_histogram_edges_explicit():
    t1 = make_trace(margin=([0.80, 0.78], 0.5, True))
    t2 = make_trace(margin=([0.60], 0.5, True))         # 单候选 → margin 无定义
    t3 = make_trace(margin=([0.30, 0.29], 0.5, False))
    agg = aggregate_traces([t1, t2, t3], cases=3)
    mh = agg["margin_histogram"]
    assert mh["edges"] == MARGIN_BUCKET_EDGES      # 桶边界显式落盘，看板不得自造桶
    assert len(mh["labels"]) == len(MARGIN_BUCKET_EDGES)
    assert mh["n_triggered"] == 3 and mh["n_linked"] == 2
    assert mh["n_single_candidate"] == 1           # 不是 0——0 会被读成"两候选同分"
    assert mh["n_with_margin"] == 2
    # margin=0.02 落 [0.02,0.05)、margin=0.01 落 [0.00,0.02)：边界左闭右开
    assert mh["counts"][mh["labels"][1]] == 1
    assert mh["counts"][mh["labels"][0]] == 1
    assert sum(mh["counts"].values()) == 2


def test_trace_agg_fallback_counts_paired_with_cases_and_total_ms():
    agg = aggregate_traces([make_trace(fallbacks=["embed_failed"]),
                            make_trace()], cases=2)
    assert agg["fallback_counts"] == {"embed_failed": 1}
    # 通则：全 0/低频的降级读数必须与题量和端到端延迟同期呈现
    assert agg["cases"] == 2 and agg["total_ms"]["p50"] is not None


def test_channel_of_block_mention_attribution():
    """mention 块按 seed_path 归组（契约最容易搞错的一点）。"""
    assert channel_of_block("mention", {"seed_path": "exact"}) == "别名精确"
    assert channel_of_block("mention", {"seed_path": "semantic"}) == "语义向量"
    assert channel_of_block("mention", {"seed_path": "token"}) == "BM25 兜底"
    assert channel_of_block("edge", {}) == "图传播"
    assert channel_of_block("chapter", {}) == "篇章路由"
    assert channel_of_block("semantic_zh", {}) == "扩展查询"
    assert channel_of_block("nope", {}) is None


def test_trace_query_hash_never_stores_raw_query():
    t = make_trace()
    assert t["query_hash"] == query_hash("q")
    assert "q" not in t["query_hash"]


# ── 2. ablation（McNemar）──────────────────────────────────────────────
def _ab(**kw):
    base = {"a": True, "b": True, "c": False, "d": False}
    on = dict(base, **kw.get("on", {}))
    off = dict(base, **kw.get("off", {}))
    return mcnemar_ablation(on, off, kw.get("n_exec", 7), kw.get("flag", "f"),
                            activation=kw.get("act"), cases_executed_basis="basis")


def test_ablation_has_all_11_contract_fields():
    out = _ab(off={"b": False})      # b 题：全开通过、关闭失败（方向不可反）
    required = {"m", "b", "c", "delta_pt", "mcnemar_p", "method", "case_ids_flipped",
                "cases_executed", "cases_total", "feature_flag", "trace_schema"}
    assert required <= set(out)
    assert out["trace_schema"] == ABLATION_SCHEMA
    assert out["feature_flag"] == "f"
    assert out["cases_total"] == 4
    assert out["m"] == 1 and out["b"] == 1 and out["c"] == 0
    assert out["delta_pt"] == -25.0        # (c-b)/total*100：方向不可反
    assert out["method"] == "exact"
    assert out["mcnemar_p"] == pytest.approx(1.0, abs=1e-9)   # m=1 时双侧精确 = 1.0


def test_ablation_m_zero_returns_null_p_not_fake_one():
    """m == 0 必须在计算**之前**短路：给 1.0 是编造。"""
    out = _ab(n_exec=0)
    assert out["m"] == 0 and out["b"] == 0 and out["c"] == 0
    assert out["mcnemar_p"] is None          # 硬条文
    assert out["delta_pt"] == 0.0
    assert out["case_ids_flipped"] == []
    # 通则：Δ≈0 必须带执行计数，并写明"未触发 ≠ 无效"
    assert out["cases_executed"] == 0
    assert "未触发" in out["conclusion"] or "cases_executed" in out["conclusion"]
    assert out["delta_pt_tier"].startswith("≤1pt")


def test_ablation_method_threshold_at_25():
    """b + c < 25 → exact；>= 25 → 卡方近似（含连续性校正）。"""
    on = {f"q{i}": True for i in range(40)}
    off = dict(on)
    for i in range(12):
        off[f"q{i}"] = False          # b = 12
    for i in range(12, 24):
        on[f"q{i}"] = False           # c = 12
    small = mcnemar_ablation(on, off, 1, "flag")       # m = 24
    assert small["m"] == 24 and small["method"] == "exact"
    off2 = dict(off)
    off2["q24"] = False               # b = 13 → m = 25
    big = mcnemar_ablation(on, off2, 1, "flag")
    assert big["m"] == 25 and big["method"] == "chi2_approx_corrected"
    # 与自由度 1 卡方上尾的解析式一致（实现注记 1 要求的单测锁定）
    chi2 = (abs(big["b"] - big["c"]) - 1) ** 2 / big["m"]
    assert big["mcnemar_p"] == pytest.approx(erfc(sqrt(chi2 / 2.0)), abs=1e-9)


def test_ablation_exact_two_sided_is_capped_at_one():
    """b == c 时双侧精确恰好 1.0（合法真值，不是"假值"）。"""
    on = {f"q{i}": True for i in range(6)}
    off = dict(on)
    for i in range(3):
        off[f"q{i}"] = False
    for i in range(3, 6):
        on[f"q{i}"] = False
    out = mcnemar_ablation(on, off, 3, "flag")
    assert out["b"] == 3 and out["c"] == 3 and out["delta_pt"] == 0.0
    assert out["mcnemar_p"] == 1.0
    assert "不显著" in out["conclusion"]
    assert "无效" in out["conclusion"]          # 不显著≠无效，必须写明


def test_ablation_unpaired_ids_are_dropped_not_zero_filled():
    on = {"a": True, "only_on": True}
    off = {"a": False, "only_off": True}
    out = mcnemar_ablation(on, off, 1, "flag")
    assert out["cases_total"] == 1 and out["m"] == 1


def test_ablation_cases_executed_basis_is_carried():
    out = _ab(on={"b": False}, n_exec=42, act={"c4_candidates": 42}, flag="f")
    assert out["cases_executed"] == 42
    assert out["activation"] == {"c4_candidates": 42}
    assert out["cases_executed_basis"] == "basis"


# ── 3. diff（唯一口径）────────────────────────────────────────────────
def test_compute_flipped_direction_is_not_reversible():
    on = {"a": True, "b": False}
    off = {"a": False, "b": True}
    flipped = compute_flipped(on, off)
    assert {"id": "a", "direction": "pass_to_fail"} in flipped
    assert {"id": "b", "direction": "fail_to_pass"} in flipped
    assert len(flipped) == 2


def test_diff_source_is_ablation_case_ids_flipped():
    """diff 必须与 ablation 同源（避免两套 diff 口径漂移）。"""
    on = {"a": True, "b": False}
    off = {"a": False, "b": False}
    abl = mcnemar_ablation(on, off, 1, "flag")
    assert abl["case_ids_flipped"] == compute_flipped(on, off) == [
        {"id": "a", "direction": "pass_to_fail"}]


# ── 4. 执行计数（§7.6.6）──────────────────────────────────────────────
def test_cases_executed_counts_cases_not_occurrences():
    rows = [{"activation": {"c4_candidates": 3}}, {"activation": {"c4_candidates": 1}},
            {"activation": {"c4_candidates": 0}}, {"activation": {}}]
    n, basis, totals = cases_executed_for(rows, "plot_weak_exempt_sources")
    assert n == 2                     # 2 个**题**触发，不是 4 次
    assert totals["c4_candidates"] == 4
    assert "跳距" in basis or "豁免" in basis


def test_cases_executed_none_for_trace_only_flag():
    """纯埋点开关不改检索结果 → None（不填 0，0 会被读成"未触发"）。"""
    n, basis, _ = cases_executed_for([], "plot_trace_enabled")
    assert n is None and "不适用" in basis


def test_cases_executed_unregistered_flag_is_flagged_not_silent():
    n, basis, _ = cases_executed_for([], "plot_brand_new_flag")
    assert n == 0 and "登记" in basis


def test_activation_keys_cover_p0_switches():
    for flag in ("plot_weak_exempt_sources", "plot_ppr_node_specificity"):
        assert flag in ACTIVATION_KEYS


# ── 5. bucket 归因（§4e）──────────────────────────────────────────────
def test_bucket_priority_alias_bridge_first():
    row = {"strict_pass": False, "zh_ratio": 0.0}
    t = make_trace(seeds=0)
    assert classify_bucket(row, t) == "bucket1_alias_bridge_missing"


def test_bucket_semantic_no_margin_when_rejected():
    row = {"strict_pass": False, "zh_ratio": 0.0}
    t = make_trace(seeds=1, margin=([0.6, 0.55], 0.5, False),
                   channels={"图传播": dict(enabled=True, executed=True, hit_count=3)})
    assert classify_bucket(row, t) == "bucket2_semantic_no_margin"


def test_bucket_extraction_imbalance_when_graph_empty():
    row = {"strict_pass": False, "zh_ratio": 0.0}
    t = make_trace(seeds=2,
                   channels={"图传播": dict(enabled=True, executed=True, hit_count=0)})
    assert classify_bucket(row, t) == "bucket3_extraction_imbalance"


def test_bucket_crosslingual_and_squeeze_and_unattributed():
    zh = {"strict_pass": False, "zh_ratio": 0.2}
    t = make_trace(seeds=1, lang="zh",
                   channels={"图传播": dict(enabled=True, executed=True, hit_count=5)})
    assert classify_bucket(zh, t) == "bucket5_crosslingual"
    ok_zh = {"strict_pass": False, "zh_ratio": 0.9}
    squeezed = make_trace(seeds=1, lang="zh", kept={"图传播": 0},
                          channels={"图传播": dict(enabled=True, executed=True,
                                                   hit_count=5)})
    assert classify_bucket(ok_zh, squeezed) == "bucket4_fusion_squeeze"
    kept = make_trace(seeds=1, lang="zh", kept={"图传播": 2},
                      channels={"图传播": dict(enabled=True, executed=True,
                                               hit_count=5)})
    assert classify_bucket(ok_zh, kept) == "unattributed"


def test_bucket_attribution_only_counts_failed_cases_and_documents_rules():
    rows = [
        {"id": "1", "strict_pass": False, "zh_ratio": 0.0},
        {"id": "2", "strict_pass": True, "zh_ratio": 0.0},
    ]
    traces = [make_trace(seeds=0), make_trace(seeds=0)]
    rep = bucket_attribution(rows, traces)
    assert rep["source"].startswith("trace_rules")
    assert rep["cases_total"] == 2 and rep["cases_failed"] == 1
    assert rep["section4e"]["bucket1_alias_bridge_missing"]["cases"] == 1
    # 通过题不得被塞进任何一个桶
    assert sum(b["cases"] for b in rep["section4e"].values()) == 1
    assert all("rule" in b and "expected_reference" in b
               for b in rep["section4e"].values())


def test_bucket_attribution_handles_missing_trace():
    """缺 trace ≠ seeds_total=0：不得据此断言"别名桥缺失"（通则禁止的误读）。"""
    rows = [{"id": "1", "strict_pass": False, "zh_ratio": 0.0}]
    rep = bucket_attribution(rows, [None])
    assert rep["traced_cases"] == 0
    assert rep["section4e"]["bucket1_alias_bridge_missing"]["cases"] == 0
    assert rep["section4e"]["unattributed_no_trace"]["cases"] == 1
    assert rep["trace_signals"]["no_trace"] == 1


def test_bucket_attribution_uses_triage_caliber_when_available():
    """§4e 桶 1 的判据是「查询里没有**该证据组实体**的名字」（triage 组级分析），
    不是"本次有没有种子"——两者读数差一个数量级（曾把桶 1 报成 0 题）。"""
    rows = [{"id": "R002", "strict_pass": False, "zh_ratio": 0.0},
            {"id": "R203", "strict_pass": False, "zh_ratio": 0.0}]
    # 两题在 trace 里都有种子（token 路匹配到别的词），trace 规则判不出桶 1
    traces = [make_trace(seeds=2,
                         channels={"图传播": dict(enabled=True, executed=True,
                                                  hit_count=3)}),
              make_trace(seeds=1,
                         channels={"图传播": dict(enabled=True, executed=True,
                                                  hit_count=3)})]
    triage = {"summary": {"pass": 191},
              "items": [{"id": "R002", "reason": "alias_bridge_gap"},
                        {"id": "R203", "reason": "unreachable_gap"}]}
    rep = bucket_attribution(rows, traces, triage=triage)
    assert "triage" in rep["source"]
    assert rep["section4e"]["bucket1_alias_bridge_missing"]["cases"] == 1
    assert rep["section4e"]["bucket3_extraction_imbalance"]["cases"] == 1
    assert rep["triage_reasons"] == {"alias_bridge_gap": 1, "unreachable_gap": 1}


def test_bucket_attribution_lists_unmapped_triage_reasons_separately():
    """§4e 未列的原因必须单列：既不是五桶之一，也不是"未归因"。"""
    rows = [{"id": "R057", "strict_pass": False, "zh_ratio": 0.9}]
    triage = {"items": [{"id": "R057", "reason": "no_entity_gap"}]}
    rep = bucket_attribution(rows, [make_trace(seeds=1, lang="zh")], triage=triage)
    assert rep["unmapped_reasons"] == {"no_entity_gap": 1}
    assert rep["section4e"]["no_entity_gap"]["cases"] == 1
    assert rep["section4e"]["no_entity_gap"]["name"] == "no_entity_gap"
    assert "补实体" in rep["section4e"]["no_entity_gap"]["rule"]


def test_bucket_attribution_reports_trace_overlay_for_bucket4_5():
    rows = [{"id": "1", "strict_pass": False, "zh_ratio": 0.1}]
    traces = [make_trace(seeds=1, lang="zh", kept={"图传播": 0},
                         channels={"图传播": dict(enabled=True, executed=True,
                                                  hit_count=4)})]
    rep = bucket_attribution(rows, traces)
    assert rep["section4e"]["bucket4_fusion_squeeze"]["trace_overlay_cases"] == 1
    assert rep["section4e"]["bucket5_crosslingual"]["trace_overlay_cases"] == 1


# ── 6. 埋点不变量 ─────────────────────────────────────────────────────
def test_trace_invariance_detects_any_change():
    a = [{"id": "1", "strict_pass": True, "n_chunks": 5},
         {"id": "2", "strict_pass": False, "n_chunks": 3}]
    assert trace_invariance(a, list(a))["identical"] is True
    b = [dict(a[0]), {"id": "2", "strict_pass": True, "n_chunks": 3}]
    inv = trace_invariance(a, b)
    assert inv["identical"] is False and inv["diff_ids"] == ["2"] and inv["diff_cases"] == 1
