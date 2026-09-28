# -*- coding: utf-8 -*-
"""文件守恒校验：移动前后 md 文件不丢不多（按文件名比对，避免路径变化干扰）。"""
from __future__ import annotations

import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def ls(tag: str | None = None) -> set[str]:
    """tag=None → 读**索引**（含已 staged 的移动）；否则读该提交树。"""
    cmd = (["git", "ls-files", "-z"] if tag is None
           else ["git", "ls-tree", "-r", "-z", "--name-only", tag])
    r = subprocess.run(cmd, cwd=str(ROOT), capture_output=True)
    return {p for p in r.stdout.decode("utf-8", "replace").split("\0") if p}


ROOT_LEVEL = {
    "RAG_SYSTEM_DESIGN.md", "GRAPHRAG_ENHANCEMENT_PLAN.md",
    "ROLEPLAY_PROMPT_OPTIMIZATION_PLAN.md", "VOICE_ITERATION_REPORT.md",
}


def in_scope_pre(p: str) -> bool:
    if p in ROOT_LEVEL:
        return True
    return p.endswith(".md") and p.startswith(("docs/", "PLAN/", "deliverables/"))


base = ls("backup-pre-docs-reorg")
now = ls()
pre = {p for p in base if in_scope_pre(p)}
post = {p for p in now if p.startswith("docs/") and p.endswith(".md")}

print(f"移动前（docs/ + PLAN/ + deliverables/ + 根级）md = {len(pre)}")
print(f"移动后 docs/ 下 md（已跟踪）                    = {len(post)}")
print(f"新增索引 docs/README.md 计入后者                = {'docs/README.md' in post}")
print()

post_names = {q.split("/")[-1] for q in post}
missing = sorted(p for p in pre if p.split("/")[-1] not in post_names)
extra = sorted(q for q in post
               if q.split("/")[-1] not in {p.split("/")[-1] for p in pre})

print(f"丢失（移动前有、移动后按名找不到）= {len(missing)}")
for m in missing[:20]:
    print(f"   - {m}")
print(f"新增（移动后多出的）              = {len(extra)}")
for e in extra[:20]:
    print(f"   + {e}")

print()
print("移动前总数 - 移动后总数 =", len(pre) - len(post), "（应为 -1，即新增 1 个索引 README）")
raise SystemExit(0 if not missing else 1)
