# -*- coding: utf-8 -*-
"""把分片 C 再切成 3 个小切片（每个约 11 万字），降低子代理读取成本。"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
D = ROOT / "data/knowledge/_audit/blind_v1"
d = json.loads((D / "corpus_C.json").read_text(encoding="utf-8"))
ch = d["chunks"]
n = len(ch)
parts = [ch[: n // 3], ch[n // 3: 2 * n // 3], ch[2 * n // 3:]]
for i, part in enumerate(parts, 1):
    lines = []
    for c in part:
        lines.append(f"===== [{c['chunk_id']}] {c['chapter_title']} / "
                     f"{c.get('part_title','')} / {c.get('scene_title','')} =====")
        lines.append(c["text"])
        lines.append("")
    p = D / f"corpus_C{i}.txt"
    p.write_text("\n".join(lines), encoding="utf-8")
    chars = sum(len(c["text"]) for c in part)
    docs = sorted({c["doc_id"] for c in part})
    print(f"C{i}: chunks={len(part)} chars={chars:,} docs={docs}")
