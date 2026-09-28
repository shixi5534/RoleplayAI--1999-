# -*- coding: utf-8 -*-
"""验证我对 RRF 的离线复现是否正确（用 collect 工件里已存的 score/reasons 对账）。

若 sum(w/(k+rank)) 能从 reasons 精确重建 score，则我的融合数学与官方一致，
后续离线扫参可信。
"""
from __future__ import annotations

import json
from pathlib import Path

R = Path("data/compendium_rag/reports")
K = 60


def check(fname: str) -> None:
    d = json.loads((R / fname).read_text(encoding="utf-8"))
    rows = [r for r in d["rows"] if r.get("mode") == "full"]
    tot = ok = 0
    worst = 0.0
    for r in rows[:40]:
        for ev in (r.get("evidence") or []):
            s = ev.get("score")
            reasons = ev.get("reasons") or []
            if s is None or not reasons:
                continue
            # reasons 形如 ["graph#1","mention#6"]
            recon = 0.0
            for rs in reasons:
                if "#" not in rs:
                    continue
                _ch, rk = rs.rsplit("#", 1)
                try:
                    recon += 1.0 / (K + int(rk))
                except ValueError:
                    pass
            tot += 1
            if abs(recon - s) < 1e-6:
                ok += 1
            else:
                worst = max(worst, abs(recon - s))
    print(f"  {fname}: 对账 {ok}/{tot} 条一致（最大偏差 {worst:.2e}）")


print("=" * 80)
print("RRF 复现正确性（w=1，k=60，从 reasons 重建 score）")
print("=" * 80)
check("rank_collect_v6c300_top30.json")
check("rank_collect_v6cblind_top30.json")
print()
print("注意：collect 里 channels 的 graph 值是 PPR 原始分（非 RRF 项），")
print("     故 score 只由 reasons 的 (channel,rank) 决定 —— 这正好用于验证融合数学。")
