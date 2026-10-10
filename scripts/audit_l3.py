# -*- coding: utf-8 -*-
"""WP3 —— L3 生成质量审查（compendium_rag，v8 冻结口径 / P4.2 装置改造）。

子代理双角色架构（防污染）：
  prepare  对每题跑 `retrieve + context`（v8 top_k=6），把 **gold 字段
           （keywords/ref/dims）在脚本层剥掉**，只留「问题 + 检索上下文」，
           按 25 题/批切成 l3_batches/ans_bNN.json 给**回答子代理**；
           gold 另存 l3_gold_map.json，**永不进子代理 prompt**。
  collect  读回答子代理产物（l3_answers/ans_bNN.json）与审查子代理产物
           （l3_judge/jdg_bNN.json），算六项 gate + 规则版越界幻觉初筛。

审查子代理拿的是「问题 + 上下文 + 回答」，同样不见 gold、不见回答端推理。

P4.2 三处改造（本次）：
  (A) 批次项改用**正式作答提示词**：`prepare` 对每题落
      ``prompt = compose.render_prompt(query, context, role_card="", history=None)``，
      与进程内 ``compose()`` **逐字同源**（``prompt_mode="compose_v1"``）；
      双盲复测**必须 history=None**，批次项里显式写 ``"history": null``。
      老字段 ``query``/``context`` 原样保留（向后兼容，老判分链路不炸）。
  (B) 每题新增「进窗块数」列：用**溯源头正则**数真正进窗的证据块
      （``^[S{n} chunk=… doc=… cat=…]``，编号按窗口顺序从 1 连续、不留空号），
      配 ``n_evidence_retrieved``（``res.evidence`` 总数）对账；
      并给出幻觉率的**并排两列**：
        - ``hallucination_rate_in_window``  窗内口径（现有定义，judge 判定）
        - ``hallucination_rate_offscript_all`` 全语料 offscript 口径
          （``_offscript_hallucination`` 正则初筛对**所有**题都算，不只 out_scope）
      正则初筛**降级为诊断列、不替换主指标**。
  (C) 小样本子集 + 产物目录分离：``--n-questions N``（分层抽样，默认全量 679）、
      ``--tag X`` 把批次/判分/报告写进独立子目录与独立文件名，迭代期冒烟
      不会覆盖定版全量产物。

运行（P4.2；``$env:PYTHONPATH="src"`` 或直接用 ``audit_common`` 自注入）：
    # 迭代期小样本 + 目录隔离（冒烟与全量分目录分文件名）
    .venv/Scripts/python.exe -X utf8 scripts/audit_l3.py --mode prepare --tag smoke --n-questions 5
    .venv/Scripts/python.exe -X utf8 scripts/audit_l3.py --mode judge-prep --tag smoke
    .venv/Scripts/python.exe -X utf8 scripts/audit_l3.py --mode collect --tag smoke
    # 定版全量（不传 --tag 时落回 v8 既有路径与文件名，保持向后兼容）
    PYTHONHASHSEED=0 .venv/Scripts/python.exe -X utf8 scripts/audit_l3.py --mode prepare
    ... --mode collect

产物：
    --tag X → 批次/回答/判分：data/knowledge/_audit/p4_harness_X/{l3_batches,l3_answers,l3_judge,l3_judge_in}
              报告        ：data/compendium_rag/reports/p4_harness_X.json
                            （prepare / judge-prep 另出 p4_harness_X_prepare.json / _judgeprep.json）
    无 --tag → 与 v8 完全一致：_audit/{l3_batches,l3_answers,l3_judge,l3_judge_in} + reports/audit_l3.json
"""
from __future__ import annotations

import argparse
import asyncio
import json
import os
import random
import re
import sys
from collections import Counter
from dataclasses import dataclass
from pathlib import Path

import audit_common as AC

AC.apply_v8_env()

AUDIT_DIR = AC.ROOT / "data" / "knowledge" / "_audit"
REPORTS_DIR = AC.ROOT / "data" / "compendium_rag" / "reports"
BATCH = 25
TOP_K_GEN = 6          # v8 生产口径的上下文注入条数
JUDGE_BATCH = 20       # judge 单批题量：context 约 3000 字/题，20 题一批控住误读率
REPEAT_FRAC = 0.2      # 复评比例（可靠性自证，Cohen κ）
SEED = 20261008

# ── P4.2 装置口径标（必须与 compose.py / retriever.py 同源，改动即口径变更）──
PROMPT_MODE = "compose_v1"    # 提示词来自 compendium_rag.compose.render_prompt
ROLE_CARD_MODE = "empty"      # 审计题集无角色归属字段 → 统一 role_card=""，显式记录
HISTORY_MODE = "none"         # 双盲复测 history=None（回答端与审查端零共享历史）

IN_SCOPE_SETS = ("300cn", "blind", "gen")
OUT_SCOPE_SETS = ("negative", "unanswerable")

EVIDENCE_HEADER = "【原文证据】"
#: 溯源头：`[S{i} chunk=… doc=… cat=…]`，由 GraphRetriever.context() 渲染
#: （src/compendium_rag/retriever.py:716-717）；只按**行首**、且必须带 `chunk=/doc=/cat=`
#: 才算一块 —— 不要用 `[S{n}]` 最大值猜块数（跳块会让号前移，最大值恰好等于块数只是巧合）。
RE_PROV_HEADER = re.compile(r"(?m)^\[S(\d+) ([^\]]*)\]")
RE_PROV_META = re.compile(r"\b(chunk|doc|cat)=")
#: 块内引用形如 `[S1]`（无空格+属性），不属于溯源头，绝不能计入块数。

# 常用默认路径（无 --tag 时的 v8 兼容口径；带 --tag 时经 paths_for() 分目录）
BATCH_DIR = AUDIT_DIR / "l3_batches"
ANS_DIR = AUDIT_DIR / "l3_answers"
JDG_DIR = AUDIT_DIR / "l3_judge"
JDG_IN_DIR = AUDIT_DIR / "l3_judge_in"
GOLD_MAP = AUDIT_DIR / "l3_gold_map.json"
MANIFEST = BATCH_DIR / "manifest.json"
OUT = REPORTS_DIR / "audit_l3.json"


def load_json(p: Path):
    return json.loads(p.read_text(encoding="utf-8"))


def _rel(p: Path) -> str:
    try:
        return str(Path(p).resolve().relative_to(AC.ROOT))
    except ValueError:
        return str(p)


# ── 产物路径解析（C：小样本/冒烟与全量分目录分文件名）──

@dataclass(frozen=True)
class L3Paths:
    """一次 L3 运行的全部读写路径。

    ``input_dir`` 只读（题集 + whitelist，永远指真实 ``_audit/``），
    其余字段是**写面**：带 ``--tag`` 时整体落 ``p4_harness_<tag>/`` 子目录。
    """

    input_dir: Path
    state_dir: Path
    batch_dir: Path
    ans_dir: Path
    jdg_dir: Path
    jdg_in_dir: Path
    gold_map: Path
    manifest: Path
    report: Path


def paths_for(args) -> L3Paths:
    """由 CLI 参数解析读写路径；``--tag`` 隔离，缺省 = v8 兼容路径。"""
    tag = (getattr(args, "tag", "") or os.environ.get("CMPRAG_L3_TAG", "") or "").strip()
    in_arg = (getattr(args, "input_dir", "") or "").strip()
    input_dir = Path(in_arg) if in_arg else AUDIT_DIR
    state_root = (getattr(args, "state_dir", "") or "").strip()
    if state_root:
        state_dir = Path(state_root)
    else:
        state_dir = AUDIT_DIR / f"p4_harness_{tag}" if tag else AUDIT_DIR
    base = (getattr(args, "report_name", "") or "").strip()
    if not base:
        base = f"p4_harness_{tag}" if tag else "audit_l3"
    reports_dir = Path(rep_arg) if (rep_arg := (getattr(args, "reports_dir", "") or "").strip()) else REPORTS_DIR
    return L3Paths(
        input_dir=input_dir,
        state_dir=state_dir,
        batch_dir=state_dir / "l3_batches",
        ans_dir=state_dir / "l3_answers",
        jdg_dir=state_dir / "l3_judge",
        jdg_in_dir=state_dir / "l3_judge_in",
        gold_map=state_dir / "l3_gold_map.json",
        manifest=state_dir / "l3_batches" / "manifest.json",
        report=reports_dir / f"{base}.json",
    )


def side_report(report: Path, kind: str) -> Path:
    """旁路报告名（``p4_harness_X.json`` → ``p4_harness_X_prepare.json``）。"""
    return report.with_name(f"{report.stem}_{kind}.json")


# ── 溯源块计数（B：进窗块数）──

def _fallback_mark() -> str:
    """R4 保底标记（引自 retriever，取不到时按冻结值回落）。"""
    try:
        from compendium_rag.retriever import FALLBACK_MARK  # noqa: PLC0415
        return FALLBACK_MARK
    except Exception:  # noqa: BLE001
        return "[节选]"


def count_blocks_in_window(context: str) -> dict:
    """数「真正进入窗口的证据块」（B）。

    口径：只看 ``【原文证据】`` 段，逐行匹配溯源头 ``^[S{n} chunk=… doc=… cat=…]``；
    编号应**从 1 连续、不留空号**（P4.0 的 ``v2_perblock`` 整块跳过、后面块号前移），
    ``contiguous`` 就是这个不变式的自检位。R4 保底路径（一块都装不下、截断注入并打
    ``[节选]``）**不是**带编号块，``n_blocks_in_window`` 记 0、``window_fallback`` 记 True。
    """
    ctx = context or ""
    parts = ctx.split(EVIDENCE_HEADER, 1)
    body = parts[1] if len(parts) == 2 else ""
    nums = [int(m.group(1)) for m in RE_PROV_HEADER.finditer(body)
            if RE_PROV_META.search(m.group(2))]
    return {
        "n_blocks_in_window": len(nums),
        "block_numbers": nums,
        "blocks_contiguous": nums == list(range(1, len(nums) + 1)),
        "window_fallback": _fallback_mark() in ctx,
    }


def _allocator() -> str:
    from compendium_rag.retriever import CONTEXT_ALLOCATOR  # noqa: PLC0415
    return CONTEXT_ALLOCATOR


def _system_prompt_sha16() -> str:
    import hashlib
    from compendium_rag.compose import ANSWER_SYSTEM_PROMPT  # noqa: PLC0415
    return hashlib.sha256(ANSWER_SYSTEM_PROMPT.encode("utf-8")).hexdigest()[:16]


def build_batch_item(qid: str, query: str, context: str, *,
                     n_evidence_retrieved: int = 0,
                     prompt: str | None = None,
                     allocator: str | None = None) -> dict:
    """构造**回答子代理**批次项（A + B 的落盘 schema）。

    ``prompt`` 缺省时用 compendium_rag.compose 现场渲染（逐字同源）；
    gold 字段（keywords/ref/set/dims）**一个都不带** —— 双盲前提。
    """
    if prompt is None:
        from compendium_rag.compose import render_prompt  # noqa: PLC0415
        prompt = render_prompt(query, context, role_card="", history=None)
    win = count_blocks_in_window(context)
    return {
        "qid": qid,
        "query": query,
        "context": context,
        "prompt": prompt,
        "prompt_mode": PROMPT_MODE,
        "allocator": allocator or _allocator(),
        "role_card_mode": ROLE_CARD_MODE,
        "history": None,
        "n_ctx_chars": len(context or ""),
        "n_blocks_in_window": win["n_blocks_in_window"],
        "n_evidence_retrieved": int(n_evidence_retrieved),
        "blocks_contiguous": win["blocks_contiguous"],
        "window_fallback": win["window_fallback"],
    }


def _batch_meta(*, top_k: int = TOP_K_GEN, batch_size: int = BATCH,
                subset: dict | None = None) -> dict:
    return {
        "schema": "audit.l3_batch/v2",
        "prompt_mode": PROMPT_MODE,
        "role_card_mode": ROLE_CARD_MODE,
        "history": HISTORY_MODE,
        "allocator": _allocator(),
        "system_prompt_sha16": _system_prompt_sha16(),
        "top_k": top_k,
        "batch_size": batch_size,
        "subset": subset or {},
    }


def _window_stats(items: list[dict]) -> dict:
    """进窗块数统计（B）。键名与 collect 侧的 metrics 保持一致，另留旧别名。"""
    ns = [int(it.get("n_blocks_in_window", 0) or 0) for it in items]
    es = [int(it.get("n_evidence_retrieved", 0) or 0) for it in items]
    mean = lambda xs: round(sum(xs) / len(xs), 4) if xs else None  # noqa: E731
    zero = sum(1 for x in ns if x == 0)
    fb = sum(1 for it in items if it.get("window_fallback"))
    return {
        # 规范键名（与 mode_collect 的 metrics 同名，便于逐轮对账）
        "n_blocks_in_window_mean": mean(ns),
        "n_blocks_in_window_min": min(ns) if ns else None,
        "n_blocks_in_window_max": max(ns) if ns else None,
        "n_zero_block_questions": zero,
        "n_window_fallback_questions": fb,
        "n_evidence_retrieved_mean": mean(es),
        "n_blocks_noncontiguous": sum(
            1 for it in items if it.get("blocks_contiguous") is False),
        # 旧别名（v8 时代命名，保持向后兼容）
        "mean_blocks_in_window": mean(ns),
        "min_blocks_in_window": min(ns) if ns else None,
        "max_blocks_in_window": max(ns) if ns else None,
        "n_fallback_questions": fb,
        "mean_evidence_retrieved": mean(es),
    }


# ── 子集抽样（C）──

def select_rows(rows: list[dict], n: int, seed: int = SEED) -> list[dict]:
    """按 ``set`` 分层的**确定性**抽样（最大余额法，至少给每个集留 1 题）。

    纪律：迭代期小样本必须覆盖五个题集（否则 L3.1/L3.5 的分母漂移无法归因），
    且同 (rows, n, seed) 必得同结果（可复现）。
    """
    if n <= 0 or n >= len(rows):
        return list(rows)
    rnd = random.Random(seed)
    groups: dict[str, list[dict]] = {}
    for r in rows:
        groups.setdefault(r["set"], []).append(r)
    for k in sorted(groups):
        rnd.shuffle(groups[k])
    names = sorted(groups)
    total = len(rows)
    counts = {k: int(n * len(groups[k]) / total) for k in names}
    seats = n - sum(counts.values())
    order = sorted(names, key=lambda k: (-(n * len(groups[k]) / total - counts[k]), k))
    while seats > 0:
        progressed = False
        for k in order:
            if seats == 0:
                break
            if counts[k] < len(groups[k]):
                counts[k] += 1
                seats -= 1
                progressed = True
        if not progressed:
            break
    if n >= len(names):                      # 保底：每集至少 1 题
        for k in names:
            if counts[k] == 0:
                donor = max(names, key=lambda x: (counts[x], x))
                if counts[donor] > 1:
                    counts[donor] -= 1
                    counts[k] += 1
    return [r for k in names for r in groups[k][:counts[k]]]


def apply_subset(rows: list[dict], args) -> tuple[list[dict], dict]:
    """``--n-questions``（分层子集）叠加 ``--limit``（旧行为：取头部），并回写参数。"""
    n = int(getattr(args, "n_questions", 0) or 0)
    seed = int(getattr(args, "sample_seed", SEED) or SEED)
    limit = int(getattr(args, "limit", 0) or 0)
    out, mode = list(rows), "full"
    if n and n < len(rows):
        out = select_rows(rows, n, seed=seed)
        mode = "stratified_sample"
    if limit:
        out = out[:limit]
        mode = mode if mode != "full" else "head_limit"
    return out, {
        "mode": mode,
        "n_requested": n or None,
        "sample_seed": seed,
        "limit": limit or None,
        "n_selected": len(out),
        "n_all": len(rows),
    }


# ───────────────────────────── prepare ─────────────────────────────

def _all_questions(E300, wl, input_dir: Path = AUDIT_DIR) -> list[dict]:
    """五集合并：answerable 196 / blind 206 / gen 120 / unanswerable 104 / 负样本 53。"""
    rows: list[dict] = []
    cn = E300.load_cases(input_dir / "rag_testset_300_cn.json")
    by_qid = {c.qid: c for c in cn}
    for qid in wl["300cn_answerable"]:
        c = by_qid[qid]
        rows.append({"qid": c.qid, "set": "300cn", "query": c.query,
                     "keywords": c.keywords, "ref": c.ref})
    for qid in wl["300cn_unanswerable"]:
        c = by_qid[qid]
        rows.append({"qid": c.qid, "set": "unanswerable", "query": c.query,
                     "keywords": c.keywords, "ref": c.ref})
    for path, name, key in ((input_dir / "blind_v1" / "questions_strict.json",
                             "blind", "blind_all"),
                            (input_dir / "rag_testset_gen_r1r2.json",
                             "gen", "gen_all")):
        qids = set(wl[key])
        for c in E300.load_cases(path):
            if c.qid in qids:
                rows.append({"qid": c.qid, "set": name, "query": c.query,
                             "keywords": c.keywords, "ref": c.ref})
    neg = load_json(input_dir / "negatives_annotation_agent.json")["items"]
    for it in neg:
        rows.append({"qid": f"neg-{it['idx']}", "set": "negative",
                     "query": it["q"], "keywords": [], "ref": ""})
    return rows


def mode_prepare(args) -> int:
    from compendium_rag import pipeline as P
    from compendium_rag.compose import render_prompt
    from compendium_rag.config import get_settings
    E300 = AC.eval300_module()
    paths = paths_for(args)

    async def run() -> int:
        s = get_settings()
        rep = AC.new_report("WP3-prepare", s)
        AC.assert_frozen_graph(rep)
        kb = P.load_kb(s)
        wl = load_json(paths.input_dir / "audit_qid_whitelist.json")["lists"]
        all_rows = _all_questions(E300, wl, paths.input_dir)
        rows, subset = apply_subset(all_rows, args)
        gold, items = {}, []
        for i, r in enumerate(rows, 1):
            res = await kb.retrieve(r["query"], top_k=TOP_K_GEN)
            ctx = kb.context(res, top_k=TOP_K_GEN)
            n_ev = len(res.get("evidence", []) or [])
            # A：正式作答提示词，逐字来自 compose（history=None：双盲前提）
            prompt = render_prompt(r["query"], ctx, role_card="", history=None)
            item = build_batch_item(r["qid"], r["query"], ctx,
                                    n_evidence_retrieved=n_ev, prompt=prompt)
            items.append(item)
            gold[r["qid"]] = {"set": r["set"], "keywords": r["keywords"],
                              "ref": r["ref"],
                              "n_ctx_chars": len(ctx),
                              "n_blocks_in_window": item["n_blocks_in_window"],
                              "n_evidence_retrieved": n_ev,
                              "blocks_contiguous": item["blocks_contiguous"],
                              "window_fallback": item["window_fallback"]}
            if i % 50 == 0:
                print(f"  …{i}/{len(rows)} 题已渲染上下文", flush=True)
        paths.ans_dir.mkdir(parents=True, exist_ok=True)
        paths.jdg_dir.mkdir(parents=True, exist_ok=True)
        paths.batch_dir.mkdir(parents=True, exist_ok=True)
        meta = _batch_meta(subset=subset)
        batches = []
        for bi in range(0, len(items), BATCH):
            chunk = items[bi:bi + BATCH]
            p = paths.batch_dir / f"ans_b{bi // BATCH + 1:02d}.json"
            p.write_text(json.dumps({"schema": "audit.l3_batch/v2",
                                     "prompt_meta": meta, "items": chunk},
                                    ensure_ascii=False, indent=1),
                         encoding="utf-8")
            batches.append({"path": _rel(p), "n": len(chunk),
                            "qids": [c["qid"] for c in chunk]})
        paths.gold_map.write_text(json.dumps(gold, ensure_ascii=False),
                                  encoding="utf-8")
        manifest = {
            "schema": "audit.l3_manifest/v2", "top_k": TOP_K_GEN,
            "n_items": len(items), "batch_size": BATCH, "batches": batches,
            "by_set": dict(Counter(r["set"] for r in rows)),
            "prompt_mode": PROMPT_MODE, "role_card_mode": ROLE_CARD_MODE,
            "history": HISTORY_MODE, "allocator": meta["allocator"],
            "system_prompt_sha16": meta["system_prompt_sha16"],
            "subset": subset, "state_dir": _rel(paths.state_dir),
            "window": _window_stats(items),
        }
        paths.manifest.write_text(json.dumps(manifest, ensure_ascii=False,
                                             indent=1), encoding="utf-8")

        # C：prepare 也回写报告（题数/子集参数/allocator/prompt_mode 必须可对账）
        rep["metrics"] = {
            "n_questions": len(items), "n_batches": len(batches),
            "subset": subset, "by_set": manifest["by_set"],
            "prompt_mode": PROMPT_MODE, "role_card_mode": ROLE_CARD_MODE,
            "history": HISTORY_MODE, "allocator": meta["allocator"],
            "system_prompt_sha16": meta["system_prompt_sha16"],
            "top_k": TOP_K_GEN, "batch_size": BATCH,
            "batch_dir": _rel(paths.batch_dir),
            "manifest": _rel(paths.manifest),
            "state_dir": _rel(paths.state_dir),
            **_window_stats(items),
        }
        rep["artifacts"] = [_rel(paths.manifest), _rel(paths.gold_map)]
        prep_report = AC.write_report(side_report(paths.report, "prepare"), rep)
        print(f"prepare：{len(items)} 题 / {len(batches)} 批 → {paths.manifest}")
        print(f"  prompt_mode={PROMPT_MODE} allocator={meta['allocator']} "
              f"role_card={ROLE_CARD_MODE!r} history={HISTORY_MODE} "
              f"subset={subset['mode']}({subset['n_selected']}/{subset['n_all']})")
        print(f"  进窗块数：均 {rep['metrics']['mean_blocks_in_window']}，"
              f"0 块题 {rep['metrics']['n_zero_block_questions']}，"
              f"保底题 {rep['metrics']['n_fallback_questions']}")
        print(f"  报告 → {prep_report}")
        return 0

    return asyncio.run(run())


# ────────────────────────── judge 装配 ──────────────────────────

def _read_dir(d: Path, pat: str) -> list[dict]:
    out = []
    if not d.exists():
        return out
    for p in sorted(d.glob(pat)):
        try:
            d_ = load_json(p)
        except (ValueError, OSError):
            continue
        rows = d_.get("items") if isinstance(d_, dict) else d_
        if isinstance(rows, list):
            out.extend(r for r in rows if isinstance(r, dict))
    return out


def _dump(path: Path, items: list[dict], meta: dict | None = None) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {"items": items}
    if meta:
        payload = {"schema": "audit.l3_judge_in/v1", "prompt_meta": meta,
                   "items": items}
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=1),
                    encoding="utf-8")


# ─────────────────────────── judge-prep ───────────────────────────

def _batch_ctx(paths: L3Paths = None) -> dict[str, dict]:
    """qid → {query, context, n_blocks_in_window, n_evidence_retrieved}。

    只从答题批次取（批次里本来就没有 gold）。旧批次缺 P4.2 列时现场用
    溯源头正则补算，老产物不炸。
    """
    p_ = paths or paths_for(argparse.Namespace())
    out: dict[str, dict] = {}
    for p in sorted(p_.batch_dir.glob("ans_b*.json")):
        try:
            items = load_json(p).get("items", [])
        except (ValueError, OSError):
            continue
        for it in items:
            ctx = it.get("context") or ""
            win = count_blocks_in_window(ctx)
            out[it["qid"]] = {
                "query": it["query"], "context": ctx,
                "n_blocks_in_window": it.get("n_blocks_in_window",
                                             win["n_blocks_in_window"]),
                "n_evidence_retrieved": it.get("n_evidence_retrieved"),
            }
    return out


def mode_judge_prep(args) -> int:
    """把「题面+上下文+回答」装配成 judge 批次；gold 字段一个都不带。

    同时冻结 20% 复评子集（固定 seed）：同一批题面上下文、由**另一个**审查
    子代理独立重判，用来算 Cohen κ。两个 judge 互不可见。
    """
    paths = paths_for(args)
    ctx = _batch_ctx(paths)
    answers = {r["qid"]: r for r in _read_dir(paths.ans_dir, "ans_b*.json")}
    manifest = load_json(paths.manifest) if paths.manifest.exists() else {}
    qids = [q for b in manifest.get("batches", []) for q in b.get("qids", [])]
    if not qids:
        qids = sorted(ctx)
    answered = [q for q in qids if q in answers and answers[q].get("answer")]
    print(f"答题覆盖 {len(answered)}/{len(qids)}")
    if not answered:
        print("没有任何回答，先跑回答子代理。")
        return 1

    items = [{"qid": q, "query": ctx[q]["query"], "context": ctx[q]["context"],
              "answer": answers[q]["answer"],
              "prompt_mode": manifest.get("prompt_mode", PROMPT_MODE),
              "allocator": manifest.get("allocator"),
              "n_blocks_in_window": ctx[q]["n_blocks_in_window"]}
             for q in answered]
    nb = (len(items) + JUDGE_BATCH - 1) // JUDGE_BATCH
    jmeta = {"prompt_mode": manifest.get("prompt_mode", PROMPT_MODE),
             "role_card_mode": manifest.get("role_card_mode", ROLE_CARD_MODE),
             "history": manifest.get("history", HISTORY_MODE),
             "allocator": manifest.get("allocator"),
             "subset": manifest.get("subset", {}),
             "n_questions": len(answered)}

    def _dump_j(path: Path, rows: list[dict]) -> None:
        _dump(path, rows, jmeta)

    paths.jdg_in_dir.mkdir(parents=True, exist_ok=True)
    for old in paths.jdg_in_dir.glob("*.json"):
        old.unlink()
    for i in range(nb):
        _dump_j(paths.jdg_in_dir / f"jdg_in_b{i + 1:02d}.json",
                items[i * JUDGE_BATCH:(i + 1) * JUDGE_BATCH])

    # 复评子集：按 qid 排序后固定 seed 抽样，保证重跑可复现
    rnd = random.Random(SEED)
    k = max(1, round(len(answered) * REPEAT_FRAC))
    rep_qids = sorted(rnd.sample(sorted(answered), k))
    rep_set = set(rep_qids)
    rep_items = [x for x in items if x["qid"] in rep_set]
    nr = (len(rep_items) + JUDGE_BATCH - 1) // JUDGE_BATCH
    for i in range(nr):
        _dump_j(paths.jdg_in_dir / f"rep_in_b{i + 1:02d}.json",
                rep_items[i * JUDGE_BATCH:(i + 1) * JUDGE_BATCH])
    (paths.jdg_in_dir / "repeat_qids.json").write_text(
        json.dumps({"schema": "audit.l3_repeat/v1", "seed": SEED,
                    "frac": REPEAT_FRAC, "n": len(rep_qids),
                    "qids": rep_qids}, ensure_ascii=False, indent=1),
        encoding="utf-8")

    rep = AC.new_report("WP3-judge-prep")
    rep["metrics"] = {
        "n_questions": len(qids), "n_answered": len(answered),
        "n_main_batches": nb, "n_repeat_batches": nr, "n_repeat_qids": len(rep_qids),
        "subset": manifest.get("subset", {}),
        "prompt_mode": manifest.get("prompt_mode", PROMPT_MODE),
        "allocator": manifest.get("allocator"),
        "batch_dir": _rel(paths.batch_dir), "judge_in_dir": _rel(paths.jdg_in_dir),
        "state_dir": _rel(paths.state_dir),
    }
    rep["artifacts"] = [_rel(paths.jdg_in_dir), _rel(paths.report)]
    jp = AC.write_report(side_report(paths.report, "judgeprep"), rep)
    print(f"judge 输入 → {paths.jdg_in_dir}：主评 {nb} 批 ×{JUDGE_BATCH}，"
          f"复评 {nr} 批 / {len(rep_qids)} 题（{REPEAT_FRAC:.0%}）")
    print(f"  报告 → {jp}")
    return 0


# ───────────────────────────── collect ─────────────────────────────

def _cohen_kappa(pairs: list[tuple]) -> float | None:
    """标准 Cohen κ（类别一致，不加权）；样本不足两档时返回 None。"""
    if len(pairs) < 2:
        return None
    cats = sorted({a for a, _ in pairs} | {b for _, b in pairs})
    if len(cats) < 2:
        return None
    n = len(pairs)
    po = sum(1 for a, b in pairs if a == b) / n
    pe = 0.0
    for c in cats:
        pa = sum(1 for a, _ in pairs if a == c) / n
        pb = sum(1 for _, b in pairs if b == c) / n
        pe += pa * pb
    if abs(1 - pe) < 1e-12:
        return None
    return round((po - pe) / (1 - pe), 4)


def _persona_bin(v) -> int | None:
    if not isinstance(v, (int, float)):
        return None
    return 0 if v <= 2 else (1 if v == 3 else 2)


def _rate(hits: int, denom: int) -> float | None:
    """分母为 0 时返回 None（不是 0.0）——无判分样本 ≠ 零幻觉，gate 必须落 N/A。"""
    return round(hits / denom, 4) if denom else None


RE_CN_NAME = re.compile(r"[一-龥]{2,8}")


def _offscript_hallucination(ans: str, ctx: str, corpus_blob: str) -> bool:
    """越界幻觉初筛：答案里出现「上下文没有、且全语料查无」的 2~4 字中文专名。

    P4.2 起本函数**对全部题**都跑一遍（``hallucination_rate_offscript_all`` 列），
    但不作为 L3.6 主指标：实测命中词是「拒答」「片段中」「未记载」这类拒答自述用语
    而非专名，无判别力（见 metrics.offscript_screen_note）。
    """
    in_ctx = {seg for seg in RE_CN_NAME.findall(ctx)}
    for seg in set(RE_CN_NAME.findall(ans)):
        if len(seg) > 4:
            continue
        if seg in in_ctx:
            continue
        if seg in corpus_blob:
            continue
        if seg in _COMMON_WORDS:
            continue
        return True
    return False


# 常见泛词不是专名，初筛要跳过（否则"我不知道/剧情里"这类都会误判）
_COMMON_WORDS = frozenset("""我不知道 无法 确认 没有 相关 记录 剧情 原文 片段 检索 正典 设定
角色 组织 地点 物品 事件 概念 名称 信息 资料 线索 游戏 玩家 我们 你们 这个 那个 什么 怎么
为什么 哪些 如何 以及 但是 因此 而且 并且 可能 应该 需要 认为 了解 知道 清楚 明显 显然
抱歉 对不起 暂时 目前 现在 之后 之前 时候 问题 答案 参考 依据 来源 证据 内容 文本 语句""".split())


def _scopes(rows: list[dict]) -> tuple[list[dict], list[dict]]:
    scored = [r for r in rows if r["scored"]]
    return ([r for r in scored if r["set"] in IN_SCOPE_SETS],
            [r for r in scored if r["set"] in OUT_SCOPE_SETS])


def _hallucination_columns(rows: list[dict]) -> dict:
    """幻觉率的**并排两列**（B）：窗内口径 + 全语料 offscript 口径。

    - ``hallucination_rate_in_window``：域内题（300cn/blind/gen）× judge 判定；
    - ``hallucination_rate_offscript_all``：正则初筛对**所有题**算一遍（分母 = 有答案的题）；
    - ``offscript_hallucination_rate``：越界题（negative/unanswerable）× judge 判定（L3.6 主指标）。
    """
    in_scope, out_scope = _scopes(rows)
    screened = [r for r in rows if r.get("offscript_screen") is not None]
    by_set = Counter()
    hit_by_set = Counter()
    for r in screened:
        by_set[r["set"]] += 1
        if r["offscript_screen"]:
            hit_by_set[r["set"]] += 1
    in_window = _rate(sum(1 for r in in_scope if r["hallucination"]), len(in_scope))
    return {
        "hallucination_rate_in_window": in_window,
        "hallucination_rate_offscript_all": _rate(
            sum(1 for r in screened if r["offscript_screen"]), len(screened)),
        "offscript_hallucination_rate": _rate(
            sum(1 for r in out_scope if r["hallucination"]), len(out_scope)),
        "offscript_all_hits": sum(1 for r in screened if r["offscript_screen"]),
        "offscript_all_denominator": len(screened),
        "offscript_all_hit_by_set": {k: hit_by_set[k] for k in sorted(by_set)},
        "offscript_all_n_by_set": {k: by_set[k] for k in sorted(by_set)},
        # 向后兼容别名：老记分卡/报告消费的键名，值 = 窗内口径
        "hallucination_rate": in_window,
        "n_in_scope": len(in_scope),
        "n_out_scope": len(out_scope),
    }


def degrade_reason(*, gold_present: bool, n_judges: int, n_answers: int) -> str | None:
    """无判分产物时的降级说明（None = 正常有判分）。

    设计：缺 gold 映射 = 连题面都没有 → 调用方硬停；judge 为空 = **优雅降级**，
    gate 全 N/A、只出题面/窗内诊断列，不抛异常。
    """
    if not gold_present:
        return ("无判分产物：未找到 gold 映射（先跑 --mode prepare，"
                "注意 --tag 要与本次一致）")
    if not n_judges:
        return (f"无判分产物：judge 目录为空（已有回答 {n_answers} 条）；"
                "persona/faithfulness/hallucination/refusal 无判分样本 → "
                "gate 全 N/A，只出窗内/全语料诊断列，不崩")
    return None


def mode_collect(args) -> int:
    from compendium_rag import pipeline as P
    from compendium_rag.config import get_settings

    paths = paths_for(args)
    gold_present = paths.gold_map.exists()
    if not gold_present:
        print(f"[无判分产物] {degrade_reason(gold_present=False, n_judges=0, n_answers=0)}"
              f"；本次未做任何 gate 判定（{_rel(paths.gold_map)}）")
        return 1

    s = get_settings()
    rep = AC.new_report("WP3", s)
    AC.assert_frozen_graph(rep)

    answers = {r["qid"]: r for r in _read_dir(paths.ans_dir, "ans_b*.json")}
    judges = {r["qid"]: r for r in _read_dir(paths.jdg_dir, "jdg_*.json")}
    reps = {r["qid"]: r for r in _read_dir(paths.jdg_dir, "rep_*.json")}
    degraded = degrade_reason(gold_present=True, n_judges=len(judges),
                              n_answers=len(answers))
    if degraded:
        print(f"[DEGRADED] {degraded}")

    ctx_by_qid = _batch_ctx(paths)
    gold = load_json(paths.gold_map)
    manifest = load_json(paths.manifest) if paths.manifest.exists() else {}
    missing = [q for b in manifest.get("batches", []) for q in b.get("qids", [])
               if q not in answers]
    missing_j = [q for b in manifest.get("batches", []) for q in b.get("qids", [])
                 if q not in judges]

    # 全语料 offscript 口径需要 corpus blob；没有任何回答时不必付这份 IO。
    has_answer = any((a.get("answer") or "") for a in answers.values())
    corpus_blob = "\n".join(ch.text for ch in P.load_chunks(s)) if has_answer else ""

    rows = []
    for qid, g in gold.items():
        a, j = answers.get(qid) or {}, judges.get(qid) or {}
        ans = a.get("answer", "") or ""
        ctx = ctx_by_qid.get(qid, {}).get("context", "") or ""
        win_rec = ctx_by_qid.get(qid, {})
        n_win = win_rec.get("n_blocks_in_window")
        if n_win is None:
            n_win = g.get("n_blocks_in_window")
        if n_win is None:
            n_win = count_blocks_in_window(ctx)["n_blocks_in_window"]
        rows.append({
            "qid": qid, "set": g["set"], "scored": bool(j),
            "persona": j.get("persona"), "voice": j.get("voice"),
            "faithfulness": j.get("faithfulness"),
            "refusal": bool(j.get("refusal")),
            "hallucination": bool(j.get("hallucination")),
            # B：正则初筛对**所有题**都算（不再只算 out_scope），作为诊断列
            "offscript_screen": (_offscript_hallucination(ans, ctx, corpus_blob)
                                 if (ans and corpus_blob) else None),
            "answer_chars": len(ans),
            "n_blocks_in_window": n_win,
            "n_evidence_retrieved": win_rec.get("n_evidence_retrieved",
                                                g.get("n_evidence_retrieved")),
            "window_fallback": win_rec.get("window_fallback", g.get("window_fallback")),
        })

    in_scope, out_scope = _scopes(rows)

    def mean(xs):
        xs = [x for x in xs if x is not None]
        return round(sum(xs) / len(xs), 4) if xs else None

    persona = mean(r["persona"] for r in in_scope)
    voice = mean(r["voice"] for r in in_scope)
    faith = mean(r["faithfulness"] for r in in_scope)
    degradation = _rate(sum(1 for r in in_scope if (r["voice"] or 5) <= 2),
                        len(in_scope))
    refusal = _rate(sum(1 for r in out_scope if r["refusal"]), len(out_scope))
    # 越界幻觉率：只用**审查子代理**的 hallucination 判定（L3.6 主指标）。
    # 正则初筛（_offscript_hallucination）实测无判别力——157 道越界题里命中 152 道，
    # 命中词是「拒答」「片段中」「未记载」这类拒答自述用语而非专名（见 metrics
    # offscript_screen_* 诊断项），只作 recall 诊断、不入分母。
    hall_cols = _hallucination_columns(rows)
    halluc = hall_cols["hallucination_rate_in_window"]
    off_halluc = hall_cols["offscript_hallucination_rate"]
    off_all = hall_cols["hallucination_rate_offscript_all"]
    screen_hits = sum(1 for r in out_scope if r["offscript_screen"])
    screen_only = sum(1 for r in out_scope
                      if r["offscript_screen"] and not r["hallucination"])

    # ── 可靠性自证：20% 子集由**另一个**审查子代理独立重判 → Cohen κ ──
    by_qid = {r["qid"]: r for r in rows}
    p_pairs, h_pairs, f_diffs = [], [], []
    for qid, rp in reps.items():
        base = by_qid.get(qid)
        if not base or not base["scored"]:
            continue
        pb, pr = _persona_bin(base["persona"]), _persona_bin(rp.get("persona"))
        if pb is not None and pr is not None:
            p_pairs.append((pb, pr))
        h_pairs.append((bool(base["hallucination"]), bool(rp.get("hallucination"))))
        fb, fr = base["faithfulness"], rp.get("faithfulness")
        if isinstance(fb, (int, float)) and isinstance(fr, (int, float)):
            f_diffs.append(abs(fb - fr))
    kappa_p = _cohen_kappa(p_pairs)
    kappa_h = _cohen_kappa(h_pairs)
    kappa_min = min([k for k in (kappa_p, kappa_h) if k is not None],
                    default=None)
    mean_fa_diff = round(sum(f_diffs) / len(f_diffs), 4) if f_diffs else None
    low_conf = kappa_min is None or kappa_min < 0.6

    ns = [r["n_blocks_in_window"] for r in rows
          if r["n_blocks_in_window"] is not None]
    metrics = {
        "n_questions": len(gold), "n_answered": len(answers),
        "n_judged": len(judges),
        "coverage": round(len(judges) / max(1, len(gold)), 4),
        "missing_answers": missing[:50], "missing_judges": missing_j[:50],
        "degraded": bool(degraded),
        "degraded_reason": degraded or "",
        "persona": persona, "voice": voice, "faithfulness": faith,
        "voice_degradation_rate": degradation,
        # B：并排两列（in_window 与老键 hallucination_rate 同值）
        "hallucination_rate": halluc,
        "hallucination_rate_in_window": halluc,
        "hallucination_rate_offscript_all": off_all,
        "offscript_all_hits": hall_cols["offscript_all_hits"],
        "offscript_all_denominator": hall_cols["offscript_all_denominator"],
        "offscript_all_hit_by_set": hall_cols["offscript_all_hit_by_set"],
        "offscript_all_n_by_set": hall_cols["offscript_all_n_by_set"],
        "refusal_rate": refusal, "offscript_hallucination_rate": off_halluc,
        "offscript_screen_hits": screen_hits,
        "offscript_screen_hit_rate": _rate(screen_hits, len(out_scope)),
        "offscript_screen_only": screen_only,
        "offscript_screen_note": (
            "正则初筛命中词为拒答自述用语（「拒答」「片段中」「未记载」等），"
            "抽样 10 条 screen-only 全部是正确拒答，无判别力，故不入 L3.6 分母；"
            "P4.2 起该初筛对**全部题**并排给出 hallucination_rate_offscript_all，"
            "仅作诊断列、不替换窗内主指标"),
        "n_in_scope": len(in_scope), "n_out_scope": len(out_scope),
        # B：进窗块数（溯源头正则计数）
        "n_blocks_in_window_mean": (round(sum(ns) / len(ns), 4) if ns else None),
        "n_blocks_in_window_min": min(ns) if ns else None,
        "n_blocks_in_window_max": max(ns) if ns else None,
        "n_zero_block_questions": sum(1 for x in ns if x == 0),
        "n_window_fallback_questions": sum(1 for r in rows
                                           if r.get("window_fallback")),
        "n_evidence_retrieved_mean": mean(
            r["n_evidence_retrieved"] for r in rows
            if r["n_evidence_retrieved"] is not None),
        "repeat_n": len(p_pairs), "kappa_persona": kappa_p,
        "kappa_hallucination": kappa_h, "mean_faithfulness_abs_diff": mean_fa_diff,
        "judge_low_confidence": low_conf,
        "metric_definitions": {
            "hallucination_rate_in_window":
                "域内题（300cn/blind/gen）× 审查子代理 hallucination 判定",
            "hallucination_rate_offscript_all":
                "全语料正则初筛（_offscript_hallucination）× 所有有答案的题（诊断列）",
            "offscript_hallucination_rate":
                "越界题（negative/unanswerable）× 审查子代理 hallucination 判定（L3.6）",
        },
    }
    # C：回写题数 / 子集参数 / allocator / prompt_mode，供逐轮对账
    rep["artifact_scope"] = {
        "state_dir": _rel(paths.state_dir),
        "batch_dir": _rel(paths.batch_dir),
        "judge_in_dir": _rel(paths.jdg_in_dir),
        "report": _rel(paths.report),
        "n_questions": len(gold),
        "subset": manifest.get("subset", {}),
        "prompt_mode": manifest.get("prompt_mode", PROMPT_MODE),
        "role_card_mode": manifest.get("role_card_mode", ROLE_CARD_MODE),
        "history": manifest.get("history", HISTORY_MODE),
        "allocator": manifest.get("allocator", _allocator()),
        "system_prompt_sha16": manifest.get("system_prompt_sha16"),
        "top_k": manifest.get("top_k", TOP_K_GEN),
    }
    rep["metrics"] = metrics
    g = rep["gate_verdicts"]
    for gate, target, actual, ok in (
        ("L3.1 角色/正典忠实度（persona，1~5）", "≥4.0", persona,
         persona is not None and persona >= 4.0),
        ("L3.2 声音退化率（voice≤2 占比）", "≤0.10", degradation,
         degradation is not None and degradation <= 0.10),
        ("L3.3 Faithfulness", "≥0.85", faith, faith is not None and faith >= 0.85),
        ("L3.4 幻觉率（域内题）", "≤0.08", halluc,
         halluc is not None and halluc <= 0.08),
        ("L3.5 越界拒答率（negative+unanswerable）", "≥0.80", refusal,
         refusal is not None and refusal >= 0.80),
        ("L3.6 越界幻觉率", "≤0.15", off_halluc,
         off_halluc is not None and off_halluc <= 0.15),
    ):
        verdict = "PASS" if ok else ("N/A" if actual is None else "FAIL")
        if actual is None and degraded:
            reason = degraded
        else:
            reason = ("judge 覆盖率 "
                      f"{metrics['coverage']:.2%}；N/A=该 gate 无判分样本"
                      if actual is None else
                      "回答子代理与审查子代理零共享历史，gold 全程未进 prompt")
        g.append(AC.gate_verdict(gate, target, actual, verdict, reason, "生成层"))
    g[3]["reason"] += (
        f"；并排诊断列 hallucination_rate_offscript_all="
        f"{off_all}（{metrics['offscript_all_hits']}/"
        f"{metrics['offscript_all_denominator']}，全语料正则初筛，不入 gate）；"
        f"进窗块数均 {metrics['n_blocks_in_window_mean']}"
        f"（0 块题 {metrics['n_zero_block_questions']}，"
        f"保底 {metrics['n_window_fallback_questions']}）")
    g[-1]["reason"] += (
        f"；正则初筛降为诊断项（越界题命中 {screen_hits}/{len(out_scope)}，"
        "命中词是拒答自述用语而非专名，无判别力）")
    # 可靠性自证项：名字里带「基础设施」→ 记分卡不计入 L3 层分母，只作披露。
    g.append(AC.gate_verdict(
        "L3.7judge 复评一致性 Cohen κ（基础设施·可靠性自证）", "≥0.60",
        kappa_min, "PASS" if not low_conf else
        ("N/A" if kappa_min is None else "FAIL"),
        f"复评 {len(p_pairs)} 题；persona κ={kappa_p}，hallucination κ={kappa_h}，"
        f"faithfulness 平均绝对差={mean_fa_diff}。"
        + ("κ 未达标 → 本层所有读数标「低置信」，只作参考不作晋级依据。"
           if low_conf else ""),
        "评测方法"))
    rep["per_case"] = rows
    out_path = AC.write_report(paths.report, rep)
    print(f"WP3 → {out_path}")
    if degraded:
        print(f"  [DEGRADED] {degraded}")
    for gv in g:
        print(f"  [{gv['verdict']}] {gv['gate']}: {gv['actual']}")
    print(f"  幻觉率并排：in_window={halluc}（{metrics['n_in_scope']} 题） | "
          f"offscript_all={off_all}（{metrics['offscript_all_denominator']} 题） | "
          f"越界 judge={off_halluc}")
    print(f"  进窗块数：均 {metrics['n_blocks_in_window_mean']}"
          f"（{metrics['n_blocks_in_window_min']}~{metrics['n_blocks_in_window_max']}）"
          f" | 子集 {rep['artifact_scope']['subset'].get('mode')} "
          f"{rep['artifact_scope']['n_questions']} 题 | "
          f"prompt_mode={rep['artifact_scope']['prompt_mode']} | "
          f"allocator={rep['artifact_scope']['allocator']}")
    return 0


MODES = {"prepare": mode_prepare, "judge-prep": mode_judge_prep,
         "collect": mode_collect}

if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="WP3 L3 生成质量审查（P4.2 装置）")
    ap.add_argument("--mode", required=True, choices=list(MODES))
    ap.add_argument("--limit", type=int, default=0, help="调试：只渲染前 N 题")
    ap.add_argument("--n-questions", "--sample", dest="n_questions", type=int,
                    default=0,
                    help="P4.2：只跑 N 题的分层子集（默认 0 = 全量 679）")
    ap.add_argument("--sample-seed", type=int, default=SEED,
                    help="子集抽样种子（默认固定，保证可复现）")
    ap.add_argument("--tag", default="",
                    help="迭代期隔离标 X：状态落 _audit/p4_harness_X/、"
                         "报告落 reports/p4_harness_X*.json（默认空 = v8 全量路径）")
    ap.add_argument("--state-dir", default="",
                    help="显式指定批次/回答/判分状态目录（默认随 --tag）")
    ap.add_argument("--input-dir", default="",
                    help="题集与 whitelist 输入目录（只读；默认 data/knowledge/_audit）")
    ap.add_argument("--reports-dir", default="", help="报告输出目录")
    ap.add_argument("--report-name", default="",
                    help="报告基名（默认 audit_l3，或 p4_harness_<tag>）")
    args = ap.parse_args()
    sys.exit(MODES[args.mode](args))
