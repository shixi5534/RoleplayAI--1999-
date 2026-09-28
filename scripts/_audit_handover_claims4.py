# -*- coding: utf-8 -*-
"""独立复核（第四轮）：§10 提交清单逐条存在性 + 计数声称。"""
from __future__ import annotations

import re
import subprocess
from pathlib import Path

doc = Path("docs/compendium-rag/handover/交接_20260928_总_39全战役.md").read_text(encoding="utf-8")

# 抽出 §10 代码块（阶段一 / 阶段二）
sec = doc.split("## 10. 本会话提交清单")[1]
blocks = re.findall(r"```(.*?)```", sec, re.S)
hashes: list[str] = []
for blk in blocks:
    for line in blk.splitlines():
        m = re.match(r"^([0-9a-f]{7,40})\s+(\S.*)$", line.strip())
        if m:
            hashes.append(m.group(1))

print(f"§10 清单解析出的提交哈希数 = {len(hashes)}")
print(f"§10 标题声称：", end="")
for line in sec.splitlines():
    if "笔" in line and "清单" in line:
        print(line.strip())
        break

print()
missing, ok = [], []
for h in hashes:
    r = subprocess.run(["git", "cat-file", "-e", f"{h}^{{commit}}"],
                       capture_output=True)
    (ok if r.returncode == 0 else missing).append(h)

print(f"  在库 = {len(ok)}")
print(f"  不在库 = {len(missing)}  {missing}")

print()
print("=== 该文档自身提交是否在清单内？===")
head = subprocess.run(["git", "rev-parse", "--short", "HEAD"],
                      capture_output=True, text=True).stdout.strip()
print(f"  当前 HEAD = {head}   在清单内 = {head in hashes}")

print()
print("=== 会话提交数（自 baseline-v5 起）===")
r = subprocess.run(["git", "log", "--oneline", "baseline-v5..HEAD"],
                   capture_output=True, text=True, encoding="utf-8", errors="replace")
lines = [l for l in r.stdout.splitlines() if l.strip()]
print(f"  baseline-v5..HEAD 实际 = {len(lines)} 笔")

print()
print("=== 清单哈希是否与 baseline-v5..HEAD 一致（集合差）===")
actual = {l.split()[0] for l in lines}
listed = set(hashes)
print(f"  清单有、实际无（多余/不存在）: {sorted(listed - actual)}")
print(f"  实际有、清单未列（漏列）    : {sorted(actual - listed)}")
