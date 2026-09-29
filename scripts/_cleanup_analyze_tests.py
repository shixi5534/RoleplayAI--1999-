# -*- coding: utf-8 -*-
"""分析 pytest 日志：区分**真实失败**与**环境（沙箱）造成的 ERROR**。

为什么必须先分：删测试的判据若是"跑不过"，必须确认那是代码问题而非本机权限问题。
本机沙箱下 pytest 的 tmp 目录不可写，会产生大量 PermissionError 假错误。
"""
from __future__ import annotations

import re
from collections import Counter
from pathlib import Path

LOG = Path("data/compendium_rag/reports/_cleanup_pytest.log")
text = LOG.read_text(encoding="utf-8", errors="replace")

print("=" * 84)
print("① 总结行")
print("=" * 84)
for ln in text.splitlines():
    if re.search(r"\d+ (passed|failed|error)", ln):
        print("  " + ln.strip())

print()
print("=" * 84)
print("② ERROR 归因（按异常类型）")
print("=" * 84)
err_lines = [l for l in text.splitlines() if l.startswith("ERROR ")]
print(f"  ERROR 总数（行）= {len(err_lines)}")
kinds = Counter()
for l in err_lines:
    m = re.search(r"- (\w+Error|\w+Exception|Failed|assert)", l)
    kinds[m.group(1) if m else "(未标注)"] += 1
for k, v in kinds.most_common():
    print(f"    {k:24} {v}")
print()
perm = [l for l in err_lines if "PermissionError" in l]
print(f"  ⇒ 其中 PermissionError（**本机沙箱造成，非代码问题**）= {len(perm)}")
other = [l for l in err_lines if "PermissionError" not in l]
print(f"  ⇒ 其它 ERROR = {len(other)}")
for l in other[:15]:
    print(f"      {l[:150]}")

print()
print("=" * 84)
print("③ FAILED 归因（按测试文件）")
print("=" * 84)
fail_lines = [l for l in text.splitlines() if l.startswith("FAILED ")]
print(f"  FAILED 总数 = {len(fail_lines)}")
byfile = Counter(l.split("::")[0].replace("FAILED ", "").strip() for l in fail_lines)
for f, n in byfile.most_common():
    print(f"    {n:3}  {f}")
print()
for l in fail_lines:
    print(f"      {l[:160]}")
