# -*- coding: utf-8 -*-
"""可删集计算（精简快速版）：data/compendium_rag 顶层的一次性产物。

修正前一版的三个缺陷：
  1. Windows 下 `str(Path)` 用反斜杠 → 路径比较失效；统一用 as_posix()。
  2. `Path.parts` 对**绝对**路径判断不直观 → 改用相对路径的 parts。
  3. 语料范围过宽（吸入 .venv/node_modules 数万文件、且做全文本匹配极慢）
     → 只扫仓库自有源码与文档（显式白名单目录）。
"""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

SKIP = {".venv", "node_modules", ".git", "__pycache__", ".pytest_cache",
        ".pytest_bt", ".pytest_tmp", ".pytest_tmp2", ".pytest_tmp3",
        ".pytest_ws", "tmp_pytest", "logs", "_poc_shots", "vendor",
        "pytest-of-Lenovo", "roleplay_test_qenmhfwr", "_r4replay"}


def collect(globs: tuple[str, ...]) -> list[str]:
    out: list[str] = []
    for g in globs:
        for q in ROOT.glob(g):
            if not q.is_file():
                continue
            try:
                rel = q.relative_to(ROOT)
            except ValueError:
                continue
            parts = set(rel.parts)
            if SKIP & parts:
                continue
            out.append(rel.as_posix())
    return sorted(set(out))


# ── 永不删 ──
LOCKED: set[str] = {"data/compendium_rag/graph.json"}
for bf in (ROOT / "data/compendium_rag/reports").glob("baseline_v*.json"):
    try:
        d = json.loads(bf.read_text(encoding="utf-8"))
    except Exception:
        continue
    for _k, rel in (d.get("artifact_paths") or {}).items():
        LOCKED.add(f"data/compendium_rag/{rel}")

# ── 一次性产物模式 ──
DISCARD_RX = re.compile(
    r"^(_agent_batch\d+\.json"
    r"|_gen_batch\d+\.py"
    r"|_fix\d+[a-z]?\.py"
    r"|_probe[\w]*\.(py|txt)"
    r"|_cands[\w]*\.txt"
    r"|_dump[\w]*\.txt"
    r"|_c\d{3}[\w]*\.txt"
    r"|_p\d{3}[\w]*\.txt"
    r"|_s\d{3}[\w]*\.txt"
    r"|_n\d{3}[\w]*\.txt"
    r"|_sim[\w]*\.(py|txt)"
    r"|_tmp[\w]*\.(txt|py)"
    r"|_newnames[\w]*\.txt"
    r"|_r\d_[\w]*\.txt"
    r"|_types\d*\.txt"
    r"|_union[\w]*\.py"
    r"|_validate_batch[\w]*\.py"
    r"|_verify_batch[\w]*\.py"
    r"|_weld[\w]*\.txt"
    r"|_splits[\w]*\.txt"
    r"|_progress[\w]*\.py"
    r"|_r2_evidence[\w]*\.py"
    r"|_explain_member_loss[\w]*\.py"
    r"|_fix_alias[\w]*\.py"
    r"|_rd287[\w]*\.txt"
    r"|_cache277[\w]*\.txt"
    r"|_n402[\w]*\.txt|_n403[\w]*\.txt|_n404[\w]*\.txt)$"
)

all_discard_dir = collect(("data/compendium_rag/*",))
cand_init = {p for p in all_discard_dir
             if DISCARD_RX.match(p.rsplit("/", 1)[-1]) and p not in LOCKED}
print(f"初始候选 = {len(cand_init)}")

# ── 引用语料：仅仓库自有源码/文档（排除候选自身）──
CORPUS_GLOBS = ("src/**/*.py", "scripts/**/*.py", "scripts/**/*.sh",
                "tests/**/*.py", "tests/**/*.js", "docs/**/*.md",
                "*.md", "*.toml", "*.bat", "frontend/**/*.js",
                "data/compendium_rag/reports/*.py")
corpus_files = [p for p in collect(CORPUS_GLOBS) if p not in cand_init]
print(f"引用语料 = {len(corpus_files)} 个文件")

# ── 保留理由：被**保留者**引用（不动点）──
texts: dict[str, str] = {}
for p in corpus_files:
    try:
        texts[p] = (ROOT / p).read_text(encoding="utf-8", errors="replace")
    except Exception:
        pass

kept: set[str] = set()
changed = True
while changed:
    changed = False
    for c in sorted(cand_init - kept):
        name = c.rsplit("/", 1)[-1]
        if any(name in t for t in texts.values()):
            kept.add(c)
            try:
                texts[c] = (ROOT / c).read_text(encoding="utf-8", errors="replace")
            except Exception:
                pass
            changed = True

deletable = sorted(cand_init - kept)
total = sum((ROOT / p).stat().st_size for p in deletable)
print()
print("=" * 84)
print(f"可删 = {len(deletable)} 个文件，{total/1024/1024:.1f} MB")
print(f"保留 = {len(kept)} 个（被源码/文档显式引用）")
print("=" * 84)
kinds: dict[str, int] = {}
for p in deletable:
    n = p.rsplit("/", 1)[-1]
    k = ("agent_batch" if n.startswith("_agent_batch") else
         "gen_batch" if n.startswith("_gen_batch") else
         "dump" if n.startswith("_dump") else
         "cands" if n.startswith("_cands") else
         "fix" if n.startswith("_fix") else
         "probe" if n.startswith("_probe") else
         "sim" if n.startswith("_sim") else "其它")
    kinds[k] = kinds.get(k, 0) + 1
for k, v in sorted(kinds.items(), key=lambda kv: -kv[1]):
    print(f"   {k:14} {v}")

out = ROOT / "data/compendium_rag/reports/_cleanup_discard.json"
out.write_text(json.dumps({"n": len(deletable), "bytes": total,
                           "files": deletable,
                           "kept_referenced": sorted(kept)},
                          ensure_ascii=False, indent=1), encoding="utf-8")
print(f"\n-> {out.relative_to(ROOT)}")
print("\n保留样例（被引用，前 8）：")
for k in sorted(kept)[:8]:
    print(f"   {k}")
