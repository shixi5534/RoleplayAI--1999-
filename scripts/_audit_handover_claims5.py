# -*- coding: utf-8 -*-
"""独立复核（第五轮）：lex-only 0.9320 来源、验收/核验项数、锁工件在库状态。"""
from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path

R = Path("data/compendium_rag/reports")

print("=" * 88)
print("① lex-only 与 fused 对照（§3.3 与结尾「一句话交接」）")
print("=" * 88)
cand = [
    ("lex-only（词面通道单独）", "eval_blind_lexfirst.json"),
    ("fused lex=1（官方路径）", "eval_blind_lex_tiebreak.json"),
]
for label, f in cand:
    d = json.loads((R / f).read_text(encoding="utf-8"))
    rows = [r for r in d["rows"] if r.get("mode") == "full"]
    h = sum(1 for r in rows if r.get("hit"))
    print(f"  {label:26} {f:32} {h}/{len(rows)} = {h/len(rows):.4f}")
print()
print("  文档 §3.3      : lex-only 0.9320 (192/206)  vs 融合 0.8350 (172/206)")
print("  文档结尾一句话 : lex-only 0.9320 (192/206)  vs 融合 0.8301 (171/206)  <-- 与 §3.3 自相矛盾")
print(f"  192/206={192/206:.4f}   172/206={172/206:.4f}   171/206={171/206:.4f}")
print("  → 0.8301 出自『盲测验收报告 §5.3 harness 估计』，非官方路径；结尾把它当作官方融合值")

print()
print("=" * 88)
print("② 验收套件与事实核验脚本的实际项数")
print("=" * 88)
for script, claimed in [("scripts/_accept_all_phases.py", "50 项判据"),
                        ("scripts/_verify_handover_facts.py", "24 项"),
                        ("scripts/_verify_master_handover.py", "46 项")]:
    src = Path(script).read_text(encoding="utf-8")
    n_check = src.count("check(") + src.count("rec(")
    print(f"  {script:40} 源码 check/rec 调用≈{n_check:3}   文档声称 {claimed}")
    r = subprocess.run([".venv/Scripts/python.exe", script] +
                       (["_accept"] if "_accept" in script else []),
                       capture_output=True, text=True, encoding="utf-8", errors="replace")
    out = r.stdout or ""
    np_ = out.count("[PASS]") + out.count("[OK ]") + out.count("[OK]")
    nf = out.count("[FAIL]") + out.count("[BAD")
    print(f"      实跑: 通过≈{np_}  失败≈{nf}   末行={out.strip().splitlines()[-1][:60] if out.strip() else '(空)'}")

print()
print("=" * 88)
print("③ BASELINE_v6 锁定工件在 git 中的状态")
print("=" * 88)
b = json.loads((R / "baseline_v6.json").read_text(encoding="utf-8"))
for k in sorted(b["artifact_sha256_16"]):
    # 找同名文件
    matches = list(R.glob(f"{k}.json"))
    tracked = subprocess.run(["git", "ls-files", "--error-unmatch",
                              str(R / f"{k}.json")], capture_output=True)
    print(f"  {k:26} 同名文件={[m.name for m in matches]}  已入库={tracked.returncode==0}")
print()
for f in ["eval_300cn_lex_tiebreak.json", "eval_blind_lex_tiebreak.json",
          "baseline_v6_acceptance.json", "rank_rerank_lab_300cn_v6.json"]:
    p = R / f
    tracked = subprocess.run(["git", "ls-files", "--error-unmatch", str(p)],
                             capture_output=True)
    print(f"  {f:34} exists={p.exists()}  已入库={tracked.returncode==0}")
