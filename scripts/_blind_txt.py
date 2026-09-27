# -*- coding: utf-8 -*-
"""把盲测分片额外导出为**纯文本**，降低子代理读取成本（避免大 JSON 解析失败）。

每个分片输出 corpus_<TAG>.txt：
  ===== [chunk_id] 篇章 / Part / Scene =====
  <正文>
并同时输出一个**分片内人物/专名清单** corpus_<TAG>_names.txt，
帮助出题人快速定位可出题的实体（不含任何 gold/答案）。
"""
from __future__ import annotations

import json
import re
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
D = ROOT / "data/knowledge/_audit/blind_v1"

for tag in ("A", "B", "C", "D"):
    p = D / f"corpus_{tag}.json"
    if not p.exists():
        continue
    d = json.loads(p.read_text(encoding="utf-8"))
    lines = []
    name_counter = Counter()
    for c in d["chunks"]:
        lines.append(f"===== [{c['chunk_id']}] {c['chapter_title']} / "
                     f"{c.get('part_title','')} / {c.get('scene_title','')} =====")
        lines.append(c["text"])
        lines.append("")
        # 粗提专名：**加粗** 与 引号内、以及说话人
        for m in re.findall(r"\*\*(.+?)\*\*", c["text"]):
            name_counter[m.strip()] += 1
        for sp in (c.get("speakers") or []):
            name_counter[str(sp).strip()] += 1
    (D / f"corpus_{tag}.txt").write_text("\n".join(lines), encoding="utf-8")

    names = sorted([n for n, k in name_counter.items() if k >= 2 and 1 < len(n) <= 12],
                   key=lambda n: -name_counter[n])
    (D / f"corpus_{tag}_names.txt").write_text(
        "\n".join(f"{n}\t{name_counter[n]}" for n in names[:400]), encoding="utf-8")
    print(f"[{tag}] txt={len('\n'.join(lines)):,} chars  names={len(names)}")
print("done")
