# -*- coding: utf-8 -*-
"""文档归类（精确版）：用**结构性**判别式区分三套并存系统。

为什么不能用内容词：「剧情图谱」与「compendium 正典」同源于《重返未来：1999》，
共享角色名/篇章名，内容词必然串味。故改用结构性证据：

  P1 compendium_rag（正典图谱，当前主线）
     - 代码/数据路径 src/compendium_rag、data/compendium_rag
     - 图规模 7033 / 30269、块 3695、盲测 206
     - 专有物：rrf_k、lex_first、目标①、R1–R5 图谱修复、图谱修复作战书、
       排序侧实验、题集i、正典入库、BASELINE_v*、COMPENDIUM_RAG*
  P2 plot_graph（剧情图谱，前身/并行）
     - src/roleplay/core/knowledge/plot_*.py、data/knowledge/plot_graph_wu_ming_zhe.json
     - 图规模 10406 / 7582、块 9021、指标 inject_pass / strict_pass
     - 专有物：灰机、篇章路由、plot_semantic、PLAN/、T1/T4/…、300 题 RAG 召回
  P3 roleplay_core（lore 向量层 / 角色扮演系统 / 架构）
     - RAG_SYSTEM_DESIGN、GRAPHRAG加强计划书、ARCHITECTURE、UPGRADE_PLAN
     - lore_wu_ming_zhe、VectorStore、persona_prompt、命名空间、角色卡
  P4 voice_desktop（语音与桌宠）
     - Live2D / 语音 / 桌宠 / TTS / 口型 / pet-v0.3
  P5 qq（QQ 通道）
"""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKIP = re.compile(r"[\\/](\.venv|\.git|node_modules|__pycache__|\.pytest|\.idea|vendor|models|logs|_poc_shots|tmp_pytest)[\\/]")

# (项目, 正则, 权重)
RULES: list[tuple[str, str, int]] = [
    # ── P1 compendium_rag ──
    ("P1_compendium", r"compendium_rag|compendium/|COMPENDIUM_RAG", 10),
    ("P1_compendium", r"\b7033\b|\b30269\b|\b3695\b", 10),
    ("P1_compendium", r"盲测\s*206|blind_v1|questions_strict", 8),
    ("P1_compendium", r"rrf_k|lex_first|lex_weight|CMPRAG_", 8),
    ("P1_compendium", r"目标①|正典入库|图谱修复作战书|排序侧实验|题集i|R5\s*落盘|R5\s*立项", 8),
    ("P1_compendium", r"BASELINE_v[2-7]|baseline-v[2-7]", 6),
    ("P1_compendium", r"repairs_v|retrieval\.py|graph_store\.py", 5),
    # ── P2 plot_graph ──
    ("P2_plot", r"plot_graph|plot rag|PlotGraph|plot_semantic|plot_corpus", 10),
    ("P2_plot", r"\b10406\b|\b7582\b|\b9021\b", 10),
    ("P2_plot", r"inject_pass|strict_pass|inject 177|strict 195", 8),
    ("P2_plot", r"灰机|huijiwiki|篇章路由", 6),
    ("P2_plot", r"剧情图谱|剧情抽取|剧情清洗|剧情术语|剧情时间轴", 6),
    ("P2_plot", r"PLAN/|IDEAS_LOG", 5),
    # ── P3 roleplay core ──
    ("P3_core", r"RAG_SYSTEM_DESIGN|GRAPHRAG加强计划书|GRAPHRAG_ENHANCEMENT", 10),
    ("P3_core", r"ARCHITECTURE\.md|UPGRADE_PLAN|lore_wu_ming_zhe", 8),
    ("P3_core", r"VectorStore|persona_prompt|命名空间|lore_<cid>|document_ingest", 6),
    ("P3_core", r"角色卡|roleplay-ai 角色扮演提示词|提示词注入", 5),
    # ── P4 voice/desktop ──
    ("P4_voice", r"Live2D|desktop pet|DESKTOP_PET|pet-v0\.3|桌宠", 10),
    ("P4_voice", r"语音|TTS|口型|VOICE_ITERATION", 6),
    # ── P5 QQ ──
    ("P5_qq", r"QQ_INTEGRATION|QQ语音|OneBot|NapCat", 10),
]

TARGETS: list[Path] = []
for pat in ("docs/**/*", "PLAN/**/*", "deliverables/**/*.md", "*.md",
            "data/docs/*.md", "data/compendium_rag/*.md"):
    TARGETS += [p for p in ROOT.glob(pat)
                if p.is_file()
                and p.suffix.lower() in (".md", ".txt", ".json", ".mermaid")
                and not SKIP.search(str(p))]
TARGETS = sorted(set(TARGETS))

results: list[dict] = []
for p in TARGETS:
    t = p.read_text(encoding="utf-8", errors="replace")
    scores: dict[str, int] = {}
    ev: dict[str, list[str]] = {}
    for cat, rx, w in RULES:
        ms = re.findall(rx, t)
        if ms:
            scores[cat] = scores.get(cat, 0) + w * min(len(ms), 4)
            ev.setdefault(cat, [])[:0] = [m if isinstance(m, str) else str(m) for m in ms[:2]]
    rel = str(p.relative_to(ROOT)).replace("\\", "/")
    if not scores:
        results.append({"path": rel, "cat": "UNKNOWN", "scores": {}, "ev": {}})
        continue
    top = max(scores.values())
    winners = sorted([c for c, s in scores.items() if s == top])
    results.append({"path": rel, "cat": "+".join(winners),
                    "scores": scores, "ev": {k: v for k, v in ev.items() if k in winners}})

by: dict[str, list[dict]] = {}
for r in results:
    by.setdefault(r["cat"], []).append(r)

print(f"扫描 {len(results)} 个文件，{len(by)} 组\n")
for cat in sorted(by, key=lambda c: (-len(by[c]), c)):
    print("=" * 112)
    print(f"[{cat}]  n={len(by[cat])}")
    print("=" * 112)
    for r in by[cat]:
        print(f"  {r['path']:74} {r['scores']}")
    print()

out = ROOT / "data/compendium_rag/reports/_doc_classification.json"
out.write_text(json.dumps(results, ensure_ascii=False, indent=1), encoding="utf-8")
print(f"-> {out}")
