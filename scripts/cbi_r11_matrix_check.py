"""闸门矩阵自检（纯只读）：P10 §R11 那张表的每个数字都必须能直接从读数产物里取到。

为什么要单独留这个脚本：R11 是**汇总表面**，它是这一轮里最容易被后续改动悄悄带偏的一类文字
—— 读数重跑一次、子标准多一格，正文不会报错，只有表会开始说谎。所以把三件事变成断言：
  1) 表里四行的 counts / CBI 与产物字段逐一相等（三个仪器读数 + 叠加列的两把尺子）；
  2) 三个仪器读数里 false 的子标准**只有** "人工抽检 kappa>=0.80"，且 κ 的详情写的是"未达成"
     （没测 ≠ 测了不过，这条区分是 §R11 的立论前提）；
  3) 叠加列 `cbi_result_v2hard.json` **不含** MRR / Faithfulness 字段 ——
     那两条是三个仪器读数共用的基线，引用叠加列时不能顺手替它答。
另外核正文里的四个数字串确实出现在表里（防止脚本与文字各说各话）。

用法：`PYTHONIOENCODING=utf-8 .venv/Scripts/python.exe scripts/cbi_r11_matrix_check.py`
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
R = ROOT / "data" / "compendium_rag" / "reports"
P10 = (ROOT / "docs" / "compendium-rag" / "P10修复计划_CBI收口.md").read_text(encoding="utf-8")
REPORT = (ROOT / "docs" / "compendium-rag" / "P9_CBI报告.md").read_text(encoding="utf-8")

INSTRUMENT_READINGS = {
    "cbi_result_full.json": (0, 3, 21, 0.9844),
    "cbi_result_v2instrument.json": (0, 0, 30, 0.982),
    "cbi_result_v2instrument_v2_r2.json": (0, 0, 30, 0.982),
}
KAPPA_KEY = "人工抽检 kappa>=0.80"


def load(name: str) -> dict:
    return json.loads((R / name).read_text(encoding="utf-8"))


def main() -> int:
    fails: list[str] = []
    for name, expect in INSTRUMENT_READINGS.items():
        d = load(name)
        c = d["counts"]
        got = (c["N_hard"], c["N_soft"], c["N_retrieval"], d["cbi"]["measured"])
        false_only = sorted(k for k, v in d["sub_criteria"].items() if not v)
        print(f"{name}: {got} == 表值 {expect} 且 false 只有 κ："
              f"{got == expect and false_only == [KAPPA_KEY]}")
        if got != expect:
            fails.append(f"{name} 计数/CBI 与表不符：{got} != {expect}")
        if false_only != [KAPPA_KEY]:
            fails.append(f"{name} false 的子标准不止 κ：{false_only}")
        if "未达成" not in json.dumps(d.get("sub_details"), ensure_ascii=False):
            fails.append(f"{name} 的 κ 没写成『未达成』（没测与测了不过必须能区分）")

    hv = load("cbi_result_v2hard.json")
    rv2, rv1 = hv["ruler_v2"], hv["ruler_v1"]
    print(f"叠加列: ruler_v2 {rv2['counts']} {rv2['cbi']} failed={rv2['failed_gates']}")
    if (rv2["counts"]["hard"], rv2["cbi"]) != (4, 0.9764):
        fails.append("叠加列 hard=4 / CBI=0.9764 与表不符")
    if rv2["gates"]["N_hard=0"] is not False:
        fails.append("叠加列 N_hard=0 应为 false")
    if (rv1["counts"]["hard"], rv1["cbi"]) != (0, 0.9844):
        fails.append("叠加列的 ruler_v1 应与 cbi_result_full 同值")
    if "MRR" in json.dumps(hv, ensure_ascii=False):
        fails.append("叠加列里出现了 MRR 字段 —— §R11 说它不该有，得改文字或改产物")

    for pat in (r"\| 0 \| 3 \| 21 \| 0\.9844 \|",
                r"\| \*\*4\*\* \| 3 \| 21 \| 0\.9764 \|",
                r"\| 0 \| 0 \| 30 \| 0\.9820 \|"):
        if not re.search(pat, P10):
            fails.append(f"§R11 表里找不到 {pat}")
    if "§R11" not in REPORT:
        fails.append("报告 §4 没有指向 §R11")
    if "判分尺子的条款号" not in REPORT:
        fails.append("报告里 R2/R3 的命名冲突（尺子条款 vs P10 项）没被澄清")

    print("\nRESULT:", "§R11 的每个数都来自产物" if not fails else "FAIL -> " + " | ".join(fails))
    return 1 if fails else 0


if __name__ == "__main__":
    raise SystemExit(main())
