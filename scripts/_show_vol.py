# -*- coding: utf-8 -*-
"""读取已完成的 vol_*.json，输出阶段性对比（跑批过程中也能看）。"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AB = ROOT / "data" / "knowledge" / "_audit" / "ablation"
OUT = AB / "vol_partial.txt"
ORDER = ["base", "sem_top10", "sem_top20", "men_pe10", "men_cap20",
         "edges20", "chap_top6", "link_top6", "combo_s_m"]
KEYS = ("inject_pass", "strict_pass", "recall", "mrr",
        "avg_returned_chunks", "latency_p50_ms", "latency_p95_ms")
buf: list[str] = []

data: dict[str, dict] = {}
for name in ORDER:
    p = AB / f"vol_{name}.json"
    if p.is_file():
        try:
            s = json.loads(p.read_text(encoding="utf-8")).get("summary") or {}
            data[name] = {k: s.get(k) for k in KEYS}
        except Exception as e:  # noqa: BLE001
            buf.append(f"[warn] {name} 读取失败：{e}")

base = data.get("base", {})
buf.append("=" * 92)
buf.append(f"已完成 {len(data)}/{len(ORDER)} 轮｜判定以 inject_pass 为准")
buf.append("=" * 92)
buf.append(f"{'配置':<12}{'inject':>9}{'Δinject':>9}{'strict':>9}{'recall':>9}"
           f"{'MRR':>8}{'返回块':>8}{'p50':>7}{'p95':>7}")
buf.append("-" * 92)
for name in ORDER:
    if name not in data:
        continue
    d = data[name]
    inj = d.get("inject_pass") or 0.0
    delta = inj - (base.get("inject_pass") or 0.0) if base and name != "base" else 0.0
    buf.append(f"{name:<12}{inj:>9.4f}{delta:>+9.4f}"
               f"{(d.get('strict_pass') or 0):>9.4f}{(d.get('recall') or 0):>9.4f}"
               f"{(d.get('mrr') or 0):>8.4f}{(d.get('avg_returned_chunks') or 0):>8.2f}"
               f"{(d.get('latency_p50_ms') or 0):>7.0f}"
               f"{(d.get('latency_p95_ms') or 0):>7.0f}")
buf.append("-" * 92)
buf.append("注：延迟必须与 base 同批次比较（不同批次受 ollama 预热影响）。")
OUT.write_text("\n".join(buf), encoding="utf-8")
