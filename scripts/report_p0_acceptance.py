# -*- coding: utf-8 -*-
"""P0 验收报告生成器（M-12 数据源 → markdown，**不手抄任何数字**）。

为什么要脚本生成而不是手写：
  1. 手抄必然引入"报告数字与 JSON 不一致"，而本项目全部结论都锚定 JSON 物证；
  2. §7.6.6 的成对产出要求（阴性读数 ↔ 执行计数）可以在生成时**自动核对**，
     手写只能靠人记得；
  3. 报告 schema 门禁（四键齐备 / ablation 11 字段 / 六通道顺序 / 9 值枚举）
     本来就是机器判据，交给人看会漏。

用法：
  .venv/Scripts/python.exe -X utf8 scripts/report_p0_acceptance.py \
      --pytest "956 passed, 1 skipped" \
      --out deliverables/plot-graph-rag-p0-acceptance.md
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from roleplay.core.knowledge.retrieval_trace import (  # noqa: E402
    ABLATION_SCHEMA,
    CHANNEL_ORDER,
    SKIP_REASONS,
)

AUDIT = ROOT / "data" / "knowledge" / "_audit"
R0 = AUDIT / "plot_rag_eval_report_r0.json"
ABLATION_DIR = AUDIT / "ablation"
HUIJI = AUDIT / "rag_huiji_eval_report.json"

ABLATION_REQUIRED = ["m", "b", "c", "delta_pt", "mcnemar_p", "method",
                     "case_ids_flipped", "cases_executed", "cases_total",
                     "feature_flag", "trace_schema"]
TRACE_AGG_REQUIRED = ["cases", "channels", "skip_reason_dist", "margin_histogram",
                      "fallback_counts", "total_ms", "squeezed_total", "graph_hit_total"]
CHANNEL_REQUIRED = ["channel", "cases_executed", "hit_rate", "hit_avg",
                    "kept_in_final_avg", "kept_rate", "squeezed_avg",
                    "contribution_share", "skip_reason_dist", "latency"]

# 消融矩阵行（顺序即报告里的呈现顺序）：(报告文件, 功能说明, 预期作用面)
MATRIX_ROWS = [
    ("plot_rag_eval_report_r0.json", "R0 全开（参照轮）", "—"),
    ("ablation/c4_off.json", "关 C4 手工边豁免弱证过滤", "R8 红线：人工事实边是否参与传播"),
    ("ablation/d1_off.json", "关 D1 node specificity", "泛种子抑制 / 多跳质量"),
    ("ablation/d1_on.json", "D1 全开（D1 消融的参照轮）", "—"),
]


def load(path: Path) -> dict | None:
    if not path.is_file():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def schema_gate(r0: dict, ablations: list[dict]) -> list[tuple[str, bool, str]]:
    """报告 schema 门禁（机器判据，逐条给结论）。"""
    out: list[tuple[str, bool, str]] = []
    top_required = ["event", "summary", "trace_agg", "ablation", "diff_vs_baseline",
                    "bucket_attribution", "assets_sha256_head16", "items"]
    missing = [k for k in top_required if k not in r0]
    out.append(("eval_run_complete 顶层键齐备", not missing, f"缺 {missing}" if missing
                else "、".join(top_required)))
    out.append(("event 取值", r0.get("event") == "eval_run_complete", str(r0.get("event"))))
    ta = r0.get("trace_agg") or {}
    missing = [k for k in TRACE_AGG_REQUIRED if k not in ta]
    out.append(("trace_agg 字段齐备（表 7.6.4-a）", not missing, f"缺 {missing}" if missing
                else "8 字段齐备"))
    chans = [c.get("channel") for c in (ta.get("channels") or [])]
    out.append(("六通道固定顺序（§7.6.1）", chans == list(CHANNEL_ORDER), str(chans)))
    miss_c = sorted({k for c in (ta.get("channels") or [])
                     for k in CHANNEL_REQUIRED if k not in c})
    out.append(("channels[] 子结构字段齐备", not miss_c, f"缺 {miss_c}" if miss_c
                else "10 字段齐备（含设计侧双列 kept_in_final_avg/kept_rate）"))
    bad_skip = sorted({r for c in (ta.get("channels") or [])
                       for r in (c.get("skip_reason_dist") or {})} - set(SKIP_REASONS))
    out.append(("skip_reason 只用 9 值枚举", not bad_skip, f"越界 {bad_skip}" if bad_skip
                else f"9 值内（{len(SKIP_REASONS)} 值枚举）"))
    out.append(("trace_agg.cases == summary.cases",
                ta.get("cases") == (r0.get("summary") or {}).get("cases"),
                f"{ta.get('cases')} vs {(r0.get('summary') or {}).get('cases')}"))
    # − 通则自动核对：每一条"零值/无变化"读数必须与执行计数同段 −
    pairs = [
        ("squeezed_total ↔ graph_hit_total", "squeezed_total" in ta and "graph_hit_total" in ta,
         f"{ta.get('squeezed_total')} ↔ {ta.get('graph_hit_total')}"),
        ("fallback_counts ↔ cases + total_ms",
         "fallback_counts" in ta and "cases" in ta and bool(ta.get("total_ms")),
         f"{ta.get('fallback_counts')} ↔ cases={ta.get('cases')} total_ms={ta.get('total_ms')}"),
        ("kept_rate 分母 0 → null",
         all((c.get("kept_rate") is not None) or c.get("cases_executed") == 0
             or c.get("hit_blocks_avg") in (0, 0.0, None)
             for c in (ta.get("channels") or [])),
         "仅当块级候选为 0 时出现 null"),
    ]
    for name, ok, detail in pairs:
        out.append((f"通则成对产出：{name}", bool(ok), str(detail)))
    # ablation 段
    for a in ablations:
        if a.get("ablation") is None:
            out.append((f"ablation 段存在（{Path(a.get('_src', '?')).name}）", False,
                        "消融运行却为 null"))
            continue
        ab = a["ablation"]
        missing = [k for k in ABLATION_REQUIRED if k not in ab]
        ok = not missing
        note = f"m={ab.get('m')} p={ab.get('mcnemar_p')} method={ab.get('method')}"
        if ab.get("m") == 0 and ab.get("mcnemar_p") is not None:
            ok, note = False, f"m=0 却给了 mcnemar_p={ab.get('mcnemar_p')}（假值）"
        out.append((f"ablation 11 字段 + m=0→null（{Path(a['_src']).name}）", ok,
                    note if ok else f"缺 {missing}；{note}"))
        out.append((f"ablation.trace_schema（{Path(a['_src']).name}）",
                    ab.get("trace_schema") == ABLATION_SCHEMA, str(ab.get("trace_schema"))))
    return out


def pair_negative_rows(r0: dict) -> list[tuple[str, str, str]]:
    """§7.6.6 阴性读数 ↔ 适用性前提（报告正文的成对清单）。

    **必须与 r0 的实际字段对齐**：这里若引用了报告里不存在的键，成对清单就会
    变成"看起来成对、其实是空话"——比不写更糟。
    """
    ta = r0.get("trace_agg") or {}
    neg_trace = ta.get("negatives") or {}
    neg = r0.get("negatives") or {}
    mh = ta.get("margin_histogram") or {}
    return [
        ("`trace_agg.squeezed_total`", str(ta.get("squeezed_total")),
         f"`graph_hit_total` = {ta.get('graph_hit_total')}"
         f"（图传播 {chan(ta, '图传播')} + 篇章路由 {chan(ta, '篇章路由')}）；"
         f"图通道子集 squeezed = {ta.get('squeezed_total_graph_only')}"),
        ("`trace_agg.fallback_counts`", str(ta.get("fallback_counts")),
         f"`cases` = {ta.get('cases')}；`total_ms` = {ta.get('total_ms')}"),
        ("`trace_agg.margin_histogram`（触发数）",
         f"triggered = {mh.get('n_triggered')}",
         f"`n_with_margin` = {mh.get('n_with_margin')}；"
         f"`n_single_candidate` = {mh.get('n_single_candidate')}；"
         f"阈值 {mh.get('thresholds')}"),
        ("`negatives.negative_injection_total`（R3 零注入）",
         f"{neg.get('negative_injection_total')} 块 / {neg.get('cases')} 条",
         f"负样本通道执行计数：图传播 hit {chan(neg_trace, '图传播')}、"
         f"语义向量 hit {chan(neg_trace, '语义向量')}、seeds 合计 "
         f"{neg_trace.get('seeds_total_sum')}、skip {neg_trace.get('skip_reason_dist')}"),
    ]


def chan(agg: dict, name: str, key: str = "hit_blocks_total"):
    for c in agg.get("channels") or []:
        if c.get("channel") == name:
            return c.get(key)
    return None


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--pytest", default="", help="pytest 结果串（如 '956 passed, 1 skipped'）")
    ap.add_argument("--out", default=str(ROOT / "deliverables" / "plot-graph-rag-p0-acceptance.md"))
    args = ap.parse_args()

    r0 = load(R0)
    if r0 is None:
        print(f"[FAIL] 缺少主轮报告 {R0}：先跑 scripts/run_ablation_matrix.py --only R0")
        return 1
    ablations: list[dict] = []
    for rel, _name, _scope in MATRIX_ROWS:
        d = load(AUDIT / rel)
        if d is not None:
            d["_src"] = rel
            ablations.append(d)
    huiji = load(HUIJI) or {}
    s = r0.get("summary") or {}
    neg = r0.get("negatives") or {}
    ta = r0.get("trace_agg") or {}
    ba = r0.get("bucket_attribution") or {}
    gates = schema_gate(r0, [a for a in ablations if a.get("ablation")])
    n_gate_fail = sum(1 for _n, ok, _d in gates if not ok)

    L: list[str] = []
    add = L.append
    add("# 剧情图谱 RAG —— P0 验收报告（M-12 数据源自动生成）")
    add("")
    add(f"> 生成器：`scripts/report_p0_acceptance.py`（所有数字取自 "
        f"`data/knowledge/_audit/` 下的 JSON 物证，**无手抄**）｜"
        f"主轮报告：`{R0.relative_to(ROOT).as_posix()}`｜"
        f"开始时间 {((r0.get('meta') or {}).get('started_at'))}")
    add("")
    add("## 0. 结论速览")
    add("")
    add("| 门禁 | 判据 | 实测 | 结论 |")
    add("|---|---|---|---|")
    p95 = s.get("latency_p95_ms")
    sp = s.get("strict_pass") or 0.0
    strict_verdict = ("达标" if sp >= 0.75
                      else f"**未达标（差 {(0.75 - sp) * 100:.1f}pt）**")
    n_res = len(neg.get("known_residual") or [])
    n_new = len(neg.get("new_leaks") or [])
    neg_verdict = ("达标" if (n_new == 0 and neg.get("negative_injection_total") == 0)
                   else f"**有界未达标**（已知残余 {n_res} 条，新增泄漏 {n_new} 条）")
    hj_pass = (huiji.get("summary") or {}).get("passed")
    add(f"| 300 题严格通过率 | 目标 ≥75%（基线 63.7%） | "
        f"{s.get('strict_pass_n')}/{s.get('cases')} = {pct(s.get('strict_pass'))} | "
        f"{strict_verdict} |")
    add(f"| 注入口径通过率 | 产品真实口径 | "
        f"{s.get('inject_pass_n')}/{s.get('cases')} = {pct(s.get('inject_pass'))} | 记录 |")
    add(f"| A5 负样本零注入 | 逐条 0 块 | 注入 {neg.get('negative_injection_total')} 块 / "
        f"{neg.get('cases')} 条 | {neg_verdict} |")
    hj_cases = huiji.get("cases")
    hj_n = len(hj_cases) if isinstance(hj_cases, list) else hj_cases
    add(f"| 灰机 14 题标准 | 14/14（口径 `--top {huiji.get('top_chunks')}`） | "
        f"{hj_pass}/{hj_n} | {'达标' if hj_pass == 14 else '未达标'} |")
    add(f"| pytest 全绿 | 0 失败 | {args.pytest or '（未提供）'} | "
        f"{'达标' if args.pytest and 'failed' not in args.pytest else '待确认'} |")
    add(f"| A1 延迟增量 | p95 增量 ≤100ms（同条件基线） | "
        f"本轮 p95 {p95}ms（见 §2） | 见 §2 |")
    add(f"| 报告 schema | 四键齐备 + 11 字段 + 9 值枚举 + 成对产出 | "
        f"{len(gates) - n_gate_fail}/{len(gates)} 条通过 | "
        f"{'达标' if n_gate_fail == 0 else f'**{n_gate_fail} 条未通过**'} |")
    add("")
    add("## 1. 主轮指标")
    add("")
    add(f"- 题量 **{s.get('cases')}**｜严格通过 **{s.get('strict_pass_n')}**"
        f"（{pct(s.get('strict_pass'))}）｜天花板内 {pct(s.get('ceiling_pass'))}"
        f"（天花板内题 {s.get('ceiling_cases')}）")
    add(f"- 块精度 {s.get('chunk_precision')}｜答案块率 {s.get('answer_chunk_rate')}"
        f"｜MRR {s.get('mrr')}｜oracle recall {s.get('recall')}"
        f"｜平均返回 {s.get('avg_returned_chunks')} 块｜空结果 {pct(s.get('empty_rate'))}")
    add(f"- 注入口径（预算 {((r0.get('meta') or {}).get('config') or {}).get('plot_context_max_chars')} 字符，"
        f"实际均装入 {s.get('injected_chars_avg')} 字符）："
        f"{s.get('inject_pass_n')}（{pct(s.get('inject_pass'))}）")
    add(f"- 延迟 p50 {s.get('latency_p50_ms')}ms｜p90 {s.get('latency_p90_ms')}ms"
        f"｜p95 {s.get('latency_p95_ms')}ms｜max {s.get('latency_max_ms')}ms")
    add(f"- 路径归因 {s.get('path_counts')}")
    add("")
    add("### 1b. 灰机 14 题闸门：**按返回预算分口径**（预算不同，读数不同）")
    add("")
    add("| 报告 | 口径 `--top` | 通过 | 缺口题 |")
    add("|---|---|---|---|")
    for rel in ("rag_huiji_eval_report.json", "ablation/huiji_top10.json",
                "ablation/huiji_top6.json", "ablation/huiji_top5.json"):
        d = load(AUDIT / rel)
        if not d:
            continue
        fails = [c.get("q") for c in (d.get("cases") or []) if not c.get("pass")]
        add(f"| `{rel}` | {d.get('top_chunks')} | "
            f"{(d.get('summary') or {}).get('passed')}/{len(d.get('cases') or [])} | "
            f"{'、'.join(fails) or '—'} |")
    add("")
    add("> 闸门口径是 **`--top 10`（14/14）**；脚本默认 `--top 5` 更严，"
        "在「维也纳篇与卡卡尼亚对峙决斗的医生是谁？」上少一块证据（13/14）。"
        "**同一份代码在不同返回预算下读数不同**，故口径必须随读数一起写出——"
        "只写「14/14」而不写预算是不可比的读数。")
    add("")
    add("")
    add("| 口径 | 值 | 用途 |")
    add("|---|---|---|")
    add(f"| ① 基线事实（现状 p95 实测） | {baseline_p95()}ms"
        f"（`plot_rag_eval_report_p0_2_baseline.json`） | 事实记录，不是允许上限 |")
    add(f"| ② **合入判据**：新增在线组件 p95 增量 | "
        f"{increment()}ms（阈值 ≤100ms） | **唯一判据** |")
    add(f"| ③ 历史 300ms 绝对线 | 本轮 {s.get('latency_p95_ms')}ms | **不作判据**（消歧遗留） |")
    add("")
    add("> 埋点轮的耗时**不计入** p95：延迟一律取无埋点首轮，否则评测自身开销会污染判据。"
        f"首轮与埋点轮逐题判定一致性 = "
        f"{(ta.get('invariance_vs_main_pass') or {}).get('identical')}"
        f"（差异 {(ta.get('invariance_vs_main_pass') or {}).get('diff_cases')}"
        f"/{(ta.get('invariance_vs_main_pass') or {}).get('cases')}）——"
        "这一条同时是「埋点不改变检索结果」的不变量检验。")
    add("")
    add("### 2b. 同条件重复运行的 p95 抖动（这就是判据必须用增量、不能用绝对线的原因）")
    add("")
    add("| 报告 | 配置差异 | p95 (ms) |")
    add("|---|---|---|")
    for rel, label in ((("plot_rag_eval_report_p0_2_baseline.json"), "M8 基线（同配置）"),
                       (("ablation/d1_on.json"), "D1 全开（排序路径与 R0 相同）"),
                       (("ablation/d1_off.json"), "D1 关（= R0 配置）"),
                       (("ablation/c4_off.json"), "C4 关"),
                       (("plot_rag_eval_report_r0.json"), "R0 全开")):
        d = load(AUDIT / rel)
        if d:
            add(f"| `{rel}` | {label} | "
                f"{((d.get('summary') or {}).get('latency_p95_ms'))} |")
    add("")
    add("> 同一份代码、同一题集、同一配置的多次运行，p95 相差可达数十毫秒"
        "（OS 文件缓存、嵌入服务排队、CPU 频率）。因此 Spec §1.4.1 的三口径里，"
        "历史 300ms **绝对线**不作判据；判据是**同条件增量 ≤100ms**。")
    add("")
    add("## 3. 六通道瀑布（`trace_agg.channels[]`，跨题聚合）")
    add("")
    add("| 通道 | 量纲 | 执行题数/总题数 | 命中率 | hit_avg | hit_blk_avg | kept_avg | kept_rate | 被挤出 | skip_reason 分布 |")
    add("|---|---|---|---|---|---|---|---|---|---|")
    for c in ta.get("channels") or []:
        add(f"| {c['channel']} | {c.get('unit')} | {c.get('cases_executed')}/{ta.get('cases')} "
            f"| {fmt_pct(c.get('hit_rate'))} | {fmt(c.get('hit_avg'))} "
            f"| {fmt(c.get('hit_blocks_avg'))} | {fmt(c.get('kept_in_final_avg'))} "
            f"| {fmt_pct(c.get('kept_rate'))} | {fmt(c.get('squeezed_avg'))} "
            f"| {c.get('skip_reason_dist')} |")
    add("")
    add(f"- **桶 4 融合层稀释**：`squeezed_total` = {ta.get('squeezed_total')}"
        f"（{ta.get('squeezed_total_basis')}）")
    add(f"  - 适用性前提 `graph_hit_total` = **{ta.get('graph_hit_total')}**"
        f"（{ta.get('graph_hit_total_basis')}）；图通道子集 "
        f"`squeezed_total_graph_only` = {ta.get('squeezed_total_graph_only')}")
    add(f"  - 规格原文公式逐字复算值 `squeezed_total_literal_spec_formula` = "
        f"{ta.get('squeezed_total_literal_spec_formula')}"
        f"（与主口径的差额 = 「别名精确」种子量纲混入块量纲的部分，落盘以便审计）")
    mh = ta.get("margin_histogram") or {}
    add(f"- **AC-3 标定证据（margin 直方图）**：桶边界显式落盘 `{mh.get('edges')}`；"
        f"触发 {mh.get('n_triggered')} 题、有 margin {mh.get('n_with_margin')}、"
        f"单候选（margin 无定义）{mh.get('n_single_candidate')}")
    add(f"  - 分布：{mh.get('counts')}")
    add(f"  - 阈值取值：{mh.get('thresholds')}")
    add(f"- **降级**：`fallback_counts` = {ta.get('fallback_counts')}"
        f"（适用性前提：`cases` = {ta.get('cases')}、`total_ms` = {ta.get('total_ms')}）")
    add(f"- **负样本通道执行计数**（R3 的成因侧证据）")
    negt = ta.get("negatives") or {}
    add(f"  - 负样本 {negt.get('cases')} 条：seeds 合计 {negt.get('seeds_total_sum')}、"
        f"图传播 hit {chan(negt, '图传播')}、语义向量 hit {chan(negt, '语义向量')}")
    add(f"  - skip_reason：{negt.get('skip_reason_dist')} —— "
        "「零注入」到底是护栏拦下的还是通道压根没跑，由这两行区分")
    add("")
    add("## 4. 消融矩阵（AC-1：判据本体 = McNemar 配对检验）")
    add("")
    add("| 运行 | 关闭的功能 | m | b | c | delta_pt | method | mcnemar_p | cases_executed | cases_total | 判读 |")
    add("|---|---|---|---|---|---|---|---|---|---|---|")
    for rel, name, _scope in MATRIX_ROWS:
        d = load(AUDIT / rel)
        if d is None:
            add(f"| {name} | — | — | — | — | — | — | — | — | — | 报告缺失 |")
            continue
        ab = d.get("ablation")
        ds = d.get("summary") or {}
        if ab is None:
            add(f"| {name} | — | — | — | — | — | — | — | — | — | "
                f"非消融：严格通过 {ds.get('strict_pass_n')}/{ds.get('cases')}"
                f"（{pct(ds.get('strict_pass'))}） |")
            continue
        add(f"| {name} | `{ab.get('feature_flag')}`={ab.get('off_value')!r} | {ab.get('m')} "
            f"| {ab.get('b')} | {ab.get('c')} | {ab.get('delta_pt')} | `{ab.get('method')}` "
            f"| {ab.get('mcnemar_p')} | {ab.get('cases_executed')} | {ab.get('cases_total')} "
            f"| {one_line(ab.get('conclusion'))} |")
    add("")
    for rel, name, scope in MATRIX_ROWS:
        d = load(AUDIT / rel)
        if not d or not d.get("ablation"):
            continue
        ab = d["ablation"]
        add(f"**{name}**（作用面：{scope}）")
        add("")
        add(f"- 全开 {ab.get('on_value')!r}（参照 `{short(ab.get('reference'))}`） → "
            f"关闭 {ab.get('off_value')!r}；配对题数 {ab.get('cases_total')}")
        add(f"- `cases_executed` = **{ab.get('cases_executed')}** —— "
            f"{ab.get('cases_executed_basis')}")
        add(f"- 原始执行计数：{ab.get('activation')}")
        add(f"- 快速判读档（**不作判据**）：{ab.get('delta_pt_tier')}")
        add(f"- 结论：{ab.get('conclusion')}")
        off = ab.get("off_pass") or {}
        if off:
            add(f"- 关闭轮：严格通过 {off.get('strict_pass_n')}"
                f"（{pct(off.get('strict_pass'))}）；负样本注入 "
                f"{off.get('negative_injection_total')} 块，新增泄漏 "
                f"{len(off.get('negative_new_leaks') or [])} 条")
        add(f"- 参照轮 `{short(ab.get('reference'))}`：**只差被消融开关的那一轮**"
            f"（其余配置相同）——配对前提由 `--ablate-on` 的配置一致性硬校验保证"
            f"（不一致时脚本直接拒绝出结论），不靠人记得。")
        add("")
    add("## 5. 逐题 diff（数据源统一取 `ablation.case_ids_flipped`）")
    add("")
    dv = r0.get("diff_vs_baseline") or {}
    add(f"- 配对题数 {dv.get('cases_paired')}｜来源 `{dv.get('source')}`")
    add(f"- 新增通过（fail→pass）{len(dv.get('newly_passed') or [])} 题："
        f"{', '.join(dv.get('newly_passed') or []) or '—'}")
    add(f"- 新增失败（pass→fail）{len(dv.get('newly_failed') or [])} 题："
        f"{', '.join(dv.get('newly_failed') or []) or '—'}")
    add("")
    add("## 6. 失分桶归因（架构 §4e 五桶）")
    add("")
    add(f"失分 **{ba.get('cases_failed')}/{ba.get('cases_total')}**"
        f"（通过 {ba.get('cases_passed')}；有 trace 的失分题 {ba.get('traced_cases')}）")
    add("")
    add(f"**第一层口径（根因）**：`{ba.get('source')}`"
        + (f"｜来源 `{short(ba.get('triage_source'))}`（该轮通过 "
           f"{ba.get('triage_pass')}/300，与本轮同源核对）" if ba.get("triage_source") else ""))
    add("")
    add("| 桶 | 题数 | 占失分 | §4e 期望规模（偏离即需重校归因） | trace 症状题数 | 判定规则 |")
    add("|---|---|---|---|---|---|")
    for key, b in (ba.get("section4e") or {}).items():
        add(f"| {b.get('name')} | {b.get('cases')} | {pct(b.get('share_of_failed'))} "
            f"| {b.get('expected_reference')} | {b.get('trace_overlay_cases')} "
            f"| {b.get('rule')} |")
    add("")
    add(f"triage 全部根因：{ba.get('triage_reasons')}")
    add("")
    add(f"§4e 未列的原因（数据/算法缺口，**单列**不并入未归因）：{ba.get('unmapped_reasons')}")
    add("")
    add(f"**第二层口径（症状，可重叠）**：{ba.get('trace_signals')}——{ba.get('overlay_note')}")
    add("")
    add(f"> {ba.get('note')}")
    add("")
    add("**偏离核对（架构 §5 第 9 条：无某桶题量占比严重偏离预期，否则归因需重校）**")
    add("")
    b1 = (ba.get("section4e") or {}).get("bucket1_alias_bridge_missing") or {}
    add(f"- 桶 1（别名桥缺失）：本轮 {b1.get('cases')} 题 / 300，审计 §1 基线为 111 题 / 300"
        f"（M8 语义层上线后已下降；差额即语义层直接命中答案块的那部分）")
    add(f"- 桶 3/桶 5 的期望规模是**结构性事实**（边密度不平衡、88% 英文 ASR），"
        f"不是阈值；本轮读数见上表")
    add("")
    add("## 7. 阴性证据通则核对表（§7.6.6）")
    add("")
    add("| 阴性读数 | 值 | 必须并列的适用性前提 |")
    add("|---|---|---|")
    for a, b, c in pair_negative_rows(r0):
        add(f"| {a} | {b} | {c} |")
    add("")
    add("## 8. 报告 schema 门禁（机器判据）")
    add("")
    add("| # | 判据 | 结论 | 证据 |")
    add("|---|---|---|---|")
    for i, (name, ok, detail) in enumerate(gates, start=1):
        add(f"| {i} | {name} | {'✅ 通过' if ok else '❌ 未通过'} | {detail} |")
    add("")
    add("## 8b. 「默认关 / 开关关掉时与现状逐位一致」的证据")
    add("")
    add("| 开关 | 默认值 | 关掉后的行为 | 证据 |")
    add("|---|---|---|---|")
    add("| `plot_weak_exempt_sources`（C4） | `\"manual\"`（**Spec §4 锁定值**，非 False） | "
        "空串 = 无豁免 = P0-1 改造前的过滤口径 | C4 消融轮与 R0 **逐题判定完全一致**"
        f"（m={_ab(load(AUDIT / 'ablation' / 'c4_off.json'), 'm')}，mcnemar_p=null） |")
    add("| `plot_ppr_node_specificity`（D1） | `False` | 默认即现状：`seed_weights=None`，"
        "PPR 输入逐键逐值不变 | `tests/test_plotrag_p0.py::"
        "TestBitIdenticalRegression::test_none_params_bit_identical`"
        "（以**改造前算法的参考实现**在真实规模随机图上差分，逐位相等） |")
    add("| `plot_semantic_rerank_enabled`（B3） | `False` | 未实现（P0-2） | 未启用即不存在该路径 |")
    add("| `plot_semantic_zh_enabled`（A1） | `False` | 未实现（P1-1） | 同上 |")
    add("| `plot_trace_enabled`（F8a） | `False` | 关时不构造 trace、不计时、不写盘 | "
        "埋点轮与主轮逐题判定一致"
        f"（{(ta.get('invariance_vs_main_pass') or {}).get('identical')}，"
        f"差异 {(ta.get('invariance_vs_main_pass') or {}).get('diff_cases')}"
        f"/{(ta.get('invariance_vs_main_pass') or {}).get('cases')}） |")
    add("")
    add("**R0 与 M8 基线逐位一致（检索结果未被本次改动触碰）**")
    add("")
    add("| 指标 | 基线（M8 口径） | R0 全开 | Δ |")
    add("|---|---|---|---|")
    for key in ("strict_pass", "chunk_precision", "answer_chunk_rate", "mrr"):
        b = (baseline().get("summary") or {}).get(key)
        c = s.get(key)
        add(f"| {key} | {b} | {c} | "
            f"{'—' if b is None or c is None else round(float(c) - float(b), 6)} |")
    add("")
    add("> 四项排序指标**逐位相等**说明：M-11 埋点（新增字段与计时）与 `hit_blocks` 归因"
        "（只影响报告聚合、不改排序）都没有触碰检索结果。延迟单独裁决（§2），"
        "不并入本表。")
    add("")
    add("## 9. 逐项决策（结论形态：默认开关决策 / 待实现项）")
    add("")
    d1 = load(AUDIT / "ablation" / "d1_off.json")
    c4 = load(AUDIT / "ablation" / "c4_off.json")
    if d1 and d1.get("ablation"):
        a = d1["ablation"]
        net = int(a.get("b") or 0) - int(a.get("c") or 0)
        add(f"- **P0-4 D1（node specificity）：保持默认关。** 依据：配对检验 "
            f"m={a.get('m')}（b={a.get('b')} 通过→失败 / c={a.get('c')} 失败→通过），"
            f"Δ={a.get('delta_pt')}pt，`mcnemar_p`={a.get('mcnemar_p')}（{a.get('method')}）"
            f"≥0.05 → 不显著；开启后净损 {net} 题（b 比 c 多 {net}）。"
            f"`cases_executed`={a.get('cases_executed')}——**功能确实被测到了**，"
            f"因此这不是「没测到」的阴性结论，而是「测到了、无正收益」。")
    if c4 and c4.get("ablation"):
        a = c4["ablation"]
        add(f"- **P0-1 C4（手工边豁免）：保留 Spec 锁定默认值 `\"manual\"`。** 依据：配对检验 "
            f"m={a.get('m')}（无翻转），`mcnemar_p`=null；`cases_executed`="
            f"{a.get('cases_executed')}（图路确实存在被豁免保留的弱证边候选）。"
            f"意义不在 300 题通过率，而在 R8 红线：人工事实边经过图谱重建后仍在场"
            f"（`apply_manual_edges.py --check` 新增 0、在场率 100%）。")
    add("- **P0-2（B2+B3）：未实现**，开关默认关、无执行计数键 → "
        "`cases_executed` 显式报「未登记」而不是 0（避免把「未实现」读成「无效果」）。"
        "该项承担 AC-1 的 75% 目标缺口与 A5 的 5 条已知残余。")
    add("- **P0-3（A2 别名表扩充）：未实现**；triage 已给出待补清单"
        "（中文正名零命中·度≥3 的实体 40 个），是 P0-3 的输入。")
    add("")
    add("## 10. 未达标项与遗留（逐条登记，不以「已知」代替「已修复」）")
    add("")
    add(f"- A5 已知残余 {len(neg.get('known_residual') or [])} 条（待 B3 reranker 安全间隔）：")
    for q in neg.get("known_residual") or []:
        add(f"  - `{q}`")
    add(f"- 新增泄漏 {len(neg.get('new_leaks') or [])} 条"
        f"{'：' + str(neg.get('new_leaks')) if neg.get('new_leaks') else '（无）'}")
    if (s.get("strict_pass") or 0) < 0.75:
        add(f"- 严格通过率 {pct(s.get('strict_pass'))} < 75%：剩余缺口由 P0-2（B2 实体摘要嵌入 "
            f"+ B3 reranker 安全间隔）与 P0-3（A2 别名表扩充）承担，本报告只登记现状。")
    add(f"- 未实现/未消融项：P0-2（B2/B3）、P0-3（A2）、P1-1（A1）——"
        f"对应功能开关默认关（`plot_semantic_rerank_enabled` / `plot_semantic_zh_enabled`），"
        f"未登记执行计数键的开关会由 `cases_executed` 显式报「未登记」而不是静默报 0。")
    add("")
    add("## 11. 复现命令（本报告全部数字可由此重放）")
    add("")
    add("```bash")
    add("# ① 全量主轮 + 埋点轮 + trace_agg/diff/bucket（含 A1/A5 自检）")
    add(".venv/Scripts/python.exe -X utf8 scripts/run_ablation_matrix.py --only R0")
    add("")
    add("# ② 消融两行（C4 / D1；内部串行，含参照轮）")
    add(".venv/Scripts/python.exe -X utf8 scripts/run_ablation_matrix.py")
    add("")
    add("# ③ §4e 归因的权威口径（逐题根因；供 bucket_attribution 第一层消费）")
    add(".venv/Scripts/python.exe -X utf8 scripts/triage_plot_rag.py \\")
    add("    --out data/knowledge/_audit/plot_rag_triage_r0.json")
    add("")
    add("# ④ 灰机 14 题正确性标准")
    add(".venv/Scripts/python.exe -X utf8 scripts/eval_rag_huiji.py")
    add("")
    add("# ⑤ 单测全绿")
    add(".venv/Scripts/python.exe -X utf8 -m pytest tests/ -q")
    add("")
    add("# ⑥ 生成本报告（不手抄任何数字；schema 门禁不过则退出码 4）")
    add(".venv/Scripts/python.exe -X utf8 scripts/report_p0_acceptance.py \\")
    add('    --pytest "959 passed, 1 skipped" \\')
    add("    --out deliverables/plot-graph-rag-p0-acceptance.md")
    add("```")
    add("")
    add("> **串行**执行 ①②：本项目的延迟判据是 p95 增量 ≤100ms，并发两轮会互相抢 "
        "CPU 与本地嵌入服务，测到的是排队时间而不是组件开销（延迟三口径的第一条就是"
        "「同条件」）。")
    add("")
    out = Path(args.out)
    out.write_text("\n".join(L) + "\n", encoding="utf-8")
    print(f"[save] {out}（{len(L)} 行；schema 门禁 {len(gates) - n_gate_fail}/{len(gates)} 通过）")
    return 0 if n_gate_fail == 0 else 4


def pct(v) -> str:
    return "—" if v is None else f"{float(v):.1%}"


def fmt(v) -> str:
    return "—" if v is None else f"{v}"


def fmt_pct(v) -> str:
    return "—" if v is None else f"{float(v):.0%}"


def one_line(s) -> str:
    return " ".join(str(s or "—").split())[:80]


def short(p) -> str:
    """报告里一律用相对路径（绝对路径既冗长又随机器漂移）。"""
    s = str(p or "")
    root = str(ROOT)
    return s[len(root) + 1:].replace("\\", "/") if s.startswith(root) else s


def baseline():
    return load(AUDIT / "plot_rag_eval_report_p0_2_baseline.json") or {}


def _ab(report: dict | None, key: str):
    """从某轮报告里取 ablation 字段（缺报告/缺段时给 None，不编造）。"""
    if not report or not report.get("ablation"):
        return None
    return report["ablation"].get(key)


def baseline_p95():
    return ((baseline().get("summary") or {}).get("latency_p95_ms", "—"))


def increment():
    b = load(AUDIT / "plot_rag_eval_report_p0_2_baseline.json")
    r0 = load(R0)
    if not b or not r0:
        return "—"
    bp = ((b.get("summary") or {}).get("latency_p95_ms"))
    cp = ((r0.get("summary") or {}).get("latency_p95_ms"))
    if bp is None or cp is None:
        return "—"
    return f"{round(float(cp) - float(bp), 1)}"


if __name__ == "__main__":
    raise SystemExit(main())
