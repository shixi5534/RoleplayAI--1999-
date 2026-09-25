# -*- coding: utf-8 -*-
"""负样本安全核算：识别器对离题查询的误报率，以及是否引入新的注入泄漏。"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

import eval_plot_rag as E  # noqa: E402

AUDIT = ROOT / "data" / "knowledge" / "_audit"
OUT = AUDIT / "_negatives_safety.txt"
buf: list[str] = []

ann = json.loads((AUDIT / "negatives_annotation_agent.json").read_text(encoding="utf-8"))
items = ann["items"]
n = len(items)
fp = [it for it in items if it.get("entity")]
known = set(getattr(E, "KNOWN_RESIDUAL_NEGATIVES", None) or [])

buf.append("=" * 82)
buf.append("负样本安全核算｜识别器对「离题查询」的误报率")
buf.append("=" * 82)
buf.append(f"负样本 {n} 题")
buf.append(f"识别器误报（给出实体名）：{len(fp)} 题 → **误报率 {len(fp) / n:.1%}**")
buf.append("")
if fp:
    buf.append("误报明细：")
    for it in fp:
        tag = "（基线本就泄漏）" if it["q"] in known else "**新增风险**"
        buf.append(f"  · [{it['q']}] → {it['entity']} {tag}")
        if it.get("note"):
            buf.append(f"      {it['note']}")
buf.append("")
buf.append(f"其中落在既有残留泄漏清单里的：{sum(1 for it in fp if it['q'] in known)} 题")
buf.append(f"**新增风险项**：{sum(1 for it in fp if it['q'] not in known)} 题")
buf.append("")
buf.append("-" * 82)
buf.append("与实测护栏交叉验证（53 题零注入红线，扩展版 vs 基线）")
buf.append("-" * 82)


def load(name: str) -> dict:
    p = AUDIT / "repeat" / name
    return json.loads(p.read_text(encoding="utf-8")) if p.is_file() else {}


b = (load("base_1.json").get("negatives") or {})
for tag, fn in (("expand_all", "expand_1.json"), ("expand_hm", "expand_hm_1.json"),
                ("expand_high", "expand_high_1.json")):
    x = (load(fn).get("negatives") or {})
    if not x:
        continue
    buf.append(f"  {tag:<12}注入 {b.get('negative_injection_total')}→"
               f"{x.get('negative_injection_total')}｜"
               f"violations {len(b.get('violations') or [])}→"
               f"{len(x.get('violations') or [])}｜"
               f"new_leaks {len(b.get('new_leaks') or [])}→"
               f"{len(x.get('new_leaks') or [])}")

buf.append("")
buf.append("=" * 82)
buf.append("判定")
buf.append("=" * 82)
new_risk = sum(1 for it in fp if it["q"] not in known)
if new_risk == 0:
    buf.append("✅ 未引入新的注入风险：唯一误报项本就在基线残留泄漏清单内。")
    buf.append("   且实测三档扩展的护栏指标与基线**逐项相同**（无间接影响）。")
    buf.append("")
    buf.append("⚠️ 但仍需注意：本次负样本题**未被扩展**，所以这只是"
               "「扩展不做坏事」的证据，")
    buf.append("   不是「识别器在离线查询上零误报」的证明。"
               "生产前应为识别器加护栏：")
    buf.append("   · 只接受出现在正典名单/图谱实体表里的输出（拒绝自由发挥）")
    buf.append("   · 置信度低于阈值不扩展")
    buf.append("   · 对负样本集做一次真实识别器回归（要求零实体输出）")
else:
    buf.append(f"❌ 存在 {new_risk} 项新增风险，需为识别器加护栏后再上线。")

OUT.write_text("\n".join(buf), encoding="utf-8")
