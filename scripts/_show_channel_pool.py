# -*- coding: utf-8 -*-
"""汇总 diag_channel_pool.py 的各 tag 结果，输出横向对比表。"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT / "data" / "knowledge" / "_audit"
OUT = AUDIT / "_channel_pool_summary.txt"
SUFFIX = "_v2"   # v1（lf=0）已作废：把词法通道掐掉了
ORDER = ["base", "no_semantic", "no_chapter", "lexical_always", "edges1"]
LABEL = {
    "base": "base（四通道）",
    "no_semantic": "关语义通道",
    "no_chapter": "关篇章路由",
    "lexical_always": "BM25 常开",
    "edges1": "边上限 1（≈停图传播）",
}
buf: list[str] = []

data: dict[str, dict] = {}
for t in ORDER:
    p = AUDIT / f"channel_pool_{t}{SUFFIX}.json"
    if p.is_file():
        try:
            data[t] = json.loads(p.read_text(encoding="utf-8"))
        except Exception as e:  # noqa: BLE001
            buf.append(f"[warn] {t}: {e}")

buf.append("=" * 92)
buf.append(f"通道拆解横向对比（A 类 67 题，生产口径 lf=2；已完成 {len(data)}/{len(ORDER)} 组）")
buf.append("=" * 92)


def pct(d: dict, k: str) -> float:
    n = d.get("n") or 1
    return d.get(k, 0) / n


for scope, key in (("A 类（不在候选池，本轮决策依据）", "a_class"),
                   ("全量 300 题（本轮未跑，见 v1 作废文件）", "all")):
    buf.append("")
    buf.append(f"【{scope}】")
    buf.append(f"{'配置':<22}{'题数':>6}{'任一组在池':>12}{'单块全覆盖':>12}{'平均池深':>10}")
    buf.append("-" * 92)
    base_full = None
    for t in ORDER:
        if t not in data:
            continue
        d = data[t].get(key)
        if not d:
            continue
        if base_full is None:
            base_full = pct(d, "full")
        delta = pct(d, "full") - base_full
        mark = "" if t == "base" else f"   Δ全覆盖 {delta:+.1%}"
        buf.append(f"{LABEL[t]:<22}{d.get('n', 0):>6}{pct(d, 'group_any'):>12.1%}"
                   f"{pct(d, 'full'):>12.1%}{(d.get('pool_sum', 0) / max(d.get('n', 1), 1)):>10.1f}{mark}")
    buf.append("-" * 92)

buf.append("")
buf.append("读法：")
buf.append("  · 某配置让 A 类的「单块全覆盖」明显上升 ⇒ 该通道是瓶颈，配置可救")
buf.append("  · 所有配置都不动 ⇒ 是**查询不匹配**，必须改查询侧（改写 / 领域词典 / 实体链接）")
buf.append("  · 「任一组在池」高而「单块全覆盖」低 ⇒ 证据分散在多块，属多跳题固有难度")

OUT.write_text("\n".join(buf), encoding="utf-8")
