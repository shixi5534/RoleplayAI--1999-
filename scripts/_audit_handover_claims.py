# -*- coding: utf-8 -*-
"""独立复核：交接文档（总）§0/§3/§4 的关键数字 vs 磁盘原始 rows。

只读。判据：一律从 rows 的 hit/rr 字段用统一口径（mode + answerable）重算，
再与 baseline_v6.json / 交接文档声称值对账。
"""
from __future__ import annotations

import json
from pathlib import Path

R = Path("data/compendium_rag/reports")


def load(f: str) -> list[dict]:
    return json.loads((R / f).read_text(encoding="utf-8"))["rows"]


def rate(rows: list[dict], mode: str, answerable: bool | None = True) -> tuple[int, int]:
    sel = [r for r in rows if r.get("mode") == mode]
    if answerable is not None:
        sel = [r for r in sel if bool(r.get("answerable")) == answerable]
    return sum(1 for r in sel if r.get("hit")), len(sel)


print("=" * 78)
print("① 300cn 各口径（分母 = answerable 196）")
print("=" * 78)
FILES = {
    "lex=0 (v5)": "eval_300cn_v6_tb_lexoff.json",
    "lex=1 (v6, lex_on)": "eval_300cn_lex_on.json",
    "lex=1 (v6, tiebreak)": "eval_300cn_lex_tiebreak.json",
    "lex=1 + lex_first=3": "eval_300cn_lexfirst.json",
}
CLAIMED = {  # 交接文档 §4 / §0 声称值
    "lex=0 (v5)": ("full", 0.7959),
    "lex=1 (v6, lex_on)": ("full", 0.8418),
    "lex=1 (v6, tiebreak)": ("full", 0.8418),
    "lex=1 + lex_first=3": ("full", 0.8469),
}
for label, f in FILES.items():
    p = R / f
    if not p.exists():
        print(f"  [缺文件] {label:24} {f}")
        continue
    rows = load(f)
    hf, nf = rate(rows, "full", True)
    hg, ng = rate(rows, "graph_only", True)
    hu, nu = rate(rows, "full", False)
    print(f"  {label:24} full {hf}/{nf}={hf/nf:.4f}   graph_only {hg}/{ng}={hg/ng:.4f}"
          f"   unans {hu}/{nu}")
    # 文档是否用「全 mode 命中数 / answerable 分母」造成错配
    hall = sum(1 for r in rows if r.get("mode") == "full" and r.get("hit"))
    if hall != hf:
        print(f"       ⚠ 全 full 命中={hall} 但 answerable 命中={hf}"
              f"（差 {hall-hf} = 不可答题命中）；用 {hall}/{nf}={hall/nf:.4f} 会虚高")

print()
print("=" * 78)
print("② 盲测 206：裸检索 / 生产口径 与两笔不同 run 的区分")
print("=" * 78)
rows = load("eval_blind_lex_on.json")
hb, nb = rate(rows, "full", None)
print(f"  eval_blind_lex_on     盲测裸 full {hb}/{nb} = {hb/nb:.4f}")
rows = load("eval_blind_lex_tiebreak.json")
ht, nt = rate(rows, "full", None)
print(f"  eval_blind_lex_tiebreak 盲测裸 full {ht}/{nt} = {ht/nt:.4f}")

for f, barekey in [("frozen_prod_on_blind.json", "baseline_hit6"),
                   ("frozen_prod_on_blindfinal.json", "baseline_hit6")]:
    p = R / f
    if not p.exists():
        continue
    d = json.loads(p.read_text(encoding="utf-8"))
    for k, v in d.items():
        if k.startswith("blind"):
            print(f"  {f} [{k}] 裸={v[barekey]:.4f} 生产={v['frozen_hit6']:.4f} "
                  f"up={v['up']} down={v['down']}  (n={v['n']})")
acc = json.loads((R / "baseline_v6_acceptance.json").read_text(encoding="utf-8"))
b = acc["blind206 (留出集)"]
print(f"  baseline_v6_acceptance 盲测裸={b['bare_hit6']:.4f} 生产={b['rerank_hit6']:.4f} "
      f"up={b['up']} down={b['down']}")
print(f"      校验 172+{b['up']}-{b['down']} = {172+b['up']-b['down']}/{nb} = "
      f"{(172+b['up']-b['down'])/nb:.4f}")
d2 = json.loads((R / "frozen_prod_on_blindfinal.json").read_text(encoding="utf-8"))["blind_final(206)"]
print(f"      校验 132+{d2['up']}-{d2['down']} = {132+d2['up']-d2['down']}/{d2['n']} = "
      f"{(132+d2['up']-d2['down'])/d2['n']:.4f}")

print()
print("=" * 78)
print("③ lex-only vs 融合（§3.3 与结尾「一句话交接」对账）")
print("=" * 78)
for label, f, mode in [("lex-only 盲测", "eval_blind_lexfirst.json", "full")]:
    pass
print("  文档 §3.3 声称 lex-only=0.9320（192/206）、融合=0.8350（172/206）")
print(f"  192/206 = {192/206:.4f}")
print(f"  172/206 = {172/206:.4f}")
print(f"  171/206 = {171/206:.4f}   <- 结尾「一句话交接」写的 0.8301 对应 171")

print()
print("=" * 78)
print("④ _verify_v6_locks.py 的键->文件映射核对")
print("=" * 78)
import hashlib

lockmap = {
    "graph_live": Path("data/compendium_rag/graph.json"),
    "baseline_v5": R / "baseline_v5.json",
    "eval_300cn_lex_on": R / "eval_300cn_lex_on.json",
    "eval_gen_lex_on": R / "eval_gen_lex_on.json",
    "eval_blind_lex_on": R / "eval_blind_lex_on.json",
    "eval_blind_lex_tiebreak": R / "eval_blind_lex_tiebreak.json",
    # 脚本里把 eval_300cn_lex_off 映射到了 eval_blind_lex_off.json
    "eval_300cn_lex_off (脚本映射)": R / "eval_blind_lex_off.json",
    "eval_300cn_lex_off (名义应为)": R / "eval_300cn_lex_off.json",
}
b6 = json.loads((R / "baseline_v6.json").read_text(encoding="utf-8"))
for k, p in lockmap.items():
    if not p.exists():
        print(f"  [缺失] {k:32} {p.name}")
        continue
    got = hashlib.sha256(p.read_bytes()).hexdigest()[:16]
    want = b6["artifact_sha256_16"].get(k.split(" ")[0], "(未在锁内)")
    print(f"  {k:32} {p.name:32} {got}  锁={want}")
