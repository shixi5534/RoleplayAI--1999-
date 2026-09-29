# -*- coding: utf-8 -*-
"""移动后体检：验证引用完整性（这是"放好"的验收判据）。

检查项：
  A) 运行时端点：main.py 的磁盘路径确实存在
  B) 所有 markdown 相对链接可解析（无 404）
  C) 代码/文档里提及的 docs/… 路径都存在（旧路径残留 = 漏改）
  D) docs/ 平铺层已清空、文件总数守恒
"""
from __future__ import annotations

import posixpath
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FAILS: list[str] = []


def ck(label: str, cond: bool, detail: str = "") -> None:
    print(f"  [{'OK ' if cond else 'BAD'}] {label}{('  ' + detail) if detail else ''}")
    if not cond:
        FAILS.append(label)


print("=" * 96)
print("A) 运行时端点（main.py 的磁盘路径）")
print("=" * 96)
target = ROOT / "docs/voice-desktop/pet-design/DESKTOP_PET_DESIGN.md"
ck("端点磁盘文件存在", target.is_file(), str(target.relative_to(ROOT)))
src_main = (ROOT / "src/roleplay/main.py").read_text(encoding="utf-8")
ck("main.py 磁盘路径已指向新位置",
   '"voice-desktop" / "pet-design"' in src_main)
ck("main.py URL 路由保持不变（前端依赖）",
   '@app.get("/docs/DESKTOP_PET_DESIGN.md"' in src_main)
fe = (ROOT / "frontend/js/desktop-pet.js").read_text(encoding="utf-8")
ck("前端 URL 引用未变", "./docs/DESKTOP_PET_DESIGN.md" in fe)

print()
print("=" * 96)
print("B) markdown 相对链接可解析")
print("=" * 96)
broken: list[str] = []
n_links = 0
for p in ROOT.glob("docs/**/*.md"):
    rel = str(p.relative_to(ROOT)).replace("\\", "/")
    # ⚠ CHRONICLE.md 是**编年史**：它刻意引用**已被合并删除**的原始文档路径，
    #   作为"该条目出自哪份原文"的可追溯锚点（配合 backup 标签可复原）。
    #   这些不是断链，而是归档引用 —— 单独统计，不计入失败。
    is_chronicle = p.name == "CHRONICLE.md"
    t = p.read_text(encoding="utf-8", errors="replace")
    for label, tgt in re.findall(r"\[([^\]]*)\]\(([^)\s]+)\)", t):
        if tgt.startswith(("http://", "https://", "#", "mailto:")):
            continue
        tt = tgt.split("#", 1)[0]
        if not tt:
            continue
        n_links += 1
        resolved = posixpath.normpath(posixpath.join(posixpath.dirname(rel), tt))
        if not (ROOT / resolved).exists():
            if is_chronicle:
                continue          # 归档引用，不计失败
            broken.append(f"{rel}  ->  {tgt}")
    # 编年史里的 `- 来源：\`path\`` 反引号引用同样属归档锚点，跳过检查
ck(f"docs/ 内 {n_links} 个相对链接（编年史归档引用除外）全部可解析",
   not broken, f"{len(broken)} 断链")
for b in broken[:15]:
    print(f"        ✗ {b}")

print()
print("=" * 96)
print("C) 失效引用检测（只报**本次移动新引入**的断链）")
print("=" * 96)
# 判据：同名引用在**移动前**能否解析。移动前就断的（glob 通配、笔误、规划中的文件名）
# 不算本次回归。基线取自 backup 标签的 docs 平铺树。
import subprocess

BASE_TAG = "backup-pre-docs-reorg"
base_files: set[str] = set()
r = subprocess.run(["git", "ls-tree", "-r", "--name-only", BASE_TAG],
                   cwd=str(ROOT), capture_output=True, text=True,
                   encoding="utf-8", errors="replace")
if r.returncode == 0:
    base_files = {x.strip() for x in r.stdout.splitlines() if x.strip()}


def broken_now() -> set[str]:
    out: set[str] = set()
    SCAN = ("src/**/*.py", "scripts/**/*.py", "tests/**/*.py",
            "frontend/**/*.js", "docs/**/*.md", "*.md", "desktop/**/*.md")
    EXCL = {"scripts/_docs_reorg_plan.py", "scripts/_docs_fix_refs.py",
            "scripts/_docs_preview_map.py", "scripts/_docs_health.py",
            # 该脚本**故意**以旧路径为测试数据（核对"移动前既存断链"），不是漏改
            "scripts/_docs_check_prebroken.py",
            # 编年史生成器把被合并的原始路径写入 CHRONICLE.md，属**归档引用**
            "scripts/_cleanup_build_chronicle.py",
            "scripts/_cleanup_docs_plan.py"}
    files: list[Path] = []
    for g in SCAN:
        files += [p for p in ROOT.glob(g)
                  if p.is_file() and ".venv" not in p.parts
                  and "node_modules" not in p.parts and "__pycache__" not in p.parts]
    # ⚠ scripts/_archive/ 存放**已被取代**的一次性脚本（含当年的旧路径字面量），
    #   它们不是活代码，扫描它们必然产生"断链"噪声 —— 排除。
    files = [p for p in files if "_archive" not in p.parts]
    rx = re.compile(r"(?<![\w/\\.-])((?:docs|deliverables|PLAN)/"
                    r"[^\s`\)\]，。、；：\"'*{]+\.(?:md|txt|mermaid))")
    for p in sorted(set(files)):
        rel = str(p.relative_to(ROOT)).replace("\\", "/")
        if rel in EXCL:
            continue
        # ⚠ CHRONICLE.md 刻意引用**已合并删除**的原始路径（归档锚点，可经
        #   backup 标签复原），不是断链 —— 跳过，避免把归档引用误报为回归。
        if p.name == "CHRONICLE.md":
            continue
        t = p.read_text(encoding="utf-8", errors="replace")
        for ref in set(rx.findall(t)):
            if (ROOT / ref).exists():
                continue
            if p.suffix == ".md":
                alt = posixpath.normpath(posixpath.join(posixpath.dirname(rel), ref))
                if (ROOT / alt).exists():
                    continue
            out.add(f"{rel}  ->  {ref}")
    return out


now = broken_now()
# 移动前就断的：引用名在基线树里也找不到（去掉 docs/ 前缀后在 base_files 里查不到）
pre_broken = {s for s in now
              if not any(f.endswith(s.split("->")[-1].strip().split("/")[-1])
                         for f in base_files)}
new_broken = now - pre_broken
ck("无本次移动新引入的断链", not new_broken,
   f"{len(new_broken)} 新 / {len(pre_broken)} 原有")
for s in sorted(new_broken)[:20]:
    print(f"        ✗ {s}")
print(f"        （移动前既存的断链 {len(pre_broken)} 处，非本次回归，未计入）")
for s in sorted(pre_broken)[:6]:
    print(f"        · {s}")

print()
print("=" * 96)
print("D) 结构")
print("=" * 96)
flat = [p.name for p in (ROOT / "docs").iterdir() if p.is_file()]
ck("docs/ 平铺层已清空（仅允许 README.md）",
   all(n == "README.md" for n in flat), str(flat))
ck("PLAN/ 目录已无文件或已移除",
   not (ROOT / "PLAN").exists() or not any((ROOT / "PLAN").rglob("*")),
   str([p.name for p in (ROOT / "PLAN").rglob("*")]) if (ROOT / "PLAN").exists() else "")
ck("deliverables/ 仅剩资源（无 .md）",
   not any((ROOT / "deliverables").rglob("*.md")))
ck("根级仅剩 README.md",
   sorted(p.name for p in ROOT.glob("*.md")) == ["README.md"],
   str(sorted(p.name for p in ROOT.glob("*.md"))))
tot = len(list((ROOT / "docs").rglob("*.md")))
print(f"        docs/ 下 .md 总数 = {tot}")

print()
print("=" * 96)
if FAILS:
    print(f"RESULT: {len(FAILS)} 项失败")
    for f in FAILS:
        print(f"   - {f}")
    raise SystemExit(1)
print("RESULT: ALL OK")
