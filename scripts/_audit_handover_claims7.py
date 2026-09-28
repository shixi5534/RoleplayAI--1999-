# -*- coding: utf-8 -*-
"""第七轮：collect/eval 三方交叉对账 + 该文档提交清单核验。"""
from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path

R = Path("data/compendium_rag/reports")


def ans_hits(f: str, mode: str = "full") -> tuple[int, int]:
    d = json.loads((R / f).read_text(encoding="utf-8"))
    rows = [r for r in d["rows"] if r.get("mode") == mode and r.get("answerable")]
    return sum(1 for r in rows if r.get("hit")), len(rows)


print("=" * 88)
print("① 300cn full answerable hit —— collect 汇总 / collect rows / eval 三方对账")
print("=" * 88)
c = json.loads((R / "rank_collect_v6c300_top30.json").read_text(encoding="utf-8"))
h, n = ans_hits("rank_collect_v6c300_top30.json")
print(f"  collect summary full.answerable.hit6 = {c['summary']['full']['answerable']['hit6']} (n={c['summary']['full']['answerable']['n']})")
print(f"  collect rows 重算                     = {h}/{n} = {h/n:.4f}")
for f in ["eval_300cn_lex_tiebreak.json", "eval_300cn_lexfirst.json",
          "eval_300cn_lex_on.json"]:
    h2, n2 = ans_hits(f)
    mark = "  <-- BASELINE_v6 锁定的就是这个文件" if f == "eval_300cn_lex_on.json" else ""
    print(f"  {f:34} = {h2}/{n2} = {h2/n2:.4f}{mark}")
print()
print("  → 0.8418 在 collect / tiebreak / lexfirst 三处一致；")
print("    但被锁定的 eval_300cn_lex_on.json 只有 0.8367（在 tiebreak 修复之前跑）。")

print()
print("=" * 88)
print("② 专文（召回率85目标收官）§10 提交清单核验")
print("=" * 88)
doc = Path("docs/compendium-rag/handover/交接_20260928_召回率85目标收官与融合重构.md").read_text(encoding="utf-8")
sec = doc.split("## 10. 本会话提交清单")[1]
hashes = re.findall(r"(?m)^([0-9a-f]{7})\s", sec)
print(f"  清单解析哈希数 = {len(hashes)}")
missing = []
for hh in hashes:
    r = subprocess.run(["git", "cat-file", "-e", f"{hh}^{{commit}}"], capture_output=True)
    if r.returncode != 0:
        missing.append(hh)
print(f"  在库={len(hashes)-len(missing)}  不在库={len(missing)} {missing}")
print(f"  文档标题声称 15 笔；实际列出 {len(hashes)} 笔")
