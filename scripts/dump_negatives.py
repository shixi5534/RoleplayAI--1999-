# -*- coding: utf-8 -*-
"""导出 53 道负样本查询，供「识别器会不会给离题查询编实体」的安全标注。"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

import eval_plot_rag as E  # noqa: E402

AUDIT = ROOT / "data" / "knowledge" / "_audit"
cases = list(getattr(E, "NEGATIVE_CASES", []) or [])

lines = [f"负样本 {len(cases)} 题｜用途：验证识别器对**离题查询**是否误产出实体",
         "判据：若识别器给出实体名 ⇒ 生产上会把实体拼进查询 ⇒ 可能诱发注入",
         ""]
payload = []
for i, item in enumerate(cases, 1):
    cat, q = (item if isinstance(item, (list, tuple)) and len(item) == 2
              else ("?", str(item)))
    lines.append(f"{i:>2}. [{cat}] {q}")
    payload.append({"idx": i, "category": cat, "q": q})

lines.append("")
lines.append("已有残留泄漏（基线就存在的，非本次引入）：")
for q in (getattr(E, "KNOWN_RESIDUAL_NEGATIVES", None) or []):
    lines.append(f"  · {q}")

(AUDIT / "negatives_for_review.txt").write_text("\n".join(lines), encoding="utf-8")
(AUDIT / "negatives_list.json").write_text(
    json.dumps(payload, ensure_ascii=False, indent=1), encoding="utf-8")
