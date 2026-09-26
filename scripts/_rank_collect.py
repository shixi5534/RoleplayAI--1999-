# -*- coding: utf-8 -*-
"""排序实验 · 逐题证据采集（rank_collect）。

为什么需要它：eval300 报告每题只存 hit/rr 等汇总字段，**不存证据列表**，
离线重排（rerank lab）与名次分布诊断无从下手。本脚本把每题 top-K 证据
（chunk_id / score / channels / ppr / reasons）连同名次与 gold 判定一起落盘，
供 ``_rank_rerank_lab.py`` / ``_rank_stats.py`` 离线消费——运行期一次检索，
此后全部实验零检索、零网关。

零网关：本脚本不 import requests/httpx/urllib/openai/socket，不访问任何
云端网关；唯一的网络是项目自带 ``OllamaEmbedder``（本地 Ollama bge-m3，
与 eval300 同一条链路）。

⚠️ ``eval_keywords`` 是**评测专用**字段（gold 答案关键词）：只允许用于
   评测打分与 ORACLE 诊断，**禁止当特征**喂给任何盲（deployable）策略。
   见 ``_rank_rerank_lab.py`` 的 BLIND FEATURE RULE。

口径（逐字对齐 compendium_rag_eval300.score_case）：
  - 命中判定：证据块 ``text + chapter_title + scene_title + part_title``
    拼成的 blob 含任一 gold 关键词；
  - ``rank``：top_k 窗口内第一个含 gold 关键词的证据块名次（1 基；无则 null）；
  - ``hit = rank 非空``，``rr = 1/rank``；
  - ``answerable``：运行期规则 ``any(k in corpus_blob for k in keywords)``，
    corpus_blob = 全部块文本换行拼接（与 eval300 相同，不含篇名）；
  - ``seed_hit``：seeds 名与关键词互为子串（同 eval300）。

补名（--map，可选）：q' = query + " " + " ".join(名字)，名字取
``kb.graph.entities[eid].name``（缺失实体跳过，同 ``_replay_entity_map.py``），
最多取 ``--max-pick``（默认 3，同 ``_iset_eval5.py`` 的 MAX_PICK）。

qvecs：**原始 query**（非 q_used）的嵌入向量，full 模式才采，每 qid 只存一份。
注意：--map 场景下检索内部嵌的是 q_used，这里按约定存原始 query 的向量。

用法（项目根目录）：
  ./.venv/Scripts/python.exe scripts/_rank_collect.py \
      --set data/knowledge/_audit/rag_testset_300_cn.json --tag 300_cn --top-k 20
  冒烟（后台有评测链在跑 Ollama 时务必小步）：
  ./.venv/Scripts/python.exe scripts/_rank_collect.py \
      --set data/knowledge/_audit/rag_testset_300_cn.json --tag smoke_g \
      --modes graph_only --limit 20
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
from compendium_rag.embedder import OllamaEmbedder  # noqa: E402
from compendium_rag_eval300 import Case, flatten_evidence, load_cases  # noqa: E402

DEFAULT_OUT_DIR = ROOT / "data" / "compendium_rag" / "reports"
NOTE_EVAL_KEYWORDS = "eval_keywords 为评测专用（gold 答案关键词），禁止当特征"


def build_map_names(kb, map_path: Path, max_pick: int) -> dict[str, list[str]]:
    """映射档补名：eid → 规范名（同 _replay_entity_map.py），截断到 max_pick。"""
    m = json.loads(map_path.read_text(encoding="utf-8"))["map"]
    out: dict[str, list[str]] = {}
    for qid, eids in m.items():
        names = [kb.graph.entities[e].name for e in eids if e in kb.graph.entities]
        out[qid] = names[:max_pick]
    return out


async def collect_one(kb, case: Case, q_used: str, top_k: int,
                      use_vector: bool) -> dict:
    """单题单模式采集：检索 + 评分（复刻 eval300.score_case）+ 全量证据。"""
    t0 = time.time()
    res = await kb.retrieve(q_used, top_k=top_k, use_vector=use_vector)
    dt = time.time() - t0

    ev = res.get("evidence", [])
    rank = None
    for i, e in enumerate(ev[:top_k], start=1):
        c = kb.retriever.chunks.get(e["chunk_id"])
        if not c:
            continue
        blob = f"{c.text}\n{c.chapter_title}\n{c.scene_title}\n{c.part_title}"
        if any(k in blob for k in case.keywords):
            rank = i
            break

    seed_names = [s["name"] for s in res.get("seeds", [])]
    seed_hits = [k for k in case.keywords
                 if any(k == n or k in n or n in k for n in seed_names)]
    grounded = all(e["chunk_id"] in kb.retriever.chunks for e in ev[:top_k])

    return {
        "qid": case.qid, "query": case.query, "q_used": q_used,
        "answerable": case.dims.get("_answerable"),
        "eval_keywords": case.keywords,
        "rank": rank, "rr": (1.0 / rank) if rank else 0.0,
        "hit": rank is not None,
        "seed_hit": bool(seed_hits), "grounded": grounded,
        "n_evidence": len(ev), "n_edges": len(res.get("edges", [])),
        "seconds": round(dt, 3), "dims": case.dims,
        "evidence": [{"rank": i, "chunk_id": e["chunk_id"],
                      "score": e["score"], "channels": e.get("channels", {}),
                      "ppr": e.get("ppr", 0.0),
                      "reasons": e.get("reasons", [])}
                     for i, e in enumerate(ev[:top_k], start=1)],
    }


def summarize(rows: list[dict], top_k: int) -> dict:
    """由 rank 派生 hit@6 / hit@10 / MRR@6 / MRR@10，分层报告。"""
    def grp(sub: list[dict]) -> dict:
        n = len(sub)
        if not n:
            return {"n": 0}
        ranks = [r["rank"] for r in sub]
        return {
            "n": n,
            "hit6": round(sum(1 for x in ranks if x and x <= 6) / n, 4),
            "hit10": round(sum(1 for x in ranks if x and x <= min(10, top_k)) / n, 4),
            "mrr6": round(sum(1.0 / x for x in ranks if x and x <= 6) / n, 4),
            "mrr10": round(sum(1.0 / x for x in ranks if x and x <= min(10, top_k)) / n, 4),
        }

    out: dict[str, dict] = {}
    for name, sub in (("all", rows),
                      ("answerable", [r for r in rows if r["answerable"]]),
                      ("unanswerable", [r for r in rows if not r["answerable"]])):
        out[name] = grp(sub)
    return out


async def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--set", required=True, help="测试集 json（如 rag_testset_300_cn.json）")
    ap.add_argument("--tag", required=True, help="产物标签（进默认文件名）")
    ap.add_argument("--top-k", type=int, default=20)
    ap.add_argument("--modes", default="full,graph_only")
    ap.add_argument("--map", default="", help="entity_map.json（可选，补名回放）")
    ap.add_argument("--max-pick", type=int, default=3, help="补名最多取几个（默认 3）")
    ap.add_argument("--limit", type=int, default=0, help="只跑前 N 题（调试）")
    ap.add_argument("--out", default="")
    args = ap.parse_args()

    set_path = Path(args.set) if Path(args.set).is_absolute() else ROOT / args.set
    modes = [m.strip() for m in args.modes.split(",") if m.strip()]
    for m in modes:
        if m not in ("full", "graph_only"):
            print(f"[FAIL] 未知模式：{m}")
            return 1

    s = get_settings()
    kb = P.load_kb(s)
    cases = load_cases(set_path)
    if args.limit:
        cases = cases[:args.limit]

    # answerable 运行期判定：与 eval300 完全同一条规则
    corpus_blob = "\n".join(c.text for c in kb.chunks)
    for c in cases:
        c.dims["_answerable"] = any(k in corpus_blob for k in c.keywords)

    map_names: dict[str, list[str]] = {}
    if args.map:
        map_path = Path(args.map) if Path(args.map).is_absolute() else ROOT / args.map
        map_names = build_map_names(kb, map_path, args.max_pick)
        print(f"映射档：{map_path.name}  覆盖题数={sum(1 for v in map_names.values() if v)}")

    out_path = (Path(args.out) if args.out else
                DEFAULT_OUT_DIR / f"rank_collect_{args.tag}_top{args.top_k}.json")
    if not out_path.is_absolute():
        out_path = ROOT / out_path
    out_path.parent.mkdir(parents=True, exist_ok=True)

    print(f"库：块={len(kb.chunks)} 实体={len(kb.graph.entities)} "
          f"题数={len(cases)}  top_k={args.top_k}  modes={modes}")

    qvecs: dict[str, list[float]] = {}
    rows: list[dict] = []
    t_start = time.time()
    for mode in modes:
        use_vec = (mode == "full")
        emb = None
        if use_vec:
            emb = OllamaEmbedder(s.embed_base_url, s.embed_model, s.embed_timeout)
            await emb.__aenter__()
        try:
            for i, c in enumerate(cases, 1):
                names = map_names.get(c.qid) or []
                q_used = c.query + (" " + " ".join(names) if names else "")
                # qvecs 存原始 query 的嵌入（每 qid 一份，与模式无关）
                if use_vec and c.qid not in qvecs:
                    qvecs[c.qid] = await emb.embed_one(c.query)
                row = await collect_one(kb, c, q_used, args.top_k, use_vec)
                row["mode"] = mode
                rows.append(row)
                if i % 10 == 0 or i == len(cases):
                    print(f"  [{mode}] {i}/{len(cases)} ({time.time()-t_start:.0f}s)",
                          flush=True)
        finally:
            if emb is not None:
                await emb.__aexit__(None, None, None)

    # 一致性自检：rr == 1/rank（rank 非空时）
    bad = [r["qid"] for r in rows
           if r["rank"] is not None and abs(r["rr"] - 1.0 / r["rank"]) > 1e-9]
    summary = {m: summarize([r for r in rows if r["mode"] == m], args.top_k)
               for m in modes}

    gst = {"chunks": len(kb.chunks), "entities": len(kb.graph.entities),
           "edges": len(kb.graph.edges)}
    report = {
        "kind": "rank_collect",
        "notes": [NOTE_EVAL_KEYWORDS,
                  "rank 为 top_k 窗口内第一个 gold 命中块名次（1 基，null=未入窗）",
                  "qvecs 为原始 query（非 q_used）的 bge-m3 嵌入，仅 full 模式采集"],
        "testset": str(set_path), "map": args.map or "",
        "max_pick": args.max_pick if args.map else 0,
        "tag": args.tag, "top_k": args.top_k, "modes": modes,
        "corpus": gst, "n_cases": len(cases),
        "rows": rows,
        "qvecs": qvecs,
        "summary": summary,
    }
    if args.map:
        report["map_names"] = map_names
    out_path.write_text(json.dumps(report, ensure_ascii=False), encoding="utf-8")

    print(f"\n== 分组指标（由 rank 派生）==")
    for m in modes:
        print(f"  ── {m} ──")
        for grp_name in ("all", "answerable", "unanswerable"):
            g = summary[m][grp_name]
            if not g.get("n"):
                continue
            print(f"     {grp_name:14s} n={g['n']:4d}  hit@6={g['hit6']:.4f}  "
                  f"hit@10={g['hit10']:.4f}  MRR@6={g['mrr6']:.4f}  "
                  f"MRR@10={g['mrr10']:.4f}")
    print(f"\n报告 → {out_path}  ({out_path.stat().st_size/1e6:.1f} MB, "
          f"qvecs={len(qvecs)})")
    if bad:
        print(f"[FAIL] rr 与 rank 不自洽 {len(bad)} 行：{bad[:10]}")
        return 1
    print("[PASS] rr == 1/rank 全部自洽")
    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
