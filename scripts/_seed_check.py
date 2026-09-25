# -*- coding: utf-8 -*-
"""种子敏感性汇总：同一输入在不同 PYTHONHASHSEED 下结果是否一致。

若不一致 ⇒ 检索链路存在非确定性 ⇒ 此前所有"单次运行"的结论都必须补方差区间，
MCNeMar 的 p 值也不再成立（它假设单次确定性测量）。
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REP = ROOT / "data" / "knowledge" / "_audit" / "repeat"
OUT = ROOT / "data" / "knowledge" / "_audit" / "_seed_check.txt"
buf: list[str] = []


def load(n: str) -> dict:
    p = REP / n
    return json.loads(p.read_text(encoding="utf-8")) if p.is_file() else {}


def items(d: dict) -> dict[str, dict]:
    return {str(x.get("id")): x for x in (d.get("items") or [])}


GROUPS = {
    "clean 题集（未扩展）": ["base_1.json", "base_2.json", "base_3.json",
                            "entoff_1.json", "seed_base_1.json", "seed_base_7.json"],
    "expanded 题集（已扩展）": ["expand_1.json", "expand_2.json",
                               "seed_exp_1.json", "seed_exp_7.json",
                               "entnolist_1.json"],
}
KEYS = ("inject_pass", "strict_pass", "recall")

for title, names in GROUPS.items():
    buf.append("=" * 92)
    buf.append(title)
    buf.append("=" * 92)
    buf.append(f"{'运行':<20}{'inject':>10}{'strict':>10}{'recall':>10}{'elapsed':>10}")
    buf.append("-" * 92)
    loaded = {}
    for n in names:
        d = load(n)
        if not d:
            continue
        s = d.get("summary") or {}
        loaded[n] = d
        buf.append(f"{n:<20}{s.get('inject_pass', 0):>10.4f}"
                   f"{s.get('strict_pass', 0):>10.4f}{s.get('recall', 0):>10.4f}"
                   f"{(d.get('meta') or {}).get('elapsed_s', 0):>10.1f}")
    vals = [float((d.get("summary") or {}).get("inject_pass") or 0)
            for d in loaded.values()]
    if vals:
        buf.append("-" * 92)
        buf.append(f"{'极差':<20}{max(vals) - min(vals):>10.4f}")
    # 逐题两两一致率
    if len(loaded) >= 2:
        buf.append("")
        buf.append("逐题 inject 一致率（两两比对）：")
        names2 = list(loaded)
        base_n = names2[0]
        ib = items(loaded[base_n])
        for n in names2[1:]:
            ix = items(loaded[n])
            common = sorted(set(ib) & set(ix))
            same = sum(1 for q in common
                       if bool(ib[q].get("inject_pass")) == bool(ix[q].get("inject_pass")))
            d_ = len(common) - same
            buf.append(f"  {base_n:<18} vs {n:<18} 一致 {same}/{len(common)}"
                       f"｜不同 {d_}")
    buf.append("")

buf.append("=" * 92)
buf.append("判定")
buf.append("=" * 92)
buf.append("若「clean 题集」组极差与逐题差值均为 0，而「expanded 题集」组不为 0，")
buf.append("⇒ 确定性依赖于查询内容：扩展后的查询触发了链路里的顺序敏感分支。")

OUT.write_text("\n".join(buf), encoding="utf-8")
