# -*- coding: utf-8 -*-
"""定位矛盾：为什么「组件+白名单关」不等于「裸拼接」？

逐题打印两者生成的 query，找出差异来源。
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

from roleplay.core.knowledge.plot_entity_expand import (  # noqa: E402
    EntityExpander, StaticMapIdentifier,
)

AUDIT = ROOT / "data" / "knowledge" / "_audit"
OUT = AUDIT / "_entity_component_debug.txt"
buf: list[str] = []

clean = json.loads((AUDIT / "rag_testset_300_clean.json").read_text(encoding="utf-8"))
expanded = {str(c["id"]): c for c in
            json.loads((AUDIT / "rag_testset_300_expanded.json")
                       .read_text(encoding="utf-8"))}
MAP = AUDIT / "entity_expand_map.json"
m = json.loads(MAP.read_text(encoding="utf-8"))["map"]

buf.append(f"静态映射条目 {len(m)} 条")
buf.append("")

ident = StaticMapIdentifier(MAP)
same = diff = missed = 0
buf.append(f"{'id':<8}{'组件生成':<34}{'裸拼接':<34}{'一致'}")
buf.append("-" * 88)
for c in clean:
    qid = str(c["id"])
    raw_q = c["q"]
    # 组件路径（白名单关 = 原样透传）
    exp = EntityExpander(identifier=ident, enforce_whitelist=False, top_k=3, max_append=4)
    got = exp.expand(raw_q)
    # 裸拼接路径
    want = expanded.get(qid, {}).get("q", raw_q)
    ok = got.strip() == want.strip()
    if want.strip() == raw_q.strip():
        if got.strip() == raw_q.strip():
            same += 1
        else:
            diff += 1
            buf.append(f"{qid:<8}{got[:32]:<34}{want[:32]:<34}❌ 组件多拼了")
    else:
        if ok:
            same += 1
        else:
            diff += 1
            buf.append(f"{qid:<8}{got[-32:]:<34}{want[-32:]:<34}❌ 不一致")
buf.append("-" * 88)
buf.append(f"一致 {same}｜不一致 {diff}")
buf.append("")

# 直接查映射命中情况
hit = 0
for c in clean:
    if ident.identify(c["q"], []):
        hit += 1
buf.append(f"静态映射能命中的题数：{hit}/{len(clean)}")
loc = sum(1 for c in clean if str(c["id"]) in
          {str(x["id"]) for x in json.loads((AUDIT / "positive_rank.json").read_text(encoding="utf-8"))
           if x.get("verdict") == "A_不在候选池"})
buf.append(f"A 类题数：{loc}")
buf.append("")
buf.append(f"组件统计（最后一次）：{exp.stats}")

OUT.write_text("\n".join(buf), encoding="utf-8")
