# -*- coding: utf-8 -*-
"""按「项目指纹」自动分类文档（只读，不改动任何文件）。

三个 RAG/系统的判别性特征：
  A. compendium_rag（正典图谱）   : 7033 / 30269 / 3695 块 / compendium / 正典 / 盲测206
  B. plot_graph（剧情图谱）        : 10406 / 7582 / 9021 块 / plot_graph / 灰机 / 篇章路由
  C. roleplay core（lore 向量层）  : lore_wu_ming_zhe / VectorStore / persona_prompt / 角色卡
  D. 语音与桌宠                    : Live2D / TTS / 桌宠 / VoiceIteration
  E. 提示词优化                    : ROLEPLAY_PROMPT / persona prompt
"""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKIP = re.compile(r"[\\/](\.venv|\.git|node_modules|__pycache__|\.pytest|\.idea|vendor|models|logs|_poc_shots)[\\/]")

# 权重：命中即加分。按"最具体 → 最泛"排序。
RULES: list[tuple[str, str, int]] = [
    ("A_compendium", r"compendium|正典入库|COMPENDIUM_RAG|7033|30269|3695 块|3695块|盲测 206|盲测206", 3),
    ("A_compendium", r"目标①|R5 定向|R5立项|R4-K01|插入序|tiebreak|rrf_k|lex_first", 3),
    ("B_plot", r"剧情图谱|plot_graph|plot rag|PlotGraph|10406|7582|9021", 3),
    ("B_plot", r"灰机|huijiwiki|篇章路由|多跳覆盖|plot_semantic", 2),
    ("C_core_lore", r"lore_wu_ming_zhe|lore 向量|lore层|VectorStore|EmbedderPort|persona_prompt", 3),
    ("C_core_lore", r"命名空间|namespace|lore_<cid>|episodic", 1),
    ("D_voice", r"Live2D|TTS|语音|桌宠|desktop pet|DESKTOP_PET|VoiceIteration|口型|lip", 3),
    ("E_prompt", r"ROLEPLAY_PROMPT|提示词注入|persona prompt|角色扮演提示词", 3),
    ("F_qq", r"QQ 机器人|QQ_INTEGRATION|OneBot|napcat", 3),
]

TARGETS: list[Path] = []
for pat in ("docs/**/*.md", "docs/**/*.txt", "PLAN/*", "deliverables/**/*.md",
            "*.md", "data/docs/*.md", "data/compendium_rag/*.md"):
    TARGETS += [p for p in ROOT.glob(pat) if p.is_file() and not SKIP.search(str(p))]
TARGETS = sorted(set(TARGETS))

buckets: dict[str, list[tuple[str, list]]] = {}
for p in TARGETS:
    t = p.read_text(encoding="utf-8", errors="replace")
    scores: dict[str, int] = {}
    for cat, rx, w in RULES:
        n = len(re.findall(rx, t))
        if n:
            scores[cat] = scores.get(cat, 0) + w * min(n, 5)
    rel = str(p.relative_to(ROOT)).replace("\\", "/")
    if not scores:
        buckets.setdefault("Z_unknown", []).append((rel, []))
        continue
    top = max(scores.values())
    winners = sorted([c for c, s in scores.items() if s == top])
    buckets.setdefault("+".join(winners), []).append(
        (rel, sorted(scores.items(), key=lambda kv: -kv[1])[:3]))

print(f"扫描 {len(TARGETS)} 个文件，得到 {len(buckets)} 个分组\n")
for cat in sorted(buckets, key=lambda c: (-len(buckets[c]), c)):
    rows = buckets[cat]
    print("=" * 104)
    print(f"[{cat}]  n={len(rows)}")
    print("=" * 104)
    for rel, sc in rows:
        print(f"   {rel:70} {sc}")
    print()
