# -*- coding: utf-8 -*-
"""清理前的**证据收集**：哪些测试/脚本是真正必要的，哪些是历史一次性产物。

判据（可机械核验，不靠文件名印象）：
  A. 被 pytest 收集的测试文件（testpaths=tests, 命名 test_*.py）
  B. 未被收集的"伪测试"（放在 tests/ 但 pytest 不会跑）
  C. 每个测试文件测的 src 模块是否存在（无对应模块 = 可能测的是已删代码）
  D. 脚本的**被引用度**（是否被其它脚本/src/docs 提到）—— 零引用 = 一次性产物候选
"""
from __future__ import annotations

import json
import re
import subprocess
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def tracked(pat: str) -> list[str]:
    """注意：desktop/node_modules 等大量路径会让 `git ls-files <glob>` 极慢，
    故统一用**全量列表 + 前缀过滤**（一次调用，结果缓存）。"""
    global _ALL_TRACKED
    if _ALL_TRACKED is None:
        r = subprocess.run(["git", "ls-files", "-z"], cwd=str(ROOT),
                           capture_output=True)
        _ALL_TRACKED = [x for x in r.stdout.decode("utf-8", "replace").split("\0") if x]
    prefix = pat.rstrip("*")
    return [p for p in _ALL_TRACKED if p.startswith(prefix)]


_ALL_TRACKED: list[str] | None = None


print("=" * 90)
print("① tests/ 组成")
print("=" * 90)
tests = tracked("tests/*")
py_tests = [t for t in tests if t.endswith(".py")]
collected = [t for t in py_tests
             if Path(t).name.startswith("test_") and "/" in t]
not_collected = [t for t in py_tests if t not in collected]
print(f"  tests/ 已跟踪文件 = {len(tests)}")
print(f"  pytest 会收集（test_*.py）= {len(collected)}")
print(f"  **不会收集**（伪测试/辅助）= {len(not_collected)}:")
for t in not_collected:
    ln = len((ROOT / t).read_text(encoding="utf-8", errors="replace").splitlines())
    print(f"     {t:48} {ln:>5} 行")

print()
print("=" * 90)
print("② 每个测试文件的规模（行数）—— 找出验证性巨物")
print("=" * 90)
sizes = sorted(((len((ROOT / t).read_text(encoding="utf-8",
                                          errors="replace").splitlines()), t)
                for t in collected), reverse=True)
for n, t in sizes:
    print(f"  {n:>5}  {t}")

print()
print("=" * 90)
print("③ 脚本被引用度（src/tests/docs/其它脚本 中提到该文件名的次数）")
print("=" * 90)
scripts = [s for s in tracked("scripts/*.py")]
corpus: list[tuple[str, str]] = []
for g in ("src/**/*.py", "tests/**/*.py", "scripts/**/*.py", "docs/**/*.md", "*.md"):
    for p in ROOT.glob(g):
        if p.is_file() and ".venv" not in p.parts:
            try:
                corpus.append((str(p.relative_to(ROOT)).replace("\\", "/"),
                               p.read_text(encoding="utf-8", errors="replace")))
            except Exception:
                pass
print(f"  语料文件数 = {len(corpus)}；脚本数 = {len(scripts)}")

refcnt = Counter()
for name, text in corpus:
    for s in scripts:
        base = Path(s).name
        if base == Path(name).name:
            continue
        if base in text:
            refcnt[base] += 1

zero = sorted(s for s in scripts if refcnt[Path(s).name] == 0)
print(f"\n  **零引用脚本** = {len(zero)} / {len(scripts)}")
groups = Counter()
for s in zero:
    b = Path(s).stem
    m = re.match(r"^(_[a-z0-9]+)", b)
    groups[m.group(1) if m else "(其它)"] += 1
for k, v in groups.most_common(20):
    print(f"     {k:12} {v}")
print()
print("  零引用样例（前 40）:")
for s in zero[:40]:
    print(f"     {s}")
