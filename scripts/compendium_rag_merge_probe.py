# -*- coding: utf-8 -*-
"""检查为何 `重塑之手` 被归并到 `重塑·信徒`，以及包含关系是否被错误合并。

关键问题：`决斗` ⊂ `决斗观赏赛` 这类**部分包含**是否被 union-find 误合并？
（本库的全名归并规则要求"短名 + 分隔符 + 其余"，理论上不应触发。）
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from compendium_rag import pipeline as P  # noqa: E402
from compendium_rag.config import get_settings  # noqa: E402
from compendium_rag.extract import PROMPT_VERSION, ExtractionCache, cache_key, normalize  # noqa: E402
from compendium_rag.graph_store import GraphStore  # noqa: E402


def main() -> int:
    s = get_settings()
    chunks = P.load_chunks(s)
    cache = ExtractionCache(s.cache_dir)
    per = []
    for c in chunks:
        raw = cache.get_raw(cache_key(c, s.llm_model, PROMPT_VERSION))
        if raw is not None:
            per.append((c.chunk_id, normalize(c, raw)))

    g = GraphStore(fingerprint="audit")
    g.build_from_extractions(per)
    print(f"实体={len(g.entities)} 边={len(g.edges)}")

    # 哪些实体归并到了 重塑·信徒？
    target = g.resolve("重塑·信徒")
    print(f"\n=== 归并到 `重塑·信徒` 的成员 ===")
    members = [n for n, eid in g.alias_index.items() if eid == target]
    print("  " + "、".join(members))

    for probe in ("重塑之手", "重塑", "重塑·信徒"):
        eid = g.resolve(probe)
        print(f"  {probe} → {eid}")

    print("\n=== 部分包含是否被误合并（应各自独立）===")
    for a, b in [("决斗", "决斗观赏赛"), ("切尔西", "切尔西花展"),
                 ("乔治橡树", "橡树"), ("中心瞭望塔", "瞭望塔"),
                 ("软盘", "便携式软盘"), ("神秘术", "光学神秘术")]:
        ea, eb = g.resolve(a), g.resolve(b)
        status = "同一实体（可能误合并）" if ea == eb and ea else "独立"
        print(f"  {a} / {b}: {status}")

    print("\n=== 每条边的证据可溯源性 ===")
    no_ev = [e for e in g.edges if not e.evidence]
    no_chunk = [e for e in g.edges if not e.chunk_ids]
    print(f"  无 evidence 的边：{len(no_ev)}/{len(g.edges)}")
    print(f"  无 chunk_ids 的边：{len(no_chunk)}/{len(g.edges)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
