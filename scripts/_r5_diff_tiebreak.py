# -*- coding: utf-8 -*-
"""逐题对账：tie-break 修复后 vs 冷启动基线（确认修复是**行为保持**的）。

判据（先于结果固定）：
  - 若修复后与「冷启动 after_r3」逐题完全一致 -> 修复消除的只是**暖态任意性**，
    冷启动语义未被改变（这是期望结果：修复把暖态拉回冷态，而非引入第三种语义）；
  - 若出现新翻转 -> 必须逐题列出并归因，不可当噪声。
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
R = ROOT / "data/compendium_rag/reports"


def rows(name: str, mode: str = "full"):
    d = json.loads((R / name).read_text(encoding="utf-8"))
    out = {}
    for r in d["rows"]:
        if r.get("mode") == mode:
            out[str(r.get("qid"))] = r
    return out


def cmp(a_name: str, b_name: str, mode: str = "full") -> None:
    A, B = rows(a_name, mode), rows(b_name, mode)
    keys = sorted(set(A) | set(B))
    flips = [(k, A[k].get("hit"), B[k].get("hit"), A[k].get("rr"), B[k].get("rr"))
             for k in keys if (A[k].get("hit") != B[k].get("hit")
                               or abs((A[k].get("rr") or 0) - (B[k].get("rr") or 0)) > 1e-9)]
    ha = sum(1 for k in A if A[k].get("hit") and A[k].get("answerable"))
    hb = sum(1 for k in B if B[k].get("hit") and B[k].get("answerable"))
    print(f"--- [{mode}] {a_name}  vs  {b_name}")
    print(f"    answerable hit: {ha} -> {hb}   (rows A={len(A)} B={len(B)})")
    print(f"    逐题差异条数: {len(flips)}")
    for k, x, y, xr, yr in flips[:20]:
        print(f"      {k}: hit {x}->{y}   rr {xr}->{yr}")
    if not flips:
        print("    ✓ 逐题零差异（修复行为保持）")


def main() -> int:
    print("=" * 78)
    print("A. tie-break 修复后 vs 冷启动基线（300cn）")
    cmp("eval_300cn_recheck2_postrebuild_20260927.json",
        "eval_300cn_after_tiebreak_20260927.json")
    print()
    print("B. tie-break 修复后 vs 暖态 after_r4（应恰为 R4 声称救回的 3 题翻回）")
    cmp("eval_300cn_after_r4.json", "eval_300cn_after_tiebreak_20260927.json")
    print()
    print("C. graph_only 通道")
    cmp("eval_300cn_recheck2_postrebuild_20260927.json",
        "eval_300cn_after_tiebreak_20260927.json", mode="graph_only")
    print("=" * 78)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
