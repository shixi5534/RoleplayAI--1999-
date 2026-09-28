# -*- coding: utf-8 -*-
"""逐文件核对（稳健版）：各 eval 报告 full / graph_only 的 hit@6 + 锁对账。

目的：查清 baseline_v6.json 的汇总数字各自来自哪个文件，
特别是 300cn 与盲测的「裸 hit@6」是否混用了不同代（tie-break 前/后）的文件。
"""
import hashlib
import json
from pathlib import Path

R = Path("data/compendium_rag/reports")


def stat(name, mode):
    p = R / name
    if not p.exists():
        return None
    d = json.loads(p.read_text(encoding="utf-8"))
    rows = [r for r in d["rows"] if r.get("mode") == mode]
    if not rows:
        return (0, 0, None, hashlib.sha256(p.read_bytes()).hexdigest()[:16])
    h = sum(1 for r in rows if r.get("hit"))
    g = sum(1 for r in rows if r.get("grounded"))
    return h, len(rows), round(h / len(rows), 4), hashlib.sha256(p.read_bytes()).hexdigest()[:16]


files = [
    "eval_300cn_lex_on.json", "eval_300cn_lex_tiebreak.json", "eval_300cn_v6_tb_lexoff.json",
    "eval_blind_lex_on.json", "eval_blind_lex_tiebreak.json", "eval_blind_lex_off.json",
    "eval_gen_lex_on.json", "eval_gen_lex_tiebreak.json",
]
print(f"{'file':40} {'mode':11} {'hit/n':>10} {'rate':>7}  sha16")
for f in files:
    for m in ("full", "graph_only"):
        r = stat(f, m)
        if r is None:
            print(f"{f:40} {m:11} {'MISSING':>10}")
        else:
            h, n, rt, sh = r
            ratio = f"{h}/{n}" if n else "-"
            print(f"{f:40} {m:11} {ratio:>10} {str(rt):>7}  {sh}")

print()
print("=== baseline_v6.json 锁对账 ===")
b = json.loads((R / "baseline_v6.json").read_text(encoding="utf-8"))
mapping = {
    "graph_live": Path("data/compendium_rag/graph.json"),
    "baseline_v5": R / "baseline_v5.json",
    "eval_300cn_lex_on": R / "eval_300cn_lex_on.json",
    "eval_gen_lex_on": R / "eval_gen_lex_on.json",
    "eval_blind_lex_on": R / "eval_blind_lex_on.json",
    "eval_blind_lex_tiebreak": R / "eval_blind_lex_tiebreak.json",
    "eval_300cn_lex_off": R / "eval_300cn_lex_off.json",
}
for k, exp in b["artifact_sha256_16"].items():
    p = mapping[k]
    if not p.exists():
        print(f"  {k:26} 期望 {exp}  **文件缺失** ({p.name})")
        continue
    got = hashlib.sha256(p.read_bytes()).hexdigest()[:16]
    print(f"  {k:26} {got}  {'OK' if got == exp else 'MISMATCH(期望 ' + exp + ')'}")

print()
print("=== 汇总字段 vs 各文件（定位来源）===")
claims = [
    ("secondary_300cn.lex_on_bare_hit6", b["secondary_300cn"]["lex_on_bare_hit6"]["rate"], "full"),
    ("secondary_300cn.lex_on_graph_only", b["secondary_300cn"]["lex_on_graph_only"]["rate"], "graph_only"),
    ("primary_blind.bare_hit6", b["primary_blind"]["bare_hit6"]["rate"], "full"),
    ("generalization_120.lex_on_full_hit6", b["generalization_120"]["lex_on_full_hit6"]["rate"], "full"),
]
for label, claim, mode in claims:
    print(f"  {label} = {claim}")
    for f in files:
        r = stat(f, mode)
        if r and r[2] is not None and abs(r[2] - claim) < 1e-9:
            print(f"      <- 来源命中: {f} ({r[0]}/{r[1]})")
