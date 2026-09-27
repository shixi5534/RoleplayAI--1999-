# -*- coding: utf-8 -*-
"""对照：RRF 次级键修复对既有结果的影响（是否行为保持）。

判据（预注册）：
  - 若 300cn/盲测 hit@6 与修复前**相同** -> 修复只消除任意性，不改变语义（期望）；
  - 若不同 -> 逐题列出翻转，说明原先是"任意选择"在影响指标。
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
R = ROOT / "data/compendium_rag/reports"


def load(p):
    fp = R / p
    return json.loads(fp.read_text(encoding="utf-8")) if fp.exists() else None


def rates(d, mode="full"):
    if d is None:
        return None
    rows = [r for r in d["rows"] if r.get("mode") == mode and r.get("answerable")]
    h = sum(1 for r in rows if r.get("hit"))
    return h, len(rows)


def main() -> int:
    pairs = [
        ("300cn (lex=1)", "eval_300cn_lex_on.json", "eval_300cn_lex_tiebreak.json"),
        ("盲测 206 (lex=1)", "eval_blind_lex_on.json", "eval_blind_lex_tiebreak.json"),
    ]
    for label, before, after in pairs:
        db, da = load(before), load(after)
        if da is None:
            print(f"[wait] {after} 未生成")
            continue
        rb, ra = rates(db), rates(da)
        print(f"\n=== {label} ===")
        print(f"  修复前 hit@6 = {rb[0]}/{rb[1]} = {rb[0] / rb[1]:.4f}")
        print(f"  修复后 hit@6 = {ra[0]}/{ra[1]} = {ra[0] / ra[1]:.4f}")
        b = {str(r["qid"]): r for r in db["rows"] if r.get("mode") == "full"}
        a = {str(r["qid"]): r for r in da["rows"] if r.get("mode") == "full"}
        up = [q for q in a if a[q].get("hit") and not b.get(q, {}).get("hit")]
        dn = [q for q in b if b[q].get("hit") and not a.get(q, {}).get("hit")]
        rrdiff = [q for q in a if q in b and abs((a[q].get("rr") or 0) - (b[q].get("rr") or 0)) > 1e-9]
        print(f"  up={len(up)} {sorted(up)[:8]}")
        print(f"  down={len(dn)} {sorted(dn)[:8]}")
        print(f"  rr 变化条数 = {len(rrdiff)}")
        same = rb == ra and not up and not dn
        print(f"  判定: {'行为保持（仅消除任意性）' if same else '指标有变化（需归因）'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
