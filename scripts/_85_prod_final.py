# -*- coding: utf-8 -*-
"""生产口径总对照：k=60 池 vs k=1 池，两集（冻结重排权重不变）。"""
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
fb = lab.FeatureBuilder(kb)
POOL = 30

print(f"冻结配置：{policy} a={param}（300cn 拟合，未在盲测重拟合）")
print(f"{'池':34} {'裸池 hit@6':>12} {'生产口径':>10} {'up/down':>10}")
print("-" * 74)
rows = []
for label, fname in [
    ("300cn  池 k=60 (v6)", "rank_collect_v6c300_top30.json"),
    ("300cn  池 k=1  (new)", "rank_collect_k1c300_top30.json"),
    ("blind  池 k=60 (v6)", "rank_collect_v6cblind_top30.json"),
    ("blind  池 k=1  (new)", "rank_collect_k1blind_top30.json"),
]:
    p = R / fname
    if not p.exists():
        print(f"{label:34} {'缺失':>12}")
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
    rows.append((label, base_m["hit6"], m["hit6"], len(up), len(down),
                 m["hit10"], m["mrr6"]))
    print(f"{label:34} {base_m['hit6']:>12.4f} {m['hit6']:>10.4f} "
          f"{len(up):>4}/{len(down):<4}")

print()
print("=== 判定 ===")
d300 = [r for r in rows if r[0].startswith("300cn")]
dblind = [r for r in rows if r[0].startswith("blind")]
if len(d300) == 2 and len(dblind) == 2:
    print(f"  300cn 生产口径: k=60 {d300[0][2]:.4f} -> k=1 {d300[1][2]:.4f}"
          f"  {'无回退 ✓' if d300[1][2] >= d300[0][2] - 1e-9 else '回退 ✗'}")
    print(f"  blind 生产口径: k=60 {dblind[0][2]:.4f} -> k=1 {dblind[1][2]:.4f}"
          f"  {'提升 ✓' if dblind[1][2] > dblind[0][2] else '回退 ✗'}")
