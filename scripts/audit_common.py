# -*- coding: utf-8 -*-
"""四层审查公共库 —— 冻结口径、判分函数、图 BFS 工具、报告 schema。

纪律（写死，任何 audit_* 脚本不得绕过）：
1. 只读审查：本库不提供任何写图/调参入口；对抗注入只能在
   ``GraphStore.from_dict`` 的内存副本上做。
2. v8 冻结口径：``CMPRAG_LEX_WEIGHT=1.0 / CMPRAG_RRF_K=1 / CMPRAG_LEX_FIRST=0``，
   由 :func:`apply_v8_env` 在 import compendium config 之前注入
   （config 默认值 0.0/60 ≠ 生产值，直接跑就口径漂移）。
3. 判分口径逐字复制 ``scripts/compendium_rag_eval300.py``：
   ref+evidence 并集关键词、top-k 证据块 blob（text+chapter+scene+part）子串命中。
4. 每份报告必须回写 ``frozen_graph_sha`` 与 ``retrieval_config`` 快照，
   供 WP6 记分卡对账。
"""
from __future__ import annotations

import hashlib
import json
import os
import sys
from collections import deque
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))
if str(ROOT / "scripts") not in sys.path:
    sys.path.insert(0, str(ROOT / "scripts"))

# ── 冻结锚点 ──
# v8：审查期（WP0–WP6，baseline_v8.json）冻结件，P1 之后已成历史。
V8_GRAPH_SHA16 = "026b41699f021db2"
# v9-P1：谓语受控化就地落盘后的现行件（reports/p1_apply.json 有全量对账）。
V9P1_GRAPH_SHA16 = "7cac5867e8c80879"
# v9-P2 r8：L4.5 修边提案落盘（28 条，边 27151->27135，实体 7033 不变）。
V9P2_GRAPH_SHA16 = "56507b18ac2113b6"
# v9-P3 r9：L4.5 二次盲评确认的 18 条纯 delete_edge 落盘（边 27135->27117，实体 7033 不变）。
V9P3_GRAPH_SHA16 = "329671bba0988c68"
# v9-P4 r10：L4.5 三轮盲评交叉确认的 6 条纯 delete_edge 落盘（边 27117->27111，实体 7033 不变）。
# R10-L45-007（Z-[告知]->安洁）按「原文成立、仅 evidence 句错引」判 keep_with_note，未删。
V9P4_GRAPH_SHA16 = "fb7322dd4f558e7c"
# v9-P5 r11：L4.4 正典裁决修边落盘（1 条 delete_edge：集体潜意识-[包含]->迷思海，
# 边 27111->27110，实体 7033 不变）。依据 = 用户 2026-10-10 裁决「批准删除」
# （P7 全量复审报告 §9 待裁决第④条）；提案 data/compendium_rag/repairs_v10/proposal.json，
# 取证 chunk activity__35101_绿松石蛇俱乐部:17.1.1 全文无「包含」。
V9P5_GRAPH_SHA16 = "911bb538160db80e"
# 现行审查锚点。**v8/v9 不得混用**：拿旧图跑新闸门、或拿新图对旧基线，
# 都会把「图谱变了」误读成「检索/生成变了」。要比 v8 就显式传 expect=V8_GRAPH_SHA16。
# 注意：P4–P7 四份验收报告与 2026-10-10 记分卡绑的是 V9P4（fb7322dd…），
# 它们记录的是 r11 落盘前的图状态，属历史，不得与 r11 之后的读数混表。
FROZEN_GRAPH_SHA16 = V9P5_GRAPH_SHA16
V8_RETRIEVAL_ENV = {
    "CMPRAG_LEX_WEIGHT": "1.0",
    "CMPRAG_RRF_K": "1",
    "CMPRAG_LEX_FIRST": "0",
}
# v8 裸检索三主数（full 模式，top_k=6，hit@6）—— WP0 环境自检对账用
V8_SELFCHECK = {
    "300cn": {"artifact": "eval_300cn_k1.json", "tier": "answerable",
              "hits": 167, "n": 196, "rate": 0.852},
    "blind206": {"artifact": "eval_blind_k1.json", "tier": "all",
                 "hits": 184, "n": 206, "rate": 0.8932},
    "gen120": {"artifact": "eval_gen120_k1.json", "tier": "all",
               "hits": 118, "n": 120, "rate": 0.9833},
}
V8_SAFETY = {"hits": 1, "n": 104}  # unanswerable 安全线
V8_TOP_K = 6


def apply_v8_env() -> None:
    """强制 v8 冻结检索口径（进程环境变量优先于 .env）。

    必须在 ``from compendium_rag.config import get_settings`` **首次调用前**执行
    （Settings 字段是 default_factory 读 env，且 get_settings 有 lru_cache）。
    """
    for k, v in V8_RETRIEVAL_ENV.items():
        os.environ[k] = v
    os.environ.setdefault("PYTHONHASHSEED", "0")


def sha16_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for blk in iter(lambda: f.read(1 << 20), b""):
            h.update(blk)
    return h.hexdigest()[:16]


def config_snapshot(s) -> dict:
    """检索相关 config 快照（回写进每份报告，口径漂移即可见）。"""
    return {
        "lex_weight": s.lex_weight, "lex_top": s.lex_top,
        "lex_first": s.lex_first, "rrf_k": s.rrf_k,
        "top_k": s.top_k, "ppr_damping": s.ppr_damping,
        "graph_weight": s.graph_weight, "vector_weight": s.vector_weight,
        "entity_link_top": s.entity_link_top,
        "seed_score_threshold": s.seed_score_threshold,
        "llm_model": s.llm_model, "embed_model": s.embed_model,
        "pythonhashseed": os.environ.get("PYTHONHASHSEED", ""),
    }


# ── 判分口径（逐字复制 compendium_rag_eval300，勿改）──

def eval300_module():
    """返回判分母本模块（load_cases/Case/score_case/summarize）。"""
    import compendium_rag_eval300 as E300  # noqa: PLC0415
    return E300


def blob_of(chunk) -> str:
    return f"{chunk.text}\n{chunk.chapter_title}\n{chunk.scene_title}\n{chunk.part_title}"


# ── 排序指标（WP2 用；二元相关）──

def recall_at_k(ranked_relevant: list[bool], n_relevant: int) -> float:
    """集合级 Recall@k = |Top-k ∩ R_q| / |R_q|。"""
    if n_relevant <= 0:
        return 0.0
    return sum(1 for r in ranked_relevant if r) / n_relevant


def mrr_at_k(ranked_relevant: list[bool]) -> float:
    for i, r in enumerate(ranked_relevant, start=1):
        if r:
            return 1.0 / i
    return 0.0


def ndcg_at_k(ranked_relevant: list[bool], n_relevant: int) -> float:
    """二元相关 NDCG@k：IDCG 按 min(|R_q|, k) 截断。"""
    import math
    k = len(ranked_relevant)
    dcg = sum(1.0 / math.log2(i + 1)
              for i, r in enumerate(ranked_relevant, start=1) if r)
    ideal_n = min(n_relevant, k)
    if ideal_n <= 0:
        return 0.0
    idcg = sum(1.0 / math.log2(i + 1) for i in range(1, ideal_n + 1))
    return dcg / idcg


# ── 纯 dict 图 BFS 工具（compendium 图零 networkx）──

def build_adjacency(graph) -> dict[str, set[str]]:
    """无向邻接表（eid -> 邻居集合），含全部实体（孤立点为空集）。"""
    adj: dict[str, set[str]] = {eid: set() for eid in graph.entities}
    for e in graph.edges:
        if e.src in adj and e.dst in adj:
            adj[e.src].add(e.dst)
            adj[e.dst].add(e.src)
    return adj


def degrees(adj: dict[str, set[str]]) -> dict[str, int]:
    return {n: len(nb) for n, nb in adj.items()}


def connected_components(adj: dict[str, set[str]]) -> list[set[str]]:
    seen: set[str] = set()
    comps: list[set[str]] = []
    for start in adj:
        if start in seen:
            continue
        comp: set[str] = set()
        q = deque([start])
        seen.add(start)
        while q:
            n = q.popleft()
            comp.add(n)
            for m in adj[n]:
                if m not in seen:
                    seen.add(m)
                    q.append(m)
        comps.append(comp)
    return comps


def largest_cc_ratio(adj: dict[str, set[str]]) -> float:
    if not adj:
        return 0.0
    comps = connected_components(adj)
    return max(len(c) for c in comps) / len(adj)


def induced_subgraph(adj: dict[str, set[str]], nodes: set[str]) -> dict[str, set[str]]:
    return {n: adj.get(n, set()) & nodes for n in nodes}


def subgraph_connectivity(adj: dict[str, set[str]], nodes: set[str]) -> float:
    """诱导子图最大连通分量占节点数比例。"""
    if not nodes:
        return 0.0
    sub = induced_subgraph(adj, nodes)
    comps = connected_components(sub)
    return max(len(c) for c in comps) / len(nodes)


# ── 报告 schema ──

def gate_verdict(name: str, target: str, actual, verdict: str,
                 reason: str = "", root_cause_bucket: str = "") -> dict:
    assert verdict in ("PASS", "FAIL", "N/A")
    return {"gate": name, "target": target, "actual": actual,
            "verdict": verdict, "reason": reason,
            "root_cause_bucket": root_cause_bucket}


def new_report(wp: str, settings=None, extra: dict | None = None) -> dict:
    rep = {
        "schema": "compendium_rag.audit/v1",
        "wp": wp,
        "frozen_graph_sha": "",
        "retrieval_config": {},
        "metrics": {},
        "gate_verdicts": [],
        "per_case": [],
        "artifacts": [],
    }
    if settings is not None:
        gp = settings.graph_path
        if gp.exists():
            rep["frozen_graph_sha"] = sha16_file(gp)
        rep["retrieval_config"] = config_snapshot(settings)
    if extra:
        rep.update(extra)
    return rep


def assert_frozen_graph(rep: dict, expect: str | None = None) -> None:
    """图 SHA 漂移即中止。``expect`` 缺省用现行锚点 :data:`FROZEN_GRAPH_SHA16`。"""
    want = expect or FROZEN_GRAPH_SHA16
    if rep["frozen_graph_sha"] != want:
        raise SystemExit(
            f"[FATAL] 图谱 SHA 漂移：{rep['frozen_graph_sha']} != "
            f"{want}（现行锁）。审查中止，先查明谁改了图。")


def write_report(path: Path, rep: dict) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(rep, ensure_ascii=False, indent=2),
                    encoding="utf-8")
    return path
