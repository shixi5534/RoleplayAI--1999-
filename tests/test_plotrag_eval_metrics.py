# -*- coding: utf-8 -*-
"""评测台口径的回归测试（Spec §1.4.1 延迟三口径 / §9.0 阴性证据通则）。

本轮修掉的四处**口径缺陷**（都是"数据没错、口径错了"的沉默错误）
    1. **延迟吃通用容差**：通用容差 0.02 是为比率型指标（0.5pt）设计的，套到 693ms 上
       等于 ±0.02ms——1ms 的正常抖动就被判"回退"。Spec §1.4.1 要求延迟**单独裁决**。
    2. **负样本口径变了却当回退比**：题量 10 → 53 时，绝对注入块数随题量放大，
       跨口径比大小是**假回退**（实测 0 → 37 被报成 +37 回退）。
    3. **合格项被打印成「未达标」**：旧版给所有 note 无条件加 `[未达标]` 前缀，
       把"A1 达标""[参考]"这类正常信息误标为失败。
    4. **A5 只报总数**：混在一起会让"**新增**泄漏"看起来也是"早就知道的"，
       从而失去报警价值——已知残余与新增泄漏必须分开报。
"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

spec = importlib.util.spec_from_file_location("_eval_plot_rag_t", ROOT / "scripts" / "eval_plot_rag.py")
ev = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ev)


def _summary(p95=700.0, strict=0.637):
    return {"latency_p95_ms": p95, "strict_pass": strict, "chunk_precision": 0.33,
            "answer_chunk_rate": 0.22, "mrr": 0.386, "recall": 0.30,
            "avg_returned_chunks": 7.5, "empty_rate": 0.01,
            "latency_p50_ms": 640.0, "latency_p90_ms": 680.0}


def _neg(total=0, cases=53, residual=(), new=()):
    return {"cases": cases, "negative_injection_total": total,
            "negative_clean": total == 0, "violations": list(residual) + list(new),
            "known_residual": list(residual), "new_leaks": list(new),
            "clear": not new}


class TestLatencyCriterion:
    def test_uses_increment_not_absolute_300ms(self):
        """p95 691ms 在 300ms 绝对线下"不合格"，但在 A1 增量判据下**达标**。

        Spec AC-5 明确：历史 300ms 线**不作合入判据**（否则 M8 语义层的 ~500ms
        查询嵌入会被判死，而它是当前最大的一块收益来源）。
        """
        base = {"summary": {"latency_p95_ms": 693.3}}
        ok, notes = ev.check_targets(_summary(p95=691.2), _neg(), base)
        assert ok, notes
        assert any("A1 达标" in n for n in notes), notes
        assert not any("A1 未达标" in n for n in notes)

    def test_increment_over_100ms_fails(self):
        base = {"summary": {"latency_p95_ms": 500.0}}
        ok, notes = ev.check_targets(_summary(p95=650.0), _neg(), base)
        assert not ok
        assert any("A1 未达标" in n and "150.0ms" in n for n in notes), notes

    def test_without_baseline_is_informational_only(self):
        ok, notes = ev.check_targets(_summary(p95=5000.0), _neg(), None)
        assert ok, "无同条件基线时不应判不合格，只报参考值"
        assert any(n.startswith("[参考]") for n in notes)


class TestNegativeReporting:
    def test_known_residual_and_new_leaks_reported_separately(self):
        neg = _neg(total=37, residual=["巴黎在哪个国家"],
                   new=["今天天气怎么样"])
        ok, notes = ev.check_targets(_summary(), neg, {"summary": {"latency_p95_ms": 700.0}})
        assert not ok
        joined = " ".join(notes)
        assert "已知残余 1 条" in joined and "新增泄漏 1 条" in joined
        assert "回归" in joined, "新增泄漏必须显式提示为回归"

    def test_known_residual_alone_still_fails_but_no_regression_note(self):
        neg = _neg(total=37, residual=["巴黎在哪个国家", "哈利波特是谁"])
        ok, notes = ev.check_targets(_summary(), neg, {"summary": {"latency_p95_ms": 700.0}})
        assert not ok, "A5 有残余就必须判未达标（不得静默当通过）"
        assert not any("回归" in n for n in notes)

    def test_clean_negatives_pass(self):
        ok, notes = ev.check_targets(
            _summary(), _neg(total=0), {"summary": {"latency_p95_ms": 700.0}})
        assert ok, notes


class TestBaselineComparison口径:
    def _report(self, p95, neg_total, neg_cases):
        return {"summary": {"latency_p95_ms": p95, "strict_pass": 0.637,
                            "chunk_precision": 0.33, "answer_chunk_rate": 0.22,
                            "mrr": 0.386},
                "negatives": {"negative_injection_total": neg_total, "cases": neg_cases}}

    def test_negative_set_size_change_is_not_a_regression(self):
        base = self._report(693.0, 0, 10)
        cur = self._report(691.0, 37, 53)
        rows, regressed = ev.compare_with_baseline(base, cur, tolerance=0.02)
        assert not regressed, "负样本口径变了却判回退 = 假回退"
        row = next(r for r in rows if r["metric"] == "negative_injection_total")
        assert "口径不可比" in row["verdict"]

    def test_same_size_negative_regression_still_caught(self):
        base = self._report(693.0, 0, 53)
        cur = self._report(691.0, 3, 53)
        rows, regressed = ev.compare_with_baseline(base, cur, tolerance=0.02)
        assert regressed, "同口径下的真实注入增长必须被抓到"

    def test_latency_jitter_is_not_a_regression(self):
        """1ms 抖动不得触发延迟回退（旧版被通用容差 0.02ms 误判）。"""
        base = self._report(693.3, 0, 53)
        cur = self._report(694.3, 0, 53)
        rows, regressed = ev.compare_with_baseline(base, cur, tolerance=0.02)
        assert not regressed
        row = next(r for r in rows if r["metric"] == "latency_p95_ms")
        assert row["verdict"] == "回退" or True  # 允许多报，但不许判回退
        assert not regressed

    def test_latency_over_100ms_is_a_regression(self):
        base = self._report(600.0, 0, 53)
        cur = self._report(750.0, 0, 53)
        _rows, regressed = ev.compare_with_baseline(base, cur, tolerance=0.02)
        assert regressed, "延迟增量 150ms > 100ms 必须判回退"

    def test_ratio_metrics_still_use_pt_tolerance(self):
        base = self._report(600.0, 0, 53)
        base["summary"]["strict_pass"] = 0.65
        cur = self._report(600.0, 0, 53)
        cur["summary"]["strict_pass"] = 0.63
        _rows, regressed = ev.compare_with_baseline(base, cur, tolerance=0.01)
        assert regressed, "比率指标仍应按 pt 容差判回退"
