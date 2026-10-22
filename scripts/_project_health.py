# -*- coding: utf-8 -*-
"""全项目整理**体检**：结构 / 忽略规则 / 根目录洁净度 / 依赖一致性。

这是「整齐」的可执行判据：跑一遍即知项目是否仍处于整理后的状态。
"""
from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FAILS: list[str] = []


def ck(label: str, cond: bool, detail: str = "") -> None:
    print(f"  [{'OK ' if cond else 'BAD'}] {label}{('  ' + detail) if detail else ''}")
    if not cond:
        FAILS.append(label)


def git(*a: str) -> str:
    r = subprocess.run(["git", *a], cwd=str(ROOT), capture_output=True)
    return r.stdout.decode("utf-8", "replace")


TRACKED = {p for p in git("ls-files", "-z").split("\0") if p}

print("=" * 88)
print("A) 根目录洁净度")
print("=" * 88)
# 允许保留在根级的文件
ROOT_OK = {
    ".env", ".env.example", ".gitattributes", ".gitignore",
    "pyproject.toml", "README.md", "requirements.txt", "start_server.bat",
    # 文件级地图（目录/源码/脚本/测试 + 常见任务入口），docs/README.md 指向它
    "PROJECT_MAP.md",
    # ⚠ git worktree 下 `.git` 是**文件**（指向真实 gitdir），非目录 —— 必须放行，
    #   否则本检查在干净副本（worktree）里必然误报。
    ".git",
}
# 已由 .gitignore 显式声明的本机产物（存在也合规，但必须被忽略）
IGNORED_OK = {
    ".env.env.bak.20260831_232917": "本地 .env 备份（.env.*.bak* 已忽略）",
    "_shuzhi_extract.txt": "一次性抽取产物（已忽略）",
    "_tmp_pron_edges.txt": "一次性探针产物（已忽略）",
    # 2026-10-09/10 P4–P7 派工残留（.gitignore 已有显式规则，见「根级作业清单」段）
    "_jobs.json": "P4–P7 派工清单（已忽略）",
    "_jobs2.json": "P4–P7 派工清单（已忽略）",
    "_p7_jobs.json": "P7 派工清单（已忽略）",
    "_p7_plan.json": "P7 派工计划（已忽略）",
    "p4_diag2.py": "P4 诊断脚本残留（已忽略）",
}
actual_root = {p.name for p in ROOT.iterdir() if p.is_file()}
extra = sorted(actual_root - ROOT_OK - set(IGNORED_OK))
ck("根级无未登记的多余文件", not extra, str(extra))
for name, why in IGNORED_OK.items():
    if (ROOT / name).exists():
        r = subprocess.run(["git", "check-ignore", "-q", name],
                           cwd=str(ROOT), capture_output=True)
        ck(f"  {name} 已被忽略（{why}）", r.returncode == 0)

print()
print("=" * 88)
print("B) 本机残留目录已被忽略（防再次污染 git status）")
print("=" * 88)
# 注意：目录若已被删除，则无需再被忽略 —— 但 .gitignore 规则仍应在位，
# 以便下次 pytest 生成时自动忽略。故检查的是**规则**而非目录存在性。
gi = (ROOT / ".gitignore").read_text(encoding="utf-8")
for pat in (".pytest_bt/", ".pytest_ws/", ".pytest_tmp*/", "pytest-of-Lenovo/",
            "roleplay_test_qenmhfwr/", "_poc_shots/", "tmp_pytest/", "logs/",
            ".pytest_cache/"):
    ck(f".gitignore 含规则 {pat}",
       any(ln.strip() == pat for ln in gi.splitlines()))

print()
print("=" * 88)
print("C) 存档目录（一次性产物已归档而非散落）")
print("=" * 88)
arch = ROOT / "scripts" / "_archive"
ck("scripts/_archive/ 存在", arch.exists())
if arch.exists():
    names = sorted(p.name for p in arch.iterdir())
    ck("  含 src_data_20260729（早期数据）", "src_data_20260729" in names, str(names))
    ck("  含 _cue_feasibility.py", "_cue_feasibility.py" in names)
    ck("  含 _strip_test.js", "_strip_test.js" in names)
ck("src/data 已移出代码树", not (ROOT / "src" / "data").exists())

print()
print("=" * 88)
print("D) 依赖清单一致性（requirements.txt vs pyproject.toml）")
print("=" * 88)
pq = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
rq = (ROOT / "requirements.txt").read_text(encoding="utf-8")
# 取 pyproject 的 dependencies 段
m = re.search(r"dependencies\s*=\s*\[(.*?)\]", pq, re.S)
deps = re.findall(r'"([^"]+)"', m.group(1)) if m else []
missing = [d for d in deps
           if d.split("==")[0].split("[")[0].lower()
           not in rq.lower()]
ck("requirements.txt 覆盖 pyproject 全部运行时依赖", not missing, str(missing))
ck("python-multipart 在 requirements.txt", "python-multipart" in rq)
ck("fastapi 在 requirements.txt", "fastapi" in rq)

print()
print("=" * 88)
print("E) 结构完整性（整理不得破坏既有体系）")
print("=" * 88)
for d in ("src", "tests", "scripts", "docs", "data", "frontend", "desktop"):
    ck(f"{d}/ 存在", (ROOT / d).is_dir())
ck("docs 索引在库", (ROOT / "docs/README.md").exists())
ck("data/compendium_rag/graph.json 在库",
   (ROOT / "data/compendium_rag/graph.json").exists())
# 关键脚本仍在
for s in ("_verify_v8_locks.py", "_docs_health.py", "_project_tidy.py"):
    ck(f"scripts/{s} 在库", (ROOT / "scripts" / s).exists())

print()
print("=" * 88)
if FAILS:
    print(f"RESULT: {len(FAILS)} 项失败 -> {FAILS}")
    raise SystemExit(1)
print("RESULT: ALL OK")
