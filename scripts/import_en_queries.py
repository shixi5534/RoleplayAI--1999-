# -*- coding: utf-8 -*-
"""把工作区的 3 批英文检索式导入项目 _audit（避免命令行出现中文路径）。"""
from __future__ import annotations

import json
from pathlib import Path

SRC = Path(r"C:\Users\Lenovo\WorkBuddy\2026-09-17-13-00-26")
DST = Path(__file__).resolve().parents[1] / "data" / "knowledge" / "_audit" / "en_queries_300_20260917.json"

out: dict[str, str] = {}
for i in (1, 2, 3):
    d = json.loads((SRC / f"_en_queries_{i}.json").read_text(encoding="utf-8"))
    for k, v in d.items():
        if not k.startswith("_"):
            out[k] = v
DST.write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
print(f"imported {len(out)} -> {DST.name}")
