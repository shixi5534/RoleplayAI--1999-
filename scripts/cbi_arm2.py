"""CBI 判分第二臂（独立重判抽检单的 52 条）：量 judge 自身的可重复性。

**这不是规格要的那一格** —— 规格写的是「LLM Judge 与人工一致性 κ ≥ 0.80」，
那一格只能由人出（task #9）。这里给的是**噪声底**：同一把尺子（`判分尺子_CBI统一rubric.md`）、
不同的盲代理，重判抽检单里同样 52 条，看机判自己稳不稳。
两种用途：
  1. 若机-机 κ 就已经低，那人工那格的 κ≥0.80 不可能是"模型问题"，而是判据本身不稳；
  2. 探针 pass 1/pass 2 换尺造成 0.935→0.970 的先例说明：判分器方差能量级到跨档，
     所以要一个数。

stage（CBI_STAGE）：
  build   从 `spotcheck_sheet.json` 造 3 份判分批（**不含任何机判结果**，第二臂看不到第一臂）；
  kappa   读 `probe/jout_arm2/jdg2_b*_verdict.json`，与第一臂算 Cohen κ + 一致率 + 混淆。

只读测试集与判分件；只写 `probe/jin_arm2/`、`reports/cbi/judge_arm2.jsonl`、
`reports/cbi_spotcheck_machine.json`。
"""

from __future__ import annotations

import json
import os
import sys
from collections import Counter
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from cbi_spotcheck import cohen, MAP          # 同一套判定映射与 κ 实现，别另写一份

REPORTS = ROOT / "data" / "compendium_rag" / "reports"
CBI = REPORTS / "cbi"
PROBE = CBI / "probe"
SHEET = CBI / "spotcheck_sheet.json"
JIN = PROBE / "jin_arm2"
JOUT = PROBE / "jout_arm2"
JUDGE1 = CBI / "judge_full.jsonl"
ARM2 = CBI / "judge_arm2.jsonl"
OUT = REPORTS / "cbi_spotcheck_machine.json"
STAGE = os.environ.get("CBI_STAGE", "build")
PER = 20


def build() -> int:
    rows = json.loads(SHEET.read_text(encoding="utf-8"))["rows"]
    ts = json.loads((REPORTS / "cbi_testset_500_control.json").read_text(encoding="utf-8"))
    samples = {s["sample_id"]: s for s in ts["samples"]}
    ans = {json.loads(l)["sample_id"]: json.loads(l)["answer"]
           for l in (CBI / "answers.jsonl").read_text(encoding="utf-8").splitlines()}
    JIN.mkdir(parents=True, exist_ok=True)
    for bi in range(0, len(rows), PER):
        items = []
        for r in rows[bi:bi + PER]:
            sid = r["sample_id"]
            s = samples[sid]
            items.append({"sample_id": sid, "role": s["perspective"],
                          "other_role": s["pair"]["b_name"], "query": s["prompt"],
                          "answer": ans[sid], "fact_self": s["injected"]["a_says"],
                          "fact_other": s["injected"]["b_says"]})
        body = json.dumps({"schema": "compendium_rag.cbi_judge_batch/v1",
                           "task": "判 answer 是否泄漏 other_role 的私密（三态）",
                           "items": items}, ensure_ascii=False, indent=1)
        longest = max(len(ln) for ln in body.splitlines())
        if longest > 320:
            raise SystemExit(f"[FATAL] 判分批超长行 {longest}，子代理 read 会截断")
        f = JIN / f"jdg2_b{bi // PER + 1:02d}.json"
        f.write_text(body, encoding="utf-8")
        json.loads(f.read_text(encoding="utf-8"))
        print(f"  {f.name}: {len(items)} 条 / {f.stat().st_size} B")
    print(f"[OK] 第二臂判分批 → {JIN}（共 {len(rows)} 条，含 0 条机判结果）")
    return 0


def kappa() -> int:
    v2, dup = {}, []
    for fp in sorted(JOUT.glob("jdg2_b*_verdict.json")):
        for it in json.loads(fp.read_text(encoding="utf-8")).get("items", []):
            sid = it.get("sample_id")
            if sid in v2 and v2[sid].get("verdict") != it.get("verdict"):
                dup.append(sid)
            v2[sid] = it
    if not v2:
        raise SystemExit(f"[FATAL] {JOUT} 里没有判分件，先派第二臂")
    v1 = {}
    for line in JUDGE1.read_text(encoding="utf-8").splitlines():
        r = json.loads(line)
        v1[r["sample_id"]] = r["verdict"]
    sheet = json.loads(SHEET.read_text(encoding="utf-8"))["rows"]
    ids = [r["sample_id"] for r in sheet]
    missing = [i for i in ids if i not in v2]
    if missing:
        raise SystemExit(f"[FATAL] 第二臂缺 {len(missing)} 条（未达 qid 集合相等）：{missing[:6]}")
    ARM2.write_text("".join(json.dumps({"sample_id": sid, "verdict": v2[sid]["verdict"],
                                        "evidence_quote": v2[sid].get("evidence_quote", ""),
                                        "why": v2[sid].get("why", "")}, ensure_ascii=False) + "\n"
                    for sid in ids), encoding="utf-8")
    pairs = [(MAP[v1[sid]], MAP[v2[sid]["verdict"]]) for sid in ids]
    c = cohen(pairs)
    out = {
        "schema": "compendium_rag.cbi_machine_reproducibility/v1",
        "at": datetime.now().isoformat(timespec="seconds"),
        "n": len(ids), "arm1": "judge_full.jsonl（本会话 25 批统一 rubric）",
        "arm2": "jout_arm2（独立盲代理重判，同一把尺，看不到第一臂结果）",
        "cohen_kappa_machine": c,
        "disagreements": [{"sample_id": s, "arm1": v1[s], "arm2": v2[s]["verdict"],
                           "arm2_confidence": v2[s].get("confidence")}
                          for s in ids if v1[s] != v2[s]["verdict"]],
        "arm2_distribution": dict(Counter(v2[s]["verdict"] for s in ids)),
        "arm1_distribution": dict(Counter(v1[s] for s in ids)),
        "intra_file_verdict_conflicts": dup,
        "status_of_the_spec_gate": ("未满足 —— 规格要的是机判 vs **人工**。"
                                    "这一格只是噪声底参考，不能拿来当 κ≥0.80 的达成证据。"),
    }
    OUT.write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"[OK] 机-机可重复性 → {OUT.name}")
    print(f"     n={c['n']} κ={c['kappa']} 一致率={c['observed_agreement']} "
          f"期望={c['expected_agreement']} 退化={c['degenerate']}")
    print(f"     arm1 {out['arm1_distribution']} ｜ arm2 {out['arm2_distribution']}")
    print("     注意：这不是规格要的那一格 κ（那一格要人标），只是噪声底")
    return 0


if __name__ == "__main__":
    raise SystemExit(kappa() if STAGE == "kappa" else build())
