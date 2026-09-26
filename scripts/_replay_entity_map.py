# -*- coding: utf-8 -*-
"""阶段 3：离线回放评测 —— q' = q + 识别实体名，全量口径复评。

评分逻辑逐字复用 compendium_rag_eval300.score_case，保证与已存档基线同口径。
两种档：
  --map none           零档自检（必须逐位复现 eval_*_after_welds.json）
  --map <file.json>    识别映射回放档
闸门（计划书 §5 阶段3 / §6）：
  full/answerable hit@6 提升；unanswerable 不升；grounded=1.000；
  逐题 up/down 题号必报。
"""
from __future__ import annotations

import argparse
import asyncio
import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

from compendium_rag import pipeline as P  # noqa: E402
from compendium_rag.config import get_settings  # noqa: E402
from compendium_rag_eval300 import Case, flatten_evidence, load_cases, score_case, summarize  # noqa: E402

SETS = {
    "native": ROOT / "data" / "knowledge" / "_audit" / "rag_testset_native.json",
    "300_cn": ROOT / "data" / "knowledge" / "_audit" / "rag_testset_300_cn.json",
}
BASE = {
    "native": ROOT / "data" / "compendium_rag" / "reports" / "eval_native_after_welds.json",
    "300_cn": ROOT / "data" / "compendium_rag" / "reports" / "eval_300_cn_after_welds.json",
}
CMP_FIELDS = ("hit", "rr", "seed_hit", "grounded", "n_evidence", "n_edges")


async def run(kb, cases, names_by_qid, top_k):
    rows = []
    corpus_blob = "\n".join(c.text for c in kb.chunks)
    for c in cases:
        c.dims["_answerable"] = any(k in corpus_blob for k in c.keywords)
    for mode, use_vec in (("full", True), ("graph_only", False)):
        t0 = time.time()
        for i, c in enumerate(cases, 1):
            extra = names_by_qid.get(c.qid) or []
            q = c.query + (" " + " ".join(extra) if extra else "")
            r = await score_case(kb, Case(qid=c.qid, query=q, keywords=c.keywords,
                                          dims=c.dims, ref=c.ref), top_k, use_vec)
            r["mode"] = mode
            r["answerable"] = c.dims["_answerable"]
            rows.append(r)
            if i % 50 == 0:
                print(f"  [{mode}] {i}/{len(cases)} ({time.time()-t0:.0f}s)", flush=True)
    return rows


def diff_vs_baseline(rows, base_rows, label):
    bkey = {(r["qid"], r["mode"]): r for r in base_rows}
    mism, ups, downs = [], [], []
    for r in rows:
        b = bkey.get((r["qid"], r["mode"]))
        if b is None:
            mism.append((r["qid"], r["mode"], "missing_in_baseline"))
            continue
        for f in CMP_FIELDS:
            if r[f] != b[f]:
                mism.append((r["qid"], r["mode"], f, b[f], r[f]))
                if f == "hit":
                    (ups if r["hit"] else downs).append(r["qid"])
                break
    print(f"\n== {label} vs after_welds 基线 ==")
    print(f"差异行数: {len(mism)}  (hit 翻转 up={len(set(ups))} down={len(set(downs))})")
    for x in mism[:60]:
        print("  DIFF", x)
    return ups, downs


def groups(rows, mode="full"):
    sub = [r for r in rows if r["mode"] == mode]
    out = {}
    for name, ss in (("all", sub),
                     ("answerable", [r for r in sub if r["answerable"]]),
                     ("unanswerable", [r for r in sub if not r["answerable"]])):
        sm = summarize(ss)
        out[name] = (sm.get("cases"), sm.get("hit@k"), sm.get("MRR"), sm.get("grounded"))
        print(f"  {name:14s} n={sm.get('cases')}  hit@6={sm.get('hit@k')}  "
              f"MRR={sm.get('MRR')}  grounded={sm.get('grounded')}")
    return out


async def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--set", choices=list(SETS), required=True)
    ap.add_argument("--map", default="none", help="映射 json 或 none（零档自检）")
    ap.add_argument("--top-k", type=int, default=6)
    ap.add_argument("--out", default="")
    args = ap.parse_args()

    kb = P.load_kb(get_settings())
    cases = load_cases(SETS[args.set])

    names_by_qid: dict[str, list[str]] = {}
    if args.map != "none":
        m = json.loads(Path(args.map).read_text(encoding="utf-8"))["map"]
        for qid, eids in m.items():
            names_by_qid[qid] = [kb.graph.entities[e].name for e in eids
                                 if e in kb.graph.entities]
    print(f"set={args.set} n={len(cases)} 映射覆盖题数={len(names_by_qid)}")

    rows = await run(kb, cases, names_by_qid, args.top_k)

    base_rows = json.loads(BASE[args.set].read_text(encoding="utf-8"))["rows"]
    label = "零档自检" if args.map == "none" else f"回放档({Path(args.map).name})"
    print(f"\n== {label} 分组指标（full 模式）==")
    g_new = groups(rows)
    print(f"\n== 基线 after_welds 分组指标（full 模式，参考）==")
    g_old = groups(base_rows)
    ups, downs = diff_vs_baseline(rows, base_rows, label)

    if args.out:
        Path(args.out).write_text(json.dumps(
            {"set": args.set, "map": args.map, "rows": rows,
             "up": sorted(set(ups)), "down": sorted(set(downs)),
             "new": g_new, "old": g_old},
            ensure_ascii=False, indent=1), encoding="utf-8")
        print(f"报告 → {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
