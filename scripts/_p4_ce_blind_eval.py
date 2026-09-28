# -*- coding: utf-8 -*-
"""P4 业务价值实测：**零样本交叉编码器**重排放宽池，能否超过现有生产口径？

纪律说明（为什么这个测量是干净的）：
  CE 是**预训练模型零样本使用**，未在 300cn 上做任何拟合，
  因此把它应用到**盲测 206 题**不构成"在留出集上重新拟合"。

对照（盲测 206，full 口径）：
  A) RRF 裸检索（lex=1）           = 0.8350
  B) 冻结线性重排（v6 production）  = 0.8786  <- 当前 BASELINE_v6 验收值
  C) **零样本 CE 重排放宽池(60)**   = 本脚本测量目标

判据（预注册）：
  - 若 C > B -> P4 值得立项，且给出量化增益；
  - 若 C <= B -> P4 对该指标无增益（可能仍对池内 miss 有帮助，但不足以上线）。
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

from compendium_rag import pipeline as P                       # noqa: E402
from compendium_rag.config import get_settings                 # noqa: E402
from _lex_channel_full import LexIndex, load_cases             # noqa: E402
from _r5_variant_scan import clear_ppr_cache, install_fast_ppr  # noqa: E402


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--set", default=str(ROOT / "data/knowledge/_audit/blind_v1/questions_strict.json"))
    ap.add_argument("--collect", default=str(ROOT / "data/compendium_rag/reports/rank_collect_v6cblind_top30.json"))
    ap.add_argument("--model", default="bge-reranker-large")
    ap.add_argument("--pool", type=int, default=60)
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--max-chars", type=int, default=1200)
    ap.add_argument("--out", default=str(ROOT / "data/compendium_rag/reports/_p4_ce_blind.json"))
    args = ap.parse_args()

    s = get_settings()
    kb = P.load_kb(s)
    print("[build] lex index …")
    lex = LexIndex(kb.chunks)
    install_fast_ppr()
    qvecs = (json.loads(Path(args.collect).read_text(encoding="utf-8")).get("qvecs") or {})
    cases = load_cases(Path(args.set))
    ans = "\n".join(c.text for c in kb.chunks)
    cases = [c for c in cases if any(k in ans for k in c["keywords"])]
    if args.limit:
        cases = cases[:args.limit]
    print(f"[tset] {Path(args.set).name} n={len(cases)} pool={args.pool}")

    from transformers import AutoModelForSequenceClassification, AutoTokenizer
    import torch
    md = ROOT / "models" / args.model
    t0 = time.time()
    tok = AutoTokenizer.from_pretrained(str(md))
    model = AutoModelForSequenceClassification.from_pretrained(str(md))
    model.eval()
    torch.set_num_threads(min(8, torch.get_num_threads()))
    print(f"[CE] {args.model} loaded {time.time()-t0:.1f}s")

    chunks = kb.retriever.chunks

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

    def hit6_top(ids, kws):
        for i, cid in enumerate(ids[:6], 1):
            c = chunks.get(cid)
            if not c:
                continue
            b = f"{c.text}\n{c.chapter_title}\n{c.scene_title}\n{c.part_title}"
            if any(k in b for k in kws):
                return True
        return False

    rrf_hit = ce_hit = 0
    perq = {}
    t1 = time.time()
    for i, c in enumerate(cases, 1):
        ids = pool_for(c["qid"], c["q"])
        rrf_h = hit6_top(ids, c["keywords"])          # A) RRF 序前 6
        rrf_hit += rrf_h
        texts = [(c["q"], (chunks[cid].text if cid in chunks else "")[:args.max_chars])
                 for cid in ids]
        with torch.no_grad():
            enc = tok([t[0] for t in texts], [t[1] for t in texts], padding=True,
                      truncation=True, max_length=512, return_tensors="pt")
            logits = model(**enc).logits.view(-1).float().numpy()
        order = sorted(range(len(ids)), key=lambda j: (-logits[j], ids[j]))
        ce_ids = [ids[j] for j in order]
        ce_h = hit6_top(ce_ids, c["keywords"])        # C) CE 序前 6
        ce_hit += ce_h
        perq[c["qid"]] = {"rrf": rrf_h, "ce": ce_h}
        if i % 25 == 0 or i == len(cases):
            print(f"  {i}/{len(cases)}  RRF={rrf_hit}  CE={ce_hit}  ({time.time()-t1:.0f}s)")

    n = len(cases)
    up = sorted(q for q in perq if perq[q]["ce"] and not perq[q]["rrf"])
    dn = sorted(q for q in perq if perq[q]["rrf"] and not perq[q]["ce"])
    print(f"\n=== 盲测 {n} 题，full 口径 hit@6 ===")
    print(f"  A) RRF 裸检索        = {rrf_hit}/{n} = {rrf_hit/n:.4f}")
    print(f"  C) 零样本 CE 重排    = {ce_hit}/{n} = {ce_hit/n:.4f}")
    print(f"  B) 冻结线性重排(v6)  = 0.8786  (既有，作参照)")
    print(f"  CE vs RRF: up={len(up)} down={len(dn)}")
    print(f"    up  : {up[:12]}")
    print(f"    down: {dn[:12]}")
    out = {"n": n, "rrf_hit6": rrf_hit / n, "ce_hit6": ce_hit / n,
           "baseline_v6": 0.8786, "up": up, "down": dn,
           "per_q": perq, "pool": args.pool, "model": args.model}
    Path(args.out).write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\n-> {args.out}")
    verdict = ("CE 优于基线 -> P4 值得立项" if ce_hit / n > 0.8786
               else "CE 未超基线 -> P4 对主口径无增益")
    print(f"判定: {verdict}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
