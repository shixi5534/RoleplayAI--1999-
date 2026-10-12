# -*- coding: utf-8 -*-
"""Faithfulness 那一格的**适用域**：CBI 这套题能不能给它定义域？（只读实算）

背景：`Faithfulness >= 0.98 不回退` 与 `MRR >= 0.39 不回退` 两条我一直只从 r11 审计读数，
MRR 那条已经在报告 §2.13 把适用域钉死了，Faithfulness 这条还没被问过同一个问题。
这里问的是：**审计版 faithfulness 要的是"答案有没有语料支撑"，
而 CBI 集的对抗性事实按纪律必须"只进上下文、不写图"** ⇒ 被注入的那些句子在语料里
应当是**找不到支撑的**（找到了反而是注入泄漏到图/缓存里，那是要报的事故）。
所以把 CBI 答案送去算 faithfulness，量的会是"对抗设计本身"，不是幻觉。

三件事分开量（全部只读）：
  1) `injected.a_says` / `injected.b_says` **整句**在 3695 块全文里逐字出现的条数（期望 0）；
  2) 同上的 **10 字滑窗**版本：只要有一个 10 字窗口落在语料里就算"有重叠"，
     并把重叠片段列出来 —— 逐字 0 不代表内容无关（人名、canon 片段都会重叠），
     这一层是用来**防止把第 1 层读成"注入完全外在于语料"**；
  3) 每题 top-6 检索块的拼接文本里是否含任一注入整句（期望 0 ⇒ 检索通道没把注入带回图侧）。

产物：`reports/cbi/faithfulness_applicability.{json,md}`。
用法：`PYTHONIOENCODING=utf-8 .venv/Scripts/python.exe scripts/cbi_faithfulness_applicability.py`
"""
from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path

for _stream in (sys.stdout, sys.stderr):
    if hasattr(_stream, "reconfigure"):
        _stream.reconfigure(errors="replace")

ROOT = Path(__file__).resolve().parents[1]
R = ROOT / "data" / "compendium_rag"
REPORTS = R / "reports"
CBI = REPORTS / "cbi"
OUT_JSON = CBI / "faithfulness_applicability.json"
OUT_MD = CBI / "faithfulness_applicability.md"
K = 10

CASES = [
    ("v1 × 控制", REPORTS / "cbi_testset_500_control.json", CBI / "retrieval_cc.jsonl"),
    ("v1 × 字面", REPORTS / "cbi_testset_500.json", CBI / "retrieval.jsonl"),
    ("v2 × 控制", REPORTS / "cbi_testset_500_v2_control.json", CBI / "retrieval_v2_cc.jsonl"),
]


def load_chunks() -> dict:
    ck = json.loads((R / "chunks.json").read_text(encoding="utf-8"))["chunks"]
    return {c["chunk_id"]: c.get("text") or "" for c in ck}


def analyse(label: str, ts_path: Path, retr_path: Path, chunks: dict) -> dict:
    ts = json.loads(ts_path.read_text(encoding="utf-8"))
    samples = ts["samples"]
    whole = "".join(chunks.values())
    top = {}
    if retr_path.exists():
        for ln in retr_path.read_text(encoding="utf-8").splitlines():
            if ln.strip():
                r = json.loads(ln)
                top[r["sample_id"]] = r.get("top_ids") or []
    verbatim = Counter()
    overlap = Counter()
    spans = []
    in_top = 0
    for s in samples:
        inj = s.get("injected") or {}
        ctx = "".join(chunks.get(x, "") for x in top.get(s["sample_id"], []))
        for fld in ("a_says", "b_says"):
            f = (inj.get(fld) or "").strip()
            if not f:
                continue
            verbatim[fld] += 1 if f in whole else 0
            grams = [f[i:i + K] for i in range(max(1, len(f) - K + 1)) if f[i:i + K] in whole]
            overlap[fld if not grams else fld + "_overlap"] += 1
            if grams:
                spans.append({"sample_id": s["sample_id"], "field": fld,
                              "fact": f, "matched_spans": grams[:3]})
            if f in ctx:
                in_top += 1
    n = len(samples)
    return {
        "label": label, "testset": ts_path.name, "channel": retr_path.name,
        "n_samples": n, "n_chunks": len(chunks), "corpus_chars": len(whole),
        "verbatim_in_corpus": dict(verbatim),
        "no10gram_overlap": dict(overlap),
        "overlap_examples": spans[:12],
        "n_overlap_examples": len(spans),
        "verbatim_in_top6": in_top,
        "channel_rows": len(top),
    }


def md(res: list, chunks_missing: bool) -> str:
    L = ["# Faithfulness 那一格的适用域（只读实算，10-12）", "",
         f"语料：`chunks.json` {res[0]['n_chunks'] if res else '—'} 块 / "
         f"{res[0]['corpus_chars'] if res else 0:,} 字符。"
         "注入纪律是「私密只进上下文、不写图」，所以下面两个 0 是**设计要求的**，不是运气。", ""]
    if chunks_missing:
        L += ["> ⚠ `chunks.json` 读不到 ⇒ 本表所有计数无从可算，见脚本退出码。", ""]
    L += ["| 读数 | 样本 | 注入整句在语料逐字出现（a/b） | 10 字窗口**零重叠**（a/b） | "
          "有重叠的条数 | 注入整句出现在 top-6 上下文 |",
          "| --- | --- | --- | --- | --- | --- |"]
    for x in res:
        v, o = x["verbatim_in_corpus"], x["no10gram_overlap"]
        L.append(f"| {x['label']} | {x['n_samples']} | {v.get('a_says', 0)}/{v.get('b_says', 0)} | "
                 f"{o.get('a_says', 0)}/{o.get('b_says', 0)} | {x['n_overlap_examples']} | "
                 f"{x['verbatim_in_top6']} |")
    for x in res:
        if not x["overlap_examples"]:
            continue
        L += ["", f"## {x['label']}：有重叠的那几条（片段逐字列出）", ""]
        for s in x["overlap_examples"]:
            L.append(f"- `{s['sample_id']}` {s['field']}：片段 {' / '.join(s['matched_spans'])}"
                     f" ｜ 整句：{s['fact'][:60]}")
    L += ["", "> **结论（这一格为什么不能由 CBI 集出数）**：审计版 faithfulness 问的是"
          "「答案里的断言有没有语料支撑」。本集里被注入的私密按纪律**只存在于 prompt**，"
          "整句在 3695 块里逐字出现 **0** 条、在每题 top-6 拼接文本里也是 **0** 条 ⇒ "
          "把 CBI 答案送去算 faithfulness，量到的是「对抗设计本身」而不是幻觉；"
          "而守住了边界的回答（`N_hard=0`）恰恰因为**什么都没说**才会显得『高支撑』。"
          "所以 `Faithfulness>=0.98 不回退` 与 MRR 同构：**只能在 r11 审计的三套题上读**，"
          "支撑它的是三个输入指纹未变（图 / 块 / src 摘要），不是这 500 条。",
          "> **10 字窗口那一层的用途**：防止把上面那个 0 误读成『注入完全外在于语料』。"
          "B 侧确实有少数条与语料有 10 字重叠，看片段就知道是**角色全名**（v1）或"
          "**canon 原文片段**（v2 的注入是按 R5bis 要求逐对撰写、取材于该角色自己的 anecdote），"
          "不是『这条私密已在图里』。这一列同时也就是一次注入泄漏体检："
          "若哪天注入句子真的整句进了语料/缓存，第 1 列会立刻非零。"]
    return "\n".join(L) + "\n"


DOC = ROOT / "docs" / "compendium-rag" / "P9_CBI报告.md"


def doc_check(res: list) -> list:
    """报告 §2.15 那张表是正文里的数字，必须有资格变红（§5-28 同一条纪律）：
    逐格回到本次实算比一遍。第一行写全数、后续行允许『**0** / **0**』这种同形写法，
    所以比的是单元格字符串本身，不做语义猜测。"""
    bad = []
    if not DOC.exists():
        return [f"报告不存在（{DOC.name}）⇒ §2.15 无从核对"]
    sec = DOC.read_text(encoding="utf-8").split("### 2.15", 1)[-1].split("\n## ", 1)[0]
    if "### 2.15" not in DOC.read_text(encoding="utf-8"):
        return ["报告里没有 §2.15"]
    for x in res:
        line = next((ln for ln in sec.splitlines()
                     if ln.startswith("|") and x["label"] in ln), "")
        if not line:
            bad.append(f"§2.15 找不到 {x['label']} 那一行")
            continue
        v, o = x["verbatim_in_corpus"], x["no10gram_overlap"]
        want = [f"{v.get('a_says', 0)} / {v.get('b_says', 0)}",
                f"{o.get('a_says', 0)} / {o.get('b_says', 0)}",
                str(x["n_overlap_examples"]), str(x["verbatim_in_top6"])]
        c = [s.strip().replace("*", "") for s in line.strip("|").split("|")]
        got = c[2:6]
        cols = ["注入整句在语料逐字出现", "10 字窗口零重叠", "有重叠的条数", "top-6 含注入整句"]
        for j, (g, w) in enumerate(zip(got, want)):
            if g != w:
                bad.append(f"§2.15 {x['label']} 的「{cols[j]}」列正文={g!r} 现算={w!r}")
        print(f"[§2.15 核对] {x['label']}：{got == want}")
    n_overlap = sum(x["n_overlap_examples"] for x in res)
    if "同一对的 5 个题位" in sec and n_overlap not in (5, 10, 15):
        bad.append(f"正文把重叠条数解释成『同一对的 5 个题位』，但三套合计是 {n_overlap}")
    return bad


def main() -> int:
    chunks = load_chunks()
    if not chunks:
        print("[FAIL] chunks.json 里一个块都没有 ⇒ 适用域无从可算，不出表")
        return 1
    res = [analyse(l, p, q, chunks) for l, p, q in CASES if p.exists()]
    problems = []
    for x in res:
        v = x["verbatim_in_corpus"]
        print(f"[{x['label']}] 注入整句在语料逐字出现 a={v.get('a_says', 0)} b={v.get('b_says', 0)}"
              f"（样本 {x['n_samples']}）| 10 字零重叠 a={x['no10gram_overlap'].get('a_says', 0)} "
              f"b={x['no10gram_overlap'].get('b_says', 0)} | top-6 内含注入句 {x['verbatim_in_top6']} 条")
        if v.get("a_says", 0) or v.get("b_says", 0):
            problems.append(f"{x['label']}：注入整句出现在语料里 —— 那是注入泄漏，不是适用域问题")
        if x["verbatim_in_top6"]:
            problems.append(f"{x['label']}：top-6 上下文里出现注入整句")
    if problems:
        print("\n[FAIL] " + "\n[FAIL] ".join(problems))
        return 1
    OUT_JSON.write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding="utf-8")
    OUT_MD.write_text(md(res, False), encoding="utf-8")
    print(f"\n[OK] 写出 {OUT_JSON.name} / {OUT_MD.name}（{len(res)} 个读数）")
    bad = doc_check(res)
    if bad:
        print("[FAIL] 报告 §2.15 与本脚本现算不一致：")
        for b in bad:
            print("   !! " + b)
        return 1
    print("[OK] 报告 §2.15 的每个数都回到本脚本的现算值")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
