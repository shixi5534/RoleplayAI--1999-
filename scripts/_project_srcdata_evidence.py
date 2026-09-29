# -*- coding: utf-8 -*-
"""确认 src/data 是**旧版残留**（非当前数据）：时间/规模/引用三重证据。"""
from __future__ import annotations

import subprocess
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

print("=" * 84)
print("① 时间与规模（src/data 为早期误落盘）")
print("=" * 84)
for p in ("src/data/characters/wu_ming_zhe.json",
          "data/characters/wu_ming_zhe.json",
          "src/data/knowledge/persona.json",
          "data/knowledge/persona.json",
          "src/data/sessions/diag-0002.json"):
    f = ROOT / p
    if not f.exists():
        print(f"  {p:44} (不存在)")
        continue
    mt = time.strftime("%Y-%m-%d %H:%M", time.localtime(f.stat().st_mtime))
    print(f"  {p:44} {f.stat().st_size:>7} B  {mt}")

print()
print("=" * 84)
print("② 代码是否**硬编码**指向 src/data")
print("=" * 84)
r = subprocess.run(["git", "ls-files", "-z"], cwd=str(ROOT), capture_output=True)
TRACKED = [p for p in r.stdout.decode("utf-8", "replace").split("\0") if p]
hits = []
for f in TRACKED:
    if not f.endswith((".py", ".toml", ".bat", ".env.example", ".md")):
        continue
    fp = ROOT / f
    if not fp.is_file() or fp.stat().st_size > 2_000_000:
        continue
    t = fp.read_text(encoding="utf-8", errors="replace")
    for pat in ("src/data", "src\\data"):
        if pat in t:
            hits.append((f, pat))
print(f"  引用 'src/data' 的文件数 = {len(hits)}")
for f, p in hits[:12]:
    print(f"     {f}  含 {p}")
if not hits:
    print("     （无 —— 代码不依赖该目录）")

print()
print("=" * 84)
print("③ 该目录是否被 .gitignore 挡（说明当初就被判定为不该入库）")
print("=" * 84)
rr = subprocess.run(["git", "check-ignore", "-v", "src/data"],
                    cwd=str(ROOT), capture_output=True)
print("  ", rr.stdout.decode("utf-8", "replace").strip() or "(未忽略)")
print(f"  已跟踪文件数 = {sum(1 for t in TRACKED if t.startswith('src/data/'))}")
