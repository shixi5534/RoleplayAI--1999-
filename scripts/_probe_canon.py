# -*- coding: utf-8 -*-
"""探查 huiji_canon.json —— 看能不能给 LLM 提供「角色名单 + 描述」做实体识别。"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CANON = ROOT / "data" / "lore" / "wu_ming_zhe" / "huiji_canon.json"
OUT = ROOT / "data" / "knowledge" / "_audit" / "_canon_probe.txt"
buf: list[str] = []


def p(*a):
    buf.append(" ".join(str(x) for x in a))


if not CANON.is_file():
    OUT.write_text(f"[MISSING] {CANON}", encoding="utf-8")
    raise SystemExit(0)

d = json.loads(CANON.read_text(encoding="utf-8"))
p(f"文件 {CANON.name}｜顶层键 {list(d)}")
p("=" * 78)
for k, v in d.items():
    if isinstance(v, dict):
        p(f"{k}: dict len={len(v)}")
        items = list(v.items())[:3]
        for kk, vv in items:
            p(f"   样例 {kk} -> {str(vv)[:200]}")
    elif isinstance(v, list):
        p(f"{k}: list len={len(v)}  样例 {str(v[:3])[:300]}")
    else:
        p(f"{k}: {str(v)[:120]}")

# 尝试抽出「中文名 -> 描述/别名」的映射
p()
p("=" * 78)
p("候选名单可用性")
p("=" * 78)
for key in ("characters", "npcs", "name_table"):
    obj = d.get(key)
    if isinstance(obj, dict):
        p(f"  {key}: {len(obj)} 条")
        sample = list(obj.items())[:2]
        for kk, vv in sample:
            p(f"    {kk} -> {str(vv)[:220]}")
    elif isinstance(obj, list):
        p(f"  {key}: {len(obj)} 条  样例 {str(obj[:2])[:220]}")

OUT.write_text("\n".join(buf), encoding="utf-8")
