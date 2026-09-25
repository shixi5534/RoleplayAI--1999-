# -*- coding: utf-8 -*-
"""T7：真实补名端到端验证（静态映射形态，不改检索代码）。

与"补名上界"实验的区别（关键）
------------------------------
- 上界实验（ab_query_rewrite.py --oracle-names）用的是**题集 ref 里的标准答案**，
  等于把答案喂给检索器 → +28 题；
- 本实验用的是**依据语料块内"描述↔实体名"共现**构造的映射表
  （`data/knowledge/_audit/t7_static_topup_map_20260917.json`，每条附 basis）。
  这才是"模型离线读语料能补出什么"的真实水平。

做法：命中映射的题把补名拼到 query 尾部（等价于项目已有的 ``StaticMapIdentifier``
静态映射后端），其余题逐位不变；两档都用主评测口径判定（``evaluate_case``）。

用法（项目根目录）
------------------
    .venv/Scripts/python.exe -X utf8 scripts/ab_static_topup.py \\
        --map data/knowledge/_audit/t7_static_topup_map_20260917.json \\
        --testset data/knowledge/_audit/rag_testset_300.json \\
        --out data/knowledge/_audit/ab_static_topup_300.json

产物：JSON + 同名 .log（含逐题 delta，便于看"补对了没救回"的题）
退出码：0 正常｜1 环境缺失｜2 语义降级｜3 映射缺失
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

DEFAULT_OUT = ROOT / "data" / "knowledge" / "_audit" / "ab_static_topup.json"

_LOG: list[str] = []


def log(msg: str) -> None:
    print(msg, flush=True)
    _LOG.append(str(msg))


def main() -> int:
    ap = argparse.ArgumentParser(description="真实补名（静态映射）端到端验证")
    ap.add_argument("--character", default="wu_ming_zhe")
    ap.add_argument("--map", dest="map_path", required=True)
    ap.add_argument("--testset", default=str(ROOT / "data/knowledge/_audit/rag_testset_300.json"))
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--out", default=str(DEFAULT_OUT))
    ap.add_argument("--allow-degraded", action="store_true")
    args = ap.parse_args()

    out_path = Path(args.out)
    log_path = out_path.with_suffix(out_path.suffix + ".log")
    mp = Path(args.map_path)
    if not mp.is_file():
        log(f"[FAIL] 映射表不存在：{mp}")
        return 3
    raw = json.loads(mp.read_text(encoding="utf-8"))
    table: dict[str, Any] = raw.get("map") or raw
    log(f"[map] 补名映射 {len(table)} 条")

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
    if args.limit:
        items = items[: args.limit]
    oracle = E.build_oracle(retr.corpus, items)
    log(f"[load] 题量 {len(items)}｜命中映射 {sum(1 for it in items if str(it.get('id')) in table)}")

    def run(label: str, enable: bool) -> dict[str, Any]:
        t0 = time.time()
        n_pass = 0
        n_inj = 0
        per: list[dict] = []
        for it in items:
            qid = str(it.get("id"))
            q = str(it.get("q"))
            entry = table.get(qid)
            patch = bool(enable and entry)
            q_used = f"{q} {' '.join(entry.get('names') or [])}" if patch else q
            item2 = dict(it)
            item2["q"] = q_used
            row = E.evaluate_case(retr, item2, oracle[qid], top, lex_fb, inject_chars)
            ok = bool(row.get("strict_pass"))
            n_pass += int(ok)
            n_inj += int(bool(row.get("inject_pass")))
            per.append({"id": qid, "patched": patch, "pass": ok,
                        "names": (entry or {}).get("names")})
        neg = E.evaluate_negatives(retr, top, lex_fb)
        r = {
            "label": label, "enable": enable,
            "strict_pass_n": n_pass, "strict_pass": D.rate(n_pass, len(items)),
            "inject_pass_n": n_inj, "inject_pass": D.rate(n_inj, len(items)),
            "negatives": {"cases": neg.get("cases"),
                          "cases_with_injection": len(neg.get("violations") or []),
                          "injection_total": neg.get("negative_injection_total"),
                          "new_leaks": neg.get("new_leaks")},
            "per_case": per,
            "elapsed_s": round(time.time() - t0, 1),
        }
        log(f"  [{label}] strict {n_pass}/{len(items)}｜inject {n_inj}"
            f"｜负样本失守 {r['negatives']['cases_with_injection']}/{r['negatives']['cases']} 条"
            f"（注入 {r['negatives']['injection_total']} 块）｜{r['elapsed_s']}s")
        return r

    base = run("基线", False)
    patched = run("补名（静态映射）", True)

    # 逐题 delta：映射题的"补对但没救回 / 救回 / 补错"三态
    bmap = {c["id"]: c["pass"] for c in base["per_case"]}
    changed = []
    mapped_stat = {"mapped": 0, "fixed": 0, "broken": 0}
    for c in patched["per_case"]:
        if not c["patched"]:
            continue
        mapped_stat["mapped"] += 1
        was, now = bmap.get(c["id"], False), c["pass"]
        if now and not was:
            mapped_stat["fixed"] += 1
            changed.append({"id": c["id"], "effect": "fixed", "names": c["names"]})
        elif was and not now:
            mapped_stat["broken"] += 1
            changed.append({"id": c["id"], "effect": "broken", "names": c["names"]})
    report = {
        "generated_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        "config": {"testset": Path(args.testset).name, "cases": len(items),
                   "map": mp.name, "map_size": len(table)},
        "results": [{k: v for k, v in base.items() if k != "per_case"},
                    {k: v for k, v in patched.items() if k != "per_case"}],
        "delta": {"d_strict": patched["strict_pass_n"] - base["strict_pass_n"],
                  "d_inject": patched["inject_pass_n"] - base["inject_pass_n"],
                  "d_neg_cases": (patched["negatives"]["cases_with_injection"]
                                  - base["negatives"]["cases_with_injection"])},
        "mapped_effect": mapped_stat,
        "changes": changed,
    }
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    log(f"\n==== 摘要 ====　Δstrict={report['delta']['d_strict']:+d} 题"
        f"　Δinject={report['delta']['d_inject']:+d} 题"
        f"　Δ负样本失守={report['delta']['d_neg_cases']:+d} 条")
    log(f"映射题 {mapped_stat['mapped']}｜救回 {mapped_stat['fixed']}"
        f"｜反而砸掉 {mapped_stat['broken']}")
    for c in changed:
        log(f"  {c['effect']:7s} {c['id']} 补名={c['names']}")
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
