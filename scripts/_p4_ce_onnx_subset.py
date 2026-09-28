# -*- coding: utf-8 -*-
"""P4 全量可行性：改用 **ONNX int8** CE（266MB，生产同款）重跑同一有界子集，
对比 fp32 bge-reranker-large 的结果，判断能否用它做**全量** 206 题验收。

动机：fp32 CPU 上 ~110s/题，全量 206 题 >1 小时（已实测超时）。
ONNX int8 是仓库既有、生产同款（CrossEncoderReranker 默认走它），若质量接近，
则可用它完成全量验收。

判据：
  - 与 fp32 在同子集上的 hit@6 差异（若接近 -> 可用）；
  - 单题耗时（若 <20s -> 全量 ~1 小时内可行）。
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

MISS = {"R005", "R012", "R094", "R127", "R170", "R171",
        "R180", "R244", "R248", "R273", "R292", "R297", "R298", "R001"}


class OnnxCE:
    def __init__(self, model_dir: Path, onnx_file: str, max_len: int = 512):
        import onnxruntime as ort
        from transformers import AutoTokenizer
        self.tok = AutoTokenizer.from_pretrained(str(model_dir))
        so = ort.SessionOptions()
        so.intra_op_num_threads = 8
        self.sess = ort.InferenceSession(str(model_dir / onnx_file),
                                         sess_options=so,
                                         providers=["CPUExecutionProvider"])
        self.max_len = max_len

    def score(self, pairs, batch=16):
        out = []
        for i in range(0, len(pairs), batch):
            seg = pairs[i:i + batch]
            enc = self.tok([a for a, _ in seg], [b for _, b in seg], padding=True,
                           truncation=True, max_length=self.max_len, return_tensors="np")
            feed = {k: v for k, v in enc.items()
                    if k in {x.name for x in self.sess.get_inputs()}}
            lg = self.sess.run(None, feed)[0]
            out.extend(np.asarray(lg).reshape(-1).tolist())
        return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=26)
    ap.add_argument("--pool", type=int, default=60)
    ap.add_argument("--max-chars", type=int, default=1200)
    args = ap.parse_args()

    s = get_settings()
    kb = P.load_kb(s)
    lex = LexIndex(kb.chunks)
    install_fast_ppr()

    blind = load_cases(ROOT / "data/knowledge/_audit/blind_v1/questions_strict.json")
    c300 = load_cases(ROOT / "data/knowledge/_audit/rag_testset_300_cn.json")
    ans = "\n".join(c.text for c in kb.chunks)
    blind = [c for c in blind if any(k in ans for k in c["keywords"])]
    c300 = [c for c in c300 if any(k in ans for k in c["keywords"])]
    miss_cases = [c for c in c300 if c["qid"] in MISS]
    rng = random.Random(20260928)
    others = [c for c in blind if c["qid"] not in MISS]
    rng.shuffle(others)
    cases = miss_cases + others[: max(0, args.n - len(miss_cases))]
    print(f"[subset] n={len(cases)}（与 fp32 版同一抽样种子，保证可比）")

    qvecs = {}
    for f in ("rank_collect_v6c300_top30.json", "rank_collect_v6cblind_top30.json"):
        p = ROOT / "data/compendium_rag/reports" / f
        if p.exists():
            qvecs.update(json.loads(p.read_text(encoding="utf-8")).get("qvecs") or {})

    chunks = kb.retriever.chunks
    ce = OnnxCE(ROOT / "models" / "bge-reranker-base-onnx", "onnx/model_int8.onnx")
    print("[CE] onnx int8 ready")

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

    t0 = time.time()
    ce_hit = 0
    per = []
    for c in cases:
        ids = pool_for(c["qid"], c["q"])
        pairs = [(c["q"], (chunks[x].text if x in chunks else "")[:args.max_chars]) for x in ids]
        lg = ce.score(pairs, batch=16)
        order = sorted(range(len(ids)), key=lambda j: (-lg[j], ids[j]))
        h = hit([ids[j] for j in order], c["keywords"])
        ce_hit += h
        per.append({"qid": c["qid"], "ce": h})
    n = len(cases)
    dt = time.time() - t0
    print(f"\n=== ONNX int8 CE，子集 n={n} ===")
    print(f"  hit@6 = {ce_hit}/{n} = {ce_hit/n:.4f}")
    print(f"  耗时 = {dt:.0f}s -> {dt/n:.1f}s/题 ；全量 206 题预计 {dt/n*206/60:.1f} 分钟")
    print(f"  对照：fp32 large 在该子集 = 13/26 = 0.5000")
    print(f"  对照：冻结线性重排        = 11/26 = 0.4231")
    p = ROOT / "data/compendium_rag/reports/_p4_ce_onnx_subset.json"
    p.write_text(json.dumps({"n": n, "ce_hit6": ce_hit / n, "seconds_per_q": dt / n,
                             "per_q": per}, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"-> {p}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
