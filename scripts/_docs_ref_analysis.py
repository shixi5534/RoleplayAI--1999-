# -*- coding: utf-8 -*-
"""文档合并前的**引用分析**：哪些 docs 被代码/脚本实际引用（合并会断链）。

输出：
  · 被引用的 docs 清单（这些必须保留原路径，或同步改引用）
  · 未被任何代码引用的 docs（可安全合并进编年史）
"""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKIP = {".venv", "node_modules", ".git", "__pycache__", ".pytest_cache",
        ".pytest_ws", "tmp_pytest", "_poc_shots", "vendor", "_r4replay"}


def rel_files(globs: tuple[str, ...]) -> list[Path]:
    out = []
    for g in globs:
        for q in ROOT.glob(g):
            if q.is_file():
                rel = q.relative_to(ROOT)
                if not (SKIP & set(rel.parts)):
                    out.append(q)
    return sorted(set(out))


# 所有 docs 文档
docs = [p for p in (ROOT / "docs").rglob("*")
        if p.is_file() and p.suffix in (".md", ".txt", ".mermaid")]
docs_rel = {p.relative_to(ROOT).as_posix() for p in docs}

# 引用来源：代码/脚本/测试/根文档（**不含 docs 自身**，因为 docs 内部互引可一起改）
#
# ⚠ 必须排除**文档迁移工具自身**：`_docs_reorg_plan.py` 把全部 docs 路径作为
#   **映射表数据**内嵌，`_docs_fix_refs.py` / `_docs_health.py` 含检查清单 ——
#   它们不是"消费者"，会把 138/140 全部误判为"被引用"。
EXCLUDE_SRC = {
    "scripts/_docs_reorg_plan.py",
    "scripts/_docs_fix_refs.py",
    "scripts/_docs_health.py",
    "scripts/_docs_preview_map.py",
    "scripts/_docs_conservation.py",
    "scripts/_docs_check_prebroken.py",
    "scripts/_doc_classify.py",
    "scripts/_doc_classify2.py",
    "scripts/_doc_inventory.py",
    "scripts/_doc_ambiguous.py",
    "scripts/_doc_check_uncertain.py",
    "scripts/_docs_ref_analysis.py",
    "scripts/_cleanup_build_chronicle.py",
}

ref_sources = [p for p in rel_files(
    ("src/**/*.py", "scripts/**/*.py", "tests/**/*.py",
     "tests/**/*.js", "frontend/**/*.js", "desktop/**/*.md",
     "*.md", "pyproject.toml", "*.bat"))
    if p.relative_to(ROOT).as_posix() not in EXCLUDE_SRC]
print(f"docs 文件数 = {len(docs_rel)}")
print(f"引用来源（代码/脚本/测试/根文档）= {len(ref_sources)}")

refs: dict[str, list[str]] = {}
for p in ref_sources:
    try:
        t = p.read_text(encoding="utf-8", errors="replace")
    except Exception:
        continue
    src = p.relative_to(ROOT).as_posix()
    if src in docs_rel:
        continue
    for d in docs_rel:
        name = Path(d).name
        # 精确路径 或 文件名（后者更宽松，避免漏判）
        if d in t or (name in t and len(name) > 8):
            refs.setdefault(d, []).append(src)

print()
print("=" * 92)
print(f"① 被代码/脚本引用的 docs = {len(refs)}（这些必须保留原路径或同步改引用）")
print("=" * 92)
for d in sorted(refs):
    print(f"  {d}")
    for s in refs[d][:4]:
        print(f"       <- {s}")

print()
print("=" * 92)
print(f"② 未被任何代码引用的 docs = {len(docs_rel) - len(refs)}（可安全合并）")
print("=" * 92)
unref = sorted(docs_rel - set(refs))
for d in unref:
    print(f"  {d}")

out = ROOT / "data/compendium_rag/reports/_docs_refs.json"
out.write_text(json.dumps({"referenced": {k: v for k, v in refs.items()},
                           "unreferenced": unref},
                          ensure_ascii=False, indent=1), encoding="utf-8")
print(f"\n-> {out.relative_to(ROOT)}")
