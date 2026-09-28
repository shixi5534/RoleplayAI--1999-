# -*- coding: utf-8 -*-
"""生产口径验证：k=1 的池 + **冻结重排**（权重来自 300cn v6 lab，未重新拟合）。

为何必须测：冻结重排的 `full_topN` 策略用到池内**原始名次** rn，
k 改变会改变池序 → 生产口径未必与裸检索同向。orig(RRF分) 权重为 0，
故改 k 不会扭曲已冻结的权重，但池序变化仍需实测。

复用既有 _side_verify_8786.py 的机制：从 collect 池 + 冻结 policy 重算。
本脚本对「k=60 池」与「k=1 池」分别算生产口径。
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

labdoc = json.loads((R / "rank_rerank_lab_300cn_v6.json").read_text(encoding="utf-8"))
chosen = labdoc["chosen"]
feats = lab.BASE_FEATURES
w = np.array([float(chosen["weights"].get(f, 0.0)) for f in feats])
policy, param = chosen["policy"], list(chosen["params"].values())[0]
print(f"[frozen] policy={policy} params={chosen['params']} "
      f"(300cn lab chosen hit6={chosen['hit6']})")
print(f"[frozen] orig 权重 = {chosen['weights'].get('orig')}  <- 为 0 则改 k 不扭曲权重")

fb = lab.FeatureBuilder(kb)
POOL = 30

for label, fname in [("300cn", "rank_collect_v6c300_top30.json"),
                     ("blind", "rank_collect_v6cblind_top30.json")]:
    p = R / fname
    if not p.exists():
        print(f"[skip] {fname} 缺失"); continue
    d = lab.load_collect(p, POOL) if hasattr(lab, "load_collect") else None
    if d is None:
        print(f"[skip] load_collect 不可用"); continue
    prep = lab.prepare(d, kb, fb, "full", POOL, None)
    Z, G, ans = prep["Z"], prep["G"], prep["ans"]
    idx = np.where(ans)[0]
    base_perm = np.tile(np.arange(POOL), (len(idx), 1))
    base_m = lab.metrics(base_perm, G[idx], POOL)
    perm = lab.apply_policy(policy, param, Z[idx] @ w, POOL)
    m = lab.metrics(perm, G[idx], POOL)
    up, down = lab.flips(perm, G[idx], [prep["qids"][i] for i in idx],
                         prep["base_hit6"][idx], POOL)
    print(f"\n=== {label} (pool={POOL}) ===")
    print(f"  n={m['n']}  裸池 hit@6={base_m['hit6']}  ->  生产口径(重排) hit@6={m['hit6']}")
    print(f"  hit10={m['hit10']}  mrr6={m['mrr6']}  up={len(up)} down={len(down)}")
print()
print("注：本脚本用的是**既有 collect 池**（k=60 采集）。")
print("    k=1 的真实池需重新采集；裸检索已用真冷启动验证（300cn 0.8520 / blind 0.8932）。")
