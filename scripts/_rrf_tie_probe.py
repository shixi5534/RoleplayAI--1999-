# -*- coding: utf-8 -*-
"""检验 rrf_fuse 是否真的会出现**平局**（决定是否必须加次级键）。

若平局在真实数据上从不出现，则当前写法虽然脆弱但无实际风险；
若出现，则加显式次级键是必要的（否则排序取决于 dict 插入序 = #39 同类缺陷）。
"""
from __future__ import annotations

import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from compendium_rag import pipeline as P                      # noqa: E402
from compendium_rag.config import get_settings                # noqa: E402


def main() -> int:
    s = get_settings()
    kb = P.load_kb(s)
    r = kb.retriever
    import json
    ts = json.loads((ROOT / "data/knowledge/_audit/rag_testset_300_cn.json").read_text(encoding="utf-8"))
    qs = [c["q"] for c in ts["cases"]]

    # 直接观察 rrf_fuse 的分数是否有并列
    tie_queries = []
    for q in qs[:120]:
        seeds = r.link(q, top_k=6)
        seeds = [x for x in seeds if x.score >= 0.34] or seeds[:2]
        channels = {}
        if seeds:
            gc, _ = r.graph_channel(seeds)
            channels["graph"] = gc
            channels["mention"] = r.mention_channel(seeds)
        if r.lex_index is not None:
            lh = dict(r.lex_index.search(q, 30))
            if lh:
                channels["lex"] = lh
        if not channels:
            continue
        # 复刻 rrf_fuse 的 agg 计算
        agg: dict[str, float] = {}
        for ch, scored in channels.items():
            ranked = sorted(scored.items(), key=lambda kv: -kv[1])
            for rank, (cid, _raw) in enumerate(ranked, start=1):
                agg[cid] = agg.get(cid, 0.0) + 1.0 / (60 + rank)
        vals = Counter(round(v, 12) for v in agg.values())
        ties = {k: c for k, c in vals.items() if c > 1}
        if ties:
            tie_queries.append((q[:24], sum(ties.values()), len(ties)))

    print(f"检验 120 题：出现分数并列的题数 = {len(tie_queries)}")
    for q, ntied, ngroups in tie_queries[:12]:
        print(f"  {q}: 并列元素 {ntied} 个，并列组 {ngroups} 组")
    if not tie_queries:
        print("  -> 真实数据上无并列；当前写法虽脆弱但无实际排序风险")
    else:
        print("  -> **存在并列**：排序将依赖 dict 插入序，必须加显式次级键")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
