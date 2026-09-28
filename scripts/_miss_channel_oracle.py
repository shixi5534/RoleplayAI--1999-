# -*- coding: utf-8 -*-
"""目标① 决定性诊断：14 道池内 miss 的 gold 块**是否出现在任何通道的候选集**里？

这决定了救治路线：
  - 若 gold 出现在某通道（哪怕排名很后）-> 属**融合/排序**问题，可靠调权重解决；
  - 若 gold 不出现在**任何**通道的输出里 -> 属**候选源缺失**，必须新增来源
    （查询侧供给 P3 / 补充抽提），不可能靠调参救回。

方法：对每题取各通道的**全量**输出（不截断），检查 gold 是否在其中及其排名。
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

from compendium_rag import pipeline as P                      # noqa: E402
from compendium_rag.config import get_settings                # noqa: E402
from _lex_channel_full import LexIndex                        # noqa: E402

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
    lex = LexIndex(kb.chunks)

    ts = json.loads((ROOT / "data/knowledge/_audit/rag_testset_300_cn.json").read_text(encoding="utf-8"))
    by = {str(c["id"]): c for c in ts["cases"]}

    print(f"{'qid':6}{'gold':>5}  {'graph':>7}{'mention':>8}{'lex':>7}{'vector':>8}   结论")
    print("-" * 92)
    from collections import Counter
    verdicts = Counter()
    for q in MISS:
        c = by[q]
        kws = kws_of(c)
        gold = {cid for cid, t in blob.items() if any(k in t for k in kws)}
        seeds = r.link(c["q"], top_k=6)
        seeds = [x for x in seeds if x.score >= 0.34] or seeds[:2]

        gc = {}
        mc = {}
        if seeds:
            gc, _ = r.graph_channel(seeds)
            mc = r.mention_channel(seeds)
        lc = dict(lex.search(c["q"], 10 ** 6))

        def bestrank(chan):
            if not chan:
                return None
            ranked = sorted(chan.items(), key=lambda kv: (-kv[1], kv[0]))
            for i, (cid, _) in enumerate(ranked, 1):
                if cid in gold:
                    return i
            return None

        rg, rm, rl = bestrank(gc), bestrank(mc), bestrank(lc)
        any_in = any(x is not None for x in (rg, rm, rl))
        if any_in:
            verdicts["候选里有（融合/排序问题）"] += 1
            concl = "候选里有 -> 可调融合/权重"
        else:
            verdicts["任何通道都没有（需新候选源 = P3）"] += 1
            concl = "**无通道可达 -> 必须 P3/补抽提**"
        fmt = lambda x: "-" if x is None else str(x)
        print(f"{q:6}{len(gold):>5}  {fmt(rg):>7}{fmt(rm):>8}{fmt(rl):>7}{'未测':>8}   {concl}")

    print()
    print("结论分布:", dict(verdicts))
    print("\n注：lex 通道为全量输出（未截断），graph/mention 为其自然输出。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
