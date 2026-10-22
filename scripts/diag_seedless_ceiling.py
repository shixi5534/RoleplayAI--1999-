# -*- coding: utf-8 -*-
"""无种子题「语义上界」探测（只读诊断脚本，不改任何检索行为与配置）。

为什么需要这个脚本
-------------------
``docs/plot-graph-rag/CHRONICLE.md §2026-09-17·下一步计划`` 定位到：失败 105 题里约 76–79 题
是「描述性、查询里不含实体名」的问法，``seeds`` 为空 → 语义块通道被种子门控
短路。计划直接给出了修复路径 A（LLM 解析出实体回填 seeds）与 B（校准
``semantic_link_min``）。但在动手实现之前，有一个必须先用数据回答的问题：

    **把种子门控拿掉，语义通道自己能救回多少题？**

- 若语义 top-20 里**根本没有**正解块（上界很低），那 A/B 都救不了，
  真瓶颈在索引/embedding/块粒度侧，做 A 是白投一周。
- 若语义 top-20 里**大量**有正解块（上界很高），那瓶颈就是门控与阈值，
  B（改一个浮点数）可能就够了，不必先上 LLM。

本脚本就是用来量这个上界的，同时产出路径 B 的阈值标定数据：

1. **块侧上界**：无种子题上，语义检索 top-K 能否取回相关块（recall@K），
   以及单纯用语义块能否覆盖全部证据组（semantic_ceiling_strict@K）。
2. **实体侧上界**：``search_entities`` 的 top-K 里有没有真阳实体
   （entity_recall@K），真阳的分数分布如何。
3. **阈值安全性**：用主评测台的 53 条负样本跑同一条实体链接管线，给出
   「阈值 t → 真阳接住率 vs 负样本误链接率」对照表——路径 B 的阈值只能从
   这张表里选，不能拍脑袋。

口径纪律
--------
- 题集加载、oracle 构建**直接复用** ``scripts/eval_plot_rag.py`` 的函数，
  不另造一套判定（另造口径会导致结论与主评测不可比，本项目已踩过一次：
  自建 strict 72.67% vs 主评测 67.67%）。
- 检索器走**生产同一条装配路径** ``build_plot_registry(settings)``。
- 语义索引未加载（静默降级）时**拒绝出报告**（EXIT=2），沿用主评测护栏。

用法（项目根目录）
------------------
    .venv/Scripts/python.exe -X utf8 scripts/diag_seedless_ceiling.py
    .venv/Scripts/python.exe -X utf8 scripts/diag_seedless_ceiling.py --limit 20   # 冒烟
    .venv/Scripts/python.exe -X utf8 scripts/diag_seedless_ceiling.py --allow-degraded

产物
----
- JSON：``data/knowledge/_audit/diag_seedless_ceiling.json``（可用 --out 覆盖）
- 日志：同路径 ``.log``（本机 PowerShell 不回传 stdout，日志必须自行落盘）

退出码：0 正常｜1 环境/数据缺失｜2 语义通道降级（拒绝出报告）
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

from roleplay.config import get_settings  # noqa: E402
from roleplay.core.knowledge.factory import build_plot_registry  # noqa: E402

# 复用主评测台的题集加载 / oracle 构建 / 负样本集，保证口径一致。
# 该模块顶层只有 import 与常量定义（无副作用执行），可安全导入。
import eval_plot_rag as E  # noqa: E402

DEFAULT_OUT = ROOT / "data" / "knowledge" / "_audit" / "diag_seedless_ceiling.json"
KS = (1, 3, 5, 10, 20)
THRESHOLDS = (0.20, 0.25, 0.30, 0.35, 0.40, 0.45, 0.50, 0.55, 0.60)
# 实体名与证据关键词互相判包含时的最小长度：短于 2 字符的中文/英文片段
# 会产生大量假真阳（「他」「a」），宁可漏标也不制造噪声。
MIN_NAME_LEN = 2

_LOG: list[str] = []


def log(msg: str) -> None:
    print(msg, flush=True)
    _LOG.append(str(msg))


def quantiles(values: list[float], qs: tuple[float, ...] = (0.1, 0.25, 0.5, 0.75, 0.9)) -> dict[str, float]:
    """分位数（线性插值）；空列表返回空 dict——不返回 0，避免「没测到」被读成 0。"""
    if not values:
        return {}
    vs = sorted(values)
    out: dict[str, float] = {}
    for q in qs:
        pos = q * (len(vs) - 1)
        lo = int(pos)
        hi = min(lo + 1, len(vs) - 1)
        frac = pos - lo
        out[f"p{int(q * 100)}"] = round(vs[lo] + (vs[hi] - vs[lo]) * frac, 4)
    return out


def rate(hit: int, total: int) -> float | None:
    """比率；分母为 0 时返回 None（口径纪律：不给出可被误读的 0）。"""
    return round(hit / total, 4) if total else None


def embed_with_retry(retr, text: str, retries: int = 1, backoff: float = 0.2) -> Any | None:
    """查询嵌入 + 一次重试 + 显式降级。

    C4：外部调用（嵌入服务）必须写明重试次数、退避与失败后的降级路径。
    这里降级 = 返回 None，调用方跳过该题并计入 embed_failed（不让它悄悄变成 0 分）。
    """
    for attempt in range(retries + 1):
        try:
            vec = retr.semantic.embed_query(text)
        except Exception as exc:  # noqa: BLE001 - 诊断脚本不得因单题异常中断
            log(f"  [warn] embed 异常（第 {attempt + 1} 次）：{exc!r}")
            vec = None
        if vec is not None:
            return vec
        if attempt < retries:
            time.sleep(backoff * (attempt + 1))
    return None


def build_entity_name_map(retr) -> dict[str, list[str]]:
    """eid -> [正名 + 别名...]（一次性构建，避免每题重扫 6814 实体）。"""
    out: dict[str, list[str]] = {}
    for ent in retr.store.entities():
        eid = str(ent.get("id"))
        names = [str(ent.get("name") or "")] + [str(a) for a in (ent.get("aliases") or [])]
        out[eid] = [n for n in names if n and len(n) >= MIN_NAME_LEN]
    return out


def truth_entities_for_item(
    item: dict,
    oracle_entry: dict,
    corpus,
    name_map: dict[str, list[str]],
) -> tuple[set[str], str]:
    """判定某题的「真阳实体」集合，返回 ``(真阳 eid 集合, 判定来源说明)``。

    两路取并集，且分别记录——因为两路都可能失效，合并后才知道到底标到了什么：
      1. **证据路**：实体名与题目 evidence 关键词互相包含（如「星锑」↔ 证据组里的「星锑」）；
      2. **上下文路**：实体名出现在 oracle full 块（单块覆盖全部证据组的块）文本里。

    只取 full 而非 any：any 集合在泛关键词下会膨胀到上千块，拼接开销与噪声都不可控。
    """
    groups = item.get("evidence") or []
    keywords = [str(k) for g in groups for k in (g or []) if str(k)]
    rel_text_parts: list[str] = []
    for h in list(oracle_entry.get("full") or [])[:50]:
        chunk = corpus.by_hash(str(h))
        if chunk is not None:
            rel_text_parts.append(chunk.text)
    rel_text = "\n".join(rel_text_parts)

    truth: set[str] = set()
    src_evidence = 0
    src_context = 0
    for eid, names in name_map.items():
        hit_ev = False
        for n in names:
            nl = n.lower()
            for kw in keywords:
                kl = str(kw).lower()
                if len(kl) < MIN_NAME_LEN:
                    continue
                if nl in kl or kl in nl:
                    hit_ev = True
                    break
            if hit_ev:
                break
        hit_ctx = any(n in rel_text for n in names) if rel_text else False
        if hit_ev:
            src_evidence += 1
        if hit_ctx:
            src_context += 1
        if hit_ev or hit_ctx:
            truth.add(eid)
    note = f"evidence={src_evidence}, context={src_context}"
    return truth, note


def main() -> int:
    ap = argparse.ArgumentParser(description="无种子题语义上界探测（只读诊断）")
    ap.add_argument("--character", default="wu_ming_zhe", help="角色 id")
    ap.add_argument("--testset", default="", help="题集路径（默认现行 300 题基准）")
    ap.add_argument("--top-entities", type=int, default=20, help="实体链接候选深度（默认 20）")
    ap.add_argument("--top-chunks", type=int, default=20, help="语义块候选深度（默认 20）")
    ap.add_argument("--limit", type=int, default=0, help="只跑前 N 题（冒烟用，不作结论）")
    ap.add_argument("--out", default=str(DEFAULT_OUT), help="报告落盘路径")
    ap.add_argument("--allow-degraded", action="store_true",
                    help="语义索引降级时仍出报告（报告会标注 degraded=True）")
    args = ap.parse_args()

    out_path = Path(args.out)
    log_path = out_path.with_suffix(out_path.suffix + ".log")
    started = time.strftime("%Y-%m-%d %H:%M:%S")

    settings = get_settings()
    registry = build_plot_registry(settings)
    retr = registry.get(args.character)
    if retr is None:
        log(f"[FAIL] 剧情图谱未加载（角色 {args.character}）")
        return 1
    degraded = getattr(retr, "semantic", None) is None
    if degraded and not args.allow_degraded:
        log("[FAIL] 语义通道已静默降级（语义索引未加载），拒绝在错误状态下出报告。"
            " 加 --allow-degraded 可强行继续。")
        return 2
    if degraded:
        log("[warn] 语义降级态：本轮读数无意义，仅供对照。")

    items = E.load_testset(Path(args.testset) if args.testset else None)
    if args.limit:
        items = items[: args.limit]
    log(f"[load] 题量 {len(items)}｜语料 {len(retr.corpus.chunks)} 块｜角色 {args.character}")

    t0 = time.time()
    oracle = E.build_oracle(retr.corpus, items)
    log(f"[oracle] 构建完成 {time.time() - t0:.1f}s")

    name_map = build_entity_name_map(retr)
    log(f"[ents] 实体名表 {len(name_map)} 条")

    cfg = {
        "top_chunks_probe": args.top_chunks,
        "top_entities_probe": args.top_entities,
        "semantic_top": getattr(retr, "semantic_top", None),
        "semantic_min_score": getattr(retr, "semantic_min_score", None),
        "semantic_link_top": getattr(retr, "semantic_link_top", None),
        "semantic_link_min": getattr(retr, "semantic_link_min", None),
        "embedder": getattr(getattr(retr, "semantic", None), "embedder_name", ""),
        "degraded": degraded,
    }
    log(f"[cfg] {json.dumps(cfg, ensure_ascii=False)}")

    per_case: list[dict] = []
    n_seedless = 0
    n_embed_failed = 0
    n_with_truth_ent = 0
    chunk_recall = {k: 0 for k in KS}
    chunk_ceiling = {k: 0 for k in KS}
    ent_recall = {k: 0 for k in KS}
    truth_scores: list[float] = []
    top_nontruth_scores: list[float] = []

    t0 = time.time()
    for i, item in enumerate(items, start=1):
        q = str(item.get("q") or "")
        qid = str(item.get("id") or "")
        seeds = retr.seed_gate(retr.link_detailed(q))
        if seeds:
            continue
        n_seedless += 1
        ent = oracle.get(qid) or {"full": set(), "any": set(), "ceiling": False}
        truth, note = truth_entities_for_item(item, ent, retr.corpus, name_map)
        if truth:
            n_with_truth_ent += 1
        case: dict[str, Any] = {
            "id": qid, "q": q, "n_truth_entities": len(truth), "truth_src": note,
        }
        # 每题进度落盘：本机 stdout 不回传，长跑时只能靠文件判断跑到哪一步。
        if n_seedless % 10 == 0:
            log(f"  [progress] 无种子题 {n_seedless} 题｜已用 {time.time() - t0:.0f}s")

        if degraded:
            per_case.append(case)
            continue
        qvec = embed_with_retry(retr, q)
        if qvec is None:
            n_embed_failed += 1
            case["embed_failed"] = True
            per_case.append(case)
            continue

        # ── 块侧：语义通道在【无种子门控】下的召回上界 ──────────────────────
        hits = retr.semantic.search(qvec, args.top_chunks)
        related_ranks: list[int] = []
        cov_union_parts: list[str] = []
        for rank, (h, score) in enumerate(hits, start=1):
            chunk = retr.corpus.by_hash(str(h))
            if chunk is None:
                continue
            is_rel = str(chunk.hash) in (ent.get("any") or set())
            if is_rel and not related_ranks:
                case["first_related_score"] = round(float(score), 4)
            if is_rel:
                related_ranks.append(rank)
            cov_union_parts.append(chunk.text)
        case["n_related_in_top"] = len(related_ranks)
        case["first_related_rank"] = related_ranks[0] if related_ranks else None
        case["top1_chunk_score"] = round(float(hits[0][1]), 4) if hits else None
        for k in KS:
            if related_ranks and related_ranks[0] <= k:
                chunk_recall[k] += 1
        groups = item.get("evidence") or []
        for k in KS:
            union = "\n".join(cov_union_parts[:k])
            covered = [any(str(kw) in union for kw in (g or [])) for g in groups]
            if groups and all(covered):
                chunk_ceiling[k] += 1

        # ── 实体侧：search_entities 的真阳排位与分数（路径 B 的标定数据）──────
        cands = retr.semantic.search_entities(qvec, args.top_entities)
        ent_rows: list[dict] = []
        truth_best_rank = None
        truth_best_score = None
        for rank, (eid, score) in enumerate(cands, start=1):
            eid_s = str(eid)
            is_truth = eid_s in truth
            if is_truth and truth_best_rank is None:
                truth_best_rank = rank
                truth_best_score = float(score)
            ent_rows.append({
                "rank": rank, "eid": eid_s, "score": round(float(score), 4),
                "truth": is_truth, "name": (name_map.get(eid_s) or [""])[0],
            })
        if truth_best_score is not None:
            truth_scores.append(truth_best_score)
        non_truth_top = next((float(s) for _e, s in cands if str(_e) not in truth), None)
        if non_truth_top is not None:
            top_nontruth_scores.append(non_truth_top)
        for k in KS:
            if truth_best_rank is not None and truth_best_rank <= k:
                ent_recall[k] += 1
        case["truth_best_rank"] = truth_best_rank
        case["truth_best_score"] = (round(truth_best_score, 4)
                                    if truth_best_score is not None else None)
        case["top_nontruth_score"] = (round(non_truth_top, 4)
                                      if non_truth_top is not None else None)
        case["entity_cands"] = ent_rows[:10]
        per_case.append(case)

    log(f"[scan] 无种子题 {n_seedless}/{len(items)}｜有真阳实体 {n_with_truth_ent}"
        f"｜嵌入失败 {n_embed_failed}｜耗时 {time.time() - t0:.0f}s")

    # ── 负样本：阈值安全性基线（路径 B 的护栏）─────────────────────────────
    neg_rows: list[dict] = []
    neg_max_scores: list[float] = []
    if not degraded:
        for cat, qn in E.NEGATIVE_CASES:
            qv = embed_with_retry(retr, qn)
            if qv is None:
                neg_rows.append({"cat": cat, "q": qn, "embed_failed": True, "max_score": None})
                continue
            cands = retr.semantic.search_entities(qv, max(args.top_entities, 5))
            mx = float(cands[0][1]) if cands else None
            if mx is not None:
                neg_max_scores.append(mx)
            neg_rows.append({
                "cat": cat, "q": qn, "max_score": round(mx, 4) if mx is not None else None,
                "top1_name": (name_map.get(str(cands[0][0]), [""])[0]) if cands else "",
            })
        log(f"[neg] 负样本 {len(E.NEGATIVE_CASES)} 条｜嵌入成功 {len(neg_max_scores)}")

    # 阈值对照表：真阳接住率 vs 负样本误链接率
    threshold_table: list[dict] = []
    for t in THRESHOLDS:
        linked = sum(
            1 for c in per_case
            if c.get("truth_best_score") is not None and c["truth_best_score"] >= t
        )
        neg_linked = sum(1 for s in neg_max_scores if s >= t)
        threshold_table.append({
            "threshold": t,
            "truth_link_rate": rate(linked, n_with_truth_ent),
            "neg_link_rate": rate(neg_linked, len(neg_max_scores)),
            "truth_linked": linked,
            "neg_linked": neg_linked,
        })

    report = {
        "generated_at": started,
        "character": args.character,
        "config": cfg,
        "counts": {
            "items": len(items),
            "seedless": n_seedless,
            "with_truth_entity": n_with_truth_ent,
            "embed_failed": n_embed_failed,
            "negatives": len(E.NEGATIVE_CASES),
            "negatives_embedded": len(neg_max_scores),
        },
        "chunk_side_upper_bound": {
            "recall_at_k": {str(k): rate(chunk_recall[k], n_seedless - n_embed_failed)
                            for k in KS},
            "semantic_only_ceiling_at_k": {
                str(k): rate(chunk_ceiling[k], n_seedless - n_embed_failed) for k in KS},
        },
        "entity_side_upper_bound": {
            "recall_at_k": {str(k): rate(ent_recall[k], n_with_truth_ent) for k in KS},
            "truth_best_score_quantiles": quantiles(truth_scores),
            "top_nontruth_score_quantiles": quantiles(top_nontruth_scores),
        },
        "negatives_detail": neg_rows,
        "neg_max_score_quantiles": quantiles(neg_max_scores),
        "threshold_table": threshold_table,
        "per_case": per_case,
    }
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    log(f"[out] {out_path}")

    log("\n==== 摘要 ====")
    log(f"无种子题：{n_seedless}/{len(items)}（其中含真阳实体标注 {n_with_truth_ent}）")
    log(f"块侧召回上界 recall@K：{json.dumps(report['chunk_side_upper_bound']['recall_at_k'], ensure_ascii=False)}")
    log(f"块侧语义单通道天花板 ceiling@K："
        f"{json.dumps(report['chunk_side_upper_bound']['semantic_only_ceiling_at_k'], ensure_ascii=False)}")
    log(f"实体侧召回上界 entity_recall@K："
        f"{json.dumps(report['entity_side_upper_bound']['recall_at_k'], ensure_ascii=False)}")
    log(f"真阳分数分位：{json.dumps(quantiles(truth_scores), ensure_ascii=False)}")
    log(f"负样本 top1 分数分位：{json.dumps(quantiles(neg_max_scores), ensure_ascii=False)}")
    log("阈值表（truth_link_rate vs neg_link_rate）：")
    for row in threshold_table:
        log(f"  t={row['threshold']:.2f}  真阳接住 {row['truth_link_rate']}  "
            f"负样本误接 {row['neg_link_rate']}")

    log_path.write_text("\n".join(_LOG), encoding="utf-8")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except SystemExit:
        raise  # 正常退出码（0/1/2）不得被下面的崩溃兜底吞掉
    except BaseException as exc:  # noqa: BLE001 - 诊断脚本崩溃也要留下现场
        import traceback
        try:
            Path(str(DEFAULT_OUT) + ".crash").write_text(
                f"{time.strftime('%Y-%m-%d %H:%M:%S')}\n{traceback.format_exc()}",
                encoding="utf-8")
        except Exception:
            pass
        print(f"[CRASH] {exc!r}", flush=True)
        raise
