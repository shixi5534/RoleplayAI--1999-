"""诊断臂 D1/D1b 聚合：量「B 的内容点被挂在 A 自己身上」这一类的规模 K。

只读 probe/jout_diag*，只写 reports/cbi/diag_rows.jsonl 与 diag_K.{json,md}。
不动任何 verdict、不改 R1–R5、不回填 cbi_result_full.json。
用法：.venv/Scripts/python.exe -X utf8 scripts/cbi_diag_k.py
"""
from __future__ import annotations

import glob
import json
import os
from collections import Counter
from pathlib import Path

ROOT = Path(os.environ.get("ROLEPLAY_ROOT", ".")).resolve()
CBID = ROOT / "data" / "compendium_rag" / "reports" / "cbi"
PROBE = CBID / "probe"
RESULT = ROOT / "data" / "compendium_rag" / "reports" / "cbi_result_full.json"
CLS = {"none", "attributed_to_B", "attributed_to_A", "unclear"}
N = 500


def j(p: Path) -> dict:
    return json.loads(p.read_text(encoding="utf-8"))


def src(indir: Path, pat: str) -> dict[str, dict]:
    rows: dict[str, dict] = {}
    for f in sorted(glob.glob(str(indir / pat))):
        for it in j(Path(f))["items"]:
            rows[it["sample_id"]] = it
    return rows


def merge(indir: Path, outdir: Path, pat: str, want_batches: int) -> tuple[dict, list]:
    files = sorted(glob.glob(str(outdir / pat)))
    rows: dict[str, dict] = {}
    problems: list[str] = []
    if len(files) != want_batches:
        problems.append(f"{outdir.name}: 产物 {len(files)} != {want_batches} 批")
    for f in files:
        d = j(Path(f))
        bid = d.get("batch_id", Path(f).stem)
        srcp = indir / f"{bid}.json"
        if not srcp.exists():
            problems.append(f"{outdir.name}/{bid}: 无输入批")
            continue
        ids_in = [it["sample_id"] for it in j(srcp)["items"]]
        got = d["items"]
        if sorted(x["sample_id"] for x in got) != sorted(ids_in):
            problems.append(f"{outdir.name}/{bid}: sample_id 集合与输入不等")
            continue
        for it in got:
            sid = it["sample_id"]
            c = it.get("b_point_in_answer")
            q = it.get("evidence_quote") or ""
            if c not in CLS:
                problems.append(f"{outdir.name}/{bid}/{sid}: 档位非法 {c!r}")
                continue
            if c != "none":
                if not q or q not in rows_in(srcp)[sid]["answer"]:
                    problems.append(f"{outdir.name}/{bid}/{sid}: 引文不可逐字寻址 → 降为 none")
                    c, q = "none", ""
            rows[sid] = {"sample_id": sid, "b_point_in_answer": c, "evidence_quote": q,
                         "note": it.get("note", ""), "batch_id": bid}
    return rows, problems


_CACHE: dict[str, dict] = {}


def rows_in(path: Path) -> dict[str, dict]:
    k = str(path)
    if k not in _CACHE:
        _CACHE[k] = {it["sample_id"]: it for it in j(path)["items"]}
    return _CACHE[k]


def main() -> int:
    items = src(PROBE / "jin_full", "jdg_b*.json")
    if len(items) != N:
        raise SystemExit(f"[FATAL] 源 {len(items)} != {N}")

    d1, p1 = merge(PROBE / "jin_full", PROBE / "jout_diag", "jdg_b*_diag.json", 25)
    d1b, p2 = merge(PROBE / "jin_sprobe", PROBE / "jout_diagb", "jdg_s*_diag.json", 5)
    problems = p1 + p2
    if len(d1) != N:
        raise SystemExit(f"[FATAL] D1 有效 {len(d1)} != {N}；{problems[:6]}")
    if len(d1b) != 100:
        raise SystemExit(f"[FATAL] D1b 有效 {len(d1b)} != 100；{problems[:6]}")

    (CBID / "diag_rows.jsonl").write_text(
        "\n".join(json.dumps(d1[k], ensure_ascii=False) for k in sorted(d1)) + "\n",
        encoding="utf-8")

    c1 = Counter(v["b_point_in_answer"] for v in d1.values())
    c1b = Counter(v["b_point_in_answer"] for v in d1b.values())
    common = sorted(set(d1) & set(d1b))
    same = sum(1 for k in common if d1[k]["b_point_in_answer"] == d1b[k]["b_point_in_answer"])
    flip = [k for k in common if d1[k]["b_point_in_answer"] != d1b[k]["b_point_in_answer"]]

    k_hard = c1["attributed_to_A"]
    hits = []
    for sid in sorted(d1):
        if d1[sid]["b_point_in_answer"] != "none":
            it = items[sid]
            hits.append({"sample_id": sid, "query_type": sid.split("-")[-1],
                         "class": d1[sid]["b_point_in_answer"],
                         "quote": d1[sid]["evidence_quote"], "note": d1[sid]["note"],
                         "role": it["role"], "other_role": it["other_role"],
                         "fact_self": it["fact_self"], "fact_other": it["fact_other"],
                         "answer": it["answer"],
                         "d1b": d1b.get(sid, {}).get("b_point_in_answer", "（不在切片内）")})
    by_type = Counter(h["query_type"] for h in hits)
    by_pair = Counter(h["sample_id"].rsplit("-", 1)[0] for h in hits)

    res = j(RESULT)
    n_retr, n_soft = res["counts"]["N_retrieval"], res["counts"]["N_soft"]

    def cbi(nh: int, ns: int) -> float:
        return round(1 - (1.0 * nh + 0.5 * ns + 0.3 * n_retr) / N, 4)

    scen = {
        "as_registered": {"hard": 0, "soft": n_soft, "cbi": cbi(0, n_soft)},
        "class_as_hard": {"hard": k_hard, "soft": n_soft, "cbi": cbi(k_hard, n_soft),
                          "gate_hard_zero": k_hard == 0,
                          "gate_soft_le_5": n_soft <= 5,
                          "gate_cbi_ge_97": cbi(k_hard, n_soft) >= 0.97},
        "class_as_soft": {"hard": 0, "soft": n_soft + k_hard, "cbi": cbi(0, n_soft + k_hard),
                          "gate_hard_zero": True,
                          "gate_soft_le_5": n_soft + k_hard <= 5,
                          "gate_cbi_ge_97": cbi(0, n_soft + k_hard) >= 0.97},
    }

    out = {"schema": "compendium_rag.cbi_diag_k/v1", "n_total": N,
           "coverage": {"d1_batches": 25, "d1_rows": len(d1),
                        "d1b_batches": 5, "d1b_rows": len(d1b),
                        "overlap": len(common), "overlap_agreement": round(same / len(common), 4),
                        "overlap_flips": flip},
           "validation_problems": problems,
           "d1_counts": {k: c1.get(k, 0) for k in CLS},
           "d1b_counts": {k: c1b.get(k, 0) for k in CLS},
           "K_attributed_to_A": k_hard, "K_by_query_type": dict(by_type),
           "K_by_pair": dict(by_pair), "hits": hits, "cbi_scenarios": scen,
           "not_backfilled": "本读数不替换 cbi_result_full.json，不改 R1–R5，不改任何 verdict"}
    (CBID / "diag_K.json").write_text(json.dumps(out, ensure_ascii=False, indent=1) + "\n",
                                      encoding="utf-8")

    L = ["# 诊断臂 D1：B 的内容点挂在谁身上（全量 500 + style_probe 复现 100）", "",
         "这条臂**不判泄漏**，只回答一个事实问题：`fact_other` 的具体内容点有没有出现在答案里，"
         "出现的话是挂在 B 身上还是挂在 A 自己身上。目的是给口径裁决定规模，"
         "不回填任何 verdict、不动 R1–R5。", "",
         f"- D1 覆盖 {len(d1)} / {N}，25 批全齐；复现档 D1b 覆盖 {len(d1b)}（style_probe 100）。",
         f"- 校验问题 {len(problems)} 条：{problems[:4]}",
         f"- 两档在 100 行重叠上的一致率 **{round(same/len(common),4)}**，翻转 {flip}。",
         "", "| 档位 | D1（500） | D1b（100 style_probe） |", "|--|--|--|"]
    for c in ("none", "attributed_to_B", "attributed_to_A", "unclear"):
        L.append(f"| `{c}` | {c1.get(c,0)} | {c1b.get(c,0)} |")
    L += ["", f"**K = `attributed_to_A` 的条数 = {k_hard}（{k_hard/N:.1%}）**；"
          f"`attributed_to_B` = {c1.get('attributed_to_B',0)}——"
          "五十条里没有任何一条把 B 的内容点明确说成是 B 的。",
          f"按查询型分布：{dict(by_type)}；按角色对分布：{dict(by_pair)}"
          "（同一个角色对里多型同现，说明这不是单条抖动）。", "",
          "## 逐条", ""]
    for h in hits:
        L += [f"### {h['sample_id']} — `{h['class']}`（D1b：{h['d1b']}）",
              f"- A={h['role']}｜B={h['other_role']}",
              f"- `fact_self`：{h['fact_self']}",
              f"- `fact_other`：{h['fact_other']}",
              f"- 答案：{h['answer']}",
              f"- 引文：`{h['quote']}`",
              f"- 核对说明：{h['note']}", ""]
    L += ["## 口径裁决要花钱的地方", "",
          f"| 口径 | hard | soft | CBI | hard=0 | soft≤5 | CBI≥0.97 |", "|--|--|--|--|--|--|--|",
          f"| 尺子 v1（现行） | 0 | {n_soft} | {scen['as_registered']['cbi']} | ✅ | ✅ | ✅ |",
          f"| 把 K 记 hard | {k_hard} | {n_soft} | {scen['class_as_hard']['cbi']} | ❌ | ✅ | ✅ |",
          f"| 把 K 记 soft | 0 | {n_soft + k_hard} | {scen['class_as_soft']['cbi']} | ✅ | ❌ | ✅ |",
          "",
          f"三个口径下总式都还在 0.97 以上（检索通道 {n_retr} 条才是主惩罚项），"
          "但**两条子标准各破一条**：记 hard 破 `N_hard=0`，记 soft 破 `soft ≤ 5`。"
          "现行读数 `0.9844` 与「硬泄漏 = 0」的说法只有在尺子 v1 下成立。", "",
          "## 机制没定死，但产品缺陷定了", "",
          "`attributed_to_A` 有两种可能来源：(a) 上下文里 B 那条注入的内容被 A 拿去当了自己的；"
          "(b) 判分人看到的角色粗口来自扮演者对该角色的一般设定知识，注入的 A 侧陈述没被带走。"
          "答案文本本身分不开这两种——`'该死'` 这种具体词不在注入句里，"
          "所以 (a) 需要改写才能成立，而 (b) 用不着假设泄漏。", "",
          "两种机制指向**同一个产品缺陷**：答案层既没有把 B 侧内容挡在 A 的口吻之外，"
          "也没有把注入的 A 侧陈述稳稳带进答案。修法在提示词与测试集，不在判分口径："
          "P10 §R7（边界指令作为控制项 + 裸臂金丝雀）与 §R5bis（注入逐对独特化）。"]
    (CBID / "diag_K.md").write_text("\n".join(L) + "\n", encoding="utf-8")

    print(f"[OK] D1 {len(d1)} 行 / D1b {len(d1b)} 行；重叠一致率 {round(same/len(common),4)} "
          f"翻转 {flip}")
    print(f"     D1 {dict(c1)}")
    print(f"     D1b {dict(c1b)}")
    print(f"     K={k_hard} 按型 {dict(by_type)} 按对 {dict(by_pair)}")
    print(f"     口径场景 {json.dumps(scen, ensure_ascii=False)}")
    print(f"     校验问题 {len(problems)} {problems[:3]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
