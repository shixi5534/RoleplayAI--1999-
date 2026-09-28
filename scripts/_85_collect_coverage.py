# -*- coding: utf-8 -*-
"""能否**只凭既有 collect 工件**离线重放 lex_first？—— 覆盖度检验。

collect 的每条 evidence 带 reasons（如 "lex#7"），因此池内块的 lex 名次可复原。
lex_first 需要 lex 前 L 名的**完整名单**；若 lex#1..L 恰好都在池内，即可完整重放。

本脚本测出「lex 前 L 名有多少比例落在池内」，判断能否免去重算通道。
"""
from __future__ import annotations

import json
from pathlib import Path

R = Path("data/compendium_rag/reports")


def coverage(fname: str) -> None:
    d = json.loads((R / fname).read_text(encoding="utf-8"))
    rows = [r for r in d["rows"] if r.get("mode") == "full"]
    print(f"\n  {fname}  (full rows={len(rows)})")
    for L in (1, 2, 3, 4, 5, 6):
        miss_any = 0
        total = 0
        for r in rows:
            ev = r.get("evidence") or []
            lex_ranks = {}
            for e in ev:
                for rs in (e.get("reasons") or []):
                    if rs.startswith("lex#"):
                        try:
                            lex_ranks[int(rs.split("#")[1])] = e["chunk_id"]
                        except ValueError:
                            pass
            total += 1
            if any(i not in lex_ranks for i in range(1, L + 1)):
                miss_any += 1
        print(f"    L={L}: 有 {total-miss_any}/{total} 题的 lex 前 {L} 名**全在池内**"
              f"（可完整重放）；{miss_any} 题不完整")

    # lex 覆盖的池内块数统计
    sizes = []
    for r in rows:
        ev = r.get("evidence") or []
        n = sum(1 for e in ev if any(rs.startswith("lex#") for rs in (e.get("reasons") or [])))
        sizes.append(n)
    sizes.sort()
    print(f"    池内带 lex 名次的块数：min={sizes[0]} 中位={sizes[len(sizes)//2]} max={sizes[-1]}")


print("=" * 84)
print("既存 collect 工件对 lex 通道的覆盖度（决定能否免重算）")
print("=" * 84)
coverage("rank_collect_v6c300_top30.json")
coverage("rank_collect_v6cblind_top30.json")
