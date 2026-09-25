# -*- coding: utf-8 -*-
"""组件三态校验：关闭=零回归？开启=复现收益？白名单代价多少？"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT / "data" / "knowledge" / "_audit"
REP = AUDIT / "repeat"
OUT = AUDIT / "_component_check.txt"
KEYS = ("inject_pass", "strict_pass", "recall", "mrr", "avg_returned_chunks")
buf: list[str] = []


def load(name: str) -> dict:
    p = REP / name
    return json.loads(p.read_text(encoding="utf-8")) if p.is_file() else {}


def summ(d: dict) -> dict:
    s = d.get("summary") or {}
    return {k: s.get(k) for k in KEYS}


def per_item(d: dict) -> dict[str, dict]:
    out = {}
    for it in d.get("items") or []:
        qid = str(it.get("id") or "")
        if qid:
            out[qid] = {"inject": bool(it.get("inject_pass")),
                        "strict": bool(it.get("strict_pass"))}
    return out


runs = {
    "base（基线）": load("base_1.json"),
    "expand_1（裸拼接，无组件）": load("expand_1.json"),
    "entoff（组件关闭）": load("entoff_1.json"),
    "enton（组件开启+白名单）": load("enton_1.json"),
    "entnolist（组件开启，白名单关）": load("entnolist_1.json"),
}
runs = {k: v for k, v in runs.items() if v}

buf.append("=" * 88)
buf.append("组件三态校验")
buf.append("=" * 88)
buf.append(f"{'运行':<30}{'inject':>10}{'strict':>10}{'recall':>10}{'MRR':>9}{'返回块':>9}")
buf.append("-" * 88)
for k, v in runs.items():
    s = summ(v)
    buf.append(f"{k:<30}{s['inject_pass']:>10.4f}{s['strict_pass']:>10.4f}"
               f"{s['recall']:>10.4f}{s['mrr']:>9.4f}"
               f"{s['avg_returned_chunks']:>9.2f}")
buf.append("=" * 88)

# —— 零回归校验：组件关闭 vs 基线，逐题比对 ——
b, off = runs.get("base（基线）"), runs.get("entoff（组件关闭）")
if b and off:
    ib, io = per_item(b), per_item(off)
    common = set(ib) & set(io)
    diff = [q for q in common if ib[q] != io[q]]
    same = all(summ(b)[k] == summ(off)[k] for k in KEYS)
    buf.append("")
    buf.append("① 零回归校验（组件关闭 vs 基线）")
    buf.append(f"   汇总指标逐项相同：{'✅ 是' if same else '❌ 否'}")
    buf.append(f"   逐题比对：{len(common)} 题中不一致 {len(diff)} 题 "
               f"{'✅ 零回归' if not diff else '❌ 有回归：' + str(diff[:8])}")

# —— 端到端复现 ——
on, nolist = runs.get("enton（组件开启+白名单）"), runs.get("entnolist（组件开启，白名单关）")
raw = runs.get("expand_1（裸拼接，无组件）")
if b and on:
    sb, so = summ(b), summ(on)
    buf.append("")
    buf.append("② 端到端复现（组件开启 + 白名单）")
    buf.append(f"   inject {sb['inject_pass']:.4f} → {so['inject_pass']:.4f} "
               f"({so['inject_pass'] - sb['inject_pass']:+.4f})")
    buf.append(f"   strict {sb['strict_pass']:.4f} → {so['strict_pass']:.4f} "
               f"({so['strict_pass'] - sb['strict_pass']:+.4f})")
if b and nolist:
    sn = summ(nolist)
    buf.append("")
    buf.append("③ 白名单代价（白名单关 vs 开）")
    so = summ(on) if on else {}
    if so:
        buf.append(f"   打开白名单 inject {so['inject_pass']:.4f}｜"
                   f"关闭白名单 inject {sn['inject_pass']:.4f}｜"
                   f"差 {sn['inject_pass'] - so['inject_pass']:+.4f}")
        buf.append(f"   （白名单是防线 1：关掉等于让模型自由发挥，不建议）")
if raw and on and b:
    sr = summ(raw)
    buf.append("")
    buf.append("④ 与「裸拼接」对照（验证白名单是否损失了收益）")
    buf.append(f"   裸拼接（无校验）inject {sr['inject_pass']:.4f}｜"
               f"组件+白名单 {summ(on)['inject_pass']:.4f}｜"
               f"差 {summ(on)['inject_pass'] - sr['inject_pass']:+.4f}")

buf.append("")
buf.append("=" * 88)
OUT.write_text("\n".join(buf), encoding="utf-8")
