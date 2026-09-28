# -*- coding: utf-8 -*-
"""复核 v6 头条数字：把 300cn 上拟合的冻结配置应用到 v6 盲测池，重算生产口径。

背景：baseline_v6.json 声称 primary_blind.production_rerank_hit6 = 0.8786，
但磁盘上找不到任何承载该数字的盲测验收文件（frozen_prod_v6_blind.json 不存在）。
本脚本用 v6 的池重算，判定该数字是否可复现。
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
s = get_settings()
kb = P.load_kb(s)

# 冻结配置：来自 300cn v6 lab 的 chosen
labdoc = json.loads((R / "rank_rerank_lab_300cn_v6.json").read_text(encoding="utf-8"))
chosen = labdoc["chosen"]
feats = lab.BASE_FEATURES
w = np.array([float(chosen["weights"].get(f, 0.0)) for f in feats])
policy = chosen["policy"]
param = list(chosen["params"].values())[0]
print(f"[frozen] {policy} {chosen['params']}  (300cn lab chosen hit6={chosen['hit6']})")

fb = lab.FeatureBuilder(kb)
pool = 30
for label, fname in [("blind206 (v6 pool)", "rank_collect_v6cblind_top30.json"),
                     ("300cn (v6 pool)", "rank_collect_v6c300_top30.json")]:
    p = R / fname
    if not p.exists():
        print(f"[skip] {fname} 缺失")
        continue
    d = lab.load_collect(p, pool)
    prep = lab.prepare(d, kb, fb, "full", pool, None)
    Z, G, ans = prep["Z"], prep["G"], prep["ans"]
    idx = np.where(ans)[0]
    base_perm = np.tile(np.arange(pool), (len(idx), 1))
    base_m = lab.metrics(base_perm, G[idx], pool)
    perm = lab.apply_policy(policy, param, Z[idx] @ w, pool)
    m = lab.metrics(perm, G[idx], pool)
    up, down = lab.flips(perm, G[idx], [prep["qids"][i] for i in idx],
                         prep["base_hit6"][idx], pool)
    print(f"\n=== {label} ===")
    print(f"  n={m['n']}  bare hit@6={base_m['hit6']}  ->  rerank hit@6={m['hit6']}")
    print(f"  hit10={m['hit10']}  mrr6={m['mrr6']}  up={len(up)} down={len(down)}")
    print(f"  up={up[:12]}")
    print(f"  down={down[:12]}")
