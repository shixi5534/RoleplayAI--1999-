# -*- coding: utf-8 -*-
"""生成并校验 BASELINE_v7 锁（取代 v6）。

v7 = v6 + `CMPRAG_RRF_K=1`（其余配置不变，图未改）。
本脚本：
  1. 从磁盘工件计算 SHA-16；
  2. 写出 baseline_v7.json（含正确文件名映射，修正 v6 锁键 eval_300cn_lex_off
     指向盲测文件的历史缺陷）；
  3. 立刻复算校验，确保 100% 可命中。
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


# 键 -> 相对 data/compendium_rag 的路径（显式、真实存在）
ARTIFACTS = {
    "graph_live": "graph.json",
    "baseline_v6": "reports/baseline_v6.json",
    "eval_300cn_v7": "reports/eval_300cn_k1.json",
    "eval_blind_v7": "reports/eval_blind_k1.json",
    "eval_gen120_v7": "reports/eval_gen120_k1.json",
    "rank_collect_300cn_v7": "reports/rank_collect_k1c300_top30.json",
    "rank_collect_blind_v7": "reports/rank_collect_k1blind_top30.json",
}

locks: dict[str, str] = {}
missing: list[str] = []
for k, rel in ARTIFACTS.items():
    p = DATA / rel
    if not p.exists():
        missing.append(f"{k} -> {rel}")
        continue
    locks[k] = sha16(p)

if missing:
    print("[FATAL] 缺失工件：")
    for m in missing:
        print("   ", m)
    raise SystemExit(1)

doc = {
    "baseline": "BASELINE_v7",
    "frozen_at": "2026-09-28",
    "supersedes": "BASELINE_v6",
    "freeze_scope": (
        "在 v6（词面通道 lex_weight=1.0）之上，追加 RRF 排名折扣常数 "
        "CMPRAG_RRF_K=1（v6/v5 为历史默认 k=60）。图与题集均未改动。"
    ),
    "retrieval_config": {
        "lex_weight": 1.0,
        "lex_top": 30,
        "lex_first": 0,
        "rrf_k": 1,
        "note": (
            "rrf_k 是**唯一**新旋钮。k 越小，各通道头部名次的相对权重越大："
            "k=60 时 rank1/rank6 仅差 1/61 vs 1/66（+8%），k=1 时为 1/2 vs 1/7（3.5×），"
            "即在多个通道都排前列的候选显著胜出。前序会话只扫过通道权重"
            "（w_lex 1→16）而从未扫 k。k 在 300cn 上选（k=1 与 k=2 同分，取更小者），"
            "盲测 206 为留出集。"
        ),
        "rollback": "CMPRAG_RRF_K=60 即回到 BASELINE_v6 口径；再置 CMPRAG_LEX_WEIGHT=0 回到 v5",
    },
    "graph": {
        "entities": 7033,
        "edges": 30269,
        "sha256_16": locks["graph_live"],
        "note": "v7 未改图（与 v6 同一图）",
    },
    "primary_blind": {
        "caliber": "子代理盲写 206 题留出集（无泄题、与 300cn 零重叠）",
        "bare_hit6": {"hits": 184, "n": 206, "rate": 0.8932},
        "bare_hit6_graph_only": {"hits": 174, "n": 206, "rate": 0.8447},
        "production_rerank_hit6": 0.9175,
        "production_caliber": "full + 冻结重排（权重在 300cn 上拟合，未在盲测重拟合）",
        "up": 17, "down": 5,
        "target_line": 0.85,
        "verdict": "PASS",
        "prev_v6": {"bare_hit6": 0.8350, "production_rerank_hit6": 0.8786},
    },
    "secondary_300cn": {
        "bare_hit6": {"hits": 167, "n": 196, "rate": 0.8520},
        "bare_hit6_graph_only": {"hits": 157, "n": 196, "rate": 0.8010},
        "production_rerank_hit6": 0.8673,
        "up": 6, "down": 4,
        "target_line": 0.85,
        "verdict": "PASS",
        "prev_v6": {"bare_hit6": 0.8418, "production_rerank_hit6": 0.8673},
    },
    "generalization_120": {
        "bare_hit6": {"hits": 118, "n": 120, "rate": 0.9833},
        "bare_hit6_graph_only": {"hits": 116, "n": 120, "rate": 0.9667},
        "prev_v6": {"bare_hit6": 0.9083},
    },
    "safety_line": {
        "unanswerable_hits": 1, "unanswerable_n": 104,
        "grounded": 1.0,
        "note": "与 v6 完全相同（1/104、1.0000），无新增虚假命中",
    },
    "caveats": [
        "300cn 的 31 道 miss 中有 15 道经独立审计为 gold 缺陷（见 "
        "data/knowledge/_audit/_85_gold_audit.json）；该审计**未用于**抬分，"
        "题集本体未改动，仅作诊断背景。",
        "rrf_k=1 使 RRF 分数尺度从 ~1/61 变为 ~1/2。冻结重排对 orig(RRF分) 的权重"
        "实测为 0.0，故不扭曲权重；已在 k=1 池上实测生产口径无回退（300cn 0.8673）。",
        "所有数字为冷启动产出（PYTHONHASHSEED=0，独立进程）。",
    ],
    "artifact_sha256_16": locks,
    "artifact_paths": ARTIFACTS,
    "unfreeze": "R6 或 P4 StaticReranker 接线前冻结；落盘后以 BASELINE_v8 取代",
}

out = R / "baseline_v7.json"
out.write_text(json.dumps(doc, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"-> {out}\n")

print("=== 立即复算校验 ===")
ok = True
for k, rel in ARTIFACTS.items():
    got = sha16(DATA / rel)
    good = got == locks[k]
    ok &= good
    print(f"  [{'OK ' if good else 'BAD'}] {k:26} {got}  ({rel})")
print(f"\n判定: {'全部命中 ✓' if ok else '存在不一致 ✗'}")
