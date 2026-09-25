# -*- coding: utf-8 -*-
"""决定性对比②：用**真实 registry 持有的 expander**（已 bind_store）生成 query，
与 rag_testset_300_expanded.json 逐题比对文本；不一致的打印出来。

前一次对比用的是**手动新建**的 EntityExpander（没 bind_store），可能漏掉了差异。
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

from roleplay.config import get_settings  # noqa: E402
from roleplay.core.knowledge.factory import build_plot_registry  # noqa: E402

AUDIT = ROOT / "data" / "knowledge" / "_audit"
OUT = AUDIT / "_query_diff.txt"
buf: list[str] = []

clean = json.loads((AUDIT / "rag_testset_300_clean.json").read_text(encoding="utf-8"))
expanded = {str(c["id"]): c for c in
            json.loads((AUDIT / "rag_testset_300_expanded.json")
                       .read_text(encoding="utf-8"))}

s = get_settings()
retr = build_plot_registry(s).get("wu_ming_zhe")
exp = getattr(retr, "entity_expander", None)
buf.append(f"enabled={getattr(s, 'plot_entity_expand_enabled', None)} "
           f"whitelist={getattr(s, 'plot_entity_expand_whitelist', None)} "
           f"expander={type(exp).__name__ if exp else None}")
if exp is not None:
    buf.append(f"  names={len(getattr(exp, 'names', []) or [])} "
               f"map={len(getattr(exp, '_name_map', {}) or {})} "
               f"enforce_whitelist={exp.enforce_whitelist}")
buf.append("")

same = 0
diffs: list[str] = []
n_ext = 0
for c in clean:
    qid = str(c["id"])
    raw = c["q"]
    if exp is None:
        got = raw
    else:
        got = exp.expand(raw)
    want = expanded[qid]["q"]
    if got != raw:
        n_ext += 1
    if got.strip() == want.strip():
        same += 1
    else:
        diffs.append(f"[{qid}]\n    got ={got}\n    want={want}")

buf.append(f"逐题比对：一致 {same}/{len(clean)}｜不一致 {len(diffs)}")
buf.append(f"组件实际扩展题数：{n_ext}")
buf.append(f"expander stats：{getattr(exp, 'stats', None)}")
buf.append("")
for d in diffs[:20]:
    buf.append(d)
if len(diffs) > 20:
    buf.append(f"... 另有 {len(diffs) - 20} 条")

OUT.write_text("\n".join(buf), encoding="utf-8")
