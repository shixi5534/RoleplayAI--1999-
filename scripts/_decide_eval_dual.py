# -*- coding: utf-8 -*-
"""双口径评测：同时报告「含 gold 缺陷题」与「剔除缺陷题」两套数字。

动机：gold 缺陷题会永久压低基线并误导优化方向，但**剔除它们是"抬分"动作**，
必须显式、可审计、且**两种口径同时给出**（否则等于挑有利数字报告）。

用法：
  python scripts/_decide_eval_dual.py                 # 评 300cn/gen120/blind 当前工件
  python scripts/_decide_eval_dual.py --file X.json   # 评指定 eval 工件
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT / "data/knowledge/_audit"
REG = json.loads((AUDIT / "gold_defects_registry.json").read_text(encoding="utf-8"))
CONSERVATIVE = set(REG["exempt_qids_conservative"])
INCLUSIVE = set(REG["exempt_qids_inclusive"])


def load_rates(f: Path) -> dict:
    d = json.loads(f.read_text(encoding="utf-8"))
    rows = [r for r in d["rows"] if r.get("mode") == "full" and r.get("answerable")]
    return {r["qid"]: bool(r.get("hit")) for r in rows}


def report(label: str, hits: dict[str, bool]) -> None:
    n = len(hits)
    h = sum(1 for v in hits.values() if v)
    # 保守口径：剔除 12 道高置信缺陷
    keep = {q: v for q, v in hits.items() if q not in CONSERVATIVE}
    nk = len(keep)
    hk = sum(1 for v in keep.values() if v)
    # 宽松口径：剔除 15 道
    keep2 = {q: v for q, v in hits.items() if q not in INCLUSIVE}
    nk2 = len(keep2)
    hk2 = sum(1 for v in keep2.values() if v)
    print(f"  {label}")
    print(f"     原始口径      {h:>4}/{n:<4} = {h/n:.4f}")
    if nk:
        print(f"     剔除12(保守)  {hk:>4}/{nk:<4} = {hk/nk:.4f}   "
              f"（豁免 {n-nk} 道，本集实际命中 "
              f"{sum(1 for q in CONSERVATIVE if hits.get(q))} 道）")
    if nk2:
        print(f"     剔除15(宽松)  {hk2:>4}/{nk2:<4} = {hk2/nk2:.4f}")
    print()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--file", default="")
    args = ap.parse_args()

    R = ROOT / "data/compendium_rag/reports"
    print("=" * 88)
    print("双口径报告（gold 缺陷剔除法：保守=12 道 / 宽松=15 道）")
    print("=" * 88)
    print(f"  来源登记表：{REG['kind']} v{REG['version']}  "
          f"（{REG['counting_rule'].splitlines()[0].strip()}）")
    print()

    if args.file:
        report(Path(args.file).name, load_rates(Path(args.file)))
        return 0

    for label, f in [("300cn  (v7, k=1)", "eval_300cn_k1.json"),
                     ("盲测206 (v7, k=1)", "eval_blind_k1.json"),
                     ("泛化120 (v7, k=1)", "eval_gen120_k1.json")]:
        p = R / f
        if p.exists():
            report(label, load_rates(p))
    print("注：盲测/gen120 **不含** gold 缺陷题（缺陷只在 300cn 审计过），")
    print("    故其两列数字相同；此处照实列出以证明未挑口径。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
