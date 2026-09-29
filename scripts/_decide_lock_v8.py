# -*- coding: utf-8 -*-
"""生成并校验 BASELINE_v8：v7 + R6（摘除死别名 诊疗@诊所）。

v8 = v7 的检索配置（lex_weight=1.0, rrf_k=1）+ 新图（026b41699f021db2）。
指标零变化（R6 只影响 GA-25，冷启动实测与 v7 一致）。
v8 的意义：承接 R6 改图后的新 **live 锚点**，并闭合 R4-K01 悬置仲裁。
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data/compendium_rag"
R = DATA / "reports"


def sha16(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()[:16]


ARTIFACTS = {
    "graph_live": "graph.json",
    "graph_prev_r6": "backups/graph.json.prev.r6",
    "baseline_v7": "reports/baseline_v7.json",
    "repairs_v6_proposal": "repairs_v6/proposal.json",
    "eval_300cn_v7_rerun": "reports/eval_300cn_k1.json",
    "eval_blind_v7_rerun": "reports/eval_blind_k1.json",
    "eval_gen120_v7_rerun": "reports/eval_gen120_k1.json",
    "rank_collect_300cn_v7": "reports/rank_collect_k1c300_top30.json",
}

locks, missing = {}, []
for k, rel in ARTIFACTS.items():
    p = DATA / rel
    if not p.exists():
        missing.append(f"{k} -> {rel}")
        continue
    locks[k] = sha16(p)
if missing:
    print("[FATAL] 缺失：", missing)
    raise SystemExit(1)

doc = {
    "baseline": "BASELINE_v8",
    "frozen_at": "2026-09-28",
    "supersedes": "BASELINE_v7",
    "freeze_scope": (
        "v7 的检索配置（lex_weight=1.0, rrf_k=1）不变，仅**图谱**因 R6 变更："
        "摘除死别名 诊疗@诊所（执行 R4-K01 于 2026-09-27 作出但未落盘的仲裁）。"
        "指标零变化。"
    ),
    "retrieval_config": {
        "lex_weight": 1.0,
        "lex_top": 30,
        "lex_first": 0,
        "rrf_k": 1,
        "note": "与 v7 **完全相同**；本轮未改检索逻辑。",
    },
    "graph": {
        "entities": 7033,
        "edges": 30269,
        "sha256_16": locks["graph_live"],
        "prev": "4bbefd9eba577c01 (prev.r6，可回滚)",
        "change": "别名 诊疗@诊所 摘除；别名总数 917 -> 916",
        "change_proof": (
            "与 prev.r6 逐项对比：实体集合相同、边内容指纹相同"
            "（8be363bbe3d00044）、除 aliases 外 0 处字段变化、恰 1 个实体别名变化。"
            "见 scripts/_decide_verify_r6.py。"
        ),
    },
    "metrics": {
        "note": "指标**零变化**：R6 只影响含『诊疗』的题，三集共 1 道（GA-25），"
                "冷启动实测 hit/rr 与 v7 完全一致（scripts/_decide_r6_no_change.py）。",
        "300cn_bare_hit6": {"hits": 167, "n": 196, "rate": 0.8520},
        "blind206_bare_hit6": {"hits": 184, "n": 206, "rate": 0.8932},
        "gen120_bare_hit6": {"hits": 118, "n": 120, "rate": 0.9833},
        "300cn_production_hit6": 0.8673,
        "blind206_production_hit6": 0.9175,
        "safety_unanswerable": {"hits": 1, "n": 104},
        "grounded": 1.0,
    },
    "r4_k01_status": {
        "state": "**APPLIED（2026-09-28，以新批次 R6 执行）**",
        "gate": "预注册闸门『摘除后 GA-25 必须保持命中』实测 PASS（冷启动复测一致）",
        "why_new_batch": (
            "不修改 repairs_v4/proposal.json —— 其 R4-K01 必须保持 keep_with_note，"
            "否则从 prev.r4 重放无法复现冻结 SHA c021f0a0bc7a0dce（BASELINE_v4 锚点）。"
        ),
        "metric_effect": "零（卫生性修复，不记作能力提升）",
    },
    "superseded_anchor_note": (
        "v6/v7 的 artifact_sha256_16.graph_live 指向 4bbefd9eba577c01，"
        "该图已被 R6 取代（按设计失效）。历史惯例：v4 的验收判据为"
        "「除 live 外 6/6 命中」，即 live 锚点随图演进、其余工件锁不变。"
    ),
    "artifact_sha256_16": locks,
    "artifact_paths": ARTIFACTS,
    "unfreeze": "P3 补抽提或 P4 接线前冻结；落盘后以 BASELINE_v9 取代",
}

out = R / "baseline_v8.json"
out.write_text(json.dumps(doc, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"-> {out.relative_to(ROOT)}\n")
print("=== 立即复算校验 ===")
ok = True
for k, rel in ARTIFACTS.items():
    got = sha16(DATA / rel)
    good = got == locks[k]
    ok &= good
    print(f"  [{'OK ' if good else 'BAD'}] {k:24} {got}  ({rel})")
print(f"\n判定: {'全部命中 ✓' if ok else '存在不一致 ✗'}")
raise SystemExit(0 if ok else 1)
