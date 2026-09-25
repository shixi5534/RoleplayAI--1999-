# -*- coding: utf-8 -*-
"""诊断单个 evidence 未命中:python _diag_ev.py <号位> <关键词>"""
import json
import sys
from pathlib import Path

R = Path(__file__).resolve().parent
slot, kw = sys.argv[1], sys.argv[2]
dump = {}
for l in (R / f"_dump{slot}.txt").read_text(encoding="utf-8-sig").splitlines():
    if l.strip():
        o = json.loads(l)
        dump[o["key"]] = o["text"]
b = json.loads((R / f"_agent_batch{slot}.json").read_text(encoding="utf-8"))
for k, blk in b.items():
    for r in blk.get("relations") or []:
        e = r.get("evidence") or ""
        if kw not in e and kw not in dump.get(k, ""):
            continue
        t = dump.get(k, "")
        print(f"key={k} {r.get('src')}-{r.get('rel')}>{r.get('dst')}")
        print(f"  ev={e!r} len={len(e)} 命中={e in t}")
        i = t.find(kw)
        if i >= 0:
            print(f"  ctx={t[max(0, i - 30):i + 30]!r}")
