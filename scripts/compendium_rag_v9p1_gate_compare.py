# -*- coding: utf-8 -*-
"""v9-P1 回归闸门对账（**只读**）：三主数逐位对比 v8，判 PASS/FAIL。

为什么要一个专门脚本，而不是拿日志里的四舍五入读数比：
- 闸门是硬门（谓语改写可能改边权与邻接），判错方向的代价是把整段 P1 回滚或把退化放行；
- 日志里的 hit@k 只到小数点后三位，0.893 与 0.8932 这种差异正好落在门槛上；
- 「不低于 v8」必须是**同口径同子集**的比较：300cn 用 answerable(196)，blind206/gen120 用 all，
  模式固定 full（与 v8 基线一致；graph_only 只作旁证）。

用法：
  PYTHONPATH=src .venv/Scripts/python.exe -X utf8 scripts/compendium_rag_v9p1_gate_compare.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
R = ROOT / "data/compendium_rag/reports"

# (名称, v8 产物, v9p1 产物, 模式, 子集, 预登记下限)
GATES = [
    ("300cn_bare_hit6", "eval_300cn_k1", "eval_300cn_k1_v9p1", "full", "answerable", 0.852),
    ("blind206_bare_hit6", "eval_blind_k1", "eval_blind_k1_v9p1", "full", "all", 0.8932),
    ("gen120_bare_hit6", "eval_gen120_k1", "eval_gen120_k1_v9p1", "full", "all", 0.9833),
]


def _subset(rows: list[dict], mode: str, sel: str) -> list[dict]:
    out = [r for r in rows if r.get("mode") == mode]
    if sel == "answerable":
        out = [r for r in out if r.get("answerable")]
    return out


def _rate(rows: list[dict], key: str) -> float:
    return sum(1 for r in rows if r.get(key)) / len(rows) if rows else float("nan")


def _mrr(rows: list[dict]) -> float:
    return sum(float(r.get("rr") or 0.0) for r in rows) / len(rows) if rows else float("nan")


def _paired(old: list[dict], new: list[dict]) -> tuple[int, int, list[str]]:
    ob = {r["qid"]: bool(r.get("hit")) for r in old}
    nb = {r["qid"]: bool(r.get("hit")) for r in new}
    shared = sorted(set(ob) & set(nb))
    up = [q for q in shared if not ob[q] and nb[q]]
    down = [q for q in shared if ob[q] and not nb[q]]
    return len(up), len(down), down


def main() -> int:
    verdicts = []
    failed = False
    for name, v8_tag, v9_tag, mode, sel, prereg in GATES:
        p8, p9 = R / f"{v8_tag}.json", R / f"{v9_tag}.json"
        if not p9.exists():
            print(f"[pending] {name}: 缺产物 {p9.name}")
            verdicts.append({"gate": name, "status": "pending"})
            failed = True          # 缺一个就不许宣布整道闸门过了
            continue
        d8 = json.loads(p8.read_text(encoding="utf-8"))
        d9 = json.loads(p9.read_text(encoding="utf-8"))
        r8 = _subset(d8["rows"], mode, sel)
        r9 = _subset(d9["rows"], mode, sel)
        h8, h9 = _rate(r8, "hit"), _rate(r9, "hit")
        up, down, down_qids = _paired(r8, r9)
        # 预登记下限必须与 v8 实算一致，否则说明两边口径不同（题集换了 / 子集定义漂了）
        calib_ok = abs(h8 - prereg) < 5e-4
        ok = calib_ok and h9 >= h8 - 1e-12
        verdicts.append({
            "gate": name, "mode": mode, "subset": sel,
            "n_v8": len(r8), "n_v9": len(r9),
            "hit6_v8": round(h8, 6), "hit6_v9": round(h9, 6),
            "prereg_floor": prereg, "caliber_matches_prereg": calib_ok,
            "mrr_v8": round(_mrr(r8), 6), "mrr_v9": round(_mrr(r9), 6),
            "paired_up": up, "paired_down": down, "down_qids": down_qids[:20],
            "corpus_v8": d8.get("corpus"), "corpus_v9": d9.get("corpus"),
            "status": "PASS" if ok else "FAIL",
        })
        print(f"[{'PASS' if ok else 'FAIL'}] {name}: "
              f"v8={h8:.6f} (n={len(r8)}) → v9={h9:.6f} (n={len(r9)}) "
              f"Δ={h9 - h8:+.6f} up={up} down={down}"
              + ("" if calib_ok else f"  ⚠ v8 实算与预登记下限 {prereg} 不符，口径不一致"))

    out = R / "p1_gate_compare.json"
    out.write_text(json.dumps({
        "schema": "compendium_rag.p1_gate_compare/v1",
        "mode": "read-only",
        "rule": "三主数（同口径同子集，mode=full）v9 不得低于 v8；缺任一产物不得宣布通过",
        "verdict": "PASS" if not failed and all(v["status"] == "PASS" for v in verdicts)
                   else ("PENDING" if any(v["status"] == "pending" for v in verdicts) else "FAIL"),
        "gates": verdicts,
    }, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"对账 → {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
