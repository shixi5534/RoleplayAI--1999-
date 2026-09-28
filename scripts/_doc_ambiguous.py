# -*- coding: utf-8 -*-
"""打印**争议文件**开头若干行，供人工判定归属（只读）。"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
C = json.loads((ROOT / "data/compendium_rag/reports/_doc_classification.json")
               .read_text(encoding="utf-8"))

# 只挑：多项目并列（tie）或含 P1+P2 混合的
AMB = [r for r in C if "+" in r["cat"] or
       (r["cat"] == "P2_plot" and r["scores"].get("P1_compendium"))]

print(f"争议文件 {len(AMB)} 个\n")
for r in AMB:
    p = ROOT / r["path"]
    lines = [ln.strip() for ln in p.read_text(encoding="utf-8", errors="replace").splitlines()
             if ln.strip()][:7]
    print("=" * 110)
    print(f"{r['path']}   {r['scores']}")
    for ln in lines:
        print(f"    {ln[:150]}")
    print()
