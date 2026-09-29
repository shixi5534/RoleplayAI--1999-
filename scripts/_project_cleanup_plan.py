# -*- coding: utf-8 -*-
"""全项目整理：**决策表**（先算清，再动手）。

分类（每类都有可核验理由）：
  JUNK      本机运行残留（pytest 临时/沙箱、空目录）→ 直接删，并补 .gitignore
  RESIDUE   一次性探针产物（未跟踪、无引用）→ 删或归入 scripts/_archive
  FIXIGNORE 应忽略但未忽略 → 补 .gitignore（不删文件，避免误伤）
  KEEP      必要文件
"""
from __future__ import annotations

import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def git(*args: str) -> str:
    r = subprocess.run(["git", *args], cwd=str(ROOT), capture_output=True)
    return r.stdout.decode("utf-8", "replace")


TRACKED = {p for p in git("ls-files", "-z").split("\0") if p}

# ── 本机运行残留（0 跟踪文件，纯垃圾）──
JUNK_DIRS = [
    ".pytest_bt", ".pytest_ws", ".pytest_tmp", ".pytest_tmp2", ".pytest_tmp3",
    ".pytest_cache", "pytest-of-Lenovo", "roleplay_test_qenmhfwr",
    "tmp_pytest", "_poc_shots", "src/data",
]

# ── 根级散落：未跟踪的一次性探针 ──
RESIDUE_FILES = [
    "_cue_feasibility.py",
    "_strip_test.js",
]

# ── 应补进 .gitignore 的条目（当前未被忽略）──
GITIGNORE_ADD = [
    (".pytest_bt/", "pytest 沙箱 basetemp（权限受限，本机残留）"),
    (".pytest_ws/", "pytest 可写 basetemp（本机调试用）"),
    ("pytest-of-Lenovo/", "pytest tmp 基目录"),
    ("roleplay_test_qenmhfwr/", "conftest 的 mkdtemp 残留"),
    ("_poc_shots/", "POC 截图临时目录"),
    ("_cue_feasibility.py", "一次性探针（标记返回可行性实测）"),
    ("_strip_test.js", "一次性原型（MarkerStripper v2 方案验证）"),
]

print("=" * 92)
print("① 本机运行残留（目录）")
print("=" * 92)
for d in JUNK_DIRS:
    p = ROOT / d
    if not p.exists():
        print(f"  [skip] {d} 不存在")
        continue
    n = sum(1 for _ in p.rglob("*") if _.is_file())
    mb = sum(f.stat().st_size for f in p.rglob("*") if f.is_file()) / 1024 / 1024
    tracked = sum(1 for t in TRACKED if t.startswith(d + "/"))
    flag = "✓ 可删" if tracked == 0 else f"⚠ 含 {tracked} 个已跟踪文件"
    print(f"  {d:26} 文件={n:<6} {mb:7.2f}MB  跟踪={tracked}  {flag}")

print()
print("=" * 92)
print("② 根级散落文件")
print("=" * 92)
for f in RESIDUE_FILES:
    p = ROOT / f
    if not p.exists():
        print(f"  [skip] {f}")
        continue
    print(f"  {f:26} {p.stat().st_size/1024:6.1f}KB  "
          f"跟踪={f in TRACKED}  引用={len([1 for t in TRACKED if t != f and f in _]) if False else '—'}")

print()
print("=" * 92)
print("③ .gitignore 缺口")
print("=" * 92)
for pat, why in GITIGNORE_ADD:
    r = subprocess.run(["git", "check-ignore", "-q", pat.rstrip("/")],
                       cwd=str(ROOT), capture_output=True)
    ignored = r.returncode == 0
    print(f"  {pat:26} 当前已忽略={ignored}   ({why})")

out = ROOT / "data/compendium_rag/reports/_project_cleanup_plan.json"
out.write_text(json.dumps({"junk_dirs": JUNK_DIRS,
                           "residue_files": RESIDUE_FILES,
                           "gitignore_add": GITIGNORE_ADD},
                          ensure_ascii=False, indent=1), encoding="utf-8")
print(f"\n-> {out.relative_to(ROOT)}")
