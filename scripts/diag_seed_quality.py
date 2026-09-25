# -*- coding: utf-8 -*-
"""种子质量画像（只读诊断）：失败题到底是「没种子」还是「种子选错了」。

背景
----
``docs/RAG召回优化下一步计划_20260917.md`` 把主瓶颈定为「seeds 为空」，
路径 A 是「seeds 为空时做描述性解析回填」。

但 ``scripts/diag_seedless_ceiling.py`` 全量实测：300 题里 seeds 为空只有 **6 题**，
与文档声称的 76–79 题差了一个数量级。而 ``plot_graph.py`` 的种子门控注释里
自己写着：「失败题的种子几乎总是非空（只是选错了，如「洞穴」「海盗」）」。

两者只能有一个是真的。本脚本用**主评测口径**（复用 ``eval_plot_rag.evaluate_case``）
把失败题按种子质量分组，给出决定性证据：

  - ``seeds 为空`` 多少题？
  - ``seeds 非空但全都不是真阳实体`` 多少题？（= 种子选错）
  - ``seeds 含真阳`` 多少题？这些题的通过率又是多少？

判定「真阳实体」的方法与 ``diag_seedless_ceiling.truth_entities_for_item`` 完全一致
（证据关键词路 ∪ oracle full 上下文路），保证两个脚本的结论可互相印证。

用法（项目根目录）
------------------
    .venv/Scripts/python.exe -X utf8 scripts/diag_seed_quality.py
    .venv/Scripts/python.exe -X utf8 scripts/diag_seed_quality.py --limit 30   # 冒烟

产物：``data/knowledge/_audit/diag_seed_quality.json`` + 同名 ``.log``
退出码：0 正常｜1 环境/数据缺失｜2 语义通道降级
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from collections import Counter
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

from roleplay.config import get_settings  # noqa: E402
from roleplay.core.knowledge.factory import build_plot_registry  # noqa: E402

import diag_seedless_ceiling as D  # noqa: E402  （复用真阳判定与工具函数）
import eval_plot_rag as E  # noqa: E402

DEFAULT_OUT = ROOT / "data" / "knowledge" / "_audit" / "diag_seed_quality.json"

_LOG: list[str] = []


def log(msg: str) -> None:
    print(msg, flush=True)
    _LOG.append(str(msg))


def main() -> int:
    ap = argparse.ArgumentParser(description="失败题种子质量画像（只读诊断）")
    ap.add_argument("--character", default="wu_ming_zhe")
    ap.add_argument("--testset", default="")
    ap.add_argument("--limit", type=int, default=0, help="只跑前 N 题（冒烟）")
    ap.add_argument("--out", default=str(DEFAULT_OUT))
    ap.add_argument("--allow-degraded", action="store_true")
    args = ap.parse_args()

    out_path = Path(args.out)
    log_path = out_path.with_suffix(out_path.suffix + ".log")

    settings = get_settings()
    registry = build_plot_registry(settings)
    retr = registry.get(args.character)
    if retr is None:
        log(f"[FAIL] 剧情图谱未加载（{args.character}）")
        return 1
    degraded = getattr(retr, "semantic", None) is None
    if degraded and not args.allow_degraded:
        log("[FAIL] 语义通道已降级，拒绝出报告（--allow-degraded 可强行继续）")
        return 2

    top = int(getattr(settings, "plot_max_chunks", 3) or 3)
    lex_fb = int(getattr(settings, "plot_lexical_fallback", 2) or 0)
    items = E.load_testset(Path(args.testset) if args.testset else None)
    if args.limit:
        items = items[: args.limit]
    log(f"[load] 题量 {len(items)}｜top={top}｜lexical_fallback={lex_fb}")

    oracle = E.build_oracle(retr.corpus, items)
    name_map = D.build_entity_name_map(retr)

    buckets: dict[str, int] = {
        "pass": 0, "fail": 0,
        "fail_seedless": 0,
        "fail_seeds_no_truth": 0,
        "fail_seeds_has_truth": 0,
    }
    # 分组通过率：种子含真阳 vs 不含真阳（「种子质量是否决定成败」的直接证据）
    grp: dict[str, dict[str, int]] = {
        "has_truth": {"n": 0, "pass": 0},
        "no_truth": {"n": 0, "pass": 0},
        "seedless": {"n": 0, "pass": 0},
    }
    seed_path_counter: Counter = Counter()
    wrong_seed_names: Counter = Counter()
    per_case: list[dict] = []

    t0 = time.time()
    for i, item in enumerate(items, start=1):
        q = str(item.get("q") or "")
        qid = str(item.get("id") or "")
        linked = retr.link_detailed(q)
        seeds = retr.seed_gate(linked)
        ent = oracle.get(qid) or {"full": set(), "any": set(), "ceiling": False}
        truth, _note = D.truth_entities_for_item(item, ent, retr.corpus, name_map)
        # 主评测口径判定（检索行为与生产一致；此处注入口径不开，只看 strict）
        row = E.evaluate_case(retr, item, ent, top, lex_fb, 0)
        passed = bool(row.get("strict_pass"))

        seed_rows = []
        has_exact = False
        has_truth_seed = False
        for eid, info in (linked or {}).items():
            eid_s = str(eid)
            path = str((info or {}).get("path") or "")
            if path == "exact":
                has_exact = True
            if eid_s in truth and eid_s in seeds:
                has_truth_seed = True
            seed_rows.append({
                "eid": eid_s,
                "name": str((info or {}).get("name") or "") or (name_map.get(eid_s) or [""])[0],
                "path": path,
                "gated": eid_s in seeds,
                "truth": eid_s in truth,
            })
        seed_path_counter["has_exact" if has_exact else ("token_only" if seeds else "none")] += 1

        key = "seedless" if not seeds else ("has_truth" if has_truth_seed else "no_truth")
        grp[key]["n"] += 1
        if passed:
            grp[key]["pass"] += 1
            buckets["pass"] += 1
        else:
            buckets["fail"] += 1
            if not seeds:
                buckets["fail_seedless"] += 1
            elif has_truth_seed:
                buckets["fail_seeds_has_truth"] += 1
            else:
                buckets["fail_seeds_no_truth"] += 1
                # 误种子画像：只统计失败且 seeds 全错的题，按「进入门控的名字」计数
                for sr in seed_rows:
                    if sr["gated"] and sr["name"]:
                        wrong_seed_names[sr["name"]] += 1

        per_case.append({
            "id": qid, "q": q, "pass": passed, "n_seeds": len(seeds),
            "has_truth_seed": has_truth_seed, "n_truth_entities": len(truth),
            "seeds": seed_rows[:8],
        })
        if i % 50 == 0:
            log(f"  [progress] {i}/{len(items)}｜已用 {time.time() - t0:.0f}s")

    report: dict[str, Any] = {
        "generated_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        "character": args.character,
        "config": {"top": top, "lexical_fallback": lex_fb, "degraded": degraded},
        "counts": {"items": len(items), **buckets},
        "pass_rate_by_seed_quality": {
            k: {"n": v["n"], "pass": v["pass"], "pass_rate": D.rate(v["pass"], v["n"])}
            for k, v in grp.items()
        },
        "seed_path_distribution": dict(seed_path_counter),
        "top_wrong_seed_names": wrong_seed_names.most_common(30),
        "per_case": per_case,
    }
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    log("\n==== 摘要 ====")
    log(f"通过 {buckets['pass']} / 失败 {buckets['fail']}（题量 {len(items)}）")
    log(f"失败题分组：无种子 {buckets['fail_seedless']}｜种子全错 {buckets['fail_seeds_no_truth']}"
        f"｜种子含真阳仍失败 {buckets['fail_seeds_has_truth']}")
    for k, v in report["pass_rate_by_seed_quality"].items():
        log(f"  {k:10s} n={v['n']:3d}  pass={v['pass']:3d}  pass_rate={v['pass_rate']}")
    log(f"种子路径分布：{dict(seed_path_counter)}")
    log("最常被误当种子的实体（失败且全错题）：")
    for name, cnt in wrong_seed_names.most_common(15):
        log(f"  {name} × {cnt}")
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
