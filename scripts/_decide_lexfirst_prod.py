# -*- coding: utf-8 -*-
"""§1 决定性证据：lex_first 在**生产口径**上的影响（冻结重排，三池对照）。

冻结权重来自 rank_rerank_lab_300cn_v6.json 的 chosen（未在任何池上重拟合）。
对照：
  A. k=60 池（v6 时代）
  B. k=1  池（v7 当前）
  C. k=1 + lex_first=3 池（若启用 lex_first 会怎样）
"""
from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

from compendium_rag import pipeline as P                       # noqa: E402
from compendium_rag.config import get_settings                 # noqa: E402

spec = importlib.util.spec_from_file_location("lab", ROOT / "scripts/_rank_rerank_lab.py")
lab = importlib.util.module_from_spec(spec)
spec.loader.exec_module(lab)

R = ROOT / "data/compendium_rag/reports"
kb = P.load_kb(get_settings())
chosen = json.loads((R / "rank_rerank_lab_300cn_v6.json")
                    .read_text(encoding="utf-8"))["chosen"]
feats = lab.BASE_FEATURES
w = np.array([float(chosen["weights"].get(f, 0.0)) for f in feats])
policy, param = chosen["policy"], list(chosen["params"].values())[0]
print(f"冻结配置：{policy} a={param}（300cn 拟合，未重拟合）\n")
fb = lab.FeatureBuilder(kb)
POOL = 30

print(f"{'池':32} {'裸 hit@6':>10} {'生产口径':>10} {'up/down':>9}")
print("-" * 68)
res = {}
for label, fname in [
    ("A 300cn k=60 (v6)", "rank_collect_v6c300_top30.json"),
    ("B 300cn k=1  (v7)", "rank_collect_k1c300_top30.json"),
    ("C 300cn k=1+lf3", "rank_collect_k1lf3c300_top30.json"),
]:
    p = R / fname
    if not p.exists():
        print(f"{label:32} 缺文件 {fname}")
        continue
    d = lab.load_collect(p, POOL)
    prep = lab.prepare(d, kb, fb, "full", POOL, None)
    Z, G, ans = prep["Z"], prep["G"], prep["ans"]
    idx = np.where(ans)[0]
    base_m = lab.metrics(np.tile(np.arange(POOL), (len(idx), 1)), G[idx], POOL)
    perm = lab.apply_policy(policy, param, Z[idx] @ w, POOL)
    m = lab.metrics(perm, G[idx], POOL)
    up, down = lab.flips(perm, G[idx], [prep["qids"][i] for i in idx],
                         prep["base_hit6"][idx], POOL)
    res[label] = m["hit6"]
    print(f"{label:32} {base_m['hit6']:>10.4f} {m['hit6']:>10.4f} "
          f"{len(up):>4}/{len(down):<4}")

print()
print("=" * 68)
print("判定")
print("=" * 68)
a = res.get("A 300cn k=60 (v6)")
b = res.get("B 300cn k=1  (v7)")
c = res.get("C 300cn k=1+lf3")
if b is not None and c is not None:
    print(f"  v7 生产口径 (k=1)          = {b:.4f}")
    print(f"  若再加 lex_first=3          = {c:.4f}")
    print(f"  -> {'lex_first 使生产口径下降 ✗（应保持关闭）' if c < b else 'lex_first 不降生产口径'}")
if a is not None and b is not None:
    print(f"  v6 -> v7（本次改动）        = {a:.4f} -> {b:.4f}"
          f"  {'（无回退 ✓）' if b >= a - 1e-9 else '（回退 ✗）'}")
