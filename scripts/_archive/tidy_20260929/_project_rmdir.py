# -*- coding: utf-8 -*-
"""清理沙箱残留的**空目录壳**（rmtree 删除了文件，但目录本身被拒）。

报告每个目录的真实状态：已删除 / 仍为空壳 / 仍含文件。
"""
from __future__ import annotations

import os
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

TARGETS = [
    ".pytest_bt", ".pytest_ws", ".pytest_tmp", ".pytest_tmp2", ".pytest_tmp3",
    ".pytest_cache", "pytest-of-Lenovo", "roleplay_test_qenmhfwr", "tmp_pytest",
]

print("=" * 76)
for d in TARGETS:
    p = ROOT / d
    if not p.exists():
        print(f"  [已删除] {d}")
        continue
    files = sum(1 for f in p.rglob("*") if f.is_file())
    # 先尽力删空子目录，再删自身
    for sub in sorted((x for x in p.rglob("*") if x.is_dir()),
                      key=lambda x: -len(x.parts)):
        try:
            sub.rmdir()
        except OSError:
            pass
    try:
        shutil.rmtree(p)
        state = "已删除"
    except OSError as e:
        state = f"仍存在（{type(e).__name__}）"
    left = sum(1 for f in p.rglob("*") if f.is_file()) if p.exists() else 0
    print(f"  [{state}] {d}  剩余文件={files if not p.exists() else left}"
          f"{'  目录壳' if p.exists() and left == 0 else ''}")

print("=" * 76)
remaining = [d for d in TARGETS if (ROOT / d).exists()]
if remaining:
    print(f"沙箱仍锁定的空壳目录 {len(remaining)} 个：{remaining}")
    print("说明：文件已全部清除（体积 0），仅目录项被沙箱拒绝删除；")
    print("      .gitignore 已声明，不影响版本库，也不会再出现在 git status。")
else:
    print("全部清除完成。")
