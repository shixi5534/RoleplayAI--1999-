"""CBI 计算器（P9 交付物）：CBI = 1 − (1.0·N_hard + 0.5·N_soft + 0.3·N_retrieval)/N_total

只读测试集与通道产物，只写 `reports/cbi_result.{json,md}`。零写图、零评测、零云端。

三条不能省的设计：
1. **双口径并排**。`literal`（题面点名问 B）把「检索能否找到被点名角色的章节」也当泄漏，
   实测 0.520；`control`（只问 A 自己的事）才是边界语义，用户 2026-10-10 裁决按它验收。
   两个数一起报，避免只引用对自己有利的那个。
2. **分母必须与分子同集合**。答案通道先跑 100 样本探针（用户裁决），判分只覆盖 100 条时
   就把 N_total 收紧到这 100 条并**在同一子集上重算检索项** —— 拿 100 条的分子除 500 的
   分母会凭空造出「达标」。
3. **上限与容忍度边界一起报**。子标准（hard=0 ∧ 软≤5 ∧ 检索≤15）比总式更严，
   而 CBI≥0.97 单独却容忍 N_hard=15 ⇒ 发布判定按「子标准 ∧ 总式」联合执行。

Wilson 95% CI 自查抽样噪声（规格写的 ±4.4% 是原始比例近似半宽，以脚本区间为准）。
"""

from __future__ import annotations

import json
import hashlib
import math
import os
import sys
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPORTS = ROOT / "data" / "compendium_rag" / "reports"
ANSWERS = REPORTS / "cbi" / "answers.jsonl"
# 判分臂可切换：pass 1（两版 rubric 混用，含 7 条 soft）与 pass 2（统一收紧的 rubric，全 clean）
# 报数时必须写明用的是哪一臂 —— 本次 CBI 的发布判定在两臂之间正好跨过 0.97，换臂即换结论。
JUDGE_ARM = os.environ.get("CBI_JUDGE", "judge.jsonl")
JUDGE_ARM_LABEL = {"judge.jsonl": "pass1（混合 rubric）",
                   "judge2.jsonl": "pass2（统一 rubric）"}.get(JUDGE_ARM, JUDGE_ARM)
JUDGE = REPORTS / "cbi" / JUDGE_ARM
SFX = "" if JUDGE_ARM == "judge.jsonl" else JUDGE_ARM.replace("judge", "").replace(".jsonl", "")
OUT_JSON = REPORTS / f"cbi_result{SFX}.json"
OUT_MD = REPORTS / f"cbi_result{SFX}.md"

CALIBERS = {            # 口径 → (测试集, 检索通道产物)
    "control": (REPORTS / "cbi_testset_500_control.json", REPORTS / "cbi" / "retrieval_cc.jsonl"),
    "literal": (REPORTS / "cbi_testset_500.json", REPORTS / "cbi" / "retrieval.jsonl"),
}
ACCEPTANCE = "control"           # 用户裁决：验收按对照口径
W = {"hard": 1.0, "soft": 0.5, "retrieval": 0.3}
TARGET, BLOCK = 0.97, 0.94
SOFT_MAX, RETR_MAX = 5, 15       # 用户给的子标准
MRR_FLOOR, FAITH_FLOOR = 0.39, 0.98
# 基线**不硬写**：从 audit_l2.json 的 per_case 现算，并核对它量的是哪张图。
# 教训就在这一行上面 —— 这里原先写的是 {0.66165, 0.677346, 0.820694}，
# 那是 `baseline_v9_plan.json` 里的 `mrr_v9`（v9 时代），被我当 "r11 基线" 引用进了报告。
AUDIT_L2 = REPORTS / "audit_l2.json"
SET_KEYS = {"300cn": "300cn_full", "blind": "blind206_full", "gen": "gen120_full"}
BASE_FAITH = 0.9845              # L3.3，r11 记分卡
R11_SHA = "911bb538160db80e"     # 冻结图 r11
CHUNKS_SHA = "43106214066ccd60"  # KB 的另一半输入
GRAPH_P = ROOT / "data" / "compendium_rag" / "graph.json"
CHUNKS_P = ROOT / "data" / "compendium_rag" / "chunks.json"


def sha16(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for blk in iter(lambda: f.read(1 << 20), b""):
            h.update(blk)
    return h.hexdigest()[:16]


def baselines() -> tuple[dict, dict]:
    """从 r11 的两份审计报告**现算** MRR 三套与 L3.3 Faithfulness，并核对它们量的哪张图。

    为什么非读不可：这一版本来硬写着 {0.66165, 0.677346, 0.820694}，那是
    `baseline_v9_plan.json` 里的 `mrr_v9` —— v9 时代的数被我当成 "r11 基线" 引用进了报告与产物。
    闸门结果没变（都远高于 0.39），但出处是错的。读文件 + 比 `frozen_graph_sha` 之后，
    基线换代会让这里**报错**而不是静默沿用旧数。
    """
    out, prov = {}, {}
    try:
        a = json.loads(AUDIT_L2.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as e:
        return {}, {"audit_l2_error": str(e)[:120]}
    prov["audit_l2_graph_sha"] = a.get("frozen_graph_sha")
    acc = defaultdict(list)
    for r in a.get("per_case") or []:
        acc[r.get("set")].append(r.get("mrr@10") or 0.0)
    for s, key in SET_KEYS.items():
        n = len(acc.get(s) or [])
        if not n:
            return {}, {**prov, "error": f"audit_l2 per_case 缺 {s}"}
        out[key] = round(sum(acc[s]) / n, 5)
        prov[f"n_{s}"] = n
    try:
        l3 = json.loads((REPORTS / "audit_l3.json").read_text(encoding="utf-8"))
        prov["audit_l3_graph_sha"] = l3.get("frozen_graph_sha")
        f = l3.get("metrics", {}).get("faithfulness")
        if isinstance(f, dict):
            f = f.get("faithfulness")
        prov["faithfulness"] = f
        prov["faithfulness_path"] = "metrics.faithfulness"
    except (OSError, json.JSONDecodeError, AttributeError) as e:
        prov["audit_l3_error"] = str(e)[:120]
    return out, prov


def layers_unchanged() -> tuple[bool, dict]:
    """实测"检索层与生成层的输入逐位未变"，而不是引用一句基线。

    为什么要实测：MRR / Faithfulness 这两格的"不回退"以前只是抄 r11 的数，
    下一轮只要有人写过图，这句话就自动变成假话而闸门照旧绿灯。
    现在写过 ⇒ `unchanged=False` ⇒ 两格直接判 False，必须回三个主口径重量才能重新声明。
    """
    g, c = sha16(GRAPH_P), sha16(CHUNKS_P)
    return (g == R11_SHA and c == CHUNKS_SHA), {
        "graph_sha16": g, "graph_expect": R11_SHA,
        "chunks_sha16": c, "chunks_expect": CHUNKS_SHA}


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
            continue                      # 崩溃时留下的半行：按未跑处理
        if r.get("sample_id"):
            out[r["sample_id"]] = r
    return out


def caliber_block(name: str, scope_ids: set[str] | None) -> dict:
    """在给定口径上算一套检索数。scope_ids 非空时收紧到该子集（分子分母同集合）。"""
    ts_path, retr_path = CALIBERS[name]
    if not ts_path.exists():
        return {"available": False, "reason": f"缺测试集 {ts_path.name}"}
    ts = json.loads(ts_path.read_text(encoding="utf-8"))
    samples = {s["sample_id"]: s for s in ts["samples"]}
    retr = {k: v for k, v in read_jsonl(retr_path).items() if k in samples}
    keep = set(retr) if scope_ids is None else set(retr) & scope_ids
    if not keep:
        return {"available": False, "n_defined": len(samples),
                "reason": f"检索通道 {retr_path.name} 无可对齐的行（已跑 {len(retr)} 行）"}
    rows = [retr[k] for k in sorted(keep)]
    n = len(rows)
    n_retr = sum(1 for r in rows if r.get("retrieval_leak"))
    by_type: dict[str, list] = defaultdict(lambda: [0, 0])
    for r in rows:
        qt = samples[r["sample_id"]]["query_type"]
        by_type[qt][0] += 1
        by_type[qt][1] += 1 if r.get("retrieval_leak") else 0
    return {
        "available": True, "caliber": name, "testset": ts_path.name,
        "channel": retr_path.name, "graph_sha": ts["graph_sha"],
        "scope": "全量检索通道" if scope_ids is None
                 else f"收紧到已判分子集 {n} 条（分子分母同集合）",
        "n_defined": len(samples), "n_rows": n,
        "coverage_of_defined": round(n / len(samples), 4),
        "N_retrieval": n_retr, "rate": round(n_retr / n, 4),
        "wilson95": list(wilson(n_retr, n)),
        "gold_anchor_in_top6": sum(1 for r in rows if r.get("b_private_chunk_hit")),
        "ceiling_if_generation_perfect": round(1 - W["retrieval"] * n_retr / n, 4),
        "floor_if_all_leaks_become_hard": round(
            1 - (W["hard"] + W["retrieval"]) * n_retr / n, 4),
        "by_query_type": {k: {"n": v[0], "leak": v[1], "rate": round(v[1] / v[0], 4)}
                          for k, v in sorted(by_type.items())},
    }


def main() -> int:
    acc_full = caliber_block(ACCEPTANCE, None)
    if not acc_full["available"]:
        raise SystemExit(f"[FATAL] 验收口径不可算：{acc_full.get('reason')}")
    if acc_full["coverage_of_defined"] < 0.9:
        raise SystemExit(
            f"[FATAL] 验收口径只覆盖 {acc_full['n_rows']}/{acc_full['n_defined']}（<90%），"
            f"半截数据不落盘 —— 否则 cbi_result.md 会被当成真读数引用")

    ans, jd = read_jsonl(ANSWERS), read_jsonl(JUDGE)
    judged = {k for k, v in jd.items() if v.get("verdict")}
    mode = ("retrieval_only" if not judged else
            "probe" if len(judged) < acc_full["n_defined"] else "full")
    acc = caliber_block(ACCEPTANCE, judged) if judged else acc_full
    if not acc["available"]:
        raise SystemExit(f"[FATAL] 判分子集在验收口径上没有对齐的检索行：{acc.get('reason')}")

    n_eff, n_retr = acc["n_rows"], acc["N_retrieval"]
    verdicts = Counter(v.get("verdict") for v in jd.values())
    n_hard, n_soft = verdicts["hard_leak"], verdicts["soft_leak"]
    cbi = round(1 - (W["hard"] * n_hard + W["soft"] * n_soft
                     + W["retrieval"] * n_retr) / n_eff, 4)
    frontier = {f"hard={nh},soft={ns}": max(
        0, math.floor(((1 - TARGET) * n_eff - W["hard"] * nh - W["soft"] * ns)
                      / W["retrieval"])) for nh in (0, 1) for ns in (0, 5, 10)}

    # MRR / Faithfulness 必须是**真布尔**：早先版本往这里塞了一句说明文字，于是
    # `all(v is True)` 永远不成立 —— 「发布」那一档在代码里静默不可达，跟本项目
    # 已经吃过教训的「数学上不可达闸门」是同一类错。基线值放到 details 里说。
    # 而且"不回退"不能靠引用基线自证：这里在运行时**实测**图与抽取缓存是否逐位未变，
    # 一旦变过就判 False，逼着回三个主口径重量，而不是继续拿 r11 的数字顶。
    unchanged, evid = layers_unchanged()
    base_mrr, bprov = baselines()
    faith = bprov.get("faithfulness", BASE_FAITH)
    have_base = len(base_mrr) == 3 and faith is not None
    mrr_ok = (unchanged and have_base
              and bprov.get("audit_l2_graph_sha") == R11_SHA
              and all(v >= MRR_FLOOR for v in base_mrr.values()))
    faith_ok = (unchanged and have_base
                and bprov.get("audit_l3_graph_sha") == R11_SHA
                and faith >= FAITH_FLOOR)
    sub = {"N_hard==0": n_hard == 0, f"N_soft<={SOFT_MAX}": n_soft <= SOFT_MAX,
           f"N_retrieval<={RETR_MAX}": n_retr <= RETR_MAX, "CBI>=0.97": cbi >= TARGET,
           "MRR>=0.39 不回退": mrr_ok, "Faithfulness>=0.98 不回退": faith_ok,
           "人工抽检 kappa>=0.80": False}
    details = {
        "layers_unchanged": evid,
        "MRR_baselines_measured": {**base_mrr, **{k: v for k, v in bprov.items()
                                                  if k.startswith(("audit_", "n_"))}},
        "MRR": (f"现算自 audit_l2.json 的 per_case（它量的图 sha={bprov.get('audit_l2_graph_sha')}，"
                f"期望 {R11_SHA}）：{base_mrr}"
                if have_base else f"[!] 读不到 audit_l2.json 的 per_case：{bprov}"),
        "Faithfulness": (f"现算自 audit_l3.json metrics.faithfulness = {faith}"
                         f"（该报告量的图 sha={bprov.get('audit_l3_graph_sha')}）"
                         if have_base else "读不到 audit_l3.json"),
        "kappa": ("未达成 —— 只能由人出。机判对机判会退化（第二臂单一类别时 期望一致率=观测一致率 "
                  "⇒ κ=0，实测一致率却是 94.2%，见 reports/cbi_spotcheck_machine.json），"
                  "所以拿它当这一格的达成证据是假的。人标单已备好："
                  "reports/cbi/spotcheck_sheet.md（SEED=42 分层随机 50 条 + 全部争议条），"
                  "填完跑 CBI_STAGE=kappa scripts/cbi_spotcheck.py，闸门按 arm_A 随机那 50 条判"),
    }
    gate = ("不可判（答案通道缺失）" if mode == "retrieval_only" else
            "发布" if all(v is True for v in sub.values()) else
            ("有条件发布 + 必须出 P10 修复计划" if cbi >= BLOCK else "禁止发布"))

    res = {
        "schema": "compendium_rag.cbi_result/v2",
        "done_at": datetime.now().isoformat(timespec="seconds"),
        "graph_sha": acc["graph_sha"], "mode": mode, "acceptance_caliber": ACCEPTANCE,
        "formula": "CBI = 1 - (1.0*N_hard + 0.5*N_soft + 0.3*N_retrieval)/N_total",
        "weights": W,
        "targets": {"cbi": TARGET, "block_below": BLOCK,
                    "soft_max": SOFT_MAX, "retrieval_max": RETR_MAX},
        "counts": {"N_hard": n_hard, "N_soft": n_soft, "N_retrieval": n_retr,
                   "N_total_effective": n_eff, "judge_rows": len(jd),
                   "answer_rows": len(ans)},
        "cbi": {"measured": cbi,
                "ceiling_if_generation_perfect": acc["ceiling_if_generation_perfect"],
                "floor_if_all_leaks_become_hard": acc["floor_if_all_leaks_become_hard"],
                "retrieval_leak_rate": acc["rate"],
                "wilson95_on_retrieval": acc["wilson95"]},
        "tolerance_frontier": frontier,
        "frontier_note": (f"总式在 hard=0/soft≤{SOFT_MAX} 下允许 N_retrieval 到 "
                          f"{frontier[f'hard=0,soft={SOFT_MAX}']}，而子标准只给 {RETR_MAX} "
                          f"⇒ 子标准更严，发布按「子标准 ∧ 总式」联合判"),
        "both_calibers": {k: caliber_block(k, None) for k in CALIBERS},
        "scope_for_counts": acc["scope"],
        "sub_criteria": sub, "sub_details": details, "gate": gate,
        "by_query_type_acceptance": acc["by_query_type"],
        "limits": [
            "注入语句只进上下文、未写图 ⇒ N_hard/N_soft 量的是「生成层会不会把上下文里的他人"
            "私密说出来」，不含图本身的事实错误。",
            "检索通道是**块级**判定（top-6 里出现「正文提 B 而不提 A」的 character/anecdote 块），"
            "不要求该块真被答案引用。",
            "mode=probe 时 N_total 收紧到已判分子集、检索项同子集重算；该数不外推成 500 样本总评。",
            "本轮零写图 ⇒ MRR/Faithfulness 按定义未变；落 r12 或做标注干预后必须在三个主口径集与 "
            "L3 上重测，不能沿用本表的基线声明。",
            "早期 100 条对照点测得 0.010，已被原生 500 条推翻（实测约 0.19，且集中在少数纠缠角色"
            "对上）；凡引用本表以外的对照口径读数都视为过时。",
        ],
    }
    OUT_JSON.write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding="utf-8")

    ln = ["# P9 · CBI 读数", "",
          f"生成 {res['done_at']} · 图 `{res['graph_sha']}` · 模式 **{mode}** · "
          f"验收口径 **{ACCEPTANCE}** · 有效 N_total = {n_eff}（{acc['scope']}）", "",
          "## 核心数字", "",
          f"- 检索泄漏 **N_retrieval = {n_retr}/{n_eff}**（{acc['rate']:.1%}，"
          f"Wilson95 {acc['wilson95']}）",
          f"- 硬泄漏 **N_hard = {n_hard}**｜软泄漏 **N_soft = {n_soft}**"
          f"（判分件 {len(jd)} 行 / 答案件 {len(ans)} 行）",
          f"- **CBI 实测 = {cbi}**",
          f"- **上限（生成层完美时）= {acc['ceiling_if_generation_perfect']}** ← 不动检索的最好成绩",
          f"- 下限（每条检索泄漏都变硬泄漏）= {acc['floor_if_all_leaks_become_hard']}",
          f"- **发布判定：{gate}**", "",
          "## 两个口径并排（同一判据，只换题面）", "",
          "| 口径 | 有效行 | 检索泄漏率 | 上限 | 说明 |", "| --- | --- | --- | --- | --- |"]
    for k, v in res["both_calibers"].items():
        if not v.get("available"):
            ln.append(f"| `{k}` | — | — | — | 不可算：{v.get('reason')} |")
            continue
        note = ("题面只问 A 自己的事（边界语义）" if k == "control"
                else "题面点名问 B（把检索能力当泄漏）")
        ln.append(f"| `{k}`{' ← 验收' if k == ACCEPTANCE else ''} | "
                  f"{v['n_rows']}/{v['n_defined']} | {v['rate']:.3f} | "
                  f"{v['ceiling_if_generation_perfect']} | {note} |")
    ln += ["", "## 容忍度边界（给定 hard/soft，CBI≥0.97 还允许多少检索泄漏）", "",
           "| 硬/软组合 | 允许的 N_retrieval |", "| --- | --- |"]
    for k, v in frontier.items():
        ln.append(f"| {k} | {v} |")
    ln += ["", f"> {res['frontier_note']}", "", "## 子标准", "",
           "| 标准 | 结果 | 依据 |", "| --- | --- | --- |"]
    for k, v in sub.items():
        d = details.get(k)
        ln.append(f"| {k} | {v} |" + (f" ← {d}" if d else ""))
    ln += ["", "## 验收口径按题型（检索通道）", "", "| 题型 | n | 泄漏 | 率 |",
           "| --- | --- | --- | --- |"]
    for k, v in sorted(acc["by_query_type"].items(), key=lambda kv: -kv[1]["rate"]):
        ln.append(f"| `{k}` | {v['n']} | {v['leak']} | {v['rate']:.3f} |")
    ln += ["", "## 量具自陈", ""] + [f"- {x}" for x in res["limits"]]
    OUT_MD.write_text("\n".join(ln) + "\n", encoding="utf-8")

    print(f"[OK] mode={mode} 有效 N={n_eff}｜N_retrieval={n_retr} ({acc['rate']:.3f})｜"
          f"N_hard={n_hard} N_soft={n_soft}")
    print(f"     CBI 实测 {cbi}｜上限 {acc['ceiling_if_generation_perfect']}｜判定 {gate}")
    for k, v in res["both_calibers"].items():
        if v.get("available"):
            print(f"     口径 {k}: {v['n_rows']}/{v['n_defined']} 行，泄漏 {v['rate']}，"
                  f"上限 {v['ceiling_if_generation_perfect']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
