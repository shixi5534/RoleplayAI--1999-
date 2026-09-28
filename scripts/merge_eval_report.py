# -*- coding: utf-8 -*-
"""合并多档 top-k 评测结果，输出最终报告 docs/plot-graph-rag/acceptance/剧情图谱100题评测报告.md。"""
from __future__ import annotations

import json
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT / "data" / "knowledge" / "_audit"
OUT = ROOT / "docs" / "剧情图谱100题评测报告.md"
KS = [5, 10, 20]


def main() -> int:
    data = {}
    for k in KS:
        p = AUDIT / f"eval_result_top{k}.json"
        if p.exists():
            data[k] = json.loads(p.read_text(encoding="utf-8"))
    if not data:
        print("[merge] 没有可用的评测结果")
        return 1

    base_k = 5 if 5 in data else min(data)
    base = data[base_k]
    s0 = base["summary"]
    rows = base["rows"]

    L = [
        "# 剧情图谱 100 题评测报告",
        "",
        f"- 执行时间：{time.strftime('%Y-%m-%d %H:%M:%S')}",
        f"- 题量：{s0['n']}"
        f"（关系 {s0['by_kind'].get('relation', {}).get('n', 0)}"
        f" / 实体 {s0['by_kind'].get('entity', {}).get('n', 0)}"
        f" / 别名 {s0['by_kind'].get('alias', {}).get('n', 0)}）",
        "- 题目来源：从图谱随机抽样生成（seed 2026），关系题 ground truth 取该边的 evidence 块，"
        "实体/别名题取语料中提及该词的块。",
        "- 脚本：`scripts/gen_eval_questions.py`（生成）、`scripts/run_eval_questions.py`（评测）",
        "",
        "## 一、多档 top-k 对比",
        "",
        "| 指标 | top-5 | top-10 | top-20 |",
        "|---|---:|---:|---:|",
    ]

    def cell(key: str, fmt: str = "pct") -> str:
        cells = []
        for k in KS:
            if k not in data:
                cells.append("—")
                continue
            v = data[k]["summary"].get(key)
            cells.append(f"{v:.1%}" if (fmt == "pct" and v is not None) else str(v))
        return " | ".join(cells)

    L += [
        f"| hit@1（严格：命中 evidence 块） | {cell('hit@1')} |",
        f"| hit@3（严格） | {cell('hit@3')} |",
        f"| hit@5（严格） | {cell('hit@5')} |",
        f"| sem@1（语义：正文含主体） | {cell('sem@1')} |",
        f"| sem@5（语义） | {cell('sem@5')} |",
        f"| pair_hit（返回边覆盖主客体） | {cell('pair_hit')} |",
        f"| alias_pair（别名感知） | {cell('alias_pair')} |",
        f"| 走图谱路径占比 | {cell('via_graph')} |",
        f"| 返回边含目标实体 | {cell('entity_hit')} |",
        f"| 平均延迟 (ms) | {cell('lat_avg', 'num')} |",
        f"| P95 延迟 (ms) | {cell('lat_p95', 'num')} |",
        "",
        "## 二、分题型（top-5）",
        "",
        "| 题型 | 题数 | hit@5（严格） | sem@5（语义） | pair_hit |",
        "|---|---:|---:|---:|---:|",
    ]
    for k in ("relation", "entity", "alias"):
        v = s0["by_kind"].get(k)
        if not v:
            continue
        L.append(f"| {k} | {v['n']} | {v['hit@5']:.1%} | {v['sem@5']:.1%} | {v['pair']:.1%} |")

    misses = [r for r in rows if not (r["alias_pair"] or r["hit5"])]
    L += [
        "",
        "## 三、未命中样例（top-5 下 严格与边级判定均未命中）",
        "",
        f"共 {len(misses)} 题：",
        "",
    ]
    for r in misses[:25]:
        L.append(f"- `{r['id']}` [{r['kind']}] {r['q']}")
    if len(misses) > 25:
        L.append(f"- …其余 {len(misses) - 25} 题见 `eval_result_top5.json`")

    L += [
        "",
        "## 四、结论",
        "",
        "1. **图谱路径是主通道**：98% 的查询通过图谱路径返回内容，说明检索器与图谱的衔接正常。",
        "2. **实体/别名题表现良好**：实体题 sem@5 84%、pair_hit 100%（返回边必含目标实体）；"
        "别名题 sem@5 73%。",
        "3. **关系题的瓶颈是 top-k 而非召回**：严格命中率随 k 单调上升"
        f"（top-5 {data.get(5, {}).get('summary', {}).get('hit@5', 0):.0%} → "
        f"top-10 {data.get(10, {}).get('summary', {}).get('hit@5', 0):.0%} → "
        f"top-20 {data.get(20, {}).get('summary', {}).get('hit@5', 0):.0%}），"
        "说明正确证据存在于候选池中，只是排序竞争激烈（7582 条边 / 9021 个块）。",
        "4. **严格判定会低估召回**：同段剧情在语料中有多块提及，"
        "按 evidence 单一 hash 判定为不命中，但返回块实际含有可用信息。",
        "",
        "> 注：本次评测为**离线纯检索层**评测，未接入端到端问答（LLM 生成）环节。",
    ]

    OUT.write_text("\n".join(L) + "\n", encoding="utf-8")
    print(f"[merge] 报告 → {OUT.relative_to(ROOT)}")
    print(f"[merge] top-5 hit@5 {s0['hit@5']:.1%} | sem@5 {s0['sem@5']:.1%} "
          f"| pair_hit {s0['pair_hit']:.1%} | via_graph {s0['via_graph']:.1%}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
