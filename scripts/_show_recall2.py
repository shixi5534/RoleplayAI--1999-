# -*- coding: utf-8 -*-
"""深挖：D 桶是真召回失败还是候选池太浅；C 桶放宽 top 能救回多少。"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT / "data" / "knowledge" / "_audit"
OUT = AUDIT / "_recall_summary2.txt"
buf: list[str] = []


def p(*a):
    buf.append(" ".join(str(x) for x in a))


d = json.loads((AUDIT / "diag_recall_cause.json").read_text(encoding="utf-8"))
rows = d["rows"]
n = len(rows)

# 1) 候选池深度：top_chunks=30 时实际返回多少块
lens = sorted(r["len_ch30"] for r in rows)
p("=" * 70)
p(f"① 候选池深度：请求 top=30 时实际返回块数（n={n}）")
p(f"   中位 {lens[n//2]}｜最小 {lens[0]}｜最大 {lens[-1]}")
for lo, hi in ((0, 5), (6, 10), (11, 20), (21, 29), (30, 30)):
    p(f"   {lo:>2}-{hi:<2} 块：{sum(1 for x in lens if lo <= x <= hi):>3} 题")
shallow = sum(1 for x in lens if x < 25)
p(f"   ⇒ 返回不足 25 块（候选池偏浅）的共 {shallow} 题")

# 2) D 桶内部：浅池 vs 深池仍漏
dr = [r for r in rows if r["bucket"] == "D_recall_fail"]
d_shallow = [r for r in dr if r["len_ch30"] < 25]
p()
p("=" * 70)
p(f"② D 桶（真召回失败 {len(dr)} 题）内部拆解")
p(f"   候选池 <25 块（压根没生成够候选）：{len(d_shallow)} 题")
p(f"   候选池 ≥25 块（池子够深但仍漏掉）  ：{len(dr) - len(d_shallow)} 题")
p(f"   D 桶 n_full（语料中可答块数）中位："
  f"{sorted(r['n_full'] for r in dr)[len(dr)//2]}")
p(f"   n_full=1（语料里只有 1 块能答，极稀疏）的题数："
  f"{sum(1 for r in dr if r['n_full'] == 1)}")

# 3) C 桶：放宽 top 能救回多少
cr = [r for r in rows if r["bucket"] == "C_squeezed"]
p()
p("=" * 70)
p(f"③ C 桶（证据块在 6~30 名，共 {len(cr)} 题）：放宽 top 的边际收益")
for t in (6, 8, 10, 12, 15, 20, 30):
    got = sum(1 for r in cr if r["rank_in_30"] <= t)
    p(f"   top={t:<3} 可救回 {got:>3} 题（累计占全量 {got / n:>6.2%}）")

# 4) 综合：把 A 桶视作指标噪声后的真实结构
a = sum(1 for r in rows if r["bucket"] == "A_no_ceiling")
b = sum(1 for r in rows if r["bucket"] == "B_top5")
p()
p("=" * 70)
p("④ 综合（recall 低的三层原因）")
p(f"   A 指标性（语料无单块可答，recall 恒 0）      {a:>3} 题  {a/n:>6.1%}")
p(f"   C 排序/截断（证据在 6~30 名，放宽 top 可救） {len(cr):>3} 题  {len(cr)/n:>6.1%}")
p(f"   D 真召回失败（候选池里就没有）              {len(dr):>3} 题  {len(dr)/n:>6.1%}")
p(f"   B 已进 top-5（这部分没问题）                {b:>3} 题  {b/n:>6.1%}")

OUT.write_text("\n".join(buf), encoding="utf-8")
