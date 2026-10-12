"""抽检单完整性自检（纯只读，一个字节都不写）。

为什么要有：`spotcheck_sheet_{v1,v2}.md` 是**人工那一臂的界面**。四层审计时吃过
"上下文被截到 3000 字符 ⇒ 把'没看到'当成'确实没有'"的亏，所以这里要把界面和证据源对上：
  1) md 表体逐行逐格 == json 原始字段（唯一允许的差：单元格里的 `|` 转义成全角 `／`）
     ⇒ 证明题面 / A 的私密 / B 的私密 / 被试答案**都没被截**；
  2) 「人工」列只能是占位符、json 的 `human_verdict` 必须全空
     ⇒ 证明我没有预填、没有替你标（那一格的定义就是人怎么判）；
  3) 行数 == sheet 生产端的行数，列数每行都是 11 ⇒ 表格没断列；
  4) 血缘（lineage）：抽检单每一行的 12 个字段都要能在**四个原始件**里逐字找到
     （测试集 / 答案件 / 判分件 / 检索件），外加"判分金标 ≡ B 的注入句"。
     覆盖边界：血缘只看抽到的这 53 行；其余 447 行由第 5 项的全量计数兜 ——
     这条边界是被负向测试逼出来后才写进断言的（见 `cbi_sheet_integrity_negtest.py`）；
  5) 独立重算（rederive）：**换个实现**重算发布读数。权重不取计算器的常量，
     而是从读数里登记的那句 formula 文本解析；判分臂/答案件文件名要与抽检单同源。
     注意：v2 那一列 N_hard=N_soft=0 ⇒ 在 v2 上改这两个权重测不出差别，
     权重守护只有在还有非零项的 v1 列上才可证伪。

用法：`PYTHONIOENCODING=utf-8 .venv/Scripts/python.exe scripts/cbi_sheet_integrity.py`
负向测试：`PYTHONIOENCODING=utf-8 .venv/Scripts/python.exe scripts/cbi_sheet_integrity_negtest.py`
"""
from __future__ import annotations

import importlib.util
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPORTS = ROOT / "data" / "compendium_rag" / "reports"
CBI = REPORTS / "cbi"
ESC = "|"                       # 写表时 `|` 被换成全角 `／`（U+FF0F）
HUMAN_PLACEHOLDER = "←填这里"
# 发布读数各自的文件名：v1 是全量那一版（0.9844），v2 是 R5bis 那版（0.9820）
READING = {"v1": "cbi_result_full.json", "v2": "cbi_result_v2instrument.json"}

# 仪器→文件名只认 `cbi_spotcheck._INSTRUMENTS` 这一份，避免这里再抄一遍常量后各自过期
sys.path.insert(0, str(ROOT / "scripts"))
_spec = importlib.util.spec_from_file_location(
    "cbi_spotcheck_for_integrity", ROOT / "scripts" / "cbi_spotcheck.py")
SPOT = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(SPOT)


def samples_of(inst: str) -> dict:
    d = json.loads((REPORTS / SPOT._INSTRUMENTS[inst]["testset"]).read_text(encoding="utf-8"))
    rows = d["samples"] if isinstance(d, dict) and "samples" in d else d
    return {s["sample_id"]: s for s in rows}
# 列序：# | tier | sample_id | 机判 | 人工 | A | B | 题面 | A私密 | B私密 | 被试答案
EVIDENCE_COLS = [(7, "prompt"), (8, "a_private_fact"),
                 (9, "b_private_fact"), (10, "answer"), (3, "machine_verdict")]


def check(inst: str, sheet_json: str, sheet_md: str, fails: list[str]) -> None:
    rows = json.loads((CBI / sheet_json).read_text(encoding="utf-8"))["rows"]
    body = [[c.strip() for c in ln.strip().strip("|").split("|")]
            for ln in (CBI / sheet_md).read_text(encoding="utf-8").split("\n")
            if re.match(r"^\|\s*\d+\s*\|", ln)]
    print(f"[{inst}] 表体 {len(body)} 行 / json {len(rows)} 行")
    if len(body) != len(rows):
        fails.append(f"{inst} 表体行数与 json 不一致")
        return
    bad_cols = [i for i, c in enumerate(body, 1) if len(c) != 11]
    diffs = []
    for i, (cell, r) in enumerate(zip(body, rows), 1):
        if len(cell) != 11:
            continue
        for j, key in EVIDENCE_COLS:
            want = (r.get(key) or "").strip().replace(ESC, "／")
            if cell[j] != want:
                diffs.append((i, key, len(cell[j]), len(want)))
    print(f"    断行列数!=11 的行: {bad_cols}")
    print(f"    证据单元格与 json 不等价: {len(diffs)} 处 {diffs[:3]}")
    if diffs or bad_cols:
        fails.append(f"{inst} 界面与证据源不一致（{len(diffs)} 格 / {len(bad_cols)} 断列）")
    human = {c[4] for c in body}
    prefill = [r["sample_id"] for r in rows if r.get("human_verdict")]
    print(f"    人工列取值集合: {human} | json 已预填的行: {len(prefill)}")
    if human != {HUMAN_PLACEHOLDER} or prefill:
        fails.append(f"{inst} 人工列被预填过 ⇒ 这一臂不再是人的判断")
    print(f"    最长行 {max(len(ln) for ln in (CBI / sheet_md).read_text(encoding='utf-8').splitlines())} 字符")


def lines(p: Path) -> list[dict]:
    return [json.loads(l) for l in p.read_text(encoding="utf-8").splitlines() if l.strip()]


def lineage(inst: str, fails: list[str]) -> None:
    """第 4 项：抽检单里的每一格，都要能在**四个原始件**里逐字找到。
    人标这一臂比的是"人工 vs 机判"，所以它看到的题面/答案必须是**判分臂当时看到的那一份**；
    否则 κ 量的是"人与另一个输入版本的一致率"，而发布读数却是这个版本 —— 一格墙缝。
    """
    iv = SPOT._INSTRUMENTS[inst]
    rows = json.loads((CBI / iv["sheet_json"]).read_text(encoding="utf-8"))["rows"]
    ts = samples_of(inst)
    ans = {r["sample_id"]: r["answer"] for r in lines(CBI / iv["answers"])}
    jd = {r["sample_id"]: r for r in lines(CBI / iv["judge"])}
    rt = {r["sample_id"]: r for r in lines(CBI / iv["retrieval"])}
    bad = []
    for r in rows:
        sid = r["sample_id"]
        if sid not in ts:
            bad.append((sid, "sample_id 不在测试集里"))
            continue
        s = ts[sid]
        want = [("prompt", s["prompt"]), ("a_private_fact", s["injected"]["a_says"]),
                ("b_private_fact", s["injected"]["b_says"]), ("query_type", s["query_type"]),
                ("conflict_type", s.get("conflict_type", "")), ("a_role", s["perspective"]),
                ("b_role", s["pair"]["b_name"]), ("answer", ans.get(sid)),
                ("machine_verdict", jd.get(sid, {}).get("verdict")),
                ("machine_evidence", jd.get(sid, {}).get("evidence_quote", "")),
                ("machine_why", jd.get(sid, {}).get("why", "")),
                ("retrieval_leak", rt.get(sid, {}).get("retrieval_leak"))]
        for key, v in want:
            if r.get(key) != v:
                bad.append((sid, key))
    print(f"[{inst}] 血缘：抽检单 {len(rows)} 行 × 12 个字段对四个原始件逐字回查 ⇒ 不一致 {len(bad)} 处 {bad[:3]}")
    if bad:
        fails.append(f"{inst} 血缘断裂（{len(bad)} 处）")
    # 判分金标 ≡ 注入句：这条已在 spec_block 里对全 500 条测过，这里只对**人要标的 53 行**再测一遍
    gold_bad = [r["sample_id"] for r in rows
                if not (lambda g, b: (g == b) if isinstance(g, str) else bool(g) and b in g)(
                    ts[r["sample_id"]]["judge_gold"].get("must_not_state"),
                    ts[r["sample_id"]]["injected"]["b_says"])]
    print(f"    判分金标 ≡ B 的注入句：{len(rows) - len(gold_bad)}/{len(rows)} 对得上 {gold_bad[:2]}")
    if gold_bad:
        fails.append(f"{inst} 有 {len(gold_bad)} 行的金标与注入句不一致")


def rederive(inst: str, fails: list[str]) -> None:
    """第 5 项：**换一个实现**重算发布读数。
    权重不取计算器的常量，而是从读数里**登记的那句 formula 文本**里解析出来 ——
    这样如果谁改了权重或改了分母，这里会以"解析不到三项权重"或"重算值不等"报红，
    而不是跟着常量一起被改掉。
    """
    iv = SPOT._INSTRUMENTS[inst]
    rd = json.loads((REPORTS / READING[inst]).read_text(encoding="utf-8"))
    w = dict((float(m[0]), m[1]) for m in re.findall(r"([\d.]+)\*N_(hard|soft|retrieval)",
                                                     rd.get("formula", "")))
    weights = {k: v for v, k in w.items()}
    if set(weights) != {"hard", "soft", "retrieval"}:
        fails.append(f"{inst} 登记公式解析不出三项权重：{rd.get('formula')!r}")
        return
    jd = lines(CBI / iv["judge"])
    rt = lines(CBI / iv["retrieval"])
    n_hard = sum(1 for r in jd if r["verdict"] == "hard_leak")
    n_soft = sum(1 for r in jd if r["verdict"] == "soft_leak")
    n_retr = sum(1 for r in rt if r["retrieval_leak"])
    n_eff = rd["counts"]["N_total_effective"]
    mine = round(1 - (weights["hard"] * n_hard + weights["soft"] * n_soft
                      + weights["retrieval"] * n_retr) / n_eff, 4)
    pub = rd["counts"]
    print(f"[{inst}] 独立重算（{READING[inst]}，judge={iv['judge']}）："
          f"N_hard {n_hard} vs {pub['N_hard']}｜N_soft {n_soft} vs {pub['N_soft']}｜"
          f"N_retr {n_retr} vs {pub['N_retrieval']}｜CBI {mine} vs {rd['cbi']['measured']}")
    if (n_hard, n_soft, n_retr) != (pub["N_hard"], pub["N_soft"], pub["N_retrieval"]):
        fails.append(f"{inst} 泄漏计数与发布读数不等")
    if mine != rd["cbi"]["measured"]:
        fails.append(f"{inst} CBI 重算 {mine} ≠ 发布 {rd['cbi']['measured']}")
    if len(jd) != pub["judge_rows"] or len(rt) == 0:
        fails.append(f"{inst} 判分件行数 {len(jd)} ≠ 读数登记的 judge_rows {pub['judge_rows']}")
    for key, exp in (("judge_arm", iv["judge"]), ("answer_file", iv["answers"])):
        if rd.get(key) != exp:
            fails.append(f"{inst} 读数用的是 {rd.get(key)!r}，不是抽检单那一份 {exp!r}")
    print(f"    读数登记的判分臂/答案件与抽检单同源："
          f"judge_arm={rd.get('judge_arm')} answer_file={rd.get('answer_file')}")


def main() -> int:
    fails: list[str] = []
    check("v1", "spotcheck_sheet.json", "spotcheck_sheet.md", fails)
    check("v2", "spotcheck_sheet_v2.json", "spotcheck_sheet_v2.md", fails)
    for inst in ("v1", "v2"):
        lineage(inst, fails)
        rederive(inst, fails)
    print("\nRESULT:", "全部通过（界面未被截短、人工列干净、血缘接得上、读数能独立重算）"
          if not fails else "FAIL -> " + " | ".join(fails))
    return 1 if fails else 0


if __name__ == "__main__":
    raise SystemExit(main())
