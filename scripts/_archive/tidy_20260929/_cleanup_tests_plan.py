# -*- coding: utf-8 -*-
"""tests/ 精简决策：区分**长期回归测试**与**一次性验证脚本**。

判据（可核验）：
  · pytest 是否收集（test_*.py 且能 import）
  · 是否属于"QA 一次性验证/交付核对"（test_qa_*、voice_repro/*、e2e_*）
  · 是否有对应 src 模块（无对应 = 测的是历史快照）
输出决策表供人工复核，不直接删。
"""
from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
r = subprocess.run(["git", "ls-files", "-z"], cwd=str(ROOT), capture_output=True)
TRACKED = [p for p in r.stdout.decode("utf-8", "replace").split("\0") if p]
tests = sorted(p for p in TRACKED if p.startswith("tests/"))

# 一次性验证/交付核对类（按语义命名）
ONESHOT_RX = re.compile(
    r"^(test_qa_|qa_consistency|e2e_)|^tests/voice_repro/"
)
# 重放/验证特定修复的（对应已闭合的历史问题）
HISTORY_RX = re.compile(
    r"^(test_plotrag_m0_|test_plotrag_p0|test_plotrag_optimization|"
    r"test_plotrag_huiji_canon|test_plotrag_real_dialogue|test_wiki_canonical|"
    r"test_rag_graphrag_audit|test_plotrag_semantic|test_plotrag_trace|"
    r"test_plotrag_negative_guard|test_plotrag_eval_|test_plot_graph|"
    r"test_plot_timeline|test_plot_graph_retrieval_live|test_prompt_p)"
)

rows = []
for t in tests:
    p = ROOT / t
    if not p.is_file():
        continue
    name = Path(t).name
    lines = len(p.read_text(encoding="utf-8", errors="replace").splitlines())
    collected = name.startswith("test_") and name.endswith(".py")
    oneshot = bool(ONESHOT_RX.search(t))
    hist = bool(HISTORY_RX.match(name))
    rows.append({"path": t, "lines": lines, "collected": collected,
                 "oneshot": oneshot, "history": hist})

print(f"tests/ 已跟踪文件 = {len(rows)}\n")
print(f"{'lines':>6}  {'collect':7} {'oneshot':7} {'history':7}  path")
print("-" * 100)
for x in sorted(rows, key=lambda z: -z["lines"]):
    print(f"{x['lines']:>6}  {str(x['collected']):7} {str(x['oneshot']):7} "
          f"{str(x['history']):7}  {x['path']}")

oneshot = [x for x in rows if x["oneshot"]]
hist = [x for x in rows if x["history"] and not x["oneshot"]]
core = [x for x in rows if not x["oneshot"] and not x["history"]]
print()
print("=" * 100)
print(f"一次性验证类 = {len(oneshot)}   历史专项类 = {len(hist)}   核心回归类 = {len(core)}")
print("=" * 100)
print("\n一次性验证类（建议合并/精简）:")
for x in sorted(oneshot, key=lambda z: -z["lines"]):
    print(f"   {x['lines']:>5}  {x['path']}")
print("\n历史专项类（对应已闭合问题，可评估保留）:")
for x in sorted(hist, key=lambda z: -z["lines"]):
    print(f"   {x['lines']:>5}  {x['path']}")
print("\n核心回归类（须保留）:")
for x in sorted(core, key=lambda z: -z["lines"]):
    print(f"   {x['lines']:>5}  {x['path']}")

out = ROOT / "data/compendium_rag/reports/_tests_plan.json"
out.write_text(json.dumps(rows, ensure_ascii=False, indent=1), encoding="utf-8")
print(f"\n-> {out.relative_to(ROOT)}")
