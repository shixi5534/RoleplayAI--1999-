# -*- coding: utf-8 -*-
"""BASELINE_v7 锁复算（与 _verify_v6_locks.py 同形，但用显式真实路径）。"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

DATA = Path("data/compendium_rag")
b = json.loads((DATA / "reports/baseline_v7.json").read_text(encoding="utf-8"))

print("=" * 76)
print("BASELINE_v7 工件锁复算")
print("=" * 76)
paths = b["artifact_paths"]
ok = True
# graph_live 是**活图**锚点：R6 改图后按设计失效（历史惯例：除 live 外全部命中）。
# 其余工件锁必须全中 —— 这才是"历史可重建"的判据。
LIVE_KEYS = {"graph_live"}
ok_nonlive = True
for k, want in b["artifact_sha256_16"].items():
    rel = paths.get(k)
    if rel is None:
        print(f"  [BAD] {k:26} 无路径映射")
        ok = False
        continue
    p = DATA / rel
    if not p.exists():
        print(f"  [MISSING] {k:26} {rel}")
        ok = False
        continue
    got = hashlib.sha256(p.read_bytes()).hexdigest()[:16]
    good = got == want
    ok &= good
    if k not in LIVE_KEYS:
        ok_nonlive &= good
    tag = "" if good else ("  <- 活图锚点，已由 R6 演进（预期）"
                           if k in LIVE_KEYS else "  <- 非预期！")
    print(f"  [{'OK ' if good else 'BAD'}] {k:26} {got} (lock {want}){tag}")
print(f"\n判定: {'全部命中' if ok else '存在不一致'}")
print(f"      非活图锁: {'全部命中' if ok_nonlive else '存在不一致 ✗'}"
      f"（历史可重建判据）")

print("\n=== v7 关键数字（读自基线工件）===")
pb, s3, g1 = b["primary_blind"], b["secondary_300cn"], b["generalization_120"]
print(f"  盲测206  裸检索   = {pb['bare_hit6']['rate']} "
      f"({pb['bare_hit6']['hits']}/{pb['bare_hit6']['n']})  -> {pb['verdict']}")
print(f"  盲测206  graph_only = {pb['bare_hit6_graph_only']['rate']}")
print(f"  盲测206  生产口径  = {pb['production_rerank_hit6']}")
print(f"  300cn    裸检索   = {s3['bare_hit6']['rate']} "
      f"({s3['bare_hit6']['hits']}/{s3['bare_hit6']['n']})  -> {s3['verdict']}")
print(f"  300cn    生产口径  = {s3['production_rerank_hit6']}")
print(f"  泛化120  裸检索   = {g1['bare_hit6']['rate']}")
sl = b["safety_line"]
print(f"  安全线 unanswerable = {sl['unanswerable_hits']}/{sl['unanswerable_n']}"
      f"   grounded = {sl['grounded']}")
if not ok:
    print()
    print("注：若唯一不匹配项是 graph_live，属**预期** —— R6（2026-09-28）已演进图谱，")
    print("    该锚点按设计失效（历史惯例：除 live 外全部命中）。")
    print("    当前 live 锚点见 BASELINE_v8（026b41699f021db2），用 _verify_v8_locks.py 复算。")
# 退出码以**非活图锁**为准：它们全中即证明历史工件可从 git 重建。
raise SystemExit(0 if ok_nonlive else 1)
