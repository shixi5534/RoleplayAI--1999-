# -*- coding: utf-8 -*-
"""修正 _lex_channel_full_scan.json 里 selected_on_300cn.n 的误标。

原实现写入了 best[2]（= MRR 之和），而非题数。此处按 300cn answerable 题数订正，
其余字段（含留出集泛化结论）不变。
"""
import json
from pathlib import Path

p = Path("data/compendium_rag/reports/_lex_channel_full_scan.json")
d = json.loads(p.read_text(encoding="utf-8"))

ts = json.loads(Path("data/knowledge/_audit/rag_testset_300_cn.json").read_text(encoding="utf-8"))
chunks = json.loads(Path("data/compendium_rag/chunks.json").read_text(encoding="utf-8"))["chunks"]
blob = "\n".join(c["text"] for c in chunks)
n_ans = 0
for c in ts["cases"]:
    kws = []
    for g in (c.get("evidence") or []):
        items = g if isinstance(g, (list, tuple)) else [g]
        kws.extend(str(x) for x in items if x)
    if kws and any(k in blob for k in kws):
        n_ans += 1

s = d["selected_on_300cn"]
old = s.get("n")
s["n"] = n_ans
s["rate"] = round(s["hit"] / n_ans, 4)
s["_fix_note"] = f"n 原误写为 MRR 之和({old})，已订正为 answerable 题数 {n_ans}"
p.write_text(json.dumps(d, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"[fix] selected_on_300cn: hit={s['hit']} n={s['n']} rate={s['rate']} (原 n={old})")
