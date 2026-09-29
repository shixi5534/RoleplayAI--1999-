# -*- coding: utf-8 -*-
"""tests/ 精简的**最终决策依据**：确认哪些是"未被 pytest 收集的一次性脚本"。

pytest 配置：testpaths=["tests"]，默认 python_files=test_*.py。
故 `tests/voice_repro/repro.py`、`tests/qa_consistency_check.py`、
`tests/e2e_pet_voice.py`、`tests/test_pet_master_plan.js` **不会被收集** ——
它们是手工调试脚本，不是回归测试。

同时核验它们是否被其它文件引用（被引用则保留）。
"""
from __future__ import annotations

import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

NOT_COLLECTED = [
    "tests/voice_repro/repro.py",
    "tests/voice_repro/repro2.py",
    "tests/voice_repro/repro3.py",
    "tests/qa_consistency_check.py",
    "tests/e2e_pet_voice.py",
    "tests/test_pet_master_plan.js",
]

# 引用来源（排除自身）
r = subprocess.run(["git", "ls-files", "-z"], cwd=str(ROOT), capture_output=True)
TRACKED = [p for p in r.stdout.decode("utf-8", "replace").split("\0") if p]
SKIP = {".venv", "node_modules", ".git", "__pycache__"}

texts: dict[str, str] = {}
for p in TRACKED:
    if p in NOT_COLLECTED:
        continue
    if SKIP & set(Path(p).parts):
        continue
    fp = ROOT / p
    try:
        if fp.stat().st_size < 3_000_000:
            texts[p] = fp.read_text(encoding="utf-8", errors="replace")
    except Exception:
        pass

print("=" * 88)
print("未被 pytest 收集的文件 —— 引用核验")
print("=" * 88)
result = {}
for t in NOT_COLLECTED:
    fp = ROOT / t
    if not fp.exists():
        continue
    name = Path(t).name
    hits = [k for k, v in texts.items() if name in v]
    size = len(fp.read_text(encoding="utf-8", errors="replace").splitlines())
    result[t] = {"lines": size, "referenced_by": hits}
    status = f"被引用 {hits[:3]}" if hits else "零引用"
    print(f"  {t:40} {size:>4} 行   {status}")

print()
print("=" * 88)
print("结论")
print("=" * 88)
zero = [t for t, v in result.items() if not v["referenced_by"]]
print(f"  零引用（可删/合并）= {len(zero)}")
for t in zero:
    print(f"     {t}  ({result[t]['lines']} 行)")
print(f"  被引用（须保留）= {len(result)-len(zero)}")

out = ROOT / "data/compendium_rag/reports/_tests_notcollected.json"
out.write_text(json.dumps(result, ensure_ascii=False, indent=1), encoding="utf-8")
print(f"\n-> {out.relative_to(ROOT)}")
