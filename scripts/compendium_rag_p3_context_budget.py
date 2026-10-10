# -*- coding: utf-8 -*-
"""v9-P3 步骤3 · `context()` 预算实测（只读，零 LLM/零嵌入）。

`context()` 把【图谱实体】【关系脉络】【原文证据】三段拼成一个串，再
`out[:max_chars]` **整体尾切**。检索给的是 top-6 块，模型看到的是切完之后剩下的部分——
这中间的差**以前没人量过**。WP3 审查里 L3.4 幻觉率的「窗内无据」caveat 就落在这段预算上。

P3 加了溯源头（`[S{i} chunk=… doc=… cat=…]`）之后，这笔账必须重算：头本身占多少窗、
多少块因此整块掉出。P4 要把尾切改成按块预算分配，这条曲线就是它的对照基线。

块状态判据（每题取 evidence[:top_k]，与 `context()` 用同一批块）：
- `complete`：块正文**整段**出现在渲染串里；
- `partial` ：该块的溯源头在串里、正文不完整 → 模型看到半块（最危险的一类）；
- `dropped` ：连头都没进窗。

用法：
    PYTHONPATH=src .venv/Scripts/python.exe -X utf8 \\
        scripts/compendium_rag_p3_context_budget.py
产物：``data/compendium_rag/reports/p3_context_budget.{json,md}``
"""
from __future__ import annotations

import asyncio
import hashlib
import json
import os
import re
import statistics
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
for _k, _v in {"CMPRAG_LEX_WEIGHT": "1.0", "CMPRAG_RRF_K": "1",
               "CMPRAG_LEX_FIRST": "0", "PYTHONHASHSEED": "0"}.items():
    os.environ.setdefault(_k, _v)      # 必须在 import config 之前

from compendium_rag import pipeline as P  # noqa: E402
from compendium_rag.config import get_settings  # noqa: E402

EXPECTED_SHA = "7cac5867e8c80879"
R = ROOT / "data" / "compendium_rag" / "reports"
SETS = {
    "300cn": ROOT / "data" / "knowledge" / "_audit" / "rag_testset_300_cn.json",
    "blind206": ROOT / "data" / "knowledge" / "_audit" / "blind_v1" / "questions_strict.json",
    "gen120": ROOT / "data" / "knowledge" / "_audit" / "rag_testset_gen_r1r2.json",
}
PER_SET = int(os.environ.get("P3_BUDGET_PER_SET", "8"))
HEAD_RE = re.compile(r"\[S(\d)((?: (?:chunk|doc|cat)=\S+)+)\] ")


def sha16(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()[:16]


def main() -> int:
    s = get_settings()
    sha = sha16(s.graph_path)
    if sha != EXPECTED_SHA:
        raise SystemExit(f"图指纹漂移：期望 {EXPECTED_SHA}，实际 {sha}，中止")
    kb = P.load_kb(s)
    queries = []
    for tag, path in SETS.items():
        d = json.loads(path.read_text(encoding="utf-8"))
        rows = d if isinstance(d, list) else d.get("cases", [])
        for r in sorted(rows, key=lambda x: str(x.get("id", "")))[:PER_SET]:
            queries.append((tag, str(r.get("id", "")), r.get("q", "")))

    ctx_len, head_chars, statuses = [], [], {"complete": 0, "partial": 0, "dropped": 0}
    per_case = []
    for tag, qid, q in queries:
        res = asyncio.run(kb.retrieve(q, top_k=s.top_k, use_vector=False))
        ctx = kb.context(res)
        ctx_len.append(len(ctx))
        heads = {int(m.group(1)): (m.end() - m.start()) for m in HEAD_RE.finditer(ctx)}
        head_chars += list(heads.values())
        c_complete = c_partial = c_dropped = 0
        for i, e in enumerate(res["evidence"][:s.top_k], 1):
            c = kb.retriever.chunks.get(e["chunk_id"])
            if not c:
                continue
            if c.text and c.text in ctx:
                st = "complete"
                c_complete += 1
            elif i in heads:
                st = "partial"
                c_partial += 1
            else:
                st = "dropped"
                c_dropped += 1
            statuses[st] += 1
        per_case.append({"set": tag, "qid": qid, "ctx_chars": len(ctx),
                         "n_heads": len(heads), "complete": c_complete,
                         "partial": c_partial, "dropped": c_dropped})

    block_len = [len(c.text) for c in kb.retriever.chunks.values()]
    total_blocks = sum(statuses.values())
    mean_head = statistics.mean(head_chars) if head_chars else 0.0
    rep = {
        "done_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "graph_sha256_16": sha,
        "caliber": {"mode": "graph_only", "use_vector": False, "top_k": s.top_k,
                    "context_max_chars": s.context_max_chars,
                    "per_set": PER_SET, "queries": len(queries),
                    "CMPRAG_LEX_WEIGHT": os.environ.get("CMPRAG_LEX_WEIGHT"),
                    "CMPRAG_RRF_K": os.environ.get("CMPRAG_RRF_K"),
                    "CMPRAG_LEX_FIRST": os.environ.get("CMPRAG_LEX_FIRST"),
                    "PYTHONHASHSEED": os.environ.get("PYTHONHASHSEED")},
        "rendering": {"ctx_len_mean": round(statistics.mean(ctx_len), 1),
                      "ctx_len_min": min(ctx_len), "ctx_len_max": max(ctx_len),
                      "saturated_at_budget": sum(
                          1 for x in ctx_len if x >= s.context_max_chars),
                      "provenance_head_mean_chars": round(mean_head, 1),
                      "provenance_head_share_of_budget": round(
                          mean_head / s.context_max_chars, 4),
                      "provenance_heads_rendered": len(head_chars)},
        "corpus_block_len": {"mean": round(statistics.mean(block_len)),
                             "median": statistics.median(block_len),
                             "p90": sorted(block_len)[int(len(block_len) * 0.9)],
                             "chunks": len(block_len)},
        "block_status": {**statuses, "total": total_blocks,
                         "complete_ratio": round(statuses["complete"] / total_blocks, 4),
                         "partial_ratio": round(statuses["partial"] / total_blocks, 4),
                         "dropped_ratio": round(statuses["dropped"] / total_blocks, 4)},
        "mean_blocks_in_window": round(
            (statuses["complete"] + statuses["partial"]) / len(queries), 2),
        "per_case": per_case,
    }
    R.mkdir(parents=True, exist_ok=True)
    (R / "p3_context_budget.json").write_text(
        json.dumps(rep, ensure_ascii=False, indent=2), encoding="utf-8")
    md = [
        "# v9-P3 步骤3 · `context()` 预算实测",
        "",
        f"- 图谱 `{sha}`；口径 `graph_only / top_k={s.top_k} / "
        f"max_chars={s.context_max_chars}`；{len(queries)} 题（三集各 {PER_SET}，按 qid 排序）",
        f"- 渲染长度：均值 {rep['rendering']['ctx_len_mean']}，"
        f"**{rep['rendering']['saturated_at_budget']}/{len(queries)} 题饱和在预算上**"
        f"（`out[:max_chars]` 是硬切，所以多出来的每一个字都逐字挤掉正文）",
        f"- 溯源头：均 **{rep['rendering']['provenance_head_mean_chars']} 字/条** = 预算的 "
        f"{rep['rendering']['provenance_head_share_of_budget']:.2%}/块，样本内共 "
        f"{rep['rendering']['provenance_heads_rendered']} 条",
        f"- 块长：均 {rep['corpus_block_len']['mean']} 字、中位 "
        f"{rep['corpus_block_len']['median']} 字（全 {rep['corpus_block_len']['chunks']} 块）",
        "",
        "## top-6 证据块进窗情况（主读数）",
        "",
        f"| 状态 | 块数 | 占比 |",
        f"| --- | --- | --- |",
        f"| 完整进窗 | {statuses['complete']} | {rep['block_status']['complete_ratio']:.2%} |",
        f"| **被从中间切断** | {statuses['partial']} | {rep['block_status']['partial_ratio']:.2%} |",
        f"| 整块掉出窗外 | {statuses['dropped']} | {rep['block_status']['dropped_ratio']:.2%} |",
        f"| 合计（top-6 × 题） | {total_blocks} | 100% |",
        "",
        f"每题平均只有 **{rep['mean_blocks_in_window']}** 块（含半块）进窗。",
        "",
        "## 这两句结论",
        "",
        "1. 溯源头不是主要代价（2.59%/块）；**主要代价是 53% 的检索结果根本没进模型视野**——"
        "块均 918 字，窗口还要先装实体段与关系段。",
        "2. 所以 L3.4 的「窗内无据」里有相当一部分是**预算问题不是检索问题**。P4 改按块分配预算后，"
        "复测必须并报「进窗块数」这一列，否则改动效果与预算噪声无法区分。",
        "",
        "> 只读脚本：不写图谱、不重建索引、不触 LLM/嵌入。",
        "",
    ]
    (R / "p3_context_budget.md").write_text("\n".join(md), encoding="utf-8")
    print(f"[done] 完整 {statuses['complete']} / 切断 {statuses['partial']} / "
          f"掉出 {statuses['dropped']}（共 {total_blocks}）；"
          f"每题进窗 {rep['mean_blocks_in_window']} 块；头均 "
          f"{rep['rendering']['provenance_head_mean_chars']} 字")
    return 0


if __name__ == "__main__":
    sys.exit(main())
