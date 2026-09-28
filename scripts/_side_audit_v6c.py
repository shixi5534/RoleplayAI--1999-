# -*- coding: utf-8 -*-
"""补全：answerable-only 各口径 + 生产（重排）口径 + v6 声称值溯源。"""
import json
from pathlib import Path

R = Path("data/compendium_rag/reports")


def stat(name, mode, ans=True):
    p = R / name
    if not p.exists():
        return None
    d = json.loads(p.read_text(encoding="utf-8"))
    rows = [r for r in d["rows"] if r.get("mode") == mode]
    if ans is not None:
        rows = [r for r in rows if bool(r.get("answerable")) == ans]
    if not rows:
        return (0, 0, None)
    h = sum(1 for r in rows if r.get("hit"))
    return h, len(rows), round(h / len(rows), 4)


print("=== answerable-only（196 / 206 基数）===")
for f in ["eval_300cn_lex_on.json", "eval_300cn_lex_tiebreak.json", "eval_300cn_v6_tb_lexoff.json"]:
    for m in ("full", "graph_only"):
        r = stat(f, m, True)
        print(f"  {f:34} {m:11} {r[0]}/{r[1]} = {r[2]}")

print()
print("=== v6 声称 vs 磁盘（300cn）===")
b = json.loads((R / "baseline_v6.json").read_text(encoding="utf-8"))
print("  v6 secondary_300cn.lex_on_bare_hit6   =", b["secondary_300cn"]["lex_on_bare_hit6"]["rate"])
print("  v6 secondary_300cn.lex_on_graph_only  =", b["secondary_300cn"]["lex_on_graph_only"]["rate"])
print("  v6 锁里挂的 eval_300cn_lex_on          =", stat("eval_300cn_lex_on.json", "full", True)[2])
print("  v6 锁里挂的 eval_300cn_lex_on(gonly)   =", stat("eval_300cn_lex_on.json", "graph_only", True)[2])
print("  未入锁的 eval_300cn_lex_tiebreak       =", stat("eval_300cn_lex_tiebreak.json", "full", True)[2])

print()
print("=== 生产（重排）口径 ===")
acc = json.loads((R / "baseline_v6_acceptance.json").read_text(encoding="utf-8"))
for k, v in acc.items():
    print(f"  {k}: bare={v['bare_hit6']}  rerank={v['rerank_hit6']}  hit10={v['hit10']}  up={v['up']} down={v['down']}")

print()
print("=== 目标① 收口结论（读最新报告）===")
for p in sorted(R.glob("../..").__iter__()):
    pass
docs = Path("docs")
cands = [d for d in docs.glob("*.md") if "miss" in d.name or "缺口" in d.name or "召回" in d.name]
for d in cands:
    print("  -", d.name, d.stat().st_size)
