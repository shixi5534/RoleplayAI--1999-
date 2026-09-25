# -*- coding: utf-8 -*-
"""直接找出两次运行结果不同的题，并打印它们的 query，看是否真的一致。"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT / "data" / "knowledge" / "_audit"
REP = AUDIT / "repeat"
OUT = AUDIT / "_diff_cases.txt"
buf: list[str] = []


def load(n):
    p = REP / n
    return json.loads(p.read_text(encoding="utf-8")) if p.is_file() else {}


a = load("expand_1.json")
b = load("entnolist_1.json")

ia = {str(x.get("id")): x for x in (a.get("items") or [])}
ib = {str(x.get("id")): x for x in (b.get("items") or [])}

buf.append(f"expand_1   items={len(ia)}  inject={(a.get('summary') or {}).get('inject_pass')}")
buf.append(f"entnolist_1 items={len(ib)}  inject={(b.get('summary') or {}).get('inject_pass')}")
buf.append("")

diff_inj = [q for q in sorted(set(ia) & set(ib))
            if bool(ia[q].get("inject_pass")) != bool(ib[q].get("inject_pass"))]
buf.append(f"inject 判定不同的题：{len(diff_inj)} 题")
buf.append("")

buf.append(f"{'id':<8}{'expand':<9}{'entnolist':<11}{'query'}")
buf.append("-" * 100)
for q in diff_inj[:25]:
    buf.append(f"{q:<8}{str(bool(ia[q].get('inject_pass'))):<9}"
               f"{str(bool(ib[q].get('inject_pass'))):<11}{str(ia[q].get('q'))[:60]}")
    buf.append(f"        entnolist 记录的 q：{str(ib[q].get('q'))[:70]}")
if len(diff_inj) > 25:
    buf.append(f"... 另有 {len(diff_inj) - 25} 题")

# 抽查几题的 chunks 数
buf.append("")
buf.append("抽查（前 5 道差异题）的返回块数与 missing_groups：")
for q in diff_inj[:5]:
    buf.append(f"  [{q}] expand: n_chunks={ia[q].get('n_chunks')} "
               f"inject_missing={ia[q].get('inject_missing')} "
               f"injected_chars={ia[q].get('injected_chars')}")
    buf.append(f"        entnolist: n_chunks={ib[q].get('n_chunks')} "
               f"inject_missing={ib[q].get('inject_missing')} "
               f"injected_chars={ib[q].get('injected_chars')}")

OUT.write_text("\n".join(buf), encoding="utf-8")
