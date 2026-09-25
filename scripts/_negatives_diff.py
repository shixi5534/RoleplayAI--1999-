# -*- coding: utf-8 -*-
"""对比基线与查询扩展版的负样本护栏（扩展是否引入了新的注入泄漏）。"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT / "data" / "knowledge" / "_audit"
OUT = AUDIT / "_negatives_diff.txt"
buf: list[str] = []


def load(name: str) -> dict:
    p = AUDIT / "repeat" / name
    if not p.is_file():
        return {}
    return json.loads(p.read_text(encoding="utf-8"))


b = load("base_1.json").get("negatives") or {}
x = load("expand_1.json").get("negatives") or {}

buf.append("=" * 70)
buf.append("负样本护栏对比（53 题「零注入」红线）")
buf.append("=" * 70)
buf.append(f"{'项':<28}{'基线':>12}{'查询扩展':>12}{'Δ':>10}")
buf.append("-" * 70)
for k, label in (("negative_injection_total", "注入总次数"),
                 ("cases", "负样本题数"), ("elapsed_s", "耗时s")):
    bv, xv = b.get(k), x.get(k)
    if bv is None and xv is None:
        continue
    bv = bv or 0
    xv = xv or 0
    buf.append(f"{label:<28}{bv:>12}{xv:>12}{xv - bv:>+10}")

buf.append("-" * 70)
for k in ("negative_clean", "clear"):
    if k in b or k in x:
        buf.append(f"{k:<28}{str(b.get(k)):>12}{str(x.get(k)):>12}")

buf.append("")
buf.append("分类明细：")
cats = sorted(set((b.get("by_category") or {})) | set((x.get("by_category") or {})))
for c in cats:
    bb = (b.get("by_category") or {}).get(c) or {}
    xx = (x.get("by_category") or {}).get(c) or {}
    buf.append(f"  {c:<14}题数 {bb.get('cases', '-'):>4}→{xx.get('cases', '-'):<4}"
               f"注入 {bb.get('injected', 0):>3}→{xx.get('injected', 0):<3}"
               f"（有注入题数 {bb.get('cases_with_injection', 0)}→"
               f"{xx.get('cases_with_injection', 0)}）")

buf.append("")
buf.append(f"violations 条数：基线 {len(b.get('violations') or [])}｜"
           f"扩展 {len(x.get('violations') or [])}")
buf.append(f"new_leaks 条数：基线 {len(b.get('new_leaks') or [])}｜"
           f"扩展 {len(x.get('new_leaks') or [])}")

OUT.write_text("\n".join(buf), encoding="utf-8")
