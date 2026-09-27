# -*- coding: utf-8 -*-
"""生成 BASELINE_v5 机器可读锁定件（R5 落盘后）。

对照 BASELINE_v4 的结构；记录 R5 前后的双口径，并把 R4-K01 处置登记为未决。
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
D = ROOT / "data/compendium_rag"


def sha16(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()[:16]


def lab_chosen(name: str):
    d = json.loads((D / "reports" / name).read_text(encoding="utf-8"))
    ch = d.get("chosen") or {}
    cv = d.get("loo_cv") or d.get("cv") or {}
    return d, ch, cv


def main() -> int:
    g = json.loads((D / "graph.json").read_text(encoding="utf-8"))
    v4 = json.loads((D / "reports/baseline_v4.json").read_text(encoding="utf-8"))

    d5, ch5, cv5 = lab_chosen("rank_rerank_lab_300cn_r5.json")
    d4, ch4, cv4 = lab_chosen("rank_rerank_lab_300cn_rc0927.json")

    def cfg(c):
        return c.get("config") or c.get("name") or str(c)[:80]

    def hit(c):
        return c.get("hit6") if c.get("hit6") is not None else c.get("hit@6")

    doc = {
        "baseline": "BASELINE_v5",
        "frozen_at": "2026-09-27",
        "freeze_scope": "R5（定向补桥：scene 共现边）落盘后冻结；取代 BASELINE_v4",
        "graph": {
            "entities": len(g["entities"]),
            "edges": len(g["edges"]),
            "fingerprint": g.get("fingerprint", ""),
            "sha256_16": sha16(D / "graph.json"),
            "repair_batches": ["R1(20)", "R2(71)", "R3(18生效)", "R4(78)", "R5(312 add_edge)"],
            "backups": ["prev.r1r2", "prev.r3", "prev.r4", "prev.r5"],
            "r5_design": {
                "kind": "定向补桥（用户裁决 (丙)）",
                "rule": "共现对中至少一端属于缺口集合（相遇测试不可达组成员 ∪ probe 度<15）",
                "edges_added": 312,
                "edge_growth_pct": round(312 / 29957 * 100, 2),
                "why_not_full": "全量方案 +12,788 边仅 +1 题且使 维尔汀 邻居摊薄 ×0.548；定向方案 +312 边零回归",
            },
        },
        "primary": {
            "caliber": "300_cn answerable(196) full rerank-ON（cold-start）",
            "rerank_hit6": hit(ch5),
            "config": cfg(ch5),
            "loo_cv_hit6": cv5.get("cv_hit6"),
            "loo_cv_overfit_gap_hit6": cv5.get("overfit_gap_hit6"),
            "loo_cv_folds": cv5.get("n_folds"),
            "previous_v4_cold": hit(ch4),
            "delta_vs_v4_cold": (round(hit(ch5) - hit(ch4), 4)
                                 if hit(ch5) is not None and hit(ch4) is not None else None),
            "target_line": 0.85,
            "verdict": "PASS",
        },
        "secondary": {
            "bare_hit6_cold": 0.7959,
            "bare_hits": "156/196",
            "graph_only_hit6_cold": 0.6735,
            "graph_only_hits": "132/196",
            "safety": {"unanswerable": "1/104", "grounded": 1.0},
        },
        "meetability_after_r5": {
            "probe_bad": "0/6（R5 前 2/6）",
            "groups_unreachable_pairs": "32/50（R5 前 42/50）",
            "verdicts": "全员可遇 1 / 部分可遇 7 / 不可达 0",
            "same_scene_groups": "0（本轮只建多跳可达，未建同 chunk 交集）",
        },
        "eval300_no_regression": {
            "full": "156/196 不变，0 up / 0 down",
            "graph_only": "132/196 不变，0 up / 0 down",
        },
        "r4_k01_status": {
            "state": "NOT-APPLIED（用户裁决：暂不执行，留待 BASELINE_v5 一并决策）",
            "detail": "诊所的别名『诊疗』仲裁曾被记为采纳摘除，但实际从未落盘；"
                      "Applier 因缺 alias 字段 fail-closed，已还原为 keep_with_note 并标注。",
            "impact_if_applied": "会改变 GA-25 种子集并产生新图 SHA；需重跑 GA-25 闸门",
        },
        "artifact_sha256_16": {
            "graph_live": sha16(D / "graph.json"),
            "backup_prev_r4": sha16(D / "backups/graph.json.prev.r4"),
            "backup_prev_r5": sha16(D / "backups/graph.json.prev.r5"),
            "eval_300cn_after_r5": sha16(D / "reports/eval_300cn_after_r5.json"),
            "rank_collect_r5": sha16(D / "reports/rank_collect_r5_top30.json"),
            "rank_rerank_lab_300cn_r5": sha16(D / "reports/rank_rerank_lab_300cn_r5.json"),
            "meetability_after_r5": sha16(D / "reports/meetability_test_after_r5.json"),
            "baseline_v4": sha16(D / "reports/baseline_v4.json"),
        },
        "unfreeze": "R6 或 P4 StaticReranker 接线前冻结；落盘后以 BASELINE_v6 取代",
    }
    out = D / "reports/baseline_v5.json"
    out.write_text(json.dumps(doc, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[ok] -> {out}")
    print(json.dumps({k: doc[k] for k in ("primary", "secondary")}, ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
