# -*- coding: utf-8 -*-
"""把已标注的预测转成 static 后端可读的映射文件（键 = 查询原文）。

用途：用真实生产代码路径回放「实体扩展」，验证组件端到端可用，
并测出**白名单校验**相对「不做校验」损失多少。
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT / "data" / "knowledge" / "_audit"

cases = {str(c["id"]): c for c in
         json.loads((AUDIT / "rag_testset_300_clean.json").read_text(encoding="utf-8"))}
P = json.loads((AUDIT / "entity_preds_agent.json").read_text(encoding="utf-8"))["preds"]

m: dict[str, list[dict]] = {}
for qid, pr in P.items():
    item = cases.get(qid)
    if not item:
        continue
    picks = pr.get("picks") or []
    if not picks:
        continue
    m[item["q"]] = [{"name": n, "conf": pr.get("conf", "mid")} for n in picks]

dst = AUDIT / "entity_expand_map.json"
dst.write_text(json.dumps({
    "meta": {
        "source": "entity_preds_agent.json（agent 标注的实体识别预测）",
        "keys": "查询原文（未经扩展）",
        "conf": "high/mid/low → 0.9/0.7/0.4",
        "note": "仅供离线回放验证组件；生产需换成 LLM 后端或用预生成映射覆盖真实流量",
    },
    "map": m,
}, ensure_ascii=False, indent=1), encoding="utf-8")

(AUDIT / "_entity_map_build.txt").write_text(
    f"映射条目 {len(m)} 条（对应 {len(P)} 题中的有预测者）\n"
    f"输出 {dst.name}\n", encoding="utf-8")
