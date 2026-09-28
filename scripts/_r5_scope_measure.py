# -*- coding: utf-8 -*-
"""R5 立项前范围测量（只读）：同 chunk 共现的「同场」边规模与 PPR 稀释风险。

R5 目标（docs/compendium-rag/ranking/RAG接入生产使用方案_20260926.md §92）：
  scene 级共现表 —— 同一 part.scene.chunk 内共现的实体补「同场」边并锚定版本，
  直击相遇测试暴露的「同场相遇=0」与 2 跳稀缺。范围：≥2 角色实体共现的 chunk。

**闸门重点 = PPR 稀释**：R5 会大幅增加边数，而 PPR 的转移权重
（见 retriever.py build_adjacency）会被更多边摊薄，可能**降低**既有题的命中。
故本脚本先量规模与稀释幅度，再决定是否值得落盘。

输出（只读，不写图/索引）：
  1. 候选 chunk 数、角色实体在 chunk 内的分布；
  2. 朴素两两连边（全连接）与「星型连边」两种方案的边增量；
  3. 对既有图的度分布 / 加权度的影响估计（稀释比的粗算）。
"""
from __future__ import annotations

import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))


def main() -> int:
    s = None
    from compendium_rag.config import get_settings
    from compendium_rag import pipeline as P
    from compendium_rag.graph_store import GraphStore

    s = get_settings()
    g = GraphStore.load(s.graph_path)
    chunks = P.load_chunks(s)
    print(f"[load] entities={len(g.entities)} edges={len(g.edges)} chunks={len(chunks)}")

    # 角色实体
    chars = {eid for eid, e in g.entities.items() if e.type == "角色"}
    print(f"[scope] 角色实体 = {len(chars)} / {len(g.entities)}")

    # 每个 chunk 里出现的角色：用实体自身的 chunk_ids（图谱已有的溯源）
    # 注：mentions 通道即「实体被提及的块」，这是最保守的口径（只用已落盘证据）
    chunk2chars: dict[str, set[str]] = defaultdict(set)
    for eid in chars:
        for cid in g.entities[eid].chunk_ids:
            chunk2chars[cid].add(eid)

    sizes = Counter(len(v) for v in chunk2chars.values())
    multi = {c: v for c, v in chunk2chars.items() if len(v) >= 2}
    print(f"[scope] 有角色出现的 chunk = {len(chunk2chars)}")
    print(f"[scope] 角色数分布（前 8）: {sorted(sizes.items())[:8]}")
    print(f"[scope] ≥2 角色的 chunk（R5 候选） = {len(multi)}")

    # 方案 A：全连接（每对角色一条同场边）
    pairs_full = sum(n * (n - 1) // 2 for n in (len(v) for v in multi.values()))
    # 方案 B：星型（选度数最高的角色为锚，其余连到锚）
    pairs_star = sum(len(v) - 1 for v in multi.values())
    # 方案 C：仅对「规模受控」的场景连边（上限 K）
    for K in (4, 6, 8):
        pairs_cap = sum(min(len(v), K) * (min(len(v), K) - 1) // 2 for v in multi.values())
        print(f"[方案C] 角色数上限 K={K}: 边增量 {pairs_cap:,}")

    cur = len(g["edges"]) if isinstance(g, dict) else len(g.edges)
    print()
    print(f"[baseline] 现有边 {cur:,}")
    print(f"[方案A] 全连接同场边   +{pairs_full:,}  = {cur + pairs_full:,}  （{pairs_full / cur * 100:.0f}% 增幅）")
    print(f"[方案B] 星型同场边     +{pairs_star:,}  = {cur + pairs_star:,}  （{pairs_star / cur * 100:.0f}% 增幅）")

    # 稀释粗算：PPR 转移权重 ∝ confidence*count，度越高每边摊薄越多
    deg = Counter()
    for e in g.edges:
        deg[e.src] += 1
        deg[e.dst] += 1
    # 同场边会给每个参与角色增加 (len-1) 或 (n-1) 条出边
    add_deg = Counter()
    for v in multi.values():
        for eid in v:
            add_deg[eid] += len(v) - 1
    top = add_deg.most_common(10)
    print()
    print("[稀释] 同场边带来的度数增量 Top10（原度 -> 新度, 倍数）:")
    for eid, add in top:
        old = deg.get(eid, 0)
        print(f"   {eid:24} {old:5} -> {old + add:5}  (×{(old + add) / max(old, 1):.1f})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
