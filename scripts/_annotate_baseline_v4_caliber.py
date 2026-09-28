# -*- coding: utf-8 -*-
"""给 BASELINE_v4 的机器可读锁定件加「暖/冷双口径」注记（只增字段，不改既有数字）。

用户裁决 Q1=(a)：加注而非重锁。理由——
  * baseline_v4.json 的 7 个工件 SHA-16 全部自洽且已入库（可复算命中）；
  * 缺陷只在「口径未标注」，不在数字被篡改；
  * 重锁会抹掉一段真实历史（暖态测量本身是合法证据，只是不能当冷启动口径用）。

本脚本幂等：重复运行结果一致。仅新增顶层键 `caliber_annotation`，
并**校验既有 7 个 SHA 在加注前后不变**（防止误改）。
"""
from __future__ import annotations

import hashlib
import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
P = ROOT / "data/compendium_rag/reports/baseline_v4.json"

ANNOTATION = {
    "annotated_at": "2026-09-27",
    "annotated_by": "#39 复验收官（用户裁决 Q1=(a)：加注暖/冷双口径，不重锁）",
    "scope": "本文件 primary/secondary 的全部「实测」数字为**暖态（warm-process）测量**，非冷启动可复现口径。",
    "reason": (
        "R4 的评测跑在 Applier 落盘后的同一进程内（内存 alias_index 插入序）；"
        "冷启动自 graph.json 重建（文件序）插入序不同，"
        "根因见 retriever.py:300 稳定排序无显式次级键。"
    ),
    "warm_vs_cold": {
        "300cn_bare_hit6": {"warm": 0.8112, "warm_hits": "159/196",
                            "cold": 0.7959, "cold_hits": "156/196"},
        "300cn_rerank_hit6": {"warm_refit_alpha0.3": 0.8673, "warm_alpha1.0": 0.8571,
                              "cold_alpha1.0": 0.8724, "cold_loo_cv": 0.8622},
        "gen120_hit6": {"warm": 0.8083, "warm_hits": "97/120",
                        "cold": 0.8000, "cold_hits": "96/120"},
        "300cn_graph_only": {"cold": 0.6735, "cold_hits": "132/196"},
        "target_line_0.85": {"warm": "PASS", "cold": "PASS（0.8724）"},
    },
    "r4_gain_attribution": (
        "R4 的 +4 题收益（300cn 的 R163/R248/R299 + 泛化的 GA-20）全部为暖态测量；"
        "冷启动收益为 0 —— vs after_r3 逐题零差异，vs after_r4 恰此 4 题翻回。"
    ),
    "severity_measured": (
        "修复前实测：300 题中 37 题的 seeds 随 alias_index 插入序改变"
        "（PPR/RRF 吸收了大部分，故仅 3 题翻转 hit@6）。"
    ),
    "frozen_artifacts_status": "本文件 7 个 SHA-16 均可由 git blob 重算命中（含 graph_live=c021f0a0bc7a0dce），冻结件本身自洽。",
    "replacement": "修复后的确定值记入 BASELINE_v5（R5 落盘时一并锁定）；本基线不重锁。",
    "reference": "docs/compendium-rag/baseline-repairs/核验报告_20260927_分支A复验与R4差异归因.md；docs/compendium-rag/baseline-repairs/图谱修复作战书_预注册_20260926.md §4bis",
}


def sha16(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()[:16]


def main() -> int:
    raw_before = P.read_bytes()
    doc = json.loads(raw_before.decode("utf-8"))
    locks_before = dict(doc.get("artifact_sha256_16", {}))

    doc["caliber_annotation"] = ANNOTATION

    # 只增字段：既有顶层键与数字必须逐字未动
    body = json.dumps(doc, ensure_ascii=False, indent=2)
    after = json.loads(body)
    assert after["artifact_sha256_16"] == locks_before, "冻结 SHA 被改动，拒绝写入"
    for k in ("baseline", "frozen_at", "graph", "primary", "secondary"):
        assert after[k] == json.loads(raw_before.decode("utf-8"))[k], f"{k} 被改动"

    shutil.copy2(P, P.with_suffix(".json.prev_annotate"))
    P.write_text(body, encoding="utf-8")
    print(f"[ok] 已加注 {P.name}")
    print(f"     sha16 {sha16(raw_before)} -> {sha16(P.read_bytes())}（仅新增 caliber_annotation）")
    print(f"     既有 7 个冻结 SHA 未变动: {sorted(locks_before) == sorted(after['artifact_sha256_16'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
