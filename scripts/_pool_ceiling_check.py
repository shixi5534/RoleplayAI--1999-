# -*- coding: utf-8 -*-
"""核对报告中的两个断言：
  A) lex=1 后 300cn 池上限 hit@30 仍为 0.9286（与 lex=0 相同）
  B) 仍有 9 道题 gold 不进池（需 P3）
"""
import json
from pathlib import Path

R = Path("data/compendium_rag/reports")


def pool_ceiling(name):
    d = json.loads((R / name).read_text(encoding="utf-8"))
    rows = [r for r in d["rows"] if r["mode"] == "full" and r["answerable"]]
    n = len(rows)
    h30 = sum(1 for r in rows if r.get("rank") and r["rank"] <= 30)
    miss = sorted(r["qid"] for r in rows if not r.get("rank") or r["rank"] > 30)
    return h30, n, miss


for lbl, f in [("lex=0 (r5 pool)", "rank_collect_r5_top30.json"),
               ("lex=1 (v6 pool)", "rank_collect_v6c300_top30.json")]:
    h, n, miss = pool_ceiling(f)
    print(f"{lbl:18} hit@30 = {h}/{n} = {h/n:.4f}   池内 miss {len(miss)} 题")
    print(f"                   {miss}")
