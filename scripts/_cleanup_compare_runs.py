# -*- coding: utf-8 -*-
"""对比两次 pytest 运行，量化"环境噪声"占比 —— 决定能否据测试结果删文件。"""
from __future__ import annotations

import re
from pathlib import Path

R = Path("data/compendium_rag/reports")
for f in ("_cleanup_pytest.log", "_cleanup_pytest2.log"):
    p = R / f
    if not p.exists():
        print(f"{f}: 不存在")
        continue
    t = p.read_text(encoding="utf-8", errors="replace")
    summ = [l for l in t.splitlines() if re.search(r"\d+ (passed|failed)", l)]
    n_perm = t.count("PermissionError")
    n_err = len([l for l in t.splitlines() if l.startswith("ERROR ")])
    n_fail = len([l for l in t.splitlines() if l.startswith("FAILED ")])
    print(f"--- {f} ---")
    print(f"  总结行: {summ[-1].strip() if summ else '(无)'}")
    print(f"  ERROR 行 = {n_err}   FAILED 行 = {n_fail}   PermissionError 出现 = {n_perm}")
    if n_err:
        print(f"  ⇒ ERROR 中疑似环境（PermissionError）占比 = "
              f"{min(100, round(100 * min(n_perm, n_err) / n_err))}%")
    print()
