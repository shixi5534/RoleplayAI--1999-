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
    print(f"  [{'OK ' if good else 'BAD'}] {k:26} {got} (lock {want})  {rel}")
print(f"\n判定: {'全部命中' if ok else '存在不一致'}")

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
raise SystemExit(0 if ok else 1)
