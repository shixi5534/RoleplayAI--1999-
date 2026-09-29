# -*- coding: utf-8 -*-
"""全项目整理：**执行**（默认 dry-run）。

已确认的事实（见 _project_cleanup_plan.py 输出）：
  · 11 个本机残留目录，**0 个已跟踪文件** —— 删除不影响版本库
  · 2 个根级一次性探针（未跟踪）
  · 7 条 .gitignore 缺口

用法：
  python scripts/_project_tidy.py            # dry-run
  python scripts/_project_tidy.py --apply    # 执行
"""
from __future__ import annotations

import argparse
import os
import re
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# ── A. 本机运行残留（0 跟踪文件；已逐一核验）──
JUNK_DIRS = [
    ".pytest_bt", ".pytest_ws", ".pytest_tmp", ".pytest_tmp2", ".pytest_tmp3",
    ".pytest_cache", "pytest-of-Lenovo", "roleplay_test_qenmhfwr",
    "tmp_pytest", "_poc_shots",
]

# ── A2. 需**归档**而非直删：内容与现役数据不同（早期版本）──
# 核验（_project_srcdata_evidence.py）：src/data 的文件为 2026-07-29、规模更小、
# 已被 data/ 的 09-11/09-19 版本取代；.gitignore 早已声明 src/data/（当初即判定不入库）；
# 零代码引用。因**内容确实不同**（不是纯副本），故归档而不删，保留可回溯性。
ARCHIVE_DIR_SRC = "src/data"
ARCHIVE_DIR_DST = "scripts/_archive/src_data_20260729"

# ── B. 根级一次性探针 → 归档（不删，移入 scripts/_archive/）──
ARCHIVE = {
    "_cue_feasibility.py": "标记返回逻辑可行性实测（一次性探针）",
    "_strip_test.js": "MarkerStripper v2 原型（一次性方案验证）",
}

# ── C. .gitignore 缺口 ──
GITIGNORE_BLOCK = """
# ── 本机运行残留（2026-09-29 整理补充）──────────────────────────────
# 下列目录由 pytest / conftest 在本机生成，属「沙箱产物」，不入库。
# 历史上它们未列入 .gitignore，会持续污染 `git status`。
.pytest_bt/
.pytest_ws/
.pytest_tmp*/
pytest-of-Lenovo/
roleplay_test_qenmhfwr/
_poc_shots/

#   根级一次性探针（已归档到 scripts/_archive/，防复发）
/_cue_feasibility.py
/_strip_test.js
"""


def git_tracked() -> set[str]:
    r = subprocess.run(["git", "ls-files", "-z"], cwd=str(ROOT),
                       capture_output=True)
    return {p for p in r.stdout.decode("utf-8", "replace").split("\0") if p}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()
    TRACKED = git_tracked()

    print("=" * 88)
    print("A. 删除本机运行残留")
    print("=" * 88)
    removed = 0
    for d in JUNK_DIRS:
        p = ROOT / d
        if not p.exists():
            print(f"  [skip] {d}（不存在）")
            continue
        n_tracked = sum(1 for t in TRACKED if t.startswith(d + "/"))
        if n_tracked:
            print(f"  [SKIP] {d} 含 {n_tracked} 个已跟踪文件 —— 不动")
            continue
        n = sum(1 for f in p.rglob("*") if f.is_file())
        mb = sum(f.stat().st_size for f in p.rglob("*") if f.is_file()) / 1048576
        print(f"  [DEL]  {d:26} {n:>5} 文件  {mb:7.2f}MB")
        if args.apply:
            shutil.rmtree(p, ignore_errors=True)
        removed += 1

    print()
    print("=" * 88)
    print("A2. 归档早期版本的 src/data（内容与现役不同，故不直删）")
    print("=" * 88)
    sd = ROOT / ARCHIVE_DIR_SRC
    if sd.exists():
        n = sum(1 for f in sd.rglob("*") if f.is_file())
        print(f"  [MOVE] {ARCHIVE_DIR_SRC} -> {ARCHIVE_DIR_DST}   ({n} 文件)")
        if args.apply:
            dst = ROOT / ARCHIVE_DIR_DST
            dst.parent.mkdir(parents=True, exist_ok=True)
            if dst.exists():
                shutil.rmtree(dst, ignore_errors=True)
            shutil.move(str(sd), str(dst))
    else:
        print(f"  [skip] {ARCHIVE_DIR_SRC}（不存在）")

    print()
    print("=" * 88)
    print("B. 归档根级一次性探针")
    print("=" * 88)
    arch = ROOT / "scripts" / "_archive"
    for name, why in ARCHIVE.items():
        src = ROOT / name
        if not src.exists():
            print(f"  [skip] {name}（不存在）")
            continue
        dst = arch / name
        print(f"  [MOVE] {name} -> scripts/_archive/{name}   ({why})")
        if args.apply:
            arch.mkdir(parents=True, exist_ok=True)
            shutil.move(str(src), str(dst))

    print()
    print("=" * 88)
    print("C. 补 .gitignore")
    print("=" * 88)
    gi = ROOT / ".gitignore"
    text = gi.read_text(encoding="utf-8")
    if ".pytest_bt/" in text:
        print("  [skip] 已含本块")
    else:
        print("  [ADD]  追加 7 条（6 目录 + 2 探针，去重后）")
        if args.apply:
            if not text.endswith("\n"):
                text += "\n"
            gi.write_text(text + GITIGNORE_BLOCK, encoding="utf-8")

    print()
    print("=" * 88)
    if args.apply:
        print(f"完成：删 {removed} 个残留目录，归档 {len(ARCHIVE)} 个探针，补 .gitignore")
    else:
        print("（dry-run；加 --apply 执行）")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
