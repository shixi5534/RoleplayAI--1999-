# -*- coding: utf-8 -*-
"""目标① 决定性测试：**向量（语义）通道**放宽能否带回 14 道 miss？

理由：lex 通道虽含 gold 但排名 8–1214（字面重叠弱），说明这些题的题干
**描述了答案却未点名**（如 R005 问"载具"、gold 是"号船"；R297 问"多少岁"、
gold 是"12岁/twelve"）—— 属**语义鸿沟**，只有嵌入/交叉编码器能桥。

测试：
  1. 每题 gold 在当前 vector_top=30 的向量通道中的排名；
  2. 把 vector_top 放宽到 100 / 300，gold 是否进入，以及全量 hit@6 是否提升；
  3. 给出 oracle 上限（若完全按 gold 排序能到多少）。
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from compendium_rag import pipeline as P                      # noqa: E402
from compendium_rag.config import get_settings                # noqa: E402

MISS = ["R001", "R005", "R012", "R094", "R127", "R170", "R171",
        "R180", "R244", "R248", "R273", "R292", "R297", "R298"]


def kws_of(c):
    out = []
    for g in (c.get("evidence") or []):
        items = g if isinstance(g, (list, tuple)) else [g]
        out.extend(str(x) for x in items if x)
    return [k.strip() for k in out if k.strip()]


def main() -> int:
    s = get_settings()
    kb = P.load_kb(s)
    r = kb.retriever
    if r.chunk_index is None:
        print("[FAIL] 无 chunk_index，向量通道不可用")
        return 1
    chunks = {c.chunk_id: c for c in kb.chunks}
    blob = {cid: f"{c.text}\n{c.chapter_title}\n{c.scene_title}\n{c.part_title}"
            for cid, c in chunks.items()}

    cd = json.loads((ROOT / "data/compendium_rag/reports/rank_collect_v6c300_top30.json")
                    .read_text(encoding="utf-8"))
    qvecs = cd.get("qvecs") or {}
    ts = json.loads((ROOT / "data/knowledge/_audit/rag_testset_300_cn.json").read_text(encoding="utf-8"))
    by = {str(c["id"]): c for c in ts["cases"]}

    print(f"{'qid':6}{'gold':>5}{'vec排名(全库)':>14}  说明")
    print("-" * 70)
    in_top100 = 0
    for q in MISS:
        c = by[q]
        qv = qvecs.get(q)
        if qv is None:
            print(f"{q:6}{'?':>5}{'(无qvec)':>14}")
            continue
        kws = kws_of(c)
        gold = {cid for cid, t in blob.items() if any(k in t for k in kws)}
        # 全库向量排序（用 chunk_index 的全量矩阵）
        hits = r.chunk_index.search(qv, 10 ** 6)
        rank = None
        for i, (cid, _sc) in enumerate(hits, 1):
            if cid in gold:
                rank = i
                break
        if rank and rank <= 100:
            in_top100 += 1
        note = "**语义可达**" if rank and rank <= 100 else ("深排名" if rank else "全库无 gold")
        print(f"{q:6}{len(gold):>5}{str(rank):>14}  {note}")

    print(f"\ngold 进入向量 top-100 的题数: {in_top100}/14")
    print("=> 若该数很小，说明**语义通道也无法桥接**，这些题需要查询侧供给（P3）")
    print("   或补充抽提，或更强的交叉编码器重排（P4）配合更宽池。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
