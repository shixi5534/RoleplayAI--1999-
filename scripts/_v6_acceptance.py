# -*- coding: utf-8 -*-
"""BASELINE_v6 验收：把 **300cn(lex=1) 上拟合**的重排配置，冻结后应用到盲测 206 题。

判据（预注册，目标 ②）：生产口径（full + rerank）在盲测留出集上 ≥ 0.85。
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
    prod = json.loads((ROOT / "data/compendium_rag/reports/rank_rerank_lab_300cn_v6.json")
                      .read_text(encoding="utf-8"))["chosen"]
    feats = lab.BASE_FEATURES + ("extra",) if False else lab.BASE_FEATURES
    # chosen.weights 的键可能多于 BASE_FEATURES（含 chunk_len/log_deg 等）
    w = np.array([float(prod["weights"].get(f, 0.0)) for f in feats])
    print(f"[frozen] {prod['policy']} {prod['params']}")
    print(f"[frozen] weights = {dict(zip(feats, w))}")

    pool = 30
    fb = lab.FeatureBuilder(kb)
    targets = [
        ("blind206 (留出集)", "rank_collect_v6cblind_top30.json"),
        ("300cn (调参集)", "rank_collect_v6c300_top30.json"),
    ]
    out = {}
    for label, fname in targets:
        p = ROOT / "data/compendium_rag/reports" / fname
        if not p.exists():
            print(f"[skip] {fname}")
            continue
        d = lab.load_collect(p, pool)
        prep = lab.prepare(d, kb, fb, "full", pool, None)
        Z, G, ans = prep["Z"], prep["G"], prep["ans"]
        idx = np.where(ans)[0]
        base = lab.metrics(np.tile(np.arange(pool), (len(idx), 1)), G[idx], pool)
        S = Z[idx] @ w
        perm = lab.apply_policy(prod["policy"], prod["params"]["a"], S, pool)
        m = lab.metrics(perm, G[idx], pool)
        up, down = lab.flips(perm, G[idx], [prep["qids"][i] for i in idx],
                             prep["base_hit6"][idx], pool)
        out[label] = {"n": m["n"], "bare_hit6": base["hit6"], "rerank_hit6": m["hit6"],
                      "hit10": m["hit10"], "mrr6": m["mrr6"],
                      "up": len(up), "down": len(down), "up_qids": up, "down_qids": down}
        print(f"\n=== {label} ===")
        print(f"  裸检索 hit@6     = {base['hit6']}")
        print(f"  **生产口径(重排) = {m['hit6']}**  (hit@10={m['hit10']}, MRR6={m['mrr6']})")
        print(f"  up={len(up)} down={len(down)}")
        if "blind" in label:
            print(f"  目标 0.85 -> {'PASS' if m['hit6'] >= 0.85 else 'FAIL'}")

    op = ROOT / "data/compendium_rag/reports/baseline_v6_acceptance.json"
    op.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\n-> {op}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
