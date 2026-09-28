# -*- coding: utf-8 -*-
"""P4 决定性验证：**真跑交叉编码器**，看放宽池后进池的 6 道能否被 CE 排进 top-6。

为什么必须真跑：
  仓库已落盘的 ce_*_300_cn.json 只覆盖**原 top-30 池**（键为名次 "1".."30"），
  无法回答"池放宽到 60 后 CE 能否救"这个问题。故此处直接对**放宽池**打分。

范围（控制成本）：只对 4 道 miss（含 3 道新进池题）+ 6 道对照题打分，
每对 (query, chunk)，用 bge-reranker-large（本地 fp32）。

判据（预注册）：
  - 若新进池题的 gold 在 CE 排序下进入 top-6 -> P4 值得立项；
  - 否则 CE 也救不回，须走 P3（查询侧供给）或补充抽提。
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

from compendium_rag import pipeline as P                      # noqa: E402
from compendium_rag.config import get_settings                # noqa: E402
from _lex_channel_full import LexIndex                        # noqa: E402
from _r5_variant_scan import clear_ppr_cache, install_fast_ppr  # noqa: E402

TARGETS = ["R180", "R244", "R248", "R273", "R292", "R298"]
CONTROLS = ["R001", "R018", "R052", "R164", "R231", "R238"]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="bge-reranker-large")
    ap.add_argument("--pool", type=int, default=60)
    ap.add_argument("--max-chars", type=int, default=1200)
    args = ap.parse_args()

    s = get_settings()
    kb = P.load_kb(s)
    print("[build] lex index …")
    lex = LexIndex(kb.chunks)
    install_fast_ppr()

    from transformers import AutoModelForSequenceClassification, AutoTokenizer
    import torch
    md = ROOT / "models" / args.model
    print(f"[CE] loading {md} …")
    t0 = time.time()
    tok = AutoTokenizer.from_pretrained(str(md))
    model = AutoModelForSequenceClassification.from_pretrained(str(md))
    model.eval()
    torch.set_num_threads(min(8, torch.get_num_threads()))
    print(f"[CE] loaded in {time.time()-t0:.1f}s")

    ts = json.loads((ROOT / "data/knowledge/_audit/rag_testset_300_cn.json").read_text(encoding="utf-8"))
    by = {str(c["id"]): c for c in ts["cases"]}
    chunks = kb.retriever.chunks
    blob = {cid: f"{c.text}\n{c.chapter_title}\n{c.scene_title}\n{c.part_title}"
            for cid, c in chunks.items()}

    def kws(c):
        out = []
        for g in (c.get("evidence") or []):
            items = g if isinstance(g, (list, tuple)) else [g]
            out.extend(str(x) for x in items if x)
        return [k.strip() for k in out if k.strip()]

    qvecs = (json.loads((ROOT / "data/compendium_rag/reports/rank_collect_v6c300_top30.json")
                        .read_text(encoding="utf-8")).get("qvecs") or {})

    def pool_for(qid, q):
        clear_ppr_cache()
        seeds = kb.retriever.link(q, top_k=6)
        seeds = [x for x in seeds if x.score >= 0.34] or seeds[:2]
        ch = {"lex": dict(lex.search(q, 30))}
        if seeds:
            gc, _ = kb.retriever.graph_channel(seeds)
            ch["graph"] = gc
            ch["mention"] = kb.retriever.mention_channel(seeds)
        qv = qvecs.get(qid)
        if qv is not None:
            ch["vector"] = kb.retriever.vector_channel(qv, 50)
        return [e.chunk_id for e in kb.retriever.rrf_fuse(ch, weights={"lex": 1.0}, top_n=args.pool)]

    print(f"\n{'qid':6}{'池内gold名次':>12}{'CE序gold名次':>14}  CE top6?")
    print("-" * 56)
    ce_hit = 0
    tot = 0
    for qid in TARGETS + CONTROLS:
        c = by[qid]
        kq = kws(c)
        gold = {cid for cid, t in blob.items() if any(k in t for k in kq)}
        ids = pool_for(qid, c["q"])
        rrf_rank = next((i for i, cid in enumerate(ids, 1) if cid in gold), None)
        # CE 打分
        texts = [(c["q"], (chunks[cid].text if cid in chunks else "")[:args.max_chars])
                 for cid in ids]
        with torch.no_grad():
            enc = tok([t[0] for t in texts], [t[1] for t in texts],
                      padding=True, truncation=True, max_length=512, return_tensors="pt")
            logits = model(**enc).logits.view(-1).float().numpy()
        order = sorted(range(len(ids)), key=lambda i: (-logits[i], ids[i]))
        ce_rank = next((r for r, i in enumerate(order, 1) if ids[i] in gold), None)
        ok = ce_rank is not None and ce_rank <= 6
        ce_hit += ok
        tot += 1
        print(f"{qid:6}{str(rrf_rank):>12}{str(ce_rank):>14}  {'**YES**' if ok else 'no'}")
    print(f"\nCE 排序把 gold 排进 top-6 的: {ce_hit}/{tot}")
    print(f"  其中新进池 6 道: {ce_hit if False else ''}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
