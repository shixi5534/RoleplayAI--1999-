# -*- coding: utf-8 -*-
"""盲测 miss 归因：找出**盲测条件下**真正的瓶颈（seed 空 / 图不通 / 需语义）。

与 300cn 的 14 道 miss 不同，盲测题由独立子代理按"玩家口语+描述性指代"写成，
预期失败模式更偏「实体链接失败」与「语义改写」。
"""
from __future__ import annotations

import json
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
    chunks = {c.chunk_id: c for c in kb.chunks}
    blob = {cid: f"{c.text}\n{c.chapter_title}\n{c.scene_title}\n{c.part_title}"
            for cid, c in chunks.items()}

    d = json.loads((ROOT / "data/knowledge/_audit/blind_v1/questions_strict.json")
                   .read_text(encoding="utf-8"))
    cases = d["cases"]

    def kws(c):
        out = []
        for g in c["evidence"]:
            out.extend(g)
        return out

    retr = kb.retriever
    stat = Counter()
    rows = []
    for c in cases:
        k = kws(c)
        gold = [cid for cid, t in blob.items() if any(x in t for x in k)]
        seeds = retr.link(c["q"], top_k=6)
        seeds = [x for x in seeds if x.score >= 0.34] or seeds[:2]
        g_chunks, _ = retr.graph_channel(seeds) if seeds else ({}, [])
        m_chunks = retr.mention_channel(seeds) if seeds else {}
        # gold 是否进池（graph 或 mention）
        in_graph = len(set(gold) & set(g_chunks))
        in_mention = len(set(gold) & set(m_chunks))
        tag = ("no_seed" if not seeds else
               "graph_hit" if in_graph else
               "mention_hit" if in_mention else
               "no_channel")
        stat[tag] += 1
        rows.append((c["id"], tag, len(gold), [x.eid for x in seeds][:3]))

    print("=== 盲测 strict 152 题的**图通道**可达性分类 ===")
    for k, v in stat.most_common():
        print(f"  {k:14} {v:4}  ({v / len(cases):.1%})")
    print()
    print("=== no_seed（实体链接零命中）样例 ===")
    n = 0
    for cid, tag, ng, sd in rows:
        if tag == "no_seed":
            print(f"  {cid}: gold块={ng} seeds={sd}")
            n += 1
            if n >= 10:
                break
    print()
    print("=== gold 块数=0 的题（题面与语料脱节？）===")
    zero = [r for r in rows if r[2] == 0]
    print(f"  {len(zero)} 题 {[r[0] for r in zero][:10]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
