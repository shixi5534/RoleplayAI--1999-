# -*- coding: utf-8 -*-
"""T4：HippoRAG 式「PPR 引导 dense 排序」实验（不改检索代码，运行期 patch）。

动机（文献 + 实测）
--------------------
- 本项目架构与 HippoRAG（NeurIPS 2024）同构：PPR 图传播 + 知识图谱 + dense 相似度。
  差距在融合方式：HippoRAG 用 PPR 实体分布**引导** dense 检索与排序；
  我们语义通道是"按 cosine 名次"扁平进 RRF。
- 实测：multi-hop 通过率两份题集一致地低（45–50%），HippoRAG 同任务 recall@5 83–96%。

做法（monkeypatch ``semantic.search``，主评测口径判定）
------------------------------------------------------
1. 候选池扩大：原查询先取 cosine top-30（不只 top-5）；
2. 块的 PPR 权重：PPR 分数 top-M 实体 → ``_name_hits(正名)`` 倒排命中块 →
   按 ``PPR分 × 名字权重 × (1+0.3·ln 次数)`` 累加到块（与 mention 通道同口径）；
3. 融合排序：``score = cosine + β · ppr_norm``，仍取 ``top_k`` 个（通道规模不变，
   这是"整体重排 inject −26"教训后的硬约束：只动排序，不动名额结构）；
4. 判定完全复用 ``eval_plot_rag.evaluate_case`` 主口径；负样本必跑。

无种子 / 无 PPR 的题自动退化为原序（安全降级）。

用法（项目根目录）
------------------
    .venv/Scripts/python.exe -X utf8 scripts/ab_ppr_dense.py --beta 0.1 --limit 20   # 冒烟
    .venv/Scripts/python.exe -X utf8 scripts/ab_ppr_dense.py --beta 0.05 0.1 0.2     # 全量扫

产物：``data/knowledge/_audit/ab_ppr_dense.json`` + 同名 ``.log``
退出码：0 正常｜1 环境缺失｜2 语义降级
"""
from __future__ import annotations

import argparse
import json
import math
import sys
import time
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

from roleplay.config import get_settings  # noqa: E402
from roleplay.core.knowledge.factory import build_plot_registry  # noqa: E402

import diag_seedless_ceiling as D  # noqa: E402
import eval_plot_rag as E  # noqa: E402

DEFAULT_OUT = ROOT / "data" / "knowledge" / "_audit" / "ab_ppr_dense.json"
POOL = 30          # 候选池：cosine top-30（比通道 top-5 大，给 PPR 重排留空间）
PPR_TOP_M = 50     # 参与"块权重"计算的 PPR 实体数上限

_LOG: list[str] = []


def log(msg: str) -> None:
    print(msg, flush=True)
    _LOG.append(str(msg))


def main() -> int:
    ap = argparse.ArgumentParser(description="PPR 引导 dense 排序实验")
    ap.add_argument("--character", default="wu_ming_zhe")
    ap.add_argument("--testset", default="", help="默认 300 题基准")
    ap.add_argument("--betas", nargs="+", type=float, default=[0.1],
                    help="PPR 权重系数（可多档）")
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--out", default=str(DEFAULT_OUT))
    ap.add_argument("--allow-degraded", action="store_true")
    args = ap.parse_args()

    out_path = Path(args.out)
    log_path = out_path.with_suffix(out_path.suffix + ".log")

    settings = get_settings()
    registry = build_plot_registry(settings)
    retr = registry.get(args.character)
    if retr is None:
        log("[FAIL] 图谱未加载")
        return 1
    sem = getattr(retr, "semantic", None)
    if sem is None and not args.allow_degraded:
        log("[FAIL] 语义通道已降级（--allow-degraded 可强行继续）")
        return 2

    top = int(getattr(settings, "plot_max_chunks", 3) or 3)
    lex_fb = int(getattr(settings, "plot_lexical_fallback", 2) or 0)
    inject_chars = int(getattr(settings, "plot_context_max_chars", 1000) or 0)
    items = E.load_testset(Path(args.testset) if args.testset else None)
    if args.limit:
        items = items[: args.limit]
    oracle = E.build_oracle(retr.corpus, items)
    log(f"[load] 题量 {len(items)}｜top={top}｜lexical_fallback={lex_fb}｜betas={args.betas}")

    # 预建：hash → 块下标（_name_hits 用块下标）；eid → 正名
    hash2idx = {str(getattr(c, "hash", "") or ""): i
                for i, c in enumerate(retr.corpus.chunks)}
    name_of: dict[str, str] = {}
    for ent in retr.store.entities():
        nm = str((ent or {}).get("name") or "").strip()
        if nm:
            name_of[str(ent.get("id"))] = nm
    log(f"[idx] 语料 {len(hash2idx)} 块｜实体 {len(name_of)}")

    # ── patch：语义通道候选池扩大 + PPR 权重重排 ────────────────────────────
    orig_search = sem.search
    state: dict[str, Any] = {"beta": 0.0}

    def patched_search(qvec, top_k=5):
        base = orig_search(qvec, POOL)
        ppr = getattr(retr, "_qr_ppr", None)
        beta = state["beta"]
        if not ppr or beta <= 0 or not base:
            return orig_search(qvec, top_k)
        # 块 PPR 权重（PPR top-M 实体的名字倒排，口径与 mention 通道一致）
        w: dict[int, float] = {}
        ranked = sorted(ppr.items(), key=lambda kv: -kv[1])[:PPR_TOP_M]
        for eid, s in ranked:
            nm = name_of.get(str(eid))
            if not nm:
                continue
            hits, weight = retr._name_hits(nm)
            if not hits:
                continue
            contrib = float(s) * float(weight)
            for ci, cnt in hits.items():
                w[ci] = w.get(ci, 0.0) + contrib * (1.0 + 0.3 * math.log(max(1, cnt)))
        if not w:
            return orig_search(qvec, top_k)
        mx = max(w.values()) or 1.0
        merged: dict[str, float] = {}
        for h, s in base:
            ci = hash2idx.get(str(h))
            bonus = beta * (w.get(ci, 0.0) / mx) if ci is not None else 0.0
            merged[str(h)] = float(s) + bonus
        out = sorted(merged.items(), key=lambda kv: -kv[1])
        return out[: max(int(top_k), 5)]

    def run(label: str, beta: float) -> dict[str, Any]:
        state["beta"] = beta
        sem.search = patched_search if beta > 0 else orig_search
        t0 = time.time()
        n_pass = 0
        n_inj = 0
        by_type: dict[str, dict[str, int]] = {}
        rows_meta: list[dict] = []
        for it in items:
            q = str(it.get("q"))
            qid = str(it.get("id"))
            ttype = str((it.get("dims") or {}).get("type") or "")
            seeds = retr.seed_gate(retr.link_detailed(q))
            retr._qr_ppr = retr._ppr(seeds) if seeds else None
            row = E.evaluate_case(retr, it, oracle[qid], top, lex_fb, inject_chars)
            ok = bool(row.get("strict_pass"))
            n_pass += int(ok)
            n_inj += int(bool(row.get("inject_pass")))
            by_type.setdefault(ttype, {"n": 0, "p": 0})
            by_type[ttype]["n"] += 1
            by_type[ttype]["p"] += int(ok)
            if not ok:
                rows_meta.append({"id": qid, "type": ttype})
        retr._qr_ppr = None
        neg = E.evaluate_negatives(retr, top, lex_fb)
        r = {
            "label": label, "beta": beta,
            "strict_pass_n": n_pass, "strict_pass": D.rate(n_pass, len(items)),
            "inject_pass_n": n_inj, "inject_pass": D.rate(n_inj, len(items)),
            "by_type": {k: {"n": v["n"], "pass": v["p"], "rate": D.rate(v["p"], v["n"])}
                        for k, v in sorted(by_type.items())},
            "negatives": {"cases": neg.get("cases"),
                          "cases_with_injection": len(neg.get("violations") or []),
                          "injection_total": neg.get("negative_injection_total"),
                          "new_leaks": neg.get("new_leaks")},
            "elapsed_s": round(time.time() - t0, 1),
        }
        log(f"  [{label}] strict {n_pass}/{len(items)}｜inject {n_inj}"
            f"｜负样本失守 {r['negatives']['cases_with_injection']}/{r['negatives']['cases']} 条"
            f"（注入 {r['negatives']['injection_total']} 块）｜{r['elapsed_s']}s")
        for t, v in r["by_type"].items():
            log(f"    {t:10s} {v['pass']}/{v['n']}（{v['rate']}）")
        return r

    results = [run("基线（无 PPR 引导）", 0.0)]
    for b in args.betas:
        results.append(run(f"PPR引导 β={b}", b))
    sem.search = orig_search

    base = results[0]
    report = {
        "generated_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        "config": {"cases": len(items), "top": top, "lexical_fallback": lex_fb,
                   "inject_chars": inject_chars, "pool": POOL, "ppr_top_m": PPR_TOP_M},
        "results": results,
        "delta": [{"beta": r["beta"],
                   "d_strict": r["strict_pass_n"] - base["strict_pass_n"],
                   "d_inject": r["inject_pass_n"] - base["inject_pass_n"],
                   "d_neg_cases": (r["negatives"]["cases_with_injection"]
                                   - base["negatives"]["cases_with_injection"])}
                  for r in results],
        "fail_ids_baseline": [c["id"] for c in []],
    }
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    log("\n==== 摘要 ====")
    for d in report["delta"]:
        log(f"beta={d['beta']:<5} Δstrict={d['d_strict']:+d} 题"
            f"　Δinject={d['d_inject']:+d} 题　Δ负样本失守={d['d_neg_cases']:+d} 条")
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
