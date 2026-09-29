# -*- coding: utf-8 -*-
"""scripts/ 可删集计算（不动点，同 data 版的严格方法）。

保留判据（任一成立即保留）：
  1. 被**保留者**（源码/测试/文档/其它保留脚本）显式引用；
  2. 被验收套件 / 交接核验脚本调用；
  3. 名字属**生产/运维**类（build_/eval_/apply_/acceptance_/gen_ 等）—— 不是一次性探针。
其余"一次性探针/审计/中间实验"脚本为可删候选。
"""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

SKIP = {".venv", "node_modules", ".git", "__pycache__", ".pytest_cache",
        ".pytest_ws", "tmp_pytest", "_poc_shots", "vendor", "_r4replay",
        ".pytest_bt", ".pytest_tmp", ".pytest_tmp2", ".pytest_tmp3",
        "pytest-of-Lenovo", "roleplay_test_qenmhfwr"}


def files(globs: tuple[str, ...]) -> list[str]:
    out = []
    for g in globs:
        for q in ROOT.glob(g):
            if q.is_file():
                rel = q.relative_to(ROOT)
                if not (SKIP & set(rel.parts)):
                    out.append(rel.as_posix())
    return sorted(set(out))


SCRIPTS = files(("scripts/*.py", "scripts/*.sh"))

# ── 生产/运维类脚本：永不删（按语义命名，人工白名单）──
PROD_RX = re.compile(
    r"^(build_|eval_|apply_|acceptance_|gen_|rag_testset_candidates_|"
    r"huiji_|merge_|report_|score_|run_|verify_|compendium_rag_|"
    r"ablate_|ab_|diag_|test_|normalize_|plot_timeline|mark_|audit_full_|"
    r"audit_|acceptance|retrieval|train_|index_|ingest_|export_|import_|"
    r"migrate_|backup_|restore_|cleanup_|serve_|start_|health_)"
)

# ── 一次性前缀：删候选 ──
ONESHOT_RX = re.compile(
    r"^(_85_|_decide_|_side_|_p3_|_p4_|_miss_|_r5_|_lex_|_fusion_|_blind_|"
    r"_check_|_audit_handover|_probe|_sim|_fix|_batch|_tmp|_debug|_diag_|"
    r"_compare|_analyze_|_ce_|_chk|_dbg|_exp_|_test_|_scan|_sweep|_grid|"
    r"_rank_|_score_|_dump|_n\d|_c\d|_p\d|_s\d|_replay|_r2_|_weld|_union)"
)

ALL_SRC = files(("src/**/*.py", "tests/**/*.py", "tests/**/*.js",
                 "docs/**/*.md", "*.md", "pyproject.toml", "*.bat",
                 "frontend/**/*.js", "scripts/**/*.py", "scripts/**/*.sh"))

# 语料：排除候选脚本自身
cand_init = {s for s in SCRIPTS if ONESHOT_RX.match(Path(s).name)
             and not PROD_RX.match(Path(s).name)}
print(f"scripts 总数 = {len(SCRIPTS)}   初始一次性候选 = {len(cand_init)}")

texts: dict[str, str] = {}
for p in ALL_SRC:
    if p in cand_init:
        continue
    fp = ROOT / p
    try:
        if fp.stat().st_size < 2_000_000:
            texts[p] = fp.read_text(encoding="utf-8", errors="replace")
    except Exception:
        pass
print(f"引用语料 = {len(texts)} 个文件")

kept: set[str] = set()
changed = True
while changed:
    changed = False
    for c in sorted(cand_init - kept):
        name = Path(c).name
        if any(name in t for t in texts.values()):
            kept.add(c)
            try:
                texts[c] = (ROOT / c).read_text(encoding="utf-8", errors="replace")
            except Exception:
                pass
            changed = True

dele = sorted(cand_init - kept)
print()
print("=" * 84)
print(f"可删脚本 = {len(dele)} / {len(SCRIPTS)}")
print(f"保留（被引用/生产类）= {len(kept)}")
print("=" * 84)
pref: dict[str, int] = {}
for s in dele:
    m = re.match(r"^(_[a-z0-9]+)", Path(s).stem)
    k = m.group(1) if m else "(其它)"
    pref[k] = pref.get(k, 0) + 1
for k, v in sorted(pref.items(), key=lambda kv: -kv[1])[:20]:
    print(f"   {k:16} {v}")

out = ROOT / "data/compendium_rag/reports/_cleanup_scripts_discard.json"
out.write_text(json.dumps({"n": len(dele), "files": dele,
                           "kept_referenced": sorted(kept)},
                          ensure_ascii=False, indent=1), encoding="utf-8")
print(f"\n-> {out.relative_to(ROOT)}")
print("\n可删样例（前 12）：")
for s in dele[:12]:
    print(f"   {s}")
