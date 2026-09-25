# -*- coding: utf-8 -*-
"""语义候选池深度消融（只改运行时实例属性，不改配置、不改检索代码）。

为什么做这个实验
-----------------
``diag_block_provenance.py`` 实测：105 道失败题里 **60 题（57%）的正解块从未进入任何
通道候选池**（``never_candidate``），只有 27 题（26%）属于"进过候选池但被融合挤出"。
也就是说旧结论「100/105 是被融合挤掉的」不成立，主战场是**召回面**——候选池太浅。

最便宜的召回面杠杆就是 ``semantic_top``：当前 **5**，即语义通道最多只向融合层交 5 个块
（``plot_graph.retrieve`` 里 ``semantic.search(qvec, self.semantic_top)``）。
它是既有的运行期属性，改它不需要动配置、不需要改代码，且已有 ``semantic_min_score``
与种子门控兜底精度，是典型的「先验证再实现」的探针实验。

方法（配对对照，同实例、同题集、同随机源）：
  1. 先跑**生产当前值**档（``semantic_top=5``）做装置自检：strict_pass_n 必须与主评测
     基线 195 一致；不一致说明实验装置有问题，结论不可信，直接中止（退出码 3）。
  2. 再跑目标档（默认 20），报 strict / inject / 负样本注入三项。
  3. 负样本用主评测同一套 53 条（``E.evaluate_negatives``），误注入只允许持平。

用法（项目根目录）
------------------
    .venv/Scripts/python.exe -X utf8 scripts/ab_semantic_depth.py
    .venv/Scripts/python.exe -X utf8 scripts/ab_semantic_depth.py --depths 5,20,30
    .venv/Scripts/python.exe -X utf8 scripts/ab_semantic_depth.py --limit 30   # 冒烟

产物：``data/knowledge/_audit/ab_semantic_depth.json`` + 同名 ``.log``
退出码：0 正常｜1 环境缺失｜2 语义降级｜3 基线档与 195 不符（装置不可信）
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

import eval_plot_rag as E  # noqa: E402

DEFAULT_OUT = ROOT / "data" / "knowledge" / "_audit" / "ab_semantic_depth.json"
# 主评测全量基线（2026-09-17）：strict 195/300。**装置自检的锚**，不达标即中止。
BASELINE_STRICT_N = 195

_LOG: list[str] = []


def log(msg: str) -> None:
    print(msg, flush=True)
    _LOG.append(str(msg))


def run_pass(retr, items: list[dict], oracle: dict, top: int, lex_fb: int,
             inject_chars: int, label: str) -> dict:
    """跑一轮全量评测（主评测同口径），返回 summary + 负样本读数。"""
    t0 = time.time()
    rows = [E.evaluate_case(retr, it, oracle[str(it.get("id"))], top, lex_fb, inject_chars)
            for it in items]
    summary = E.aggregate(rows)
    neg = E.evaluate_negatives(retr, top, lex_fb)
    # 口径说明：``negative_injection_total`` 是**块数**（一条负样本可能返回多块），
    # 而护栏判据是「**逐条**零注入」。两者必须并列报：只看块数会把"1 条漏 5 块"
    # 和"5 条各漏 1 块"混为一谈，而它们的修法完全不同。
    neg_cases = len(neg.get("violations") or [])
    log(f"  [{label}] strict {summary.get('strict_pass_n')}/{len(items)}"
        f" ({summary.get('strict_pass')})｜inject {summary.get('inject_pass')}"
        f"｜负样本失守 {neg_cases}/{neg.get('cases')} 条"
        f"（新增泄漏 {len(neg.get('new_leaks') or [])}，注入 {neg.get('negative_injection_total')} 块）"
        f"｜耗时 {time.time() - t0:.0f}s")
    return {
        "label": label,
        "strict_pass_n": summary.get("strict_pass_n"),
        "strict_pass": summary.get("strict_pass"),
        "inject_pass": summary.get("inject_pass"),
        "mrr": summary.get("mrr"),
        "latency_p95_ms": summary.get("latency_p95_ms"),
        "negatives": {
            "cases": neg.get("cases"),
            "cases_with_injection": neg_cases,
            "injection_total": neg.get("negative_injection_total"),
            "new_leaks": neg.get("new_leaks"),
            "clean": neg.get("negative_clean"),
        },
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="语义候选池深度消融（运行期属性，不改配置）")
    ap.add_argument("--character", default="wu_ming_zhe")
    ap.add_argument("--depths", default="5,20", help="候选池深度档位（逗号分隔，第 1 档必须为生产值）")
    ap.add_argument("--limit", type=int, default=0, help="只跑前 N 题（冒烟，不作结论）")
    ap.add_argument("--out", default=str(DEFAULT_OUT))
    ap.add_argument("--allow-degraded", action="store_true")
    ap.add_argument("--skip-selfcheck", action="store_true",
                    help="跳过与 195 基线的装置自检（仅限 --limit 冒烟时使用）")
    args = ap.parse_args()

    out_path = Path(args.out)
    log_path = out_path.with_suffix(out_path.suffix + ".log")
    depths = [int(x) for x in str(args.depths).split(",") if str(x).strip()]

    settings = get_settings()
    registry = build_plot_registry(settings)
    retr = registry.get(args.character)
    if retr is None:
        log(f"[FAIL] 剧情图谱未加载（{args.character}）")
        return 1
    if getattr(retr, "semantic", None) is None and not args.allow_degraded:
        log("[FAIL] 语义通道已降级，拒绝出报告（--allow-degraded 可强行继续）")
        return 2

    top = int(getattr(settings, "plot_max_chunks", 3) or 3)
    lex_fb = int(getattr(settings, "plot_lexical_fallback", 2) or 0)
    inject_chars = int(getattr(settings, "plot_context_max_chars", 1000) or 0)
    prod_depth = int(getattr(retr, "semantic_top", 5))
    items = E.load_testset(None)
    if args.limit:
        items = items[: args.limit]
    oracle = E.build_oracle(retr.corpus, items)
    log(f"[load] 题量 {len(items)}｜top={top}｜lexical_fallback={lex_fb}"
        f"｜inject_chars={inject_chars}｜生产 semantic_top={prod_depth}")

    results: list[dict[str, Any]] = []
    for d in depths:
        retr.semantic_top = d
        r = run_pass(retr, items, oracle, top, lex_fb, inject_chars, f"semantic_top={d}")
        r["semantic_top"] = d
        results.append(r)
        # 装置自检：生产档必须复现 195，否则本轮所有读数作废
        if d == prod_depth and not args.skip_selfcheck and not args.limit:
            if r["strict_pass_n"] != BASELINE_STRICT_N:
                log(f"[FAIL] 装置自检不通过：生产档 strict {r['strict_pass_n']} ≠ 基线 "
                    f"{BASELINE_STRICT_N}。本轮读数不可信，已中止。")
                report = {"generated_at": time.strftime("%Y-%m-%d %H:%M:%S"),
                          "selfcheck": "FAILED", "results": results}
                out_path.write_text(json.dumps(report, ensure_ascii=False, indent=2),
                                    encoding="utf-8")
                log_path.write_text("\n".join(_LOG), encoding="utf-8")
                return 3
            log(f"  [selfcheck] 生产档复现基线 {BASELINE_STRICT_N} ✓ 装置可信")

    retr.semantic_top = prod_depth  # 还原运行期属性

    base = results[0]
    report = {
        "generated_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        "character": args.character,
        "config": {"top": top, "lexical_fallback": lex_fb, "inject_chars": inject_chars,
                   "prod_semantic_top": prod_depth, "items": len(items)},
        "selfcheck": "PASSED" if base["strict_pass_n"] == BASELINE_STRICT_N else "SKIPPED",
        "results": results,
        "delta_vs_prod": [
            {
                "semantic_top": r["semantic_top"],
                "d_strict_pass_n": (r["strict_pass_n"] or 0) - (base["strict_pass_n"] or 0),
                "d_inject_pass": (round((r["inject_pass"] or 0) - (base["inject_pass"] or 0), 4)
                                  if r["inject_pass"] is not None and base["inject_pass"] is not None
                                  else None),
                "d_neg_cases": (r["negatives"]["cases_with_injection"] or 0)
                               - (base["negatives"]["cases_with_injection"] or 0),
                "d_neg_blocks": (r["negatives"]["injection_total"] or 0)
                                - (base["negatives"]["injection_total"] or 0),
                "new_leaks": r["negatives"]["new_leaks"],
            }
            for r in results
        ],
    }
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    log("\n==== 摘要 ====")
    for row in report["delta_vs_prod"]:
        log(f"semantic_top={row['semantic_top']:>3}  Δstrict={row['d_strict_pass_n']:+d} 题"
            f"  Δinject={row['d_inject_pass']}"
            f"  Δ负样本失守={row['d_neg_cases']:+d} 条 / Δ块数={row['d_neg_blocks']:+d}"
            f"  新增泄漏={row['new_leaks']}")
    log(f"[out] {out_path}")
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
