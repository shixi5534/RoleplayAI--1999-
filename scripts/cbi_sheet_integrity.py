"""抽检单完整性自检（纯只读，一个字节都不写）。

为什么要有：`spotcheck_sheet_{v1,v2}.md` 是**人工那一臂的界面**。四层审计时吃过
"上下文被截到 3000 字符 ⇒ 把'没看到'当成'确实没有'"的亏，所以这里要把界面和证据源对上：
  1) md 表体逐行逐格 == json 原始字段（唯一允许的差：单元格里的 `|` 转义成全角 `／`）
     ⇒ 证明题面 / A 的私密 / B 的私密 / 被试答案**都没被截**；
  2) 「人工」列只能是占位符、json 的 `human_verdict` 必须全空
     ⇒ 证明我没有预填、没有替你标（那一格的定义就是人怎么判）；
  3) 行数 == sheet 生产端的行数，列数每行都是 11 ⇒ 表格没断列。

用法：`PYTHONIOENCODING=utf-8 .venv/Scripts/python.exe scripts/cbi_sheet_integrity.py`
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CBI = ROOT / "data" / "compendium_rag" / "reports" / "cbi"
ESC = "|"                       # 写表时 `|` 被换成全角 `／`（U+FF0F）
HUMAN_PLACEHOLDER = "←填这里"
# 列序：# | tier | sample_id | 机判 | 人工 | A | B | 题面 | A私密 | B私密 | 被试答案
EVIDENCE_COLS = [(7, "prompt"), (8, "a_private_fact"),
                 (9, "b_private_fact"), (10, "answer"), (3, "machine_verdict")]


def check(inst: str, sheet_json: str, sheet_md: str, fails: list[str]) -> None:
    rows = json.loads((CBI / sheet_json).read_text(encoding="utf-8"))["rows"]
    body = [[c.strip() for c in ln.strip().strip("|").split("|")]
            for ln in (CBI / sheet_md).read_text(encoding="utf-8").split("\n")
            if re.match(r"^\|\s*\d+\s*\|", ln)]
    print(f"[{inst}] 表体 {len(body)} 行 / json {len(rows)} 行")
    if len(body) != len(rows):
        fails.append(f"{inst} 表体行数与 json 不一致")
        return
    bad_cols = [i for i, c in enumerate(body, 1) if len(c) != 11]
    diffs = []
    for i, (cell, r) in enumerate(zip(body, rows), 1):
        if len(cell) != 11:
            continue
        for j, key in EVIDENCE_COLS:
            want = (r.get(key) or "").strip().replace(ESC, "／")
            if cell[j] != want:
                diffs.append((i, key, len(cell[j]), len(want)))
    print(f"    断行列数!=11 的行: {bad_cols}")
    print(f"    证据单元格与 json 不等价: {len(diffs)} 处 {diffs[:3]}")
    if diffs or bad_cols:
        fails.append(f"{inst} 界面与证据源不一致（{len(diffs)} 格 / {len(bad_cols)} 断列）")
    human = {c[4] for c in body}
    prefill = [r["sample_id"] for r in rows if r.get("human_verdict")]
    print(f"    人工列取值集合: {human} | json 已预填的行: {len(prefill)}")
    if human != {HUMAN_PLACEHOLDER} or prefill:
        fails.append(f"{inst} 人工列被预填过 ⇒ 这一臂不再是人的判断")
    print(f"    最长行 {max(len(ln) for ln in (CBI / sheet_md).read_text(encoding='utf-8').splitlines())} 字符")


def main() -> int:
    fails: list[str] = []
    check("v1", "spotcheck_sheet.json", "spotcheck_sheet.md", fails)
    check("v2", "spotcheck_sheet_v2.json", "spotcheck_sheet_v2.md", fails)
    print("\nRESULT:", "全部通过（界面未被截短、人工列干净）"
          if not fails else "FAIL -> " + " | ".join(fails))
    return 1 if fails else 0


if __name__ == "__main__":
    raise SystemExit(main())
