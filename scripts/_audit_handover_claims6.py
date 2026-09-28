# -*- coding: utf-8 -*-
"""独立复核（第六轮）：针对『召回率85目标收官与融合重构』专文的声称逐条对账。"""
from __future__ import annotations

import json
from pathlib import Path

R = Path("data/compendium_rag/reports")


def ans_hit(f: str, mode: str = "full", ans: bool | None = True) -> tuple[int, int]:
    p = R / f
    if not p.exists():
        return (-1, -1)
    d = json.loads(p.read_text(encoding="utf-8"))
    sel = [r for r in d["rows"] if r.get("mode") == mode]
    if ans is not None:
        sel = [r for r in sel if bool(r.get("answerable")) == ans]
    return sum(1 for r in sel if r.get("hit")), len(sel)


print("=" * 90)
print("① §3 双口径总账逐格对账")
print("=" * 90)
rows = [
    ("盲测206 full 裸", "lex=0", 0.6408, "eval_blind_lex_off.json", "full", None),
    ("盲测206 full 裸", "lex=1", 0.8350, "eval_blind_lex_tiebreak.json", "full", None),
    ("盲测206 full 裸", "lex_first", 0.9223, "eval_blind_lexfirst.json", "full", None),
    ("盲测206 graph_only", "lex=0", 0.4175, "eval_blind_lex_off.json", "graph_only", None),
    ("盲测206 graph_only", "lex=1", 0.7427, "eval_blind_lex_tiebreak.json", "graph_only", None),
    ("盲测206 graph_only", "lex_first", 0.9029, "eval_blind_lexfirst.json", "graph_only", None),
    ("300cn full 裸", "lex=1", 0.8418, "eval_300cn_lex_tiebreak.json", "full", True),
    ("300cn full 裸", "lex_first", 0.8418, "eval_300cn_lexfirst.json", "full", True),
    ("300cn graph_only", "lex=1", 0.8010, "eval_300cn_lex_tiebreak.json", "graph_only", True),
    ("300cn graph_only", "lex_first", 0.8163, "eval_300cn_lexfirst.json", "graph_only", True),
    ("泛化120 full", "lex=1", 0.9083, "eval_gen_lex_on.json", "full", True),
    ("泛化120 full", "lex=0", 0.8000, "eval_gen_tiebreak.json", "full", True),
]
for label, cfg, claim, f, mode, ans in rows:
    h, n = ans_hit(f, mode, ans)
    if h < 0:
        print(f"  {label:22} {cfg:10} 声称={claim:.4f}  [缺文件 {f}]")
        continue
    got = h / n
    flag = "OK " if abs(got - claim) < 5e-5 else "*** MISMATCH"
    print(f"  {label:22} {cfg:10} 声称={claim:.4f}  重算={got:.4f} ({h}/{n})  [{flag}]")

print()
print("=" * 90)
print("② §4.1 lex-only = 192/206 = 0.9320 —— 磁盘上有承载工件吗？")
print("=" * 90)
print("  可查到的近似工件:")
for f in ["eval_blind_lexfirst.json"]:
    h, n = ans_hit(f, "full", None)
    print(f"    {f:34} full {h}/{n} = {h/n:.4f}   <-- 不是 192/206")
print("  192/206 无同名验收工件；文档称其来自 scripts/_fusion_vs_lexonly.py 的实时计算")
print("  （该脚本不落盘结果，故 0.9320 无法由磁盘工件复核）")
print("  ⚠ 若 lex-only 实为 190/206=0.9223，则 §4.1 的『lex_first 使 0.8350→0.9223』")
print("     正好等于把 lex-only 上限取回 —— 两者非常可能是同一测量")

print()
print("=" * 90)
print("③ §5.2 声称：collect 文件 hit 字段 = hit@top_k(=30)，不是 hit@6")
print("=" * 90)
for f in ["rank_collect_v6c300_top30.json", "rank_collect_v6cblind_top30.json"]:
    p = R / f
    if not p.exists():
        print(f"  [缺] {f}")
        continue
    d = json.loads(p.read_text(encoding="utf-8"))
    mp = d.get("map", {})
    ks = list(mp.keys())
    print(f"  {f}: map 条目={len(ks)}  样例键={ks[:2]}")
    for k in ks[:2]:
        v = mp[k]
        print(f"     {k}: type={type(v).__name__} keys={list(v.keys()) if isinstance(v,dict) else v}")
        if isinstance(v, dict):
            for kk in ("hit", "rank", "gold_rank"):
                if kk in v:
                    print(f"        {kk} = {v[kk]}")
    # 用 gold_rank 反推 hit 口径
    if isinstance(mp[ks[0]], dict) and "gold_rank" in mp[ks[0]]:
        gr = [v.get("gold_rank") for v in mp.values() if isinstance(v, dict)]
        gr = [g for g in gr if isinstance(g, int)]
        if gr:
            print(f"     gold_rank 分布: <=6 的 {sum(1 for g in gr if g<=6)}/{len(gr)}"
                  f"   <=30 的 {sum(1 for g in gr if g<=30)}/{len(gr)}")
