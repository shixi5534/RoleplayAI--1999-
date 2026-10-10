"""P7 · 生成 v8→v9 逐项 delta 表（记分卡口径）。

用途：把 ``data/compendium_rag/reports/v8_audit/`` 与现行 ``data/compendium_rag/reports/``
的**同名同 gate 报告**逐条对比，产出：

- ``data/compendium_rag/reports/p7_delta_v8_v9.json``
- ``data/compendium_rag/reports/p7_delta_v8_v9.md``

设计纪律（对应 ``docs/compendium-rag/优化计划_v9_2026-10-08.md``）：

1. **v8/v9 不混表**：两侧分别汇总，任一侧缺报告即在该行标 ``missing``，
   **不得**用另一侧的数值补位；
2. **只报涨不报跌 = 违规**：每行强制给出 ``direction``（升/降/平），
   降的行必须以 ``⚠`` 标出；
3. **两口径并列**：L2.1 与 L4.1a 额外给诊断口径列（原口径为计分口径）；
4. **不进图、不调 LLM、不联网、只读**；不用 rmtree/unlink。

另有一张**专项表**：三主数（300cn / blind206 / gen120）的 full 与 graph_only 两口径
逐集对比，数据来自 ``eval_*_k1.json``(v8) 与 ``eval_*_k1_r10.json``(v9)，
**必须显式列出 blind206 graph_only 的下跌题**（计划 :127 要求）。

用法::

    PYTHONPATH=src .venv/Scripts/python.exe -X utf8 \
        scripts/compendium_rag_p7_delta.py
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPORTS = ROOT / "data" / "compendium_rag" / "reports"
V8_DIR = REPORTS / "v8_audit"

# 两口径并列：这些 gate 额外给诊断读数（诊断列不改判）
DIAGNOSTIC_GATES = {
    "L2.1 Recall@10（集合级，主口径=三集合并）": "L2.1_diag_recall_at_10",
    "L4.1a 方向对成对完整率": "L4.1a_diag_raw_pairing",
}

# 三主数：v8 与 v9(r10) 的产物名
EVAL_PAIRS = [
    ("300cn", "eval_300cn_k1.json", "eval_300cn_k1_r10.json"),
    ("blind206", "eval_blind_k1.json", "eval_blind_k1_r10.json"),
    ("gen120", "eval_gen120_k1.json", "eval_gen120_k1_r10.json"),
]

# 已知的**口径性**差（不是数据回退）：这些 gate 的判定文本里写死了 v8 基准，
# 在任何 v9 图上必然翻转，必须与本表其它行区分开，否则会被误读成质量回退。
CALIBER_LOCKS = {
    "graph_sha_vs_v8":
        "`scripts/audit_wp0_env.py` 硬编 `AC.V8_GRAPH_SHA16` 作为期望值，"
        "在任何 v9 图上必然 FAIL——口径性失败，不是图回退。",
    "v8_three_main_numbers":
        "同一脚本把 v8 期的三主数当基线逐位比对；blind206 与 gen120 各高 1 题"
        "属真实读数变化（见第 6 节三主数专项），不是回退，但该 gate 的"
        "「逐位相等」口径本身已不适用于 v9。",
}


def _load(p: Path) -> dict | None:
    if not p.exists():
        return None
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


def _num(v):
    return v if isinstance(v, (int, float)) and not isinstance(v, bool) else None


def _direction(a, b) -> str:
    """升/降/平/不可比。数值方向一律给出，不省略。"""
    x, y = _num(a), _num(b)
    if x is None or y is None:
        return "n/a"
    if abs(y - x) < 1e-12:
        return "平"
    return "升" if y > x else "降"


def _polarity(target: str | None) -> str:
    """从 target 文本判定「越大越好」还是「越小越好」。"""
    t = (target or "").strip()
    if t.startswith("≥") or t.startswith(">"):
        return "higher_better"
    if t.startswith("≤") or t.startswith("<"):
        return "lower_better"
    if "=0" in t or "= 0" in t:
        return "lower_better"
    return "unknown"


def _metric_direction(numeric: str, target: str | None) -> str:
    """把数值方向映射成指标方向（改善/恶化/持平/不可判）。

    关键：``L3.4 幻觉率`` 这类「越小越好」的门槛，读数**下降是改善**；
    若只报数值方向会把它误标成「降/违规」。
    """
    if numeric in ("n/a", "不可比"):
        return "不可判"
    if numeric == "平":
        return "持平"
    pol = _polarity(target)
    if pol == "unknown":
        return "不可判"
    want_down = pol == "lower_better"
    improved = (numeric == "降") if want_down else (numeric == "升")
    return "改善" if improved else "恶化"


def _gates(d: dict | None) -> dict[str, dict]:
    if not d:
        return {}
    return {g["gate"]: g for g in (d.get("gate_verdicts") or [])}


def build_delta() -> dict:
    rows: list[dict] = []
    files = sorted({p.name for p in V8_DIR.glob("audit_*.json")}
                   | {p.name for p in REPORTS.glob("audit_*.json")})
    for name in files:
        if name in ("audit_scorecard.json",):
            continue
        v8, cur = _load(V8_DIR / name), _load(REPORTS / name)
        g8, gc = _gates(v8), _gates(cur)
        names = list(dict.fromkeys(list(g8) + list(gc)))
        for gname in names:
            a, b = g8.get(gname), gc.get(gname)
            if a is None or b is None:
                rows.append({
                    "report": name, "gate": gname,
                    "status": "missing_v8" if a is None else "missing_v9",
                    "target": (a or b).get("target"),
                    "v8": None if a is None else a.get("actual"),
                    "v9": None if b is None else b.get("actual"),
                    "verdict_v8": None if a is None else a.get("verdict"),
                    "verdict_v9": None if b is None else b.get("verdict"),
                    "direction": "不可比",
                })
                continue
            rows.append({
                "report": name, "gate": gname, "status": "both",
                "target": a.get("target"),
                "v8": a.get("actual"), "v9": b.get("actual"),
                "verdict_v8": a.get("verdict"), "verdict_v9": b.get("verdict"),
                "verdict_flip": a.get("verdict") != b.get("verdict"),
                "direction": _direction(a.get("actual"), b.get("actual")),
                "polarity": _polarity(a.get("target")),
                "metric_direction": _metric_direction(
                    _direction(a.get("actual"), b.get("actual")), a.get("target")),
                "caliber_lock": CALIBER_LOCKS.get(gname),
                "reason_v9": (b.get("reason") or "")[:200],
            })

    # 两口径并列（现算）
    diag = _load(REPORTS / "audit_scorecard.json") or {}
    diagnostics = diag.get("diagnostics") or {}
    v8_sc = _load(V8_DIR / "audit_scorecard.json") or {}
    v9_sha = diag.get("frozen_graph_sha")
    v8_sha = v8_sc.get("frozen_graph_sha")
    if not v8_sha:
        # v8 记分卡缺失时退回从 v8 报告推断，且不与 v9 混用
        seen = sorted({(g.get("frozen_graph_sha") or "")
                       for g in (_load(p) or {} for p in V8_DIR.glob("audit_*.json"))
                       if g.get("frozen_graph_sha")})
        v8_sha = seen[0] if len(seen) == 1 else (seen or None)

    # 三主数专项
    eval_rows = []
    for label, v8_name, v9_name in EVAL_PAIRS:
        d8, d9 = _load(REPORTS / v8_name), _load(REPORTS / v9_name)
        entry = {"set": label, "v8_file": v8_name, "v9_file": v9_name,
                 "status": "both" if (d8 and d9) else "missing", "modes": {}}
        for mode in ("full", "graph_only"):
            e: dict = {}
            for scope, pred in (("answerable", lambda r: r.get("answerable")),
                                ("all", lambda r: True)):
                def stat(d):
                    if not d:
                        return None
                    rs = [r for r in d["rows"] if r["mode"] == mode and pred(r)]
                    if not rs:
                        return None
                    n = len(rs)
                    return {"n": n,
                            "hit": sum(1 for r in rs if r["hit"]),
                            "hit_rate": round(sum(1 for r in rs if r["hit"]) / n, 6),
                            "mrr": round(sum(r["rr"] for r in rs) / n, 6),
                            "qids": {r["qid"]: bool(r["hit"]) for r in rs}}
                s8, s9 = stat(d8), stat(d9)
                if s8 and s9:
                    up = sorted(q for q in s8["qids"]
                                if s9["qids"].get(q) and not s8["qids"][q])
                    dn = sorted(q for q in s8["qids"]
                                if s8["qids"][q] and not s9["qids"].get(q))
                    e[scope] = {
                        "n": s9["n"], "hit_v8": s8["hit"], "hit_v9": s9["hit"],
                        "hit_rate_v8": s8["hit_rate"], "hit_rate_v9": s9["hit_rate"],
                        "hit_rate_delta": round(s9["hit_rate"] - s8["hit_rate"], 6),
                        "mrr_v8": s8["mrr"], "mrr_v9": s9["mrr"],
                        "mrr_delta": round(s9["mrr"] - s8["mrr"], 6),
                        "paired_up": len(up), "paired_down": len(dn),
                        "up_qids": up, "down_qids": dn,
                        "direction": _direction(s8["hit_rate"], s9["hit_rate"]),
                    }
                else:
                    e[scope] = None
            entry["modes"][mode] = e
        if d9:
            entry["corpus"] = d9.get("corpus")
        eval_rows.append(entry)

    return {
        "schema": "compendium_rag.p7_delta/v1",
        "mode": "read-only",
        "caliber": {
            "rule": "v8 归档 = data/compendium_rag/reports/v8_audit/；v9 = data/compendium_rag/reports/"
                    "；两侧分别汇总，任一侧缺报告标 missing，不得互相补位。",
            "v8_graph_sha": v8_sha,
            "v9_graph_sha": v9_sha,
            "v8_scorecard_total": v8_sc.get("weighted_total_pct"),
            "v9_scorecard_total": diag.get("weighted_total_pct"),
            "v8_scorecard_grade": v8_sc.get("grade"),
            "v9_scorecard_grade": diag.get("grade"),
        },
        "gates": rows,
        "diagnostics": diagnostics,
        "three_main_numbers": eval_rows,
    }


def _fmt(v) -> str:
    if isinstance(v, float):
        return f"{v:.4f}"
    if isinstance(v, dict):
        return json.dumps(v, ensure_ascii=False)[:60]
    return str(v)


def _md(o: dict) -> str:
    rows = o["gates"]
    both = [r for r in rows if r["status"] == "both"]
    missing = [r for r in rows if r["status"] != "both"]
    flips = [r for r in both if r.get("verdict_flip")]
    worse = [r for r in both if r.get("metric_direction") == "恶化"]
    better = [r for r in both if r.get("metric_direction") == "改善"]
    ambiguous = [r for r in both if r.get("metric_direction") == "不可判"]

    L = ["# v8 → v9 逐项 delta 表", "",
         f"- 口径：{o['caliber']['rule']}",
         f"- v8 图 SHA：`{o['caliber']['v8_graph_sha']}`；"
         f"v9 图 SHA：`{o['caliber']['v9_graph_sha']}`",
         f"- 总分：v8 **{o['caliber']['v8_scorecard_total']}%"
         f"（{o['caliber']['v8_scorecard_grade']}）** → "
         f"v9 **{o['caliber']['v9_scorecard_total']}%"
         f"（{o['caliber']['v9_scorecard_grade']}）**",
         f"- 可比 gate：{len(both)}；单侧缺失：{len(missing)}；"
         f"判定翻转：{len(flips)}；指标改善：{len(better)}；"
         f"**指标恶化：{len(worse)}**；方向不可判：{len(ambiguous)}",
         "",
         "> 纪律：本表逐行给出**数值方向**与**指标方向**（由 target 的 ≥/≤ 极性判定），"
         "恶化行以 ⚠ 标注——只报涨不报跌即为违规。",
         "> 注意：幻觉率、泄漏率等「越小越好」的门槛，读数下降是改善而非恶化，"
         "故必须看指标方向列，不能只看数值方向。", "",
         "## 1. 逐 gate delta", "",
         "| 报告 | gate | 目标 | v8 | v9 | 数值方向 | 指标方向 | v8 判定 | v9 判定 |",
         "|---|---|---|---|---|---|---|---|---|"]
    for r in rows:
        mark = ""
        if r["status"] != "both":
            mark = f"（{r['status']}，不可比）"
        elif r.get("metric_direction") == "恶化":
            mark = " ⚠"
        md_dir = r.get("metric_direction", "")
        L.append(f"| {r['report'].replace('audit_','').replace('.json','')} "
                 f"| {r['gate']} | {r.get('target','')} | {_fmt(r['v8'])} "
                 f"| {_fmt(r['v9'])} | {r['direction']} "
                 f"| {md_dir}{mark} "
                 f"| {r.get('verdict_v8','')} | {r.get('verdict_v9','')} |")

    L += ["", "## 2. 判定翻转清单", ""]
    if flips:
        for r in flips:
            arrow = "FAIL → PASS" if r["verdict_v9"] == "PASS" else "PASS → FAIL"
            tag = "（**口径性**，见下）" if r.get("caliber_lock") else ""
            L.append(f"- **{r['gate']}**：{arrow}"
                     f"（{_fmt(r['v8'])} → {_fmt(r['v9'])}）{tag}")
    else:
        L.append("- 无。")

    locked = [r for r in flips if r.get("caliber_lock")]
    if locked:
        L += ["", "### 2b. 口径性翻转说明（不是质量回退）", ""]
        for r in locked:
            L.append(f"- **{r['gate']}**：{r['caliber_lock']}")

    L += ["", "## 3. 指标恶化清单（必须并列，不得被主口径盖过）", ""]
    if worse:
        for r in worse:
            L.append(f"- ⚠ **{r['gate']}**：{_fmt(r['v8'])} → {_fmt(r['v9'])}"
                     f"（{r['direction']}，目标 {r.get('target')}，"
                     f"v9 判定 {r.get('verdict_v9')}）")
    else:
        L.append("- 无。")

    L += ["", "## 4. 指标改善清单（并列，便于对照）", ""]
    if better:
        for r in better:
            L.append(f"- **{r['gate']}**：{_fmt(r['v8'])} → {_fmt(r['v9'])}"
                     f"（{r['direction']}，目标 {r.get('target')}，"
                     f"v9 判定 {r.get('verdict_v9')}）")
    else:
        L.append("- 无。")

    L += ["", "## 5. 两口径并列（诊断列，不改判）", ""]
    for key in ("L2.1", "L4.1a"):
        d = (o.get("diagnostics") or {}).get(key)
        if not d:
            L.append(f"- **{key}**：缺读数，无法现算。")
            continue
        L.append(f"- **{key}**（目标 {d.get('target')}，"
                 f"计分口径判定 {d.get('verdict_at_primary')}）")
        L.append(f"  - 原口径：**{d['primary']}** — {d['primary_form']}")
        L.append(f"  - 诊断口径：**{d['diagnostic']}** — {d['diagnostic_form']}")
        if d.get("oracle_ceiling") is not None:
            L.append(f"  - oracle 天花板：{d['oracle_ceiling']}")
        if d.get("reading"):
            L.append(f"  - 读法：{d['reading']}")
    if (o.get("diagnostics") or {}).get("note"):
        L.append(f"  - 口径声明：{o['diagnostics']['note']}")

    L += ["", "## 6. 三主数专项（full / graph_only 两口径）", "",
          "| 集 | 模式 | 子集 | n | v8 hit@6 | v9 hit@6 | Δ | v8 MRR | v9 MRR | "
          "配对 +/− | 方向 |", "|---|---|---|---|---|---|---|---|---|---|---|"]
    for e in o["three_main_numbers"]:
        for mode in ("full", "graph_only"):
            for scope in ("answerable", "all"):
                s = (e["modes"] or {}).get(mode, {}).get(scope) if e.get("modes") else None
                if not s:
                    continue
                mark = " ⚠" if s["direction"] == "降" else ""
                L.append(f"| {e['set']} | {mode} | {scope} | {s['n']} "
                         f"| {s['hit_rate_v8']:.4f} | {s['hit_rate_v9']:.4f} "
                         f"| {s['hit_rate_delta']:+.4f} | {s['mrr_v8']:.4f} "
                         f"| {s['mrr_v9']:.4f} "
                         f"| +{s['paired_up']}/−{s['paired_down']} | {s['direction']}{mark} |")

    L += ["", "### 6b. 配对翻转题（逐题级，计划 :127 要求 blind206 graph_only 必须列出）", ""]
    any_q = False
    for e in o["three_main_numbers"]:
        for mode in ("full", "graph_only"):
            for scope in ("answerable", "all"):
                s = (e["modes"] or {}).get(mode, {}).get(scope) if e.get("modes") else None
                if not s or (not s["down_qids"] and not s["up_qids"]):
                    continue
                any_q = True
                L.append(f"- **{e['set']} / {mode} / {scope}**："
                         f"翻正 {s['paired_up']} {s['up_qids']}；"
                         f"翻负 {s['paired_down']} {s['down_qids']}")
    if not any_q:
        L.append("- 无逐题翻转。")

    if missing:
        L += ["", "## 7. 单侧缺失（不可比，未互相补位）", ""]
        for r in missing:
            L.append(f"- {r['report']} · {r['gate']}：{r['status']}")

    L += ["", "---", "",
          "本表由 `scripts/compendium_rag_p7_delta.py` 现算生成，只读两侧报告；"
          "未改图、未改门槛分母、未调 LLM。", ""]
    return "\n".join(L)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-json", default=str(REPORTS / "p7_delta_v8_v9.json"))
    ap.add_argument("--out-md", default=str(REPORTS / "p7_delta_v8_v9.md"))
    ap.add_argument("--stdout", action="store_true", help="只打印，不写盘")
    args = ap.parse_args()

    if not V8_DIR.is_dir():
        print(f"[FATAL] v8 归档目录不存在：{V8_DIR}")
        return 2
    o = build_delta()
    md = _md(o)
    if not args.stdout:
        Path(args.out_json).write_text(
            json.dumps(o, ensure_ascii=False, indent=2), encoding="utf-8")
        Path(args.out_md).write_text(md, encoding="utf-8")

    both = [r for r in o["gates"] if r["status"] == "both"]
    flips = [r for r in both if r.get("verdict_flip")]
    worse = [r for r in both if r.get("metric_direction") == "恶化"]
    better = [r for r in both if r.get("metric_direction") == "改善"]
    print(f"可比 gate {len(both)}；判定翻转 {len(flips)}；"
          f"指标改善 {len(better)}；指标恶化 {len(worse)}")
    for r in flips:
        print(f"  翻转 {r['gate']}: {r['verdict_v8']} -> {r['verdict_v9']}")
    for r in worse:
        print(f"  ⚠ 恶化 {r['gate']}: {_fmt(r['v8'])} -> {_fmt(r['v9'])}"
              f"（目标 {r.get('target')}）")
    for r in better:
        print(f"  改善 {r['gate']}: {_fmt(r['v8'])} -> {_fmt(r['v9'])}")
    for e in o["three_main_numbers"]:
        g = (e.get("modes") or {}).get("graph_only", {}).get("all")
        if g and g["paired_down"]:
            print(f"  ⚠ {e['set']} graph_only 翻负 {g['paired_down']} 题："
                  f"{g['down_qids']}")
    if args.stdout:
        print()
        print(md)
    else:
        print(f"→ {args.out_json}")
        print(f"→ {args.out_md}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
