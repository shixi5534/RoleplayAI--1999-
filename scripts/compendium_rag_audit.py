# -*- coding: utf-8 -*-
"""对**已完成的抽取缓存**做全量质量审计。

价值：在建图跑完之前就能发现系统性问题（噪声比例、空结果率、类型分布、
关系多样性），而不是等两小时才发现要重跑。
"""
from __future__ import annotations

import collections
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from compendium_rag.config import get_settings  # noqa: E402
from compendium_rag.extract import (ExtractionCache, cache_key, normalize,  # noqa: E402
                                    PROMPT_VERSION)
from compendium_rag import pipeline as P  # noqa: E402


def main() -> int:
    s = get_settings()
    chunks = P.load_chunks(s)
    by_id = {c.chunk_id: c for c in chunks}
    cache = ExtractionCache(s.cache_dir)

    ents = collections.Counter()
    rels = collections.Counter()
    types = collections.Counter()
    per_chunk_e = []
    per_chunk_r = []
    empty = 0
    done = 0
    noise_examples = []

    for c in chunks:
        raw = cache.get_raw(cache_key(c, s.llm_model, PROMPT_VERSION))
        if raw is None:
            continue
        done += 1
        ex = normalize(c, raw)
        ne, nr = len(ex.entities), len(ex.relations)
        per_chunk_e.append(ne)
        per_chunk_r.append(nr)
        if ne == 0 and nr == 0:
            empty += 1
        for e in ex.entities:
            ents[e.name] += 1
            types[e.type] += 1
        for r in ex.relations:
            rels[r.relation] += 1

    print(f"已完成抽取：{done}/{len(chunks)} 块 "
          f"({done / max(1, len(chunks)) * 100:.1f}%)")
    if not done:
        print("缓存为空")
        return 0

    def pct(xs, p):
        if not xs:
            return 0
        xs = sorted(xs)
        return xs[min(len(xs) - 1, int(len(xs) * p))]

    print(f"\n实体/块：mean={sum(per_chunk_e)/done:.2f} "
          f"p50={pct(per_chunk_e, .5)} p90={pct(per_chunk_e, .9)} "
          f"max={max(per_chunk_e)}")
    print(f"关系/块：mean={sum(per_chunk_r)/done:.2f} "
          f"p50={pct(per_chunk_r, .5)} p90={pct(per_chunk_r, .9)} "
          f"max={max(per_chunk_r)}")
    print(f"空结果块：{empty} ({empty/done*100:.1f}%)")
    print(f"去重后实体名：{len(ents)}")
    print(f"关系类型数：{len(rels)}")

    print("\n=== 实体类型分布 ===")
    for t, n in types.most_common():
        print(f"  {t:6} {n:>6}  ({n/sum(types.values())*100:.1f}%)")

    print("\n=== 高频实体 TOP 30（提取精度抽检）===")
    for n, k in ents.most_common(30):
        print(f"  {k:>5}  {n}")

    print("\n=== 关系类型 TOP 30 ===")
    for r, k in rels.most_common(30):
        print(f"  {k:>5}  {r}")

    # 单次出现的实体（长尾，可能含噪声）
    once = [n for n, k in ents.items() if k == 1]
    print(f"\n只出现 1 次的实体：{len(once)} "
          f"({len(once)/max(1,len(ents))*100:.1f}%)")
    print("  样例：", "、".join(sorted(once, key=len, reverse=True)[:25]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
