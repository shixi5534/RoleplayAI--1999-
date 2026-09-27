# -*- coding: utf-8 -*-
"""为盲写题的子代理准备**互不重叠**的语料分片文件。

设计要点（保证盲性与可比性）：
  - 每个分片是一个独立 JSON：{chunk_id, chapter_title, part_title, scene_title, text}
  - 分片之间 doc_id 不重叠 -> 子代理看不到彼此的选题面
  - **不提供**现有 300cn 题集、gold、评测脚本 -> 真正的盲写
  - 要求子代理引用**逐字**证据关键词，与既有评测契约（子串命中）一致
"""
from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data/knowledge/_audit/blind_v1"
OUT.mkdir(parents=True, exist_ok=True)

chunks = json.loads((ROOT / "data/compendium_rag/chunks.json").read_text(encoding="utf-8"))["chunks"]
by_doc: dict[str, list[dict]] = defaultdict(list)
for c in chunks:
    by_doc[c["doc_id"]].append(c)

# 分片方案：类别混搭，doc 互斥，每个 agent 覆盖多类别以匹配真实分布
PARTITIONS = {
    "A": ["mainline__104_老虎的金黄", "mainline__108_忧郁的热带",
          "activity__34101_不老春", "activity__11101_雷米特杯失窃案",
          "anecdote__1901_雾行者角色故事", "character__17701_小房间"],
    "B": ["mainline__109_疯癫与文明", "mainline__112_远征记",
          "activity__36101_人们向何处去", "activity__21101_77号往事",
          "anecdote__1906_重返人间", "character__19603_犹在镜中"],
    "C": ["mainline__000_此即明日", "mainline__113_他者的悲哀",
          "activity__18101_再见_来亚什基", "activity__25101_唐人街影话",
          "anecdote__1907_第九条美德", "character__23601_夜游十字街"],
    "D": ["mainline__105_洞穴的囚徒", "mainline__110_复乐园",
          "activity__27101_1987宇宙组曲", "activity__35101_绿松石蛇俱乐部",
          "anecdote__1903_帕米埃角色故事", "character__20601_旧金山小子"],
}

summary = {}
for tag, docs in PARTITIONS.items():
    rows = []
    for d in docs:
        for c in by_doc.get(d, []):
            rows.append({"chunk_id": c["chunk_id"], "doc_id": c["doc_id"],
                         "chapter_title": c["chapter_title"],
                         "part_title": c.get("part_title", ""),
                         "scene_title": c.get("scene_title", ""),
                         "speakers": c.get("speakers", []),
                         "text": c["text"]})
    p = OUT / f"corpus_{tag}.json"
    p.write_text(json.dumps({"tag": tag, "docs": docs, "n_chunks": len(rows),
                             "chunks": rows}, ensure_ascii=False, indent=1),
                 encoding="utf-8")
    chars = sum(len(r["text"]) for r in rows)
    summary[tag] = {"docs": docs, "n_chunks": len(rows), "chars": chars,
                    "file": str(p.relative_to(ROOT))}
    print(f"[{tag}] chunks={len(rows):5} chars={chars:8,} docs={docs}")

(OUT / "_manifest.json").write_text(json.dumps(summary, ensure_ascii=False, indent=1),
                                    encoding="utf-8")
print(f"\n-> {OUT}")
