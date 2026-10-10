# -*- coding: utf-8 -*-
"""P6 · L4.5 多臂 A/B —— 通用合成器（任意两臂互比）。

与 `compendium_rag_p6_l45_ab2_synth.py` 的区别：臂目录由参数给定，可对比
p1base / r8 / r8b / r9 任意两臂；图 SHA 硬门按 `--sha-a/--sha-b` 校验。

对照分析的核心：把两臂**输入边逐条相同**的块划为 control（判分噪声下限），
输入边不同的块划为 changed（修边的真实效果）。没有这个划分，就无法区分
「修边起作用」与「两轮判分者尺度不同」。

用法::

    PYTHONPATH=src .venv/Scripts/python.exe -X utf8 \
      scripts/compendium_rag_p6_l45_ab_multi.py \
      --a-dir data/knowledge/_audit/l4_multiscene_p1base  --sha-a 7cac5867e8c80879 \
      --b-dir data/knowledge/_audit/l4_multiscene_r9      --sha-b <r9sha16> \
      --graph-a data/compendium_rag/backups/graph.json.prev.r8 \
      --graph-b data/compendium_rag/graph.json \
      --out p6_l45_ab_r9

只读；写 `data/compendium_rag/reports/<out>.json` 与 `.md`。
不改图、不联网、不调 LLM、无 rmtree/unlink。
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPORTS = ROOT / "data" / "compendium_rag" / "reports"
GATE = 4.0


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
    ap = argparse.ArgumentParser()
    ap.add_argument("--a-dir", required=True)
    ap.add_argument("--b-dir", required=True)
    ap.add_argument("--graph-a", required=True)
    ap.add_argument("--graph-b", required=True)
    ap.add_argument("--sha-a", required=True)
    ap.add_argument("--sha-b", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--expect-n", type=int, default=62)
    a = ap.parse_args()

    A_DIR = ROOT / a.a_dir
    B_DIR = ROOT / a.b_dir
    for label, p, want in (("A", ROOT / a.graph_a, a.sha_a),
                           ("B", ROOT / a.graph_b, a.sha_b)):
        if not p.exists():
            print(f"[FATAL] 缺图 {label}: {p}")
            return 2
        got = sha16(p)
        if got.lower() != want.lower():
            print(f"[FATAL] 图谱 SHA 漂移 {label}: {got} != {want}")
            return 2
        print(f"[ok] {label} {p.name} sha16={got}")

    ra = load_reviews(A_DIR)
    rb = load_reviews(B_DIR)
    for name, arm in ((f"A({A_DIR.name})", ra), (f"B({B_DIR.name})", rb)):
        if len(arm) != a.expect_n:
            print(f"[FATAL] {name} 只有 {len(arm)} 块，期望 {a.expect_n}")
            return 2

    common = sorted(set(ra) & set(rb))
    only_a = sorted(set(ra) - set(rb))
    only_b = sorted(set(rb) - set(ra))
    print(f"common={len(common)} only_a={len(only_a)} only_b={len(only_b)}")

    in_a = load_input_edges(A_DIR)
    in_b = load_input_edges(B_DIR)

    changed = [c for c in common if in_a.get(c) != in_b.get(c)]
    control = [c for c in common if in_a.get(c) == in_b.get(c)]
    print(f"changed={len(changed)} control={len(control)}")

    all_s = stats(ra, rb, common)
    ctrl_s = stats(ra, rb, control)
    chg_s = stats(ra, rb, changed)

    per_chunk = sorted(
        (
            {
                "chunk_id": c,
                "a": ra[c]["coherence"],
                "b": rb[c]["coherence"],
                "delta": rb[c]["coherence"] - ra[c]["coherence"],
                "nm_a": ra[c]["n_mismatch"],
                "nm_b": rb[c]["n_mismatch"],
                "n_edges_a": ra[c]["n_edges"],
                "n_edges_b": rb[c]["n_edges"],
                "changed": c in changed,
                "batch": ra[c]["batch"],
            }
            for c in common
        ),
        key=lambda r: (-abs(r["delta"]), r["chunk_id"]),
    )

    out = {
        "schema": "audit.p6_l45_ab_multi/v1",
        "gate": GATE,
        "design": {
            "arm_a": {"dir": a.a_dir, "graph": a.graph_a, "sha16": a.sha_a},
            "arm_b": {"dir": a.b_dir, "graph": a.graph_b, "sha16": a.sha_b},
            "note": "control = 两臂输入边逐条相同的块（判分噪声下限）；"
                    "changed = 输入边不同的块（修边真实效果）",
        },
        "chunk_sets": {
            "common": len(common), "only_a": only_a, "only_b": only_b,
            "changed_blocks": len(changed), "control_blocks": len(control),
        },
        "all": all_s, "control": ctrl_s, "changed": chg_s,
        "per_chunk": per_chunk,
        "le2_list_b": sorted([c for c in common if rb[c]["coherence"] <= 2]),
        "le2_list_a": sorted([c for c in common if ra[c]["coherence"] <= 2]),
    }

    REPORTS.mkdir(parents=True, exist_ok=True)
    (REPORTS / f"{a.out}.json").write_text(
        json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")

    md = [
        f"# P6 · L4.5 A/B（{A_DIR.name} vs {B_DIR.name}）\n",
        f"- A = `{a.graph_a}` sha16 `{a.sha_a}`",
        f"- B = `{a.graph_b}` sha16 `{a.sha_b}`",
        f"- 共同块 {len(common)}；输入边改变 {len(changed)}；对照组 {len(control)}\n",
        "## 总读数\n",
        "| 组 | n | A 均值 | B 均值 | Δ | 涨 | 跌 | 平 | A≤2 | B≤2 |",
        "|---|---|---|---|---|---|---|---|---|---|",
    ]
    for name, s in (("全体", all_s), ("对照组", ctrl_s), ("改变组", chg_s)):
        md.append(
            f"| {name} | {s['n']} | {s['mean_a']} | {s['mean_b']} | {s['delta']:+} | "
            f"{s['up']} | {s['down']} | {s['flat']} | {s['le2_a']} | {s['le2_b']} |"
        )
    md.append("")
    md.append(f"- **gate ≥{GATE}**：A `{all_s['mean_a']}` / B `{all_s['mean_b']}` → "
              f"**{'PASS' if all_s['mean_b'] >= GATE else 'FAIL'}**")
    md.append(f"- 分布 A={all_s['dist_a']} B={all_s['dist_b']}")
    md.append(f"- 对照组（边逐条相同）同分 {ctrl_s['identical']}/{ctrl_s['n']}、"
              f"差 1 分 {ctrl_s['diff_by_1']}、差 ≥2 {ctrl_s['diff_by_ge2']} → 判分噪声下限")
    md.append(f"- 改变组 A={chg_s['mean_a']} → B={chg_s['mean_b']}（Δ{chg_s['delta']:+}）")
    md.append("")
    md.append("## B 臂仍 ≤2 的块\n")
    for c in out["le2_list_b"]:
        md.append(f"- `{c}` A={ra[c]['coherence']} B={rb[c]['coherence']} "
                  f"(nm {ra[c]['n_mismatch']}→{rb[c]['n_mismatch']})")
    md.append("")
    md.append("## 逐块明细（按 |Δ| 降序）\n")
    md.append("| chunk_id | 改变 | A | B | Δ | nm_A | nm_B | 边数 A→B |")
    md.append("|---|---|---|---|---|---|---|---|")
    for r in per_chunk:
        md.append(
            f"| `{r['chunk_id']}` | {'Y' if r['changed'] else ''} | {r['a']} | {r['b']} | "
            f"{r['delta']:+} | {r['nm_a']} | {r['nm_b']} | {r['n_edges_a']}→{r['n_edges_b']} |"
        )
    (REPORTS / f"{a.out}.md").write_text("\n".join(md) + "\n", encoding="utf-8")

    print(f"ALL     A={all_s['mean_a']} B={all_s['mean_b']} d={all_s['delta']:+} "
          f"up={all_s['up']} down={all_s['down']} flat={all_s['flat']} "
          f"le2 {all_s['le2_a']}->{all_s['le2_b']}")
    print(f"CTRL    A={ctrl_s['mean_a']} B={ctrl_s['mean_b']} d={ctrl_s['delta']:+} "
          f"identical={ctrl_s['identical']}/{ctrl_s['n']}")
    print(f"CHANGED A={chg_s['mean_a']} B={chg_s['mean_b']} d={chg_s['delta']:+}")
    print(f"gate >= {GATE}: {'PASS' if all_s['mean_b'] >= GATE else 'FAIL'}")
    print(f"-> {REPORTS / (a.out + '.json')}")
    print("[done]")
    return 0


if __name__ == "__main__":
    sys.exit(main())
