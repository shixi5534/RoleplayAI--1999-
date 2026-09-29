# -*- coding: utf-8 -*-
"""R6 落盘后逐项核验：与备份对比，证明**只有预期的那一处变化**。"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
A = ROOT / "data/compendium_rag/backups/pre-r4k01/graph.json"
B = ROOT / "data/compendium_rag/graph.json"

a = json.loads(A.read_text(encoding="utf-8"))
b = json.loads(B.read_text(encoding="utf-8"))

print("=" * 76)
print("R6 落盘核验：R4-K01 摘除 诊疗@诊所")
print("=" * 76)
print(f"  SHA16  {hashlib.sha256(A.read_bytes()).hexdigest()[:16]}  ->  "
      f"{hashlib.sha256(B.read_bytes()).hexdigest()[:16]}")
print(f"  entities {len(a['entities'])} -> {len(b['entities'])}")
print(f"  edges    {len(a['edges'])} -> {len(b['edges'])}")

ea = {x["eid"]: x for x in a["entities"]}
eb = {x["eid"]: x for x in b["entities"]}
print(f"  实体集合相同: {set(ea) == set(eb)}")

diff = [k for k in ea if ea[k].get("aliases") != eb[k].get("aliases")]
print(f"  别名有变化的实体 (应恰为 1 个): {diff}")
for k in diff:
    print(f"     {k}: {ea[k].get('aliases')}  ->  {eb[k].get('aliases')}")


def edge_fp(g) -> str:
    s = json.dumps(g["edges"], ensure_ascii=False, sort_keys=True)
    return hashlib.sha256(s.encode()).hexdigest()[:16]


print(f"  边内容指纹: {edge_fp(a)} -> {edge_fp(b)}"
      f"  {'（逐条相同 ✓）' if edge_fp(a) == edge_fp(b) else '（有变化 ✗）'}")
print(f"  别名总数: {sum(len(x.get('aliases') or []) for x in a['entities'])} -> "
      f"{sum(len(x.get('aliases') or []) for x in b['entities'])}")

# 其它字段（描述/类型/块）是否被动过
other = [k for k in ea
         if {kk: vv for kk, vv in ea[k].items() if kk != "aliases"}
         != {kk: vv for kk, vv in eb[k].items() if kk != "aliases"}]
print(f"  除 aliases 外其它字段有变化的实体 (应为 0): {len(other)} {other[:5]}")

ok = (len(a["entities"]) == len(b["entities"]) and len(a["edges"]) == len(b["edges"])
      and set(ea) == set(eb) and diff == ["诊所"] and edge_fp(a) == edge_fp(b)
      and not other)
print()
print("判定:", "只有预期的一处变化 ✓" if ok else "存在非预期变化 ✗")
raise SystemExit(0 if ok else 1)
