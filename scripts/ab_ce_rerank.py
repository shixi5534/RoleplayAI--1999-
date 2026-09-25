# -*- coding: utf-8 -*-
"""T1：bge-reranker 交叉编码器精排实验（不改检索代码，只走 chunks_transform 钩子）。

为什么这么做
------------
把已存在未启用的 ``CrossEncoderReranker``（bge-reranker-base ONNX）接入检索管线，
标定「候选池大小 k」：spy 住 ``_fuse_channels`` 拿到五通道并集候选池（去重、cap 到 k），
用交叉编码器对 (query, chunk.text) 打分，取 top-(top_chunks+lexical_fallback) 包成
``RetrievedChunk`` 走**主评测口径**（``evaluate_case(chunks_transform=...)``）。

分带纪律（前人踩坑）：包回的 ``RetrievedChunk`` 分数必须线性映射回
``[FUSE_MIN_SCORE(0.6), FUSE_MAX_SCORE(1.0) - ε]``。``persona_prompt.build_plot_context``
对 ``plot_graph`` 组只留绝对下限 0.05（豁免 0.85 相对门），故只要分数 ≥ 0.6 全部保留，
顺序由分数大小决定——这正是精排要的效果。

判定口径**完全复用主评测**，不自建 strict/inject 口径（自建会导致 72.67% vs 67.67% 不可比）。

用法（项目根目录）
------------------
    .venv/Scripts/python.exe -X utf8 scripts/ab_ce_rerank.py --k 20 30 50
    .venv/Scripts/python.exe -X utf8 scripts/ab_ce_rerank.py --k 30 --limit 20   # 冒烟

产物：``data/knowledge/_audit/ab_ce_rerank.json`` + 同名 ``.log``
退出码：0 正常｜1 环境缺失（图谱未加载/CE 不可用）｜2 语义通道降级
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

from roleplay.config import get_settings  # noqa: E402
from roleplay.core.knowledge.factory import build_plot_registry  # noqa: E402
from roleplay.core.knowledge.plot_graph import (  # noqa: E402
    FUSE_MIN_SCORE,
    FUSE_MAX_SCORE,
    RetrievedChunk,
)
from roleplay.core.knowledge.plot_rerank import CrossEncoderReranker  # noqa: E402

import eval_plot_rag as E  # noqa: E402

DEFAULT_OUT = ROOT / "data" / "knowledge" / "_audit" / "ab_ce_rerank.json"
MODEL_DIR = ROOT / "models" / "bge-reranker-base-onnx"
DEFAULT_BASELINE = ROOT / "data" / "knowledge" / "_audit" / "baseline_300.json"

_LOG: list[str] = []


def log(msg: str) -> None:
    print(msg, flush=True)
    _LOG.append(str(msg))


def main() -> int:
    ap = argparse.ArgumentParser(description="bge-reranker 交叉编码器精排标定")
    ap.add_argument("--character", default="wu_ming_zhe")
    ap.add_argument("--k", nargs="+", type=int, default=[20, 30, 50],
                    help="候选池大小（五通道并集 cap 到 k）")
    ap.add_argument("--limit", type=int, default=0, help="只跑前 N 题（冒烟）")
    ap.add_argument("--out", default=str(DEFAULT_OUT))
    ap.add_argument("--baseline", default=str(DEFAULT_BASELINE))
    ap.add_argument("--allow-degraded", action="store_true")
    args = ap.parse_args()

    out_path = Path(args.out)
    log_path = out_path.with_suffix(out_path.suffix + ".log")

    settings = get_settings()
    registry = build_plot_registry(settings)
    retr = registry.get(args.character)
    if retr is None:
        log("[FAIL] 剧情图谱未加载")
        return 1
    sem = getattr(retr, "semantic", None)
    if sem is None and not args.allow_degraded:
        log("[FAIL] 语义通道已降级（--allow-degraded 可强行继续）")
        return 2

    # ── 交叉编码器（已存在未启用的 CrossEncoderReranker）──
    ce = CrossEncoderReranker(model_dir=str(MODEL_DIR), onnx_file="onnx/model_int8.onnx")
    if not ce.available():
        log(f"[FAIL] 交叉编码器不可用：{ce.last_error}")
        return 1
    log(f"[CE] 已加载：{MODEL_DIR} / onnx/model_int8.onnx")

    top = int(getattr(settings, "plot_max_chunks", 6) or 6)
    lex_fb = int(getattr(settings, "plot_lexical_fallback", 2) or 0)
    inject_chars = int(getattr(settings, "plot_context_max_chars", 2400) or 0)
    budget = top + max(0, lex_fb)

    items = E.load_testset(None)
    oracle = E.build_oracle(retr.corpus, items)
    log(f"[load] 题集 {len(items)}｜top={top}｜lexical_fallback={lex_fb}｜预算 {budget} 块")

    # spy：捕获融合前全通道候选（裸 PlotChunk，去重，cap 到本次 k）
    cap: dict[str, list] = {"pool": []}
    orig_fuse = retr._fuse_channels

    def spy(channels, *, limit):
        seen: list[tuple[str, float, object, dict]] = []
        seen_h: set[str] = set()
        for _path, _w, ch_items in channels:
            for score, c, extra in ch_items:
                h = str(getattr(c, "hash", "") or "")
                if h and h not in seen_h:
                    seen_h.add(h)
                    seen.append((str(_path), float(score), c, dict(extra or {})))
        cap["pool"] = seen
        return orig_fuse(channels, limit=limit)

    retr._fuse_channels = spy

    def make_rerank(k: int, timings: list):
        """返回 chunks_transform：对 k 候选池做交叉编码器精排，取 top-budget 包回。

        ``timings`` 收集每次调用的 CE 精排墙钟（含打分+包回），用于**独立**度量
        生产路径的 p95 增量（evaluate_case 的 latency_ms 只计 retrieve、不含 transform，
        不能直接当增量基准）。
        """
        def fn(query: str, chunks: list) -> list:
            pool = cap.get("pool") or []
            if not pool:
                return chunks
            # 五通道并集去重后 cap 到 k
            capped = pool[:k]
            t0 = time.perf_counter()
            try:
                scored = []
                for (_path, _sc, c, extra) in capped:
                    s = ce.score_pair(query, str(getattr(c, "text", "") or ""))
                    scored.append((float(s), c, extra))
                if not scored:
                    return chunks
                scored.sort(key=lambda t: -t[0])
            except Exception as exc:  # 推理异常 → 降级为原序（与生产一致）
                log(f"  [warn] CE 推理异常：{exc!r}")
                return chunks
            finally:
                timings.append((time.perf_counter() - t0) * 1000.0)
            picked = scored[:budget]
            raw = [s for s, _c, _e in picked]
            lo, hi = min(raw), max(raw)
            span = (hi - lo) or 1.0
            ceil = FUSE_MAX_SCORE - 1e-3
            out: list = []
            for s, c, extra in picked:
                frac = (s - lo) / span
                norm = FUSE_MIN_SCORE + (ceil - FUSE_MIN_SCORE) * frac
                meta = c.meta(retr.namespace)
                meta.update(extra or {})
                meta["ce_rerank"] = True
                meta["ce_pool_k"] = k
                out.append(RetrievedChunk(text=c.text, score=float(norm), metadata=meta))
            return out
        return fn

    def run_negatives(k: int, timings: list) -> dict:
        """负样本：套用同款 transform，并用主评测 evaluate_negatives 对偶校验。"""
        transform = make_rerank(k, timings)
        total = 0
        cases_with = 0
        dirty: list[str] = []
        for _cat, q in E.NEGATIVE_CASES:
            cap["pool"] = []
            chunks = retr.retrieve(q, top_chunks=top, lexical_fallback=lex_fb)
            chunks = transform(q, chunks)
            n = len(chunks)
            total += n
            if n:
                cases_with += 1
                dirty.append(q)
        known = set(getattr(E, "KNOWN_RESIDUAL_NEGATIVES", ()) or ())
        ref = E.evaluate_negatives(retr, top, lex_fb)
        ref_cases = len(ref.get("violations") or [])
        ref_blocks = ref.get("negative_injection_total")
        consistent = (ref_cases == cases_with and ref_blocks == total)
        if not consistent:
            log(f"  [warn] 负样本口径不一致：本函数 {cases_with} 条/{total} 块 "
                f"vs 主评测 {ref_cases} 条/{ref_blocks} 块")
        return {
            "cases": len(E.NEGATIVE_CASES),
            "cases_with_injection": cases_with,
            "injection_total": total,
            "violations": list(dirty),
            "new_leaks": [q for q in dirty if q not in known],
            "crosscheck_main_eval": {
                "cases_with_injection": ref_cases,
                "injection_total": ref_blocks,
                "consistent": consistent,
            },
        }

    def run(label: str, k: int) -> dict:
        t0 = time.time()
        n_pass = n_inj = 0
        pool_sizes: list[int] = []
        ce_timings: list[float] = []
        limit = args.limit or len(items)
        for item in items[:limit]:
            cap["pool"] = []
            row = E.evaluate_case(retr, item, oracle[str(item.get("id"))], top, lex_fb,
                                  inject_chars, chunks_transform=make_rerank(k, ce_timings))
            n_pass += int(bool(row.get("strict_pass")))
            n_inj += int(bool(row.get("inject_pass")))
            pool_sizes.append(len(cap["pool"]))
        neg = run_negatives(k, ce_timings)
        ce_p95 = round(E.percentile(ce_timings, 0.95), 1) if ce_timings else 0.0
        ce_p50 = round(E.percentile(ce_timings, 0.50), 1) if ce_timings else 0.0
        r = {
            "label": label, "k": k,
            "strict_pass_n": n_pass, "strict_pass": round(n_pass / limit, 4),
            "inject_pass_n": n_inj, "inject_pass": round(n_inj / limit, 4),
            "pool_avg": round(sum(pool_sizes) / max(1, len(pool_sizes)), 1),
            "pool_k": k,
            "ce_latency_p50_ms": ce_p50,
            "ce_latency_p95_ms": ce_p95,
            "negatives": {
                "cases": neg["cases"],
                "cases_with_injection": neg["cases_with_injection"],
                "injection_total": neg["injection_total"],
                "new_leaks": neg["new_leaks"],
                "crosscheck_main_eval": neg["crosscheck_main_eval"],
            },
            "elapsed_s": round(time.time() - t0, 1),
        }
        xc = r["negatives"].get("crosscheck_main_eval") or {}
        log(f"  [{label}] strict {n_pass}/{limit}｜inject {n_inj}/{limit}"
            f"｜候选池均 {r['pool_avg']} 块"
            f"｜负样本失守 {neg['cases_with_injection']}/{neg['cases']} 条"
            f"（注入 {neg['injection_total']} 块，新增泄漏 {len(neg['new_leaks'] or [])}，"
            f"对偶校验 {'一致' if xc.get('consistent') else '不一致'}）｜{r['elapsed_s']}s")
        return r

    # 延迟口径取无埋点运行；p95 直接读 aggregate 的 latency_p95_ms。
    results = []
    for k in args.k:
        results.append(run(f"CE k={k}", k))

    retr._fuse_channels = orig_fuse

    # ── 与基线对齐 ──
    base = {"strict_pass_n": None, "inject_pass_n": None,
            "neg_cases": None, "neg_blocks": None, "latency_p95_ms": None,
            "neg_violations": None}
    bp = Path(args.baseline)
    if bp.is_file():
        b = json.loads(bp.read_text(encoding="utf-8"))
        base["strict_pass_n"] = b.get("summary", {}).get("strict_pass_n")
        base["inject_pass_n"] = b.get("summary", {}).get("inject_pass_n")
        base["neg_cases"] = (b.get("negatives", {}) or {}).get("cases_with_injection")
        base["neg_blocks"] = (b.get("negatives", {}) or {}).get("negative_injection_total")
        base["latency_p95_ms"] = (b.get("summary", {}) or {}).get("latency_p95_ms")
        base["neg_violations"] = (b.get("negatives", {}) or {}).get("violations")
        log(f"[base] 基线 strict={base['strict_pass_n']} inject={base['inject_pass_n']} "
            f"负样本失守={base['neg_cases']} 条 / 注入={base['neg_blocks']} 块 "
            f"p95={base['latency_p95_ms']}ms")
    else:
        log("[warn] 未找到基线 JSON，跳过 delta 计算（仅报原始数）")

    # 每个 k 的负样本：与基线 violation 集合对比，得到「真正新增的泄漏」
    for r in results:
        nv = base.get("neg_violations") or []
        r["negatives"]["new_vs_baseline"] = [
            q for q in r["negatives"].get("violations", [])
            if q not in set(nv)
        ]

    report = {
        "generated_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        "config": {"top": top, "lexical_fallback": lex_fb,
                   "inject_chars": inject_chars, "budget": budget,
                   "ks": list(args.k), "model_dir": str(MODEL_DIR),
                   "onnx": "onnx/model_int8.onnx", "cases": args.limit or len(items)},
        "baseline": base,
        "results": results,
        "delta_vs_baseline": [
            {
                "k": r["k"],
                "d_strict": ((r["strict_pass_n"] or 0) - (base["strict_pass_n"] or 0))
                            if base["strict_pass_n"] is not None else None,
                "d_inject": ((r["inject_pass_n"] or 0) - (base["inject_pass_n"] or 0))
                            if base["inject_pass_n"] is not None else None,
                "d_neg_cases": ((r["negatives"]["cases_with_injection"] or 0)
                                - (base["neg_cases"] or 0))
                            if base["neg_cases"] is not None else None,
                "d_neg_blocks": ((r["negatives"]["injection_total"] or 0)
                                 - (base["neg_blocks"] or 0))
                            if base["neg_blocks"] is not None else None,
            }
            for r in results
        ],
    }
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    log_path.write_text("\n".join(_LOG), encoding="utf-8")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except SystemExit:
        raise
    except BaseException as exc:  # noqa: BLE001
        import traceback
        try:
            Path(str(DEFAULT_OUT) + ".crash").write_text(
                f"{time.strftime('%Y-%m-%d %H:%M:%S')}\n{traceback.format_exc()}",
                encoding="utf-8")
        except Exception:
            pass
        print(f"[CRASH] {exc!r}", flush=True)
        raise
