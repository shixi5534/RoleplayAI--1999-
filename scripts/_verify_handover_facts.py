# -*- coding: utf-8 -*-
"""交接文档事实核验：逐条比对文档中的数字与磁盘证据，防止交接文档本身出错。"""
import json
import os
from pathlib import Path

R = Path("data/compendium_rag/reports")
FAILS = []


def chk(label, got, want):
    ok = got == want
    print(f"  [{'OK ' if ok else 'BAD'}] {label}: got={got} want={want}")
    if not ok:
        FAILS.append(label)


def hits(f, mode="full", ans=True):
    p = R / f
    if not p.exists():
        return None
    d = json.loads(p.read_text(encoding="utf-8"))
    rows = [x for x in d["rows"] if x.get("mode") == mode
            and bool(x.get("answerable")) is ans]
    return (sum(1 for x in rows if x.get("hit")), len(rows))


print("=== §3 双口径总账核验 ===")
chk("盲测 lex=0 full", hits("eval_blind_lex_off.json"), (132, 206))
chk("盲测 lex=1 full", hits("eval_blind_lex_tiebreak.json"), (172, 206))
chk("盲测 lex_first=3 full", hits("eval_blind_lexfirst.json"), (190, 206))
chk("盲测 lex_first=3 graph_only", hits("eval_blind_lexfirst.json", "graph_only"), (186, 206))
chk("300cn lex=0 full", hits("eval_300cn_after_r5.json"), (156, 196))
chk("300cn lex=1 full", hits("eval_300cn_lex_tiebreak.json"), (165, 196))
chk("300cn lex_first=3 full", hits("eval_300cn_lexfirst.json"), (165, 196))
chk("300cn lex_first=3 graph_only", hits("eval_300cn_lexfirst.json", "graph_only"), (160, 196))
chk("300cn lex=0 unans", hits("eval_300cn_after_r5.json", "full", False), (1, 104))
chk("300cn lex_first=3 unans", hits("eval_300cn_lexfirst.json", "full", False), (1, 104))

print("\n=== §4.2 重拟合过拟合核验 ===")
p = R / "_p3_lexfirst_refit.json"
if p.exists():
    d = json.loads(p.read_text(encoding="utf-8"))
    chk("refit 300cn rerank", d["300cn"]["rerank_hit6"], 0.8724)
    chk("refit blind rerank", d["blind206"]["rerank_hit6"], 0.7427)
    chk("refit blind down", d["blind206"]["down"], 37)

print("\n=== §4.5 RM3 否决核验（脚本内数字，此处只查文件存在）===")
print("  (RM3 数字来自 _p3_prf_rm3.py 运行输出，非落盘 JSON)")

print("\n=== §4.6 CE 核验 ===")
p = R / "_p4_ce_subset.json"
if p.exists():
    d = json.loads(p.read_text(encoding="utf-8"))
    chk("CE subset rrf", round(d["rrf"], 4), 0.3462)
    chk("CE subset lin", round(d["lin"], 4), 0.4231)
    chk("CE subset ce", round(d["ce"], 4), 0.5)
p = R / "_p4_ce_onnx_subset.json"
if p.exists():
    d = json.loads(p.read_text(encoding="utf-8"))
    chk("ONNX int8 ce", round(d["ce_hit6"], 4), 0.4231)

print("\n=== §4.4 放宽池/池上限核验 ===")
# 池上限从 collect 重算
d = json.loads((R / "rank_collect_v6c300_top30.json").read_text(encoding="utf-8"))
rows = [r for r in d["rows"] if r["mode"] == "full" and r["answerable"]]
h30 = sum(1 for r in rows if r.get("rank") and r["rank"] <= 30)
chk("300cn 池上限 hit@30", h30, 182)

print("\n=== §10 提交/图不变式 ===")
import hashlib
import subprocess
b = open("data/compendium_rag/graph.json", "rb").read()
g = json.loads(b.decode("utf-8"))
chk("entities", len(g["entities"]), 7033)
chk("edges", len(g["edges"]), 30269)
chk("graph sha16", hashlib.sha256(b).hexdigest()[:16], "4bbefd9eba577c01")
n = int(subprocess.run(["git", "rev-list", "--count", "2f9d966..HEAD"],
                       capture_output=True, text=True).stdout.strip())
# 提交数会随每次新提交增长，故只断言「≥15 笔」（交接文档落盘时的值），并如实打印
print(f"  [{'OK ' if n >= 15 else 'BAD'}] session commits >= 15: got={n}")
if n < 15:
    FAILS.append("session commits")
tags = subprocess.run(["git", "tag", "-l"], capture_output=True, text=True).stdout.split()
chk("tag count", len(tags), 5)

print()
print("RESULT:", "ALL OK" if not FAILS else f"{len(FAILS)} MISMATCH: {FAILS}")
