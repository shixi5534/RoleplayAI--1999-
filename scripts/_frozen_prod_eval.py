# -*- coding: utf-8 -*-
"""**冻结配置外样本检验**：把 300cn 上选定的生产重排配置，原样应用到盲测题集。

为什么必须这样做：
  `_rank_rerank_lab.py` 会在**传入的任何题集上重新拟合**权重与 α。
  因此"盲测集上 lab=0.94"是**样本内**数字，不是系统能力。
  真实问题应当是：把在 300cn 上冻结的配置拿到盲测题上，还能得多少？

判据（预注册）：
  - 生产口径 hit@6 = 冻结权重 + full_topN(a=1.0) 在盲测集上的成绩
  - 若 ≥0.85 则"过关"成立；否则如实报告差距
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

from compendium_rag import pipeline as P                       # noqa: E402
from compendium_rag.config import get_settings                 # noqa: E402
import importlib.util                                          # noqa: E402

spec = importlib.util.spec_from_file_location("lab", ROOT / "scripts/_rank_rerank_lab.py")
lab = importlib.util.module_from_spec(spec)
spec.loader.exec_module(lab)


def main() -> int:
    s = get_settings()
    kb = P.load_kb(s)

    # ── 冻结的生产配置（来自 300cn 的 rank_rerank_lab_300cn_r5.json chosen）──
    prod = json.loads((ROOT / "data/compendium_rag/reports/rank_rerank_lab_300cn_r5.json")
                      .read_text(encoding="utf-8"))["chosen"]
    feats = lab.BASE_FEATURES
    w = np.array([float(prod["weights"].get(f, 0.0)) for f in feats])
    print("[frozen] policy:", prod["policy"], "params:", prod["params"])
    print("[frozen] weights:", dict(zip(feats, w)))

    TARGETS = {
        "blind_strict(207)": ROOT / "data/compendium_rag/reports/rank_collect_blindstrict_top30.json",
        "300cn(196)": ROOT / "data/compendium_rag/reports/rank_collect_r5_top30.json",
    }
    pool = 30
    fb = lab.FeatureBuilder(kb)
    out = {}
    for label, path in TARGETS.items():
        if not path.exists():
            print(f"[skip] {path.name} 不存在")
            continue
        d = lab.load_collect(path, pool)
        prep = lab.prepare(d, kb, fb, "full", pool, None)
        if prep["mismatch"]:
            print(f"  [warn] 基线自检不一致 {len(prep['mismatch'])} 题")
        Z, G, ans = prep["Z"], prep["G"], prep["ans"]
        # 只评 answerable（与主口径一致）
        idx = np.where(ans)[0]
        base_perm = np.tile(np.arange(pool), (len(idx), 1))
        base_m = lab.metrics(base_perm, G[idx], pool)
        S = Z[idx] @ w
        perm = lab.apply_policy(prod["policy"], prod["params"]["a"], S, pool)
        m = lab.metrics(perm, G[idx], pool)
        up, down = lab.flips(perm, G[idx], [prep["qids"][i] for i in idx],
                             prep["base_hit6"][idx], pool)
        out[label] = {"n": m["n"], "baseline_hit6": base_m["hit6"],
                      "frozen_hit6": m["hit6"], "hit10": m["hit10"],
                      "mrr6": m["mrr6"], "up": len(up), "down": len(down),
                      "up_qids": up, "down_qids": down}
        print(f"\n=== {label} ===")
        print(f"  baseline(现网) hit@6 = {base_m['hit6']}")
        print(f"  **冻结配置  ** hit@6 = {m['hit6']}  (hit@10={m['hit10']}, MRR6={m['mrr6']})")
        print(f"  up={len(up)} down={len(down)}")
        print(f"  target 0.85 -> {'PASS' if m['hit6'] >= 0.85 else 'FAIL'}")

    p = ROOT / "data/compendium_rag/reports/frozen_prod_on_blind.json"
    p.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\n-> {p}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
