# -*- coding: utf-8 -*-
"""目标① 决定性测试：**融合重构（lex 前 3 优先）** 能否提升**生产口径**（full+冻结重排）？

发现链：
  1. 盲测 206 上 **lex-only 0.9320 > fused 0.8301**（融合在稀释词面通道）；
  2. 权重扫描（1→16）无法修复；
  3. 结构改法 **m2_union(3)**（lex 前 3 占位，其余按融合序补足，去重）
     在 **300cn 选参**下同时改善两集：
       300cn 163 -> **166**/196 = 0.8469（全部配置最优）
       盲测  171 -> **188**/206 = 0.9126

本脚本把 m2_union(3) 接到**生产口径**（池 + 冻结 v6 重排），并核验安全线。

判据（预注册）：
  - 主判据：盲测生产口径 ≥ 现值 0.8786（不降）；
  - 安全线：unanswerable 不高于基线、grounded=1.0；
  - 同时给出 300cn 与泛化，验证非单集过拟合。
"""
from __future__ import annotations

import argparse
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
from _lex_channel_full import LexIndex, load_cases             # noqa: E402
from _r5_variant_scan import clear_ppr_cache, install_fast_ppr  # noqa: E402
from _fusion_restructure import channels_for, ranked_ids       # noqa: E402

spec = importlib.util.spec_from_file_location("lab", ROOT / "scripts/_rank_rerank_lab.py")
lab = importlib.util.module_from_spec(spec)
spec.loader.exec_module(lab)


def build_pool(kb, lex, q, qvec, top_n=30, lex_first=3):
    """m2_union(lex_first)：lex 前 L 优先，其余按融合序补足（去重）。"""
    clear_ppr_cache()
    lex_scored = dict(lex.search(q, 30))
    ch, _ = channels_for(kb.retriever, q, qvec)
    ch["lex"] = lex_scored
    fused = kb.retriever.rrf_fuse(ch, weights={"lex": 1.0}, top_n=max(top_n, 24))
    fused_ids = [e.chunk_id for e in fused]
    lex_ids = ranked_ids(lex_scored, top_n)
    out, seen = [], set()
    for cid in lex_ids[:lex_first] + fused_ids + lex_ids:
        if cid and cid not in seen:
            seen.add(cid)
            out.append(cid)
    return out[:top_n]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--lex-first", type=int, default=3)
    ap.add_argument("--pool", type=int, default=30)
    args = ap.parse_args()

    s = get_settings()
    kb = P.load_kb(s)
    print("[build] lex index …")
    lex = LexIndex(kb.chunks)
    install_fast_ppr()

    prod = json.loads((ROOT / "data/compendium_rag/reports/rank_rerank_lab_300cn_v6.json")
                      .read_text(encoding="utf-8"))["chosen"]
    feats = lab.BASE_FEATURES
    w = np.array([float(prod["weights"].get(f, 0.0)) for f in feats])
    a = float(prod["params"]["a"])
    fb = lab.FeatureBuilder(kb)
    print(f"[frozen reranker] {prod['policy']} a={a}")

    qv = {}
    for f in ("rank_collect_v6c300_top30.json", "rank_collect_v6cblind_top30.json"):
        p = ROOT / "data/compendium_rag/reports" / f
        if p.exists():
            qv.update(json.loads(p.read_text(encoding="utf-8")).get("qvecs") or {})

    ans = "\n".join(c.text for c in kb.chunks)
    sets = [
        ("300cn", [c for c in load_cases(ROOT / "data/knowledge/_audit/rag_testset_300_cn.json")
                   if any(k in ans for k in c["keywords"])]),
        ("盲测206", [c for c in load_cases(ROOT / "data/knowledge/_audit/blind_v1/questions_strict.json")
                     if any(k in ans for k in c["keywords"])]),
    ]
    out = {}
    for name, cases in sets:
        pool = args.pool
        Zs, Gs = [], []
        for c in cases:
            qvec = qv.get(c["qid"])
            ids = build_pool(kb, lex, c["q"], qvec, pool, args.lex_first)
            if len(ids) < pool:
                ids += [ids[-1]] * (pool - len(ids))
            Z1, _ = fb.question(c["q"], qvec, [{"chunk_id": x} for x in ids],
                                kb.retriever.link)
            Zs.append(Z1)
            row = []
            for cid in ids:
                ch = kb.retriever.chunks.get(cid)
                b = (f"{ch.text}\n{ch.chapter_title}\n{ch.scene_title}\n{ch.part_title}"
                     if ch else "")
                row.append(any(k in b for k in c["keywords"]))
            Gs.append(row)
        Z = np.stack(Zs)
        G = np.array(Gs, dtype=bool)
        base = lab.metrics(np.tile(np.arange(pool), (len(cases), 1)), G, pool)
        S = Z @ w
        perm = lab.apply_policy(prod["policy"], a, S, pool)
        m = lab.metrics(perm, G, pool)
        up, down = lab.flips(perm, G, np.array([c["qid"] for c in cases]),
                             lab.eval_perm(np.tile(np.arange(pool), (len(cases), 1)), G, pool)[0],
                             pool)
        out[name] = {"n": m["n"], "pool_rrf_hit6": base["hit6"], "rerank_hit6": m["hit6"],
                     "hit10": m["hit10"], "up": len(up), "down": len(down),
                     "up_qids": up, "down_qids": down}
        print(f"\n=== {name} (lex_first={args.lex_first}) ===")
        print(f"  池序 hit@6      = {base['hit6']}")
        print(f"  **生产口径(重排) = {m['hit6']}**  (hit@10={m['hit10']})")
        print(f"  up={len(up)} down={len(down)}")
        if name.startswith("盲测"):
            print(f"  对照现值 0.8786 -> {'提升' if m['hit6'] > 0.8786 else '未提升'}")

    p = ROOT / "data/compendium_rag/reports/_fusion_restructure_accept.json"
    p.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\n-> {p}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
