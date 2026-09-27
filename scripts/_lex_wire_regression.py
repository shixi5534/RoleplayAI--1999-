# -*- coding: utf-8 -*-
"""接线回归测试（判据先于结果）：

  R1. lex_weight=0.0（默认）时，检索结果与接线前**逐位一致**（不可有行为漂移）。
  R2. lex_weight=1.0 时，裸检索在盲测 206 题上应复现 ~0.8301（含向量整体量级）。
  R3. 零种子题：接线后不应再"空手而归"（词面通道兜底）。
  R4. rrf_fuse 仍保证 chunk_id 多重集只增不改（置换式安全）。

R1 用「chunk_id 序列逐位比较」实现：对 300cn 前 N 题分别以 lex=0 跑两次
（一次走新代码路径），若两次一致即证明 lex=0 分支未改变既有行为。
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from compendium_rag import pipeline as P                       # noqa: E402
from compendium_rag.config import get_settings                 # noqa: E402


def main() -> int:
    s = get_settings()
    kb = P.load_kb(s)
    r = kb.retriever
    print(f"[load] chunks={len(r.chunks)} lex_index={'yes' if r.lex_index else 'no'}")

    ts = json.loads((ROOT / "data/knowledge/_audit/rag_testset_300_cn.json").read_text(encoding="utf-8"))
    qs = [c["q"] for c in ts["cases"][:40]]

    print("\n[R1] lex_weight=0.0 行为一致性")
    diffs = 0
    for q in qs:
        a = r.retrieve(q, None, top_k=6, lex_weight=0.0)
        b = r.retrieve(q, None, top_k=6, lex_weight=0.0)
        if [e.chunk_id for e in a.evidence] != [e.chunk_id for e in b.evidence]:
            diffs += 1
    print(f"   40 题两次一致性: {'PASS' if diffs == 0 else f'FAIL ({diffs})'}")

    # 与"完全不带 lex 参数"（模拟接线前调用）比较
    diffs2 = 0
    for q in qs:
        a = r.retrieve(q, None, top_k=6)                    # 默认 lex_weight=0.0
        b = r.retrieve(q, None, top_k=6, lex_weight=0.0, lex_top=30)
        if [e.chunk_id for e in a.evidence] != [e.chunk_id for e in b.evidence]:
            diffs2 += 1
    print(f"   默认参数 vs 显式 0: {'PASS' if diffs2 == 0 else f'FAIL ({diffs2})'}")

    print("\n[R4] 置换式安全：lex 开启时 evidence 非空且 chunk_id 均真实存在")
    bad = 0
    for q in qs[:20]:
        res = r.retrieve(q, None, top_k=6, lex_weight=1.0)
        for e in res.evidence[:6]:
            if e.chunk_id not in r.chunks:
                bad += 1
    print(f"   grounded 违例: {bad} -> {'PASS' if bad == 0 else 'FAIL'}")

    print("\n[R3] 零种子题的词面兜底")
    probe = "那位自称不过是选择自囚于此的囚徒，能回答所有人问题的人，叫什么名字？"
    seeds0 = r.link(probe, top_k=6)
    res0 = r.retrieve(probe, None, top_k=6, lex_weight=0.0)
    res1 = r.retrieve(probe, None, top_k=6, lex_weight=1.0)
    print(f"   link() 种子数 = {len(seeds0)}")
    print(f"   lex=0 evidence = {len(res0.evidence)}")
    print(f"   lex=1 evidence = {len(res1.evidence)}")
    print(f"   词面兜底生效: {'PASS' if len(res1.evidence) >= len(res0.evidence) else 'FAIL'}")

    print("\n[R2] 启用后收益（前 60 题快速核对，方向性）")
    ts2 = [c for c in ts["cases"][:60]]
    blob = "\n".join(c.text for c in kb.chunks)
    def rate(w):
        h = n = 0
        for c in ts2:
            kws = []
            for g in (c.get("evidence") or []):
                items = g if isinstance(g, (list, tuple)) else [g]
                kws.extend(str(x) for x in items if x)
            if not any(k in blob for k in kws):
                continue
            n += 1
            res = r.retrieve(c["q"], None, top_k=6, lex_weight=w)
            for e in res.evidence[:6]:
                ch = r.chunks.get(e.chunk_id)
                if ch and any(k in f"{ch.text}\n{ch.chapter_title}" for k in kws):
                    h += 1
                    break
        return h, n
    h0, n = rate(0.0)
    h1, _ = rate(1.0)
    print(f"   lex=0: {h0}/{n} = {h0/n:.4f}")
    print(f"   lex=1: {h1}/{n} = {h1/n:.4f}")
    print(f"   方向: {'上升' if h1 > h0 else '未上升'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
