# -*- coding: utf-8 -*-
"""M-12 消融矩阵串行跑批（单进程串行：并发会污染延迟口径）。

顺序（每步一个报告，全部可单独复跑）：
  R0       主轮（含埋点轮）→ plot_rag_eval_report_r0.json（同时是 C4 消融的参照轮）
  R-D1-on  D1 全开一轮 → ablation/d1_on.json（作为 D1 消融的**参照轮**）
  R-D1-off D1 消融（pass_on = d1_on，pass_off = 本轮实跑）→ ablation/d1_off.json
  R-C4-off C4 消融（pass_on = r0，pass_off = 本轮实跑）→ ablation/c4_off.json
            （C4 的 off 值 = 空串 = 无豁免 = P0-1 改造前的过滤口径）

**串行**跑批的理由：本项目延迟判据是 p95 增量 ≤100ms，并发两轮会互相抢 CPU/嵌入服务，
测出来的是排队时间而不是组件开销（延迟三口径的第一条就是"同条件"）。

用法：.venv/Scripts/python.exe -X utf8 scripts/run_ablation_matrix.py [--only R0]
"""
from __future__ import annotations

import argparse
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PY = str(ROOT / ".venv" / "Scripts" / "python.exe")
EVAL = str(ROOT / "scripts" / "eval_plot_rag.py")
AUDIT = ROOT / "data" / "knowledge" / "_audit"
BASE = AUDIT / "plot_rag_eval_report_p0_2_baseline.json"

STEPS: list[tuple[str, list[str]]] = [
    ("R0", [
        EVAL, "--quiet", "--check-targets",
        "--baseline", str(BASE),
        "--out", str(AUDIT / "plot_rag_eval_report_r0.json"),
    ]),
    ("R-D1-on", [
        # 参照轮：D1 全开跑一轮（开关由环境变量注入，见下方 env）。
        # **不带 --ablate-flag**：它是参照，不是消融；它自己出 ablation 就是自我参照。
        EVAL, "--quiet", "--no-trace", "--check-targets",
        "--baseline", str(BASE),
        "--out", str(AUDIT / "ablation" / "d1_on.json"),
    ]),
    ("R-D1-off", [
        EVAL, "--quiet", "--no-trace", "--check-targets",
        "--ablate-flag", "plot_ppr_node_specificity",
        "--ablate-on", "true", "--ablate-off", "false",
        "--ablate-reference", str(AUDIT / "ablation" / "d1_on.json"),
        "--out", str(AUDIT / "ablation" / "d1_off.json"),
    ]),
    ("R-C4-off", [
        EVAL, "--quiet", "--no-trace", "--check-targets",
        "--ablate-flag", "plot_weak_exempt_sources",
        "--ablate-on", "manual", "--ablate-off", "",
        "--ablate-reference", str(AUDIT / "plot_rag_eval_report_r0.json"),
        "--out", str(AUDIT / "ablation" / "c4_off.json"),
    ]),
]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", default="", help="只跑某一步（名字见 STEPS）")
    args = ap.parse_args()
    (AUDIT / "ablation").mkdir(parents=True, exist_ok=True)
    rc_all = 0
    for name, cmd in STEPS:
        if args.only and args.only != name:
            continue
        t0 = time.time()
        print(f"\n{'=' * 70}\n[step] {name}  ({time.strftime('%H:%M:%S')})\n{'=' * 70}",
              flush=True)
        # 第一步（D1 全开）需要临时把开关打开：用环境变量注入，不改配置文件
        env = None
        if name == "R-D1-on":
            import os
            env = dict(os.environ, ROLEPLAY_PLOT_PPR_NODE_SPECIFICITY="true")
        p = subprocess.run([PY, "-X", "utf8", *cmd], cwd=str(ROOT), env=env)
        print(f"[step] {name} 退出码 {p.returncode}｜耗时 {time.time() - t0:.0f}s", flush=True)
        rc_all = rc_all or p.returncode
    print(f"\n[matrix] 全部完成，退出码（按位或）{rc_all}")
    return rc_all


if __name__ == "__main__":
    raise SystemExit(main())
