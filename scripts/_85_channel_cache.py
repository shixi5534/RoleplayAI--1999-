# -*- coding: utf-8 -*-
"""85% 目标基础设施：把每题的四通道输出**缓存到磁盘**，之后扫参/改规则毫秒级。

动机（前序报告纪律）：PPR 是主要耗时（1-3s/题）；批量实验务必先缓存通道结果再扫参。

本脚本对 300cn(全集300→answerable) 与盲测 strict(206) 各算一次通道：
  lex(BM25, top300) / graph(PPR, top200) / mention(top200) / vector(top200)
并顺带落盘每题 gold 命中块集合（供离线 hit@6 判定，无需再加载语料）。

只读语料与图，只写 reports/ 下的新文件。
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
from _r5_variant_scan import clear_ppr_cache, install_fast_ppr  # noqa: E402
from _lex_channel_full import LexIndex, load_cases             # noqa: E402

R = ROOT / "data/compendium_rag/reports"
AUDIT = ROOT / "data/knowledge/_audit"

SETS = {
    "300cn": (AUDIT / "rag_testset_300_cn.json", "rank_collect_v6c300_top30.json"),
    "blind": (AUDIT / "blind_v1/questions_strict.json", "rank_collect_v6cblind_top30.json"),
}

LEX_N, GRAPH_N, MENT_N, VEC_N = 300, 200, 200, 200


def ranked(d: dict, n: int) -> list[list]:
    return [[cid, round(float(s), 8)]
            for cid, s in sorted(d.items(), key=lambda kv: (-kv[1], kv[0]))[:n]]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--out", default="")
    args = ap.parse_args()

    s = get_settings()
    kb = P.load_kb(s)
    print("[build] lex index …", flush=True)
    lex = LexIndex(kb.chunks)
    install_fast_ppr()
    rets = kb.retriever
    chunks = rets.chunks

    # chunk_id -> 判定用的文本 blob（与官方 eval 完全一致）
    blob = {cid: f"{c.text}\n{c.chapter_title}\n{c.scene_title}\n{c.part_title}"
            for cid, c in chunks.items()}
    print(f"[corpus] chunks={len(chunks)}", flush=True)

    out: dict = {"meta": {"lex_n": LEX_N, "graph_n": GRAPH_N, "ment_n": MENT_N,
                          "vec_n": VEC_N, "seed_threshold": 0.34},
                 "sets": {}}

    t0 = time.time()
    for setname, (spath, qvec_file) in SETS.items():
        cases = load_cases(spath)
        qvecs = (json.loads((R / qvec_file).read_text(encoding="utf-8")).get("qvecs") or {})
        print(f"\n[{setname}] cases={len(cases)} qvecs={len(qvecs)}", flush=True)
        recs: dict[str, dict] = {}
        for i, c in enumerate(cases, 1):
            if args.limit and i > args.limit:
                break
            qid, q = c["qid"], c["q"]
            clear_ppr_cache()
            seeds = rets.link(q, top_k=6)
            seeds = [x for x in seeds if x.score >= 0.34] or seeds[:2]
            ch: dict[str, dict] = {}
            ch["lex"] = dict(lex.search(q, LEX_N))
            if seeds:
                gc, _ = rets.graph_channel(seeds)
                ch["graph"] = dict(gc)
                ch["mention"] = dict(rets.mention_channel(seeds))
            qv = qvecs.get(qid)
            if qv is not None:
                ch["vector"] = dict(rets.vector_channel(qv, VEC_N))
            gold = [cid for cid, b in blob.items() if any(k in b for k in c["keywords"])]
            recs[qid] = {
                "q": q,
                "keywords": list(c["keywords"]),
                "n_seeds": len(seeds),
                "seed_names": [x.name for x in seeds[:6]],
                "channels": {
                    "lex": ranked(ch.get("lex", {}), LEX_N),
                    "graph": ranked(ch.get("graph", {}), GRAPH_N),
                    "mention": ranked(ch.get("mention", {}), MENT_N),
                    "vector": ranked(ch.get("vector", {}), VEC_N),
                },
                "gold": gold,
            }
            if i % 25 == 0 or i == len(cases):
                print(f"  {i}/{len(cases)}  {time.time()-t0:.0f}s", flush=True)
        n_ans = sum(1 for r in recs.values() if r["gold"])
        print(f"[{setname}] n={len(recs)}  answerable(有gold)={n_ans}  "
              f"零seed={sum(1 for r in recs.values() if r['n_seeds']==0)}", flush=True)
        out["sets"][setname] = recs

    dest = Path(args.out) if args.out else (R / "_85_channel_cache.json")
    dest.write_text(json.dumps(out, ensure_ascii=False), encoding="utf-8")
    print(f"\n-> {dest}  ({dest.stat().st_size/1e6:.1f} MB)  {time.time()-t0:.0f}s")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
