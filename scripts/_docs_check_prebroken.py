# -*- coding: utf-8 -*-
"""确认「移动前既存断链」在备份标签里确实也是断的（避免把本次遗留误报为历史问题）。"""
from __future__ import annotations

import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = "backup-pre-docs-reorg"

CANDIDATES = [
    ("docs/compendium强模型实体识别_计划书.md", "docs/compendium召回率_终结报告.md"),
    ("docs/核验报告Phase2_20260927_插入序根因闭合与tiebreak修复.md", "docs/核验报告Phase2_...md"),
    ("PLAN/后端计划.md", "docs/参数消融报告.md"),
    ("PLAN/后端计划.md", "docs/题集口径复核.md"),
    ("docs/GRAPHRAG加强计划书.md", "deliverables/graphrag-ab-report.md"),
    ("docs/DESKTOP_PET_DESIGN.md", "docs/PACKAGING.md"),
]

print("核对：这些引用在**移动前**（备份标签）是否也指向不存在的文件\n")
allfiles = subprocess.run(["git", "ls-tree", "-r", "-z", "--name-only", BASE],
                          cwd=str(ROOT), capture_output=True).stdout.decode(
                              "utf-8", "replace").split("\0")
allset = {f for f in allfiles if f}
for src, ref in CANDIDATES:
    r = subprocess.run(["git", "show", f"{BASE}:{src}"],
                       cwd=str(ROOT), capture_output=True)
    if r.returncode != 0:
        print(f"  ? 源文件不在备份中: {src}")
        continue
    content = r.stdout.decode("utf-8", "replace")
    present = ref in content
    target_exists = ref in allset
    print(f"  {src}")
    print(f"      引用 {ref}")
    print(f"      移动前存在于该文: {present}   目标文件移动前已存在: {target_exists}")
    print(f"      -> {'原有断链（非本次引入）' if present and not target_exists else '需复查'}")
    print()
