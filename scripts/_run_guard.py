# -*- coding: utf-8 -*-
"""兜底启动器：捕获**模块级**异常（含 import 失败）并落盘。

为什么需要：PowerShell 的 stdout/stderr 重定向在本机会写成 UTF-16，
读出来是二进制；只靠退出码又看不到任何信息。
本启动器用 runpy 加载目标脚本，把完整 traceback 写进 UTF-8 文件。

用法：.venv/Scripts/python.exe -X utf8 scripts/_run_guard.py scripts/diag_b4_prf.py
"""
from __future__ import annotations

import runpy
import sys
import traceback
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
target = sys.argv[1] if len(sys.argv) > 1 else ""
log = ROOT / "data" / "knowledge" / "_audit" / "_guard_traceback.txt"
try:
    runpy.run_path(str(ROOT / target), run_name="__main__")
except SystemExit:
    raise
except BaseException:  # noqa: BLE001
    log.write_text(f"target={target}\n\n" + traceback.format_exc(), encoding="utf-8")
    raise
