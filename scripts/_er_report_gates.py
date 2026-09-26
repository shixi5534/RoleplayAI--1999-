# -*- coding: utf-8 -*-
"""ER 阶段 3 闸门报告：零档逐位自检 + 映射档全量口径/安全底线/逐题归因/McNemar。

只读离线产物，不触网关、不跑检索。
  --set 300_cn --zero reports/replay_300cn_zero.json --map reports/replay_300cn_map.json
任一档缺文件则跳过并在输出里标 pending（陈旧产物不会印出 pass：按 (set,map,行数) 现场校验）。
"""
from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REP = ROOT / "data" / "compendium_rag" / "reports"
CMP_FIELDS = ("hit", "rr", "seed_hit", "grounded", "n_evidence", "n_edges")
BASE = {
    "native": REP / "eval_native_after_welds.json",
    "300_cn": REP / "eval_300_cn_after_welds.json",
}


def load_rows(p: Path):
    return json.loads(p.read_text(encoding="utf-8"))["rows"]


def groups(rows, mode):
    sub = [r for r in rows if r["mode"] == mode]
    out = {}
    for name, ss in (("all", sub),
                     ("answerable", [r for r in sub if r.get("answerable")]),
                     ("unanswerable", [r for r in sub if not r.get("answerable")])):
        n = len(ss)
        out[name] = {
            "n": n,
            "hit": round(sum(1 for r in ss if r["hit"]) / n, 4) if n else None,
            "mrr": round(sum(r["rr"] for r in ss) / n, 4) if n else None,
            "grounded_all": bool(ss) and all(r["grounded"] for r in ss),
            "grounded_rate": round(sum(1 for r in ss if r["grounded"]) / n, 4) if n else None,
        }
    return out


def mcnemar_exact(b: int, c: int) -> float:
    n = b + c
    if n == 0:
        return 1.0
    k = min(b, c)
    tail = sum(math.comb(n, i) for i in range(k + 1)) / (2 ** n)
    return min(1.0, 2 * tail)


def zero_verdict(set_name: str, zero_path: Path, out: list) -> None:
    if not zero_path.exists():
        out.append(f"- 零档自检：**pending**（{zero_path.name} 尚未生成）")
        return
    new = load_rows(zero_path)
    base = load_rows(BASE[set_name])
    if json.loads(zero_path.read_text(encoding="utf-8")).get("map") != "none":
        out.append("- 零档自检：**FAIL**（该产物 map 档不是 none，输入不合法）")
        return
    bkey = {(r["qid"], r["mode"]): r for r in base}
    diffs = []
    for r in new:
        b = bkey.get((r["qid"], r["mode"]))
        if b is None:
            diffs.append((r["qid"], r["mode"], "missing_in_baseline"))
            continue
        for f in CMP_FIELDS:
            if r[f] != b[f]:
                diffs.append((r["qid"], r["mode"], f, b[f], r[f]))
                break
    aligned = sum(1 for r in new if (r["qid"], r["mode"]) in bkey)
    verdict = "PASS 逐位复现" if not diffs and aligned == len(base) == len(new) else "FAIL 评测具不中立"
    out.append(f"- 零档自检：行数 {len(new)} / 基线 {len(base)} / 对齐 {aligned} → **{verdict}**，差异 {len(diffs)} 行")
    for d in diffs[:20]:
        out.append(f"  - DIFF {d}")


def map_verdict(set_name: str, map_path: Path, out: list) -> None:
    if not map_path.exists():
        out.append(f"- 映射档：**pending**（{map_path.name} 尚未生成）")
        return
    obj = json.loads(map_path.read_text(encoding="utf-8"))
    expect = f"entity_map_{set_name}.json"
    used = str(obj.get("map", ""))
    if Path(used).name != expect:
        out.append(f"- 映射档：**FAIL 产物不匹配**（回放用的映射是 `{used or '未知'}`，"
                   f"不是当前的 `{expect}`；须重跑回放）")
        return
    new, base = obj["rows"], load_rows(BASE[set_name])
    bkey = {(r["qid"], r["mode"]): r for r in base}
    nkey = {(r["qid"], r["mode"]): r for r in new}
    mp = json.loads((ROOT / "data" / "compendium_rag" / f"entity_map_{set_name}.json")
                    .read_text(encoding="utf-8"))["map"]
    affected = {q for q, v in mp.items() if v}
    for mode in ("full", "graph_only"):
        g_new, g_old = groups(new, mode), groups(base, mode)
        out.append(f"### {mode}")
        for grp in ("all", "answerable", "unanswerable"):
            a, b = g_old[grp], g_new[grp]
            dh = None if a["hit"] is None or b["hit"] is None else round(
                (b["hit"] - a["hit"]) * 100, 2)
            dh_s = "n/a" if dh is None else f"{dh:+.2f}pt"
            tag = ""
            if grp == "unanswerable":
                tag = "  [安全底线：" + ("不升 PASS" if (b["hit"] or 0) <= (a["hit"] or 0) else "上升 FAIL") + "]"
            if grp == "answerable":
                tag = "  [主口径：" + ("提升 PASS" if (dh or 0) > 0 else "未提升 FAIL") + "]"
            out.append(
                f"- {grp} n={b['n']}  hit@6 {a['hit']} → {b['hit']}"
                f"（{dh_s}）  MRR {a['mrr']} → {b['mrr']}"
                f"  grounded {b['grounded_rate']}{tag}"
            )
        miss = [r["qid"] for r in new if (r["qid"], r["mode"]) not in bkey]
        if miss:
            out.append(f"- **缺基线行**（这些题无法配对）：{sorted(set(miss))}")
        pair = [(q, m, r, bkey[(q, m)]) for (q, m), r in nkey.items() if (q, m) in bkey]
        ups = sorted(q for q, m, r, b in pair if m == mode and r["hit"] and not b["hit"])
        downs = sorted(q for q, m, r, b in pair if m == mode and not r["hit"] and b["hit"])
        out.append(f"- 逐题翻转（{mode}）up={len(ups)} {ups}")
        out.append(f"- 逐题翻转（{mode}）down={len(downs)} {downs}")
        if mode == "full":
            aff_in = [q for q in ups if q in affected]
            aff_out = [q for q in downs if q in affected]
            unk_in = [q for q in ups if q not in affected]
            unk_out = [q for q in downs if q not in affected]
            out.append(f"- 归因检查：映射覆盖题 {len(affected)} 道；up 中被覆盖 {len(aff_in)}、未覆盖 {len(unk_in)}；"
                       f"down 中被覆盖 {len(aff_out)}、未覆盖 {len(unk_out)}")
            b_, c_ = len(ups), len(downs)
            out.append(f"- McNemar（full，hit@6 逐题配对）b={b_} c={c_} p={mcnemar_exact(b_, c_):.5f}")
            cb_in = [q for q in ups if q in affected]
            cb_out = [q for q in downs if q in affected]
            out.append(f"- McNemar（full，仅映射覆盖题）b={len(cb_in)} c={len(cb_out)} "
                       f"p={mcnemar_exact(len(cb_in), len(cb_out)):.5f}"
                       f"  ← 补名净效应的配对集（未覆盖题翻转不入场）")
            out.append("- 注：未覆盖题上的翻转=检索随机性/排序噪声，不计入补名效果")
    return


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--set", choices=["native", "300_cn"], required=True)
    ap.add_argument("--zero", default="")
    ap.add_argument("--map", default="")
    ap.add_argument("--out", default="")
    args = ap.parse_args()

    out = [f"# ER 阶段3 闸门 · set={args.set}", ""]
    slug = args.set.replace("_", "")
    zp = Path(args.zero) if args.zero else REP / f"replay_{slug}_zero.json"
    mp = Path(args.map) if args.map else REP / f"replay_{slug}_map.json"
    if not zp.is_absolute():
        zp = ROOT / zp
    if not mp.is_absolute():
        mp = ROOT / mp
    zero_verdict(args.set, zp, out)
    out.append("")
    map_verdict(args.set, mp, out)
    text = "\n".join(out) + "\n"
    print(text)
    if args.out:
        p = Path(args.out) if Path(args.out).is_absolute() else ROOT / args.out
        p.write_text(text, encoding="utf-8")
        print(f"[written] {p}")
    # 退出码：pending/FAIL 不得被当成通过
    if "pending" in text:
        return 2
    return 1 if "**FAIL" in text else 0


if __name__ == "__main__":
    sys.exit(main())
