# -*- coding: utf-8 -*-
"""构造「查询扩展版」题集：只给 A 类题追加预测实体，其余题原样不动。

为什么要做成独立题集
    这样能直接复用官方评测脚本 `eval_plot_rag.py --testset` 与
    `eval_repeat.py --mcnemar`，不用自造判定口径（历史教训：自造口径的结论全部作废）。
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT / "data" / "knowledge" / "_audit"

src = AUDIT / "rag_testset_300_clean.json"
rank = AUDIT / "positive_rank.json"
preds = AUDIT / "entity_preds_agent.json"

cases = json.loads(src.read_text(encoding="utf-8"))
a_ids = {str(r["id"]) for r in json.loads(rank.read_text(encoding="utf-8"))
         if r.get("verdict") == "A_不在候选池"}
P = json.loads(preds.read_text(encoding="utf-8"))["preds"]

out = []
touched = 0
for c in cases:
    qid = str(c["id"])
    d = dict(c)
    if qid in a_ids:
        picks = (P.get(qid) or {}).get("picks") or []
        if picks:
            d["q"] = f"{c['q']} {' '.join(picks)}".strip()
            d["_expanded_with"] = picks      # 留痕，便于事后核对
            touched += 1
    out.append(d)

dst = AUDIT / "rag_testset_300_expanded.json"
dst.write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")

(AUDIT / "_expanded_build.txt").write_text(
    f"源 {src.name}｜输出 {dst.name}\n"
    f"A 类 {len(a_ids)} 题，实际追加 {touched} 题\n"
    f"其余 {len(out) - touched} 题 query 逐字未改\n",
    encoding="utf-8")
