"""尺子 v2 口径（用户 2026-10-11 裁决：`attributed_to_A` 记 hard）双列读数。

不改 `cbi_calculator.py`、不改任何 verdict 文件、不覆盖 `cbi_result_full.json`：
v2 = v1 判定 + 诊断臂 D1 的 `attributed_to_A` 叠加为 hard，两列并排报。
用法：.venv/Scripts/python.exe -X utf8 scripts/cbi_caliber_v2.py
"""
from __future__ import annotations

import json
import os
from pathlib import Path

ROOT = Path(os.environ.get("ROLEPLAY_ROOT", ".")).resolve()
REP = ROOT / "data" / "compendium_rag" / "reports"
CBID = REP / "cbi"
FULL = REP / "cbi_result_full.json"
JUDGE_V1 = CBID / "judge_full.jsonl"
DIAG = CBID / "diag_rows.jsonl"
OUT_JSON = REP / "cbi_result_v2hard.json"
OUT_MD = REP / "cbi_result_v2hard.md"

N = 500
W = {"hard": 1.0, "soft": 0.5, "retrieval": 0.3}
GATES = {"cbi": 0.97, "hard": 0, "soft": 5, "retrieval": 15}


def cbi(nh: int, ns: int, nr: int) -> float:
    return round(1 - (W["hard"] * nh + W["soft"] * ns + W["retrieval"] * nr) / N, 4)


def main() -> int:
    for p in (FULL, JUDGE_V1, DIAG):
        if not p.exists():
            raise SystemExit(f"[FATAL] 缺输入 {p}")
    res = json.loads(FULL.read_text(encoding="utf-8"))
    n_retr = res["counts"]["N_retrieval"]
    n_total = res["counts"]["N_total_effective"]
    if n_total != N:
        raise SystemExit(f"[FATAL] 分母 {n_total} != {N}，本脚本按 500 写死")

    v1: dict[str, str] = {}
    for ln in JUDGE_V1.read_text(encoding="utf-8").splitlines():
        if ln.strip():
            r = json.loads(ln)
            v1[r["sample_id"]] = r["verdict"]
    diag: dict[str, str] = {}
    for ln in DIAG.read_text(encoding="utf-8").splitlines():
        if ln.strip():
            r = json.loads(ln)
            diag[r["sample_id"]] = r["b_point_in_answer"]
    if len(v1) != N or len(diag) != N:
        raise SystemExit(f"[FATAL] v1 {len(v1)} / D1 {len(diag)}，都要正好 500")

    # v2：D1 判为 attributed_to_A / attributed_to_B 的行一律记 hard；其余沿用 v1。
    # v1 已经是 hard 的行保持 hard（当前是 0 条，这句只是防止将来读数静默变形）。
    promoted = sorted(k for k, c in diag.items() if c in ("attributed_to_A", "attributed_to_B"))
    overlap_with_v1_leak = [k for k in promoted if v1[k] != "clean"]
    v2 = dict(v1)
    for k in promoted:
        v2[k] = "hard_leak"

    def cnt(d: dict[str, str]) -> dict[str, int]:
        return {"hard": sum(1 for x in d.values() if x == "hard_leak"),
                "soft": sum(1 for x in d.values() if x == "soft_leak"),
                "clean": sum(1 for x in d.values() if x == "clean")}

    c1, c2 = cnt(v1), cnt(v2)
    r1, r2 = cbi(c1["hard"], c1["soft"], n_retr), cbi(c2["hard"], c2["soft"], n_retr)

    def gate(c: dict[str, int], reading: float) -> dict:
        return {"CBI>=0.97": reading >= GATES["cbi"],
                "N_hard=0": c["hard"] == GATES["hard"],
                "N_soft<=5": c["soft"] <= GATES["soft"],
                f"N_retrieval<=15": n_retr <= GATES["retrieval"]}

    g1, g2 = gate(c1, r1), gate(c2, r2)
    fails2 = [k for k, ok in g2.items() if not ok]
    verdict2 = ("完全发布" if not fails2 else
                "有条件发布 + P10 必修" if r2 >= 0.94 else "禁止发布")

    out = {
        "schema": "compendium_rag.cbi_result_v2hard/v1",
        "caliber_ruling": "用户 2026-10-11 裁决：诊断臂 D1 的 attributed_to_A 记 hard_leak",
        "graph_sha": res["graph_sha"], "mode": "full",
        "acceptance_caliber": res["acceptance_caliber"],
        "retrieval_channel_unchanged": n_retr,
        "promoted_rows": promoted,
        "promoted_overlap_with_v1_nonclean": overlap_with_v1_leak,
        "ruler_v1": {"counts": {**c1, "retrieval": n_retr}, "cbi": r1,
                     "gates": g1, "verdict": res["gate"]},
        "ruler_v2": {"counts": {**c2, "retrieval": n_retr}, "cbi": r2,
                     "gates": g2, "failed_gates": fails2, "verdict": verdict2},
        "note": "v1 读数未被覆盖：`cbi_result_full.json` 原样保留，本文件是并列的第二列",
    }
    OUT_JSON.write_text(json.dumps(out, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")

    L = ["# CBI 尺子 v2 口径读数（与 v1 并列，不替换）", "",
         "**裁决**：用户 2026-10-11 就 §R8 的 4 条 `attributed_to_A` 裁定 **记 hard_leak**。",
         f"实现方式：D1 判 `attributed_to_A` / `attributed_to_B` 的行一律记 hard，其余沿用 v1 判定；"
         f"检索通道 {n_retr} 条不动（口径裁决只动答案层那一格）。",
         f"图 sha `{res['graph_sha']}` 不变，零写图、零云端。",
         "",
         "| 尺子 | hard | soft | retrieval | CBI | 破的闸门 | 判定 |",
         "|--|--|--|--|--|--|--|"]
    for name, c, r, g, vd in (("v1（登记原样）", c1, r1, g1, res["gate"]),
                              ("v2（本次裁决）", c2, r2, g2, verdict2)):
        bad = "、".join(k for k, ok in g.items() if not ok) or "—"
        L.append(f"| {name} | {c['hard']} | {c['soft']} | {n_retr} | **{r}** | {bad} | {vd} |")
    L += ["", f"被提升的行（{len(promoted)} 条）：{promoted}",
          f"与 v1 已有非 clean 判定的重叠：{overlap_with_v1_leak or '无'}"
          "（重叠为 0 说明 v2 不是把同一条错误数两遍）",
          "",
          "## 这句话现在必须怎么说",
          "",
          f"- **CBI = {r2}（v2 口径）**，总式仍 ≥ 0.97；",
          f"- **`N_hard = {c2['hard']} ≠ 0`** ⇒ 北极星里「硬泄漏数 = 0」这一条**没达成**，"
          "发布档位是**有条件发布 + P10 必修**，不是「CBI 达标 + 硬泄漏零」；",
          "- 检索子标准照旧不过（21 > 15）；",
          "- v1 的 0.9844 只能在明确标注「登记尺子口径」时引用，且必须同时给出 v2 那一列。",
          "",
          "## v2 还只是一次「叠加」，不是一把重判过的尺子",
          "",
          "真正的尺子 v2 要把 R1 的原文改成「属于 A 自己、且不与 `fact_self` 矛盾的信息点」，"
          "然后**全量 500 条重判**。本次没有做那一步，因为：",
          "1. 用户同时批准了 R5bis（注入逐对独特化），新测试集上重判一次比在旧集上重判更值；",
          "2. 本列用的是 D1 的归属核对，它问的是「内容点有没有出现 + 挂在谁身上」，"
          "覆盖面比「v2 尺子会新抓到什么」更宽（`attributed_to_B` 也计入，实测 0 条），"
          "所以在旧集上它已经是一个**偏保守的下界**——但它不是 v2 的正式读数。",
          "正式 v2 读数随 R5bis 那一轮一起出。"]
    OUT_MD.write_text("\n".join(L) + "\n", encoding="utf-8")

    print(f"[OK] v1 {c1} CBI {r1} 判定 {res['gate']}")
    print(f"     v2 {c2} CBI {r2} 破闸 {fails2} 判定 {verdict2}")
    print(f"     提升 {len(promoted)} 行 {promoted}")
    print(f"     与 v1 非 clean 重叠 {overlap_with_v1_leak}")
    print(f"     → {OUT_JSON.name} / {OUT_MD.name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
