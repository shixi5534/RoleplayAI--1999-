# -*- coding: utf-8 -*-
"""目标①：14 道池内 miss 的可行救治路径分类。

对每题判定：
  A) 语料层只有 1 块含答案（且是否与任何种子实体同块？）
  B) gold 块是否与查询中出现的**任何**实体/别名同块（即"如果链接对了就能到"）
  C) gold 块是否与其他题的可命中块同篇（篇级线索可用）
据此给出 P3（查询侧供给）优先级。
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
    chunks = {c.chunk_id: c for c in kb.chunks}
    blob = {cid: f"{c.text}\n{c.chapter_title}\n{c.scene_title}\n{c.part_title}"
            for cid, c in chunks.items()}

    ts = json.loads((ROOT / "data/knowledge/_audit/rag_testset_300_cn.json").read_text(encoding="utf-8"))
    by = {str(c["id"]): c for c in ts["cases"]}

    print(f"{'qid':6}{'gold块':>6}  {'种子':<34}gold块同篇?  性质")
    print("-" * 100)
    rows = []
    for q in MISS:
        c = by[q]
        kws = kws_of(c)
        gold = [cid for cid, t in blob.items() if any(k in t for k in kws)]
        seeds = r.link(c["q"], top_k=6)
        seeds = [x for x in seeds if x.score >= 0.34] or seeds[:2]
        g_chapters = {chunks[cid].chapter_title for cid in gold}
        seed_chapters = {chunks[cid].chapter_title
                         for x in seeds for cid in kb.graph.entities[x.eid].chunk_ids}
        overlap = bool(g_chapters & seed_chapters)
        # 性质判定
        if not seeds:
            nature = "零种子（需查询侧补充实体供给）"
        elif not overlap:
            nature = "种子与gold不同篇（需桥接/查询改写）"
        else:
            nature = "同篇但通道未带回（候选生成缺口）"
        rows.append((q, len(gold), [x.eid for x in seeds], overlap, nature))
        sd = ",".join(x.eid for x in seeds)[:30] or "(空)"
        print(f"{q:6}{len(gold):>6}  {sd:<34}{str(overlap):<11}{nature}")

    print()
    from collections import Counter
    print("性质分布:", dict(Counter(x[4] for x in rows)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
