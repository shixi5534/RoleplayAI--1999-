# -*- coding: utf-8 -*-
"""比对 expand_1（旧代码）与 expand_2（新代码）的逐题 query 与判定，定位差异来源。"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REP = ROOT / "data" / "knowledge" / "_audit" / "repeat"
OUT = ROOT / "data" / "knowledge" / "_audit" / "_exp12_diff.txt"
buf: list[str] = []


def load(n):
    p = REP / n
    return json.loads(p.read_text(encoding="utf-8")) if p.is_file() else {}


a, b = load("expand_1.json"), load("expand_2.json")
ia = {str(x.get("id")): x for x in (a.get("items") or [])}
ib = {str(x.get("id")): x for x in (b.get("items") or [])}

buf.append(f"expand_1 inject={(a.get('summary') or {}).get('inject_pass')} "
           f"recall={(a.get('summary') or {}).get('recall')}")
buf.append(f"expand_2 inject={(b.get('summary') or {}).get('inject_pass')} "
           f"recall={(b.get('summary') or {}).get('recall')}")
buf.append("")

q_diff = [q for q in sorted(set(ia) & set(ib))
          if str(ia[q].get("q")) != str(ib[q].get("q"))]
res_diff = [q for q in sorted(set(ia) & set(ib))
            if bool(ia[q].get("inject_pass")) != bool(ib[q].get("inject_pass"))]
buf.append(f"q 字段不同的题：{len(q_diff)}")
buf.append(f"inject 判定不同的题：{len(res_diff)}")
buf.append("")
for q in res_diff[:12]:
    buf.append(f"[{q}]")
    buf.append(f"    expand_1 q={str(ia[q].get('q'))[:70]}")
    buf.append(f"    expand_2 q={str(ib[q].get('q'))[:70]}")
    buf.append(f"    expand_1 inject={ia[q].get('inject_pass')} "
               f"n_chunks={ia[q].get('n_chunks')} miss={ia[q].get('inject_missing')}")
    buf.append(f"    expand_2 inject={ib[q].get('inject_pass')} "
               f"n_chunks={ib[q].get('n_chunks')} miss={ib[q].get('inject_missing')}")

# 也看看 meta 里的语料/测试集指纹
for tag, d in (("expand_1", a), ("expand_2", b)):
    m = d.get("meta") or {}
    buf.append(f"{tag} assets={m.get('assets_sha256_head16')} "
               f"elapsed={m.get('elapsed_s')} trace={m.get('trace_enabled')}")

OUT.write_text("\n".join(buf), encoding="utf-8")
