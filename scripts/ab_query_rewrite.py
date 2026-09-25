# -*- coding: utf-8 -*-
"""多问法改写 · 端到端验证（用预生成改写，走主评测口径）。

为什么还要这一步
----------------
``diag_query_rewrite.py`` 只证明了「改写能把 gold 块捞进语义 top-20」（+3/40 题）。
但候选池命中 ≠ 最终通过：中间还隔着 RRF 融合与 top-8 预算——
本项目已经踩过一次这个坑（候选池扩到 42 块、gold 入池 19 题，最终 strict 只 +1）。
所以**必须**用 ``eval_plot_rag.evaluate_case`` 的主口径量一次端到端收益。

接入方式（不改检索代码）
------------------------
monkeypatch ``semantic.search``：除原查询向量外，额外用**预生成的改写向量**各检索
一次，合并去重后仍取 ``top_k`` 个（保持语义通道候选规模不变，避免通道失衡）。
改写向量在每题 retrieve 前通过 ``retr._qr_extra_vecs`` 注入。

用法（项目根目录）
------------------
    .venv/Scripts/python.exe -X utf8 scripts/ab_query_rewrite.py \
        --testset data/knowledge/_audit/rag_testset_200_new.json --types multi-hop \
        --rewrites data/knowledge/_audit/diag_qr_ollama_mh40_rewrites.json \
        --out data/knowledge/_audit/ab_qr_e2e.json

产物：JSON + 同名 .log
退出码：0 正常｜1 环境缺失｜2 语义降级｜3 输入缺失
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path
from typing import Any

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

from roleplay.config import get_settings  # noqa: E402
from roleplay.core.knowledge.factory import build_plot_registry  # noqa: E402

import diag_seedless_ceiling as D  # noqa: E402
import eval_plot_rag as E  # noqa: E402

DEFAULT_OUT = ROOT / "data" / "knowledge" / "_audit" / "ab_query_rewrite.json"
DEFAULT_TESTSET = ROOT / "data" / "knowledge" / "_audit" / "rag_testset_200_new.json"

_LOG: list[str] = []


def log(msg: str) -> None:
    print(msg, flush=True)
    _LOG.append(str(msg))


def main() -> int:
    ap = argparse.ArgumentParser(description="多问法改写端到端验证")
    ap.add_argument("--character", default="wu_ming_zhe")
    ap.add_argument("--testset", default=str(DEFAULT_TESTSET))
    ap.add_argument("--rewrites", default="", help="改写缓存 JSON（{q: [改写...]}）")
    ap.add_argument("--oracle-names", action="store_true",
                    help="用题集 ref 里的标准答案名做「完美补名」上界（不经 LLM）")
    ap.add_argument("--types", default="", help="只测这些 type（逗号分隔）")
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--out", default=str(DEFAULT_OUT))
    ap.add_argument("--allow-degraded", action="store_true")
    args = ap.parse_args()

    out_path = Path(args.out)
    log_path = out_path.with_suffix(out_path.suffix + ".log")

    if args.oracle_names:
        # 上界模式：改写由题集 ref 构造，必须等 items 筛完再建（故此处先置空）
        rewrites = {}
    else:
        rw_path = Path(args.rewrites)
        if not rw_path.is_file():
            log(f"[FAIL] 改写缓存不存在：{rw_path}（或用 --oracle-names 跑上界）")
            return 3
        rewrites = json.loads(rw_path.read_text(encoding="utf-8"))
        log(f"[rw] 改写缓存 {len(rewrites)} 条")

    ts_path = Path(args.testset)
    items = E.load_testset(ts_path if ts_path.is_file() else None)
    if args.types:
        want = {t.strip() for t in str(args.types).split(",") if t.strip()}
        items = [it for it in items
                 if str((it.get("dims") or {}).get("type")) in want]
    # 只保留有改写的题（保证两档同题集配对）；上界模式下改写尚未构造，跳过此筛
    if not args.oracle_names:
        items = [it for it in items if str(it.get("q")) in rewrites]
    if args.limit:
        items = items[: args.limit]
    if not items:
        log("[FAIL] 筛后无题（题集与改写缓存无交集？）")
        return 3
    if args.oracle_names:
        # 「完美补名」上界：用题集 ref 里的标准答案名拼到查询尾部。
        # 它回答的是：即使模型能 100% 补出答案实体名，这条路最多能拿多少分？
        # 上界都不值得，就不必再为「怎么让模型补得更准」继续投入。
        import re

        for it in items:
            ref = str(it.get("ref") or "")
            names: list[str] = []
            m = re.match(r"^([^（(]+)[（(]([^）)]+)", ref)
            if m:
                a = m.group(1).strip()
                b = m.group(2).split("，")[0].strip()
                names += [x for x in (a, b) if x]
            elif ref:
                names.append(ref.strip())
            q = str(it.get("q"))
            rewrites[q] = [f"{q} {n}" for n in names[:2]]
        log(f"[oracle-names] 由 ref 构造完美补名查询 {len(rewrites)} 条")
    log(f"[load] 题量 {len(items)}")

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
    oracle = E.build_oracle(retr.corpus, items)

    # 预嵌入全部改写（批量）：在线只需查，不重复烧时间
    vec_cache: dict[str, list[np.ndarray]] = {}
    all_texts: list[str] = []
    owner: list[tuple[str, int]] = []
    for q, vs in rewrites.items():
        vec_cache[q] = []
        for v in vs:
            owner.append((q, len(all_texts)))
            all_texts.append(v)
    if all_texts:
        t0 = time.time()
        embs = sem.embedder.embed(all_texts)
        for (q, idx), e in zip(owner, embs):
            vec_cache[q].append(np.asarray(e, dtype=np.float32))
        log(f"[embed] 预嵌入 {len(all_texts)} 条改写：{time.time() - t0:.0f}s")

    # ── 注入：语义通道多走几路改写向量 ──────────────────────────────────────
    orig_search = sem.search

    def patched_search(qvec, top_k=5):
        base = orig_search(qvec, top_k)
        extras = list(getattr(retr, "_qr_extra_vecs", []) or [])
        if not extras:
            return base
        merged: dict[str, float] = {}
        for h, s in base:
            merged[str(h)] = float(s)
        for v in extras:
            for h, s in orig_search(v, top_k):
                h = str(h)
                if h not in merged or float(s) > merged[h]:
                    merged[h] = float(s)
        out = sorted(merged.items(), key=lambda kv: -kv[1])
        return out[: max(int(top_k), len(base))]

    def run(label: str, enable: bool) -> dict[str, Any]:
        sem.search = patched_search if enable else orig_search
        t0 = time.time()
        n_pass = 0
        n_inj = 0
        for item in items:
            q = str(item.get("q"))
            retr._qr_extra_vecs = vec_cache.get(q, []) if enable else []
            row = E.evaluate_case(retr, item, oracle[str(item.get("id"))],
                                  top, lex_fb, inject_chars)
            n_pass += int(bool(row.get("strict_pass")))
            n_inj += int(bool(row.get("inject_pass")))
        retr._qr_extra_vecs = []
        neg = E.evaluate_negatives(retr, top, lex_fb)
        r = {
            "label": label, "enable": enable,
            "strict_pass_n": n_pass, "strict_pass": D.rate(n_pass, len(items)),
            "inject_pass_n": n_inj, "inject_pass": D.rate(n_inj, len(items)),
            "negatives": {"cases": neg.get("cases"),
                          "cases_with_injection": len(neg.get("violations") or []),
                          "injection_total": neg.get("negative_injection_total"),
                          "new_leaks": neg.get("new_leaks")},
            "elapsed_s": round(time.time() - t0, 1),
        }
        log(f"  [{label}] strict {n_pass}/{len(items)}｜inject {n_inj}"
            f"｜负样本失守 {r['negatives']['cases_with_injection']}/{r['negatives']['cases']} 条"
            f"（注入 {r['negatives']['injection_total']} 块）｜{r['elapsed_s']}s")
        return r

    results = [run("基线（无改写）", False), run("多路改写", True)]
    sem.search = orig_search
    delattr(retr, "_qr_extra_vecs") if hasattr(retr, "_qr_extra_vecs") else None

    base = results[0]
    report = {
        "generated_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        "config": {"testset": ts_path.name, "cases": len(items), "top": top,
                   "lexical_fallback": lex_fb, "inject_chars": inject_chars},
        "results": results,
        "delta": {"d_strict": results[1]["strict_pass_n"] - base["strict_pass_n"],
                  "d_inject": results[1]["inject_pass_n"] - base["inject_pass_n"],
                  "d_neg_cases": (results[1]["negatives"]["cases_with_injection"]
                                  - base["negatives"]["cases_with_injection"])},
    }
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    log(f"\n==== 摘要 ====　Δstrict={report['delta']['d_strict']:+d} 题"
        f"　Δinject={report['delta']['d_inject']:+d} 题"
        f"　Δ负样本失守={report['delta']['d_neg_cases']:+d} 条")
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
