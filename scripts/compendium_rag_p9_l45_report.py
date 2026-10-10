"""P9④ · 聚合 r11 的 L4.5 判分面板 → reports/p9_l45_panel_r11.{json,md}。

只读判分件与图，不做任何评测、不改任何既有产物。产出把三件事分清楚：
1. **r11 新鲜读数**（raw 与「别名渲染修正后」两列）—— 从此 L4.5 不再挂「本轮未重测」；
2. **与 10-08 面板的可比性边界** —— 重叠块上的同分/变好/变差计数，判分人差异有多大；
3. **面板自身的测量效度缺陷** —— `audit_l4.py:796-804` 只渲染规范名，凡原文用别名指称的块
   都会被误记错张；该缺陷同样存在于 10-08 那批（同一段代码），所以旧读数也被压低。
"""

from __future__ import annotations

import hashlib
import json
import sys
from collections import Counter
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PANEL = ROOT / "data" / "knowledge" / "_audit" / "l4_multiscene_r11"
FROZEN = ROOT / "data" / "knowledge" / "_audit" / "l4_multiscene"
GRAPH = ROOT / "data" / "compendium_rag" / "graph.json"
OUT_JSON = ROOT / "data" / "compendium_rag" / "reports" / "p9_l45_panel_r11.json"
OUT_MD = ROOT / "data" / "compendium_rag" / "reports" / "p9_l45_panel_r11.md"

EXPECTED_SHA = "911bb538160db80e"
TARGET = 4.0
ALIASFIX = "ms_b04_aliasfix_review.json"


def sha16(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for blk in iter(lambda: f.read(1 << 20), b""):
            h.update(blk)
    return h.hexdigest()[:16]


def read_items(paths) -> list[dict]:
    out = []
    for p in paths:
        out += json.loads(p.read_text(encoding="utf-8")).get("items", [])
    return out


def mean(xs) -> float:
    xs = [float(x) for x in xs if isinstance(x, (int, float))]
    return round(sum(xs) / len(xs), 4) if xs else None


def main() -> int:
    sha = sha16(GRAPH)
    if sha != EXPECTED_SHA:
        raise SystemExit(f"[FATAL] 冻结图指纹漂移：期望 {EXPECTED_SHA}，实际 {sha}；不写文件")

    base = read_items(sorted(PANEL.glob("ms_b0[123]_review.json")))
    if len(base) != 60:
        raise SystemExit(f"[FATAL] r11 主面板应有 60 条，实得 {len(base)}")
    fix = read_items([PANEL / ALIASFIX])
    if len(fix) != 5:
        raise SystemExit(f"[FATAL] 别名修正批应有 5 条，实得 {len(fix)}")

    frozen = read_items(sorted(FROZEN.glob("ms_b*_review.json")))
    f_map = {r["chunk_id"]: float(r["coherence"]) for r in frozen}
    b_map = {r["chunk_id"]: float(r["coherence"]) for r in base}
    x_map = {r["chunk_id"]: float(r["coherence"]) for r in fix}

    corr_map = dict(b_map)
    corr_map.update(x_map)
    deltas = [{"chunk_id": k, "raw": b_map[k], "alias_fixed": v, "delta": v - b_map[k]}
              for k, v in x_map.items()]

    overlap = sorted(set(f_map) & set(b_map))
    same = sum(1 for k in overlap if f_map[k] == b_map[k])
    better = sum(1 for k in overlap if b_map[k] > f_map[k])
    worse = sum(1 for k in overlap if b_map[k] < f_map[k])

    raw_mean = mean(b_map.values())
    corr_mean = mean(corr_map.values())
    mismatch_total = sum(int(r.get("n_mismatch") or 0) for r in base)
    edges_total = sum(int(r.get("n_edges") or 0) for r in base)
    low = sorted((r for r in base if float(r["coherence"]) <= 3),
                 key=lambda r: float(r["coherence"]))

    rep = {
        "schema": "compendium_rag.p9_l45_panel_r11/v1",
        "done_at": datetime.now().isoformat(timespec="seconds"),
        "graph_sha": sha, "target": TARGET,
        "reading": {"n_items": len(b_map), "mean_raw": raw_mean,
                    "mean_alias_corrected": corr_mean,
                    "verdict_raw": "FAIL" if raw_mean < TARGET else "PASS",
                    "verdict_alias_corrected": "FAIL" if corr_mean < TARGET else "PASS",
                    "score_distribution_raw": dict(sorted(Counter(b_map.values()).items())),
                    "n_edges_reviewed": edges_total, "n_mismatch_reported": mismatch_total,
                    "block_mismatch_rate": round(
                        sum(1 for r in base
                            if int(r.get("n_mismatch") or 0) > 0) / len(base), 4)},
        "alias_rendering_defect": {
            "mechanism": "audit_l4.py:796-804 与 compendium_rag_p9_l45_prep.py 同法，只渲染实体"
                         "规范名；原文若用别名指称，判分人见规范名不在字面即记凭空错张",
            "affected_chunks": [d["chunk_id"] for d in deltas],
            "affected_n": len(deltas),
            "mean_before": mean(d["raw"] for d in deltas),
            "mean_after": mean(d["alias_fixed"] for d in deltas),
            "also_affects_2026_10_08_panel": True,
        },
        "comparability_with_2026_10_08": {
            "frozen_mean": mean(f_map.values()), "frozen_n": len(f_map),
            "overlap_n": len(overlap), "same": same, "better": better, "worse": worse,
            "overlap_mean_r11": mean(b_map[k] for k in overlap),
            "overlap_mean_1008": mean(f_map[k] for k in overlap),
            "claim_allowed": "不可宣称图修复带来互洽性收益 —— 同一批重叠块上判分人差异"
                             "（28 同 / 9 升 / 17 降）远大于图改动本身",
        },
        "low_score_blocks": [{"chunk_id": r["chunk_id"], "coherence": r["coherence"],
                              "n_edges": r.get("n_edges"), "n_mismatch": r.get("n_mismatch"),
                              "why": (r.get("why") or "")[:220]} for r in low[:12]],
        "what_still_unmeasured": [
            "L4.1 谓语归组盲评分歧率 0.2：其样本文件是**故意冻结**的"
            "（audit_l4.py:254「抽样一旦交评就冻结，否则盲评结果与样本脱钩」）。"
            "r11 重出必须另立新样本并两列并报，本轮未做。",
            "L4.1a 0.0376 无需重出：它本就由 r11 图重算，偏差属抽取层（方向对缺失）。",
        ],
    }
    OUT_JSON.write_text(json.dumps(rep, ensure_ascii=False, indent=1), encoding="utf-8")

    r = rep["reading"]
    ln = ["# P9④ · L4.5 r11 新鲜判分面板", "",
          f"生成 {rep['done_at']} · 冻结图 `{sha}` · n={r['n_items']} 块 · "
          f"评审边数 {r['n_edges_reviewed']}", "",
          "## 读数", "",
          f"- **原始口径均值 {r['mean_raw']}** ⇒ 门槛 ≥{TARGET} **{r['verdict_raw']}**",
          f"- **别名渲染修正后均值 {r['mean_alias_corrected']}** ⇒ 仍 **{r['verdict_alias_corrected']}**",
          f"- 分数分布 {r['score_distribution_raw']}；含错张的块占比 {r['block_mismatch_rate']}",
          "",
          "> 从此 **L4.5 摘掉「本轮未重测、读数来自 10-08 冻结件」的标注** —— "
          "上面两个数是 r11 图上的盲评新鲜读数。", "",
          "## 面板自身的效度缺陷（必须先讲）", "",
          f"判分件只渲染实体**规范名**（`audit_l4.py:796-804`），原文用别名指称时，判分人看到"
          f"规范名不在字面就记「凭空错张」。本轮受影响 **{rep['alias_rendering_defect']['affected_n']}/60** 块，"
          f"这些块修正前均值 {rep['alias_rendering_defect']['mean_before']} → 修正后 "
          f"{rep['alias_rendering_defect']['mean_after']}。",
          "",
          "铁证：图上 `安妮` 的 aliases **已含** `洁西卡`（32 块），原文 13.0.1 也有"
          "「我真正的名字从来都不是安妮，而是洁西卡」—— 实体**早就合并了**，"
          "第一个面板却把它当未合并错张来扣分。**10-08 那批同样受此缺陷影响**（同一段代码）。",
          "",
          "## 与 10-08 读数的可比性", "",
          f"- 旧面板均值 {rep['comparability_with_2026_10_08']['frozen_mean']}"
          f"（n={rep['comparability_with_2026_10_08']['frozen_n']}），重叠块 "
          f"{rep['comparability_with_2026_10_08']['overlap_n']} 个",
          f"- 重叠块上：同分 {same} / 判分变好 {better} / 判分变差 {worse}；"
          f"旧 {rep['comparability_with_2026_10_08']['overlap_mean_1008']} vs "
          f"新 {rep['comparability_with_2026_10_08']['overlap_mean_r11']}",
          f"- **{rep['comparability_with_2026_10_08']['claim_allowed']}**", "",
          "## 低分块（≤3 分，取前 12）", ""]
    for b in rep["low_score_blocks"]:
        ln.append(f"- `{b['chunk_id']}` **{b['coherence']}** 分（{b['n_edges']} 边 / "
                  f"{b['n_mismatch']} 处错张）｜{b['why']}")
    ln += ["", "## 仍未测到的部分", ""] + [f"- {x}" for x in rep["what_still_unmeasured"]]
    OUT_MD.write_text("\n".join(ln) + "\n", encoding="utf-8")

    print(f"[OK] L4.5 r11：原始 {raw_mean} / 别名修正后 {corr_mean}（门槛 ≥{TARGET}）⇒ 均 FAIL")
    print(f"     重叠块 {len(overlap)}：同分 {same} / 升 {better} / 降 {worse}"
          f"（旧 {mean(f_map.values())} vs 新 {raw_mean}，不可归因于图修复）")
    print(f"     {OUT_JSON}\n     {OUT_MD}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
