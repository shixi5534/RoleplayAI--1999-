# -*- coding: utf-8 -*-
"""决定性对比：同一题，走「题集已扩展」vs「组件内部扩展」，返回块是否一致。

若返回块一致 ⇒ 两次运行结果不同必是别的环节（配置/口径）问题；
若不一致 ⇒ 组件的 expand 与题集拼接在**检索行为**上并非等价（例如扩展后
查询被下游按不同长度处理）。
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

import eval_plot_rag as E  # noqa: E402
from roleplay.config import get_settings  # noqa: E402
from roleplay.core.knowledge.factory import build_plot_registry  # noqa: E402

AUDIT = ROOT / "data" / "knowledge" / "_audit"
OUT = AUDIT / "_path_compare.txt"
buf: list[str] = []

clean = {str(c["id"]): c for c in
         json.loads((AUDIT / "rag_testset_300_clean.json").read_text(encoding="utf-8"))}
expanded = {str(c["id"]): c for c in
            json.loads((AUDIT / "rag_testset_300_expanded.json").read_text(encoding="utf-8"))}
rank = json.loads((AUDIT / "positive_rank.json").read_text(encoding="utf-8"))
a_ids = [str(r["id"]) for r in rank if r.get("verdict") == "A_不在候选池"][:8]

s = get_settings()
retr = build_plot_registry(s).get("wu_ming_zhe")
exp = getattr(retr, "entity_expander", None)
buf.append(f"环境：enabled={getattr(s, 'plot_entity_expand_enabled', None)} "
           f"whitelist={getattr(s, 'plot_entity_expand_whitelist', None)} "
           f"expander={type(exp).__name__ if exp else None}")
buf.append("")

for qid in a_ids:
    q_raw = clean[qid]["q"]
    q_exp = expanded[qid]["q"]
    # 路径 A：题集里已经是扩展后的 query（组件此刻若开着会再扩展一次，故临时关闭）
    saved = retr.entity_expander
    retr.entity_expander = None
    ch_a = retr.retrieve(q_exp, top_chunks=6, lexical_fallback=2)
    # 路径 B：题集是原始 query，由组件内部扩展
    retr.entity_expander = saved
    ch_b = retr.retrieve(q_raw, top_chunks=6, lexical_fallback=2)
    ha = [E.chunk_hash(c.text) for c in ch_a]
    hb = [E.chunk_hash(c.text) for c in ch_b]
    same = ha == hb
    buf.append(f"[{qid}] {'✅ 一致' if same else '❌ 不一致'}")
    buf.append(f"    扩展后 query：{q_exp}")
    buf.append(f"    路径A（题集扩展）块数 {len(ha)}｜路径B（组件扩展）块数 {len(hb)}"
               f"｜重合 {len(set(ha) & set(hb))}")
    if not same:
        for i, (x, y) in enumerate(zip(ha, hb), 1):
            if x != y:
                buf.append(f"      第 {i} 块不同：A={x[:12]} B={y[:12]}")
                break
retr.entity_expander = saved if 'saved' in dir() else None

OUT.write_text("\n".join(buf), encoding="utf-8")
