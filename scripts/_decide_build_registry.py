# -*- coding: utf-8 -*-
"""统一 gold 缺陷登记表（**权威 sidecar**）：合并既有 3 道 + 新审计 12 道 = 15 道。

为什么合并：此前有两份 sidecar（`testset_300cn_gold_defects.json` 3 道、
`_85_gold_audit.json` 31 道审计），口径与字段不一，评测脚本难以消费。
本文件是**唯一权威登记表**，供评测脚本单独统计，**绝不修改题集本体**。

判定口径（重要）：
  - 只有 `verdict=defective` 且 `confidence != low` 的题才计入"豁免集"；
  - `borderline=true` 的题单列，**默认不计入豁免**（保守，避免用可疑判定抬分）。

输出：data/knowledge/_audit/gold_defects_registry.json
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT / "data/knowledge/_audit"

# ── 既有 3 道：沿用 testset_300cn_gold_defects.json 的字段与结论 ──
LEGACY = json.loads((AUDIT / "testset_300cn_gold_defects.json")
                    .read_text(encoding="utf-8"))["defects"]

# ── 新审计 12 道：从 _85_gold_audit.json 抽取 defective 且非 low ──
new = json.loads((AUDIT / "_85_gold_audit.json").read_text(encoding="utf-8"))
new_cases = {c["qid"]: c for c in new["cases"]}

LEGACY_IDS = set(LEGACY)
registry: dict[str, dict] = {}

for qid, d in LEGACY.items():
    registry[qid] = {
        "qid": qid,
        "source": "legacy_sidecar_20260928",
        "q": d.get("q"),
        "gold": d.get("gold"),
        "defect_type": d.get("defect_type"),
        "problem": d.get("problem"),
        "evidence_chunk": d.get("evidence_chunk"),
        "corrected_keywords": d.get("corrected_keywords"),
        "confidence": "high",
        "borderline": False,
        "applies_to_testset": ["300cn"],
    }

for qid, c in new_cases.items():
    if c.get("verdict") != "defective" or qid in LEGACY_IDS:
        continue
    registry[qid] = {
        "qid": qid,
        "source": "_85_gold_audit_20260928",
        "q": c.get("q"),
        "gold": c.get("keywords"),
        "defect_type": None,          # 新审计未给统一 type，problem 里已述明
        "problem": c.get("evidence"),
        "evidence_chunk": None,
        "corrected_keywords": c.get("suggested_correct_gold"),
        "confidence": c.get("confidence", "medium"),
        "borderline": bool(c.get("borderline")),
        "applies_to_testset": ["300cn"],
    }

defective = {q: v for q, v in registry.items() if not v["borderline"]}
borderline = {q: v for q, v in registry.items() if v["borderline"]}

doc = {
    "kind": "gold_defects_registry",
    "version": 1,
    "testset": "data/knowledge/_audit/rag_testset_300_cn.json",
    "generated_at": "2026-09-28",
    "supersedes": [
        "data/knowledge/_audit/testset_300cn_gold_defects.json (3 道，已并入)",
        "data/knowledge/_audit/_85_gold_audit.json (31 道审计，defective 已并入)",
    ],
    "policy": (
        "**不修改题集本体**（红线）。本表供评测脚本按 `qid` 单独统计；"
        "引用任何指标时须注明「已剔除 N 道 gold 缺陷题」。"
    ),
    "counting_rule": (
        "两种口径，评测脚本须**同时报告**，不得只报有利者：\n"
        "  · 保守口径（默认）= defective 且 borderline=false，n={}；\n"
        "  · 宽松口径        = 全部 defective，n={}。\n"
        "borderline 的 3 道（{}）判定理由已注明，采信与否应由人工复核决定。"
        .format(len(defective), len(defective) + len(borderline), sorted(borderline))
    ),
    "n_defective": len(defective),
    "n_defective_plus_borderline": len(defective) + len(borderline),
    "n_borderline": len(borderline),
    "exempt_qids_conservative": sorted(defective),
    "exempt_qids_inclusive": sorted(defective) + sorted(borderline),
    "defective_qids": sorted(defective),
    "borderline_qids": sorted(borderline),
    "defects": {q: v for q, v in sorted(registry.items())},
}

out = AUDIT / "gold_defects_registry.json"
out.write_text(json.dumps(doc, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"[ok] -> {out.relative_to(ROOT)}")
print(f"     豁免集 n={len(defective)}: {sorted(defective)}")
print(f"     borderline n={len(borderline)} (不计入): {sorted(borderline)}")
for q in sorted(defective):
    v = defective[q]
    print(f"       {q:6} {v['confidence']:6} {str(v['defect_type'] or '-'):22} {str(v['q'])[:38]}")
