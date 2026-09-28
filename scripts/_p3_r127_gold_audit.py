# -*- coding: utf-8 -*-
"""核查 R127：gold 关键词 "purification" 命中的块，是否真的是题目所问的「装置」？

线索：目标块 mainline__105:13.0.0 里 "purification" 出现在一句**英文哲学引文**中
（"The greatest purification of all is, therefore, science"），与「大型装置」无关。
而此前核验记载 R127 的真实证据是 activity__23101 的「雾气净化器」。

若成立，则 R127 属**测试集 gold 缺陷**（关键词假阳性），不是系统失败。
"""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

chunks = json.loads((ROOT / "data/compendium_rag/chunks.json").read_text(encoding="utf-8"))["chunks"]
blob = {c["chunk_id"]: c for c in chunks}

print("=== A) 含 'purific' 的块 ===")
for cid, c in blob.items():
    if "purific" in c["text"]:
        i = c["text"].find("purific")
        print(f"  {cid}")
        print(f"     …{c['text'][max(0, i-60):i+80]}…")

print("\n=== B) 含 '净化' 的块（装置线索）===")
n = 0
for cid, c in blob.items():
    if "净化" in c["text"]:
        i = c["text"].find("净化")
        print(f"  {cid}: …{c['text'][max(0, i-50):i+70]}…")
        n += 1
        if n >= 12:
            print("  …（截断）")
            break

print("\n=== C) 专项：雾气净化器 / 净化器 ===")
for kw in ("雾气净化器", "净化器", "净化机"):
    hits = [cid for cid, c in blob.items() if kw in c["text"]]
    print(f"  {kw!r}: {len(hits)} 块 -> {hits[:4]}")

ts = json.loads((ROOT / "data/knowledge/_audit/rag_testset_300_cn.json").read_text(encoding="utf-8"))
c127 = next(c for c in ts["cases"] if str(c.get("id")) == "R127")
print("\n=== D) R127 题面与 gold ===")
print(f"  q = {c127['q']}")
print(f"  evidence = {c127['evidence']}")
print(f"  ref = {c127.get('ref','')}")
