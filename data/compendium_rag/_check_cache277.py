# -*- coding: utf-8 -*-
"""只读 cache 溯源(277 号位专用):python _check_cache277.py <名字文件>
_sim_landing 的 obs 来自 cache/,此处报出候选名在 cache 中的出处与 desc,
用于判断并发子代理是否已提交同名实体(§4.6 语义核对)。只读,不写。
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
targets = {l.strip() for l in Path(sys.argv[1]).read_text(encoding="utf-8").splitlines() if l.strip()}
hits = {t: {} for t in targets}
for p in sorted((ROOT / "cache").rglob("*.json")):
    try:
        o = json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        continue
    cid = o.get("chunk_id") or (o.get("raw") or {}).get("chunk_id") or p.stem
    raw = o.get("raw") or {}
    for e in raw.get("entities") or []:
        n = e.get("name")
        if n in targets:
            hits[n].setdefault(cid, set()).add(str(e.get("desc")))
for t in sorted(targets):
    if hits[t]:
        print(f"== {t}")
        for cid, ds in sorted(hits[t].items()):
            print(f"   {cid} :: {';'.join(sorted(ds))}")
    else:
        print(f"-- {t}: cache 无")
