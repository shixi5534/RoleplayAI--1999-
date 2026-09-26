# -*- coding: utf-8 -*-
"""题集 i · 阶段 2：盲识别视图切片器（零网关、零模型、只读候选文件）。

把 entity_candidates_i.json 切成写手无关的识别批次：每行仅
  {qid, query, candidates}   —— 绝不带 seeds/gold/关系/度数（计划书 §8 反循环）。
按「名字总数预算」分批，保证单个子代理上下文可控。

产物：data/eval_set_i/id_batches/batch_XX.jsonl
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CANDS = ROOT / "data" / "compendium_rag" / "entity_candidates_i.json"
OUT_DIR = ROOT / "data" / "eval_set_i" / "id_batches"
NAME_BUDGET = 2600  # 每批候选名总数上限
MAX_Q = 24          # 每批题目数上限


def main() -> int:
    d = json.loads(CANDS.read_text(encoding="utf-8"))
    qids = sorted(d)  # 稳定顺序
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    # 清旧批
    for old in OUT_DIR.glob("batch_*.jsonl"):
        old.unlink()

    batches: list[list[dict]] = []
    cur: list[dict] = []
    cur_names = 0
    for qid in qids:
        rec = {"qid": qid, "query": d[qid]["query"],
               "candidates": d[qid]["candidates"]}
        n = len(rec["candidates"])
        if cur and (cur_names + n > NAME_BUDGET or len(cur) >= MAX_Q):
            batches.append(cur)
            cur, cur_names = [], 0
        cur.append(rec)
        cur_names += n
    if cur:
        batches.append(cur)

    for i, b in enumerate(batches, 1):
        (OUT_DIR / f"batch_{i:02d}.jsonl").write_text(
            "\n".join(json.dumps(r, ensure_ascii=False) for r in b),
            encoding="utf-8")
    total_q = sum(len(b) for b in batches)
    print(f"批次数={len(batches)}  题数={total_q}  (应={len(qids)})")
    for i, b in enumerate(batches, 1):
        print(f"  batch_{i:02d}: {len(b)} 题, {sum(len(x['candidates']) for x in b)} 名")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
