# -*- coding: utf-8 -*-
"""reranker 收益验证（离线 A/B，复用主评测的判定口径）。

⚠️ 血泪教训（2026-09-16 第一版踩到）：
    初版脚本自建了 strict/inject 判定（简化拼装 + 漏传 lexical_fallback），
    结果基线 strict 72.67% 而主评测是 67.67% —— **口径不一致，结论完全不可比**，
    还差点把"40 题抽样 +7.5pt"的小样本噪声当成真收益。
    现改为**复用 `eval_plot_rag.evaluate_case`**，只通过 `chunks_transform` 钩子注入重排。

实验设计（严格单变量）：
    两次运行都用 top=rerank_pool 召回同一批候选，再截断到同样的 keep 块数；
    唯一差别是「截断前是否重排」。判定口径完全一致。

用法：
    .venv/Scripts/python.exe -X utf8 scripts/ab_rerank_plot.py --limit 60
    .venv/Scripts/python.exe -X utf8 scripts/ab_rerank_plot.py --limit 0 --model qwen2.5:7b
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
from roleplay.core.knowledge.plot_rerank import PlotReranker  # noqa: E402

AUDIT = ROOT / "data" / "knowledge" / "_audit"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=60)
    ap.add_argument("--model", default="qwen2.5:1.5b")
    ap.add_argument("--pool", type=int, default=10, help="召回候选数（送重排）")
    ap.add_argument("--keep", type=int, default=8, help="截断后保留块数（= top + lexical_fallback）")
    ap.add_argument("--budget", type=int, default=2400)
    ap.add_argument("--out", default="ab_rerank_plot.json",
                    help="报告文件名（相对 data/knowledge/_audit/）；多模型对比时用不同名字避免互相覆盖")
    args = ap.parse_args()

    cases = json.loads(E.TESTSET_PATH.read_text(encoding="utf-8")) if False else \
        json.loads((AUDIT / "rag_testset_300_clean.json").read_text(encoding="utf-8"))
    if args.limit:
        cases = cases[: args.limit]

    s = get_settings()
    retr = build_plot_registry(s).get("wu_ming_zhe")
    oracle = E.build_oracle(retr.corpus, cases)
    rer = PlotReranker(model=args.model, base_url="http://localhost:11434", timeout=90.0)
    if not rer.available():
        print(f"[FAIL] 重排模型不可用：{args.model}")
        return 2
    print(f"[ab] 题量 {len(cases)}｜pool={args.pool}｜keep={args.keep}｜模型 {args.model}"
          f"｜预算 {args.budget}（判定复用主评测 evaluate_case）")

    def trunc(q, chunks):
        return chunks[: args.keep]

    def rerank(q, chunks):
        if len(chunks) <= 1:
            return chunks
        items = [(float(getattr(c, "score", 0.0) or 0.0), c, {}) for c in chunks]
        out = rer.rerank(q, items, top_k=args.keep)
        return [it[1] for it in out]

    n = len(cases)
    agg = {"base_strict": 0, "rr_strict": 0, "base_inject": 0, "rr_inject": 0}
    lat_rr: list[float] = []
    for item in cases:
        row_b = E.evaluate_case(retr, item, oracle[str(item["id"])], args.pool,
                                0, args.budget, chunks_transform=trunc)
        t0 = time.perf_counter()
        row_r = E.evaluate_case(retr, item, oracle[str(item["id"])], args.pool,
                                0, args.budget, chunks_transform=rerank)
        lat_rr.append((time.perf_counter() - t0) * 1000)
        if row_b.get("strict_pass"):
            agg["base_strict"] += 1
        if row_r.get("strict_pass"):
            agg["rr_strict"] += 1
        if row_b.get("inject_pass"):
            agg["base_inject"] += 1
        if row_r.get("inject_pass"):
            agg["rr_inject"] += 1

    print()
    print("=" * 66)
    print(f"{'指标（主评测口径）':<24}{'不重排':>13}{'重排后':>13}{'变化':>13}")
    for key, label in (("strict", "strict_pass"), ("inject", "inject_pass")):
        a, b = agg[f"base_{key}"], agg[f"rr_{key}"]
        print(f"{label:<24}{a / n:>13.4f}{b / n:>13.4f}{(b - a) / n:>+13.4f}")
    print("=" * 66)
    print(f"平均单题重排耗时：{statistics.mean(lat_rr):.0f} ms")

    out = AUDIT / args.out
    out.write_text(json.dumps({
        "meta": {"model": args.model, "pool": args.pool, "keep": args.keep,
                 "cases": n, "note": "复用 eval_plot_rag.evaluate_case 口径"},
        "stat": {k: v / n for k, v in agg.items()},
        "lat_rerank_ms": round(statistics.mean(lat_rr), 1),
    }, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"[save] {out.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
