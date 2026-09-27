# -*- coding: utf-8 -*-
"""**冻结配置外样本检验（全 206 盲测题）**：把 300cn 上选定的生产重排配置原样应用。

判据（预注册）：生产口径 hit@6 = 冻结权重 + full_topN(a=1.0)。
  - 若 ≥0.85 则"盲测过关"成立；否则如实报差距。
  注意：lab 脚本会在传入题集上**重新拟合**，故其样本内数字不可用作能力声明。
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


def main() -> int:
    s = get_settings()
    kb = P.load_kb(s)
    prod = json.loads((ROOT / "data/compendium_rag/reports/rank_rerank_lab_300cn_r5.json")
                      .read_text(encoding="utf-8"))["chosen"]
    feats = lab.BASE_FEATURES
    w = np.array([float(prod["weights"].get(f, 0.0)) for f in feats])
    print(f"[frozen] {prod['policy']} {prod['params']}  weights={dict(zip(feats, w))}")

    targets = [
        ("blind_final(206)", ROOT / "data/compendium_rag/reports/rank_collect_blindfinal_top30.json"),
        ("300cn(196)", ROOT / "data/compendium_rag/reports/rank_collect_r5_top30.json"),
    ]
    pool = 30
    fb = lab.FeatureBuilder(kb)
    out = {}
    for label, path in targets:
        if not path.exists():
            print(f"[skip] missing {path.name}")
            continue
        d = lab.load_collect(path, pool)
        prep = lab.prepare(d, kb, fb, "full", pool, None)
        Z, G, ans = prep["Z"], prep["G"], prep["ans"]
        idx = np.where(ans)[0]
        base_perm = np.tile(np.arange(pool), (len(idx), 1))
        base_m = lab.metrics(base_perm, G[idx], pool)
        S = Z[idx] @ w
        perm = lab.apply_policy(prod["policy"], prod["params"]["a"], S, pool)
        m = lab.metrics(perm, G[idx], pool)
        up, down = lab.flips(perm, G[idx], [prep["qids"][i] for i in idx],
                             prep["base_hit6"][idx], pool)
        out[label] = {"n": m["n"], "baseline_hit6": base_m["hit6"],
                      "frozen_hit6": m["hit6"], "hit10": m["hit10"], "mrr6": m["mrr6"],
                      "up": len(up), "down": len(down), "up_qids": up[:30],
                      "down_qids": down[:30]}
        print(f"\n=== {label} ===")
        print(f"  baseline(现网三通道) hit@6 = {base_m['hit6']}")
        print(f"  **冻结生产配置**    hit@6 = {m['hit6']}   (hit@10={m['hit10']}, MRR6={m['mrr6']})")
        print(f"  up={len(up)} down={len(down)}")
        print(f"  target 0.85 -> {'PASS' if m['hit6'] >= 0.85 else 'FAIL'}")

    p = ROOT / "data/compendium_rag/reports/frozen_prod_on_blindfinal.json"
    p.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\n-> {p}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
