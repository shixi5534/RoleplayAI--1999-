# -*- coding: utf-8 -*-
"""核对分类存疑文件的归属（只读，打印头部与判别性证据）。"""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

UNCERTAIN = [
    "docs/compendium-rag/extraction/题集i_预注册与冻结记录.md",
    "docs/plot-graph-rag/eval/全量工作总账_20260917.md",
    "docs/plot-graph-rag/eval/排序靶子_证据块名次分布_20260916.md",
    "docs/plot-graph-rag/eval/召回率归因_20260916.md",
    "docs/plot-graph-rag/eval/RAG召回_多问法改写验证_20260917.md",
    "docs/plot-graph-rag/eval/T4_PPR引导dense标定_20260917.md",
    "docs/plot-graph-rag/eval/RAG测试对接表.md",
    "docs/plot-graph-rag/eval/RAG测试集交接文档.md",
    "docs/plot-graph-rag/eval/题集证据组复核.md",
    "docs/plot-graph-rag/eval/评测批次效应_20260917.md",
    "docs/plot-graph-rag/eval/日内现状快照_20260917.md",
    "docs/plot-graph-rag/eval/RAG召回_文献调研_20260917.md",
    "docs/roleplay-core/architecture/UPGRADE_PLAN.md",
    "docs/voice-desktop/voice/emotion_upgrade_design.md",
    "docs/voice-desktop/voice/_tmp_voicestat.txt",
]

# 判别式：P1 用 7033/30269/3695/compendium/盲测；P2 用 10406/7582/9021/plot/inject_pass
P1 = r"compendium|7033|30269|3695|盲测|blind_v1|rrf_k|lex_first"
P2 = r"plot_|剧情图谱|10406|7582|9021|inject_pass|strict_pass|灰机"

for rel in UNCERTAIN:
    p = ROOT / rel
    if not p.exists():
        print(f"[缺失] {rel}")
        continue
    t = p.read_text(encoding="utf-8", errors="replace")
    n1 = len(re.findall(P1, t))
    n2 = len(re.findall(P2, t))
    verdict = "P1_compendium" if n1 > n2 * 1.5 else ("P2_plot" if n2 > n1 * 1.5 else "?? 需人工")
    lines = [x.strip() for x in t.splitlines() if x.strip()][:5]
    print("=" * 100)
    print(f"{rel}")
    print(f"    P1命中={n1:>4}  P2命中={n2:>4}  -> 判定 {verdict}")
    for ln in lines:
        print(f"      {ln[:135]}")
    print()
