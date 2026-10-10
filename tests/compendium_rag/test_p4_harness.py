# -*- coding: utf-8 -*-
"""P4.2 装置改造的离线单元/集成测试（`scripts/audit_l3.py`）。

覆盖任务书 (A)(B)(C) 三处改造：
  A 批次项改用 compose 正式提示词，逐字同源、history=None、gold 不泄漏；
  B 进窗块数用**溯源头正则**数（不是 `[S{n}]` 最大值），幻觉率并排两列；
  C 小样本子集 + 产物目录/文件名分离，且报告回写题数与口径标。

沙箱注意：DSH 下 pytest 的 ``tmp_path`` 会 WinError 5，本文件**不使用 tmp_path**，
改用 ``scratch_dir`` 夹具（在仓库根下自建目录，用例后 shutil.rmtree 清理）。
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
for _p in (ROOT / "src", ROOT / "scripts"):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

AUDIT_L3 = ROOT / "scripts" / "audit_l3.py"


def _load_audit_l3():
    """按文件路径载入 audit_l3（scripts/ 不是包，避免与 test 同名模块冲突）。"""
    spec = importlib.util.spec_from_file_location("audit_l3_under_test", AUDIT_L3)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def A():
    return _load_audit_l3()


@pytest.fixture
def scratch_dir():
    """仓库根下的临时目录（避开沙箱下不可写的 tmp_path / 系统 temp）。"""
    d = ROOT / "_p4_test_scratch"
    if d.exists():
        shutil.rmtree(d, ignore_errors=True)
    d.mkdir(parents=True, exist_ok=True)
    try:
        yield d
    finally:
        shutil.rmtree(d, ignore_errors=True)


def _args(**kw):
    base = dict(tag="", input_dir="", state_dir="", reports_dir="",
                report_name="", n_questions=0, sample_seed=0, limit=0)
    base.update(kw)
    return argparse.Namespace(**base)


# ───────────────────────── A：compose 提示词同源 ─────────────────────────

class TestPromptModeA:
    def test_prompt_mode_constants_frozen(self, A):
        assert A.PROMPT_MODE == "compose_v1"
        assert A.ROLE_CARD_MODE == "empty"
        assert A.HISTORY_MODE == "none"

    def test_batch_item_carries_compose_prompt(self, A):
        from compendium_rag.compose import ANSWER_SYSTEM_PROMPT, render_prompt
        ctx = "【原文证据】\n[S1 chunk=c1 doc=d1 cat=story] [d1#0] 甲。\n"
        it = A.build_batch_item("q1", "这是什么？", ctx, n_evidence_retrieved=5)
        assert it["prompt"] == render_prompt("这是什么？", ctx, role_card="",
                                             history=None)
        # prompt 即 compose 摊平产物：首块是 system，逐字含系统提示词
        assert it["prompt"].startswith("## system")
        assert ANSWER_SYSTEM_PROMPT[:40] in it["prompt"]
        assert "## user" in it["prompt"]

    def test_batch_item_history_is_null(self, A):
        it = A.build_batch_item("q1", "q", "ctx")
        assert it["history"] is None
        assert it["prompt_mode"] == "compose_v1"
        assert it["role_card_mode"] == "empty"
        # 双盲前提：批次 prompt 里不得出现任何对话历史分节
        assert "## assistant" not in it["prompt"]

    def test_batch_item_backward_compatible_and_gold_free(self, A):
        it = A.build_batch_item("q1", "q", "ctx")
        assert it["query"] == "q" and it["context"] == "ctx"     # 老判分链路
        for leak in ("keywords", "ref", "set", "dims", "gold"):
            assert leak not in it, f"gold 字段泄漏：{leak}"

    def test_batch_meta_records_all_caliber_marks(self, A):
        m = A._batch_meta(subset={"mode": "stratified_sample"})
        assert m["schema"] == "audit.l3_batch/v2"
        assert m["prompt_mode"] == "compose_v1"
        assert m["role_card_mode"] == "empty"
        assert m["history"] == "none"
        assert m["allocator"] == "v2_perblock"
        assert len(m["system_prompt_sha16"]) == 16

    def test_role_card_empty_by_design(self, A):
        # 题集无角色归属字段 → 统一 role_card=""，且不得出现「角色卡」分节
        it = A.build_batch_item("q1", "q", "ctx")
        assert "【角色卡】" not in it["prompt"]


# ───────────────────── B：进窗块数（溯源头正则） ─────────────────────

CTX_OK = (
    "【图谱实体】\n  - 维也纳\n【原文证据】\n"
    "[S1 chunk=c1 doc=d1 cat=story] [d1#0] 一九九九年。\n"
    "[S2 chunk=c2 doc=d1 cat=story] [d1#1] 暴雨。\n"
    "[S3 chunk=c3 doc=d2 cat=story] [d2#0] 她自称「[S1] 归来」。\n"
)


class TestBlocksInWindowB:
    def test_counts_only_provenance_rows(self, A):
        r = A.count_blocks_in_window(CTX_OK)
        assert r["n_blocks_in_window"] == 3
        assert r["block_numbers"] == [1, 2, 3]
        assert r["blocks_contiguous"] is True
        assert r["window_fallback"] is False

    def test_inline_reference_not_counted_as_block(self, A):
        """块内 `[S1]` 引用（无 chunk=/doc=/cat=）不算块 —— 这正是不能用
        「全文 [S{n}] 最大值」猜块数的原因。"""
        ctx = ("【原文证据】\n"
               "[S1 chunk=c1 doc=d1 cat=s] [d1#0] 见 [S7]。\n"
               "[S2 chunk=c2 doc=d1 cat=s] [d1#1] 另见 [S9]。\n")
        r = A.count_blocks_in_window(ctx)
        naive_max = max(int(n) for n in __import__("re").findall(r"\[S(\d+)\]", ctx))
        assert r["n_blocks_in_window"] == 2
        assert naive_max == 9              # 最大值口径会得 9 → 口径不同
        assert r["n_blocks_in_window"] != naive_max

    def test_numbering_contiguous_after_skips(self, A):
        """跳块让号前移：渲染器按窗口顺序从 1 连续编号，绝不跳号。"""
        ctx = ("【原文证据】\n"
               "[S1 chunk=c1 doc=d1 cat=s] [d1#0] 甲。\n"
               "[S2 chunk=c2 doc=d1 cat=s] [d1#1] 乙。\n")
        r = A.count_blocks_in_window(ctx)
        assert r["block_numbers"] == list(range(1, len(r["block_numbers"]) + 1))
        assert r["blocks_contiguous"] is True

    def test_r4_fallback_is_zero_blocks(self, A):
        """R4 保底：一块都装不下 → 截断注入 + [节选]，无带编号块。"""
        r = A.count_blocks_in_window("【原文证据】\n[节选] 甲。\n[节选] 乙。\n")
        assert r["n_blocks_in_window"] == 0
        assert r["window_fallback"] is True

    def test_ignores_rows_outside_evidence_section(self, A):
        ctx = ("[S1 chunk=c1 doc=d1 cat=s] 这是【图谱实体】段里的伪头，不算。\n"
               "【原文证据】\n[S1 chunk=x doc=x cat=x] 真块。\n")
        assert A.count_blocks_in_window(ctx)["n_blocks_in_window"] == 1

    def test_provenance_regex_anchors_line_start(self, A):
        assert A.RE_PROV_HEADER.pattern.startswith("(?m)^\\[S")
        assert "chunk|doc|cat" in A.RE_PROV_META.pattern


# ───────────────── C：子集抽样 + 目录分离 ─────────────────

def _rows(n_per_set=10):
    rows = []
    for st in ("300cn", "blind", "gen", "unanswerable", "negative"):
        for i in range(n_per_set):
            rows.append({"qid": f"{st}-{i}", "set": st, "query": f"q{i}",
                         "keywords": [], "ref": ""})
    return rows


class TestSubsetC:
    def test_select_rows_covers_all_five_sets(self, A):
        out = A.select_rows(_rows(), 10, seed=A.SEED)
        assert len(out) == 10
        assert {r["set"] for r in out} == {"300cn", "blind", "gen",
                                           "unanswerable", "negative"}

    def test_select_rows_deterministic(self, A):
        a = [r["qid"] for r in A.select_rows(_rows(), 12, seed=A.SEED)]
        b = [r["qid"] for r in A.select_rows(_rows(), 12, seed=A.SEED)]
        assert a == b

    def test_select_rows_full_when_n_exceeds(self, A):
        rows = _rows(2)
        assert len(A.select_rows(rows, 999)) == len(rows)
        assert len(A.select_rows(rows, 0)) == len(rows)

    def test_apply_subset_default_is_full(self, A):
        rows = _rows()
        out, sub = A.apply_subset(rows, _args())
        assert len(out) == len(rows)
        assert sub["mode"] == "full"
        assert sub["n_selected"] == len(rows) and sub["n_all"] == len(rows)

    def test_apply_subset_stratified_and_limit(self, A):
        rows = _rows()
        out, sub = A.apply_subset(rows, _args(n_questions=15))
        assert sub["mode"] == "stratified_sample"
        assert sub["n_requested"] == 15 and sub["n_selected"] == 15
        out2, sub2 = A.apply_subset(rows, _args(limit=7))
        assert sub2["mode"] == "head_limit" and len(out2) == 7

    def test_paths_for_tag_isolates_from_frozen_full(self, A):
        p = A.paths_for(_args(tag="unittest"))
        assert p.state_dir == A.AUDIT_DIR / "p4_harness_unittest"
        assert p.batch_dir != A.BATCH_DIR
        assert p.gold_map != A.GOLD_MAP
        assert p.report.name == "p4_harness_unittest.json"
        assert p.manifest != A.MANIFEST

    def test_paths_for_no_tag_falls_back_to_v8(self, A):
        p = A.paths_for(_args())
        assert p.state_dir == A.AUDIT_DIR
        assert p.batch_dir == A.BATCH_DIR
        assert p.report == A.REPORTS_DIR / "audit_l3.json"

    def test_paths_for_empty_string_does_not_become_cwd(self, A):
        """回归：空串参数曾被 `or` 误判成 Path('.')（cwd），导致读题集失败。"""
        p = A.paths_for(_args(tag="t", input_dir="", reports_dir=""))
        assert p.input_dir == A.AUDIT_DIR
        assert p.input_dir.is_absolute() and p.input_dir != Path(".")
        assert p.report.parent == A.REPORTS_DIR

    def test_paths_for_explicit_state_and_reports_dir(self, A):
        p = A.paths_for(_args(state_dir="tmp/state", reports_dir="tmp/rep",
                              report_name="custom"))
        assert p.state_dir == Path("tmp/state")
        assert p.batch_dir == Path("tmp/state/l3_batches")
        assert p.report == Path("tmp/rep/custom.json")

    def test_side_report_naming(self, A):
        assert A.side_report(Path("x/p4_harness_t.json"), "prepare").name == \
            "p4_harness_t_prepare.json"
        assert A.side_report(Path("p.json"), "judgeprep").name == \
            "p_judgeprep.json"


# ───────────────── 降级路径与并排两列口径 ─────────────────

class TestDegradeAndColumns:
    def test_degrade_reason_three_states(self, A):
        assert isinstance(A.degrade_reason(gold_present=False, n_judges=0,
                                           n_answers=0), str)
        mid = A.degrade_reason(gold_present=True, n_judges=0, n_answers=5)
        assert isinstance(mid, str) and "N/A" in mid and "5" in mid
        assert A.degrade_reason(gold_present=True, n_judges=10,
                                n_answers=10) is None

    def test_rate_none_on_zero_denominator(self, A):
        """无样本 ≠ 零幻觉：分母 0 必须回 None（gate 落 N/A），不是 0.0。"""
        assert A._rate(0, 0) is None
        assert A._rate(1, 4) == 0.25

    def test_hallucination_columns_side_by_side(self, A):
        rows = [
            {"qid": "a", "set": "300cn", "scored": True, "hallucination": True,
             "offscript_screen": False},
            {"qid": "b", "set": "blind", "scored": True, "hallucination": False,
             "offscript_screen": True},
            {"qid": "c", "set": "negative", "scored": True, "hallucination": False,
             "offscript_screen": True},
            {"qid": "d", "set": "unanswerable", "scored": True,
             "hallucination": False, "offscript_screen": False},
            {"qid": "e", "set": "gen", "scored": False, "hallucination": False,
             "offscript_screen": None},
        ]
        c = A._hallucination_columns(rows)
        # 窗内：域内题 (a,b) × judge 判定 → 1/2
        assert c["hallucination_rate_in_window"] == 0.5
        # 全语料 offscript：所有有初筛结果的题 (a,b,c,d) → 2/4
        assert c["hallucination_rate_offscript_all"] == 0.5
        assert c["offscript_all_hits"] == 2 and c["offscript_all_denominator"] == 4
        # 越界：c,d 的 judge 判定 → 0/2
        assert c["offscript_hallucination_rate"] == 0.0
        # 兼容别名
        assert c["hallucination_rate"] == c["hallucination_rate_in_window"]
        assert c["n_in_scope"] == 2 and c["n_out_scope"] == 2

    def test_window_stats_key_names_match_collect(self, A):
        items = [{"n_blocks_in_window": 3, "n_evidence_retrieved": 6,
                  "window_fallback": False, "blocks_contiguous": True},
                 {"n_blocks_in_window": 0, "n_evidence_retrieved": 2,
                  "window_fallback": True, "blocks_contiguous": False}]
        s = A._window_stats(items)
        for k in ("n_blocks_in_window_mean", "n_blocks_in_window_min",
                  "n_blocks_in_window_max", "n_zero_block_questions",
                  "n_window_fallback_questions", "n_evidence_retrieved_mean"):
            assert k in s, f"缺少与 collect 侧同名的键：{k}"
        assert s["n_blocks_in_window_mean"] == 1.5
        assert s["n_zero_block_questions"] == 1
        assert s["n_window_fallback_questions"] == 1
        # 旧别名保留（向后兼容）
        assert s["mean_blocks_in_window"] == s["n_blocks_in_window_mean"]

    def test_modes_registry(self, A):
        assert set(A.MODES) == {"prepare", "judge-prep", "collect"}


# ───────────── 端到端：小样本 prepare → 降级 collect（子进程） ─────────────

def _run_cli(args, cwd=ROOT):
    cmd = [str(ROOT / ".venv" / "Scripts" / "python.exe"), "-X", "utf8",
           str(AUDIT_L3), *args]
    p = subprocess.run(cmd, cwd=str(cwd), capture_output=True, text=True,
                       encoding="utf-8", errors="replace")
    return p.returncode, (p.stdout or "") + (p.stderr or "")


class TestEndToEnd:
    """端到端用子进程实跑 CLI（离线；写面带隔离目录，不碰定版全量产物）。"""
    def test_prepare_subset_then_degraded_collect(self, A, scratch_dir):
        state = scratch_dir / "state"
        rdir = scratch_dir / "reports"
        rc, out = _run_cli(["--mode", "prepare", "--n-questions", "3",
                            "--state-dir", str(state), "--reports-dir", str(rdir),
                            "--report-name", "p4_harness_ut"])
        assert rc == 0, out[-800:]
        batches = sorted((state / "l3_batches").glob("ans_b*.json"))
        assert batches, "批次未落盘"
        items = [x for b in batches
                 for x in json.loads(b.read_text(encoding="utf-8"))["items"]]
        assert len(items) == 3
        assert all(x["prompt_mode"] == "compose_v1" for x in items)
        assert all(x["history"] is None for x in items)
        assert all("n_blocks_in_window" in x for x in items)
        # prepare 侧报告回写题目数/子集/allocator/prompt_mode
        pr = json.loads((rdir / "p4_harness_ut_prepare.json")
                        .read_text(encoding="utf-8"))
        m = pr["metrics"]
        assert m["n_questions"] == 3
        assert m["subset"]["mode"] == "stratified_sample"
        assert m["allocator"] == "v2_perblock"
        assert m["prompt_mode"] == "compose_v1"
        assert "n_blocks_in_window_mean" in m

        # 无判分产物 → 优雅降级：不崩、gate 全 N/A、报告仍写出
        rc2, out2 = _run_cli(["--mode", "collect", "--state-dir", str(state),
                              "--reports-dir", str(rdir),
                              "--report-name", "p4_harness_ut"])
        assert "Traceback" not in out2, out2[-800:]
        rep = json.loads((rdir / "p4_harness_ut.json").read_text(encoding="utf-8"))
        gm = rep["metrics"]
        assert gm["degraded"] is True
        assert gm["hallucination_rate_in_window"] is None
        assert "hallucination_rate_offscript_all" in gm
        l3 = {g["gate"].split()[0]: g["verdict"] for g in rep["gate_verdicts"]}
        assert all(v == "N/A" for k, v in l3.items()
                   if k.startswith("L3.") and not k.startswith("L3.7")), l3
        assert rep["artifact_scope"]["n_questions"] == 3

    def test_collect_without_gold_reports_no_judgement(self, A, scratch_dir):
        empty = scratch_dir / "empty"
        empty.mkdir(parents=True, exist_ok=True)
        rc, out = _run_cli(["--mode", "collect", "--state-dir", str(empty),
                            "--reports-dir", str(scratch_dir / "r"),
                            "--report-name", "p4_harness_ut_empty"])
        assert "无判分产物" in out
        assert "Traceback" not in out
        assert rc == 1

    def test_prepare_does_not_touch_frozen_full_artifacts(self, A, scratch_dir):
        """冒烟纪律：写面带隔离目录时，定版全量产物路径必须原封不动。"""
        before = {
            "batches": sorted(p.name for p in A.BATCH_DIR.glob("*.json")),
            "gold": A.GOLD_MAP.stat().st_mtime_ns if A.GOLD_MAP.exists() else None,
            "report": (A.OUT.stat().st_mtime_ns if A.OUT.exists() else None),
        }
        rc, out = _run_cli(["--mode", "prepare", "--n-questions", "2",
                            "--state-dir", str(scratch_dir / "s2"),
                            "--reports-dir", str(scratch_dir / "r2"),
                            "--report-name", "p4_harness_ut2"])
        assert rc == 0, out[-800:]
        after = {
            "batches": sorted(p.name for p in A.BATCH_DIR.glob("*.json")),
            "gold": A.GOLD_MAP.stat().st_mtime_ns if A.GOLD_MAP.exists() else None,
            "report": (A.OUT.stat().st_mtime_ns if A.OUT.exists() else None),
        }
        assert before == after, "定版全量产物被冒烟改动"
