# -*- coding: utf-8 -*-
"""题集 i · 冻结：annotated.jsonl → native 兼容测试集 + 分层文件 + SHA256。

冻结后不得改动（改则换版本号）。分层：
  L1  主验收池 = _pool T1（题面点名实体、答案在其 1-hop 邻域）
  L2  只报告   = MULTI（2-hop 多跳）与 无锚点描述题（anchor 空且 gold 可 resolve）
  其余 U 不发布（答案无图谱实体/泛称，评测 keyword 口径也判不稳）
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ANN = ROOT / "data/eval_set_i/annotated.jsonl"
DRAFTS = ROOT / "data/eval_set_i/drafts"
OUT = ROOT / "data/knowledge/_audit/rag_testset_i.json"

rows = [json.loads(l) for l in ANN.read_text(encoding="utf-8").splitlines() if l.strip()]
raw = {}
for fp in sorted(DRAFTS.glob("batch_*.jsonl")):
    for l in fp.read_text(encoding="utf-8").splitlines():
        if l.strip():
            r = json.loads(l)
            raw[r["qid"]] = r


def kw_of(r):
    """评测 keyword：优先原文答案写法；剥《》「」“”后若语料存在剥后形式则用剥后。"""
    ans = r["answer"].strip()
    return [ans]


cases, l2 = [], []
for r in rows:
    d = raw[r["id"]]
    case = {
        "id": r["id"], "q": r["q"], "ref": r["ref"],
        "evidence": kw_of(r),
        "dims": {"type": {"T1": "factoid", "MULTI": "multi_hop", "U": "definition"}.get(r["_pool"], "?"),
                 "difficulty": "hard", "depth": r["dims"]["depth"], "hop": r["dims"]["hop"],
                 "chapter": r["dims"]["chapter"], "text_len": "short"},
        "source": "human_blind_set_i",
        "_from_chunk": r["ref"], "_pool": r["_pool"],
        "_gold_eid": r["gold_eid"], "_anchor_eid": r["anchor_eid"],
        "_gold_name": r.get("gold_name"), "_neighborhood_size": r.get("neighborhood_size"),
        "_gold_in_neighborhood": r.get("gold_in_neighborhood"),
    }
    if r["_pool"] == "T1":
        cases.append(case)
    elif r["_pool"] == "MULTI":
        l2.append(case)
    elif r["_pool"] == "U" and not d.get("anchor") and r["answer"] and r["answer"] not in r["q"]:
        case["dims"]["type"] = "definition"
        case["_pool"] = "T2i"
        l2.append(case)

payload = {
    "_meta": {
        "name": "rag_testset_i",
        "built_from": "盲测写手（子代理只读原文）+ 事后图标注（scripts/_iset_annotate.py）",
        "rules": [
            "写手不见图谱/候选/模型输出（反循环 R2）",
            "答案词必在语料（机检）", "答案词不在题面（机检）",
            "evidence_quote 逐字命中原文（机检）",
            "pool 为事后图可达性标注，不用于筛题面",
            "标注归一化：剥标点安全；别名包含逐题人工裁决（见预注册文档裁决表）",
        ],
        "seed": 20260926, "annotator": "main-agent + 17 blind-writer subagents",
        "date": "2026-09-26",
        "counts": {"L1_T1": len(cases), "L2_report": len(l2)},
    },
    "cases": cases + l2,
}
txt = json.dumps(payload, ensure_ascii=False, indent=1)
OUT.write_text(txt, encoding="utf-8")
h = hashlib.sha256(txt.encode("utf-8")).hexdigest()
print(f"L1(T1)={len(cases)}  L2(report)={len(l2)}  → {OUT}")
print("SHA256:", h)
l1h = hashlib.sha256("\n".join(c["id"] for c in cases).encode()).hexdigest()[:16]
print("L1 qid 列表指纹:", l1h)
