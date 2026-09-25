# -*- coding: utf-8 -*-
"""确认评测报告 items[] 的字段名（eval_repeat 逐题解析要用）。"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT / "data" / "knowledge" / "_audit"
OUT = AUDIT / "_items_probe.txt"
buf: list[str] = []

p = AUDIT / "plot_rag_eval_report_clean.json"
d = json.loads(p.read_text(encoding="utf-8"))
items = d.get("items") or []
buf.append(f"items 数量 {len(items)}")
if items:
    it = items[0]
    buf.append(f"第一条的键（{len(it)} 个）：")
    for k in sorted(it):
        v = it[k]
        buf.append(f"  {k} = {str(v)[:90]}  ({type(v).__name__})")
    # 关键字段可用性
    need = ("id", "inject_pass", "strict_pass")
    for k in need:
        buf.append(f"  需要 {k}: {'✅ 有' if k in it else '❌ 缺'}")
    have = sum(1 for x in items if "inject_pass" in x and "strict_pass" in x)
    buf.append(f"含 inject_pass+strict_pass 的条目：{have}/{len(items)}")
    ids = sum(1 for x in items if str(x.get('id') or '') != '')
    buf.append(f"含非空 id 的条目：{ids}/{len(items)}")
OUT.write_text("\n".join(buf), encoding="utf-8")
