# -*- coding: utf-8 -*-
"""构造按置信度分档的查询扩展题集 + 导出负样本供安全标注。

① 阈值变体（用于回答「low 档要不要扩展」）
    expand_all   全部 67 题（已跑，基线对照用）
    expand_hm    只扩展 high+mid（实测这两档识别率 92.9%，low 只有 43.6%）
    expand_high  只扩展 high

② 负样本清单（用于回答「识别器会不会给离题查询编实体」）
    negatives_for_review.txt 供标注者逐题判断「这里有没有可识别的实体」

用法：.venv/Scripts/python.exe -X utf8 scripts/build_expanded_variants.py
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT / "data" / "knowledge" / "_audit"

cases = json.loads((AUDIT / "rag_testset_300_clean.json").read_text(encoding="utf-8"))
rank = json.loads((AUDIT / "positive_rank.json").read_text(encoding="utf-8"))
P = json.loads((AUDIT / "entity_preds_agent.json").read_text(encoding="utf-8"))["preds"]
a_ids = {str(r["id"]) for r in rank if r.get("verdict") == "A_不在候选池"}

VARIANTS = {
    "expand_all": {"high", "mid", "low"},
    "expand_hm": {"high", "mid"},
    "expand_high": {"high"},
}

log: list[str] = []
for name, allow in VARIANTS.items():
    out, touched = [], 0
    for c in cases:
        d = dict(c)
        qid = str(c["id"])
        if qid in a_ids:
            pr = P.get(qid) or {}
            picks = pr.get("picks") or []
            if picks and pr.get("conf") in allow:
                d["q"] = f"{c['q']} {' '.join(picks)}".strip()
                d["_expanded_with"] = picks
                touched += 1
        out.append(d)
    dst = AUDIT / f"rag_testset_300_{name}.json"
    dst.write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    log.append(f"{name:<14}扩展 {touched:>3} 题（允许置信度 {sorted(allow)}）")

# 负样本清单
neg = [c for c in cases if str(c["id"]).startswith("N") or c.get("kind") == "negative"]
if not neg:
    # 负样本可能单独存放，按证据为空来兜底识别
    neg = [c for c in cases if not (c.get("evidence") or [])]
lines = [f"负样本候选 {len(neg)} 题（用于「离题查询是否被编出实体」的安全验证）", ""]
for c in neg:
    lines.append(f"[{c.get('id')}] {c.get('q')}")
    lines.append(f"    类别={((c.get('dims') or {}).get('type') or c.get('category') or '-')}"
                 f"｜evidence={len(c.get('evidence') or [])}")
(AUDIT / "negatives_for_review.txt").write_text("\n".join(lines), encoding="utf-8")

(AUDIT / "_expand_variants.txt").write_text(
    "\n".join(log) + f"\n\n负样本清单写出 {len(neg)} 题 → negatives_for_review.txt\n",
    encoding="utf-8")
