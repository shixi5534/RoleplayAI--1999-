# -*- coding: utf-8 -*-
"""列出各次运行的 elapsed 与 inject，判定批次归属（慢态/快态）。"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REP = ROOT / "data" / "knowledge" / "_audit" / "repeat"
OUT = ROOT / "data" / "knowledge" / "_audit" / "_batch_state.txt"
buf: list[str] = []

files = sorted(p.name for p in REP.glob("*.json"))
buf.append(f"{'文件':<24}{'inject':>9}{'strict':>9}{'elapsed':>10}{'态':>8}")
buf.append("-" * 62)
for n in files:
    try:
        d = json.loads((REP / n).read_text(encoding="utf-8"))
    except Exception:  # noqa: BLE001
        continue
    s = d.get("summary") or {}
    if "inject_pass" not in s:
        continue
    el = float((d.get("meta") or {}).get("elapsed_s") or 0)
    state = "慢态" if el >= 120 else ("快态" if el > 0 else "?")
    buf.append(f"{n:<24}{s.get('inject_pass'):>9.4f}{s.get('strict_pass'):>9.4f}"
               f"{el:>10.1f}{state:>8}")

buf.append("")
buf.append("观察：elapsed ≥120s 的是慢态（inject≈0.62 / 0.69）,")
buf.append("      elapsed <70s 的是快态（inject≈0.55 / 0.62）。两态之间不可直接比。")

OUT.write_text("\n".join(buf), encoding="utf-8")
