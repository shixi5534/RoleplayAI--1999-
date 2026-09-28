# -*- coding: utf-8 -*-
"""独立复核（第三轮）：锁的覆盖与命名、以及「同代 vs 跨代」增益归因。"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

R = Path("data/compendium_rag/reports")
b = json.loads((R / "baseline_v6.json").read_text(encoding="utf-8"))
keys = sorted(b["artifact_sha256_16"])

print("=" * 88)
print("① BASELINE_v6 锁定键清单")
print("=" * 88)
for k in keys:
    print(f"  {k:28} {b['artifact_sha256_16'][k]}")

print()
print("② 承载头条数字 0.8786 的工件是否在锁内？")
for f in ["baseline_v6_acceptance.json", "rank_rerank_lab_300cn_v6.json",
          "eval_300cn_lex_tiebreak.json", "eval_300cn_lexfirst.json",
          "eval_blind_lexfirst.json"]:
    print(f"  {f:36} exists={(R/f).exists()}  in_lock={f[:-5] in keys}")

print()
print("③ 锁键名 -> 实际文件（按 _verify_v6_locks.py 的映射）")
mapping = {
    "graph_live": Path("data/compendium_rag/graph.json"),
    "baseline_v5": R / "baseline_v5.json",
    "eval_300cn_lex_on": R / "eval_300cn_lex_on.json",
    "eval_gen_lex_on": R / "eval_gen_lex_on.json",
    "eval_blind_lex_on": R / "eval_blind_lex_on.json",
    "eval_blind_lex_tiebreak": R / "eval_blind_lex_tiebreak.json",
    "eval_300cn_lex_off": R / "eval_blind_lex_off.json",
}
for k, p in mapping.items():
    got = hashlib.sha256(p.read_bytes()).hexdigest()[:16]
    flag = "OK " if got == b["artifact_sha256_16"][k] else "BAD"
    warn = ""
    if k == "eval_300cn_lex_off":
        warn = "  <-- 键名说 300cn，实际是盲测文件！真正的 eval_300cn_lex_off.json 不存在"
    print(f"  [{flag}] {k:26} -> {p.name:32}{warn}")

print()
print("=" * 88)
print("④ 词面通道增益的「同代 vs 跨代」归因（300cn full, answerable/196）")
print("=" * 88)


def ans_hit(f: str) -> tuple[int, int]:
    d = json.loads((R / f).read_text(encoding="utf-8"))
    rows = [r for r in d["rows"] if r.get("mode") == "full" and r.get("answerable")]
    return sum(1 for r in rows if r.get("hit")), len(rows)


pre0 = ans_hit("eval_300cn_after_r5.json")          # lex=0, tiebreak 前
post0 = ans_hit("eval_300cn_v6_tb_lexoff.json")     # lex=0, tiebreak 后
on = ans_hit("eval_300cn_lex_tiebreak.json")        # lex=1, tiebreak 后
print(f"  lex=0 tiebreak 前  {pre0[0]}/{pre0[1]} = {pre0[0]/pre0[1]:.4f}  (eval_300cn_after_r5)")
print(f"  lex=0 tiebreak 后  {post0[0]}/{post0[1]} = {post0[0]/post0[1]:.4f}  (eval_300cn_v6_tb_lexoff)")
print(f"  lex=1 tiebreak 后  {on[0]}/{on[1]} = {on[0]/on[1]:.4f}  (eval_300cn_lex_tiebreak)")
print()
print(f"  跨代（文档口径）lex=0 -> lex=1 : {(on[0]-pre0[0])} 题 = "
      f"{(on[0]-pre0[0])/196*100:+.2f}pt   <- 文档写 +4.6pt（156->165）")
print(f"  同代（干净归因）lex=0 -> lex=1 : {(on[0]-post0[0])} 题 = "
      f"{(on[0]-post0[0])/196*100:+.2f}pt   <- 词面通道净贡献")
print(f"  其中 tiebreak 修复自身贡献    : {(post0[0]-pre0[0])} 题 = "
      f"{(post0[0]-pre0[0])/196*100:+.2f}pt")
