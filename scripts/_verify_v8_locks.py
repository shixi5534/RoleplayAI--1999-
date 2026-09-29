# -*- coding: utf-8 -*-
"""BASELINE_v8 锁复算（与 _verify_v7_locks.py 同形，显式真实路径）。"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

DATA = Path("data/compendium_rag")
b = json.loads((DATA / "reports/baseline_v8.json").read_text(encoding="utf-8"))

print("=" * 78)
print("BASELINE_v8 工件锁复算")
print("=" * 78)
paths = b["artifact_paths"]
ok = True
for k, want in b["artifact_sha256_16"].items():
    rel = paths.get(k)
    if rel is None:
        print(f"  [BAD] {k:24} 无路径映射")
        ok = False
        continue
    p = DATA / rel
    if not p.exists():
        print(f"  [MISSING] {k:24} {rel}")
        ok = False
        continue
    got = hashlib.sha256(p.read_bytes()).hexdigest()[:16]
    good = got == want
    ok &= good
    print(f"  [{'OK ' if good else 'BAD'}] {k:24} {got} (lock {want})  {rel}")
print(f"\n判定: {'全部命中' if ok else '存在不一致'}")

print("\n=== v8 关键数字 ===")
m = b["metrics"]
print(f"  300cn 裸检索   = {m['300cn_bare_hit6']['hits']}/{m['300cn_bare_hit6']['n']}"
      f" = {m['300cn_bare_hit6']['rate']}")
print(f"  盲测206 裸检索 = {m['blind206_bare_hit6']['hits']}/{m['blind206_bare_hit6']['n']}"
      f" = {m['blind206_bare_hit6']['rate']}")
print(f"  泛化120 裸检索 = {m['gen120_bare_hit6']['hits']}/{m['gen120_bare_hit6']['n']}"
      f" = {m['gen120_bare_hit6']['rate']}")
print(f"  300cn 生产口径 = {m['300cn_production_hit6']}")
print(f"  盲测  生产口径 = {m['blind206_production_hit6']}")
print(f"  安全线 unanswerable = {m['safety_unanswerable']['hits']}"
      f"/{m['safety_unanswerable']['n']}   grounded = {m['grounded']}")
print(f"  图 = {b['graph']['entities']}/{b['graph']['edges']}  {b['graph']['sha256_16']}")
print(f"  R4-K01 = {b['r4_k01_status']['state']}")
raise SystemExit(0 if ok else 1)
