# -*- coding: utf-8 -*-
"""三层正例口径统一报告（P0-1）—— **零生产改动**，只读已有评测报告。

为什么必须分开报告
    本项目同一个"召回"在不同口径下差了近一倍，混着读必然误判：

    | 层级 | 口径 | 当前值 | 回答的问题 |
    |---|---|---|---|
    | 子块级 | 返回块里命中 oracle 的比例 | answer_chunk_rate 25.3% | 单个块找对了吗 |
    | 覆盖级 | 返回块**并集**覆盖全部证据组 | strict_pass 67.67% | 拼起来能答对吗 |
    | 产品级 | **注入的 2400 字符内**覆盖 | inject_pass 62.00% | 模型真能看到吗 |

    再加一个必须单列的东西：官方 `recall` 的**分母定义**——
    `recall = min(单块全覆盖块数, min(top,len(full))) / min(top,len(full))`，
    语料里没有"单块覆盖全部证据组"的题（`ceiling=False`）**恒为 0**，
    那是指标定义造成的，不是检索失败。本轮实测这类题 14 道（4.7%）。

用法
    .venv/Scripts/python.exe -X utf8 scripts/report_metric_tiers.py
    .venv/Scripts/python.exe -X utf8 scripts/report_metric_tiers.py --report <路径>
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT / "data" / "knowledge" / "_audit"
OUT = AUDIT / "_metric_tiers.txt"
DEFAULT = AUDIT / "plot_rag_eval_report_clean.json"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--report", default=str(DEFAULT))
    args = ap.parse_args()

    p_path = Path(args.report)
    buf: list[str] = []

    def p(*a):
        buf.append(" ".join(str(x) for x in a))

    if not p_path.is_file():
        OUT.write_text(f"[MISSING] {p_path}", encoding="utf-8")
        return 1

    d = json.loads(p_path.read_text(encoding="utf-8"))
    items = d.get("items") or []
    s = d.get("summary") or {}
    n = len(items) or 1

    p("=" * 84)
    p(f"三层正例口径统一报告｜{p_path.name}｜n={len(items)}")
    p("=" * 84)

    # —— 子块级 ——
    hit_any = sum(1 for it in items if (it.get("n_relevant") or 0) > 0)
    hit_full_blk = sum(1 for it in items if (it.get("n_full_match") or 0) > 0)
    avg_rel = sum((it.get("n_relevant") or 0) for it in items) / n
    avg_chunks = sum((it.get("n_chunks") or 0) for it in items) / n
    # —— 覆盖级 / 产品级 ——
    strict = sum(1 for it in items if it.get("strict_pass")) / n
    inject = sum(1 for it in items if it.get("inject_pass")) / n

    p()
    p(f"{'层级':<10}{'指标':<22}{'数值':>10}{'含义':>40}")
    p("-" * 84)
    p(f"{'子块级':<10}{'答案块命中题占比':<22}{hit_any / n:>10.1%}{'返回里有任何相关块':>40}")
    p(f"{'':<10}{'全覆盖块命中题占比':<22}{hit_full_blk / n:>10.1%}{'返回里有单块可答的块':>40}")
    p(f"{'':<10}{'平均相关块数/返回块数':<22}"
      f"{avg_rel:>6.2f}/{avg_chunks:<3.2f}{'块级精度（chunk_precision 同源）':>40}")
    p(f"{'覆盖级':<10}{'strict_pass':<22}{strict:>10.2%}{'返回并集覆盖全部证据组':>40}")
    p(f"{'产品级':<10}{'inject_pass':<22}{inject:>10.2%}{'2400 字符注入内覆盖（决策依据）':>40}")
    p("-" * 84)
    p(f"{'分层差':<10}{'覆盖级 − 产品级':<22}"
      f"{strict - inject:>+10.2%}{'「返回了但没进提示词」的损失':>40}")
    p(f"{'':<10}{'产品级 − 子块级':<22}"
      f"{inject - hit_any / n:>+10.2%}{'并集覆盖弥补了部分单块缺失':>40}")

    # —— recall 口径修正 ——
    no_ceil = [it for it in items if not it.get("ceiling")]
    with_ceil = [it for it in items if it.get("ceiling")]
    raw_recall = s.get("recall") or 0.0
    recall_ex = (sum((it.get("recall") or 0.0) for it in with_ceil) / len(with_ceil)
                 if with_ceil else 0.0)
    p()
    p("=" * 84)
    p("官方 recall 口径修正")
    p("=" * 84)
    p(f"  官方 recall 定义：min(单块全覆盖块数, min(top,len(full))) / min(top,len(full))")
    p(f"  官方值                        ：{raw_recall:.4f}")
    p(f"  · 语料里**没有**单块可答块的题 ：{len(no_ceil)} 题（{len(no_ceil) / n:.1%}）"
      f"→ recall 恒为 0，**属指标定义，不是检索失败**")
    p(f"  · 剔除这批后的 recall          ：{recall_ex:.4f}"
      f"（{len(with_ceil)} 题的均值）")
    p(f"  ⇒ 引用 recall 时必须同时标注「含 {len(no_ceil)} 题的指标性零值」，")
    p(f"    否则会把 4.7% 的口径噪声当成检索退化。")

    p()
    p("=" * 84)
    p("一句话读法")
    p("=" * 84)
    p(f"  子块级 {hit_any / n:.1%} → 覆盖级 {strict:.1%} → 产品级 {inject:.1%}。")
    p(f"  子块级低而覆盖级高 ⇒ 靠多块并集补上，**不是块级检索不行**；")
    p(f"  覆盖级高而产品级低 ⇒ **是排序/装配问题**，不是召回问题。")
    p("=" * 84)

    OUT.write_text("\n".join(buf), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
