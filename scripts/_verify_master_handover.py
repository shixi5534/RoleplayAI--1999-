# -*- coding: utf-8 -*-
"""核验总交接文档（docs/compendium-rag/handover/交接_20260928_总_39全战役.md）中的数字与磁盘证据是否一致。"""
import hashlib
import json
import re
import subprocess
from pathlib import Path

DOC = Path("docs/compendium-rag/handover/交接_20260928_总_39全战役.md")
R = Path("data/compendium_rag/reports")
FAILS = []


def chk(label, got, want):
    ok = got == want
    print(f"  [{'OK ' if ok else 'BAD'}] {label}: got={got} want={want}")
    if not ok:
        FAILS.append(label)


doc = DOC.read_text(encoding="utf-8")
print(f"[doc] {DOC.name}  {len(doc)} chars\n")

print("=== 图与 git 不变式 ===")
b = Path("data/compendium_rag/graph.json").read_bytes()
g = json.loads(b.decode("utf-8"))
chk("entities", len(g["entities"]), 7033)
chk("edges", len(g["edges"]), 30269)
chk("graph sha16", hashlib.sha256(b).hexdigest()[:16], "4bbefd9eba577c01")
n = int(subprocess.run(["git", "rev-list", "--count", "2535325..HEAD"],
                       capture_output=True, text=True).stdout.strip())
# 提交数随每次新提交增长；本文落盘时为 25，故只断言 >= 25 并如实打印
print(f"  [{'OK ' if n >= 25 else 'BAD'}] total session commits >= 25: got={n}")
if n < 25:
    FAILS.append("total session commits")
tags = subprocess.run(["git", "tag", "-l"], capture_output=True, text=True).stdout.split()
# 断言「v6 时代的标签均在库」而非**精确等于**该列表：
# 之后新增 baseline-v7 / backup-* 属正常演进，精确相等会让核验在演进后必然失败
# （与 v7 核验脚本改用自洽性断言同一教训）。
want_tags = ["baseline-v2", "baseline-v3", "baseline-v4", "baseline-v5", "baseline-v6"]
missing_tags = [t for t in want_tags if t not in tags]
print(f"  [{'OK ' if not missing_tags else 'BAD'}] tags 含 v2–v6: "
      f"missing={missing_tags} (现有 {len(tags)} 个)")
if missing_tags:
    FAILS.append("tags")

print("\n=== §4 双口径总账 ===")


def hits(f, mode="full", ans=True):
    p = R / f
    if not p.exists():
        return None
    d = json.loads(p.read_text(encoding="utf-8"))
    rows = [x for x in d["rows"] if x.get("mode") == mode
            and bool(x.get("answerable")) is ans]
    return (sum(1 for x in rows if x.get("hit")), len(rows))


chk("盲测 lex=0 (off)", hits("eval_blind_lex_off.json"), (132, 206))
chk("盲测 lex=1 (tiebreak)", hits("eval_blind_lex_tiebreak.json"), (172, 206))
chk("盲测 lex_first=3", hits("eval_blind_lexfirst.json"), (190, 206))
chk("盲测 lex_first=3 graph_only", hits("eval_blind_lexfirst.json", "graph_only"), (186, 206))
chk("300cn lex=0", hits("eval_300cn_after_r5.json"), (156, 196))
chk("300cn lex=1", hits("eval_300cn_lex_tiebreak.json"), (165, 196))
chk("300cn lex_first=3", hits("eval_300cn_lexfirst.json"), (165, 196))
chk("300cn lex_first=3 graph_only", hits("eval_300cn_lexfirst.json", "graph_only"), (160, 196))
chk("300cn unans (lex_first)", hits("eval_300cn_lexfirst.json", "full", False), (1, 104))

print("\n=== §3.1 盲测集 ===")
bp = Path("data/knowledge/_audit/blind_v1/questions_strict.json")
chk("blind strict n", len(json.loads(bp.read_text(encoding="utf-8"))["cases"]), 206)
chk("blind_shard_A n", len(json.loads(
    Path("data/knowledge/_audit/blind_v1/questions_A.json").read_text(encoding="utf-8"))["cases"]), 53)
chk("blind_shard_C_total", sum(len(json.loads(
    Path(f"data/knowledge/_audit/blind_v1/questions_C{i}.json").read_text(encoding="utf-8"))["cases"])
    for i in (1, 2, 3)), 54)

print("\n=== §3.4 重拟合过拟合 ===")
p = R / "_p3_lexfirst_refit.json"
if p.exists():
    d = json.loads(p.read_text(encoding="utf-8"))
    chk("refit 300cn", d["300cn"]["rerank_hit6"], 0.8724)
    chk("refit blind", d["blind206"]["rerank_hit6"], 0.7427)
    chk("refit blind down", d["blind206"]["down"], 37)

print("\n=== §3.8 CE ===")
p = R / "_p4_ce_subset.json"
if p.exists():
    d = json.loads(p.read_text(encoding="utf-8"))
    chk("CE large", round(d["ce"], 4), 0.5)
    chk("CE lin", round(d["lin"], 4), 0.4231)
p = R / "_p4_ce_onnx_subset.json"
if p.exists():
    chk("ONNX int8", round(json.loads(p.read_text(encoding="utf-8"))["ce_hit6"], 4), 0.4231)

print("\n=== §0/§3.2 BASELINE_v6 验收值 ===")
p = R / "baseline_v6.json"
if p.exists():
    B6 = json.loads(p.read_text(encoding="utf-8"))
    chk("v6 blind production", B6["primary_blind"]["production_rerank_hit6"], 0.8786)
    chk("v6 verdict", B6["primary_blind"]["verdict"], "PASS")
    chk("v6 unans hits", B6["secondary_300cn"]["safety_unanswerable"]["hits"], 1)
    chk("v6 grounded", B6["secondary_300cn"]["safety_unanswerable"]["grounded_rate"], 1.0)

print("\n=== 文档提到的关键文件存在性 ===")
for rel in ("docs/compendium-rag/baseline/BASELINE_v6_20260928.md",
            "docs/compendium-rag/recall/目标①_收口报告_20260928.md",
            "data/knowledge/_audit/testset_300cn_gold_defects.json",
            "data/compendium_rag/backups/graph.json.prev.r5",
            "scripts/_accept_all_phases.py",
            "scripts/_lexfirst_regression.py",
            "scripts/_fusion_vs_lexonly.py"):
    chk(f"exists {rel}", Path(rel).exists(), True)

print("\n=== 文档自身一致性（关键数字出现性）===")
for token in ("0.9223", "0.8786", "0.8418", "0.9320", "0.8301", "4bbefd9eba577c01",
              "lex_first", "CMPRAG_LEX_WEIGHT", "gold", "0.9286"):
    chk(f"doc contains {token}", token in doc, True)

print()
print("RESULT:", "ALL OK" if not FAILS else f"{len(FAILS)} MISMATCH: {FAILS}")
