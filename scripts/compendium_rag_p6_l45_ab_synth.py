"""P6 · L4.5 干净 A/B 合成器（V9P1 基线臂 vs R8 臂，同一批 62 块）。

只读：读两臂 review.json + 两臂 arm_map.json + 两份图（用于确认 18/44 分块），
写 data/compendium_rag/reports/p6_l45_ab.json 与 .md。

口径：A = V9P1 图（backups/graph.json.prev.r8, sha16 7cac5867e8c80879）
      B = R8 图（data/compendium_rag/graph.json, sha16 56507b18ac2113b6）
两臂输入块集合完全相同（62 块），批次切分相同（16/16/16/14），
故可直接逐块配对比较 —— 这是唯一能把「修边效果」与「判分者噪声」分开的设计。

不改图、不联网、不调 LLM、无 rmtree/unlink。
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT / "data" / "knowledge" / "_audit"
A_DIR = AUDIT / "l4_multiscene_p1base"
B_DIR = AUDIT / "l4_multiscene_r8"
PRE_DIR = AUDIT / "l4_multiscene"
PREV_R8 = ROOT / "data" / "compendium_rag" / "backups" / "graph.json.prev.r8"
CUR = ROOT / "data" / "compendium_rag" / "graph.json"
REPORTS = ROOT / "data" / "compendium_rag" / "reports"
GATE = 4.0
EXPECT_SHA_A = "7cac5867e8c80879"
EXPECT_SHA_B = "56507b18ac2113b6"


def sha16(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()[:16]


def load_reviews(d: Path) -> dict[str, dict]:
    out: dict[str, dict] = {}
    for p in sorted(d.glob("ms_b*_review.json")):
        raw = json.loads(p.read_text(encoding="utf-8"))
        for it in raw["items"]:
            out[it["chunk_id"]] = {
                "coherence": int(it["coherence"]),
                "n_mismatch": int(it["n_mismatch"]),
                "n_edges": int(it["n_edges"]),
                "batch": raw.get("batch"),
                "review": str(p.name),
            }
    return out


def load_input_edges(d: Path) -> dict[str, list[tuple]]:
    """chunk_id -> [(src, relation, canonical, dst), ...]（按输入顺序）"""
    out: dict[str, list[tuple]] = {}
    for p in sorted(d.glob("ms_b*.json")):
        if p.name.endswith("_review.json"):
            continue
        raw = json.loads(p.read_text(encoding="utf-8"))
        for it in raw["items"]:
            out[it["chunk_id"]] = [
                (e["src"], e["relation"], e.get("canonical"), e["dst"]) for e in it["edges"]
            ]
    return out


def graph_edge_keys(path: Path) -> dict[str, list[tuple]]:
    """chunk_id(first) -> [(src, relation, dst)] using the same 'first chunk only' rule."""
    g = json.loads(path.read_text(encoding="utf-8"))
    out: dict[str, list[tuple]] = {}
    for e in g["edges"]:
        cids = e.get("chunk_ids") or []
        if not cids:
            continue
        out.setdefault(cids[0], []).append((e["src"], e["relation"], e["dst"]))
    return out


def mean(vals: list[int]) -> float:
    return round(sum(vals) / len(vals), 4) if vals else 0.0


def dist(vals: list[int]) -> dict[str, int]:
    out: dict[str, int] = {}
    for v in sorted(set(vals)):
        out[str(v)] = vals.count(v)
    return out


def main() -> int:
    for label, p, want in (("A(V9P1)", PREV_R8, EXPECT_SHA_A), ("B(R8)", CUR, EXPECT_SHA_B)):
        if not p.exists():
            print(f"[FATAL] 缺图 {p}")
            return 2
        got = sha16(p)
        if got != want:
            print(f"[FATAL] 图谱 SHA 漂移 {label}: {got} != {want}")
            return 2
        print(f"[ok] {label} {p.name} sha16={got}")

    a = load_reviews(A_DIR)
    b = load_reviews(B_DIR)
    if not a or not b:
        print("[FATAL] 两臂 review 未齐")
        return 2
    common = sorted(set(a) & set(b))
    only_a = sorted(set(a) - set(b))
    only_b = sorted(set(b) - set(a))

    in_a = load_input_edges(A_DIR)
    in_b = load_input_edges(B_DIR)
    ga = graph_edge_keys(PREV_R8)
    gb = graph_edge_keys(CUR)

    # 分块：18 块提案触及 / 44 块对照（比较两臂输入的边集合）
    changed: list[str] = []
    control: list[str] = []
    for cid in common:
        ea = sorted(t for t in in_a.get(cid, []))
        eb = sorted(t for t in in_b.get(cid, []))
        (changed if ea != eb else control).append(cid)

    def arm_stats(cids: list[str]) -> dict:
        va = [a[c]["coherence"] for c in cids]
        vb = [b[c]["coherence"] for c in cids]
        deltas = [b[c]["coherence"] - a[c]["coherence"] for c in cids]
        return {
            "n": len(cids),
            "mean_a": mean(va),
            "mean_b": mean(vb),
            "delta": round(mean(vb) - mean(va), 4),
            "up": sum(1 for d in deltas if d > 0),
            "down": sum(1 for d in deltas if d < 0),
            "flat": sum(1 for d in deltas if d == 0),
            "dist_a": dist(va),
            "dist_b": dist(vb),
            "le2_a": sum(1 for v in va if v <= 2),
            "le2_b": sum(1 for v in vb if v <= 2),
        }

    all_stats = arm_stats(common)
    ctrl_stats = arm_stats(control)
    chg_stats = arm_stats(changed)

    per_chunk = []
    for cid in common:
        per_chunk.append(
            {
                "chunk_id": cid,
                "a": a[cid]["coherence"],
                "b": b[cid]["coherence"],
                "delta": b[cid]["coherence"] - a[cid]["coherence"],
                "n_mismatch_a": a[cid]["n_mismatch"],
                "n_mismatch_b": b[cid]["n_mismatch"],
                "n_edges_a": a[cid]["n_edges"],
                "n_edges_b": b[cid]["n_edges"],
                "changed": cid in changed,
                "batch": a[cid]["batch"],
            }
        )
    per_chunk.sort(key=lambda r: (-abs(r["delta"]), r["chunk_id"]))

    # 与控制组一致性：两臂对同一批边给出相同分 = 判分者噪声下限
    ctrl_equal = sum(1 for c in control if a[c]["coherence"] == b[c]["coherence"])
    ctrl_off1 = sum(1 for c in control if abs(a[c]["coherence"] - b[c]["coherence"]) == 1)

    out = {
        "schema": "audit.p6_l45_ab/v1",
        "gate": GATE,
        "purpose": "L4.5 干净 A/B：同 62 块、同切分，A=V9P1 图 / B=R8 图，隔离'修边效果'与'判分者噪声'",
        "arm_a": {
            "label": "V9P1",
            "graph": str(PREV_R8.relative_to(ROOT)).replace("\\", "/"),
            "sha16": EXPECT_SHA_A,
            "dir": str(A_DIR.relative_to(ROOT)).replace("\\", "/"),
        },
        "arm_b": {
            "label": "R8",
            "graph": str(CUR.relative_to(ROOT)).replace("\\", "/"),
            "sha16": EXPECT_SHA_B,
            "dir": str(B_DIR.relative_to(ROOT)).replace("\\", "/"),
        },
        "chunk_sets": {
            "common": len(common),
            "only_a": only_a,
            "only_b": only_b,
            "changed_blocks": len(changed),
            "control_blocks": len(control),
        },
        "all": all_stats,
        "control": ctrl_stats,
        "changed": chg_stats,
        "control_consistency": {
            "identical_scores": ctrl_equal,
            "diff_by_1": ctrl_off1,
            "note": "控制组 44 块两臂输入边完全一致，其差异纯为判分噪声",
        },
        "per_chunk": per_chunk,
        "le2_list_b": sorted([cid for cid in common if b[cid]["coherence"] <= 2]),
        "le2_list_a": sorted([cid for cid in common if a[cid]["coherence"] <= 2]),
    }

    REPORTS.mkdir(parents=True, exist_ok=True)
    (REPORTS / "p6_l45_ab.json").write_text(
        json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    md = []
    md.append("# P6 · L4.5 干净 A/B（V9P1 基线臂 vs R8 臂）\n")
    md.append(f"- A = `{out['arm_a']['graph']}` sha16 `{EXPECT_SHA_A}`（V9P1）")
    md.append(f"- B = `{out['arm_b']['graph']}` sha16 `{EXPECT_SHA_B}`（R8，28 条修边落盘后）")
    md.append(f"- 共同块 {len(common)}；提案触及 {len(changed)}；对照组（边集合相同）{len(control)}\n")
    md.append("## 总读数\n")
    md.append("| 组 | n | A 均值 | B 均值 | Δ | 涨 | 跌 | 平 | A ≤2 | B ≤2 |")
    md.append("|---|---|---|---|---|---|---|---|---|---|")
    for name, s in (("全体", all_stats), ("对照组(44)", ctrl_stats), ("触及组(18)", chg_stats)):
        md.append(
            f"| {name} | {s['n']} | {s['mean_a']} | {s['mean_b']} | {s['delta']:+} | "
            f"{s['up']} | {s['down']} | {s['flat']} | {s['le2_a']} | {s['le2_b']} |"
        )
    md.append("")
    md.append(f"- 对照组两臂同分 {ctrl_equal}/{len(control)}，差 1 分 {ctrl_off1}/{len(control)} → 判分噪声下限")
    md.append(f"- gate ≥{GATE}：A {all_stats['mean_a']} / B {all_stats['mean_b']} → "
              f"{'PASS' if all_stats['mean_b'] >= GATE else 'FAIL'}")
    md.append(f"- 打分分布 A={all_stats['dist_a']} B={all_stats['dist_b']}\n")
    md.append("## B 臂仍 ≤2 的块\n")
    for cid in out["le2_list_b"]:
        md.append(f"- `{cid}` A={a[cid]['coherence']} B={b[cid]['coherence']}")
    md.append("")
    md.append("## 逐块明细（按 |Δ| 降序）\n")
    md.append("| chunk_id | 触及 | A | B | Δ | nm_A | nm_B |")
    md.append("|---|---|---|---|---|---|---|")
    for r in per_chunk:
        md.append(
            f"| `{r['chunk_id']}` | {'Y' if r['changed'] else ''} | {r['a']} | {r['b']} | "
            f"{r['delta']:+} | {r['n_mismatch_a']} | {r['n_mismatch_b']} |"
        )
    (REPORTS / "p6_l45_ab.md").write_text("\n".join(md) + "\n", encoding="utf-8")

    print(f"common={len(common)} changed={len(changed)} control={len(control)}")
    print(f"ALL    A={all_stats['mean_a']} B={all_stats['mean_b']} d={all_stats['delta']:+} "
          f"up={all_stats['up']} down={all_stats['down']} flat={all_stats['flat']} "
          f"le2 {all_stats['le2_a']}->{all_stats['le2_b']}")
    print(f"CTRL   A={ctrl_stats['mean_a']} B={ctrl_stats['mean_b']} d={ctrl_stats['delta']:+} "
          f"identical={ctrl_equal}/{len(control)}")
    print(f"CHANGED A={chg_stats['mean_a']} B={chg_stats['mean_b']} d={chg_stats['delta']:+}")
    print(f"dist A={all_stats['dist_a']} B={all_stats['dist_b']}")
    print(f"-> {REPORTS / 'p6_l45_ab.json'}")
    print("[done]")
    return 0


if __name__ == "__main__":
    sys.exit(main())
