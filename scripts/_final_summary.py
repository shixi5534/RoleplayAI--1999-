# -*- coding: utf-8 -*-
"""收官核对：两个目标的最终数字。"""
import json
from pathlib import Path

R = Path("data/compendium_rag/reports")
print("=== 目标②：子代理盲写 206 题（留出集）上的生产口径 ===")
f = json.loads((R / "frozen_prod_on_blindfinal.json").read_text(encoding="utf-8"))
b = f["blind_final(206)"]
verdict = "PASS" if b["frozen_hit6"] >= 0.85 else "FAIL"
print(f"  现网裸检索        hit@6 = {b['baseline_hit6']}")
print(f"  冻结生产配置      hit@6 = {b['frozen_hit6']}  (hit@10={b['hit10']}, MRR6={b['mrr6']})")
print(f"  up={b['up']} down={b['down']}   目标 0.85 -> {verdict}")
c = f["300cn(196)"]
print(f"  [对照] 300cn 调参集 hit@6 = {c['frozen_hit6']} (up={c['up']} down={c['down']})")

print()
print("=== 目标①：召回改进（词面通道）泛化 ===")
l = json.loads((R / "_lex_channel_full_scan.json").read_text(encoding="utf-8"))
print(f"  300cn 选出 w_lex = {l['selected_on_300cn']['w_lex']} "
      f"(hit {l['selected_on_300cn']['hit']}/{l['selected_on_300cn']['n']})")
for k, v in l["holdout_blind"].items():
    print(f"  盲测 w={k}: {v['hit']}/{v['n']} = {v['hit'] / v['n']:.4f}")
print(f"  留出集 Δhit@6 = {l['holdout_delta_pt']}pt  "
      f"up={len(l['holdout_up'])} down={len(l['holdout_down'])}")
