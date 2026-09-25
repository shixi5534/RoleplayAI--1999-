# -*- coding: utf-8 -*-
"""T17b：中英双路检索融合（不是拼接，而是两路各自检索后合并）。

为什么必须补这一档（2026-09-17 实测）：
  · 纯英文 query：strict 203→**181（−22）**、inject 186→**171（−15）**；
  · 中英拼接：strict 200（−3）、inject 187（+1），但逐题"救 45 / 砸 70"——拼接把两路互相稀释。
  机理：①中文 query 能同时命中中文正典块（887 块里拼写是准的）；
  ②英文块是 ASR 转写，专名拼写不可靠（Eperon vs Apeiron、Xeno vs Zeno，58.4% 块含 `?`）；
  ③整句英文替换掉中文后，损失了中文正典这一路。
  ⇒ 正确形态应是"**保住中文路 + 追加英文路**"，且用**融合**而非拼接。

本脚本只 patch 语义通道：中文 query 走原通道（图谱通道完全不动），
额外用英文 query 的向量再检索一次，合并去重后仍取 top-k（通道规模不变）。

用法（项目根目录）
    .venv/Scripts/python.exe -X utf8 scripts/ab_query_lang2.py

退出码：0 正常｜1 环境缺失｜2 语义降级
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

AUDIT = ROOT / "data" / "knowledge" / "_audit"
_LOG: list[str] = []


def log(m: str) -> None:
    print(m, flush=True)
    _LOG.append(str(m))


def main() -> int:
    ap = argparse.ArgumentParser(description="中英双路检索融合")
    ap.add_argument("--character", default="wu_ming_zhe")
    ap.add_argument("--en", dest="en_path",
                    default=str(AUDIT / "en_queries_300_20260917.json"))
    ap.add_argument("--testset", default=str(AUDIT / "rag_testset_300_clean.json"))
    ap.add_argument("--out", default=str(AUDIT / "ab_query_lang2_300.json"))
    ap.add_argument("--allow-degraded", action="store_true")
    args = ap.parse_args()

    en = {k: v for k, v in json.loads(Path(args.en_path).read_text(encoding="utf-8")).items()
          if not k.startswith("_")}
    settings = get_settings()
    retr = build_plot_registry(settings).get(args.character)
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
    items = [it for it in E.load_testset(Path(args.testset)) if str(it.get("id")) in en]
    oracle = E.build_oracle(retr.corpus, items)
    log(f"[load] 题量 {len(items)}｜英文式 {len(en)} 条")

    vec_cache: dict[str, np.ndarray] = {}
    t0 = time.time()
    texts = [en[str(it["id"])] for it in items]
    for it, v in zip(items, sem.embedder.embed(texts)):
        vec_cache[str(it["id"])] = np.asarray(v, dtype=np.float32)
    log(f"[embed] 英文式预嵌入 {len(vec_cache)} 条｜{time.time() - t0:.0f}s")

    orig_search = sem.search
    state: dict[str, Any] = {"vec": None}

    def patched(qvec, top_k=5):
        base = orig_search(qvec, top_k)
        v = state["vec"]
        if v is None:
            return base
        extra = orig_search(v, max(int(top_k), 10))
        merged: dict[str, float] = {str(h): float(s) for h, s in base}
        for h, s in extra:
            h = str(h)
            if h not in merged or float(s) > merged[h]:
                merged[h] = float(s)
        out = sorted(merged.items(), key=lambda kv: -kv[1])
        return out[: max(int(top_k), len(base))]

    def run(label: str, dual: bool) -> dict[str, Any]:
        sem.search = patched if dual else orig_search
        t0 = time.time()
        n_pass = n_inj = 0
        per = []
        for it in items:
            qid = str(it["id"])
            state["vec"] = vec_cache.get(qid) if dual else None
            row = E.evaluate_case(retr, it, oracle[qid], top, lex_fb, inject_chars)
            ok = bool(row.get("strict_pass"))
            n_pass += int(ok)
            n_inj += int(bool(row.get("inject_pass")))
            per.append({"id": qid, "pass": ok})
        neg = E.evaluate_negatives(retr, top, lex_fb)
        r = {"label": label, "strict_pass_n": n_pass,
             "strict_pass": D.rate(n_pass, len(items)),
             "inject_pass_n": n_inj, "inject_pass": D.rate(n_inj, len(items)),
             "negatives": {"cases": neg.get("cases"),
                           "cases_with_injection": len(neg.get("violations") or []),
                           "injection_total": neg.get("negative_injection_total")},
             "per_case": per, "elapsed_s": round(time.time() - t0, 1)}
        log(f"  [{label}] strict {n_pass}/{len(items)}｜inject {n_inj}"
            f"｜负样本失守 {r['negatives']['cases_with_injection']}/{r['negatives']['cases']} 条"
            f"（注入 {r['negatives']['injection_total']} 块）｜{r['elapsed_s']}s")
        return r

    base = run("A 基线（中文 query）", False)
    dual = run("B 中英双路融合（语义通道双查）", True)
    sem.search = orig_search
    bmap = {c["id"]: c["pass"] for c in base["per_case"]}
    fixed = [c["id"] for c in dual["per_case"] if c["pass"] and not bmap.get(c["id"])]
    broken = [c["id"] for c in dual["per_case"] if bmap.get(c["id"]) and not c["pass"]]
    report = {
        "generated_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        "config": {"testset": Path(args.testset).name, "cases": len(items)},
        "results": [{k: v for k, v in r.items() if k != "per_case"} for r in (base, dual)],
        "delta": {"d_strict": dual["strict_pass_n"] - base["strict_pass_n"],
                  "d_inject": dual["inject_pass_n"] - base["inject_pass_n"],
                  "d_neg": (dual["negatives"]["cases_with_injection"]
                            - base["negatives"]["cases_with_injection"])},
        "fixed": fixed, "broken": broken,
    }
    Path(args.out).write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    log(f"\n==== 摘要 ====　Δstrict={report['delta']['d_strict']:+d}"
        f"　Δinject={report['delta']['d_inject']:+d}"
        f"　Δ负样本={report['delta']['d_neg']:+d}　救回 {len(fixed)}｜砸掉 {len(broken)}")
    log(f"[out] {args.out}")
    (Path(args.out).with_suffix(".log")).write_text("\n".join(_LOG), encoding="utf-8")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except SystemExit:
        raise
    except BaseException as exc:  # noqa: BLE001
        import traceback
        try:
            (AUDIT / "_query_lang2_crash.txt").write_text(
                f"{time.strftime('%Y-%m-%d %H:%M:%S')}\n{traceback.format_exc()}",
                encoding="utf-8")
        except Exception:
            pass
        print(f"[CRASH] {exc!r}", flush=True)
        raise
