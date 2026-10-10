"""P6 · L4.5 最终 A/B 合成（口径对齐版）。

A 臂 = V9P1 基线（`backups/graph.json.prev.r8`，sha16 7cac5867e8c80879）
B 臂 = R8（`data/compendium_rag/graph.json`，sha16 56507b18ac2113b6）

与首版合成器 `compendium_rag_p6_l45_ab_synth.py` 的区别：B 臂读 `l4_multiscene_r8b/`，
即「与 A 臂收到逐字节相同 rubric 任务书」的那一轮复评 —— 消除首轮 R8 盲评（未收到
显式三分类口径）与 A 臂之间的判分尺度混淆。首轮 R8 数字作为附注一并报出。

只读；写 `data/compendium_rag/reports/p6_l45_ab_final.json` 与 `.md`。
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
B_DIR = AUDIT / "l4_multiscene_r8b"
B_FIRST_DIR = AUDIT / "l4_multiscene_r8"
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
            }
    return out


def load_input_edges(d: Path) -> dict[str, list[tuple]]:
    out: dict[str, list[tuple]] = {}
    for p in sorted(d.glob("ms_b*.json")):
        if p.name.endswith("_review.json"):
            continue
        raw = json.loads(p.read_text(encoding="utf-8"))
        for it in raw["items"]:
            out[it["chunk_id"]] = sorted(
                (e["src"], e["relation"], e.get("canonical"), e["dst"]) for e in it["edges"]
            )
    return out


def mean(vals: list[int]) -> float:
    return round(sum(vals) / len(vals), 4) if vals else 0.0


def dist(vals: list[int]) -> dict[str, int]:
    return {str(v): vals.count(v) for v in sorted(set(vals))}


def stats(a: dict, b: dict, cids: list[str]) -> dict:
    va = [a[c]["coherence"] for c in cids]
    vb = [b[c]["coherence"] for c in cids]
    d = [b[c]["coherence"] - a[c]["coherence"] for c in cids]
    return {
        "n": len(cids),
        "mean_a": mean(va),
        "mean_b": mean(vb),
        "delta": round(mean(vb) - mean(va), 4),
        "up": sum(1 for x in d if x > 0),
        "down": sum(1 for x in d if x < 0),
        "flat": sum(1 for x in d if x == 0),
        "identical": sum(1 for x in d if x == 0),
        "diff_by_1": sum(1 for x in d if abs(x) == 1),
        "diff_by_ge2": sum(1 for x in d if abs(x) >= 2),
        "dist_a": dist(va),
        "dist_b": dist(vb),
        "le2_a": sum(1 for v in va if v <= 2),
        "le2_b": sum(1 for v in vb if v <= 2),
    }


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
    b_first = load_reviews(B_FIRST_DIR) if B_FIRST_DIR.exists() else {}
    for name, arm in (("A(p1base)", a), ("B(r8b)", b)):
        if len(arm) != 62:
            print(f"[FATAL] {name} 只有 {len(arm)} 块，期望 62")
            return 2

    common = sorted(set(a) & set(b))
    only_a = sorted(set(a) - set(b))
    only_b = sorted(set(b) - set(a))
    print(f"common={len(common)} only_a={len(only_a)} only_b={len(only_b)}")

    in_a = load_input_edges(A_DIR)
    in_b = load_input_edges(B_DIR)
    # 输入批次本身必须与 A 臂同集合
    assert set(in_a) == set(in_b), "两臂输入块集合不一致"

    changed = [c for c in common if in_a.get(c) != in_b.get(c)]
    control = [c for c in common if in_a.get(c) == in_b.get(c)]
    print(f"changed={len(changed)} control={len(control)}")

    # 交叉核对：r8b 输入应与首轮 r8 输入逐字节相同（同一批边）
    in_b_first = load_input_edges(B_FIRST_DIR) if B_FIRST_DIR.exists() else {}
    input_same_as_first = set(in_b_first) == set(in_b) and all(
        in_b_first.get(c) == in_b.get(c) for c in in_b
    )

    all_s = stats(a, b, common)
    ctrl_s = stats(a, b, control)
    chg_s = stats(a, b, changed)
    all_first = stats(a, b_first, common) if b_first else None
    ctrl_first = stats(a, b_first, control) if b_first else None

    per_chunk = sorted(
        (
            {
                "chunk_id": c,
                "a": a[c]["coherence"],
                "b": b[c]["coherence"],
                "delta": b[c]["coherence"] - a[c]["coherence"],
                "nm_a": a[c]["n_mismatch"],
                "nm_b": b[c]["n_mismatch"],
                "n_edges_a": a[c]["n_edges"],
                "n_edges_b": b[c]["n_edges"],
                "changed": c in changed,
                "batch": a[c]["batch"],
            }
            for c in common
        ),
        key=lambda r: (-abs(r["delta"]), r["chunk_id"]),
    )

    out = {
        "schema": "audit.p6_l45_ab_final/v1",
        "gate": GATE,
        "design": {
            "arm_a": {"label": "V9P1", "graph": "data/compendium_rag/backups/graph.json.prev.r8",
                      "sha16": EXPECT_SHA_A, "dir": "data/knowledge/_audit/l4_multiscene_p1base"},
            "arm_b": {"label": "R8", "graph": "data/compendium_rag/graph.json",
                      "sha16": EXPECT_SHA_B, "dir": "data/knowledge/_audit/l4_multiscene_r8b"},
            "rubric_aligned": True,
            "note": "两臂任务书逐字节同 rubric（三分类 mismatch 口径）；B 为 R8 图复评轮",
        },
        "chunk_sets": {
            "common": len(common), "only_a": only_a, "only_b": only_b,
            "changed_blocks": len(changed), "control_blocks": len(control),
            "r8b_inputs_identical_to_first_r8_round": input_same_as_first,
        },
        "all": all_s,
        "control": ctrl_s,
        "changed": chg_s,
        "first_round_b_not_rubric_aligned": {
            "all": all_first, "control": ctrl_first,
            "note": "首轮 R8 盲评（l4_multiscene_r8/）任务书未含显式三分类口径，与 A 臂不可比；仅作附注",
        },
        "per_chunk": per_chunk,
        "le2_list_b": sorted([c for c in common if b[c]["coherence"] <= 2]),
        "le2_list_a": sorted([c for c in common if a[c]["coherence"] <= 2]),
    }

    REPORTS.mkdir(parents=True, exist_ok=True)
    (REPORTS / "p6_l45_ab_final.json").write_text(
        json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    md = [
        "# P6 · L4.5 最终 A/B（口径对齐：V9P1 基线臂 vs R8 臂）\n",
        f"- A = `backups/graph.json.prev.r8` sha16 `{EXPECT_SHA_A}`（V9P1）",
        f"- B = `graph.json` sha16 `{EXPECT_SHA_B}`（R8，28 条修边后）",
        f"- 两臂任务书 rubric 逐字节相同；共同块 {len(common)}，"
        f"提案触及 {len(changed)}，对照组 {len(control)}",
        f"- r8b 输入与首轮 r8 输入一致：{input_same_as_first}\n",
        "## 总读数\n",
        "| 组 | n | A 均值 | B 均值 | Δ | 涨 | 跌 | 平 | A≤2 | B≤2 |",
        "|---|---|---|---|---|---|---|---|---|---|",
    ]
    for name, s in (("全体", all_s), ("对照组", ctrl_s), ("触及组", chg_s)):
        md.append(
            f"| {name} | {s['n']} | {s['mean_a']} | {s['mean_b']} | {s['delta']:+} | "
            f"{s['up']} | {s['down']} | {s['flat']} | {s['le2_a']} | {s['le2_b']} |"
        )
    md.append("")
    md.append(f"- **gate ≥{GATE}**：A `{all_s['mean_a']}` / B `{all_s['mean_b']}` → "
              f"**{'PASS' if all_s['mean_b'] >= GATE else 'FAIL'}**")
    md.append(f"- 分布 A={all_s['dist_a']} B={all_s['dist_b']}")
    md.append(f"- 对照组（边完全相同）同分 {ctrl_s['identical']}/{ctrl_s['n']}、"
              f"差 1 分 {ctrl_s['diff_by_1']}、差 ≥2 {ctrl_s['diff_by_ge2']} → 判分噪声下限")
    md.append(f"- 触及组 A={chg_s['mean_a']} → B={chg_s['mean_b']}（Δ{chg_s['delta']:+}）")
    if all_first:
        md.append(f"- 附注·首轮 R8（rubric 未对齐）全体 {all_first['mean_a']} → "
                  f"{all_first['mean_b']}，对照组 {ctrl_first['mean_a']} → {ctrl_first['mean_b']}"
                  f"（对照组掉 {ctrl_first['delta']:+} 说明该轮尺度更严，不可与 A 臂直接比较）")
    md.append("")
    md.append("## B 臂仍 ≤2 的块\n")
    for c in out["le2_list_b"]:
        md.append(f"- `{c}` A={a[c]['coherence']} B={b[c]['coherence']} "
                  f"(nm {a[c]['n_mismatch']}→{b[c]['n_mismatch']})")
    md.append("")
    md.append("## 逐块明细（按 |Δ| 降序）\n")
    md.append("| chunk_id | 触及 | A | B | Δ | nm_A | nm_B | 边数 A→B |")
    md.append("|---|---|---|---|---|---|---|---|")
    for r in per_chunk:
        md.append(
            f"| `{r['chunk_id']}` | {'Y' if r['changed'] else ''} | {r['a']} | {r['b']} | "
            f"{r['delta']:+} | {r['nm_a']} | {r['nm_b']} | {r['n_edges_a']}→{r['n_edges_b']} |"
        )
    (REPORTS / "p6_l45_ab_final.md").write_text("\n".join(md) + "\n", encoding="utf-8")

    print(f"ALL     A={all_s['mean_a']} B={all_s['mean_b']} d={all_s['delta']:+} "
          f"up={all_s['up']} down={all_s['down']} flat={all_s['flat']} "
          f"le2 {all_s['le2_a']}->{all_s['le2_b']}")
    print(f"CTRL    A={ctrl_s['mean_a']} B={ctrl_s['mean_b']} d={ctrl_s['delta']:+} "
          f"identical={ctrl_s['identical']}/{ctrl_s['n']}")
    print(f"CHANGED A={chg_s['mean_a']} B={chg_s['mean_b']} d={chg_s['delta']:+}")
    print(f"dist A={all_s['dist_a']} B={all_s['dist_b']}")
    print(f"gate >= {GATE}: {'PASS' if all_s['mean_b'] >= GATE else 'FAIL'}")
    print(f"-> {REPORTS / 'p6_l45_ab_final.json'}")
    print("[done]")
    return 0


if __name__ == "__main__":
    sys.exit(main())
