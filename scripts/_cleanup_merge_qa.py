# -*- coding: utf-8 -*-
"""把 4 个 QA 验证文件合并为 1 个 `test_qa_verification.py`。

依据（已核验）：
  · test_qa_scratch_max.py（24 行）是**临时调试脚本**（含 print），
    其断言 `max_items=0 → count()==0` 已被 test_qa_profile_verify.py:230 覆盖
    => 完全冗余，直接丢弃。
  · 其余 3 个（independent_verify 328 行 / profile_verify 663 行 /
    profile_r2_verify 162 行）覆盖**互不重叠**的边界集（情绪检测边界、
    画像边界、并发竞态），合并后仍全部保留，但去掉重复的 import/fixture 样板。

合并方式：**按原文件顺序拼接主体**，保留各自的 fixture，避免语义漂移；
顶部加统一说明，标注每段的来源与原始行数。
"""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

SOURCES = [
    ("tests/test_qa_independent_verify.py",
     "情绪检测边界（归一化 / 责任链穿透 / 父类回退 / SSE 契约）"),
    ("tests/test_qa_profile_verify.py",
     "用户画像边界（去重 / 提取器 / 注入 / 并发隔离 / 击穿）"),
    ("tests/test_qa_profile_r2_verify.py",
     "画像并发竞态（多 key×多任务 / 锁语义 / 无死锁 / 共享 KB）"),
]

HEADER = '''# -*- coding: utf-8 -*-
"""QA 边界验证合集（由 3 份独立 QA 报告合并，2026-09-29）。

覆盖**边界与击穿**场景，与 `test_emotion.py` / `test_profile.py` 的常规路径互补：
  ① 情绪检测边界（归一化 / 责任链穿透 / 父类回退 / SSE 契约）
  ② 用户画像边界（去重 / 提取器 / 注入 / 并发隔离 / 击穿）
  ③ 画像并发竞态（多 key×多任务 / 锁语义 / 无死锁 / 共享 KB）

> 合并说明：原为 3 个文件（328 + 663 + 162 行），因**互不重叠**故仅做拼接，
> 保留各自 fixture 与断言，不改语义。原独立的临时调试脚本
> `test_qa_scratch_max.py`（24 行，含 print）已删 —— 其断言
> （`_max_items=0 → count()==0`）已被本文件 ② 段覆盖。
>
> 依据与决策表：`data/compendium_rag/reports/_tests_plan.json`
"""
'''

parts: list[str] = [HEADER]
for rel, desc in SOURCES:
    p = ROOT / rel
    if not p.exists():
        print(f"  [skip] {rel} 不存在")
        continue
    text = p.read_text(encoding="utf-8")
    lines = text.splitlines()
    # 去掉原文件的模块 docstring（前导 """..."""）与 __future__/编码行
    body: list[str] = []
    i = 0
    # 跳过 shebang / coding / 开头 docstring
    while i < len(lines):
        s = lines[i].strip()
        if s.startswith("# -*-") or s.startswith("#!") or not s:
            i += 1
            continue
        if s.startswith('"""') or s.startswith("'''"):
            q = s[:3]
            if s.count(q) >= 2 and len(s) > 3:
                i += 1
                continue
            i += 1
            while i < len(lines) and q not in lines[i]:
                i += 1
            i += 1
            continue
        break
    body = lines[i:]
    # 去掉重复的 __future__ import
    body = [ln for ln in body if "__future__" not in ln]
    parts.append(f"\n\n# {'=' * 76}\n"
                 f"# 来源：{rel}（原 {len(lines)} 行）—— {desc}\n"
                 f"# {'=' * 76}\n")
    parts.append("\n".join(body).strip() + "\n")

out = ROOT / "tests/test_qa_verification.py"
out.write_text("".join(parts), encoding="utf-8")
print(f"[ok] -> {out.relative_to(ROOT)}  "
      f"({len(out.read_text(encoding='utf-8').splitlines())} 行)")
