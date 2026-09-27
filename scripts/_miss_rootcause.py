# -*- coding: utf-8 -*-
"""逐题根因诊断：14 道池内硬 miss 到底卡在哪一环？

对每题拆解检索管线各环节的产物：
  1. link() 种子（实体链接是否命中正确实体？）
  2. PPR 图通道拿到的证据块（是否包含 gold？）
  3. mention 通道
  4. vector 通道（qvec 存在时）
  5. 融合后排名
并检查 gold 关键词在**整个语料**中的分布 —— 判断是"没检索到"还是"语料里根本没这块"。
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from compendium_rag import pipeline as P                      # noqa: E402
from compendium_rag.config import get_settings                # noqa: E402

MISS = ["R005", "R012", "R018", "R094", "R127", "R170", "R171",
        "R231", "R244", "R248", "R251", "R273", "R297", "R298"]


def main() -> int:
    s = get_settings()
    kb = P.load_kb(s)
    chunks = {c.chunk_id: c for c in kb.chunks}
    blob = {cid: f"{c.text}\n{c.chapter_title}\n{c.scene_title}\n{c.part_title}"
            for cid, c in chunks.items()}

    ts = json.loads((ROOT / "data/knowledge/_audit/rag_testset_300_cn.json").read_text(encoding="utf-8"))
    cases = {str(c.get("id")): c for c in ts["cases"]}

    def kws_of(c):
        out = []
        for grp in (c.get("evidence") or []):
            if isinstance(grp, str):
                out.append(grp)
            elif isinstance(grp, (list, tuple)):
                out.extend(str(x) for x in grp if x)
        return [k.strip() for k in out if k and k.strip()]

    retr = kb.retriever
    for qid in MISS:
        c = cases[qid]
        kws = kws_of(c)
        q = c["q"]
        print("=" * 84)
        print(f"{qid}: {q}")
        print(f"  gold kws: {kws}")

        # 1) 全语料中 gold 关键词的分布（判定语料层是否存在）
        hits = [cid for cid, t in blob.items() if any(k in t for k in kws)]
        print(f"  [语料层] 含任一 gold kw 的块数 = {len(hits)}")
        if hits:
            print(f"           样例: {hits[:3]}")

        # 2) 种子
        seeds = retr.link(q, top_k=6)
        print(f"  [种子] {[(x.eid, x.how, round(x.score, 2)) for x in seeds]}")

        # 3) 各通道
        g_chunks, edges = retr.graph_channel(seeds)
        m_chunks = retr.mention_channel(seeds)
        g_hit = [cid for cid in g_chunks if cid in blob and any(k in blob[cid] for k in kws)]
        m_hit = [cid for cid in m_chunks if cid in blob and any(k in blob[cid] for k in kws)]
        print(f"  [graph通道] n={len(g_chunks)}  含gold={len(g_hit)} {g_hit[:2]}")
        print(f"  [mention通道] n={len(m_chunks)}  含gold={len(m_hit)} {m_hit[:2]}")
        # gold 块是否被 graph 通道**看到**（即使排名靠后）
        inter = set(hits) & set(g_chunks)
        print(f"  [关键] gold 块∩graph通道 = {len(inter)} {list(inter)[:2]}")
    print("=" * 84)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
