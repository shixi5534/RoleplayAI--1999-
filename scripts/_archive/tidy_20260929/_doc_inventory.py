# -*- coding: utf-8 -*-
"""把所有候选文档的「身份指纹」抽取出来，便于分类（只读）。

对每个 .md/.txt 打印：路径 / 大小 / 首个标题 / 前 6 行非空内容 /
以及出现的关键标识（compendium / 剧情图谱 / lore / 向量 / 10406 / 7033 …）
"""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKIP = re.compile(r"[\\/](\.venv|\.git|node_modules|__pycache__|\.pytest|\.idea|vendor|models)[\\/]")

TARGETS: list[Path] = []
for pat in ("docs/**/*.md", "docs/**/*.txt", "PLAN/*", "deliverables/**/*.md",
            "*.md", "data/docs/*", "data/compendium_rag/*.md",
            "deliverables/engineering-assurance/*.md"):
    TARGETS += [p for p in ROOT.glob(pat) if p.is_file() and not SKIP.search(str(p))]
TARGETS = sorted(set(TARGETS))

MARKERS = {
    "compendium": r"compendium|COMPENDIUM|正典",
    "剧情图谱": r"剧情图谱|plot_graph|plot rag|评测_plot",
    "lore层": r"lore层|lore_|向量层",
    "10406": r"10406",
    "7033": r"7033",
    "9021": r"9021",
    "3695": r"3695",
    "300cn": r"300_cn|300cn|rag_testset_300",
    "盲测206": r"盲测|blind_v1",
    "角色扮演": r"角色扮演|persona|角色卡",
    "语音": r"语音|voice|Live2D|TTS",
    "桌面宠物": r"桌宠|desktop pet|DESKTOP_PET",
    "QQ": r"QQ",
}

print(f"共 {len(TARGETS)} 个候选文件\n")
print("=" * 118)
for p in TARGETS:
    try:
        t = p.read_text(encoding="utf-8", errors="replace")
    except Exception as e:  # noqa: BLE001
        print(f"{p.relative_to(ROOT)}  读取失败 {e}")
        continue
    lines = [ln.strip() for ln in t.splitlines() if ln.strip()]
    title = next((ln for ln in lines[:5] if ln.startswith("#")), "(无标题)")
    head = " / ".join(lines[:5])[:150]
    hits = [k for k, rx in MARKERS.items() if re.search(rx, t)]
    rel = str(p.relative_to(ROOT)).replace("\\", "/")
    print(f"{rel}")
    print(f"    size={len(t):>7}  markers={hits}")
    print(f"    title: {title[:110]}")
    print(f"    head : {head}")
print("=" * 118)
