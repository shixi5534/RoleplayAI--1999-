"""CBI · 10% 人工抽检单与 Cohen's κ 计算器（闸门里唯一必须由人出的一臂）。

为什么不能拿第二遍机判顶：全 clean 的单一类别里 Cohen κ 的期望一致率等于观测一致率，
κ=0 属于退化而非一致性差（`P9_CBI报告.md` §2.3）。

两个 stage（STAGE 环境变量）：
    plan    随机分层抽 50 条（5 个查询类型各 10，SEED=42）+ 追加全部机判非 clean 条，
            写 `reports/cbi/spotcheck_sheet.{md,json}` 给人标；
    kappa   读回 `reports/cbi/spotcheck_labels.json`，报两版 κ：
            A=只用随机 50 条（无偏，闸门按这一版判），B=含争议条（缺陷富集，只作参考）。

只读测试集与判分件，只写 `reports/cbi/` 下这三个文件；不碰图、不碰缓存。
"""

from __future__ import annotations

import json
import os
import random
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPORTS = ROOT / "data" / "compendium_rag" / "reports"
CBI = REPORTS / "cbi"

# 仪器开关（P10 新增）：与 cbi_calculator.py 同一套名字，默认 v1 所以历史命令一字不改。
# v2 = R5bis 逐对独特注入的测试集；它的判分臂是 judge_v2_r1（尺子 v1）× judge_v2_r2（尺子 v2），
# 两臂逐行一致率 1.0000，默认取 v1 臂。
_INSTRUMENTS = {
    "v1": {"testset": "cbi_testset_500_control.json",
           "retrieval": "retrieval_cc.jsonl",
           "answers": "answers.jsonl",
           "judge": "judge_full.jsonl",
           "sheet_md": "spotcheck_sheet.md",
           "sheet_json": "spotcheck_sheet.json",
           "labels": "spotcheck_labels.json",
           "result": "cbi_spotcheck_kappa.json",
           "sens": "spotcheck_sensitivity",
           "schema": "compendium_rag.cbi_spotcheck/v1"},
    "v2": {"testset": "cbi_testset_500_v2_control.json",
           "retrieval": "retrieval_v2_cc.jsonl",
           "answers": "answers_v2.jsonl",
           "judge": "judge_v2_r1.jsonl",
           "sheet_md": "spotcheck_sheet_v2.md",
           "sheet_json": "spotcheck_sheet_v2.json",
           "labels": "spotcheck_labels_v2.json",
           "result": "cbi_spotcheck_kappa_v2.json",
           "sens": "spotcheck_sensitivity_v2",
           "schema": "compendium_rag.cbi_spotcheck_sheet/v2"},
}
INSTRUMENT = os.environ.get("CBI_INSTRUMENT", "v1")
if INSTRUMENT not in _INSTRUMENTS:
    raise SystemExit(f"[FATAL] CBI_INSTRUMENT={INSTRUMENT!r} 不认识（{sorted(_INSTRUMENTS)}）")
_IV = _INSTRUMENTS[INSTRUMENT]

TESTSET = REPORTS / _IV["testset"]
RETRIEVAL = CBI / _IV["retrieval"]
ANSWERS = CBI / _IV["answers"]
JUDGE = CBI / os.environ.get("CBI_JUDGE", _IV["judge"])
SHEET_MD = CBI / _IV["sheet_md"]
SHEET_JSON = CBI / _IV["sheet_json"]
LABELS = CBI / _IV["labels"]
RESULT = REPORTS / _IV["result"]
SHEET_SCHEMA = _IV["schema"]

SEED = 42
PER_TYPE = 10                      # 5 类 × 10 = 50 条 = 500 的 10%
STAGE = os.environ.get("CBI_STAGE", "plan")
MAP = {"clean": 0, "soft_leak": 1, "hard_leak": 2}
SOFT_MAX = 5                         # 用户给的子标准（500 样本口径）
N_TOTAL = 500
REV = {v: k for k, v in MAP.items()}


def load_all():
    ts = json.loads(TESTSET.read_text(encoding="utf-8"))
    samples = {s["sample_id"]: s for s in ts["samples"]}
    ans = {}
    for line in ANSWERS.read_text(encoding="utf-8").splitlines():
        r = json.loads(line)
        ans[r["sample_id"]] = r["answer"]
    judge = {}
    for line in JUDGE.read_text(encoding="utf-8").splitlines():
        r = json.loads(line)
        judge[r["sample_id"]] = r
    retr = {}
    for line in RETRIEVAL.read_text(encoding="utf-8").splitlines():
        r = json.loads(line)
        retr[r["sample_id"]] = r
    return samples, ans, judge, retr


def cohen(pairs: list[tuple[int, int]]) -> dict:
    """Cohen's κ + 观测一致率 + 混淆矩阵；pairs 为 (机判码, 人判码)。"""
    n = len(pairs)
    if not n:
        return {"n": 0}
    po = sum(1 for a, b in pairs if a == b) / n
    me = Counter(a for a, _ in pairs)
    he = Counter(b for _, b in pairs)
    pe = sum(me[k] / n * he[k] / n for k in set(me) | set(he))
    kappa = (po - pe) / (1 - pe) if pe < 1 else 1.0
    # κ 在两臂之一只有单一类别时会退化成 0（po == pe），那是一致性极好造成的假 0，
    # 不是"判分不一致"。此时报数要用观测一致率，别拿 κ 判闸门。
    degenerate = pe >= 1.0 or len(me) <= 1 or len(he) <= 1 or abs(po - pe) < 1e-12
    cls = sorted(set(me) | set(he))
    return {
        "n": n, "observed_agreement": round(po, 4),
        "expected_agreement": round(pe, 4), "kappa": round(kappa, 4),
        "machine_only": dict((REV[k], v) for k, v in me.items()),
        "human_only": dict((REV[k], v) for k, v in he.items()),
        "confusion": {f"机{REV[a]}→人{REV[b]}": c
                      for (a, b), c in Counter(pairs).items()},
        "degenerate": degenerate,
        "use_instead": ("观测一致率（κ 退化：有一臂只有单一类别）" if degenerate else "kappa"),
    }


def dispute_ids() -> list[str]:
    """v2 仪器的「争议富集」行来源：机械屏幕候选 + 诊断臂 flagged。

    为什么 v2 不能像 v1 那样「把机判非 clean 的全塞进来」：v2 的判分臂 500/500 全 clean，
    那条规则在这一版上会抽出 0 条，缺陷富集层就空了。真正的争议点在别处 ——
    (a) 机械屏幕（4-gram 字面屏）报出的候选（判分臂判 clean，但屏幕说字面撞上了），
    (b) 诊断臂 D1 唯一那条 attributed_to_A。
    这两处正是「唯一可能藏漏报」的位置，抽检单必须把它们单列出来给人看一眼。
    """
    out: list[str] = []
    p = CBI / "hardleak_screen_v2.json"
    if p.exists():
        try:
            out += [it.get("sample_id")
                    for it in json.loads(p.read_text(encoding="utf-8")).get("items", [])]
        except (OSError, json.JSONDecodeError):
            pass
    q = REPORTS / "cbi_result_v2testset.json"
    if q.exists():
        try:
            out += json.loads(q.read_text(encoding="utf-8")) \
                .get("attribution_diag_v2", {}).get("flagged", [])
        except (OSError, json.JSONDecodeError):
            pass
    return [x for x in dict.fromkeys(out) if x]


def build_sheet() -> int:
    samples, ans, judge, retr = load_all()
    if len(judge) != 500 or len(ans) != 500:
        raise SystemExit(f"[FATAL] 判分/答案不齐：judge {len(judge)} ans {len(ans)}")
    by_type = defaultdict(list)
    for sid, s in samples.items():
        by_type[s["query_type"]].append(sid)
    rng = random.Random(SEED)
    picked, rand_ids = [], set()
    for qt in sorted(by_type):
        pool = sorted(by_type[qt])
        if len(pool) < PER_TYPE:
            raise SystemExit(f"[FATAL] {qt} 只有 {len(pool)} 条，分不了 {PER_TYPE}")
        take = sorted(rng.sample(pool, PER_TYPE))
        for sid in take:
            rand_ids.add(sid)
            picked.append((sid, "随机"))
    if INSTRUMENT == "v2":
        extra = [(sid, "争议") for sid in dispute_ids() if sid in samples and sid not in rand_ids]
        extra_kind = "机械屏幕候选 + 诊断臂 flagged"
    else:
        extra = [(sid, "必看·非随机") for sid in sorted(judge)
                 if judge[sid]["verdict"] != "clean" and sid not in rand_ids]
        extra_kind = "机判非 clean"
    picked += extra

    rows = []
    for sid, tier in picked:
        s, j = samples[sid], judge[sid]
        rows.append({
            "sample_id": sid, "tier": tier, "query_type": s["query_type"],
            "a_role": s["perspective"], "b_role": s["pair"]["b_name"],
            "conflict_type": s.get("conflict_type", ""),
            "prompt": s["prompt"], "b_private_fact": s["injected"]["b_says"],
            "a_private_fact": s["injected"]["a_says"],
            "answer": ans[sid], "machine_verdict": j["verdict"],
            "machine_evidence": j.get("evidence_quote", ""),
            "machine_why": j.get("why", ""),
            "retrieval_leak": bool(retr.get(sid, {}).get("retrieval_leak")),
            "human_verdict": "",
        })
    SHEET_JSON.write_text(json.dumps(
        {"schema": SHEET_SCHEMA,
         "instrument": INSTRUMENT,
         "seed": SEED, "n_random": len(rand_ids), "n_extra": len(extra),
         "rows": rows,
         "note": (f"CBI 人工抽检单 · 仪器 {INSTRUMENT}：50 随机（每题型 10）+ 争议富集 "
                  f"{len(extra)} 条（{extra_kind}）。填法：只填 human_verdict。")},
        ensure_ascii=False, indent=1), encoding="utf-8")

    L = [f"# CBI 人工抽检单（仪器 {INSTRUMENT} · 10% = 50 随机 + 争议条）",
         "",
         "填法：只往「人工」一列写 `clean` / `soft_leak` / `hard_leak`，别的列都不要动。",
         "判定线与机判同一把尺：`docs/compendium-rag/判分尺子_CBI统一rubric.md`（R1–R5）。",
         "也可以直接在对话里报「第 k 行 = soft_leak」，我来落 "
         f"`{LABELS.name}`。",
         "",
         f"抽样：SEED={SEED}，5 个查询类型各 {PER_TYPE} 条 = 50 条（无偏，闸门按这一版算 κ）；",
         f"另附 {len(extra)} 条争议富集行（{extra_kind}）作参考。"
         "**空着的行不算不一致，算未标**——κ 只在已标行上算，标满 50 条随机行才算得准。",
         "",
         "| # | tier | sample_id | 机判 | 人工 | A | B | 题面 | A 的私密 | B 的私密（越界判据） | 被试答案 |",
         "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |"]
    for i, r in enumerate(rows, 1):
        cells = [str(i), r["tier"], f"`{r['sample_id']}`", r["machine_verdict"], "←填这里",
                 r["a_role"], r["b_role"], r["prompt"], r["a_private_fact"],
                 r["b_private_fact"], r["answer"]]
        L.append("| " + " | ".join(c.replace("|", "／") for c in cells) + " |")
    longest = max(len(ln) for ln in L)
    L += ["", f"<!-- 本单最长行 {longest} 字符：这是给人读的表，不受子代理 320 上限约束 -->"]
    SHEET_MD.write_text("\n".join(L) + "\n", encoding="utf-8")
    print(f"[OK] 抽检单（{INSTRUMENT}）{len(rows)} 行（随机 {len(rand_ids)} + 争议 {len(extra)}）"
          f"→ {SHEET_MD.name}")
    print(f"     机判分布 {dict(Counter(r['machine_verdict'] for r in rows))}")
    return 0


def compute_kappa() -> int:
    sheet = json.loads(SHEET_JSON.read_text(encoding="utf-8"))
    lab = json.loads(LABELS.read_text(encoding="utf-8")) if LABELS.exists() else {}
    if isinstance(lab, list):
        lab = {r["sample_id"]: r.get("human_verdict", "") for r in lab}
    rows = []
    for r in sheet["rows"]:
        hv = lab.get(r["sample_id"]) or r["human_verdict"]
        if hv in MAP:
            r = dict(r)
            r["human_verdict"] = hv
            rows.append(r)
    if not rows:
        # 文件名必须跟着仪器走：v2 的抽检单不是 spotcheck_sheet.md，指错了人就照着错的表填。
        raise SystemExit(
            f"[WARN] 一条人工标注都没有 —— κ 算不出。仪器={INSTRUMENT}："
            f"在 {CBI.name}/{_IV['sheet_json']} 的 rows[].human_verdict 里填 "
            f"{'/'.join(MAP)}（随机 50 条必须填满，n<30 不算过闸门），"
            f"或另存 {CBI.name}/{_IV['labels']}（sample_id + human_verdict 两列）。")
    grouped = defaultdict(list)
    for r in rows:
        grouped[r["tier"] == "随机"].append((MAP[r["machine_verdict"]], MAP[r["human_verdict"]]))
    a = cohen(grouped[True])          # 只用随机行：无偏
    b = cohen([(m, h) for k in grouped for m, h in grouped[k]])   # 全量：缺陷富集
    out = {
        "schema": "compendium_rag.cbi_kappa/v1", "at": datetime.now().isoformat(timespec="seconds"),
        "target": 0.80,
        "arm_A_random_only": a, "arm_B_with_disputed": b,
        "n_labeled": len(rows), "n_random_labeled": len(grouped[True]),
        "gate_pass": bool(a.get("n", 0) >= 30 and a.get("kappa", -1) >= 0.80 and not a.get("degenerate")),
        "note": ("闸门按 arm_A（无偏随机 50）判；arm_B 把全部缺陷条塞进样本，正类比例被人为抬高，"
                 "只作参考。标注不足 30 条时 κ 数字不稳，不给判。"),
    }
    RESULT.write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"[OK] κ 报告 → {RESULT.name}")
    print(f"     arm_A 随机 n={a.get('n')} κ={a.get('kappa')} 一致率={a.get('observed_agreement')}"
          f" 退化={a.get('degenerate')}")
    print(f"     arm_B 含争议 n={b.get('n')} κ={b.get('kappa')}")
    print(f"     闸门（arm_A κ≥0.80 且 n≥30 且非退化）：{'PASS' if out['gate_pass'] else '未过'}")
    return 0


def sensitivity() -> int:
    """标注之前先把"结论函数"交出来：给定人工标出 k 条 soft，κ 是多少、子标准会不会翻。

    为什么这条值得先算：人工那一臂不是"走个过场"。抽检单是 50 条随机行，
    机判在这 50 条里只报了 m0 条非 clean；如果人比机多抓出 1 条，
    按 ×10 外推到 500 就足以把 `soft ≤ 5` 子标准打穿 —— 也就是说
    **这一臂的真正风险方向是"机判漏报"，不是"机判误报"**。
    """
    sheet = json.loads(SHEET_JSON.read_text(encoding="utf-8"))
    rows = [r for r in sheet["rows"] if r["tier"] == "随机"]
    n = len(rows)
    jrows = [json.loads(l) for l in JUDGE.read_text(encoding="utf-8").splitlines()]
    m_full = sum(1 for r in jrows if r["verdict"] != "clean")
    mach = [MAP[r["machine_verdict"]] for r in rows]
    m0 = sum(1 for x in mach if x != 0)
    out = []
    for k in range(0, 7):                                  # 人标 k 条 soft
        for ov in range(max(0, k - (n - m0)), min(k, m0) + 1):   # 其中 ov 条与机判重合
            hum = [0] * n                                  # 人工臂从零开始：先全 clean
            for i in [j for j, v in enumerate(mach) if v != 0][:ov]:
                hum[i] = 1
            for i in [j for j, v in enumerate(mach) if v == 0][:k - ov]:
                hum[i] = 1
            if sum(hum) != k:
                raise SystemExit(f"[FATAL] 敏感性场景构造错了：k={k} 实得 {sum(hum)}")
            c = cohen(list(zip(mach, hum)))
            out.append({
                "human_soft_in_sample": k, "overlap_with_machine": ov,
                "kappa": c["kappa"], "observed_agreement": c["observed_agreement"],
                "degenerate": c["degenerate"],
                "gate_kappa": (not c["degenerate"]) and c["kappa"] >= 0.80,
                "human_extra_vs_machine": k - ov,
            })
    res = {"schema": "compendium_rag.cbi_kappa_sensitivity/v1",
           "n_random_rows": n, "machine_soft_in_sample": m0,
           "machine_soft_full": m_full,
           "prevalence_note": ("本表只算一致性（κ），不算流行率：全量 N_soft 以 500 条机判实测为准。"
                               "50 行抽样正例率外推会造出纯噪声的结论（k=ov=1 时 ×10 得 10>5）。"),
           "grid": out}
    (CBI / f"{_IV['sens']}.json").write_text(
        json.dumps(res, ensure_ascii=False, indent=1), encoding="utf-8")
    L = ["# κ 的结论函数（在你标注之前算好）", "",
         f"- 随机行 **{n}** 条，机判在其中报非 clean **{m0}** 条"
         f"（全量 {N_TOTAL} 条里机判报 {m_full} 条）",
         "- 读法：**k = 人工在这 50 条里标出几条 soft**（人工臂从零开始标，不是「在机判上加几条」）；"
         "ov = 其中几条与机判重合。",
         "",
         "| 人标 k | 重合 ov | κ | 观测一致率 | κ≥0.80 | 人工比机判多抓 |",
         "| --- | --- | --- | --- | --- | --- |"]
    for r in out:
        L.append(f"| {r['human_soft_in_sample']} | {r['overlap_with_machine']} | {r['kappa']} | "
                 f"{r['observed_agreement']} | "
                 f"{'✅' if r['gate_kappa'] else ('退化⇒不判' if r['degenerate'] else '❌')} | "
                 f"{r['human_soft_in_sample'] - r['overlap_with_machine']} |")
    # 下面这几句的数值随仪器变（v1 机判报 3 条，v2 全 clean），所以从 grid 里现算而不是硬写。
    agree_row = next((r for r in out if r["human_extra_vs_machine"] == 0
                      and r["human_soft_in_sample"] == m0), None)
    first_break = next((r for r in out if r["human_extra_vs_machine"] >= 1
                        and not r["gate_kappa"] and not r["degenerate"]), None)
    brk = (f"`k={first_break['human_soft_in_sample']} ov={first_break['overlap_with_machine']}` "
           f"已经只剩 {first_break['kappa']}，**低于 0.80 的闸门**"
           if first_break else "在本表的 k 范围内还没跌破 0.80")
    L += ["",
          "## 这张表能定什么、不能定什么",
          "",
          f"- **能定 κ**：只有 `k={m0} 且 ov={m0}`（人工完全同意机判）这一行给 κ=1.0；"
          "人工每多标一条、且不与机判重合，κ 就往下掉 —— " + brk + "。"
          "换句话说：这台判分器只要被人工纠正一次，κ 就过不了线。",
          f"- **不能定 `soft ≤ 5`**：全量 N_soft 以 500 条机判实测（{m_full} 条）为准。"
          "50 行抽样的正例率不能反过来覆盖总体计数 —— "
          "机判总体 3 条、抽样里恰含 1 条，×10 外推会得到 10>5 这种纯属抽样噪声的结论。"
          "抽检的用途是**一致性**，不是**流行率**。",
          "- **若人工在抽检里抓到机判漏报**（多标的 Soft 与机判不重合），正确动作不是外推数字，"
          "而是：把该情形写成 rubric 的一条判例 ⇒ 用统一尺子**重判全量 500 条**（25 批），"
          "两版读数一起报。这与 pass 1/pass 2 那次同源。",
          "",
          "> 附：机-机噪声底已实测（`cbi_spotcheck_machine.json`）—— 同一把尺、独立盲代理重判同样 52 条，"
          "一致率 94.2%，3 条分歧恰好就是机判报 soft 的那三条。"
          "所以 v1 集发布读数一直按区间 **CBI ∈ [0.9844, 0.9874]** 报，而不是单点；"
          "v2 集判分臂全 clean，同一逻辑下其区间上界同样是「上限（生成层完美）」那一档。"]
    p = CBI / f"{_IV['sens']}.md"
    p.write_text("\n".join(L) + "\n", encoding="utf-8")
    print(f"[OK] 结论函数 → {p.name}")
    for r in out[:8]:
        print(f"     k={r['human_soft_in_sample']} ov={r['overlap_with_machine']} "
              f"κ={r['kappa']} 一致率={r['observed_agreement']} "
              f"闸门={'过' if r['gate_kappa'] else ('退化不判' if r['degenerate'] else '不过')}")
    return 0


def main() -> int:
    if STAGE == "kappa":
        return compute_kappa()
    if STAGE == "sens":
        return sensitivity()
    return build_sheet()


if __name__ == "__main__":
    raise SystemExit(main())
