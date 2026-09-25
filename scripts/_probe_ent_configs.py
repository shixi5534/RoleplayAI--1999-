# -*- coding: utf-8 -*-
"""读三次运行报告里的 meta.config 快照，确认各自实际用的实体扩展配置。"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REP = ROOT / "data" / "knowledge" / "_audit" / "repeat"
OUT = ROOT / "data" / "knowledge" / "_audit" / "_ent_configs.txt"
KEYS = ("plot_entity_expand_enabled", "plot_entity_expand_backend",
        "plot_entity_expand_static_path", "plot_entity_expand_top",
        "plot_entity_expand_whitelist", "plot_entity_expand_min_conf")
buf: list[str] = []

for name in ("base_1.json", "expand_1.json", "entoff_1.json",
             "enton_1.json", "entnolist_1.json"):
    p = REP / name
    if not p.is_file():
        buf.append(f"--- {name}: MISSING ---")
        continue
    d = json.loads(p.read_text(encoding="utf-8"))
    cfg = (d.get("meta") or {}).get("config") or {}
    s = (d.get("summary") or {})
    buf.append(f"--- {name} ---")
    buf.append(f"  inject={s.get('inject_pass')} strict={s.get('strict_pass')} "
               f"recall={s.get('recall')}")
    for k in KEYS:
        buf.append(f"  {k} = {cfg.get(k, '<无此键>')!r}")
    argv = (d.get("meta") or {}).get("argv")
    buf.append(f"  argv={argv}")
    buf.append("")

OUT.write_text("\n".join(buf), encoding="utf-8")
