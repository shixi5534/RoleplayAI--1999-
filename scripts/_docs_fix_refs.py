# -*- coding: utf-8 -*-
"""移动后修复引用（**位置感知**，默认 dry-run）。

三类引用，全部处理：

  (1) 代码/文档里的**仓库根相对**路径：`docs/X.md` / `deliverables/Y.md` / `PLAN/Z.md`
      → 直接查映射表替换。

  (2) markdown **相对链接**：`../X.md` / `./X.md` / `X.md`
      → 先按**文件旧位置**解析成仓库根相对路径，查映射，再按**文件新位置**重新相对化。
      （只做 (1) 会漏掉这类，而两文件移动后深度不同时链接必断。）

  (3) 运行时端点：`src/roleplay/main.py` 里 `Path(...)/"docs"/"DESKTOP_PET_DESIGN.md"`
      由 (1) 的**字符串形态**覆盖不到（它拆成独立路径分量），故单独打补丁。

用法：
  python scripts/_docs_fix_refs.py            # dry-run
  python scripts/_docs_fix_refs.py --apply
"""
from __future__ import annotations

import argparse
import json
import posixpath
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MAPFILE = ROOT / "data/compendium_rag/reports/_docs_reorg_map.json"

# 迁移工具自身**不参与**改写（它们的路径表是"旧→新"的一次性记录）
EXCLUDE = {
    "scripts/_docs_reorg_plan.py",
    "scripts/_docs_fix_refs.py",
    "scripts/_docs_preview_map.py",
    "scripts/_docs_build_index.py",
}

SCAN_GLOBS = ("src/**/*.py", "scripts/**/*.py", "tests/**/*.py",
              "frontend/**/*.js", "frontend/**/*.html", "desktop/**/*.md",
              "desktop/**/*.js", "*.md", "docs/**/*.md", "docs/**/*.txt")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()

    plan: dict[str, str] = json.loads(MAPFILE.read_text(encoding="utf-8"))
    # old(仓库根相对) -> new(仓库根相对)；文件**已在**新位置，故还需反向表
    old2new = {k.replace("\\", "/"): v.replace("\\", "/") for k, v in plan.items()}
    new2old = {v: k for k, v in old2new.items()}
    by_base: dict[str, list[str]] = {}
    for old in old2new:
        by_base.setdefault(posixpath.basename(old), []).append(old)

    targets: list[Path] = []
    for g in SCAN_GLOBS:
        targets += [p for p in ROOT.glob(g)
                    if p.is_file() and ".venv" not in p.parts
                    and "node_modules" not in p.parts
                    and "__pycache__" not in p.parts]
    targets = sorted(set(targets))

    # 处理范围：**所有**代码文件 + **所有** markdown。
    # 关键：未移动的 markdown（README.md / desktop/CHANGES.md 等）同样可能引用已移动的文档，
    # 只处理"已移动的 md"会漏掉它们。
    todo = [p for p in targets
            if str(p.relative_to(ROOT)).replace("\\", "/") not in EXCLUDE
            and p.suffix in (".py", ".js", ".html", ".md", ".txt")]

    total_files = total_hits = 0
    detail: list[tuple[str, int]] = []

    for p in todo:
        # 文件当前实际位置（新），以及迁移前的旧位置（用于解析原有相对链接）
        rel_new = str(p.relative_to(ROOT)).replace("\\", "/")
        rel_old = new2old.get(rel_new, rel_new)
        try:
            text = p.read_text(encoding="utf-8")
        except Exception:  # noqa: BLE001
            continue
        orig = text
        hits = 0

        # ---- 分两步，互不干扰 ----
        # (A) 先处理 markdown 链接**目标**：按旧位置解析 → 查映射 → 按新位置相对化。
        # (B) 再对**其余全部文本（含链接标签）**应用"仓库根相对路径"替换。
        #     二者顺序不可颠倒：若先做 (B)，链接目标里的裸文件名会被当成根相对路径改写。
        #     只对目标做占位（而非整条链接），是为了让标签里出现的路径也能被 (B) 修正。

        targets_stash: dict[str, str] = {}

        def fix_link(mo: re.Match) -> str:
            nonlocal hits
            label, target = mo.group(1), mo.group(2)
            if target.startswith(("http://", "https://", "#", "mailto:")):
                return mo.group(0)
            anchor = ""
            t = target
            if "#" in t:
                t, anchor = t.split("#", 1)
                anchor = "#" + anchor
            if not t or not t.endswith((".md", ".txt", ".mermaid")):
                return mo.group(0)
            cand = t.lstrip("./")
            new_t = old2new.get(cand)
            if new_t is None:
                resolved = posixpath.normpath(
                    posixpath.join(posixpath.dirname(rel_old), t))
                new_t = old2new.get(resolved)
            if new_t is None:
                return mo.group(0)
            new_rel = posixpath.relpath(new_t, posixpath.dirname(rel_new) or ".")
            hits += 1
            key = f"\x00TGT{len(targets_stash)}\x00"
            targets_stash[key] = f"{new_rel}{anchor}"
            return f"[{label}]({key})"

        if p.suffix == ".md":
            text = re.sub(r"\[([^\]]*)\]\(([^)\s]+)\)", fix_link, text)

        # (B) 根相对路径替换（标签/正文/代码注释），此时链接目标已被占位保护
        for old, new in sorted(old2new.items(), key=lambda kv: -len(kv[0])):
            rx = re.compile(r"(?<![\w/.\-])" + re.escape(old))
            text, n = rx.subn(new, text)
            hits += n

        for key, val in targets_stash.items():
            text = text.replace(key, val)

        if text != orig:
            total_files += 1
            total_hits += hits
            detail.append((rel_new, hits))
            if args.apply:
                p.write_text(text, encoding="utf-8", newline="")

    for rel, n in detail:
        print(f"  {rel}   ({n} 处)")
    print(f"\n{'已改写' if args.apply else '将改写'} {total_files} 个文件，共 {total_hits} 处")
    if not args.apply:
        print("（dry-run；加 --apply 才写入）")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
