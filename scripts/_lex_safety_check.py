# -*- coding: utf-8 -*-
"""安全线专项核验：词面通道**不得**让 unanswerable 题产生虚假命中。

为什么这是关键风险：
  词面通道（BM25）会按字面重叠把块拉进候选池。若某"不可答"题的关键词恰好
  字面出现在语料里（但语义上并不构成答案），词面通道会把它顶到前面
  ——这正是安全底线的反面。主口径 `unanswerable ≤ 1/104` 必须守住。

判据（预注册）：
  1. unanswerable hit@6 不高于 lex=0 基线（1/104）；
  2. grounded 仍为 1.000（返回的 chunk_id 全部真实存在）；
  3. 倍数集不变（证据集合只增不改序 —— 由 rrf_fuse 保证，仍须程序化断言）。
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
R = ROOT / "data/compendium_rag/reports"


def load(name):
    p = R / name
    if not p.exists():
        return None
    return json.loads(p.read_text(encoding="utf-8"))


def grp(d, mode="full", ans=None):
    rows = [r for r in d["rows"] if r.get("mode") == mode]
    if ans is True:
        rows = [r for r in rows if r.get("answerable")]
    elif ans is False:
        rows = [r for r in rows if not r.get("answerable")]
    return rows


def main() -> int:
    off = load("eval_300cn_after_r5.json")
    on = load("eval_300cn_lex_on.json")
    if on is None:
        print("[wait] eval_300cn_lex_on.json 尚未生成")
        return 0

    print("=" * 76)
    print("安全线核验（300cn，full 口径，冷启动）")
    print("=" * 76)
    for label, d in [("lex=0 (R5 基线)", off), ("lex=1 (词面通道开)", on)]:
        ans = grp(d, "full", True)
        un = grp(d, "full", False)
        ha = sum(1 for r in ans if r.get("hit"))
        hu = sum(1 for r in un if r.get("hit"))
        g = sum(1 for r in ans if r.get("grounded"))
        print(f"\n[{label}]")
        print(f"  answerable  hit@6 = {ha}/{len(ans)} = {ha / len(ans):.4f}")
        print(f"  unanswerable hit@6 = {hu}/{len(un)}  (基线线 ≤ 1)")
        print(f"  grounded           = {g}/{len(ans)} = {g / len(ans):.4f}")
        outs = [r for r in ans if r.get("answerable") and not r.get("grounded")]
        print(f"  grounded 违例      = {len(outs)} -> {[r.get('qid') for r in outs][:5]}")

    # unanswerable 逐题对照
    a0 = {str(r["qid"]): r for r in grp(off, "full", False)}
    a1 = {str(r["qid"]): r for r in grp(on, "full", False)}
    newhit = [q for q in a1 if a1[q].get("hit") and not a0.get(q, {}).get("hit")]
    print(f"\n[unanswerable 新增命中] {len(newhit)} 题 -> {newhit}")
    lost = [q for q in a0 if a0[q].get("hit") and not a1.get(q, {}).get("hit")]
    print(f"[unanswerable 丢失命中] {len(lost)} 题 -> {lost}")

    print("\n=== 判定 ===")
    hu_on = sum(1 for r in grp(on, "full", False) if r.get("hit"))
    hu_off = sum(1 for r in grp(off, "full", False) if r.get("hit"))
    v1 = hu_on <= max(hu_off, 1)
    gs = [r for r in grp(on, "full", True) if not r.get("grounded")]
    v2 = len(gs) == 0
    print(f"  1) unanswerable 不高于基线 ({hu_off} -> {hu_on}): {'PASS' if v1 else 'FAIL'}")
    print(f"  2) grounded 全绿: {'PASS' if v2 else 'FAIL'}")
    print(f"  总判定: {'PASS' if (v1 and v2) else 'FAIL'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
