# -*- coding: utf-8 -*-
"""WP6 —— 四层加权记分卡与 A/B/C 定级。

层内得分 = 该层 gate 的 PASS/(PASS+FAIL)，**N/A 显式剔分母**（豁免理由已在
各 WP 报告里登记）；总分 = Σ 层得分 × 权重（L1 25 / L2 25 / L3 20 / L4 30）。
定级：A ≥85% 且 L4 全过；B ≥75%（L4 至多 1 项未过）；否则 C。
对抗测试四类不计入四层加权，单列呈现（用户标准里它们是独立小节）。

根因归类口径写死在 `_bucket()`，与各 WP 报告里的 root_cause_bucket 对账。
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from datetime import date
from pathlib import Path

import audit_common as AC

REPORTS_DIR = AC.ROOT / "data" / "compendium_rag" / "reports"
LAYER_WEIGHTS = {"L1": 25, "L2": 25, "L3": 20, "L4": 30}
LAYER_NAMES = {"L1": "图构建质量", "L2": "检索质量", "L3": "生成质量",
               "L4": "跨角色一致性"}
ADVERSARIAL = ("audit_adv_inject.json", "audit_adv_contradict.json",
               "audit_adv_confuse.json", "audit_adv_drift.json")
EXCLUDE = ("audit_wp0_env.json", "audit_scorecard.json")
DOC_DIR = AC.ROOT / "docs" / "compendium-rag" / "audit"


def _layer_of(gate: str) -> str | None:
    if "基础设施" in gate:      # 自证项（归组完备性等），不属用户四层标准
        return None
    for k in ("L1", "L2", "L3", "L4"):
        if gate.startswith(k):
            return k
    return None


def _bucket(gate: str, verdict: str, declared: str, metrics: dict) -> str:
    """写死的根因归类（用户纪律：修数据不修指标）。"""
    if verdict != "FAIL":
        return declared or "-"
    if gate.startswith("L1"):
        return "数据层"
    if gate.startswith("L2"):
        return "检索层"
    if gate.startswith("L3.3") or gate.startswith("L3.4"):
        # faithfulness/幻觉：同 qid 在 L2 也 miss → 检索层，否则生成层
        return "检索层或生成层（逐题对账见 per_case）"
    if gate.startswith("L4.1") or gate.startswith("L4.2"):
        return "数据层"
    return declared or "生成层"


def collect(reports_dir: Path | None = None) -> tuple[list[dict], list[dict]]:
    rows, adv_rows = [], []
    for p in sorted((reports_dir or REPORTS_DIR).glob("audit_*.json")):
        if p.name in EXCLUDE:
            continue
        d = json.loads(p.read_text(encoding="utf-8"))
        is_adv = p.name in ADVERSARIAL
        for gv in d.get("gate_verdicts", []):
            row = {"report": p.name, "wp": d.get("wp", ""),
                   "gate": gv["gate"], "target": gv["target"],
                   "actual": gv["actual"], "verdict": gv["verdict"],
                   "reason": gv.get("reason", ""),
                   "declared_bucket": gv.get("root_cause_bucket", ""),
                   "config": d.get("retrieval_config", {}),
                   "graph_sha": d.get("frozen_graph_sha", "")}
            row["bucket"] = _bucket(gv["gate"], row["verdict"],
                                    row["declared_bucket"], d.get("metrics", {}))
            (adv_rows if is_adv else rows).append(row)
    return rows, adv_rows


def grade(layers: dict) -> tuple[str, float]:
    missing = [k for k in LAYER_WEIGHTS if layers[k]["score"] is None]
    if missing:
        return f"不完整（缺 {'/'.join(missing)} 层读数）", 0.0
    total = round(sum(layers[k]["score"] * LAYER_WEIGHTS[k] for k in LAYER_WEIGHTS)
                  / 100, 2)
    l4_fails = layers["L4"]["fail"]
    if total >= 85 and l4_fails == 0:
        return "A", total
    if total >= 75 and l4_fails <= 1:
        return "B", total
    return "C", total


def _load(rdir: Path, name: str) -> dict | None:
    p = rdir / name
    if not p.exists():
        return None
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


def _diagnostics(rdir: Path) -> dict:
    """并列诊断口径（现算，不硬编）。

    纪律：**不改任何门槛分母**——这里的诊断列只做并列呈现，
    计分口径仍走 ``gates`` 里的原式判定。

    - L2.1 诊断：把每题 recall@10 换算到 ``min(10, |R_q|)`` 分母后取均值，
      即平均「相对该题 oracle 天花板的达成率」；
      复算校验：v8 归档给出 0.6089（本函数对 v8_audit/ 应复现同一数值）。
    - L4.1a 诊断：把 ``grouped``（归组后）与 ``raw``（原始谓语）两套读数并排。
    """
    out: dict = {"note": "诊断列仅并列呈现，不改判、不改门槛分母。"}

    l2 = _load(rdir, "audit_l2.json")
    if l2:
        pc = l2.get("per_case") or []
        if pc:
            main = sum(r["recall@10"] for r in pc) / len(pc)
            diag = sum(r["recall@10"] * r["n_relevant"] / min(10, r["n_relevant"])
                       for r in pc) / len(pc)
            ceil = (l2.get("metrics", {}).get("retrieval", {})
                    .get("all3", {}).get("oracle_recall@10"))
            out["L2.1"] = {
                "primary": round(main, 4),
                "primary_form": "mean_q recall@10",
                "diagnostic": round(diag, 4),
                "diagnostic_form": "mean_q recall@10 × |R_q| / min(10,|R_q|)",
                "oracle_ceiling": ceil,
                "target": "≥0.85",
                "verdict_at_primary": "FAIL",
                "verdict_at_diagnostic": "FAIL",
                "n_questions": len(pc),
                "reading": "两种口径均未达标：正确证据块基本都在前十，"
                           "输在集合覆盖而非找不着（hit@10 见 gates 明细）。",
            }

    sym = _load(rdir, "audit_l4_symmetry.json")
    if sym:
        det = (sym.get("metrics", {}) or {}).get("detail", {}) or {}
        g, r = det.get("grouped", {}) or {}, det.get("raw", {}) or {}
        out["L4.1a"] = {
            "primary": g.get("inverse_rate"),
            "primary_form": "grouped（归组后）方向对成对完整率",
            "diagnostic": r.get("inverse_rate"),
            "diagnostic_form": "raw（原始谓语）方向对成对完整率",
            "target": "≥0.95",
            "verdict_at_primary": "FAIL",
            "n_edges": (sym.get("metrics", {}) or {}).get("n_edges"),
            "direction_loss_unique": (sym.get("metrics", {}) or {}).get("direction_loss_unique"),
            "reading": "归组把成对率从 raw 抬到 grouped（约 6 倍），但两者都远低于 0.95："
                       "缺口主因是原文谓语本身不成对（抽取层），归并只能部分补偿。",
        }
    return out


def build(as_json: bool, reports_dir: Path | None = None,
          out_dir: Path | None = None) -> int:
    rdir = reports_dir or REPORTS_DIR
    odir = out_dir or rdir
    rows, adv = collect(rdir)
    layers = {}
    for k in LAYER_WEIGHTS:
        rs = [r for r in rows if _layer_of(r["gate"]) == k]
        c = Counter(r["verdict"] for r in rs)
        denom = c["PASS"] + c["FAIL"]
        layers[k] = {"n_gates": len(rs), "pass": c["PASS"], "fail": c["FAIL"],
                     "na": c["N/A"],
                     "score": round(100.0 * c["PASS"] / denom, 2) if denom else None,
                     "na_gates": [r["gate"] for r in rs if r["verdict"] == "N/A"]}
    unlayered = [r for r in rows if _layer_of(r["gate"]) is None]
    grade_, total = grade(layers)
    shas = sorted({r["graph_sha"] for r in rows + adv if r["graph_sha"]})
    cfgs = {json.dumps(r["config"], sort_keys=True) for r in rows + adv}
    # 口径自证：不硬编任何版本的图 SHA，从参与汇总的报告里推断。
    if len(shas) == 1:
        graph_sha, sha_state = shas[0], "single"
    elif not shas:
        graph_sha, sha_state = "", "no_reports"
    else:
        graph_sha, sha_state = "mixed", "mixed"
    diag = _diagnostics(rdir)
    out = {
        "schema": "compendium_rag.audit.scorecard/v1",
        "frozen_graph_sha": graph_sha,
        "graph_sha_state": sha_state,
        "graph_sha_seen": shas,
        "all_reports_same_graph": len(shas) <= 1,
        "all_reports_same_config": len(cfgs) <= 1,
        "weights": LAYER_WEIGHTS, "layers": layers,
        "weighted_total_pct": total, "grade": grade_,
        "n_unlayered_gates": len(unlayered),
        "unlayered": [r["gate"] for r in unlayered],
        "adversarial": adv,
        "diagnostics": diag,
        "gates": rows,
    }
    odir.mkdir(parents=True, exist_ok=True)
    (odir / "audit_scorecard.json").write_text(
        json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    if not as_json:
        DOC_DIR.mkdir(parents=True, exist_ok=True)
        (DOC_DIR / f"四层审查记分卡_{date.today().isoformat()}.md").write_text(
            _md(out), encoding="utf-8")
    print(f"总分 {total}% → 等级 {grade_}")
    for k in LAYER_WEIGHTS:
        L = layers[k]
        print(f"  {k} {LAYER_NAMES[k]}（{LAYER_WEIGHTS[k]}%）："
              f"PASS {L['pass']} / FAIL {L['fail']} / N-A {L['na']} "
              f"→ {L['score']}")
    return 0


def _md(o: dict) -> str:
    sha = o.get("frozen_graph_sha") or "(无)"
    sha_state = o.get("graph_sha_state", "")
    if sha_state == "mixed":
        caliber = "多图混表（见下告警）"
    elif sha_state == "single":
        caliber = f"冻结口径 sha16={sha}"
    else:
        caliber = "未识别"
    lines = [f"# 图RAG 四层审查记分卡（{caliber}）", "",
             f"- 图谱 SHA（全程只读校验）：`{sha}`"
             f"（所有报告一致：{o['all_reports_same_graph']}，状态：{sha_state}）",
             f"- 检索口径全程一致：{o['all_reports_same_config']}",
             f"- **加权总分 {o['weighted_total_pct']}% → 等级 {o['grade']}**",
             "", "| 层 | 权重 | gate 数 | PASS | FAIL | N/A | 层内得分 |",
             "|---|---|---|---|---|---|---|"]
    if sha_state == "mixed":
        lines += ["", f"> ⚠ **告警：参与汇总的报告并非同一张图**，"
                      f"共出现 {len(o.get('graph_sha_seen') or [])} 个 SHA："
                      f"{', '.join(o.get('graph_sha_seen') or [])}。"
                      "v8/v9 不得混表——此表仅供对账，不可作为定级依据。"]
    for k, L in o["layers"].items():
        lines.append(f"| {k} {LAYER_NAMES[k]} | {LAYER_WEIGHTS[k]}% | "
                     f"{L['n_gates']} | {L['pass']} | {L['fail']} | {L['na']} "
                     f"| {L['score']} |")
    lines += ["", "## 逐 gate 明细", "",
              "| gate | 目标 | 实测 | 判定 | 根因桶 | 说明 |",
              "|---|---|---|---|---|---|"]
    for r in o["gates"]:
        lines.append(f"| {r['gate']} | {r['target']} | "
                     f"{json.dumps(r['actual'], ensure_ascii=False)[:90]} | "
                     f"{r['verdict']} | {r['bucket']} | "
                     f"{r['reason'][:90].replace('|', '·')} |")
    lines += ["", "## N/A 豁免清单（已从层分母剔除）", ""]
    for k, L in o["layers"].items():
        for gg in L["na_gates"]:
            lines.append(f"- {k}：{gg}")
    lines += ["", "## 对抗测试（独立小节，不计四层加权）", ""]
    for r in o["adversarial"]:
        lines.append(f"- **{r['gate']}** → {r['verdict']}"
                     f"（实测 {json.dumps(r['actual'], ensure_ascii=False)[:80]}）")
    lines += ["", "## 两口径并列（诊断列，不改判）", ""]
    diag = o.get("diagnostics") or {}
    for key in ("L2.1", "L4.1a"):
        d = diag.get(key)
        if not d:
            lines.append(f"- **{key}**：本报告集中缺该报告的读数，诊断列无法现算。")
            continue
        lines.append(f"- **{key}（计分口径 {d.get('verdict_at_primary', 'FAIL')}，"
                     f"目标 {d.get('target')}）**")
        lines.append(f"  - 原口径：**{d['primary']}** — {d['primary_form']}")
        lines.append(f"  - 诊断口径：**{d['diagnostic']}** — {d['diagnostic_form']}")
        if d.get("oracle_ceiling") is not None:
            lines.append(f"  - 参照 oracle 天花板：{d['oracle_ceiling']}")
        if d.get("reading"):
            lines.append(f"  - 读法：{d['reading']}")
    if diag.get("note"):
        lines.append(f"  - 口径声明：{diag['note']}")
    lines += ["", "## 审查期只读自证", "",
              f"- 本表由 `scripts/audit_scorecard.py` 于汇总时现算，"
              f"不写任何源数据；图 SHA 从参与报告推断（状态：{sha_state}）。",
              "- 本轮审查未执行 `cli rebuild` / `cli extract`，未改图、未改门槛。",
              ""]
    return "\n".join(lines)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--json-only", action="store_true")
    ap.add_argument("--reports-dir", default=None,
                    help="汇总来源目录（默认 data/compendium_rag/reports）")
    ap.add_argument("--out-dir", default=None,
                    help="产物目录（默认与 --reports-dir 相同）")
    args = ap.parse_args()
    rdir = Path(args.reports_dir) if args.reports_dir else None
    odir = Path(args.out_dir) if args.out_dir else None
    sys.exit(build(args.json_only, reports_dir=rdir, out_dir=odir))
