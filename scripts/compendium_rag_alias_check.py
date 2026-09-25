# -*- coding: utf-8 -*-
"""检查实体归并效果：同一实体的不同写法是否被合并。

重点看审计里发现的候选问题：
- `重塑` / `重塑之手`（组织简称 vs 全称）
- `Z` / `Z女士`（西文单字名 + 后缀）
- `司辰` / `维尔汀`（称号 vs 本名，是否被模型声明为别名）
"""
from __future__ import annotations

import collections
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from compendium_rag import pipeline as P  # noqa: E402
from compendium_rag.config import get_settings  # noqa: E402
from compendium_rag.extract import (PROMPT_VERSION, ExtractionCache,  # noqa: E402
                                    cache_key)
from compendium_rag.graph_store import GraphStore  # noqa: E402

PAIRS = [("重塑", "重塑之手"), ("Z", "Z女士"), ("司辰", "维尔汀"),
         ("基金会", "圣洛夫基金会"), ("槲寄生", "槲寄生小姐")]


def main() -> int:
    s = get_settings()
    chunks = P.load_chunks(s)
    cache = ExtractionCache(s.cache_dir)

    results = {}
    alias_decls: dict[str, set[str]] = collections.defaultdict(set)
    for c in chunks:
        raw = cache.get_raw(cache_key(c, s.llm_model, PROMPT_VERSION))
        if raw is None:
            continue
        results[c.chunk_id] = raw
        from compendium_rag.extract import normalize
        ex = normalize(c, raw)
        for e in ex.entities:
            for a in e.aliases:
                alias_decls[e.name].add(a)

    print(f"参与归并的块：{len(results)}")

    # 直接看 GraphStore 的归并结果
    from compendium_rag.extract import Extraction
    per = []
    for c in chunks:
        if c.chunk_id in results:
            per.append((c.chunk_id, Extraction.from_dict(
                {"entities": results[c.chunk_id].get("entities", []),
                 "relations": []})))
    g = GraphStore(fingerprint="audit")
    # 用真实 extraction 路径（需要 normalize 后的 Extraction）
    per2 = []
    for c in chunks:
        raw = results.get(c.chunk_id)
        if raw is None:
            continue
        per2.append((c.chunk_id, normalize(c, raw)))
    g.build_from_extractions(per2)

    print(f"\n图谱：实体={len(g.entities)} 边={len(g.edges)}")
    print("\n=== 关注实体对的归并情况 ===")
    for a, b in PAIRS:
        ea, eb = g.resolve(a), g.resolve(b)
        if ea is None and eb is None:
            print(f"  {a} / {b}: 均不在图谱")
        elif ea == eb:
            print(f"  {a} / {b}: ✓ 已归并 → {ea}")
        else:
            print(f"  {a} / {b}: ✗ 未归并  ({a}→{ea}, {b}→{eb})")

    print("\n=== 模型声明的别名（TOP 30 实体）===")
    top = sorted(g.entities.values(), key=lambda e: -e.mentions)[:30]
    for e in top:
        if e.aliases:
            print(f"  {e.name} ({e.type}, {e.mentions}): "
                  f"{'、'.join(e.aliases[:6])}")

    print("\n=== 疑似未归并的近似名（同前缀/包含）===")
    names = sorted(g.entities.keys())
    shown = 0
    for i, a in enumerate(names):
        for b in names[i + 1:]:
            if a and b and (a in b or b in a) and a != b and len(a) >= 1:
                print(f"  {a}  ⊂/⊃  {b}")
                shown += 1
                if shown >= 30:
                    return 0
    return 0


if __name__ == "__main__":
    sys.exit(main())
