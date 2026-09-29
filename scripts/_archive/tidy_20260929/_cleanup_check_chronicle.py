# -*- coding: utf-8 -*-
"""编年史生成后的质量检查。"""
from pathlib import Path

for f in ("docs/compendium-rag/CHRONICLE.md", "docs/plot-graph-rag/CHRONICLE.md",
          "docs/roleplay-core/CHRONICLE.md", "docs/voice-desktop/CHRONICLE.md",
          "docs/qq/CHRONICLE.md"):
    t = Path(f).read_text(encoding="utf-8")
    dbl = sum(1 for ln in t.splitlines() if ln.startswith("- - "))
    entries = sum(1 for ln in t.splitlines() if ln.startswith("## "))
    srcs = sum(1 for ln in t.splitlines() if ln.startswith("- 来源："))
    print(f"{f:42} 条目={entries:3} 来源={srcs:3} 双项目符号={dbl}")

print()
t = Path("docs/plot-graph-rag/CHRONICLE.md").read_text(encoding="utf-8")
i = t.index("## 2026-09-09")
print("样例条目：")
print(t[i:i + 500])
