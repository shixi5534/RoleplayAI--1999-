# -*- coding: utf-8 -*-
"""读取 ablation 下 link_*.json / vol_base.json，输出语义链接相关对比。"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AB = ROOT / "data" / "knowledge" / "_audit" / "ablation"
OUT = AB / "_link_ab.txt"
ORDER = ["link_base2", "link_min20", "link_min35", "link_min50",
         "link_min35_top10", "link_top10", "link_top20", "vol_base"]
KEYS = ("inject_pass", "strict_pass", "recall", "mrr",
        "avg_returned_chunks", "latency_p50_ms", "latency_p95_ms")
buf: list[str] = []

data: dict[str, dict] = {}
for name in ORDER:
    p = AB / f"{name}.json"
    if p.is_file():
        try:
            s = json.loads(p.read_text(encoding="utf-8")).get("summary") or {}
            data[name] = {k: s.get(k) for k in KEYS}
        except Exception as e:  # noqa: BLE001
            buf.append(f"[warn] {name}: {e}")

base = data.get("link_base2") or data.get("vol_base") or {}
buf.append("=" * 92)
buf.append(f"语义实体链接相关消融（已完成 {len(data)} 轮）｜判定以 inject_pass 为准")
buf.append("=" * 92)
buf.append(f"{'配置':<18}{'inject':>9}{'Δinject':>9}{'strict':>9}{'recall':>9}"
           f"{'返回块':>8}{'p50':>7}{'p95':>7}")
buf.append("-" * 92)
for name in ORDER:
    if name not in data:
        continue
    d = data[name]
    inj = d.get("inject_pass") or 0.0
    delta = inj - (base.get("inject_pass") or 0.0) if base and name != "vol_base" else 0.0
    buf.append(f"{name:<18}{inj:>9.4f}{delta:>+9.4f}"
               f"{(d.get('strict_pass') or 0):>9.4f}{(d.get('recall') or 0):>9.4f}"
               f"{(d.get('avg_returned_chunks') or 0):>8.2f}"
               f"{(d.get('latency_p50_ms') or 0):>7.0f}"
               f"{(d.get('latency_p95_ms') or 0):>7.0f}")
buf.append("-" * 92)
buf.append("基线 vol_base = 生产配置（semantic_link_min=0.0，链接兜底从未执行）")
OUT.write_text("\n".join(buf), encoding="utf-8")
