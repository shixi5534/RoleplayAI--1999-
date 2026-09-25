# -*- coding: utf-8 -*-
"""非确定性定位：嵌入向量 / 语义检索 / 最终检索，三个层级逐个测。

跑两次（不同进程）并 diff 输出，就能定位漂移发生在哪一层：
    · 若「嵌入向量」跨进程不同      ⇒ ollama bge-m3 冷/热路径输出不一致（根因）
    · 若嵌入相同而「语义检索」不同   ⇒ 语义索引/numpy 侧有顺序依赖
    · 若语义相同而「最终检索」不同   ⇒ 融合/排序有顺序依赖

用法：.venv/Scripts/python.exe -X utf8 scripts/diag_nondeterminism.py
      （跑两次，每次一个独立进程；输出文件可 diff）
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

import eval_plot_rag as E  # noqa: E402
from roleplay.config import get_settings  # noqa: E402
from roleplay.core.knowledge.factory import build_plot_registry  # noqa: E402

AUDIT = ROOT / "data" / "knowledge" / "_audit"
stamp = time.strftime("%H%M%S")
OUT = AUDIT / f"_nondet_{stamp}.json"
CASES = {str(c["id"]): c for c in
         json.loads((AUDIT / "rag_testset_300_clean.json").read_text(encoding="utf-8"))}
QIDS = ["R003", "R013", "R017", "R021", "R042", "R071", "R075", "R001"]  # 前5为翻转题，R001为对照
REPEAT = 3

s = get_settings()
reg = build_plot_registry(s)
retr = reg.get("wu_ming_zhe")
top = int(getattr(s, "plot_max_chunks", 6))
lf = int(getattr(s, "plot_lexical_fallback", 2))
sem = getattr(retr, "semantic", None)

res: dict = {"stamp": stamp, "pid_time": time.time(),
             "semantic_status": dict(getattr(reg, "semantic_status", {}) or {}),
             "semantic_type": type(sem).__name__,
             "semantic_has_embed_query": bool(sem is not None and hasattr(sem, "embed_query")),
             "semantic_has_search": bool(sem is not None and hasattr(sem, "search")),
             "questions": {}}

for qid in QIDS:
    q = CASES[qid]["q"]
    rec: dict = {}

    # 1) 嵌入向量（同进程 3 次）+ 语义检索（同一向量 3 次）
    if res["semantic_has_embed_query"]:
        vecs = [sem.embed_query(q) for _ in range(REPEAT)]
        rec["vec_first8"] = [round(float(v), 8) for v in list(vecs[0])[:8]]
        rec["vec_repeat_identical"] = all(
            [float(x) for x in v] == [float(x) for x in vecs[0]] for v in vecs[1:])
        rec["vec_norm"] = round(sum(float(v) * float(v) for v in vecs[0]) ** 0.5, 6)
        sems = [sem.search(vecs[0], top) for _ in range(REPEAT)]
        rec["semantic_repeat_identical"] = all(x == sems[0] for x in sems[1:])
        rec["semantic_top5"] = [(h, round(sc, 6)) for h, sc in sems[0][:5]]
    else:
        rec["semantic"] = None

    # 3) 最终检索（同进程 3 次）
    finals = [retr.retrieve(q, top_chunks=top, lexical_fallback=lf) for _ in range(REPEAT)]
    hs = [[E.chunk_hash(c.text) for c in ch] for ch in finals]
    rec["final_repeat_identical"] = all(h == hs[0] for h in hs[1:])
    rec["final_hashes"] = hs[0]
    rec["final_scores"] = [round(float(getattr(c, "score", 0) or 0), 6) for c in finals[0]]

    res["questions"][qid] = rec

OUT.write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding="utf-8")
print(f"[save] {OUT.name}")
