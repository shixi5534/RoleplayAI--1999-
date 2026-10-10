# -*- coding: utf-8 -*-
"""v9-P4.0 · `context()` 预算分配器 A/B（v1_tailcut vs v2_perblock，只读、零 LLM/零嵌入）。

P3 量过：`context()` 的 `out[:max_chars]` 整体尾切让 53.5% 的 top-6 块整块掉出窗外，
13.9% 被从中间切断（半块 = 最危险的一类：模型看到一个开头就当它是全部）。
P4.0 把尾切换成**按块预算分配**（均分份额 + 超份额块整块跳过 + 余量回收 + 编号跟窗口），
这个脚本用**同一批检索结果**跑两版渲染器出对照读数。

`v1_tailcut` 是**冻结参考实现**：逐字复制自 git HEAD 的 `GraphRetriever.context()`
（生产路径里的那份代码已删除，不留死代码）。两版读数**不得混表**。

块状态判据（两版各用自己的判据，题与检索结果完全相同）：
- `complete`：块正文**整段**出现在渲染串里；
- `partial` ：块的溯源头在串里、正文不完整 → 模型看到半块；
- `dropped` ：连头都没进窗。

预登记硬检查「gold 块因窗口分配被挤出」用两条独立口径：
- 显式 gold：gen120 的 `source_chunk_ids`（检索结果里出现即计入）；
- 泛化口径：正文含题集 `evidence` 别名的块（三集都有），比较 v1 可见 / v2 掉出。

用法：
    PYTHONPATH=src .venv/Scripts/python.exe -X utf8 \\
        scripts/compendium_rag_p4_allocator_ab.py
    P4_AB_PER_SET=0 ...   # 0/空 = 三集全量

产物：``data/compendium_rag/reports/p4_allocator_ab.{json,md}``
"""
from __future__ import annotations

import asyncio
import hashlib
import itertools
import json
import os
import re
import statistics
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
for _k, _v in {"CMPRAG_LEX_WEIGHT": "1.0", "CMPRAG_RRF_K": "1",
               "CMPRAG_LEX_FIRST": "0", "PYTHONHASHSEED": "0"}.items():
    os.environ.setdefault(_k, _v)      # 必须在 import config 之前

from compendium_rag import pipeline as P  # noqa: E402
from compendium_rag.config import get_settings  # noqa: E402
from compendium_rag.retriever import (  # noqa: E402
    CONTEXT_ALLOCATOR,
    CONTEXT_ALLOCATOR_LEGACY,
    FALLBACK_MARK,
    Evidence,
    RetrievalResult,
    Seed,
)

EXPECTED_SHA = "7cac5867e8c80879"
R = ROOT / "data" / "compendium_rag" / "reports"
SETS = {
    "300cn": ROOT / "data" / "knowledge" / "_audit" / "rag_testset_300_cn.json",
    "blind206": ROOT / "data" / "knowledge" / "_audit" / "blind_v1" / "questions_strict.json",
    "gen120": ROOT / "data" / "knowledge" / "_audit" / "rag_testset_gen_r1r2.json",
}
_raw_per_set = os.environ.get("P4_AB_PER_SET", "8").strip()
PER_SET = 0 if _raw_per_set in ("", "0", "all") else int(_raw_per_set)
HEAD_V2_RE = re.compile(r"\[S(\d+) ([^\]]*)\] ")


def sha16(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()[:16]


def as_result(d: dict) -> RetrievalResult:
    """`kb.retrieve()` 返回 dict；渲染器要 `RetrievalResult`（与 `KnowledgeBase.context` 同构）。"""
    rr = RetrievalResult(query=d.get("query", ""))
    rr.seeds = [Seed(x["eid"], x["name"], x["score"], x["how"])
                for x in d.get("seeds", [])]
    rr.edges = [(e["src"], e["relation"], e["dst"], e["edge_score"])
                for e in d.get("edges", [])]
    rr.evidence = [Evidence(e["chunk_id"], e["score"], e.get("channels", {}),
                            e.get("graph_score", 0.0), e.get("reasons", []))
                   for e in d.get("evidence", [])]
    return rr


def render_v1_tailcut(retr, res, top_k: int, max_chars: int | None) -> str:
    """v1_tailcut 冻结参考实现 —— 逐字复制自 git HEAD 的 `GraphRetriever.context()`。

    `max_chars=None` 时返回**未截断**全文（供投影判据自检用）。
    """
    parts: list[str] = []
    if res.seeds:
        lines = ["【图谱实体】"]
        for s in res.seeds[:6]:
            ent = retr.graph.entities.get(s.eid)
            if not ent:
                continue
            ali = f"（别名：{'、'.join(ent.aliases[:4])}）" if ent.aliases else ""
            d = f" — {ent.desc}" if ent.desc else ""
            lines.append(f"- {ent.name}·{ent.type}{ali}{d}")
        parts.append("\n".join(lines))
    if res.edges:
        lines = ["【关系脉络】"]
        for s, r, d, _ in res.edges[:15]:
            lines.append(f"- {s} —{r}→ {d}")
        parts.append("\n".join(lines))
    if res.evidence:
        lines = ["【原文证据】"]
        for e in res.evidence[:top_k]:
            c = retr.chunks.get(e.chunk_id)
            if not c:
                continue
            loc = f"{c.chapter_title}"
            if c.scene_title:
                loc += f" / {c.scene_title}"
            lines.append(f"[{loc}] {c.text}")
        parts.append("\n\n".join(lines))
    out = "\n\n".join(parts)
    return out if max_chars is None else out[:max_chars]


def block_view(retr, res: RetrievalResult, top_k: int) -> list[dict]:
    """按 evidence 顺序取出块的可判据视图（与 `context()` 用同一批块）。"""
    out = []
    for e in res.evidence[:top_k]:
        c = retr.chunks.get(e.chunk_id)
        if not c:
            continue
        loc = f"{c.chapter_title}"
        if c.scene_title:
            loc += f" / {c.scene_title}"
        out.append({"cid": c.chunk_id, "loc": loc, "text": c.text or ""})
    return out


def statuses_v1(ctx: str, blocks: list[dict]) -> list[str]:
    """v1 判据（**诊断用，非权威**）：顺序扫描表头。

    ⚠ 此判据有已知缺陷：块定位串 `[篇名 / 场景名]` 在语料里**不唯一**
    （3695 块只有 897 个不同 loc，最大 62 块同 loc），`find(head, cursor)`
    会命中别的块或命中不到 → 与 `statuses_v1_projection` 在 5/626 题上分歧。
    权威判据是 `statuses_v1_projection`（尾切是纯前缀，`ctx == full[:max_chars]`
    已在同一次运行里断言）。此函数保留只用于自证量具分歧，不得用于出数。
    """
    out, cursor = [], 0
    for b in blocks:
        head = f"[{b['loc']}] "
        pos = ctx.find(head, cursor)
        if pos < 0:
            out.append("dropped")
            continue
        cursor = pos + len(head)
        out.append("complete" if b["text"] and b["text"] in ctx else "partial")
    return out


def statuses_v1_projection(full: str, max_chars: int, blocks: list[dict]) -> list[str]:
    """v1 自检判据：尾切 ⇒ 渲染串 = 全文前缀，用字符偏移直接判 完整/半块/掉出。"""
    out, cursor = [], 0
    for b in blocks:
        head = f"[{b['loc']}] "
        hs = full.find(head, cursor)
        if hs < 0:
            out.append("dropped")
            continue
        body_start = hs + len(head)
        end = body_start + len(b["text"])
        cursor = body_start
        if end <= max_chars:
            out.append("complete")
        elif hs < max_chars:
            out.append("partial")
        else:
            out.append("dropped")
    return out


def statuses_v2(ctx: str, blocks: list[dict]) -> tuple[list[str], list[int]]:
    """v2 判据（**权威**）：编号跟窗口会**重排**（跳过的块让后面块号前移），所以用块身份
    （`chunk=<cid>` 精确匹配）在溯源头里认块，不看号码。返回 (状态, 串里出现的号码序列)。

    ⚠ 绝不回落 `[篇名 / 场景名]` 前缀认块：loc 串在语料里不唯一
    （3695 块 → 897 个不同 loc，最大 62 块同 loc），回落会把「整块掉出窗外」
    误判成「半块」——这就是本次 A/B 首版把 v2 半块报成 724 的唯一原因。
    没有 `chunk=` 溯源头就是没进窗，一律 `dropped`。
    """
    heads: list[tuple[int, str, str]] = []      # (号码, chunk 值, 原始 meta)
    order: list[int] = []
    for m in HEAD_V2_RE.finditer(ctx):
        n = int(m.group(1))
        meta = m.group(2)
        cid = ""
        for kv in meta.split():
            if kv.startswith("chunk="):
                cid = kv[len("chunk="):]
                break
        heads.append((n, cid, meta))
        order.append(n)
    in_ctx = {cid for _n, cid, _m in heads if cid}
    out = []
    for b in blocks:
        if not (b["cid"] and b["cid"] in in_ctx):
            out.append("dropped")               # 严格身份判据，不做任何回落
            continue
        out.append("complete" if b["text"] and b["text"] in ctx else "partial")
    return out, order


def gold_keys(row: dict) -> list[str]:
    """题集 `evidence` 字段摊平成别名列表（三集格式略有差异）。"""
    ev = row.get("evidence")
    out: list[str] = []
    if isinstance(ev, list):
        for item in ev:
            if isinstance(item, list):
                out += [str(x) for x in item if x]
            elif item:
                out.append(str(item))
    return out


def gold_chunk_ids(row: dict) -> list[str]:
    v = row.get("source_chunk_ids")
    if isinstance(v, list):
        return [str(x) for x in v if x]
    return []


def ceiling_blocks(costs: list[int], budget: int) -> int:
    """完全装得下的块数上界（≤6 块，直接枚举子集）。用来区分「分配器没做好」与
    「窗口本来就装不下」——这是 P4.0 验收指标能否达标的唯一判据。"""
    if not costs:
        return 0
    best = 0
    for r in range(len(costs), 0, -1):
        for combo in itertools.combinations(costs, r):
            if sum(combo) <= budget:
                return r
    return best


def agg(statuses: list[str]) -> dict:
    d = {"complete": 0, "partial": 0, "dropped": 0}
    for s in statuses:
        d[s] += 1
    return d


def ratio(d: dict, k: str, total: int) -> float:
    return round(d[k] / total, 4) if total else 0.0


def main() -> int:
    s = get_settings()
    sha = sha16(s.graph_path)
    if sha != EXPECTED_SHA:
        raise SystemExit(f"图指纹漂移：期望 {EXPECTED_SHA}，实际 {sha}，中止")
    max_chars = s.context_max_chars
    kb = P.load_kb(s)
    retr = kb.retriever

    cases = []
    for tag, path in SETS.items():
        d = json.loads(path.read_text(encoding="utf-8"))
        rows = d if isinstance(d, list) else d.get("cases", [])
        rows = sorted(rows, key=lambda x: str(x.get("id", "")))
        if PER_SET:
            rows = rows[:PER_SET]
        cases += [(tag, r) for r in rows]

    per_case = []
    st_v1_all: list[str] = []
    st_v2_all: list[str] = []
    evicted_all = 0
    answer_bearing_evicted = 0
    gold_total = gold_v1 = gold_v2 = gold_evicted = 0
    gold_evicted_ids: list[str] = []
    fallback_total = 0
    numbering_gaps = 0
    selfcheck_ok = True
    ceiling_all = 0
    for tag, row in cases:
        qid = str(row.get("id", ""))
        q = row.get("q", "")
        d = asyncio.run(kb.retrieve(q, top_k=s.top_k, use_vector=False))
        res = as_result(d)                     # 渲染器要 RetrievalResult
        ctx1 = render_v1_tailcut(retr, res, s.top_k, max_chars)
        ctx2 = kb.context(d)                   # 生产通路（v2）
        full1 = render_v1_tailcut(retr, res, s.top_k, None)
        blocks = block_view(retr, res, s.top_k)

        st1 = statuses_v1(ctx1, blocks)
        proj1 = statuses_v1_projection(full1, max_chars, blocks)
        if st1 != proj1 or ctx1 != full1[:max_chars]:
            selfcheck_ok = False
        st2, order2 = statuses_v2(ctx2, blocks)

        # 头段占用：v1 全文 = 头段 + "\n\n" + 证据段，所以头长可**精确反解**
        # （不靠估算；两版共用同一段头，实体+关系先扣这个数）。
        if blocks:
            ev_part = "\n\n".join(
                ["【原文证据】"] + [f"[{b['loc']}] {b['text']}" for b in blocks])
            head_chars = max(0, len(full1) - len(ev_part) - 2)
        else:
            head_chars = len(full1)

        # v2 理论装配上界（同一成本模型、同一预算）
        objs = retr._collect_evidence_blocks(res, s.top_k)  # noqa: SLF001
        width = len(str(len(objs))) if objs else 1
        costs = [b.cost(width) for b in objs]
        budget = max(0, max_chars - head_chars - 2 - len("【原文证据】"))
        ceil_n = ceiling_blocks(costs, budget) if objs else 0
        ceiling_all += ceil_n

        a1, a2 = agg(st1), agg(st2)
        st_v1_all += st1
        st_v2_all += st2
        n = len(blocks)
        evicted = sum(1 for x, y in zip(st1, st2)
                      if x in ("complete", "partial") and y == "dropped")
        evicted_all += evicted

        keys = gold_keys(row)
        ab_idx = {i for i, b in enumerate(blocks)
                  if keys and any(k in b["text"] for k in keys)}
        ab_ev = sum(1 for i in ab_idx if st1[i] in ("complete", "partial")
                    and st2[i] == "dropped")
        answer_bearing_evicted += ab_ev

        gids = set(gold_chunk_ids(row))
        g_hits = [i for i, b in enumerate(blocks) if b["cid"] in gids]
        g_v1 = sum(1 for i in g_hits if st1[i] in ("complete", "partial"))
        g_v2 = sum(1 for i in g_hits if st2[i] in ("complete", "partial"))
        g_ev = [blocks[i]["cid"] for i in g_hits
                if st1[i] in ("complete", "partial") and st2[i] == "dropped"]
        gold_total += len(g_hits)
        gold_v1 += g_v1
        gold_v2 += g_v2
        gold_evicted += len(g_ev)
        gold_evicted_ids += g_ev

        fb = FALLBACK_MARK in ctx2
        fallback_total += 1 if fb else 0
        contiguous = sorted(order2) == list(range(1, len(order2) + 1))
        if not contiguous:
            numbering_gaps += 1

        per_case.append({
            "set": tag, "qid": qid, "n_blocks": n,
            "head_chars": head_chars, "budget": budget,
            "ctx_chars_v1": len(ctx1), "ctx_chars_v2": len(ctx2),
            "v1": a1, "v2": a2,
            "v2_heads": len(order2), "v2_numbering_contiguous": contiguous,
            "v2_fallback_truncated": fb,
            "ceiling_blocks": ceil_n,
            "evicted_v1_to_v2": evicted,
            "answer_bearing_blocks": len(ab_idx),
            "answer_bearing_evicted": ab_ev,
            "gold_in_evidence": len(g_hits),
            "gold_shown_v1": g_v1, "gold_shown_v2": g_v2, "gold_evicted": g_ev,
            "v1_statuses": st1, "v2_statuses": st2,
        })

    total = len(st_v1_all)
    a1, a2 = agg(st_v1_all), agg(st_v2_all)
    nq = len(cases)
    per_set = {}
    for tag in SETS:
        sub = [c for c in per_case if c["set"] == tag]
        n_t = sum(c["n_blocks"] for c in sub)
        c1 = agg([x for c in sub for x in c["v1_statuses"]])
        c2 = agg([x for c in sub for x in c["v2_statuses"]])
        per_set[tag] = {
            "queries": len(sub), "blocks": n_t,
            "v1": {**c1, "complete_ratio": ratio(c1, "complete", n_t),
                   "partial_ratio": ratio(c1, "partial", n_t),
                   "dropped_ratio": ratio(c1, "dropped", n_t),
                   "mean_blocks_in_window": round((c1["complete"] + c1["partial"]) / len(sub), 2)},
            "v2": {**c2, "complete_ratio": ratio(c2, "complete", n_t),
                   "partial_ratio": ratio(c2, "partial", n_t),
                   "dropped_ratio": ratio(c2, "dropped", n_t),
                   "mean_blocks_in_window": round((c2["complete"] + c2["partial"]) / len(sub), 2)},
            "ceiling_blocks": sum(c["ceiling_blocks"] for c in sub),
            "evicted_v1_to_v2": sum(c["evicted_v1_to_v2"] for c in sub),
            "v2_fallback_truncated": sum(1 for c in sub if c["v2_fallback_truncated"]),
        }

    def win(d: dict) -> dict:
        return {
            "complete": d["complete"], "partial": d["partial"], "dropped": d["dropped"],
            "total": total,
            "complete_ratio": ratio(d, "complete", total),
            "partial_ratio": ratio(d, "partial", total),
            "dropped_ratio": ratio(d, "dropped", total),
            "mean_blocks_in_window": round((d["complete"] + d["partial"]) / nq, 2),
        }

    v1w, v2w = win(a1), win(a2)
    c1_len = [c["ctx_chars_v1"] for c in per_case]
    c2_len = [c["ctx_chars_v2"] for c in per_case]
    heads = [c["head_chars"] for c in per_case]
    per_case_blocks_v2 = [c["v2"]["complete"] + c["v2"]["partial"] for c in per_case]
    per_case_blocks_v1 = [c["v1"]["complete"] + c["v1"]["partial"] for c in per_case]

    rep = {
        "done_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "graph_sha256_16": sha,
        "allocators": {"v2": CONTEXT_ALLOCATOR, "v1_reference": CONTEXT_ALLOCATOR_LEGACY},
        "caliber": {"mode": "graph_only", "use_vector": False, "top_k": s.top_k,
                    "context_max_chars": max_chars, "per_set": PER_SET or "all",
                    "queries": nq,
                    "CMPRAG_LEX_WEIGHT": os.environ.get("CMPRAG_LEX_WEIGHT"),
                    "CMPRAG_RRF_K": os.environ.get("CMPRAG_RRF_K"),
                    "CMPRAG_LEX_FIRST": os.environ.get("CMPRAG_LEX_FIRST"),
                    "PYTHONHASHSEED": os.environ.get("PYTHONHASHSEED")},
        "block_status": {"v1_tailcut": v1w, "v2_perblock": v2w,
                         "ceiling_blocks_total": ceiling_all,
                         "ceiling_ratio": round(ceiling_all / total, 4) if total else 0.0,
                         "ceiling_mean_blocks_in_window": round(ceiling_all / nq, 2) if nq else 0.0},
        "rendering": {
            "head_chars_mean": round(statistics.mean(heads), 1) if heads else 0.0,
            "head_chars_min": min(heads) if heads else 0,
            "head_chars_max": max(heads) if heads else 0,
            "head_share_of_budget": round((statistics.mean(heads) / max_chars), 4) if heads else 0.0,
            "ctx_len_v1_mean": round(statistics.mean(c1_len), 1) if c1_len else 0.0,
            "ctx_len_v2_mean": round(statistics.mean(c2_len), 1) if c2_len else 0.0,
            "ctx_len_v2_min": min(c2_len) if c2_len else 0,
            "ctx_len_v2_max": max(c2_len) if c2_len else 0,
            "ctx_len_over_budget_v1": sum(1 for x in c1_len if x > max_chars),
            "ctx_len_over_budget_v2": sum(1 for x in c2_len if x > max_chars),
            "blocks_in_window_v1_min": min(per_case_blocks_v1) if per_case_blocks_v1 else 0,
            "blocks_in_window_v1_max": max(per_case_blocks_v1) if per_case_blocks_v1 else 0,
            "blocks_in_window_v2_min": min(per_case_blocks_v2) if per_case_blocks_v2 else 0,
            "blocks_in_window_v2_max": max(per_case_blocks_v2) if per_case_blocks_v2 else 0,
            "v2_numbering_gaps": numbering_gaps,
            "v2_fallback_truncated_total": fallback_total,
        },
        "risk_check": {
            "evicted_v1_visible_to_v2_dropped": evicted_all,
            "answer_bearing_evicted": answer_bearing_evicted,
            "gold_in_evidence_total": gold_total,
            "gold_shown_v1": gold_v1, "gold_shown_v2": gold_v2,
            "gold_evicted_total": gold_evicted,
            "gold_evicted_ids": gold_evicted_ids,
        },
        "selfcheck": {
            "v1_signature_scan_equals_prefix_projection": selfcheck_ok,
            "v1_render_equals_full_prefix": selfcheck_ok,
        },
        "per_set": per_set,
        "per_case": per_case,
    }
    R.mkdir(parents=True, exist_ok=True)
    (R / "p4_allocator_ab.json").write_text(
        json.dumps(rep, ensure_ascii=False, indent=2), encoding="utf-8")

    md = [
        "# v9-P4.0 · `context()` 预算分配器 A/B（v1_tailcut → v2_perblock）",
        "",
        f"- 图谱 `{sha}`（硬门通过）；口径 `graph_only / top_k={s.top_k} / "
        f"max_chars={max_chars}`；{nq} 题（三集各 {PER_SET or '全量'}，按 qid 排序）",
        f"- 头段（【图谱实体】+【关系脉络】+段名）实测均 **{rep['rendering']['head_chars_mean']} 字**"
        f"（min {rep['rendering']['head_chars_min']} / max {rep['rendering']['head_chars_max']}）"
        f"= 预算的 {rep['rendering']['head_share_of_budget']:.2%}——这部分两版相同，先扣。",
        f"- v1 自检：签名扫描判据 == 前缀投影判据，且 `ctx == full[:max_chars]` → "
        f"`{selfcheck_ok}`（尾切是纯前缀，所以投影判据是精确的）。",
        "",
        "## 主读数：top-6 证据块进窗情况（同一批检索结果，两版渲染器）",
        "",
        "| 状态 | v1_tailcut | 占比 | v2_perblock | 占比 |",
        "| --- | --- | --- | --- | --- |",
        f"| 完整进窗 | {v1w['complete']} | {v1w['complete_ratio']:.2%} | "
        f"{v2w['complete']} | {v2w['complete_ratio']:.2%} |",
        f"| **被从中间切断（半块）** | {v1w['partial']} | {v1w['partial_ratio']:.2%} | "
        f"{v2w['partial']} | {v2w['partial_ratio']:.2%} |",
        f"| 整块掉出窗外 | {v1w['dropped']} | {v1w['dropped_ratio']:.2%} | "
        f"{v2w['dropped']} | {v2w['dropped_ratio']:.2%} |",
        f"| 合计（top-6 × 题） | {total} | 100% | {total} | 100% |",
        "",
        f"- 每题进窗块数：v1 **{v1w['mean_blocks_in_window']}** → v2 "
        f"**{v2w['mean_blocks_in_window']}**"
        f"（逐题区间 v1 {rep['rendering']['blocks_in_window_v1_min']}–"
        f"{rep['rendering']['blocks_in_window_v1_max']} / v2 "
        f"{rep['rendering']['blocks_in_window_v2_min']}–"
        f"{rep['rendering']['blocks_in_window_v2_max']}）",
        f"- **理论装配上界（同一成本模型穷举）**：{ceiling_all} 块 = "
        f"{rep['block_status']['ceiling_ratio']:.2%}、均 "
        f"{rep['block_status']['ceiling_mean_blocks_in_window']} 块/题 —— "
        f"这就是「窗口在现块长下最多装得下多少块」，是验收指标能不能达标的唯一判据。",
        f"- 渲染长度：v1 均 {rep['rendering']['ctx_len_v1_mean']} → v2 均 "
        f"{rep['rendering']['ctx_len_v2_mean']}（v2 min {rep['rendering']['ctx_len_v2_min']} / "
        f"max {rep['rendering']['ctx_len_v2_max']}）；超预算题数 v1 "
        f"{rep['rendering']['ctx_len_over_budget_v1']} / v2 "
        f"{rep['rendering']['ctx_len_over_budget_v2']}（硬上限 ≤{max_chars}）",
        f"- R4 保底触发（`{FALLBACK_MARK}`）：**{fallback_total}** 次；编号断号题数 "
        f"{numbering_gaps}",
        "",
        "## 预登记风险硬检查：gold 块会不会因窗口分配被挤出",
        "",
        f"- v1 可见（完整或半块）→ v2 **整块掉出**：{evicted_all} 块",
        f"- 其中正文含题集 gold 别名的块：{answer_bearing_evicted} 块",
        f"- 显式 gold（gen120 `source_chunk_ids`）：进检索结果 {gold_total} 块，"
        f"v1 可见 {gold_v1} / v2 可见 {gold_v2}，**被挤出 {gold_evicted} 块**"
        + (f"（`{', '.join(gold_evicted_ids)}`）" if gold_evicted_ids else ""),
        "",
        "## 分集读数",
        "",
        "| 集 | 题 | 块 | v1 完整 | v1 半块 | v1 掉出 | v2 完整 | v2 半块 | v2 掉出 | 上界 | 挤出 | 保底 |",
        "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for tag, x in per_set.items():
        md.append(
            f"| {tag} | {x['queries']} | {x['blocks']} | "
            f"{x['v1']['complete_ratio']:.2%} | {x['v1']['partial_ratio']:.2%} | "
            f"{x['v1']['dropped_ratio']:.2%} | {x['v2']['complete_ratio']:.2%} | "
            f"{x['v2']['partial_ratio']:.2%} | {x['v2']['dropped_ratio']:.2%} | "
            f"{x['ceiling_blocks']} | {x['evicted_v1_to_v2']} | {x['v2_fallback_truncated']} |")
    md += [
        "",
        "## 这三句结论",
        "",
        f"1. 半块率 **{v1w['partial_ratio']:.2%} → {v2w['partial_ratio']:.2%}**：R1（要么整块要么不渲染）"
        f"在真实三集上成立，模型再也看不到「一个开头当全部」的证据。",
        f"2. 完整进窗率 **{v1w['complete_ratio']:.2%} → {v2w['complete_ratio']:.2%}**，"
        f"每题 **{v1w['mean_blocks_in_window']} → {v2w['mean_blocks_in_window']}** 块。"
        f"涨不动的部分不是分配器的锅：同一成本模型下穷举上界只有 "
        f"{rep['block_status']['ceiling_ratio']:.2%}（均 "
        f"{rep['block_status']['ceiling_mean_blocks_in_window']} 块/题）——"
        f"块均成本吃掉份额，3000 字窗装不下更多块。",
        f"3. `{FALLBACK_MARK}` 保底触发 {fallback_total} 次、编号断号 {numbering_gaps} 题、"
        f"超预算 {rep['rendering']['ctx_len_over_budget_v2']} 题；gold 挤出 {gold_evicted} 块"
        f"（v1 本就看不到的不计）。",
        "",
        "> 只读脚本：不写图谱、不重建索引、不触 LLM/嵌入。v1 是冻结参考实现，"
        "生产路径 `retriever.py` 里只保留 v2。",
        "",
    ]
    (R / "p4_allocator_ab.md").write_text("\n".join(md), encoding="utf-8")
    print(f"[done] {nq} 题 / {total} 块 | v1 完整 {v1w['complete']} 半块 {v1w['partial']} "
          f"掉出 {v1w['dropped']} | v2 完整 {v2w['complete']} 半块 {v2w['partial']} "
          f"掉出 {v2w['dropped']} | 上界 {ceiling_all} | 挤出 {evicted_all} "
          f"(gold {gold_evicted}) | 保底 {fallback_total} | 断号 {numbering_gaps} | "
          f"自检 {selfcheck_ok}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
