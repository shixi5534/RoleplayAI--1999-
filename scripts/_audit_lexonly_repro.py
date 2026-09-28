# -*- coding: utf-8 -*-
"""独立复现：盲测 206 上『词面通道单独（lex-only）』hit@6 —— 验证文档 §4.1 的 192/206=0.9320。

lex-only 不涉及 PPR/图通道，故应较快。
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

from compendium_rag import pipeline as P                    # noqa: E402
from compendium_rag.config import get_settings              # noqa: E402
from compendium_rag.retriever import RetrievalResult        # noqa: E402
from _lex_channel_full import LexIndex, load_cases          # noqa: E402

s = get_settings()
kb = P.load_kb(s)
print("[build] lex index …", flush=True)
lex = LexIndex(kb.chunks)
rets = kb.retriever
chunks = rets.chunks

blind = [c for c in load_cases(ROOT / "data/knowledge/_audit/blind_v1/questions_strict.json")]
ans = "\n".join(c.text for c in kb.chunks)
blind = [c for c in blind if any(k in ans for k in c["keywords"])]
print(f"[tset] 盲测 n={len(blind)}", flush=True)

TOP_K = 6
LEX_TOP = 30
hit = 0
miss = []
for c in blind:
    res = RetrievalResult(query=c["q"])
    res.evidence = rets.rrf_fuse({"lex": dict(lex.search(c["q"], LEX_TOP))},
                                 weights={"lex": 1.0},
                                 top_n=max(TOP_K * 4, 24))
    h = False
    for e in res.evidence[:TOP_K]:
        ch = chunks.get(e.chunk_id)
        if not ch:
            continue
        b = f"{ch.text}\n{ch.chapter_title}\n{ch.scene_title}\n{ch.part_title}"
        if any(k in b for k in c["keywords"]):
            h = True
            break
    if h:
        hit += 1
    else:
        miss.append(c["qid"])

print()
print("=" * 70)
print(f"lex-only 盲测206 hit@6 = {hit}/{len(blind)} = {hit/len(blind):.4f}")
print(f"文档 §4.1 声称          = 192/206 = {192/206:.4f}")
print(f"eval_blind_lexfirst     = 190/206 = {190/206:.4f}")
print("=" * 70)
print(f"miss({len(miss)})={miss}")
