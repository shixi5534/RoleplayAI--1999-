# -*- coding: utf-8 -*-
"""探测评测报告的字段名（供消融汇总脚本取值用）。"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT / "data" / "knowledge" / "_audit"
OUT = AUDIT / "_report_keys.txt"
buf: list[str] = []


def walk(o, pre=""):
    if isinstance(o, dict):
        for k, v in o.items():
            if isinstance(v, (dict, list)):
                walk(v, f"{pre}.{k}")
            else:
                buf.append(f"{pre}.{k} = {v}")
    elif isinstance(o, list):
        buf.append(f"{pre}[] len={len(o)}")


for name in ("plot_rag_eval_report_clean.json", "plot_rag_eval_report.json"):
    p = AUDIT / name
    if not p.is_file():
        buf.append(f"--- {name}: MISSING ---")
        continue
    buf.append(f"--- {name} ---")
    try:
        walk(json.loads(p.read_text(encoding="utf-8")))
    except Exception as e:  # noqa: BLE001
        buf.append(f"ERR {e}")

OUT.write_text("\n".join(buf), encoding="utf-8")
