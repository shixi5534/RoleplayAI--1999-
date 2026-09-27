# -*- coding: utf-8 -*-
"""R5 稀释机理量化（只读）：证明「同场边注入 PPR」为何收益极小而代价高。

PPR 转移（retriever.py:252-254）为 `damping * s * (w / wsum)`，
其中 `wsum = 节点全部出边权重和`。给高枢纽加边 → wsum 增大 →
其**既有每条边**的转移概率被摊薄。本脚本量化该摊薄幅度。

输出：对既有语料中的关键实体，比较 base 与注入同场边后的
  1) wsum 增幅（= 既有边的平均摊薄倍数）；
  2) 种子实体的一跳邻居「相对转移权重」变化；
  3) 受害最重的前若干邻居（相对权重下降最多者）。
"""
from __future__ import annotations

import math
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

from compendium_rag import pipeline as P                     # noqa: E402
from compendium_rag.config import get_settings               # noqa: E402
from compendium_rag.retriever import build_adjacency         # noqa: E402
from _r5_variant_scan import build_variant                   # noqa: E402


def wsum_map(adj):
    return {n: (sum(w for _, w in nb) or 1.0) for n, nb in adj.items()}


def main() -> int:
    s = get_settings()
    kb = P.load_kb(s)
    g = kb.graph
    adj0, _, _ = build_adjacency(g)
    ws0 = wsum_map(adj0)

    g2, extra = build_variant(g, "star", 0.35)
    adj1, _, _ = build_adjacency(g2)
    ws1 = wsum_map(adj1)
    print(f"[edges] base={len(g.edges):,} -> star={len(g2.edges):,} (+{extra:,})\n")

    # 只看度数最高的枢纽
    deg = Counter()
    for e in g.edges:
        deg[e.src] += 1
        deg[e.dst] += 1
    hubs = [h for h, _ in deg.most_common(8)]
    print("=== 枢纽 wsum 摊薄（既有边的平均转移权重倍数） ===")
    for h in hubs:
        a, b = ws0.get(h, 0.0), ws1.get(h, 0.0)
        print(f"  {h:20} wsum {a:9.1f} -> {b:9.1f}  既有边摊薄 ×{a / b:.3f}  "
              f"(度 {deg[h]} -> {len([1 for m, _ in adj1.get(h, [])])})")

    # 取「维尔汀」为例，量化其邻居相对权重变化
    H = "维尔汀"
    nb0 = dict(adj0.get(H, []))
    nb1 = dict(adj1.get(H, []))
    print(f"\n=== {H} 的邻居相对转移权重（仅比较**既有**邻居） ===")
    rows = []
    for m, w in nb0.items():
        rel0 = w / ws0[H]
        rel1 = w / ws1.get(H, w)
        rows.append((rel0 - rel1, m, rel0, rel1))
    rows.sort(reverse=True)
    print(f"  既有邻居数 {len(rows)}；平均相对权重 {sum(r[2] for r in rows) / len(rows):.5f} "
          f"-> {sum(r[3] for r in rows) / len(rows):.5f}")
    print("  受害最重 Top8（相对权重下降最多）:")
    for d, m, r0, r1 in rows[:8]:
        print(f"    {m:20} {r0:.5f} -> {r1:.5f}  (×{r1 / r0:.3f})")

    print(f"\n[结论] {H} 的既有邻居相对转移权重被整体摊薄约 "
          f"×{(sum(r[3] for r in rows) / sum(r[2] for r in rows)):.3f}；"
          f"即 PPR 在同场边上多走的每一跳，都以其原有邻域的激活为代价。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
