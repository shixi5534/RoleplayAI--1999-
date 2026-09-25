# -*- coding: utf-8 -*-
"""用既有 plot RAG 的 300 题评测 Compendium 新库。

口径设计（重要）
----------------
这 300 题是为**旧语料**（B站视频转写 + 灰机 wiki，含英文名）造的，而
Compendium 是**纯简体中文官方正文**。实测约 44% 的题目标注的答案关键词
（Zanetta / Charlotte O'Hagan / Marcus …）在 Compendium 里**根本不存在**——
这些题对任何中文语料 RAG 都不可答，混在一起算会把召回率整体拉低，
得到的是一个既不反映语料差异、也不反映检索能力的数字。

因此本评测把 300 题**分层报告**，而不是只给一个总分：

1. ``all``            —— 全部题（含不可答的，最保守的口径）
2. ``answerable``     —— 答案关键词在 Compendium 中出现过的题（**主口径**）
3. ``cn_keyword``     —— 其中期望关键词是**中文**的题（最公平的子集，
                          排除"中文语料 vs 英文名查询"的语料差异）
4. ``unanswerable``   —— 关键词完全不在语料中的题（**只报不评**，
                          用于说明语料边界，不是算法失败）

指标：``hit@k``（top-k 证据块中命中任一期望关键词）、``MRR``、
``seed_recall``（期望实体是否被链接）、``grounded``（证据是否真出自语料）。
"""
from __future__ import annotations

import argparse
import asyncio
import json
import re
import sys
import time
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from compendium_rag import pipeline as P  # noqa: E402
from compendium_rag.config import get_settings  # noqa: E402

DEFAULT_SET = ROOT / "data" / "knowledge" / "_audit" / "rag_testset_300.json"
RE_CN = re.compile(r"[\u4e00-\u9fff]")


@dataclass
class Case:
    qid: str
    query: str
    keywords: list[str]
    dims: dict = field(default_factory=dict)
    ref: str = ""

    @property
    def is_cn_keyword(self) -> bool:
        return any(RE_CN.search(k) for k in self.keywords)


def flatten_evidence(ev) -> list[str]:
    out: list[str] = []
    for grp in (ev or []):
        if isinstance(grp, str):
            out.append(grp)
        elif isinstance(grp, (list, tuple)):
            out.extend(str(x) for x in grp if x)
    # 保留原样，但去重且过滤空串；单字符关键词（如数字）保留
    seen, res = set(), []
    for k in out:
        k = k.strip()
        if k and k not in seen:
            seen.add(k)
            res.append(k)
    return res


def load_cases(path: Path) -> list[Case]:
    d = json.loads(path.read_text(encoding="utf-8"))
    rows = d if isinstance(d, list) else d.get("cases", [])
    out = []
    for r in rows:
        kws = flatten_evidence(r.get("evidence"))
        if not kws:
            continue
        out.append(Case(qid=str(r.get("id", "")), query=r.get("q", ""),
                        keywords=kws, dims=r.get("dims") or {},
                        ref=r.get("ref", "")))
    return out


async def score_case(kb, case: Case, top_k: int, use_vector: bool) -> dict:
    t0 = time.time()
    res = await kb.retrieve(case.query, top_k=top_k, use_vector=use_vector)
    dt = time.time() - t0

    # hit / MRR：在 top_k 证据块的文本+篇名+场景里找期望关键词
    rr = 0.0
    hit = False
    for rank, ev in enumerate(res.get("evidence", [])[:top_k], start=1):
        c = kb.retriever.chunks.get(ev["chunk_id"])
        if not c:
            continue
        blob = f"{c.text}\n{c.chapter_title}\n{c.scene_title}\n{c.part_title}"
        if any(k in blob for k in case.keywords):
            hit = True
            if rr == 0.0:
                rr = 1.0 / rank
            break

    seed_names = [s["name"] for s in res.get("seeds", [])]
    seed_hits = [k for k in case.keywords
                 if any(k == n or k in n or n in k for n in seed_names)]
    grounded = all(ev["chunk_id"] in kb.retriever.chunks
                   for ev in res.get("evidence", [])[:top_k])

    return {"qid": case.qid, "query": case.query, "hit": hit, "rr": rr,
            "seed_hit": bool(seed_hits), "grounded": grounded,
            "n_evidence": len(res.get("evidence", [])),
            "n_edges": len(res.get("edges", [])),
            "seconds": round(dt, 3), "dims": case.dims,
            "cn_keyword": case.is_cn_keyword}


def summarize(rows: list[dict]) -> dict:
    n = len(rows)
    if not n:
        return {"cases": 0}
    by_type: dict[str, dict] = defaultdict(lambda: {"n": 0, "hit": 0})
    for r in rows:
        t = r["dims"].get("type", "?")
        by_type[t]["n"] += 1
        by_type[t]["hit"] += 1 if r["hit"] else 0
    by_hop: dict[str, dict] = defaultdict(lambda: {"n": 0, "hit": 0})
    for r in rows:
        h = r["dims"].get("hop", "?")
        by_hop[h]["n"] += 1
        by_hop[h]["hit"] += 1 if r["hit"] else 0
    return {
        "cases": n,
        "hit@k": round(sum(1 for r in rows if r["hit"]) / n, 4),
        "MRR": round(sum(r["rr"] for r in rows) / n, 4),
        "seed_recall": round(sum(1 for r in rows if r["seed_hit"]) / n, 4),
        "grounded": round(sum(1 for r in rows if r["grounded"]) / n, 4),
        "avg_seconds": round(sum(r["seconds"] for r in rows) / n, 3),
        "by_type": {k: round(v["hit"] / v["n"], 3)
                    for k, v in sorted(by_type.items())},
        "by_hop": {k: round(v["hit"] / v["n"], 3)
                   for k, v in sorted(by_hop.items())},
    }


async def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--set", default=str(DEFAULT_SET))
    ap.add_argument("--top-k", type=int, default=6)
    ap.add_argument("--no-vector", action="store_true",
                    help="只跑纯图谱模式（更快）")
    ap.add_argument("--limit", type=int, default=0, help="只跑前 N 题（调试）")
    args = ap.parse_args()

    s = get_settings()
    kb = P.load_kb(s)
    gst = kb.graph.stats()
    cases = load_cases(Path(args.set))
    if args.limit:
        cases = cases[:args.limit]

    corpus_blob = "\n".join(c.text for c in kb.chunks)
    for c in cases:
        c.dims["_answerable"] = any(k in corpus_blob for k in c.keywords)

    print(f"新库：块={len(kb.chunks)} 实体={gst['entities']} 边={gst['edges']} "
          f"覆盖={len(kb.graph.entities)} 实体")
    print(f"测试集：{Path(args.set).name}  n={len(cases)}  top_k={args.top_k}")

    modes = [("graph_only", False)] if args.no_vector else \
            [("full", True), ("graph_only", False)]

    all_rows: list[dict] = []
    for mode, use_vec in modes:
        print(f"\n{'=' * 84}\n模式：{mode}\n{'=' * 84}")
        rows = []
        for i, c in enumerate(cases, 1):
            r = await score_case(kb, c, args.top_k, use_vec)
            r["mode"] = mode
            r["answerable"] = c.dims["_answerable"]
            rows.append(r)
            if i % 50 == 0:
                acc = sum(1 for x in rows if x["hit"]) / len(rows)
                print(f"  …{i}/{len(cases)}  累计 hit@k={acc:.3f}")
        all_rows.extend(rows)

        groups = {
            "all": rows,
            "answerable": [r for r in rows if r["answerable"]],
            "answerable+cn_keyword": [r for r in rows
                                      if r["answerable"] and r["cn_keyword"]],
            "unanswerable（仅报数，不评算法）":
                [r for r in rows if not r["answerable"]],
        }
        for name, sub in groups.items():
            sm = summarize(sub)
            if not sm.get("cases"):
                continue
            print(f"\n  ── {name}  (n={sm['cases']}) ──")
            print(f"     hit@k={sm['hit@k']:.3f}  MRR={sm['MRR']:.3f}  "
                  f"seed_recall={sm['seed_recall']:.3f}  "
                  f"grounded={sm['grounded']:.3f}  "
                  f"{sm['avg_seconds']:.2f}s/题")
            print(f"     按题型：{sm['by_type']}")
            print(f"     按跳数：{sm['by_hop']}")

    # 落盘
    report = {"testset": str(args.set), "top_k": args.top_k,
              "corpus": {"chunks": len(kb.chunks),
                         "entities": gst["entities"], "edges": gst["edges"]},
              "rows": all_rows}
    out = s.reports_dir / "eval_300.json"
    s.ensure_dirs()
    out.write_text(json.dumps(report, ensure_ascii=False, indent=2),
                   encoding="utf-8")
    print(f"\n报告 → {out}")

    # 失败样例（answerable 但未命中）
    fails = [r for r in all_rows
             if r["mode"] == modes[0][0] and r["answerable"] and not r["hit"]]
    print(f"\n可答题中未命中 {len(fails)} 题，样例：")
    for r in fails[:15]:
        print(f"   [{r['qid']}] {r['query'][:56]}")
    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
