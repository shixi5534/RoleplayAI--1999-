# -*- coding: utf-8 -*-
"""T17：查询语言消融——中文 / 英文 / 中英混合，验证"英语多就转英语查"。

背景（今日实测）：语料 9021 块里 **89.5% 是英配视频转写**（8069 块），
中文层只有 887 块（9.8% = 灰机正典 663 + 中配视频 224）。
因此中文查询必须靠跨语言语义打到英文块上——而 CLIR 的经典解法是
**把查询翻译成目标语言**（query translation）。

本脚本对照三档（同一题集、同一套判定口径）：
  A 基线：原始中文 query
  B 英文：云端模型翻译的英文检索式（仅做语言转换，不添加题干未出现的信息）
  C 中英混合：中文原文 + 英文检索式拼接（语料里仍有 9.8% 中文块，混合可能两全）

用法（项目根目录）
------------------
    .venv/Scripts/python.exe -X utf8 scripts/ab_query_lang.py \\
        --en C:/Users/Lenovo/WorkBuddy/2026-09-17-13-00-26/_en_queries_all.json \\
        --testset data/knowledge/_audit/rag_testset_300_clean.json \\
        --out data/knowledge/_audit/ab_query_lang_300.json

退出码：0 正常｜1 环境缺失｜2 语义降级｜3 输入缺失
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

import diag_seedless_ceiling as D  # noqa: E402
import eval_plot_rag as E  # noqa: E402

DEFAULT_OUT = ROOT / "data" / "knowledge" / "_audit" / "ab_query_lang.json"

_LOG: list[str] = []


def log(m: str) -> None:
    print(m, flush=True)
    _LOG.append(str(m))


def main() -> int:
    ap = argparse.ArgumentParser(description="查询语言消融（中文/英文/混合）")
    ap.add_argument("--character", default="wu_ming_zhe")
    ap.add_argument("--en", dest="en_path",
                    default=str(ROOT / "data" / "knowledge" / "_audit" / "en_queries_300_20260917.json"),
                    help="英文检索式 JSON（默认 300 题批）")
    ap.add_argument("--testset", default=str(ROOT / "data/knowledge/_audit/rag_testset_300_clean.json"))
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--out", default=str(DEFAULT_OUT))
    ap.add_argument("--allow-degraded", action="store_true")
    args = ap.parse_args()

    out_path = Path(args.out)
    log_path = out_path.with_suffix(out_path.suffix + ".log")
    p = Path(args.en_path)
    if not p.is_file():
        log(f"[FAIL] 英文检索式文件不存在：{p}")
        return 3
    en: dict[str, str] = json.loads(p.read_text(encoding="utf-8"))
    en = {k: v for k, v in en.items() if not k.startswith("_")}
    log(f"[en] 英文检索式 {len(en)} 条")

    settings = get_settings()
    registry = build_plot_registry(settings)
    retr = registry.get(args.character)
    if retr is None:
        log("[FAIL] 图谱未加载")
        return 1
    if getattr(retr, "semantic", None) is None and not args.allow_degraded:
        log("[FAIL] 语义通道已降级（--allow-degraded 可强行继续）")
        return 2

    top = int(getattr(settings, "plot_max_chunks", 3) or 3)
    lex_fb = int(getattr(settings, "plot_lexical_fallback", 2) or 0)
    inject_chars = int(getattr(settings, "plot_context_max_chars", 1000) or 0)
    items = E.load_testset(Path(args.testset))
    items = [it for it in items if str(it.get("id")) in en]
    if args.limit:
        items = items[: args.limit]
    oracle = E.build_oracle(retr.corpus, items)
    log(f"[load] 题量 {len(items)}｜top={top}｜lexical_fallback={lex_fb}")

    def run(label: str, mode: str) -> dict[str, Any]:
        t0 = time.time()
        n_pass = n_inj = n_real = 0
        per: list[dict] = []
        for it in items:
            qid = str(it.get("id"))
            q_cn = str(it.get("q"))
            q_en = en.get(qid, "")
            if mode == "cn":
                q = q_cn
            elif mode == "en":
                q = q_en
            else:
                q = f"{q_cn} {q_en}"
            item2 = dict(it)
            item2["q"] = q
            row = E.evaluate_case(retr, item2, oracle[qid], top, lex_fb, inject_chars)
            ok = bool(row.get("strict_pass"))
            n_pass += int(ok)
            n_real += int(bool(row.get("strict_pass_retrieved")))
            n_inj += int(bool(row.get("inject_pass")))
            per.append({"id": qid, "pass": ok})
        neg = E.evaluate_negatives(retr, top, lex_fb)
        r = {"label": label, "mode": mode,
             "strict_pass_n": n_pass, "strict_pass": D.rate(n_pass, len(items)),
             "strict_pass_retrieved_n": n_real,
             "inject_pass_n": n_inj, "inject_pass": D.rate(n_inj, len(items)),
             "negatives": {"cases": neg.get("cases"),
                           "cases_with_injection": len(neg.get("violations") or []),
                           "injection_total": neg.get("negative_injection_total"),
                           "new_leaks": neg.get("new_leaks")},
             "per_case": per, "elapsed_s": round(time.time() - t0, 1)}
        log(f"  [{label}] strict {n_pass}/{len(items)}｜retrieved {n_real}"
            f"｜inject {n_inj}"
            f"｜负样本失守 {r['negatives']['cases_with_injection']}/{r['negatives']['cases']} 条"
            f"（注入 {r['negatives']['injection_total']} 块）｜{r['elapsed_s']}s")
        return r

    results = [run("A 基线（中文 query）", "cn"),
               run("B 英文 query", "en"),
               run("C 中英混合", "mix")]
    base = results[0]
    bmap = {c["id"]: c["pass"] for c in base["per_case"]}
    changes = []
    for r in results[1:]:
        for c in r["per_case"]:
            if c["pass"] != bmap.get(c["id"]):
                changes.append({"mode": r["mode"], "id": c["id"],
                                "effect": "fixed" if c["pass"] else "broken"})
    report = {
        "generated_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        "config": {"testset": Path(args.testset).name, "cases": len(items),
                   "en_map": Path(args.en_path).name, "en_cases": len(en)},
        "results": [{k: v for k, v in r.items() if k != "per_case"} for r in results],
        "delta": [{"label": r["label"],
                   "d_strict": r["strict_pass_n"] - base["strict_pass_n"],
                   "d_inject": r["inject_pass_n"] - base["inject_pass_n"],
                   "d_neg": (r["negatives"]["cases_with_injection"]
                             - base["negatives"]["cases_with_injection"])}
                  for r in results],
        "changes": changes,
    }
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    log("\n==== 摘要 ====")
    for d in report["delta"]:
        log(f"{d['label']:<22} Δstrict={d['d_strict']:+d}　Δinject={d['d_inject']:+d}"
            f"　Δ负样本={d['d_neg']:+d}")
    fx = sum(1 for c in changes if c["effect"] == "fixed")
    bk = sum(1 for c in changes if c["effect"] == "broken")
    log(f"逐题变化：救回 {fx}｜砸掉 {bk}")
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
            (ROOT / "data" / "knowledge" / "_audit" / "_query_lang_crash.txt").write_text(
                f"{time.strftime('%Y-%m-%d %H:%M:%S')}\n{traceback.format_exc()}",
                encoding="utf-8")
        except Exception:
            pass
        print(f"[CRASH] {exc!r}", flush=True)
        raise
