# -*- coding: utf-8 -*-
"""生产口径（k=1 池 + 冻结重排）—— 与 v6 的 k=60 池对照。

冻结权重来自 rank_rerank_lab_300cn_v6.json 的 chosen（在 300cn 上拟合，未在盲测重拟合）。
本脚本只换**池**（k=1 采集的 collect），policy/权重一律不变 —— 即"冻结配置换池"，
这正是_side_verify_8786.py 用来复现 0.8786 的同一做法。
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

chosen = json.loads((R / "rank_rerank_lab_300cn_v6.json")
                    .read_text(encoding="utf-8"))["chosen"]
feats = lab.BASE_FEATURES
w = np.array([float(chosen["weights"].get(f, 0.0)) for f in feats])
policy, param = chosen["policy"], list(chosen["params"].values())[0]
print(f"[frozen] policy={policy} params={chosen['params']}")
print(f"[frozen] orig(RRF分) 权重={chosen['weights'].get('orig')} -> 换 k 不扭曲权重\n")

fb = lab.FeatureBuilder(kb)
POOL = 30

for label, fname in [("300cn 池(k=60, v6)", "rank_collect_v6c300_top30.json"),
                     ("300cn 池(k=1, new)", "rank_collect_k1c300_top30.json")]:
    p = R / fname
    if not p.exists():
        print(f"[skip] {fname} 缺失"); continue
    d = lab.load_collect(p, POOL)
    prep = lab.prepare(d, kb, fb, "full", POOL, None)
    Z, G, ans = prep["Z"], prep["G"], prep["ans"]
    idx = np.where(ans)[0]
    base_m = lab.metrics(np.tile(np.arange(POOL), (len(idx), 1)), G[idx], POOL)
    perm = lab.apply_policy(policy, param, Z[idx] @ w, POOL)
    m = lab.metrics(perm, G[idx], POOL)
    up, down = lab.flips(perm, G[idx], [prep["qids"][i] for i in idx],
                         prep["base_hit6"][idx], POOL)
    print(f"=== {label} ===")
    print(f"  n={m['n']}  裸池 hit@6={base_m['hit6']}  ->  生产口径 hit@6={m['hit6']}")
    print(f"  hit10={m['hit10']}  mrr6={m['mrr6']}  up={len(up)} down={len(down)}")
    print()
