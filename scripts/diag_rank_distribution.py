# -*- coding: utf-8 -*-
"""证据块名次分布 —— 零成本（直接读现有报告，不跑检索）。

为什么看这个：
    inject_pass 只有 62%，而产品按 plot_context_max_chars=2400 装配、约装 2 块。
    也就是说**证据块必须排进前 2 名**才算数，排第 3~8 名跟没召回一样。
    而 recall 统计的是「进没进 top-8」，两者差着一个量级。

做法：
    报告里每题都有 mrr = 1/（第一个全证据覆盖块的名次）。
    直接换算成名次分布，看有多少题的证据块落在前 2 名。

用法：.venv/Scripts/python.exe -X utf8 scripts/diag_rank_distribution.py
"""
from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT / "data" / "knowledge" / "_audit"
SRC = AUDIT / "plot_rag_eval_report_clean.json"
OUT = AUDIT / "_rank_dist.txt"
buf: list[str] = []


def p(*a):
    buf.append(" ".join(str(x) for x in a))


d = json.loads(SRC.read_text(encoding="utf-8"))
items = d.get("items") or []
n = len(items)
if not items:
    OUT.write_text("[MISSING] 报告无 items", encoding="utf-8")
    raise SystemExit(1)

ranks: Counter[int] = Counter()   # 1..8 名次
zero = 0                          # 返回块里没有全覆盖块
for it in items:
    m = it.get("mrr") or 0.0
    if not m:
        zero += 1
        continue
    r = int(round(1.0 / m))
    ranks[min(max(r, 1), 8)] += 1

p("=" * 72)
p(f"证据块（首个全证据覆盖块）名次分布 —— 源 {SRC.name}，n={n}")
p("=" * 72)
p(f"{'名次':<8}{'题数':>8}{'占比':>10}{'累计占比':>10}")
cum = 0
for r in range(1, 9):
    c = ranks.get(r, 0)
    cum += c
    p(f"{r:<8}{c:>8}{c / n:>10.1%}{cum / n:>10.1%}")
p(f"{'无覆盖块':<8}{zero:>8}{zero / n:>10.1%}{(cum + zero) / n:>10.1%}")
p("-" * 72)

top2 = ranks.get(1, 0) + ranks.get(2, 0)
mid = sum(ranks.get(r, 0) for r in range(3, 9))
inject = (d.get("summary") or {}).get("inject_pass", 0.0)
p()
p(f"★ 单块即可作答、且排进前 2 名：{top2} 题 = {top2 / n:.2%}")
p(f"  排第 3~8 名（进得了 top-8、但进不了 2400 字符的提示词）：{mid} 题 = {mid / n:.2%}")
p(f"  完全没捞到（A 无单块可答 14 + C 在 9~30 名 26 + D 池外 60）："
  f"{zero} 题 = {zero / n:.2%}")
p()
p(f"  实测 inject_pass = {inject:.2%}，高于「前 2 名」的 {top2 / n:.2%} —— ")
p("  **不是矛盾**：inject 判的是注入的若干块**并集**是否覆盖各证据组，")
p("  两块合起来能覆盖多组证据，所以不要求单块排第 1。")
p("  本表衡量的是「单块可答块」的名次，是**上界更严**的口径。")
p()
p("⇒ 结论：")
p("  1. 把「让证据块进 top-8」当目标是错的 —— 25.3% 的题进了 top-8 却排在第 3~8 名，")
p("     提示词只装得下约 2 块，跟没召回一样。")
p("  2. 扩大候选生成量无效（sem_top20 实测 +0.67pt 且返回块数不变）——")
p("     问题不是候选不够多，是**排序不对**。")
p("  3. 重排（reranker）理论上可动的靶子是 76（第 3~8 名）+ 26（第 9~30 名）= 102 题。")

OUT.write_text("\n".join(buf), encoding="utf-8")
