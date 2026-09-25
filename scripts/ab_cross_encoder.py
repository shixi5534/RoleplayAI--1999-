# -*- coding: utf-8 -*-
"""Cross-Encoder 重排离线 A/B（全量 300 题）。

口径纪律（历史教训，勿违反）
    · **复用 `eval_plot_rag.evaluate_case`**，禁止自造判定。
      v1 实验脚本自建口径导致基线 72.67% ≠ 主评测 67.67%，结论全部作废。
    · 两次运行只差「截断前是否重排」一个变量，且**共用同一次检索**（同批次）。
    · 判定以 **inject_pass** 为准（strict_pass 可被多返回块灌水）。

额外观测（比汇总指标更能说明机制）
    · ``top2_hit``：证据块是否落在**前 2 名**——产品按 2400 字符装配只装得下约 2 块，
      这才是重排真正要改善的东西（见 docs/排序靶子_证据块名次分布_20260916.md）。

用法：
    .venv/Scripts/python.exe -X utf8 scripts/ab_cross_encoder.py
    .venv/Scripts/python.exe -X utf8 scripts/ab_cross_encoder.py --combos int8:20
"""
from __future__ import annotations

import argparse
import json
import statistics
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

import eval_plot_rag as E  # noqa: E402
from roleplay.config import get_settings  # noqa: E402
from roleplay.core.knowledge.factory import build_plot_registry  # noqa: E402
from roleplay.core.knowledge.plot_rerank import CrossEncoderReranker  # noqa: E402

AUDIT = ROOT / "data" / "knowledge" / "_audit"
AB = AUDIT / "ablation"
TESTSET = AUDIT / "rag_testset_300_clean.json"
MODEL_DIR = ROOT / "models" / "bge-reranker-base-onnx"
BUDGET = 2400


def top2_hit(chunks, full) -> bool:
    return any(E.chunk_hash(c.text) in full for c in chunks[:2])


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--combos", default="int8:20,int8:10,fp32:20",
                    help="模型变体:pool 组合，逗号分隔")
    ap.add_argument("--limit", type=int, default=0)
    args = ap.parse_args()

    cases = json.loads(TESTSET.read_text(encoding="utf-8"))
    if args.limit:
        cases = cases[: args.limit]
    n = len(cases)

    s = get_settings()
    retr = build_plot_registry(s).get("wu_ming_zhe")
    oracle = E.build_oracle(retr.corpus, cases)
    top_prod = int(getattr(s, "plot_max_chunks", 6))
    lf_prod = int(getattr(s, "plot_lexical_fallback", 2))
    keep = top_prod + lf_prod

    log: list[str] = []

    def p(*a):
        line = " ".join(str(x) for x in a)
        log.append(line)
        print(line, flush=True)

    p(f"题量 {n}｜生产返回上限 {keep}（{top_prod}+{lf_prod}）｜注入预算 {BUDGET}")
    p("=" * 96)

    results: list[dict] = []
    for combo in args.combos.split(","):
        parts = combo.split(":")
        variant, pool_s = parts[0], parts[1]
        alpha = float(parts[2]) if len(parts) > 2 else 1.0
        pool = int(pool_s)
        onnx_file = "onnx/model_int8.onnx" if variant == "int8" else "onnx/model.onnx"
        rr = CrossEncoderReranker(model_dir=str(MODEL_DIR), onnx_file=onnx_file,
                                  max_len=512, max_chars=1200)
        if not rr.available():
            p(f"[SKIP] {combo} 模型不可用：{rr.last_error}")
            continue

        agg = {"base_strict": 0, "ce_strict": 0, "base_inject": 0, "ce_inject": 0,
               "base_top2": 0, "ce_top2": 0}
        lat: list[float] = []
        rows: list[dict] = []
        t_start = time.time()
        for item in cases:
            full = oracle[str(item["id"])]["full"]

            def trunc(q, chunks, _k=keep):
                return chunks[:_k]

            # evaluate_case 内部会自己检索一次，transform 是被它回调的。
            # 这里用闭包捕获两轮各自的真实输出，避免额外检索 / 重复重排。
            seen: dict[str, list] = {}

            def trunc(q, chunks, _k=keep):
                out = chunks[:_k]
                seen["base"] = out
                return out

            def rerank(q, chunks, _k=keep, _r=rr, _a=alpha):
                if len(chunks) <= 1:
                    seen["ce"] = chunks
                    return chunks
                items = [(float(getattr(c, "score", 0.0) or 0.0), c, {}) for c in chunks]
                ce_out = [c for _s, c, _m in _r.rerank(q, items, top_k=len(chunks))]
                if _a >= 1.0:
                    out = ce_out[:_k]
                else:
                    # 名次融合：两套分数量纲不同（CE logit vs 检索 RRF 分），
                    # 直接加权相加无意义，改用与量纲无关的**名次**线性插值。
                    pos_ce = {id(c): i for i, c in enumerate(ce_out)}
                    pos_or = {id(c): i for i, c in enumerate(chunks)}
                    out = sorted(chunks,
                                 key=lambda c: (1 - _a) * pos_or[id(c)]
                                 + _a * pos_ce[id(c)])[:_k]
                seen["ce"] = out
                return out

            row_b = E.evaluate_case(retr, item, oracle[str(item["id"])], pool, 0,
                                    BUDGET, chunks_transform=trunc)
            t0 = time.perf_counter()
            row_c = E.evaluate_case(retr, item, oracle[str(item["id"])], pool, 0,
                                    BUDGET, chunks_transform=rerank)
            lat.append((time.perf_counter() - t0) * 1000)

            agg["base_strict"] += bool(row_b.get("strict_pass"))
            agg["ce_strict"] += bool(row_c.get("strict_pass"))
            agg["base_inject"] += bool(row_b.get("inject_pass"))
            agg["ce_inject"] += bool(row_c.get("inject_pass"))
            agg["base_top2"] += top2_hit(seen.get("base") or [], full)
            agg["ce_top2"] += top2_hit(seen.get("ce") or [], full)
            # 逐题明细：用来验证「相关性 ≠ 覆盖率」假设（按证据组数分层看）
            rows.append({
                "id": item.get("id"),
                "n_groups": len(item.get("evidence") or []),
                "base_inject": bool(row_b.get("inject_pass")),
                "ce_inject": bool(row_c.get("inject_pass")),
                "base_top2": bool(top2_hit(seen.get("base") or [], full)),
                "ce_top2": bool(top2_hit(seen.get("ce") or [], full)),
                "base_strict": bool(row_b.get("strict_pass")),
                "ce_strict": bool(row_c.get("strict_pass")),
            })

        rec = {
            "combo": combo, "pool": pool, "keep": keep, "model": onnx_file,
            "alpha": alpha,
            "base_strict": agg["base_strict"] / n, "ce_strict": agg["ce_strict"] / n,
            "base_inject": agg["base_inject"] / n, "ce_inject": agg["ce_inject"] / n,
            "base_top2": agg["base_top2"] / n, "ce_top2": agg["ce_top2"] / n,
            "lat_ms_median": statistics.median(lat), "lat_ms_mean": statistics.mean(lat),
            "elapsed_s": time.time() - t_start,
        }
        results.append(rec)
        # 每完成一个组合就落盘，便于中途查看，也避免长跑中断丢失全部结果
        (AB / f"cross_encoder_rows_{combo.replace(':', '_')}.json").write_text(
            json.dumps(rows, ensure_ascii=False, indent=1), encoding="utf-8")
        (AB / "cross_encoder_ab.json").write_text(
            json.dumps({"cases": n, "params": {"budget": BUDGET, "keep": keep},
                        "results": results}, ensure_ascii=False, indent=1),
            encoding="utf-8")
        (AB / "cross_encoder_ab.txt").write_text("\n".join(log), encoding="utf-8")
        p(f"[{combo}] inject {rec['base_inject']:.4f} → {rec['ce_inject']:.4f} "
          f"({rec['ce_inject'] - rec['base_inject']:+.4f})｜"
          f"top2 {rec['base_top2']:.4f} → {rec['ce_top2']:.4f} "
          f"({rec['ce_top2'] - rec['base_top2']:+.4f})｜"
          f"重排中位 {rec['lat_ms_median']:.0f}ms｜耗时 {rec['elapsed_s'] / 60:.1f}min")

    p("=" * 96)
    p(f"{'组合':<12}{'inject(前)':>11}{'inject(后)':>11}{'Δinject':>10}"
      f"{'top2(前)':>10}{'top2(后)':>10}{'Δtop2':>9}{'耗时ms':>9}")
    p("-" * 96)
    for r in results:
        p(f"{r['combo']:<12}{r['base_inject']:>11.4f}{r['ce_inject']:>11.4f}"
          f"{r['ce_inject'] - r['base_inject']:>+10.4f}"
          f"{r['base_top2']:>10.4f}{r['ce_top2']:>10.4f}"
          f"{r['ce_top2'] - r['base_top2']:>+9.4f}{r['lat_ms_median']:>9.0f}")
    p("-" * 96)
    p("注：inject_pass 为准；top2 是机制指标（证据块是否进前 2 名）。")
    p("    Δ 超过 ±0.02（±6 题）才视为超出噪声。")

    AB.mkdir(parents=True, exist_ok=True)
    (AB / "cross_encoder_ab.json").write_text(
        json.dumps({"cases": n, "params": {"budget": BUDGET, "keep": keep},
                    "results": results}, ensure_ascii=False, indent=1),
        encoding="utf-8")
    (AB / "cross_encoder_ab.txt").write_text("\n".join(log), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
