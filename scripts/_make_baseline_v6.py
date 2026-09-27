# -*- coding: utf-8 -*-
"""生成 BASELINE_v6 机器可读锁定件（词面通道启用后的冷启动基线）。

与 v5 的差别：
  - 检索配置新增 `lex_weight=1.0`（词面通道），故 v6 的裸检索口径与 v5 不可直接混比；
  - 记录 300cn / 泛化 / 盲测 三条线的 lex=0 vs lex=1 对照，便于追溯；
  - 安全线（unanswerable / grounded）逐项复核；
  - R4-K01 处置状态延续登记。

纪律：所有数字须来自**启用 lex 后的冷启动**落盘报告；缺失即标 PENDING，不猜。
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
D = ROOT / "data/compendium_rag"
R = D / "reports"


def sha16(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()[:16]


def load(name):
    p = R / name
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else None


def rate(doc, mode="full", answerable=True):
    if doc is None:
        return None
    rows = [r for r in doc["rows"]
            if r.get("mode") == mode and bool(r.get("answerable")) is answerable]
    if not rows:
        return None
    h = sum(1 for r in rows if r.get("hit"))
    g = sum(1 for r in rows if r.get("grounded"))
    return {"hits": h, "n": len(rows), "rate": round(h / len(rows), 4),
            "grounded_rate": round(g / len(rows), 4)}


def main() -> int:
    g = json.loads((D / "graph.json").read_text(encoding="utf-8"))
    v5 = load("baseline_v5.json")

    blind_on = load("eval_blind_lex_on.json")
    blind_tb = load("eval_blind_lex_tiebreak.json")
    c300 = load("eval_300cn_lex_tiebreak.json") or load("eval_300cn_lex_on.json")
    gen = load("eval_gen_lex_tiebreak.json") or load("eval_gen_lex_on.json")
    safety_on = load("eval_300cn_lex_tiebreak.json") or load("eval_300cn_lex_on.json")
    acc = load("baseline_v6_acceptance.json") or {}

    blind_final = blind_tb or blind_on
    # 生产口径（full + 冻结重排）—— 目标②的验收判据
    prod_blind = (acc.get("blind206 (留出集)") or {})
    prod_300 = (acc.get("300cn (调参集)") or {})
    doc = {
        "baseline": "BASELINE_v6",
        "frozen_at": "2026-09-28",
        "freeze_scope": ("词面通道（BM25，lex_weight=1.0）启用后冻结；"
                        "取代 BASELINE_v5（v5 为 lex=0 口径，两者不可直接混比）"),
        "retrieval_config": {
            "lex_weight": 1.0,
            "lex_top": 30,
            "note": ("启用词面通道。该通道不依赖实体链接/嵌入，用于补上"
                     "『无任何通道命中』的候选；权重 1.0 系仅在 300cn 上选定，"
                     "盲测 206 题为留出集。"),
            "rollback": "CMPRAG_LEX_WEIGHT=0 即回到 BASELINE_v5 口径",
        },
        "graph": {
            "entities": len(g["entities"]),
            "edges": len(g["edges"]),
            "sha256_16": sha16(D / "graph.json"),
            "repair_batches": ["R1(20)", "R2(71)", "R3(18生效)", "R4(78)", "R5(312 add_edge)"],
        },
        "primary_blind": {
            "caliber": "子代理盲写 206 题留出集（无泄题、与 300cn 零重叠）",
            "production_rerank_hit6": prod_blind.get("rerank_hit6"),
            "production_caliber": "full + 冻结重排（在 300cn 上拟合，未在盲测集重新拟合）",
            "bare_hit6": rate(blind_final),
            "up": prod_blind.get("up"), "down": prod_blind.get("down"),
            "target_line": 0.85,
            "verdict": None,
        },
        "secondary_300cn": {
            "production_rerank_hit6": prod_300.get("rerank_hit6"),
            "lex_on_bare_hit6": rate(c300),
            "lex_on_graph_only": rate(c300, mode="graph_only"),
            "safety_unanswerable": rate(safety_on, answerable=False),
        },
        "generalization_120": {
            "lex_on_full_hit6": rate(gen),
        },
        "comparison_vs_v5": {
            "note": "同一题集上 lex=0（v5 口径）vs lex=1（v6 口径）",
            "300cn": {"lex0": 0.7959, "lex1": rate(c300)["rate"] if rate(c300) else None},
            "blind206": {"lex0": 0.6408,
                         "lex1": rate(blind_final)["rate"] if rate(blind_final) else None},
            "gen120": {"lex0": 0.8000, "lex1": rate(gen)["rate"] if rate(gen) else None},
        },
        "determinism": {
            "rrf_secondary_key": "已加（排序键 (-score, chunk_id)，通道按名排序）",
            "evidence": "scripts/_rrf_tie_probe.py 实测 120 题中 116 题存在分数并列",
            "harness": "scripts/_rrf_determinism.py 多 hashseed 一致",
        },
        "r4_k01_status": {
            "state": "NOT-APPLIED（用户裁决：暂不执行）",
            "detail": "诊所的别名『诊疗』仲裁未落盘；Applier 曾因缺 alias 字段 fail-closed。",
        },
        "artifact_sha256_16": {},
        "unfreeze": "R6 或 P4 StaticReranker 接线前冻结；落盘后以 BASELINE_v7 取代",
    }
    p = doc["primary_blind"]
    if p["production_rerank_hit6"] is not None:
        p["verdict"] = "PASS" if p["production_rerank_hit6"] >= 0.85 else "FAIL"

    for key, rel in [("graph_live", "graph.json"),
                     ("baseline_v5", "reports/baseline_v5.json"),
                     ("eval_300cn_lex_on", "reports/eval_300cn_lex_on.json"),
                     ("eval_gen_lex_on", "reports/eval_gen_lex_on.json"),
                     ("eval_blind_lex_on", "reports/eval_blind_lex_on.json"),
                     ("eval_blind_lex_tiebreak", "reports/eval_blind_lex_tiebreak.json"),
                     ("eval_300cn_lex_off", "reports/eval_blind_lex_off.json")]:
        fp = D / rel
        if fp.exists():
            doc["artifact_sha256_16"][key] = sha16(fp)

    out = R / "baseline_v6.json"
    out.write_text(json.dumps(doc, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[ok] -> {out}")
    print(json.dumps({k: doc[k] for k in
                      ("primary_blind", "secondary_300cn", "generalization_120",
                       "comparison_vs_v5")}, ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
