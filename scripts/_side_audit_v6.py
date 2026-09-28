# -*- coding: utf-8 -*-
"""逐文件核对：各 eval 报告的 hit@6，找出 baseline_v6 汇总字段的真正来源。"""
import hashlib
import json
from pathlib import Path

R = Path("data/compendium_rag/reports")


def rate(name, mode="full", ans=None):
    p = R / name
    if not p.exists():
        return None
    d = json.loads(p.read_text(encoding="utf-8"))
    rows = [r for r in d["rows"] if r.get("mode") == mode]
    if ans is not None:
        rows = [r for r in rows if bool(r.get("answerable")) == ans]
    h = sum(1 for r in rows if r.get("hit"))
    return h, len(rows), round(h / len(rows), 4), hashlib.sha256(p.read_bytes()).hexdigest()[:16]


files = [
    "eval_300cn_lex_on.json", "eval_300cn_lex_tiebreak.json", "eval_300cn_v6_tb_lexoff.json",
    "eval_blind_lex_on.json", "eval_blind_lex_tiebreak.json", "eval_blind_lex_off.json",
    "eval_gen_lex_on.json", "eval_gen_lex_tiebreak.json",
]
print(f"{'file':42} {'ans':5} {'hit/n':>10} {'rate':>7}  sha16")
for f in files:
    for ans, tag in ((True, "ans"), (False, "unans")):
        r = rate(f, "full", ans)
        if r is None:
            print(f"{f:42} {tag:5} {'MISSING':>10}")
        else:
            h, n, rt, sh = r
            print(f"{f:42} {tag:5} {str(h)+'/'+str(n):>10} {rt:>7}  {sh}")

print()
print("=== baseline_v6.json 声明的锁 vs 磁盘 ===")
b = json.loads((R / "baseline_v6.json").read_text(encoding="utf-8"))
for k, exp in b["artifact_sha256_16"].items():
    cands = {
        "graph_live": Path("data/compendium_rag/graph.json"),
        "baseline_v5": R / "baseline_v5.json",
        "eval_300cn_lex_on": R / "eval_300cn_lex_on.json",
        "eval_gen_lex_on": R / "eval_gen_lex_on.json",
        "eval_blind_lex_on": R / "eval_blind_lex_on.json",
        "eval_blind_lex_tiebreak": R / "eval_blind_lex_tiebreak.json",
        "eval_300cn_lex_off": R / "eval_300cn_lex_off.json",
    }[k]
    if not cands.exists():
        print(f"  {k:26} 期望 {exp}  文件缺失: {cands.name}")
        continue
    got = hashlib.sha256(cands.read_bytes()).hexdigest()[:16]
    print(f"  {k:26} {got}  {'OK' if got == exp else 'MISMATCH 期望 ' + exp}")
