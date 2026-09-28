# -*- coding: utf-8 -*-
"""确认 v6 生产口径 0.8786 的溯源，以及锁清单的键名/内容一致性。"""
import hashlib
import json
from pathlib import Path

R = Path("data/compendium_rag/reports")


def sha16(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()[:16]


print("=== 1) 生产口径 0.8786 溯源 ===")
for f in sorted(R.glob("*.json")):
    try:
        d = json.loads(f.read_text(encoding="utf-8"))
    except Exception:
        continue
    s = json.dumps(d)
    if "0.8786" in s and "blind" in f.name.lower():
        print(f"  命中 {f.name}")
    if "0.8786" in s and "frozen" in f.name.lower():
        print(f"  命中 {f.name}")
for f in ["frozen_prod_v6_blind.json", "rank_rerank_lab_300cn_v6.json"]:
    p = R / f
    print(f"  {f}: {'存在' if p.exists() else '不存在'}")

print()
print("=== 2) 锁清单键名 vs 实际内容 ===")
b = json.loads((R / "baseline_v6.json").read_text(encoding="utf-8"))
locks = b["artifact_sha256_16"]
cands = sorted(R.glob("eval_*.json")) + [Path("data/compendium_rag/graph.json"), R / "baseline_v5.json"]
by_hash = {}
for p in cands:
    by_hash.setdefault(sha16(p), []).append(p.name)
for k, exp in locks.items():
    files = by_hash.get(exp, [])
    print(f"  {k:26} {exp}  -> 实际是 {files}")

print()
print("=== 3) 是否有文件名含 v6 的盲测验收件 ===")
for f in sorted(R.glob("*v6*.json")) + sorted(R.glob("*blind*frozen*.json")):
    print("  ", f.name)
