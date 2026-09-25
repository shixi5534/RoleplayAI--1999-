# -*- coding: utf-8 -*-
"""复核历史评测报告：找出「语义通道静默降级」（hashing 兜底）状态下跑的那些。

判据
    meta.elapsed_s 是最可靠的指示器：
      · bge-m3（ollama）全量 300 题 ≈ 150~205 s   ⇒ 语义通道正常
      · hashing（本地哈希）      ≈ 20 ~ 65 s    ⇒ 语义通道已静默降级
    另：报告 meta.config 里若有 plot_entity_expand_* 也一并列出（便于追溯）。

输出
    按态分组的完整清单 + 每组的 inject_pass，直接标出「哪些结论是在降级态测的」。
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT / "data" / "knowledge" / "_audit"
OUT = AUDIT / "_historical_states.txt"
buf: list[str] = []

rows: list[dict] = []
targets: list[Path] = []
for sub in ("", "ablation", "repeat"):
    d = AUDIT / sub if sub else AUDIT
    if d.is_dir():
        targets.extend(sorted(d.glob("*.json")))
buf.append(f"扫描 {len(targets)} 个 JSON（仅 _audit 顶层 / ablation / repeat）")
for p in targets:
    try:
        if p.stat().st_size > 30 * 1024 * 1024:
            continue
        d = json.loads(p.read_text(encoding="utf-8"))
    except Exception:  # noqa: BLE001
        continue
    if not isinstance(d, dict):      # 有些 JSON 顶层是 list（如名单文件）
        continue
    s = d.get("summary") or {}
    if "inject_pass" not in s:
        continue
    m = d.get("meta") or {}
    el = float(m.get("elapsed_s") or 0)
    rows.append({
        "file": str(p.relative_to(AUDIT)),
        "elapsed": el,
        "state": ("正常(语义开)" if el >= 120 else
                  "降级(语义关)" if 0 < el < 100 else "未知"),
        "inject": s.get("inject_pass"),
        "strict": s.get("strict_pass"),
        "testset": (m.get("assets_sha256_head16") or {}).get("testset", ""),
    })

rows.sort(key=lambda r: r["elapsed"])
buf.append("=" * 96)
buf.append("历史评测报告的批次态复核（elapsed ≥120s = 语义正常；<100s = 语义已静默降级）")
buf.append("=" * 96)
buf.append(f"{'文件':<64}{'elapsed':>9}{'inject':>9}{'态':>12}")
buf.append("-" * 96)
for r in rows:
    buf.append(f"{r['file'][-62:]:<64}{r['elapsed']:>9.1f}{r['inject']:>9.4f}"
               f"{r['state']:>12}")
buf.append("-" * 96)

bad = [r for r in rows if r["state"] == "降级(语义关)"]
buf.append("")
buf.append(f"总计 {len(rows)} 份含 inject_pass 的报告；其中 **降级态 {len(bad)} 份**。")
if bad:
    buf.append("")
    buf.append("⚠️ 降级态报告（其结论**不能**与正常态报告混比）：")
    for r in bad:
        buf.append(f"  · {r['file']}  inject={r['inject']}  elapsed={r['elapsed']:.1f}s")

OUT.write_text("\n".join(buf), encoding="utf-8")
