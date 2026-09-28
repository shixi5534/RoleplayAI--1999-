# -*- coding: utf-8 -*-
"""复核 T2 判定：R005 / R170 的 gold 到底是"假阳性"还是"合法单选证据"？

R127 已确证是假阳性（purification 出自英文哲学引文，与装置无关）。
但 R005（号船）与 R170（玩具盒）**可能**是合法答案 —— 需逐块人工判读上下文。
本脚本只打印上下文供判读，不做判定。
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
chunks = json.loads((ROOT / "data/compendium_rag/chunks.json").read_text(encoding="utf-8"))["chunks"]
blob = {c["chunk_id"]: c for c in chunks}

CASES = {
    "R005": ("号船", "洞穴的囚徒篇的故事主要发生在什么载具上？"),
    "R170": ("玩具盒", "人们向何处去篇里拉普拉斯的重要装置是什么？"),
    "R127": ("purification", "福格先生发明的大型装置是什么？"),
}
for qid, (kw, q) in CASES.items():
    print("=" * 86)
    print(f"{qid}: {q}")
    print(f"  关键词 {kw!r} 的命中块：")
    hits = [cid for cid, c in blob.items() if kw in c["text"]]
    for cid in hits:
        c = blob[cid]
        i = c["text"].find(kw)
        print(f"  --- {cid}  [{c['chapter_title']} / {c.get('scene_title','')}]")
        print(f"      …{c['text'][max(0, i-120):i+160]}…")
    # 检查是否有"语义等价但不同写法"的答案块
    alt = {"R005": ["Rockin", "摇滚苹果号", "摇滚", "载具", "号"],
           "R170": ["玩具箱", "玩具盒", "toy box", "拉普拉斯"],
           "R127": ["雾气净化器", "净化器", "air purifier", "福葛先生"]}
    for a in alt.get(qid, []):
        h = [cid for cid, c in blob.items() if a in c["text"]]
        print(f"  [备选写法] {a!r}: {len(h)} 块 {h[:3]}")
    print()
