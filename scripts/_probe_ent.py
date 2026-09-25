# -*- coding: utf-8 -*-
"""探针：在当前环境变量下，实体扩展器实际配置成什么、有没有真的扩展。"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

from roleplay.config import get_settings  # noqa: E402
from roleplay.core.knowledge.factory import build_plot_registry  # noqa: E402

AUDIT = ROOT / "data" / "knowledge" / "_audit"
OUT = AUDIT / "_ent_probe.txt"
buf: list[str] = []

s = get_settings()
buf.append("配置：")
for k in ("plot_entity_expand_enabled", "plot_entity_expand_backend",
          "plot_entity_expand_static_path", "plot_entity_expand_top",
          "plot_entity_expand_min_conf", "plot_entity_expand_max_append",
          "plot_entity_expand_whitelist"):
    buf.append(f"  {k} = {getattr(s, k, '<缺失>')!r}")

retr = build_plot_registry(s).get("wu_ming_zhe")
exp = getattr(retr, "entity_expander", None)
buf.append(f"\n检索器持有 expander：{type(exp).__name__ if exp else None}")
if exp is not None:
    buf.append(f"  enforce_whitelist = {getattr(exp, 'enforce_whitelist', '?')}")
    buf.append(f"  names 条数 = {len(getattr(exp, 'names', []) or [])}")
    buf.append(f"  resolver = {exp.resolver}")
    nm = getattr(exp, "_name_map", None)
    buf.append(f"  白名单映射条数 = {len(nm) if nm else 0}")
    buf.append(f"  identifier = {type(exp.identifier).__name__}"
               f"（内部映射条数 "
               f"{len(getattr(exp.identifier, '_map', {}) or {})}）")

rank = json.loads((AUDIT / "positive_rank.json").read_text(encoding="utf-8"))
a_ids = [str(r["id"]) for r in rank if r.get("verdict") == "A_不在候选池"][:5]
cases = {str(c["id"]): c for c in
         json.loads((AUDIT / "rag_testset_300_clean.json").read_text(encoding="utf-8"))}

buf.append("\n逐题实测（前 5 道 A 类）：")
before = dict(getattr(exp, "stats", {}) or {})
for qid in a_ids:
    q = cases[qid]["q"]
    out = exp.expand(q)
    changed = "✅ 扩展" if out != q else "— 未扩展"
    buf.append(f"  [{qid}] {changed}")
    buf.append(f"      原：{q}")
    buf.append(f"      后：{out}")
after = dict(getattr(exp, "stats", {}) or {})
buf.append(f"\nstats 增量：")
for k in sorted(set(before) | set(after)):
    buf.append(f"  {k}: {after.get(k, 0) - before.get(k, 0)}")
buf.append(f"stats 全量：{after}")

# 再跑一遍 300 题，看整体扩展了多少题
n_changed = 0
for c in json.loads((AUDIT / "rag_testset_300_clean.json").read_text(encoding="utf-8")):
    if exp.expand(c["q"]) != c["q"]:
        n_changed += 1
buf.append(f"\n全量 300 题中被扩展的：{n_changed} 题")
buf.append(f"最终 stats：{exp.stats}")

OUT.write_text("\n".join(buf), encoding="utf-8")
