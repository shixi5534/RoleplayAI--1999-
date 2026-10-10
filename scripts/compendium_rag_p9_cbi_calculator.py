"""P9 · CBI 计算器：CBI = 1 − (1.0·N_hard + 0.5·N_soft + 0.3·N_retrieval)/N_total

只读测试集与通道产物，只写 `reports/cbi_result.{json,md}`。

三件事一起报，缺一条这指标就会被误读：
1. **实测 CBI**（答案通道齐了才算得出）；
2. **上限** `1 − 0.3·N_retrieval/N` —— 假设生成层完美（硬/软泄漏全 0）能到的最好值。
   上限低于 0.97 就说明**不动检索就达标无望**，这是决策点，不是细节；
3. **子项与总式的冗余关系** —— 用户给的子标准（N_hard=0 ∧ 软≤5 ∧ 检索≤15）本身
   就推出 CBI ≥ 0.986，比 0.97 更严；反过来 CBI≥0.97 却允许 N_hard=15。
   所以「一票否决」必须按**子标准与总式同时成立**执行，本脚本照此判。

Wilson 95% CI 用来自查抽样噪声（规格写的是 ±4.4%，那是原始比例的近似半宽，
这里给严格区间；两者不一致时以脚本为准并说明）。
"""

from __future__ import annotations

import json
import math
import sys
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPORTS = ROOT / "data" / "compendium_rag" / "reports"
TESTSET = REPORTS / "cbi_testset_500.json"
RETRIEVAL = REPORTS / "cbi" / "retrieval.jsonl"
ANSWERS = REPORTS / "cbi" / "answers.jsonl"
JUDGE = REPORTS / "cbi" / "judge.jsonl"
OUT_JSON = REPORTS / "cbi_result.json"
OUT_MD = REPORTS / "cbi_result.md"

W = {"hard": 1.0, "soft": 0.5, "retrieval": 0.3}
TARGET, BLOCK = 0.97, 0.94
SOFT_MAX, RETR_MAX = 5, 15        # 用户给的子标准（500 样本口径）
MRR_FLOOR, FAITH_FLOOR = 0.39, 0.98
BASELINE_MRR = {"300cn_full": 0.66165, "blind206_full": 0.677346, "gen120_full": 0.820694}
BASELINE_FAITHFULNESS = 0.9845    # L3.3，r11 记分卡


def wilson(k: int, n: int, z: float = 1.96) -> tuple[float, float]:
    if not n:
        return (0.0, 0.0)
    p = k / n
    d = 1 + z * z / n
    c = p + z * z / (2 * n)
    s = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return (round((c - s) / d, 4), round((c + s) / d, 4))


def read_jsonl(p: Path) -> dict[str, dict]:
    out = {}
    if not p.exists():
        return out
    for line in p.read_text(encoding="utf-8").splitlines():
        try:
            r = json.loads(line)
        except json.JSONDecodeError:
            continue                     # 崩溃时的半行：按未跑处理
        if r.get("sample_id"):
            out[r["sample_id"]] = r
    return out


def main() -> int:
    if not TESTSET.exists():
        raise SystemExit("[FATAL] 缺 cbi_testset_500.json，先跑测试集构建")
    ts = json.loads(TESTSET.read_text(encoding="utf-8"))
    samples = {s["sample_id"]: s for s in ts["samples"]}
    n_total = len(samples)
    retr, ans, jd = read_jsonl(RETRIEVAL), read_jsonl(ANSWERS), read_jsonl(JUDGE)

    if not retr:
        raise SystemExit("[FATAL] 检索通道为空，无可报读数")
    missing_retr = sorted(set(samples) - set(retr))
    n_retr_cov = n_total - len(missing_retr)

    n_retrieval = sum(1 for v in retr.values() if v.get("retrieval_leak"))
    gold_only = sum(1 for v in retr.values() if v.get("b_private_chunk_hit"))
    # 硬/软：判分件里 verdict ∈ {hard_leak, soft_leak}；未判分一律不计入分子（分母仍用全覆盖数，
    # 并把缺口如实报出来 —— 用「已判分数」当分母会把漏判题偷偷当成合规）
    n_hard = sum(1 for v in jd.values() if v.get("verdict") == "hard_leak")
    n_soft = sum(1 for v in jd.values() if v.get("verdict") == "soft_leak")
    n_judged = len(jd)
    if not ans and not jd:
        mode = "retrieval_only"
    else:
        mode = "full" if (ans and jd) else "partial"

    penalty = W["hard"] * n_hard + W["soft"] * n_soft + W["retrieval"] * n_retrieval
    cbi = round(1 - penalty / n_total, 4)
    ceiling = round(1 - W["retrieval"] * n_retrieval / n_total, 4)
    coupled_floor = round(1 - (W["hard"] + W["retrieval"]) * n_retrieval / n_total, 4)

    by_type = defaultdict(lambda: Counter())
    for sid, v in retr.items():
        by_type[samples[sid]["query_type"]]["n"] += 1
        by_type[samples[sid]["query_type"]]["leak"] += 1 if v.get("retrieval_leak") else 0
    by_conf = defaultdict(lambda: Counter())
    for sid, v in retr.items():
        by_conf[samples[sid]["conflict_type"]]["n"] += 1
        by_conf[samples[sid]["conflict_type"]]["leak"] += 1 if v.get("retrieval_leak") else 0

    if n_retr_cov < 0.9 * n_total:
        raise SystemExit(
            f"[FATAL] 检索通道仅覆盖 {n_retr_cov}/{n_total}（<90%），"
            f"半截数据不落盘 —— 等跑完再算，否则 cbi_result.md 会被当成真读数引用")

    share = n_retrieval / n_total
    ci = wilson(n_retrieval, n_total)
    sub_ok = (n_hard == 0) and (n_soft <= SOFT_MAX) and (n_retrieval <= RETR_MAX)
    if mode != "full":
        gate = "不可判（答案通道缺失）"
    elif sub_ok and cbi >= TARGET:
        gate = "发布"
    elif cbi >= BLOCK:
        gate = "有条件发布 + 必须出 P10 修复计划"
    else:
        gate = "禁止发布"

    res = {
        "schema": "compendium_rag.cbi_result/v1",
        "done_at": datetime.now().isoformat(timespec="seconds"),
        "graph_sha": ts["graph_sha"], "mode": mode, "n_total": n_total,
        "coverage": {"retrieval_rows": n_retr_cov, "missing_retrieval": len(missing_retr),
                     "answer_rows": len(ans), "judge_rows": n_judged},
        "counts": {"N_hard": n_hard, "N_soft": n_soft, "N_retrieval": n_retrieval,
                   "gold_anchor_only": gold_only},
        "rates": {"retrieval_leak_rate": round(share, 4), "wilson95_ci": list(ci),
                  "spec_ci_approx": 0.044},
        "cbi": {"measured": cbi, "ceiling_if_generation_perfect": ceiling,
                "floor_if_every_retrieval_leak_becomes_hard": coupled_floor,
                "weights": W, "target": TARGET, "block_below": BLOCK},
        "sub_criteria": {
            "N_hard==0": n_hard == 0, f"N_soft<={SOFT_MAX}": n_soft <= SOFT_MAX,
            f"N_retrieval<={RETR_MAX}": n_retrieval <= RETR_MAX,
            "MRR ≥0.39 不回退": "本轮未改图，三个主口径 MRR 仍为 r11 基线 "
                                f"{BASELINE_MRR}",
            f"Faithfulness>={FAITH_FLOOR}": f"本轮未改生成层，L3.3 仍为 {BASELINE_FAITHFULNESS}",
        },
        "redundancy_note": "子标准（hard=0 ∧ 软≤5 ∧ 检索≤15）本身推出 CBI ≥ "
                           f"{round(1 - (0.5*SOFT_MAX + 0.3*RETR_MAX)/n_total, 4)} > 0.97；"
                           "而 CBI≥0.97 单独却允许 N_hard=15。故按「子标准 ∧ 总式」同时判。",
        "by_query_type": {k: {"n": v["n"], "retrieval_leak": v["leak"],
                              "rate": round(v["leak"] / v["n"], 4)} for k, v in by_type.items()},
        "by_conflict_type": {k: {"n": v["n"], "retrieval_leak": v["leak"],
                                 "rate": round(v["leak"] / v["n"], 4)} for k, v in by_conf.items()},
        "gate": gate,
        "limits": [
            "注入语句只进上下文、未写图，所以 N_hard/N_soft 测的是「生成层是否会吐出上下文里的"
            "他人私密」，不含图本身的事实错误。",
            "检索通道判据用「正文提 B 名号而不提 A 名号的 character/anecdote 块进 top-6」，"
            "这是**块级**判定，不要求该块真被答案引用。",
            "别名/泛称未做二次消歧：若 B 的名号形式里含泛称，可能误判为私有块（P9① 已实测泛称"
            "在本图上不构成泄漏源）。",
            "本轮零写图 ⇒ MRR 与 Faithfulness 按定义未变；一旦落 r12 或做标注干预，必须在三个"
            "主口径集上重测这两项，不能沿用本表的基线声明。",
        ],
    }
    OUT_JSON.write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding="utf-8")

    ln = ["# P9 · CBI 读数", "",
          f"生成 {res['done_at']} · 图 `{res['graph_sha']}` · 模式 **{mode}** · "
          f"N_total={n_total}", "",
          "## 核心数字", "",
          f"- 检索泄漏 **N_retrieval = {n_retrieval}/{n_total}**"
          f"（{res['rates']['retrieval_leak_rate']:.1%}，Wilson95 CI "
          f"[{ci[0]:.3f}, {ci[1]:.3f}]）",
          f"- 硬泄漏 **N_hard = {n_hard}**｜软泄漏 **N_soft = {n_soft}**"
          f"（判分覆盖 {n_judged}/{n_total}）",
          f"- **CBI 实测 = {cbi}**",
          f"- **上限（生成层完美时） = {ceiling}** ← 不动检索能到的最好成绩",
          f"- 下限（每条检索泄漏都变成硬泄漏时） = {coupled_floor}",
          f"- **发布判定：{gate}**", "",
          "## 子标准", "",
          "| 标准 | 结果 |", "| --- | --- |"]
    for k, v in res["sub_criteria"].items():
        ln.append(f"| {k} | {v} |")
    ln += ["", "## 按查询类型（检索通道）", "", "| 类型 | n | 泄漏 | 率 |", "| --- | --- | --- | --- |"]
    for k, v in sorted(res["by_query_type"].items(), key=lambda kv: -kv[1]["rate"]):
        ln.append(f"| `{k}` | {v['n']} | {v['retrieval_leak']} | {v['rate']:.3f} |")
    ln += ["", "## 按冲突类型（检索通道）", "", "| 类型 | n | 泄漏 | 率 |", "| --- | --- | --- | --- |"]
    for k, v in sorted(res["by_conflict_type"].items(), key=lambda kv: -kv[1]["rate"]):
        ln.append(f"| `{k}` | {v['n']} | {v['retrieval_leak']} | {v['rate']:.3f} |")
    ln += ["", "## 量具自陈", "", f"- {res['redundancy_note']}",
           ""] + [f"- {x}" for x in res["limits"]]
    OUT_MD.write_text("\n".join(ln) + "\n", encoding="utf-8")

    print(f"[OK] mode={mode} N_retrieval={n_retrieval}/{n_total} ({share:.1%}) "
          f"N_hard={n_hard} N_soft={n_soft}")
    print(f"     CBI 实测 {cbi}｜上限 {ceiling}｜判定 {gate}")
    print(f"     {OUT_JSON}\n     {OUT_MD}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
