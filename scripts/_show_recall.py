# -*- coding: utf-8 -*-
"""把 diag_recall_cause.json 的结论打印到 stdout（绕过 PowerShell 重定向的编码坑）。"""
from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT / "data" / "knowledge" / "_audit"
p = AUDIT / "diag_recall_cause.json"
OUT = AUDIT / "_recall_summary.txt"
_buf: list[str] = []
print = lambda *a, **k: _buf.append(" ".join(str(x) for x in a))  # noqa: A001
if not p.is_file():
    print("[MISSING] 报告不存在，先跑 diag_recall_cause.py")
    OUT.write_text("\n".join(_buf), encoding="utf-8")
    sys.exit(1)

d = json.loads(p.read_text(encoding="utf-8"))
rows = d["rows"]
n = len(rows)
cnt = Counter(r["bucket"] for r in rows)

print("=" * 76)
print(f"题量 {n}｜生产 top={d['params']['top_prod']}｜深挖 top={d['params']['top_deep']}")
print(f"recall 生产口径   = {d['recall_prod']:.4f}")
print(f"recall 深挖 top30 = {d['recall_deep']:.4f}")
print("=" * 76)
lbl = {"A_no_ceiling": "A 语料无单块可答", "B_top5": "B 已进 top-5",
       "C_squeezed": "C 被挤到 6~30", "D_recall_fail": "D 真召回失败"}
print(f"{'桶':<18}{'题数':>6}{'占比':>9}{'recall贡献':>12}{'桶内均值':>10}")
for b in ("A_no_ceiling", "B_top5", "C_squeezed", "D_recall_fail"):
    c = cnt[b]
    s = sum(r["recall_5"] for r in rows if r["bucket"] == b)
    print(f"{lbl[b]:<18}{c:>6}{c / n:>8.1%}{s / n:>12.4f}"
          f"{(s / c if c else 0):>10.4f}")
print("-" * 76)

c_rows = [r for r in rows if r["bucket"] == "C_squeezed"]
ranks = sorted(r["rank_in_30"] for r in c_rows)
if ranks:
    print(f"\nC 桶（证据块在 6~30 名）{len(c_rows)} 题，名次中位 {ranks[len(ranks)//2]}，"
          f"区间 {ranks[0]}~{ranks[-1]}")
    print("  名次分布：" + "  ".join(f"{lo}-{hi}:{sum(1 for x in ranks if lo <= x <= hi)}"
                                  for lo, hi in ((6, 8), (9, 12), (13, 20), (21, 30))))
d_rows = [r for r in rows if r["bucket"] == "D_recall_fail"]
print(f"\nD 桶（连 top-30 都没有）{len(d_rows)} 题 —— 真召回失败样本：")
for r in d_rows[:12]:
    print(f"  {r['id']}  n_full={r['n_full']}  len30={r['len_ch30']}  {r['q'][:40]}")

a = cnt["A_no_ceiling"]
rest = [r["recall_5"] for r in rows if r["bucket"] != "A_no_ceiling"]
print(f"\n剔除 A 桶后（{n - a} 题）recall = {sum(rest) / max(len(rest), 1):.4f}")

OUT.write_text("\n".join(_buf), encoding="utf-8")
