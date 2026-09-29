# -*- coding: utf-8 -*-
"""整理本会话新增的整理/审计脚本：保留「权威 / 被引用」，归档「被取代的迭代」。

判据（可核验）：
  KEEP    被 docs/README 或验收链引用，或是最终有效版本的入口
  ARCHIVE 同一任务的**早期迭代**（已被后续版本取代），或纯排查用的一次性脚本

归档到 scripts/_archive/tidy_20260929/（不删除，保留可回溯性）。
"""
from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# ── 保留：权威入口 / 被文档或验收链引用 ──
KEEP = {
    # 文档体系
    "_docs_reorg_plan.py",      # 分类决策表（docs/README 引用）
    "_docs_fix_refs.py",        # 引用修复（可复跑）
    "_docs_health.py",          # 文档体检（docs/README + 验收链引用）
    "_docs_ref_analysis.py",    # 引用分析（docs/README 引用）
    "_cleanup_docs_plan.py",    # 文档合并决策表（docs/README 引用）
    "_cleanup_build_chronicle.py",  # 编年史生成（可复跑）
    # 项目结构
    "_project_health.py",       # 结构体检（验收链引用）
    "_project_tidy.py",         # 清理执行器（可复跑）
    "_project_cleanup_plan.py",  # 清理决策表
}

# ── 归档：被取代的迭代 / 一次性排查 ──
ARCHIVE = [
    # data 清理早期迭代（plan2 修 plan 的路径 bug，plan3 修 plan2 的 .venv bug）
    "_cleanup_plan.py", "_cleanup_plan2.py",
    "_cleanup_scripts_plan.py", "_cleanup_tests_plan.py",
    "_cleanup_tests_verify.py", "_cleanup_evidence.py",
    "_cleanup_verify_discard.py", "_cleanup_merge_qa.py",
    "_cleanup_analyze_tests.py", "_cleanup_compare_runs.py",
    "_cleanup_check_chronicle.py",
    # docs 排查一次性
    "_doc_inventory.py", "_doc_classify.py", "_doc_classify2.py",
    "_doc_ambiguous.py", "_doc_check_uncertain.py",
    "_docs_preview_map.py", "_docs_conservation.py",
    "_docs_check_prebroken.py",
    # 项目结构排查一次性
    "_project_check_srcdata.py", "_project_srcdata_evidence.py",
    "_project_verify_targets.py", "_project_rmdir.py",
]

DEST = ROOT / "scripts" / "_archive" / "tidy_20260929"


def main() -> int:
    print("=" * 76)
    print("保留（权威 / 被引用）")
    print("=" * 76)
    for n in sorted(KEEP):
        p = ROOT / "scripts" / n
        print(f"  [KEEP]    {n:36} {'存在' if p.exists() else '缺失!'}")

    print()
    print("=" * 76)
    print("归档（被取代的迭代 / 一次性排查）")
    print("=" * 76)
    moved = 0
    for n in ARCHIVE:
        p = ROOT / "scripts" / n
        if not p.exists():
            print(f"  [skip]    {n}（不存在）")
            continue
        print(f"  [ARCHIVE] {n}")
        DEST.mkdir(parents=True, exist_ok=True)
        shutil.move(str(p), str(DEST / n))
        moved += 1
    print(f"\n归档 {moved} 个脚本 -> {DEST.relative_to(ROOT)}")

    # 归档后 scripts/ 顶层剩余数量
    left = sum(1 for _ in (ROOT / "scripts").glob("*.py"))
    print(f"scripts/*.py 数量 = {left}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
