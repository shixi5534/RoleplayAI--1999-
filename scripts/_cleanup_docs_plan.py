# -*- coding: utf-8 -*-
"""文档合并决策表（**合并历史过程档，保留当前权威**）。

决策分三类：
  KEEP   —— 当前权威：被代码引用、或仍生效的设计/规范/术语表/当前基线
  MERGE  —— 历史过程档：已完成的一次性报告 → 合入本子系统编年史
  DELETE —— 临时/无内容价值（如 _tmp_voicestat.txt）

本文件是**唯一决策来源**，供 _cleanup_build_chronicle.py 消费；可逐条复核。
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# ── KEEP：当前权威（不合并）──
KEEP: set[str] = set()

# 1) 被代码/脚本引用的（否则会打断核验链）
_refs = ROOT / "data/compendium_rag/reports/_docs_refs.json"
if _refs.exists():
    KEEP |= set(json.loads(_refs.read_text(encoding="utf-8"))["referenced"])

# 2) 仍生效的设计/规范/参考（即便未被代码引用也不合并）
KEEP |= {
    # ── compendium-rag：当前基线 ──
    "docs/compendium-rag/baseline/BASELINE_v6_20260928.md",
    "docs/compendium-rag/baseline/BASELINE_v7_20260928.md",
    # ── plot-graph-rag：规范 / 术语 / 参考数据（长期有效）──
    "docs/plot-graph-rag/acceptance/剧情图谱验收标准.md",
    "docs/plot-graph-rag/corpus/剧情术语对照词表.md",
    "docs/plot-graph-rag/corpus/剧情文件清洗清单.md",
    "docs/plot-graph-rag/corpus/剧情清洗注意事项.md",
    "docs/plot-graph-rag/corpus/剧情时间轴与人物去向图.md",
    "docs/plot-graph-rag/corpus/剧情时间轴与GraphRAG联动.md",
    "docs/plot-graph-rag/graph-governance/wiki-r1999-relation-reference-20260909.md",
    # ── roleplay-core：架构与设计 ──
    "docs/roleplay-core/architecture/ARCHITECTURE.md",
    "docs/roleplay-core/architecture/RAG_SYSTEM_DESIGN.md",
    "docs/roleplay-core/architecture/GRAPHRAG_ENHANCEMENT_PLAN.md",
    "docs/roleplay-core/architecture/class-diagram.mermaid",
    "docs/roleplay-core/architecture/sequence-diagram.mermaid",
    "docs/roleplay-core/profile/user_profile_design.md",
    "docs/roleplay-core/profile/profile-class-diagram.mermaid",
    "docs/roleplay-core/profile/profile-sequence-diagram.mermaid",
    # ── voice-desktop：桌宠 v0.3 设计（当前）＋运行时端点 ──
    "docs/voice-desktop/pet-design/DESKTOP_PET_DESIGN.md",   # ⚠ 运行时端点
    "docs/voice-desktop/pet-design/pet-v0.3-INDEX.md",
    "docs/voice-desktop/pet-design/pet-presentation-spec-v0.3.md",
    "docs/voice-desktop/pet-design/pet-visual-styleboard-v0.3.md",
    "docs/voice-desktop/pet-design/plan-spec-v0.3.md",
    "docs/voice-desktop/pet-design/plan-visual-v0.3.md",
    "docs/voice-desktop/voice/emotion_upgrade_design.md",
    "docs/voice-desktop/voice/语音台词集使用说明.md",
    "docs/voice-desktop/voice/调研-点击触发语音交互规范.md",
    # ── qq：语音方案（被 config.py 引用）──
    "docs/qq/QQ语音回复方案.md",
    # ── 索引 ──
    "docs/README.md",
}

# ── DELETE：临时/无价值 ──
DELETE = {
    "docs/voice-desktop/voice/_tmp_voicestat.txt",
}

# 全部文档
alldocs = {p.relative_to(ROOT).as_posix()
           for p in (ROOT / "docs").rglob("*")
           if p.is_file() and p.suffix in (".md", ".txt", ".mermaid")}

MERGE = sorted(alldocs - KEEP - DELETE)

SUBSYS = ["compendium-rag", "plot-graph-rag", "roleplay-core",
          "voice-desktop", "qq"]

print("=" * 92)
print(f"docs 总数 = {len(alldocs)}")
print(f"  KEEP（当前权威，保留原文件）= {len(KEEP & alldocs)}")
print(f"  MERGE（历史过程档，合入编年史）= {len(MERGE)}")
print(f"  DELETE（临时）= {len(DELETE & alldocs)}")
print("=" * 92)

for s in SUBSYS:
    m = [p for p in MERGE if p.startswith(f"docs/{s}/")]
    k = sorted(p for p in (KEEP & alldocs) if p.startswith(f"docs/{s}/"))
    print(f"\n▶ {s}")
    print(f"    KEEP {len(k)}:")
    for p in k:
        print(f"        {p}")
    print(f"    MERGE {len(m)} → docs/{s}/CHRONICLE.md")

out = ROOT / "data/compendium_rag/reports/_docs_merge_plan.json"
out.write_text(json.dumps({"keep": sorted(KEEP & alldocs),
                           "merge": MERGE,
                           "delete": sorted(DELETE & alldocs)},
                          ensure_ascii=False, indent=1), encoding="utf-8")
print(f"\n-> {out.relative_to(ROOT)}")
