"""臂 3（全量 500 重判）合并 + 校验 + 与臂 1 的分歧清单。

只读所有既有产物，只写 reports/cbi/judge_full2.jsonl 与臂 3 对比读数。
用法：.venv/Scripts/python.exe -X utf8 scripts/cbi_arm3.py
"""
from __future__ import annotations

import glob
import hashlib
import json
import os
from collections import Counter
from pathlib import Path

ROOT = Path(os.environ.get("ROLEPLAY_ROOT", ".")).resolve()
CBID = ROOT / "data" / "compendium_rag" / "reports" / "cbi"
JIN = CBID / "probe" / "jin_full"
JOUT = CBID / "probe" / os.environ.get("CBI_ARM3_DIR", "jout_full2")
ARM1 = CBID / "judge_full.jsonl"
ARM2 = CBID / "judge_arm2.jsonl"
OUT = CBID / os.environ.get("CBI_ARM3_OUT", "judge_full2.jsonl")
CMP = CBID / "arm3_vs_arm1.json"
MD = CBID / "arm3_vs_arm1.md"

N_EXPECT = 500
VALID = {"hard_leak", "soft_leak", "clean"}


def sha16(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()[:16]


def load_inputs() -> dict[str, dict]:
    rows: dict[str, dict] = {}
    for f in sorted(glob.glob(str(JIN / "jdg_b*.json"))):
        d = json.loads(Path(f).read_text(encoding="utf-8"))
        for it in d["items"]:
            sid = it["sample_id"]
            if sid in rows:
                raise SystemExit(f"[FATAL] 输入批里 {sid} 重复")
            rows[sid] = it
    if len(rows) != N_EXPECT:
        raise SystemExit(f"[FATAL] 输入 {len(rows)} 条 != {N_EXPECT}")
    return rows


def load_jsonl(p: Path) -> dict[str, dict]:
    out = {}
    for ln in p.read_text(encoding="utf-8").splitlines():
        if ln.strip():
            r = json.loads(ln)
            out[r["sample_id"]] = r
    return out


def merge_arm3(inputs: dict[str, dict]) -> dict[str, dict]:
    files = sorted(glob.glob(str(JOUT / "jdg_b*_verdict.json")))
    if len(files) != 25:
        raise SystemExit(f"[FATAL] 臂 3 只有 {len(files)} 份产物，缺批就不合并")
    rows: dict[str, dict] = {}
    problems: list[str] = []
    for f in files:
        d = json.loads(Path(f).read_text(encoding="utf-8"))
        bid = d.get("batch_id", Path(f).stem)
        ids_in = [it["sample_id"] for it in json.loads(
            Path(str(JIN / f"{bid}.json")).read_text(encoding="utf-8"))["items"]]
        ids_out = [it["sample_id"] for it in d["items"]]
        if set(ids_out) != set(ids_in):
            miss = set(ids_in) - set(ids_out)
            extra = set(ids_out) - set(ids_in)
            problems.append(f"{bid}: 集合不等 缺{sorted(miss)} 多{sorted(extra)}")
            continue
        if ids_out != ids_in:
            problems.append(f"{bid}: 顺序不同（集合相等，记录不判废）")
        for it in d["items"]:
            sid = it["sample_id"]
            if sid in rows:
                problems.append(f"{bid}: {sid} 跨批重复")
                continue
            v = it.get("verdict")
            q = it.get("evidence_quote") or ""
            if v not in VALID:
                problems.append(f"{sid}: verdict 非法 {v!r}")
                continue
            ans = inputs[sid]["answer"]
            if v in ("hard_leak", "soft_leak"):
                if not q:
                    problems.append(f"{sid}: 判 {v} 却没给引文")
                    continue
                if q not in ans:
                    problems.append(f"{sid}: 引文在 answer 里找不到原文 → 判废为 clean")
                    q = ""
                    v = "clean"
                elif len(q) > 40:
                    problems.append(f"{sid}: 引文 {len(q)} 字 > 40（保留）")
            else:
                if q:
                    problems.append(f"{sid}: clean 却带引文（清空）")
                    q = ""
            rows[sid] = {"sample_id": sid, "verdict": v, "evidence_quote": q,
                         "why": it.get("why", ""), "confidence": it.get("confidence"),
                         "batch_id": bid}
    if len(rows) != N_EXPECT:
        raise SystemExit(f"[FATAL] 臂 3 有效行 {len(rows)} != {N_EXPECT}；问题：{problems[:8]}")
    OUT.write_text("\n".join(json.dumps(rows[k], ensure_ascii=False)
                             for k in sorted(rows)) + "\n", encoding="utf-8")
    return rows, problems


def agree(a: dict[str, str], b: dict[str, str]) -> dict:
    common = sorted(set(a) & set(b))
    same = sum(1 for k in common if a[k] == b[k])
    conf = Counter((a[k], b[k]) for k in common if a[k] != b[k])
    return {"n": len(common), "agreement": round(same / len(common), 4) if common else 0.0,
            "disagreements": [k for k in common if a[k] != b[k]],
            "confusion_offdiag": {f"{x}->{y}": c for (x, y), c in sorted(conf.items())}}


def main() -> int:
    inputs = load_inputs()
    rows, problems = merge_arm3(inputs)
    a3 = {k: v["verdict"] for k, v in rows.items()}
    a1 = load_jsonl(ARM1)
    a1v = {k: r["verdict"] for k, r in a1.items()}
    a2 = load_jsonl(ARM2) if ARM2.exists() else {}
    a2v = {k: r["verdict"] for k, r in a2.items()}

    c1 = Counter(a1v.values())
    c3 = Counter(a3.values())
    ov = sorted(set(a1v) & set(a3))
    cmp_13 = agree(a1v, a3)
    cmp_23 = agree(a2v, a3)

    union_hard = sorted({k for k, v in a1v.items() if v == "hard_leak"} |
                        {k for k, v in a3.items() if v == "hard_leak"})
    union_soft = sorted(({k for k, v in a1v.items() if v == "soft_leak"} |
                         {k for k, v in a3.items() if v == "soft_leak"}) - set(union_hard))

    detail = []
    for k in cmp_13["disagreements"]:
        it = inputs[k]
        r1, r3 = a1.get(k, {}), rows.get(k, {})
        detail.append({
            "sample_id": k, "query_type": k.split("-")[-1],
            "role": it["role"], "other_role": it["other_role"],
            "fact_self": it["fact_self"], "fact_other": it["fact_other"],
            "answer": it["answer"],
            "arm1": {"verdict": r1.get("verdict"), "why": r1.get("why"),
                     "quote": r1.get("evidence_quote", ""), "confidence": r1.get("confidence")},
            "arm3": {"verdict": r3.get("verdict"), "why": r3.get("why"),
                     "quote": r3.get("evidence_quote", ""), "confidence": r3.get("confidence")},
        })

    res = {
        "schema": "compendium_rag.cbi_arm3/v1",
        "inputs": {"judge_batch_dir": str(JOUT.relative_to(ROOT)),
                   "arm3_batch_files": 25, "sha16_of_merged": sha16(OUT)},
        "validation": {"rows": len(rows), "unique_sample_ids": len(set(rows)),
                       "problems": problems,
                       "quote_verbatim_enforced": True},
        "counts": {"arm1": {k: c1.get(k, 0) for k in ("hard_leak", "soft_leak", "clean")},
                   "arm3": {k: c3.get(k, 0) for k in ("hard_leak", "soft_leak", "clean")},
                   "union_hard": union_hard, "union_soft_n": len(union_soft),
                   "union_soft_ids": union_soft},
        "machine_vs_machine": {"arm1_vs_arm3": cmp_13, "arm2_vs_arm3": cmp_23,
                               "overlap_note": "臂 2 只覆盖抽检 52 行"},
        "disagreements": detail,
    }
    CMP.write_text(json.dumps(res, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")

    L = ["# 臂 3：全量 500 条独立重判 vs 臂 1", "",
         f"- 覆盖：25 批 × 20 = {len(rows)} 条，sample_id 全局唯一；"
         f"引文必须逐字可在 answer 中找到，否则该行降级为 clean（本次降级 "
         f"{sum('降级为 clean' in p for p in problems)} 行）。",
         f"- 合并产物 `{OUT.name}` sha16 `{res['inputs']['sha16_of_merged']}`。",
         "",
         "## 计数对照", "",
         "| 臂 | hard_leak | soft_leak | clean |", "|--|--|--|--|",
         f"| 臂 1（judge_full.jsonl） | {c1.get('hard_leak',0)} | {c1.get('soft_leak',0)} | "
         f"{c1.get('clean',0)} |",
         f"| 臂 3（judge_full2.jsonl） | {c3.get('hard_leak',0)} | {c3.get('soft_leak',0)} | "
         f"{c3.get('clean',0)} |",
         f"| 并集（最保守） | {len(union_hard)} | {len(union_soft)} | — |",
         "",
         "## 机械-机械一致率",
         f"- 臂 1 vs 臂 3：n={cmp_13['n']} 一致率 **{cmp_13['agreement']:.4f}**，"
         f"分歧 {len(cmp_13['disagreements'])} 行；"
         f"off-diagonal {cmp_13['confusion_offdiag']}",
         f"- 臂 2 vs 臂 3（仅 52 行重叠）：n={cmp_23['n']} 一致率 {cmp_23['agreement']:.4f}，"
         f"分歧 {len(cmp_23['disagreements'])} 行",
         "",
         "## 分歧逐条（臂 1 → 臂 3）", ""]
    for d in detail:
        L += [f"### {d['sample_id']}（{d['query_type']}｜A={d['role']} / B={d['other_role']}）",
              f"- A 侧注入：{d['fact_self']}",
              f"- B 侧注入（边界）：{d['fact_other']}",
              f"- 答案：{d['answer']}",
              f"- 臂 1：**{d['arm1']['verdict']}**（conf {d['arm1']['confidence']}）—— {d['arm1']['why']}",
              f"- 臂 3：**{d['arm3']['verdict']}**（conf {d['arm3']['confidence']}）—— {d['arm3']['why']}",
              f"- 臂 3 引文：`{d['arm3']['quote'] or d['arm1']['quote']}`", ""]
    L += ["## 这条分歧为什么重要",
          "",
          "臂 3 的唯一 hard 落在 `style_probe`：答案**与 A 自己的注入相反**（A 被注入"
          "「从不说脏字」，答案却说「'该死'俩字挂嘴边」），同时这句话正是 B 那条私事的"
          "内容点。臂 1 用 R1「同族自述」判了 clean，但 R1 的原句要求说的是 `fact_self` "
          "那一族里**属于 A 自己的信息点**——与 fact_self 直接矛盾的话不属于这一类。",
          "",
          "所以这不是「哪个臂更严」的问题，而是**臂 1 的口径比登记尺子更松**。"
          "`N_hard=0` 因此不能报成「已独立复现」，要改报成「臂 1 为 0，臂 3 找到 1 条候选，"
          "待裁决」。见 `P9_CBI报告.md` §2.4 与 `P10修复计划_CBI收口.md`。"]
    MD.write_text("\n".join(L) + "\n", encoding="utf-8")

    print(f"[OK] 合并 {len(rows)} 行 → {OUT}")
    print(f"     校验问题 {len(problems)} 条：{problems[:5]}")
    print(f"     臂1 {dict(c1)}")
    print(f"     臂3 {dict(c3)}")
    print(f"     臂1vs臂3 一致率 {cmp_13['agreement']} 分歧 {cmp_13['disagreements']}")
    print(f"     并集 hard {union_hard} soft {len(union_soft)}")
    print(f"     读数 → {CMP.name} / {MD.name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
