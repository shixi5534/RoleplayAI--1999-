# -*- coding: utf-8 -*-
"""验证「相关性 ≠ 覆盖率」假设：按证据组数分层看 Cross-Encoder 的得失。

假设：
    inject_pass 要求**所有证据组**被注入的若干块**并集**覆盖；
    而 Cross-Encoder 优化的是**单块**与查询的相关性。
    若假设成立，分层结果应呈现：
        单组题 → CE 有帮助（单块覆盖即达标）
        多组题 → CE 有害（把最相关的块顶上来，挤掉了覆盖另一组的互补块）

用法：.venv/Scripts/python.exe -X utf8 scripts/_analyze_ce_rows.py
"""
from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AB = ROOT / "data" / "knowledge" / "_audit" / "ablation"
OUT = AB / "_ce_stratified.txt"
SRC = AB / "cross_encoder_rows_int8_10.json"
buf: list[str] = []


def p(*a):
    buf.append(" ".join(str(x) for x in a))


if not SRC.is_file():
    OUT.write_text(f"[MISSING] {SRC.name}", encoding="utf-8")
    raise SystemExit(1)

rows = json.loads(SRC.read_text(encoding="utf-8"))
n = len(rows)
p("=" * 84)
p(f"Cross-Encoder 分层分析（{SRC.name}，n={n}）")
p("=" * 84)

# 按证据组数分层
p(f"{'证据组数':<10}{'题数':>6}{'inject前':>10}{'inject后':>10}{'Δinject':>10}"
  f"{'top2前':>9}{'top2后':>9}{'Δtop2':>9}")
p("-" * 84)
buckets = [("1 组", [r for r in rows if r["n_groups"] == 1]),
           ("2 组", [r for r in rows if r["n_groups"] == 2]),
           ("≥3 组", [r for r in rows if r["n_groups"] >= 3])]
for label, sub in buckets:
    if not sub:
        continue
    m = len(sub)
    bi = sum(r["base_inject"] for r in sub) / m
    ci = sum(r["ce_inject"] for r in sub) / m
    bt = sum(r["base_top2"] for r in sub) / m
    ct = sum(r["ce_top2"] for r in sub) / m
    p(f"{label:<10}{m:>6}{bi:>10.4f}{ci:>10.4f}{ci - bi:>+10.4f}"
      f"{bt:>9.4f}{ct:>9.4f}{ct - bt:>+9.4f}")

single = [r for r in rows if r["n_groups"] == 1]
multi = [r for r in rows if r["n_groups"] >= 2]
p("-" * 84)
if single:
    ds = (sum(r["ce_inject"] for r in single) - sum(r["base_inject"] for r in single)) / len(single)
    p(f"单组题（{len(single)} 题）Δinject = {ds:+.4f}")
if multi:
    dm = (sum(r["ce_inject"] for r in multi) - sum(r["base_inject"] for r in multi)) / len(multi)
    p(f"多组题（{len(multi)} 题）Δinject = {dm:+.4f}")
    p()
    if ds > 0 and dm < 0:
        p("✅ **假设成立**：单组题受益、多组题受损 ⇒ 确实是「相关性 ≠ 覆盖率」问题，")
        p("   不是模型能力问题。纯相关性重排对多组证据题是**反向优化**。")
    else:
        p("❌ 假设不成立，需另找原因")

# 交叉看：top2 提升 vs inject 变化
p()
p("=" * 84)
p("交叉：证据块进前 2 名（top2）变化 → inject 结果")
p("=" * 84)
cross = Counter()
for r in rows:
    t = ("top2 提升" if (r["ce_top2"] and not r["base_top2"]) else
         "top2 下降" if (r["base_top2"] and not r["ce_top2"]) else "top2 不变")
    cross[(t, r["ce_inject"] - r["base_inject"])] += 1

p(f"{'top2 变化':<12}{'inject 变好':>12}{'inject 不变':>12}{'inject 变差':>12}")
for t in ("top2 提升", "top2 不变", "top2 下降"):
    better = cross.get((t, 1), 0)
    same = cross.get((t, 0), 0)
    worse = cross.get((t, -1), 0)
    p(f"{t:<12}{better:>12}{same:>12}{worse:>12}")

OUT.write_text("\n".join(buf), encoding="utf-8")
