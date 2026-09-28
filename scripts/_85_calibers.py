# -*- coding: utf-8 -*-
"""澄清「召回率 85%」到底指哪个口径 —— 把所有口径列全，标 PASS/FAIL。"""
from __future__ import annotations

import json
from pathlib import Path

R = Path("data/compendium_rag/reports")


def hits(f: str, mode: str = "full", ans: bool | None = True) -> tuple[int, int]:
    d = json.loads((R / f).read_text(encoding="utf-8"))
    rows = [r for r in d["rows"] if r.get("mode") == mode]
    if ans is not None:
        rows = [r for r in rows if bool(r.get("answerable")) == ans]
    return sum(1 for r in rows if r.get("hit")), len(rows)


def line(label: str, h: int, n: int) -> str:
    import math
    r = h / n
    need = max(0, math.ceil(0.85 * n) - h)
    return (f"  {label:38} {h:>4}/{n:<4} = {r:.4f}   "
            f"{'PASS ✓' if r >= 0.85 else f'FAIL ✗ (需 +{need} 题)'}")


print("=" * 92)
print("全部口径一览 —— 「召回率 ≥85%」的目标究竟差哪些")
print("=" * 92)
print()
print("[裸检索 hit@6]（无重排，官方 eval 路径）")
for lbl, f, ans in [
    ("盲测206  lex=0 (v5)", "eval_blind_lex_off.json", None),
    ("盲测206  lex=1 (v6)", "eval_blind_lex_tiebreak.json", None),
    ("盲测206  lex_first=3", "eval_blind_lexfirst.json", None),
    ("300cn    lex=0 (v5)", "eval_300cn_v6_tb_lexoff.json", True),
    ("300cn    lex=1 (v6)", "eval_300cn_lex_tiebreak.json", True),
    ("300cn    lex_first=3", "eval_300cn_lexfirst.json", True),
    ("泛化120  lex=1 (v6)", "eval_gen_lex_on.json", True),
]:
    h, n = hits(f, "full", ans)
    print(line(lbl, h, n))

print()
print("[安全线]（不得恶化）")
for lbl, f in [("300cn unanswerable 命中", "eval_300cn_lex_tiebreak.json")]:
    h, n = hits(f, "full", False)
    print(f"  {lbl:38} {h}/{n}")

print()
print("[生产口径 = 检索 + 冻结重排]（来自基线工件，非 eval）")
for lbl, v in [("盲测206 生产口径 (v6)", 0.8786),
               ("300cn  生产口径 (v6)", 0.8673),
               ("盲测206 生产口径 (v5)", None)]:
    if v is None:
        continue
    print(f"  {lbl:38} {v:.4f}   {'PASS ✓' if v >= 0.85 else 'FAIL ✗'}")

print()
print("[池上限]（重排的理论天花板）")
print(f"  {'300cn hit@30 (v6 pool)':38} 0.9286   <- 182/196，重排最多能到的上界")

print()
print("=" * 92)
print("结论")
print("=" * 92)
print("  唯一 **低于 0.85** 的主口径 = 300cn 裸检索 hit@6 = 165/196 = 0.8418（差 2 题）")
print("  盲测裸检索 lex_first=3 已 0.9223；盲测生产口径 0.8786；300cn 生产口径 0.8673")
print("  => 若要「所有口径都 ≥0.85」，只需把 300cn 裸检索 +2 题，且不得让盲测回退。")
