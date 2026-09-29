# -*- coding: utf-8 -*-
"""执行前最后核验：待归档/删除的对象是否被引用。"""
from __future__ import annotations

import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

TARGETS = ["_cue_feasibility.py", "_strip_test.js"]
r = subprocess.run(["git", "ls-files", "-z"], cwd=str(ROOT), capture_output=True)
TRACKED = [p for p in r.stdout.decode("utf-8", "replace").split("\0") if p]
SKIP = {".venv", "node_modules", ".git", "__pycache__", ".pytest_cache"}

print("=" * 84)
print("① 根级探针是否被引用")
print("=" * 84)
for t in TARGETS:
    hits = []
    for f in TRACKED:
        if f == t or (SKIP & set(Path(f).parts)):
            continue
        fp = ROOT / f
        try:
            if fp.stat().st_size < 3_000_000 and t in fp.read_text(
                    encoding="utf-8", errors="replace"):
                hits.append(f)
        except Exception:
            pass
    print(f"  {t:26} 被引用={hits if hits else '无'}")

print()
print("=" * 84)
print("② src/data 内容（疑似运行时残留）")
print("=" * 84)
sd = ROOT / "src" / "data"
if sd.exists():
    for f in sorted(sd.rglob("*")):
        if f.is_file():
            print(f"  {f.relative_to(ROOT)}  {f.stat().st_size} B")
    print(f"  已跟踪文件数 = {sum(1 for t in TRACKED if t.startswith('src/data/'))}")

print()
print("=" * 84)
print("③ src/ 代码是否把 src/data 当默认路径")
print("=" * 84)
found = []
for f in TRACKED:
    if not f.startswith("src/") or not f.endswith(".py"):
        continue
    t = (ROOT / f).read_text(encoding="utf-8", errors="replace")
    for pat in ("src/data", '"data"', "'data'"):
        if pat in t:
            found.append((f, pat))
            break
for f, pat in found[:10]:
    print(f"  {f}  含 {pat}")
if not found:
    print("  （无引用）")

print()
print("=" * 84)
print("④ _poc_shots 是否被引用")
print("=" * 84)
hits = [f for f in TRACKED if "_poc_shots" in (ROOT / f).read_text(
    encoding="utf-8", errors="replace") if (ROOT / f).is_file()
    and (ROOT / f).stat().st_size < 3_000_000]
print(f"  _poc_shots 被引用={hits if hits else '无'}")
print(f"  该目录已跟踪文件数={sum(1 for t in TRACKED if t.startswith('_poc_shots/'))}")
