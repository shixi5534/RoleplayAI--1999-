# -*- coding: utf-8 -*-
"""删除前的**安全核验**：候选文件是否被保留下来的代码/脚本引用？

原则：只删"零引用 + 非冻结锁 + 非入库证据链"的文件。
任何被引用、或被 SHA 锁覆盖的文件一律保留。
"""
from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

r = subprocess.run(["git", "ls-files", "-z"], cwd=str(ROOT), capture_output=True)
TRACKED = {p for p in r.stdout.decode("utf-8", "replace").split("\0") if p}

# ── 冻结锁覆盖的路径（绝不可删）──
LOCKED: set[str] = set()
for bf in (ROOT / "data/compendium_rag/reports").glob("baseline_v*.json"):
    try:
        d = json.loads(bf.read_text(encoding="utf-8"))
    except Exception:
        continue
    for k, rel in (d.get("artifact_paths") or {}).items():
        LOCKED.add(f"data/compendium_rag/{rel}")
    # 允许为空
for extra in ("data/compendium_rag/graph.json",
              "data/compendium_rag/backups"):
    LOCKED.add(extra)

# ── .gitattributes 声明的冻结目录（证据链）──
FROZEN_DIRS = (
    "data/compendium_rag/repairs_v",   # 修复提案/验证（SHA 锁定）
    "data/compendium_rag/reports/",    # 评测工件（锁 + 可复算）
)

# ── 一次性产物模式（data/compendium_rag 顶层）──
DISCARD_RX = re.compile(
    r"^(_agent_batch[\w]*\.json"
    r"|_gen_batch[\w]*\.py"
    r"|_fix[\w]*\.py"
    r"|_probe[\w]*\.(py|txt)"
    r"|_cands[\w]*\.txt"
    r"|_dump[\w]*\.txt"
    r"|_c[\w]*\.txt"
    r"|_p\d[\w]*\.txt"
    r"|_s\d[\w]*\.txt"
    r"|_n\d[\w]*\.txt"
    r"|_sim[\w]*\.(py|txt)"
    r"|_tmp\d*\.(txt|py)"
    r"|_newnames[\w]*\.txt"
    r"|_r\d_[\w]*\.txt"
    r"|_types[\w]*\.txt"
    r"|_union[\w]*\.py"
    r"|_validate_batch[\w]*\.py"
    r"|_verify_batch[\w]*\.py"
    r"|_weld[\w]*\.txt"
    r"|_splits[\w]*\.txt"
    r"|_progress[\w]*\.py"
    r"|_r2_evidence[\w]*\.py"
    r"|_explain_member_loss[\w]*\.py"
    r"|_fix_alias[\w]*\.py"
    r"|_audit_[a-z_]+\.py)$"
)

cand: list[Path] = []
for p in (ROOT / "data/compendium_rag").iterdir():
    if p.is_file() and DISCARD_RX.match(p.name):
        cand.append(p)

# ── 引用核验：保住被任何保留文件提到的 ──
corpus: list[tuple[str, str]] = []
for g in ("src/**/*.py", "src/**/*.json", "scripts/**/*.py", "scripts/**/*.sh",
          "tests/**/*.py", "docs/**/*.md", "*.md", "*.toml", "*.bat",
          "data/compendium_rag/*.py", "data/compendium_rag/reports/*.py"):
    for q in ROOT.glob(g):
        if q.is_file():
            try:
                corpus.append((str(q.relative_to(ROOT)).replace("\\", "/"),
                               q.read_text(encoding="utf-8", errors="replace")))
            except Exception:
                pass

referenced: list[tuple[str, str]] = []
safe: list[Path] = []
for p in cand:
    rel = str(p.relative_to(ROOT)).replace("\\", "/")
    if rel in LOCKED or any(rel.startswith(d) for d in FROZEN_DIRS):
        referenced.append((rel, "冻结锁/证据目录"))
        continue
    hits = [n for n, t in corpus if p.name in t and n != rel]
    if hits:
        referenced.append((rel, f"被引用: {hits[:3]}"))
    else:
        safe.append(p)

print("=" * 88)
print(f"一次性产物候选 = {len(cand)}")
print(f"  可安全删除（零引用、非冻结）= {len(safe)}"
      f"  体积 = {sum(p.stat().st_size for p in safe)/1024/1024:.1f} MB")
print(f"  保留（被引用或属冻结链）    = {len(referenced)}")
print("=" * 88)
print("\n保留清单（前 25）：")
for rel, why in referenced[:25]:
    print(f"   {rel}  <- {why}")

out = ROOT / "data/compendium_rag/reports/_cleanup_discard.json"
out.write_text(json.dumps(
    {"safe": [str(p.relative_to(ROOT)).replace("\\", "/") for p in safe],
     "keep": [{"path": r, "why": w} for r, w in referenced]},
    ensure_ascii=False, indent=1), encoding="utf-8")
print(f"\n-> {out.relative_to(ROOT)}")
