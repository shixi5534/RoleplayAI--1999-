# -*- coding: utf-8 -*-
"""独立复核：从原始 rows 重算各口径 hit@6，与 baseline_v6.json 汇总字段对账。"""
import json
from pathlib import Path

R = Path("data/compendium_rag/reports")


def rate(name, mode, want_answerable=None):
    d = json.loads((R / name).read_text(encoding="utf-8"))
    rows = [r for r in d["rows"] if r.get("mode") == mode]
    if want_answerable is not None:
        rows = [r for r in rows if bool(r.get("answerable")) == want_answerable]
    h = sum(1 for r in rows if r.get("hit"))
    g = sum(1 for r in rows if r.get("grounded"))
    return h, len(rows), g


print("=== 从原始 rows 重算（不读汇总字段）===")
checks = [
    ("300cn  裸  full      ", "eval_300cn_lex_on.json", "full", True),
    ("300cn  graph_only    ", "eval_300cn_lex_on.json", "graph_only", True),
    ("300cn  unanswerable  ", "eval_300cn_lex_on.json", "full", False),
    ("盲测206 裸  full      ", "eval_blind_lex_on.json", "full", None),
    ("泛化120 裸  full      ", "eval_gen_lex_on.json", "full", True),
]
for label, f, m, ans in checks:
    h, n, g = rate(f, m, ans)
    print(f"  {label} {h}/{n} = {h/n:.4f}   grounded={g}/{n}")

print()
print("=== 与 baseline_v6.json 汇总字段对账 ===")
b = json.loads((R / "baseline_v6.json").read_text(encoding="utf-8"))
pairs = [
    ("300cn lex1 裸", b["secondary_300cn"]["lex_on_bare_hit6"]["rate"], "eval_300cn_lex_on.json", "full", True),
    ("300cn graph_only", b["secondary_300cn"]["lex_on_graph_only"]["rate"], "eval_300cn_lex_on.json", "graph_only", True),
    ("盲测 裸", b["primary_blind"]["bare_hit6"]["rate"], "eval_blind_lex_on.json", "full", None),
    ("泛化 裸", b["generalization_120"]["lex_on_full_hit6"]["rate"], "eval_gen_lex_on.json", "full", True),
]
for label, claim, f, m, ans in pairs:
    h, n, _ = rate(f, m, ans)
    got = round(h / n, 4)
    print(f"  {label:18} 汇总={claim}  重算={got}  {'OK' if abs(claim-got)<1e-9 else 'MISMATCH'}")

print()
print("=== 图 SHA 与锁 ===")
import hashlib
gb = Path("data/compendium_rag/graph.json").read_bytes()
print("  graph sha16", hashlib.sha256(gb).hexdigest()[:16], "= 锁定值", b["graph"]["sha256_16"])
bad = []
for k, exp in b["artifact_sha256_16"].items():
    m = {"graph_live": "graph.json", "baseline_v5": "baseline_v5.json",
         "eval_300cn_lex_on": "eval_300cn_lex_on.json", "eval_gen_lex_on": "eval_gen_lex_on.json",
         "eval_blind_lex_on": "eval_blind_lex_on.json",
         "eval_blind_lex_tiebreak": "eval_blind_lex_tiebreak.json",
         "eval_300cn_lex_off": "eval_300cn_lex_off.json"}.get(k)
    if not m:
        bad.append((k, "unmapped")); continue
    p = Path("data/compendium_rag") / m if m == "graph.json" else R / m
    got = hashlib.sha256(p.read_bytes()).hexdigest()[:16]
    if got != exp:
        bad.append((k, got, exp))
print(f"  锁命中: {'全部 OK' if not bad else bad}")
