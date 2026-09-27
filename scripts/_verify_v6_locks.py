# -*- coding: utf-8 -*-
"""校验 BASELINE_v6 的全部 artifact SHA 是否可复算命中。"""
import hashlib
import json
from pathlib import Path

D = Path("data/compendium_rag")
b = json.loads((D / "reports/baseline_v6.json").read_text(encoding="utf-8"))
ok = True
for k, want in b["artifact_sha256_16"].items():
    # 键名 -> 路径映射
    cands = {
        "graph_live": D / "graph.json",
        "baseline_v5": D / "reports/baseline_v5.json",
        "eval_300cn_lex_on": D / "reports/eval_300cn_lex_on.json",
        "eval_gen_lex_on": D / "reports/eval_gen_lex_on.json",
        "eval_blind_lex_on": D / "reports/eval_blind_lex_on.json",
        "eval_blind_lex_tiebreak": D / "reports/eval_blind_lex_tiebreak.json",
        "eval_300cn_lex_off": D / "reports/eval_blind_lex_off.json",
    }
    p = cands.get(k)
    if p is None or not p.exists():
        print(f"  [MISSING] {k}")
        ok = False
        continue
    got = hashlib.sha256(p.read_bytes()).hexdigest()[:16]
    good = got == want
    ok &= good
    print(f"  [{'OK ' if good else 'BAD'}] {k:28} {got} (lock {want})")
print(f"\n判定: {'全部命中' if ok else '存在不一致'}")

print("\n=== v6 关键数字 ===")
pb, s3, g1 = b["primary_blind"], b["secondary_300cn"], b["generalization_120"]
print(f"  盲测206 生产口径(重排) = {pb['production_rerank_hit6']}  up={pb['up']} down={pb['down']} -> {pb['verdict']}")
print(f"  盲测206 裸检索        = {pb['bare_hit6']['rate']} ({pb['bare_hit6']['hits']}/{pb['bare_hit6']['n']})")
print(f"  300cn  生产口径        = {s3['production_rerank_hit6']}")
print(f"  300cn  裸检索          = {s3['lex_on_bare_hit6']['rate']}")
print(f"  300cn  graph_only      = {s3['lex_on_graph_only']['rate']}")
print(f"  安全线 unanswerable    = {s3['safety_unanswerable']['hits']}/{s3['safety_unanswerable']['n']}")
print(f"  泛化120                = {g1['lex_on_full_hit6']['rate'] if g1.get('lex_on_full_hit6') else g1}")
