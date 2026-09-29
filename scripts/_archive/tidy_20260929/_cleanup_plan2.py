# -*- coding: utf-8 -*-
"""可删集**定点计算**：候选若只被其它候选引用，则同属可删。

修正上一版的缺陷：`_agent_batch100.json` 被 `_gen_batch100.py` 引用，
而后者本身也是候选 —— 互相引用不能构成"保留理由"。
本版用不动点迭代：从"被**保留者**引用"出发，反复剔除只被候选引用的候选。

严格保留（永不删）：
  · 任何 baseline_v*.json 锁覆盖的路径
  · .gitattributes 声明为冻结证据的目录（repairs_v*/）
  · graph.json / backups（回滚锚点）
"""
from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
r = subprocess.run(["git", "ls-files", "-z"], cwd=str(ROOT), capture_output=True)
TRACKED = [p for p in r.stdout.decode("utf-8", "replace").split("\0") if p]
TRACKED_SET = set(TRACKED)

# ── 永不删：锁覆盖 + 回滚锚点 ──
LOCKED: set[str] = {"data/compendium_rag/graph.json"}
for bf in (ROOT / "data/compendium_rag/reports").glob("baseline_v*.json"):
    try:
        d = json.loads(bf.read_text(encoding="utf-8"))
    except Exception:
        continue
    for _k, rel in (d.get("artifact_paths") or {}).items():
        LOCKED.add(f"data/compendium_rag/{rel}")
for p in TRACKED:
    if p.startswith("data/compendium_rag/backups/"):
        LOCKED.add(p)
    if p.startswith("data/compendium_rag/repairs_v"):
        LOCKED.add(p)

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
    r"|_audit_[a-z_]+\.py"
    r"|_c287[\w]*\.txt|_c310[\w]*\.txt|_c311[\w]*\.txt|_c312[\w]*\.txt"
    r"|_c313[\w]*\.txt|_c314[\w]*\.txt|_c400[\w]*\.txt|_c401[\w]*\.txt"
    r"|_c402[\w]*\.txt|_c403[\w]*\.txt|_c404[\w]*\.txt|_c440[\w]*\.txt"
    r"|_c500[\w]*\.txt|_c501[\w]*\.txt|_c502[\w]*\.txt|_c577[\w]*\.txt"
    r"|_cache277[\w]*\.txt|_n402[\w]*\.txt|_n403[\w]*\.txt|_n404[\w]*\.txt"
    r"|_p400[\w]*\.txt|_p401[\w]*\.txt|_p402[\w]*\.txt|_p403[\w]*\.txt|_p404[\w]*\.txt"
    r"|_s400[\w]*\.txt|_s401[\w]*\.txt|_s402[\w]*\.txt|_s403[\w]*\.txt|_s404[\w]*\.txt"
    r"|_rd287[\w]*\.txt|_probe255[\w]*\.txt)$"
)

# ── 语料（用于引用检索）：只含**非候选**的保留文件 ──
# 注意：必须显式排除 .venv / node_modules / .git / pytest 临时目录，
# 否则 rglob 会吸入数万个无关文件（且浪费大量 IO）。
SKIP_PARTS = {".venv", "node_modules", ".git", "__pycache__", ".pytest_cache",
              ".pytest_bt", ".pytest_tmp", ".pytest_tmp2", ".pytest_tmp3",
              ".pytest_ws", "tmp_pytest", "logs", "_poc_shots", "vendor",
              "pytest-of-Lenovo", "roleplay_test_qenmhfwr", "_r4replay"}
ALL_FILES: list[str] = []
for g in ("src/**/*", "scripts/**/*", "tests/**/*", "docs/**/*",
          "data/compendium_rag/*", "data/knowledge/**/*", "*.md", "*.toml", "*.bat",
          "frontend/**/*", "desktop/**/*"):
    for q in ROOT.glob(g):
        if not q.is_file():
            continue
        if SKIP_PARTS & set(q.parts):
            continue
        if "node_modules" in q.parts:
            continue
        rel = q.relative_to(ROOT)
        # ⚠ Windows 下 str(Path) 用反斜杠，路径比较/前缀判断必须统一为正斜杠
        ALL_FILES.append(rel.as_posix())

DISCARD_DIR = "data/compendium_rag"
cand = {p for p in ALL_FILES
        if DISCARD_RX.match(p.rsplit("/", 1)[-1])
        and p not in LOCKED
        and p.rsplit("/", 1)[0] == DISCARD_DIR}
print(f"初始候选 = {len(cand)}")

# 保留者 = 非候选且非锁，作为引用来源
texts: dict[str, str] = {}
for p in ALL_FILES:
    if p in cand:
        continue
    fp = ROOT / p
    if fp.stat().st_size > 4_000_000:      # 跳过巨型 JSON/二进制
        continue
    try:
        texts[p] = fp.read_text(encoding="utf-8", errors="replace")
    except Exception:
        pass
print(f"引用语料（保留者）= {len(texts)} 个文件")

# 不动点：反复把"被保留者引用"的候选移出候选集
while True:
    keepers = set(texts)
    newly_kept = {c for c in cand
                  if any(Path(c).name in t for t in texts.values())}
    if not newly_kept:
        break
    # 被保留者引用的候选 => 删除它，并把它加入语料（其被引用者也可能保留）
    saved = len(cand)
    for c in newly_kept:
        cand.discard(c)
        try:
            texts[c] = (ROOT / c).read_text(encoding="utf-8", errors="replace")
        except Exception:
            pass
    if len(cand) == saved:
        break

print()
print("=" * 84)
total = sum((ROOT / c).stat().st_size for c in cand)
print(f"最终可删 = {len(cand)} 个文件，{total/1024/1024:.1f} MB")
print(f"因被保留者引用而保留的候选 = "
      f"{len({p for p in ALL_FILES if DISCARD_RX.match(Path(p).name)}) - len(cand)}")
print("=" * 84)
by_kind: dict[str, int] = {}
for c in cand:
    n = Path(c).name
    k = ("_agent_batch" if n.startswith("_agent_batch") else
         "_gen_batch" if n.startswith("_gen_batch") else
         "_dump" if n.startswith("_dump") else
         "_cands" if n.startswith("_cands") else
         "_fix" if n.startswith("_fix") else
         "_probe" if n.startswith("_probe") else
         "_sim" if n.startswith("_sim") else "其它")
    by_kind[k] = by_kind.get(k, 0) + 1
for k, v in sorted(by_kind.items(), key=lambda kv: -kv[1]):
    print(f"   {k:16} {v}")

out = ROOT / "data/compendium_rag/reports/_cleanup_discard.json"
out.write_text(json.dumps({"n": len(cand), "bytes": total,
                           "files": sorted(cand)},
                          ensure_ascii=False, indent=1), encoding="utf-8")
print(f"\n-> {out.relative_to(ROOT)}")
