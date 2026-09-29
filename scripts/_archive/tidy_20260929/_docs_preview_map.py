# -*- coding: utf-8 -*-
"""预演：不移动文件，先算出映射表并 dry-run 引用修复，确认能覆盖运行时端点。"""
from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

spec = importlib.util.spec_from_file_location("reorg", ROOT / "scripts/_docs_reorg_plan.py")
reorg = importlib.util.module_from_spec(spec)
# 阻止其 main 执行
spec.loader.exec_module(reorg)

MAPPING = reorg.MAPPING
docs = sorted(p for p in (ROOT / "docs").rglob("*") if p.is_file())
docs += sorted(p for p in (ROOT / "PLAN").rglob("*") if p.is_file())
docs += sorted(p for p in (ROOT / "deliverables").rglob("*.md") if p.is_file())
docs += [ROOT / n for n in ("RAG_SYSTEM_DESIGN.md", "GRAPHRAG_ENHANCEMENT_PLAN.md",
                            "ROLEPLAY_PROMPT_OPTIMIZATION_PLAN.md",
                            "VOICE_ITERATION_REPORT.md") if (ROOT / n).is_file()]

plan_map = {}
for p in sorted(set(docs)):
    rel = str(p.relative_to(ROOT)).replace("\\", "/")
    if rel == "docs/README.md":
        continue
    dest = MAPPING.get(rel)
    if dest:
        plan_map[rel] = f"docs/{dest}/{Path(rel).name}"

out = ROOT / "data/compendium_rag/reports/_docs_reorg_map.json"
out.write_text(json.dumps(plan_map, ensure_ascii=False, indent=1), encoding="utf-8")
print(f"[map] {len(plan_map)} 条 -> {out.relative_to(ROOT)}")

# 检查关键引用是否会被覆盖
KEY = ["docs/DESKTOP_PET_DESIGN.md", "docs/GRAPHRAG加强计划书.md",
       "docs/目标①_收口报告", "deliverables/plot-rag-audit-20260912.md",
       "PLAN/README.md", "docs/剧情图谱验收标准.md"]
print("\n关键引用覆盖检查：")
for k in KEY:
    hit = [old for old in plan_map if k in old or old in k]
    print(f"  {k:44} -> {[plan_map[h] for h in hit][:2]}")
