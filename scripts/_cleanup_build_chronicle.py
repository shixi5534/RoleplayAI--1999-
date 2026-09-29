# -*- coding: utf-8 -*-
"""生成各子系统的**编年史**（CHRONICLE.md）：把历史过程档合并为一份带日期的索引+摘要。

设计要点（为什么不是简单拼接）：
  · 原文拼接会产出几百 KB 的不可读巨物，且重复叙述同一结论；
  · 编年史给**每条一个带日期的条目**：时间 + 文档 + 一句话结论 + 关键数字；
  · 原文**不丢失**：删除前已由 git 历史保存（标签 backup-pre-testdocs-cleanup），
    且本脚本在编年史中记录每个来源文档的原始路径与 SHA-16，可随时找回。
"""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PLAN = json.loads((ROOT / "data/compendium_rag/reports/_docs_merge_plan.json")
                  .read_text(encoding="utf-8"))

SUBSYS_TITLE = {
    "compendium-rag": "正典图谱 RAG（compendium_rag）",
    "plot-graph-rag": "剧情图谱 RAG（plot_graph，前身/并行）",
    "roleplay-core": "核心系统（角色扮演 / lore 向量层 / 架构 / 提示词）",
    "voice-desktop": "语音与桌面宠物",
    "qq": "QQ 通道",
}

# 每条目抽取：首个标题、首个有意义的结论行、出现的日期
DATE_RX = re.compile(r"(20\d{2})[-_/]?(\d{2})[-_/]?(\d{2})")
CONCLUSION_RX = re.compile(
    r"(结论|一句话|摘要|总结|判定|结果|核心发现|诚实结论|结论先行)")


def first_title(text: str) -> str:
    for ln in text.splitlines()[:12]:
        s = ln.strip()
        if s.startswith("#"):
            return s.lstrip("# ").strip()
    return "(无标题)"


def key_lines(text: str, limit: int = 4) -> list[str]:
    """挑出结论性的行（去重、限长）。"""
    out: list[str] = []
    for ln in text.splitlines():
        s = ln.strip()
        if not s or s.startswith(("#", "|", "```", ">")):
            continue
        # 去掉 markdown 列表前缀，避免生成 "- - " 双重项目符号
        s = re.sub(r"^[-*+]\s+", "", s)
        if len(s) > 200:
            s = s[:197] + "…"
        if CONCLUSION_RX.search(s) or re.search(r"\d+\.\d{2,4}|\d+/\d+", s):
            if s not in out:
                out.append(s)
        if len(out) >= limit:
            break
    return out


def doc_date(rel: str, text: str) -> str:
    m = DATE_RX.search(rel) or DATE_RX.search(text[:1500])
    return f"{m.group(1)}-{m.group(2)}-{m.group(3)}" if m else "—"


for sub, title in SUBSYS_TITLE.items():
    files = [p for p in PLAN["merge"] if p.startswith(f"docs/{sub}/")]
    if not files:
        continue
    lines = [
        f"# {title} · 历史编年史",
        "",
        "> 本文件由 **79 份历史过程档**合并而来（2026-09-29 整理）。",
        "> 收录原则：已完成的一次性报告（审计 / 实验 / 验收 / 阶段总结）。",
        "> **当前权威文档仍以独立文件形式保留**，见 `docs/README.md` 索引。",
        ">",
        "> 原文未丢失：删除前快照在 git 标签 `backup-pre-testdocs-cleanup`，",
        "> 且每条下方记录了来源路径与 SHA-16，可用 `git show <tag>:<path>` 找回。",
        "",
        "---",
        "",
    ]
    for rel in sorted(files):
        p = ROOT / rel
        try:
            raw = p.read_bytes()
            text = raw.decode("utf-8", "replace")
        except Exception:
            continue
        sha = hashlib.sha256(raw).hexdigest()[:16]
        lines += [
            f"## {doc_date(rel, text)} · {first_title(text)}",
            "",
            f"- 来源：`{rel}`",
            f"- SHA-16：`{sha}`",
            "",
        ]
        kl = key_lines(text)
        if kl:
            lines.append("**要点**")
            lines.append("")
            for s in kl:
                lines.append(f"- {s}")
            lines.append("")
        lines.append("")
    out = ROOT / "docs" / sub / "CHRONICLE.md"
    out.write_text("\n".join(lines), encoding="utf-8")
    print(f"  {sub:16} 合并 {len(files):>3} 份 -> {out.relative_to(ROOT)} "
          f"({out.stat().st_size/1024:.0f} KB)")
