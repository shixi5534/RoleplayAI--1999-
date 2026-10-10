# -*- coding: utf-8 -*-
"""P6 · L4.5 R8 重新盲评的**合成器**（只读，只写一个报告）。

读 ``data/knowledge/_audit/l4_multiscene_r8/`` 下的 4 份盲评 +
``arm_map.json``，合成：
- **臂 A**（R8 前已判分的那 60 块，edges 换成 R8 现状）= 可与 R8 前逐块比较的读数；
- **臂 B**（R8 图上自然抽样的 60 块）= 若照原规则重抽会得到的读数；
- 两臂共有的 58 块逐块 delta（对照 R8 前 ``../l4_multiscene/ms_b0*_review.json``）。

判据：L4.5 gate ≥4.0/5。以**臂 A 为主读数**（保持与 3.9333 可比），
臂 B 并列披露（说明抽样边界变动带来的差异）。

红线：只读、只写 ``reports/p6_l45_r8.json`` 与 ``p6_l45_r8.md``；不用
rmtree/unlink；不联网；不调 LLM。
"""
from __future__ import annotations

import json
import statistics
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AUD = ROOT / "data" / "knowledge" / "_audit"
R8_DIR = AUD / "l4_multiscene_r8"
PRE_DIR = AUD / "l4_multiscene"
REP = ROOT / "data" / "compendium_rag" / "reports"

GATE = 4.0


def load_reviews(d: Path, pattern: str) -> dict:
    out = {}
    for p in sorted(d.glob(pattern)):
        data = json.loads(p.read_text(encoding="utf-8"))
        for it in data["items"]:
            out[it["chunk_id"]] = it
    return out


def mean_of(rev: dict, ids: list[str]) -> float | None:
    vals = [rev[c]["coherence"] for c in ids if c in rev]
    return round(statistics.mean(vals), 4) if vals else None


def dist(rev: dict, ids: list[str]) -> dict:
    from collections import Counter
    c = Counter(rev[i]["coherence"] for i in ids if i in rev)
    return {str(k): c[k] for k in sorted(c)}


def main() -> int:
    am = json.loads((R8_DIR / "arm_map.json").read_text(encoding="utf-8"))
    arm_a: list[str] = am["arm_a_frozen_pre_r8"]
    arm_b: list[str] = am["arm_b_natural_r8"]

    r8 = load_reviews(R8_DIR, "ms_b*_review.json")
    pre = load_reviews(PRE_DIR, "ms_b*_review.json")
    if not r8:
        print("[FATAL] 没有 R8 盲评产物", file=sys.stderr)
        return 2

    missing_a = [c for c in arm_a if c not in r8]
    missing_b = [c for c in arm_b if c not in r8]

    a_mean = mean_of(r8, arm_a)
    b_mean = mean_of(r8, arm_b)
    pre_mean = mean_of(pre, arm_a)

    common = [c for c in arm_a if c in r8 and c in pre]
    deltas = {c: r8[c]["coherence"] - pre[c]["coherence"] for c in common}
    up = sorted([c for c, d in deltas.items() if d > 0])
    down = sorted([c for c, d in deltas.items() if d < 0])

    mismatch_a = {c: r8[c]["n_mismatch"] for c in arm_a if c in r8
                  and r8[c].get("n_mismatch")}
    still_bad = {c: r8[c]["coherence"] for c in arm_a
                 if c in r8 and r8[c]["coherence"] <= 2}

    rep = {
        "schema": "audit.p6_l45_r8/v1",
        "graph_sha16": am.get("graph_sha16"),
        "pool_size_r8": am.get("pool_size_r8"),
        "n_union": am.get("n_union"),
        "n_reviewed": len(r8),
        "arm_a": {
            "n": len(arm_a), "n_reviewed": len(arm_a) - len(missing_a),
            "missing": missing_a, "mean": a_mean,
            "dist": dist(r8, arm_a), "gate": GATE,
            "verdict": "PASS" if (a_mean is not None and a_mean >= GATE)
            else "FAIL",
            "pre_r8_mean": pre_mean,
            "delta_vs_pre_r8": (None if a_mean is None or pre_mean is None
                                else round(a_mean - pre_mean, 4)),
        },
        "arm_b": {
            "n": len(arm_b), "n_reviewed": len(arm_b) - len(missing_b),
            "missing": missing_b, "mean": b_mean,
            "dist": dist(r8, arm_b),
            "verdict": "PASS" if (b_mean is not None and b_mean >= GATE)
            else "FAIL",
        },
        "common_with_pre_r8": {
            "n": len(common),
            "n_up": len(up), "n_down": len(down), "n_same": len(common) - len(up) - len(down),
            "up": up, "down": down,
        },
        "arm_a_detail": {
            c: {"coherence": r8[c]["coherence"],
                "n_edges": r8[c].get("n_edges"),
                "n_mismatch": r8[c].get("n_mismatch"),
                "pre_r8_coherence": pre.get(c, {}).get("coherence")}
            for c in arm_a if c in r8
        },
        "still_le2_in_arm_a": still_bad,
        "mismatch_blocks_in_arm_a": mismatch_a,
    }

    REP.mkdir(parents=True, exist_ok=True)
    (REP / "p6_l45_r8.json").write_text(
        json.dumps(rep, ensure_ascii=False, indent=2), encoding="utf-8")

    md = [
        "# P6 · L4.5 多角色互洽 · R8 重新盲评合成",
        "",
        f"- 图 SHA16：`{am.get('graph_sha16')}`（R8 修边 28 条后，边 27135）",
        f"- 候选池：{am.get('pool_size_r8')} 块；并集样本 {am.get('n_union')} 块；"
        f"实际判分 {len(r8)} 块",
        "",
        "## 双臂读数",
        "",
        f"| 臂 | 定义 | n | mean | gate ≥{GATE} |",
        "|---|---|---|---|---|",
        f"| **A（主）** | R8 前已判 60 块，edges 换 R8 现状 | "
        f"{len(arm_a) - len(missing_a)} | **{a_mean}** | "
        f"{rep['arm_a']['verdict']} |",
        f"| B（原生） | R8 图上按原规则重抽的 60 块 | "
        f"{len(arm_b) - len(missing_b)} | {b_mean} | {rep['arm_b']['verdict']} |",
        "",
        f"- 臂 A 的 R8 前同集合均值：{pre_mean} → delta "
        f"**{rep['arm_a']['delta_vs_pre_r8']}**",
        f"- 两臂共 58 块逐块比较：涨 {len(up)} / 跌 {len(down)} / 平 "
        f"{rep['common_with_pre_r8']['n_same']}",
        "",
        f"## 臂 A 分布",
        "",
        f"`{rep['arm_a']['dist']}`",
        "",
        f"## 臂 A 中仍 ≤2 的块",
        "",
        f"`{still_bad}`" if still_bad else "（无）",
        "",
        f"## 臂 A 中仍有 mismatch 的块",
        "",
    ]
    if mismatch_a:
        for c, n in sorted(mismatch_a.items(), key=lambda kv: -kv[1]):
            md.append(f"- `{c}`：n_mismatch={n}，coherence="
                      f"{r8[c]['coherence']}")
    else:
        md.append("（无）")
    md += ["", "## 说明", "",
           "- 臂 A 是主读数：它复用了 R8 前的 60 块样本，只把 edges 换成 R8 现状，"
           "因此与 3.9333 逐块可比。",
           "- 臂 B 是「若照原规则重抽」的读数，用于披露 R8 修边导致候选池 2793→2792、"
           "样本边界挪动 2 块的影响。",
           "- R8 前的 4 块 coherence=2（雷米特杯:11.0.0、绿湖:0.0.2、绿湖:1.2.0、"
           "绿湖:11.1.0）其 8 条错边已被 r8 删除，重判若仍低分属独立判断，不得改判分文件。",
           ""]
    (REP / "p6_l45_r8.md").write_text("\n".join(md), encoding="utf-8")

    print(f"A mean={a_mean} (pre {pre_mean}) verdict={rep['arm_a']['verdict']}")
    print(f"B mean={b_mean} verdict={rep['arm_b']['verdict']}")
    print(f"up={len(up)} down={len(down)} still_le2={still_bad}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
