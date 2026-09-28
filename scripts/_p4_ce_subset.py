# -*- coding: utf-8 -*-
"""P4 业务价值实测（**有界版**）：零样本 CE 重排放宽池，是否超过冻结线性重排？

为什么可以只用 50 题：
  全量 206 题 × 60 对 = ~12k 对，fp32 CPU 上需 >1 小时（已实测超时）。
  本脚本取**分层抽样 50 题**（含全部 14 道 300cn miss + 36 道随机盲测题）作为
  **判据指示器**：若 CE 在此子集上都不能超过冻结重排，则无立项价值；
  若显著超过，再考虑全量。子集会在报告中明示，不作为最终验收数字。

对照（同一子集）：
  A) RRF 裸检索（lex=1）
  B) 冻结线性重排（v6 production 权重）
  C) 零样本 CE 重排（bge-reranker-large，未在 300cn 拟合）
"""
from __future__ import annotations

import argparse
import json
import random
import sys
import time
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

from compendium_rag import pipeline as P                       # noqa: E402
from compendium_rag.config import get_settings                 # noqa: E402
from _lex_channel_full import LexIndex, load_cases             # noqa: E402
from _r5_variant_scan import clear_ppr_cache, install_fast_ppr  # noqa: E402

import importlib.util
spec = importlib.util.spec_from_file_location("lab", ROOT / "scripts/_rank_rerank_lab.py")
lab = importlib.util.module_from_spec(spec)
spec.loader.exec_module(lab)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=50)
    ap.add_argument("--pool", type=int, default=60)
    ap.add_argument("--model", default="bge-reranker-large")
    ap.add_argument("--max-chars", type=int, default=1024)
    ap.add_argument("--batch", type=int, default=16)
    args = ap.parse_args()

    s = get_settings()
    kb = P.load_kb(s)
    print("[build] lex index …")
    lex = LexIndex(kb.chunks)
    install_fast_ppr()

    # 池：盲测 + 300cn（取 miss）
    blind = load_cases(ROOT / "data/knowledge/_audit/blind_v1/questions_strict.json")
    c300 = load_cases(ROOT / "data/knowledge/_audit/rag_testset_300_cn.json")
    ans = "\n".join(c.text for c in kb.chunks)
    blind = [c for c in blind if any(k in ans for k in c["keywords"])]
    c300 = [c for c in c300 if any(k in ans for k in c["keywords"])]
    MISS = {"R005", "R012", "R094", "R127", "R170", "R171",
            "R180", "R244", "R248", "R273", "R292", "R297", "R298", "R001"}
    miss_cases = [c for c in c300 if c["qid"] in MISS]
    rng = random.Random(20260928)
    others = [c for c in blind if c["qid"] not in {x["qid"] for x in miss_cases}]
    rng.shuffle(others)
    cases = miss_cases + others[: max(0, args.n - len(miss_cases))]
    print(f"[subset] n={len(cases)}（miss={len(miss_cases)} + 盲测随机 {len(cases)-len(miss_cases)}）")

    qvecs = {}
    for f in ("rank_collect_v6c300_top30.json", "rank_collect_v6cblind_top30.json"):
        p = ROOT / "data/compendium_rag/reports" / f
        if p.exists():
            qvecs.update(json.loads(p.read_text(encoding="utf-8")).get("qvecs") or {})

    chunks = kb.retriever.chunks
    prod = json.loads((ROOT / "data/compendium_rag/reports/rank_rerank_lab_300cn_v6.json")
                      .read_text(encoding="utf-8"))["chosen"]
    feats = lab.BASE_FEATURES
    w = np.array([float(prod["weights"].get(f, 0.0)) for f in feats])
    fb = lab.FeatureBuilder(kb)

    from transformers import AutoModelForSequenceClassification, AutoTokenizer
    import torch
    md = ROOT / "models" / args.model
    tok = AutoTokenizer.from_pretrained(str(md))
    model = AutoModelForSequenceClassification.from_pretrained(str(md))
    model.eval()
    torch.set_num_threads(min(8, torch.get_num_threads()))
    print(f"[CE] {args.model} ready")

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

    def hit(ids, kws):
        for cid in ids[:6]:
            c = chunks.get(cid)
            if not c:
                continue
            b = f"{c.text}\n{c.chapter_title}\n{c.scene_title}\n{c.part_title}"
            if any(k in b for k in kws):
                return True
        return False

    res = []
    t0 = time.time()
    for i, c in enumerate(cases, 1):
        ids = pool_for(c["qid"], c["q"])
        a = hit(ids, c["keywords"])
        # B) 冻结线性重排
        evlist = ids[:args.pool]
        if len(evlist) < args.pool:
            evlist += [evlist[-1]] * (args.pool - len(evlist))
        Z1, _ = fb.question(c["q"], qvecs.get(c["qid"]),
                            [{"chunk_id": x} for x in evlist], kb.retriever.link)
        S = (Z1 @ w)[None, :]
        perm = lab.apply_policy(prod["policy"], float(prod["params"]["a"]), S, args.pool)[0]
        b_ids = [evlist[j] for j in perm]
        b = hit(b_ids, c["keywords"])
        # C) 零样本 CE（**分批**打分：一次性喂 60 对会因 padding 到最长而变慢）
        texts = [(c["q"], (chunks[x].text if x in chunks else "")[:args.max_chars]) for x in evlist]
        lg = np.zeros(len(evlist), dtype=np.float32)
        with torch.no_grad():
            for b0 in range(0, len(evlist), args.batch):
                seg = texts[b0:b0 + args.batch]
                enc = tok([t[0] for t in seg], [t[1] for t in seg], padding=True,
                          truncation=True, max_length=512, return_tensors="pt")
                lg[b0:b0 + len(seg)] = model(**enc).logits.view(-1).float().numpy()
        order = sorted(range(len(evlist)), key=lambda j: (-lg[j], evlist[j]))
        c_ids = [evlist[j] for j in order]
        cc = hit(c_ids, c["keywords"])
        res.append({"qid": c["qid"], "rrf": a, "lin": b, "ce": cc})
        if i % 10 == 0 or i == len(cases):
            print(f"  {i}/{len(cases)}  ({time.time()-t0:.0f}s)")

    n = len(res)
    ra = sum(1 for r in res if r["rrf"])
    rb = sum(1 for r in res if r["lin"])
    rc = sum(1 for r in res if r["ce"])
    print(f"\n=== 子集 n={n}，full 口径 hit@6 ===")
    print(f"  A) RRF 裸检索       = {ra}/{n} = {ra/n:.4f}")
    print(f"  B) 冻结线性重排     = {rb}/{n} = {rb/n:.4f}")
    print(f"  C) **零样本 CE**    = {rc}/{n} = {rc/n:.4f}")
    up = [r["qid"] for r in res if r["ce"] and not r["lin"]]
    dn = [r["qid"] for r in res if r["lin"] and not r["ce"]]
    print(f"  CE vs 冻结重排: up={len(up)} {up[:10]}  down={len(dn)} {dn[:10]}")
    miss_hit = {k: sum(1 for r in res if r["qid"] in MISS and r[k]) for k in ("rrf", "lin", "ce")}
    print(f"  miss 命中: RRF={miss_hit['rrf']} 线性={miss_hit['lin']} CE={miss_hit['ce']}")
    out = {"n": n, "rrf": ra / n, "lin": rb / n, "ce": rc / n,
           "up": up, "down": dn, "per_q": res, "note": "分层子集，非全量验收"}
    p = ROOT / "data/compendium_rag/reports/_p4_ce_subset.json"
    p.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\n-> {p}")
    print("判定: " + ("CE 优于冻结重排 -> P4 值得立项" if rc > rb
                     else "CE 未超冻结重排 -> P4 对主口径无增益"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
