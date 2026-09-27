# -*- coding: utf-8 -*-
"""收官确认：两个目标的最终数字（可重跑）。"""
import json
from pathlib import Path

R = Path("data/compendium_rag/reports")

print("=== 目标②：子代理盲写 206 题（留出集）上的生产口径 ===")
f = json.loads((R / "frozen_prod_on_blindfinal.json").read_text(encoding="utf-8"))
b = f["blind_final(206)"]
print(f"  现网裸检索   hit@6 = {b['baseline_hit6']}")
print(f"  冻结生产配置 hit@6 = {b['frozen_hit6']}  (hit@10={b['hit10']}, MRR6={b['mrr6']})")
print(f"  up={b['up']}  down={b['down']}   目标 0.85 -> "
      f"{'PASS' if b['frozen_hit6'] >= 0.85 else 'FAIL'}")

print()
print("=== 目标①：词面通道接线后的正式冷启动对照（盲测 206 题）===")


def full_rate(name):
    d = json.loads((R / name).read_text(encoding="utf-8"))
    rows = [r for r in d["rows"] if r.get("mode") == "full" and r.get("answerable")]
    return sum(1 for r in rows if r.get("hit")), len(rows)


h0, n = full_rate("eval_blind_strict_r5.json")
h1, n1 = full_rate("eval_blind_lex_on.json")
print(f"  通道关 lex=0 : {h0}/{n} = {h0 / n:.4f}")
print(f"  通道开 lex=1 : {h1}/{n1} = {h1 / n1:.4f}   ({(h1 - h0) / n * 100:+.1f}pt)")

print()
print("=== 图未被本次工作改动 ===")
import hashlib
gb = Path("data/compendium_rag/graph.json").read_bytes()
g = json.loads(gb.decode("utf-8"))
print(f"  entities={len(g['entities'])} edges={len(g['edges'])} "
      f"sha16={hashlib.sha256(gb).hexdigest()[:16]}")
