# -*- coding: utf-8 -*-
"""交接文档事实核验（v7）：逐条比对 docs/compendium-rag/handover/交接_20260928_召回率85收口_RRF_k常数.md 与磁盘证据。

纪律（继承 §9.7）：交接文档必须自校验 —— 不是"数字出现在文中"，而是
**数字与磁盘工件自洽**（含分子/分母、口径、SHA 锚点）。
"""
from __future__ import annotations

import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOC = ROOT / "docs/compendium-rag/handover/交接_20260928_召回率85收口_RRF_k常数.md"
B7 = ROOT / "docs/compendium-rag/baseline/BASELINE_v7_20260928.md"
DATA = ROOT / "data/compendium_rag"
R = DATA / "reports"
FAILS: list[str] = []


def ck(label: str, cond: bool, detail: str = "") -> None:
    print(f"  [{'OK ' if cond else 'BAD'}] {label}{('  ' + detail) if detail else ''}")
    if not cond:
        FAILS.append(label)


def sha16(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()[:16]


def rate(f: str, mode: str = "full", ans: bool | None = True):
    p = R / f
    if not p.exists():
        return None
    d = json.loads(p.read_text(encoding="utf-8"))
    rows = [r for r in d["rows"] if r.get("mode") == mode]
    if ans is not None:
        rows = [r for r in rows if bool(r.get("answerable")) == ans]
    return (sum(1 for r in rows if r.get("hit")), len(rows))


text = DOC.read_text(encoding="utf-8")
btext = B7.read_text(encoding="utf-8")

print("=" * 80)
print("① 文档存在 + 关键数字出现性")
print("=" * 80)
ck("交接文档在库", DOC.exists())
ck("BASELINE_v7 报告在库", B7.exists())
for n in ("0.8520", "0.8932", "0.9833", "0.8673", "0.9175", "0.8418", "0.8350",
          "CMPRAG_RRF_K", "baseline-v7", "4bbefd9eba577c01"):
    ck(f"文档含 {n}", n in text)

print()
print("=" * 80)
print("② 数字 vs 磁盘工件（自洽性，非仅出现性）")
print("=" * 80)
v7 = json.loads((R / "baseline_v7.json").read_text(encoding="utf-8"))
pairs = [
    ("300cn 裸检索", "eval_300cn_k1.json", "full", True, 167, 196),
    ("盲测 裸检索", "eval_blind_k1.json", "full", True, 184, 206),
    ("泛化120 裸检索", "eval_gen120_k1.json", "full", True, 118, 120),
    ("300cn graph_only", "eval_300cn_k1.json", "graph_only", True, 157, 196),
    ("盲测 graph_only", "eval_blind_k1.json", "graph_only", True, 174, 206),
    ("泛化120 graph_only", "eval_gen120_k1.json", "graph_only", True, 116, 120),
]
for label, f, mode, ans, wh, wn in pairs:
    rr = rate(f, mode, ans)
    ck(f"{label} = {wh}/{wn}", rr == (wh, wn), f"磁盘={rr}")

# 基线工件里记录的值必须与 eval 重算一致
ck("baseline_v7 300cn 裸 = 167/196",
   v7["secondary_300cn"]["bare_hit6"]["hits"] == 167
   and v7["secondary_300cn"]["bare_hit6"]["n"] == 196)
ck("baseline_v7 盲测 裸 = 184/206",
   v7["primary_blind"]["bare_hit6"]["hits"] == 184
   and v7["primary_blind"]["bare_hit6"]["n"] == 206)
ck("baseline_v7 泛化 裸 = 118/120",
   v7["generalization_120"]["bare_hit6"]["hits"] == 118
   and v7["generalization_120"]["bare_hit6"]["n"] == 120)
ck("文档声称的 0.8520/0.8932/0.9833 与工件一致",
   abs(167 / 196 - 0.8520) < 5e-5 and abs(184 / 206 - 0.8932) < 5e-5
   and abs(118 / 120 - 0.9833) < 5e-5)
ck("文档声称 300cn 生产口径无回退 0.8673",
   v7["secondary_300cn"]["production_rerank_hit6"] == 0.8673)
ck("文档声称 盲测生产口径 0.9175",
   v7["primary_blind"]["production_rerank_hit6"] == 0.9175)

print()
print("=" * 80)
print("③ 安全线与不变量")
print("=" * 80)
sl = v7["safety_line"]
ck("unanswerable = 1/104", sl["unanswerable_hits"] == 1 and sl["unanswerable_n"] == 104)
ck("grounded = 1.0", sl["grounded"] == 1.0)
ck("图规模未变：7033/30269（v7 时点）",
   v7["graph"]["entities"] == 7033 and v7["graph"]["edges"] == 30269)
# 图 SHA 分两层：v7 记录的**时点**活图锚点，与**当前**活图。
# R6（2026-09-28）摘除死别名后活图演进为 026b41699f021db2，属预期。
ck("v7 记录的活图锚点 = 4bbefd9eba577c01（时点事实）",
   v7["graph"]["sha256_16"] == "4bbefd9eba577c01", v7["graph"]["sha256_16"])
cur_graph = sha16(DATA / "graph.json")
ck("当前活图 = 026b41699f021db2（R6 之后，见 BASELINE_v8）",
   cur_graph == "026b41699f021db2", cur_graph)
ck("回滚锚点 prev.r6 可从 git 复原 v7 时的活图",
   sha16(DATA / "backups/graph.json.prev.r6") == "4bbefd9eba577c01")

print()
print("=" * 80)
print("④ 题集未改动（红线）")
print("=" * 80)
AUDIT = ROOT / "data/knowledge/_audit"
ck("300cn 题集 SHA-16 = b02700c70342864c",
   sha16(AUDIT / "rag_testset_300_cn.json") == "b02700c70342864c")
ck("盲测留出集 SHA-16 = abcd750a3323dc90",
   sha16(AUDIT / "blind_v1/questions_strict.json") == "abcd750a3323dc90")
ck("gold 审计旁挂在库", (AUDIT / "_85_gold_audit.json").exists())
ga = json.loads((AUDIT / "_85_gold_audit.json").read_text(encoding="utf-8"))
ck("gold 审计 31 题：16 有效 / 15 缺陷",
   ga["summary"]["n_audited"] == 31 and ga["summary"]["valid"] == 16
   and ga["summary"]["defective"] == 15, str(ga["summary"]))

print()
print("=" * 80)
print("⑤ 接线与默认值（零行为变更）")
print("=" * 80)
cfg = (ROOT / "src/compendium_rag/config.py").read_text(encoding="utf-8")
rt = (ROOT / "src/compendium_rag/retriever.py").read_text(encoding="utf-8")
pl = (ROOT / "src/compendium_rag/pipeline.py").read_text(encoding="utf-8")
ck('config 默认 rrf_k=60', '_env_int("CMPRAG_RRF_K", 60)' in cfg)
ck("retrieve 默认 rrf_k=60", "rrf_k: int = 60" in rt)
ck("两处 rrf_fuse 传 k=rrf_k", rt.count("k=rrf_k") == 2, str(rt.count("k=rrf_k")))
ck("pipeline 透传", "rrf_k=s.rrf_k" in pl)
# 实际默认值
sys.path.insert(0, str(ROOT / "src"))
import os
saved = os.environ.pop("CMPRAG_RRF_K", None)
from compendium_rag.config import get_settings  # noqa: E402
ck("Settings.rrf_k 默认 = 60", get_settings().rrf_k == 60, str(get_settings().rrf_k))
if saved:
    os.environ["CMPRAG_RRF_K"] = saved

print()
print("=" * 80)
print("⑥ 干净副本无缺件（v6 复现性断裂的回归判据）")
print("=" * 80)
ap = v7["artifact_paths"]
missing = []
for k, rel in ap.items():
    p = DATA / rel
    if not p.exists():
        missing.append(rel)
        continue
    tracked = subprocess.run(["git", "ls-files", "--error-unmatch", str(p)],
                             cwd=str(ROOT), capture_output=True)
    if tracked.returncode != 0:
        missing.append(f"{rel}(未入库)")
ck("v7 全部锁定工件存在且已入库", not missing, str(missing))
bad = [k for k, want in v7["artifact_sha256_16"].items()
       if (DATA / ap[k]).exists() and sha16(DATA / ap[k]) != want]
# graph_live 是**活图**锚点，R6 后按设计失效；其余锁必须全中（历史可重建判据）。
bad_nonlive = [k for k in bad if k != "graph_live"]
ck("v7 非活图锁全部命中（历史可重建）", not bad_nonlive, str(bad_nonlive))
if bad:
    ck("唯一失配项仅为 graph_live（R6 演进，属预期）",
       bad == ["graph_live"], str(bad))
    ck("  其历史值可由 prev.r6 复原",
       sha16(DATA / "backups/graph.json.prev.r6") == v7["artifact_sha256_16"]["graph_live"])

print()
print("=" * 80)
print("⑦ 提交与标签")
print("=" * 80)
tags = subprocess.run(["git", "tag"], cwd=str(ROOT), capture_output=True,
                      text=True, encoding="utf-8", errors="replace").stdout.split()
ck("baseline-v7 标签存在", "baseline-v7" in tags, str([t for t in tags if "v7" in t]))
ck("备份标签存在（回滚锚点）", "backup-pre-85push-20260928" in tags)
listed = re.findall(r"(?m)^([0-9a-f]{7}) ", text)
ck("文档列出的提交哈希存在且在库",
   bool(listed) and all(
       subprocess.run(["git", "cat-file", "-e", f"{h}^{{commit}}"],
                      cwd=str(ROOT), capture_output=True).returncode == 0
       for h in listed), str(listed))

print()
print("=" * 80)
if FAILS:
    print(f"RESULT: {len(FAILS)} 项失败 -> {FAILS}")
    raise SystemExit(1)
print("RESULT: ALL OK")
raise SystemExit(0)
