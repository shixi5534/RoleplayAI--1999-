# -*- coding: utf-8 -*-
"""补名回放 · 符号通道档：实体名只进 link() 种子通道，向量通道保持原始 query 嵌入。

背景（补名路由的缺口实验）：
  既有结论——把识别出的实体名拼进查询后**整体重嵌**（q'=q+名 → embed(q')）几乎丢光
  收益；而 graph_only 下名字只进符号/链接通道是有效的。本脚本补上缺的实验：
  **full 模式下，名字只进符号/链接通道（link → mention → graph PPR），
  向量通道的嵌入输入保持原始 query q（绝不 embed q'）**。离线回放，不触云端网关；
  唯一模型端点是项目既有的本地 Ollama 嵌入（仅对原始 q 嵌入，full 模式才用）。

逐字复用声明（不重实现）：
  - 评分：逐字复用 scripts/compendium_rag_eval300.py:90-120 的 ``score_case``
    （hit/rr/seed_hit/grounded/n_evidence/n_edges 逻辑一字不改），唯一改动是把
    ``kb.retrieve(case.query, ...)`` 换成本文件的 ``retrieve_split``（符号通道输入
    用 q'，向量通道输入用原始 q）。
  - 检索：``retrieve_split`` 逐行镜像 src/compendium_rag/retriever.py:398-436
    ``GraphRetriever.retrieve``（含 seed_threshold 过滤与 keep-top-2 兜底、
    top_n=max(top_k*4,24)、图谱零命中向量兜底、双调 graph_channel 取 ppr），
    **唯一差异**：``link()`` 的输入是 q' 而非 q。PPR/RRF/link/merge_vector_seeds
    全部直接调用 GraphRetriever 方法（retriever.py:290/314/330/357/368/376）。
  - q' 构造：与 scripts/_replay_entity_map.py:49 / scripts/_iset_eval5.py:139 一致
    （``q + " " + " ".join(names)``，无名字则原样）。
  - 名字解析：native/300_cn 与 scripts/_replay_entity_map.py:105-110 一致
    （eid → kb.graph.entities[e].name，缺者丢弃）；--set i 与
    scripts/_iset_eval5.py:85-88 strong 臂一致（map 值直接当名字，本图 eid=规范名）。
  - McNemar：逐字复用 scripts/_er_report_gates.py:46-52 ``mcnemar_exact``
    （math.comb，无 scipy 依赖）。
  - 分层指标：复用 scripts/_er_report_gates.py:29-43 ``groups`` 口径（n=分母，随行印出）。

档位与闸门：
  --map none          零档自检（验收闸门）：q'=q，两模式必须**逐位**复现
                      eval_{native,300_cn}_after_welds.json 的
                      (hit, rr, seed_hit, grounded, n_evidence, n_edges)。
                      --limit N 时按前 N 题比对（逐题独立，前缀可比）。
                      运行 top_k 与基线 top_k（读基线文件 top_k 字段）不同时，
                      按窗口投影比对（见 zero_check）：三通道字典与 RRF 排序
                      均不依赖检索 top_k，top_n=max(k*4,24) 只截尾——故
                      seed_hit/grounded/n_edges 直比，hit/rr/n_evidence 投影
                      到基线窗口后逐位比对。
  --map <file>        补名回放档（缺省取该 set 的内置 entity_map_{set}.json），
                      报分层指标 + 逐题 up/down + McNemar（hit@k 配对）。

  --collect-mode      额外产出 _rank_collect.py 兼容 JSON（重排实验消费）：
                      {kind, testset, map, top_k, max_pick, modes, rows,
                       qvecs, map_names, summary}，行含 qid/query/q_used/mode/
                       answerable/eval_keywords（评测专用）/rank/rr/hit/
                       seed_hit/grounded/n_evidence/n_edges/seconds/dims/
                       evidence（完整 top-K 列表）。行采集逻辑逐字复用
                      scripts/_rank_collect.py:74-110 collect_one（仅换检索调
                      用为本文件 retrieve_split，评分与 eval300 同口径）。
                      qvecs = 原始 query（非 q_used）嵌入，仅 full 模式，每
                      qid 一份。--out 缺省改为
                      rank_collect_symbol_{set}_top{K}.json（避免覆盖回放档）。

自检范围：--set i 的 eval5_set_i.json 行结构不对齐（top_k=10 的
hit6/hit10/rr@10，无 seed_hit/n_evidence/n_edges），按规格逐位自检仅对
300_cn/native 生效；i 只做 hit6/grounded 的**参考核对**（非闸门，口径不同）。

退出码：0=通过/仅报告；1=零档自检 FAIL（或 collect 行 rr/rank 不自洽）；
2=基线缺失等 pending。
"""
from __future__ import annotations

import argparse
import asyncio
import json
import math
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

from compendium_rag import pipeline as P  # noqa: E402
from compendium_rag.config import get_settings  # noqa: E402
from compendium_rag.embedder import OllamaEmbedder  # noqa: E402
from compendium_rag.retriever import RetrievalResult  # noqa: E402
from compendium_rag_eval300 import Case, load_cases  # noqa: E402

AUDIT = ROOT / "data" / "knowledge" / "_audit"
SETS = {
    "native": AUDIT / "rag_testset_native.json",
    "300_cn": AUDIT / "rag_testset_300_cn.json",
    "i": AUDIT / "rag_testset_i.json",
}
MAPS = {s: ROOT / "data" / "compendium_rag" / f"entity_map_{s}.json"
        for s in SETS}
REP = ROOT / "data" / "compendium_rag" / "reports"
BASE = {
    "native": REP / "eval_native_after_welds.json",
    "300_cn": REP / "eval_300_cn_after_welds.json",
    "i": REP / "eval5_set_i.json",   # 仅参考（empty 臂，top_k=10 口径）
}
CMP_FIELDS = ("hit", "rr", "seed_hit", "grounded", "n_evidence", "n_edges")
NOTE_EVAL_KEYWORDS = "eval_keywords 为评测专用（gold 答案关键词），禁止当特征"


# ── 分离检索：符号通道用 q'，向量通道用原始 q ──

def retrieve_split(retr, q_symbol: str, qvec, ent_hits, *, top_k: int,
                   entity_link_top: int, seed_threshold: float,
                   weights: dict, vector_top: int = 30) -> RetrievalResult:
    """逐行镜像 GraphRetriever.retrieve（retriever.py:398-436）。

    唯一差异：link() 的输入是 q_symbol（q'+名）；向量侧（qvec / ent_hits）全部
    来自原始 q 的嵌入，与基线的向量通道完全同源。参数与调用顺序保持一致。
    """
    res = RetrievalResult(query=q_symbol)
    seeds = retr.link(q_symbol, top_k=entity_link_top)
    if ent_hits:
        seeds = retr.merge_vector_seeds(seeds, ent_hits,
                                        seed_threshold, entity_link_top)
    # 低分种子丢弃（防止向量兜底的噪声实体污染 PPR 种子集）
    seeds = [s for s in seeds if s.score >= seed_threshold] or seeds[:2]
    res.seeds = seeds

    if not seeds:
        res.graph_ok = False
        res.note = "实体链接零命中，图谱通道为空"
    else:
        g_chunks, edges = retr.graph_channel(seeds, damping=0.85, max_iter=50)
        res.edges = edges
        channels = {
            "graph": g_chunks,
            "mention": retr.mention_channel(seeds),
        }
        if qvec is not None:
            channels["vector"] = retr.vector_channel(qvec, vector_top)
        evs = retr.rrf_fuse(channels, weights=weights, top_n=max(top_k * 4, 24))
        ppr_map, _ = retr.graph_channel(seeds)
        for e in evs:
            e.ppr = ppr_map.get(e.chunk_id, 0.0)
        res.evidence = evs
    if not res.evidence and qvec is not None:
        # 图谱零命中时的向量兜底，保证不空手而归
        v = retr.vector_channel(qvec, vector_top)
        res.evidence = retr.rrf_fuse({"vector": v}, top_n=top_k)
        res.note = (res.note + "；" if res.note else "") + "图谱零命中，回落向量通道"
    return res


async def score_case_split(kb, case: Case, q_raw: str, top_k: int,
                           use_vector: bool, emb) -> dict:
    """逐字复用 compendium_rag_eval300.score_case（:90-120），仅换检索调用。

    case.query 已是 q'（符号通道输入）；q_raw 是原始 query——向量通道**唯一**
    的嵌入输入，绝不嵌入 q'。graph_only（use_vector=False）零嵌入。
    """
    t0 = time.time()
    s = kb.settings
    qvec = None
    ent_hits = None
    if use_vector:
        try:
            if emb is None:
                raise RuntimeError("full 模式需要本地嵌入器")
            qvec = await emb.embed_one(q_raw)   # ← 只嵌原始 q，绝不嵌 q'
            if kb.entity_index is not None:
                ent_hits = kb.entity_index.search(qvec, s.entity_link_top)
        except Exception as exc:  # noqa: BLE001
            print(f"  [embed] {case.qid} 嵌入不可用，退化为纯符号检索：{exc}",
                  flush=True)
            qvec = None
            ent_hits = None
    res = retrieve_split(
        kb.retriever, case.query, qvec, ent_hits,
        top_k=top_k, entity_link_top=s.entity_link_top,
        seed_threshold=s.seed_score_threshold,
        weights={"graph": s.graph_weight, "mention": 1.0,
                 "vector": s.vector_weight}).to_dict()
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

    seed_names = [sn["name"] for sn in res.get("seeds", [])]
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


async def collect_one_split(kb, case: Case, q_raw: str, q_used: str,
                            top_k: int, use_vector: bool, emb):
    """逐字复用 scripts/_rank_collect.py:74-110 ``collect_one``（行结构、rank/rr/
    hit/seed_hit/grounded/n_evidence/n_edges/evidence 全部同构），唯一改动是把
    ``kb.retrieve(q_used, ...)`` 换成 ``retrieve_split``（符号通道输入 q_used，
    向量通道输入原始 q_raw 的嵌入）。

    返回 (row, qvec)：qvec 为原始 query 的嵌入（仅 full 模式），供顶层 qvecs
    复用——_rank_collect 是检索内外各嵌一次同文本；此处嵌一次共用（确定性同向量）。
    """
    t0 = time.time()
    s = kb.settings
    qvec = None
    ent_hits = None
    if use_vector:
        try:
            if emb is None:
                raise RuntimeError("full 模式需要本地嵌入器")
            qvec = await emb.embed_one(q_raw)   # ← 原始 query，绝非 q_used
            if kb.entity_index is not None:
                ent_hits = kb.entity_index.search(qvec, s.entity_link_top)
        except Exception as exc:  # noqa: BLE001
            print(f"  [embed] {case.qid} 嵌入不可用，退化为纯符号检索：{exc}",
                  flush=True)
            qvec = None
            ent_hits = None
    res = retrieve_split(
        kb.retriever, q_used, qvec, ent_hits,
        top_k=top_k, entity_link_top=s.entity_link_top,
        seed_threshold=s.seed_score_threshold,
        weights={"graph": s.graph_weight, "mention": 1.0,
                 "vector": s.vector_weight}).to_dict()
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

    seed_names = [sn["name"] for sn in res.get("seeds", [])]
    seed_hits = [k for k in case.keywords
                 if any(k == n or k in n or n in k for n in seed_names)]
    grounded = all(e["chunk_id"] in kb.retriever.chunks for e in ev[:top_k])

    row = {
        "qid": case.qid, "query": q_raw, "q_used": q_used,
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
    return row, qvec


def replay_row_from_collect(crow: dict, case: Case, n_names: int, mode: str) -> dict:
    """由 collect 行派生回放档行（闸门/分层用）：hit/rr/n_evidence 等语义与
    score_case 完全一致（同为 top_k 窗口内首个 gold 命中）。"""
    return {"qid": crow["qid"], "query": crow["q_used"],  # 回放档 rows.query 语义 = q'
            "hit": crow["hit"], "rr": crow["rr"],
            "seed_hit": crow["seed_hit"], "grounded": crow["grounded"],
            "n_evidence": crow["n_evidence"], "n_edges": crow["n_edges"],
            "seconds": crow["seconds"], "dims": crow["dims"],
            "cn_keyword": case.is_cn_keyword,
            "mode": mode, "answerable": crow["answerable"],
            "n_names": n_names}


def summarize_by_rank(rows: list[dict], top_k: int) -> dict:
    """逐字复用 scripts/_rank_collect.py:114-134 ``summarize``（由 rank 派生
    hit6/hit10/MRR@6/MRR@10，分层 all/answerable/unanswerable）。"""
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


async def run(kb, cases, names_by_qid, top_k, modes, emb, collect=False):
    """与 _replay_entity_map.run 同构：answerable 口径 + 逐题 q' 构造。

    collect=False：逐题调 score_case_split（回放档行）。
    collect=True：逐题调 collect_one_split（rank_collect 档行），并派生回放档行
    供既有闸门/分层复用（同一次检索，不重复跑）；qvecs 存原始 query 嵌入。
    """
    rows, collect_rows, qvecs = [], [], {}
    corpus_blob = "\n".join(c.text for c in kb.chunks)
    for c in cases:
        c.dims["_answerable"] = any(k in corpus_blob for k in c.keywords)
    for mode in modes:
        use_vec = (mode == "full")
        t0 = time.time()
        for i, c in enumerate(cases, 1):
            extra = names_by_qid.get(c.qid) or []
            q_used = c.query + (" " + " ".join(extra) if extra else "")
            if collect:
                crow, qvec = await collect_one_split(
                    kb, c, c.query, q_used, top_k, use_vec, emb)
                crow["mode"] = mode
                collect_rows.append(crow)
                if use_vec and qvec is not None and c.qid not in qvecs:
                    qvecs[c.qid] = qvec      # 原始 query 嵌入，每 qid 一份
                r = replay_row_from_collect(crow, c, len(extra), mode)
            else:
                r = await score_case_split(
                    kb, Case(qid=c.qid, query=q_used, keywords=c.keywords,
                             dims=c.dims, ref=c.ref),
                    c.query, top_k, use_vec, emb)
                r["mode"] = mode
                r["answerable"] = c.dims["_answerable"]
                r["n_names"] = len(extra)
            rows.append(r)
            if i % 50 == 0:
                print(f"  [{mode}] {i}/{len(cases)} ({time.time()-t0:.0f}s)",
                      flush=True)
        print(f"  [{mode}] 完成 {len(cases)}/{len(cases)} "
              f"({time.time()-t0:.0f}s)", flush=True)
    return rows, collect_rows, qvecs


# ── 基线 / 自检 / 对照 ──

def load_baseline(set_name: str):
    """返回 (base_rows, 基线 hit 字段名, 标签, 基线 top_k)。i 的基线取 eval5 empty 臂。"""
    p = BASE[set_name]
    obj = json.loads(p.read_text(encoding="utf-8"))
    if set_name == "i":
        rows = []
        for mode, mode_rows in obj["rows"]["empty"].items():
            rows.extend({**r, "mode": mode} for r in mode_rows)
        return rows, "hit6", f"{p.name}:empty 臂", obj.get("top_k", 10)
    return obj["rows"], "hit", p.name, obj.get("top_k", 6)


def mcnemar_exact(b: int, c: int) -> float:
    """逐字复用 scripts/_er_report_gates.py:46-52（math.comb，无 scipy）。"""
    n = b + c
    if n == 0:
        return 1.0
    k = min(b, c)
    tail = sum(math.comb(n, i) for i in range(k + 1)) / (2 ** n)
    return min(1.0, 2 * tail)


def groups(rows, mode, hit_field="hit", ans_by_qid=None):
    """复用 _er_report_gates.groups 口径（:29-43），n=分母。"""
    sub = [r for r in rows if r.get("mode") == mode]

    def _ans(r):
        if "answerable" in r:
            return bool(r["answerable"])
        return bool((ans_by_qid or {}).get(r["qid"]))

    out = {}
    for name, ss in (("all", sub),
                     ("answerable", [r for r in sub if _ans(r)]),
                     ("unanswerable", [r for r in sub if not _ans(r)])):
        n = len(ss)
        out[name] = {
            "n": n,
            "hit": round(sum(1 for r in ss if r[hit_field]) / n, 4) if n else None,
            "mrr": round(sum(r["rr"] for r in ss) / n, 4) if n else None,
            "grounded_all": bool(ss) and all(r["grounded"] for r in ss),
            "grounded_rate": round(sum(1 for r in ss if r["grounded"]) / n, 4)
            if n else None,
        }
    return out


def print_strata(rows, title, hit_field="hit", ans_by_qid=None):
    print(f"\n== {title} ==")
    out = {}
    for mode in ("full", "graph_only"):
        if not any(r.get("mode") == mode for r in rows):
            continue
        g = groups(rows, mode, hit_field, ans_by_qid)
        out[mode] = g
        print(f"  ── {mode} ──")
        for name, sm in g.items():
            if sm["n"]:
                print(f"  {name:14s} n={sm['n']}  hit@k={sm['hit']}  "
                      f"MRR={sm['mrr']}  grounded={sm['grounded_rate']}")
    return out


def zero_check(rows, base_rows, label, run_top_k=0, base_top_k=0):
    """零档自检：CMP_FIELDS 逐位比对（--limit 时为前缀比对）。

    运行 top_k 与基线 top_k 不同时改按**窗口投影**比对（仍逐位）：
      - 通道字典（graph/mention 种子、vector_top=30）与 RRF 排序都不依赖检索
        top_k，top_n=max(k*4,24) 只截尾 → 两个 top_k 的证据序列互为前缀；
      - seed_hit/grounded/n_edges 为窗口不变量，直比；
      - hit/rr 投影：首个 gold 名次唯一，run rank ≤ base_k 才算入基线窗口；
      - n_evidence 投影 = min(run 池大小, max(base_k*4,24))。
    """
    projected = bool(run_top_k and base_top_k and run_top_k != base_top_k)
    bkey = {(r["qid"], r["mode"]): r for r in base_rows}
    diffs, aligned = [], 0
    for r in rows:
        b = bkey.get((r["qid"], r["mode"]))
        if b is None:
            diffs.append((r["qid"], r["mode"], "missing_in_baseline"))
            continue
        aligned += 1
        if not projected:
            for f in CMP_FIELDS:
                if r[f] != b[f]:
                    diffs.append((r["qid"], r["mode"], f, b[f], r[f]))
                    break
        else:
            proj_rank = (r["rank"] if r.get("rank") is not None
                         and r["rank"] <= base_top_k else None)
            proj = {"hit": proj_rank is not None,
                    "rr": (1.0 / proj_rank) if proj_rank else 0.0,
                    "n_evidence": min(r["n_evidence"], max(base_top_k * 4, 24))}
            for f in ("seed_hit", "grounded", "n_edges", "hit", "rr",
                      "n_evidence"):
                v = proj[f] if f in proj else r[f]
                if v != b[f]:
                    diffs.append((r["qid"], r["mode"], f, b[f], v))
                    break
    ok = not diffs and aligned == len(rows)
    print(f"\n== 零档自检 vs {label} ==")
    if projected:
        print(f"  口径：运行 top_k={run_top_k} → 投影到基线 top_k={base_top_k}"
              f"（窗口不变量直比 + hit/rr/n_evidence 投影，逐位）")
    print(f"  {'BITWISE PASS' if ok else 'BITWISE FAIL'}: rows={len(rows)} "
          f"对齐={aligned} 差异={len(diffs)}  "
          f"cmp={','.join(CMP_FIELDS)}（逐位）")
    for d in diffs[:20]:
        print("  DIFF", d)
    detail = [{"qid": d[0], "mode": d[1], "field": d[2],
               "base": str(d[3]) if len(d) > 3 else "",
               "new": str(d[4]) if len(d) > 4 else ""} for d in diffs[:50]]
    return ok, {"verdict": "BITWISE PASS" if ok else "BITWISE FAIL",
                "rows": len(rows), "aligned": aligned, "diffs": len(diffs),
                "cmp_fields": list(CMP_FIELDS),
                "caliber": ("projected_top%d_to_top%d" % (run_top_k, base_top_k)
                            if projected else "bitwise_same_top_k"),
                "detail": detail}


def soft_check_i(rows, base_rows):
    """--set i 零档参考核对（非闸门）：eval5 行结构不对齐（top_k=10、hit6/hit10、
    无 seed_hit/n_evidence/n_edges），按规格逐位自检仅对 300_cn/native 生效。"""
    bkey = {(r["qid"], r["mode"]): r for r in base_rows}
    tot = agree_h = agree_g = 0
    mism = []
    for r in rows:
        b = bkey.get((r["qid"], r["mode"]))
        if b is None:
            continue
        tot += 1
        if bool(r["hit"]) == bool(b.get("hit6")):
            agree_h += 1
        else:
            mism.append((r["qid"], r["mode"], "hit6", b.get("hit6"), r["hit"]))
        if bool(r["grounded"]) == bool(b.get("grounded")):
            agree_g += 1
    print(f"\n== 零档参考核对 vs eval5_set_i.json:empty（非闸门，top_k 口径不同）==")
    print(f"  hit6 一致 {agree_h}/{tot}  grounded 一致 {agree_g}/{tot}")
    for d in mism[:10]:
        print("  DIFF", d)
    return {"hit_agree": agree_h, "grounded_agree": agree_g, "total": tot,
            "note": "eval5 行结构不对齐（top_k=10/hit6/hit10），逐位自检不适用"}


def pair_vs_baseline(rows, base_rows, hit_field, ans_by_qid, pair_window=0):
    """逐题配对（(qid,mode)）：up/down + 每模式 McNemar（hit@k）。

    pair_window>0 时，新侧 hit 按基线窗口投影（行须带 rank，collect 模式）：
    run top_k 与基线 top_k 不同时，直接比 run 窗口 hit 会把"gold 块在窗口外"
    的窗口伪影误计成 up/down（如 rank=24 > 6）。
    """
    bkey = {(str(r["qid"]), r.get("mode", "")): r for r in base_rows}
    per_mode, ups, downs, missing = {}, [], [], []
    for mode in ("full", "graph_only"):
        b_ = c_ = 0
        mu, md = [], []
        for r in rows:
            if r["mode"] != mode:
                continue
            b = bkey.get((r["qid"], mode))
            if b is None or hit_field not in b:
                missing.append((mode, r["qid"]))
                continue
            if pair_window and r.get("rank") is not None:
                nh = r["rank"] <= pair_window
            else:
                nh = bool(r["hit"])
            bh = bool(b[hit_field])
            if nh and not bh:
                mu.append(r["qid"])
            elif not nh and bh:
                md.append(r["qid"])
        b_, c_ = len(mu), len(md)
        per_mode[mode] = {"up": sorted(mu), "down": sorted(md), "b": b_,
                          "c": c_, "p": round(mcnemar_exact(b_, c_), 6)}
        ups.extend(mu)
        downs.extend(md)
    ups, downs = sorted(set(ups)), sorted(set(downs))
    return ups, downs, per_mode, missing


async def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--set", choices=sorted(SETS), required=True)
    ap.add_argument("--map", default="",
                    help="映射 json 或 none（零档自检）；缺省=内置 entity_map_<set>.json")
    ap.add_argument("--top-k", type=int, default=6)
    ap.add_argument("--modes", default="full,graph_only")
    ap.add_argument("--max-pick", type=int, default=3)
    ap.add_argument("--limit", type=int, default=0, help="只跑前 N 题（调试）")
    ap.add_argument("--collect-mode", action="store_true",
                    help="额外产出 _rank_collect.py 兼容 JSON（重排实验消费）")
    ap.add_argument("--out", default="")
    args = ap.parse_args()

    modes = [m for m in args.modes.split(",") if m]
    bad = [m for m in modes if m not in ("full", "graph_only")]
    if bad:
        print(f"未知 --modes：{bad}（可选 full,graph_only）", file=sys.stderr)
        return 2
    map_arg = args.map or str(MAPS[args.set])
    if args.out:
        out_path = Path(args.out)
    elif args.collect_mode:
        out_path = REP / f"rank_collect_symbol_{args.set}_top{args.top_k}.json"
    else:
        out_path = REP / f"replay_symbol_{args.set}_k{args.top_k}.json"

    kb = P.load_kb(get_settings())
    cases = load_cases(SETS[args.set])
    if args.limit:
        cases = cases[:args.limit]

    names_by_qid: dict[str, list[str]] = {}
    map_names_json: dict[str, list[str]] = {}
    if map_arg != "none":
        m = json.loads(Path(map_arg).read_text(encoding="utf-8"))["map"]
        # collect 兼容产物的 map_names 用 _rank_collect.build_map_names 口径（:64-71）
        for qid, eids in m.items():
            map_names_json[qid] = [kb.graph.entities[e].name for e in eids
                                   if e in kb.graph.entities][:args.max_pick]
        if args.set == "i":
            # 与 _iset_eval5.py:85-88 strong 臂一致：map 值直接当名字
            for c in cases:
                names_by_qid[c.qid] = list(m.get(c.qid, []))[:args.max_pick]
        else:
            # 与 _replay_entity_map.py:105-110 一致：eid→实体名，缺者丢弃
            for qid, eids in m.items():
                names_by_qid[qid] = [kb.graph.entities[e].name for e in eids
                                     if e in kb.graph.entities][:args.max_pick]
    n_cov = sum(1 for c in cases if names_by_qid.get(c.qid))
    print(f"set={args.set} n={len(cases)} top_k={args.top_k} "
          f"max_pick={args.max_pick} modes={modes} 映射覆盖题数={n_cov} "
          f"map={'none' if map_arg == 'none' else Path(map_arg).name} "
          f"collect={'on' if args.collect_mode else 'off'}")

    rows, collect_rows, qvecs = [], [], {}
    if "full" in modes:
        s = kb.settings
        async with OllamaEmbedder(s.embed_base_url, s.embed_model,
                                  s.embed_timeout) as emb:
            rows, collect_rows, qvecs = await run(
                kb, cases, names_by_qid, args.top_k, modes, emb,
                collect=args.collect_mode)
    else:
        rows, collect_rows, qvecs = await run(
            kb, cases, names_by_qid, args.top_k, modes, None,
            collect=args.collect_mode)

    ans_by_qid = {c.qid: c.dims.get("_answerable", False) for c in cases}
    result = {"set": args.set,
              "map": "none" if map_arg == "none" else str(Path(map_arg)),
              "top_k": args.top_k, "max_pick": args.max_pick,
              "modes": modes, "n_cases": len(cases), "rows": rows}

    if not BASE[args.set].exists():
        print(f"\n基线缺失：{BASE[args.set]} → pending（跳过自检/对照）")
        result["selfcheck"] = {"verdict": "pending"}
        if args.collect_mode:
            result["rows"] = []
            _write_collect(out_path, kb, args, SETS, map_arg, modes,
                           collect_rows, qvecs, map_names_json, result, cases)
        else:
            out_path.write_text(json.dumps(result, ensure_ascii=False, indent=1),
                                encoding="utf-8")
        print(f"报告 → {out_path}")
        return 2

    base_rows, bfield, blabel, base_top_k = load_baseline(args.set)
    result["baseline"] = {"path": str(BASE[args.set]), "hit_field": bfield,
                          "label": blabel, "top_k": base_top_k}

    # 闸门/对照的比对行：collect 模式用 collect 行（带 rank，供投影）；回放档用回放行
    gate_rows = collect_rows if args.collect_mode else rows
    if map_arg == "none":
        if args.set == "i":
            result["selfcheck"] = soft_check_i(gate_rows, base_rows)
        else:
            ok, sc = zero_check(gate_rows, base_rows, blabel,
                                run_top_k=args.top_k, base_top_k=base_top_k)
            result["selfcheck"] = sc
        print_strata(rows, f"零档自检 分组指标（hit@{args.top_k} 窗口，分母 n 随行）",
                     "hit", ans_by_qid)
        print_strata(base_rows, f"基线 {blabel} 分组指标（top_k={base_top_k}，参考）",
                     bfield, ans_by_qid)
    else:
        # 跨窗口时按基线窗口投影配对（collect 行带 rank；set i 基线为参考口径，不投影）
        cross = args.collect_mode and args.set != "i" and args.top_k != base_top_k
        pair_k = base_top_k if cross else 0
        ups, downs, per_mode, missing = pair_vs_baseline(
            gate_rows, base_rows, bfield, ans_by_qid, pair_window=pair_k)
        result["up"], result["down"] = ups, downs
        result["up_by_mode"] = {m: v["up"] for m, v in per_mode.items()}
        result["down_by_mode"] = {m: v["down"] for m, v in per_mode.items()}
        result["mcnemar"] = per_mode
        affected = {q for q, v in names_by_qid.items() if v}
        result["affected_qids"] = len(affected)
        g_new = print_strata(rows, f"回放档 分组指标（hit@{args.top_k} 窗口，分母 n 随行）",
                             "hit", ans_by_qid)
        g_old = print_strata(base_rows, f"基线 {blabel} 分组指标（top_k={base_top_k}，参考）",
                             bfield, ans_by_qid)
        result["new"], result["old"] = g_new, g_old
        for mode, v in per_mode.items():
            if not v["up"] and not v["down"] and not missing:
                continue
            aff_up = [q for q in v["up"] if q in affected]
            aff_dn = [q for q in v["down"] if q in affected]
            if pair_k:
                print(f"\n== {mode} vs {blabel}（hit@{pair_k} 基线窗口投影配对："
                      f"run top_k={args.top_k}≠基线 top_k={base_top_k}，"
                      f"新侧 hit 已投影，窗口伪影不计）==")
            else:
                print(f"\n== {mode} vs {blabel}（hit@k 配对）==")
            print(f"  up={len(v['up'])} {v['up']}")
            print(f"  down={len(v['down'])} {v['down']}")
            if missing:
                print(f"  缺基线行（无法配对）：{sorted(set(missing))}")
            print(f"  归因：映射覆盖题 {len(affected)}；up 中被覆盖 "
                  f"{len(aff_up)}、down 中被覆盖 {len(aff_dn)}")
            print(f"  McNemar b={v['b']} c={v['c']} p={v['p']:.5f}")
            if args.set == "i":
                print("  注：基线为 eval5 empty 臂（top_k=10 口径），仅参考。")
        if not any(v["up"] or v["down"] for v in per_mode.values()) and not missing:
            print(f"\n== vs {blabel}：两模式 hit@k 零翻转 ==")
            print(json.dumps(per_mode, ensure_ascii=False, indent=1))

    if args.collect_mode:
        _write_collect(out_path, kb, args, SETS, map_arg, modes, collect_rows,
                       qvecs, map_names_json, result, cases)
    else:
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(json.dumps(result, ensure_ascii=False, indent=1),
                            encoding="utf-8")
        print(f"\n报告 → {out_path}")

    if map_arg == "none":
        if args.set == "i":
            return 0  # 参考核对不设闸门（规格：结构不齐 → 逐位自检仅限 300_cn/native）
        return 0 if result["selfcheck"].get("verdict") == "BITWISE PASS" else 1
    return 0


def _write_collect(out_path, kb, args, SETS, map_arg, modes, collect_rows,
                   qvecs, map_names_json, result, cases) -> None:
    """落盘 _rank_collect.py 兼容 JSON（顶层键序对齐规格）+ 回放闸门摘要子键。"""
    bad_rr = [r["qid"] for r in collect_rows
              if r["rank"] is not None and abs(r["rr"] - 1.0 / r["rank"]) > 1e-9]
    rs = {k: v for k, v in result.items() if k != "rows"}
    if bad_rr:
        rs["selfcheck"] = {**rs.get("selfcheck", {}), "rr_rank_consistency": "FAIL"}
    collect_summary = {m: summarize_by_rank(
        [r for r in collect_rows if r["mode"] == m], args.top_k) for m in modes}
    report = {
        "kind": "rank_collect",
        "notes": [NOTE_EVAL_KEYWORDS,
                  "rank 为 top_k 窗口内第一个 gold 命中块名次（1 基，null=未入窗）",
                  "qvecs 为原始 query（非 q_used）的 bge-m3 嵌入，仅 full 模式采集",
                  "检索引擎=_replay_symbol_channel.retrieve_split：补名只进符号/链接"
                  "通道（link→mention→graph PPR），向量通道嵌原始 query"
                  "（_rank_collect 走 kb.retrieve 会把 q_used 整体重嵌）"],
        "testset": str(SETS[args.set]),
        "map": "" if map_arg == "none" else str(Path(map_arg)),
        "top_k": args.top_k,
        "max_pick": args.max_pick if map_arg != "none" else 0,
        "modes": modes,
        "rows": collect_rows,
        "qvecs": qvecs,
        "map_names": map_names_json,
        "summary": collect_summary,
        "tag": f"symbol_{args.set}",
        "corpus": {"chunks": len(kb.chunks), "entities": len(kb.graph.entities),
                   "edges": len(kb.graph.edges)},
        "n_cases": len(cases),
        "rr_rank_consistency": "PASS" if not bad_rr else "FAIL",
        "replay_summary": rs,
    }
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(report, ensure_ascii=False), encoding="utf-8")

    print(f"\n== 分组指标（由 rank 派生，_rank_collect 口径）==")
    for m in modes:
        print(f"  ── {m} ──")
        for grp_name in ("all", "answerable", "unanswerable"):
            g = collect_summary[m][grp_name]
            if not g.get("n"):
                continue
            print(f"     {grp_name:14s} n={g['n']:4d}  hit@6={g['hit6']:.4f}  "
                  f"hit@10={g['hit10']:.4f}  MRR@6={g['mrr6']:.4f}  "
                  f"MRR@10={g['mrr10']:.4f}")
    print(f"\n报告 → {out_path}  ({out_path.stat().st_size/1e6:.1f} MB, "
          f"qvecs={len(qvecs)}, map_names={len(map_names_json)})")
    if bad_rr:
        print(f"[FAIL] rr 与 rank 不自洽 {len(bad_rr)} 行：{bad_rr[:10]}")
        return
    print("[PASS] rr == 1/rank 全部自洽")


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
