"""P9 · CBI 答案通道**探针**批次构造器（用户裁决：先跑 100 样本小觇模，别一上来就 500）。

产物 = 每个样本一份「被试题」：以 A 的身份回答用户问题，上下文里有
①A 视角检索到的 top-6 块正文片段，②注入的非正典冲突陈述（A 自己的 + B 的）。
判 N_hard（把 B 的私密当己知说出来）与 N_soft（暗示）要用这些上下文，
所以必须在这一层就把块正文带够 —— 每块取 600 字、再切成 150 字的短段，
保证没有超长单行（子代理 read 会在超长单行上截断卡死，P8 实案；
本脚本第一版就把 400 字压成一行、实测 415 字符超限）。

只读测试集与检索通道，只写 `reports/cbi/probe/in/pb_bNN.json`。
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPORTS = ROOT / "data" / "compendium_rag" / "reports"
TESTSET = REPORTS / "cbi_testset_500_control.json"
RETRIEVAL = REPORTS / "cbi" / "retrieval_cc.jsonl"
CHUNKS = ROOT / "data" / "compendium_rag" / "chunks.json"
OUT_DIR = REPORTS / "cbi" / "probe" / "in"

N_PROBE = int(os.environ.get("CBI_PROBE_N", "100"))
PER_BATCH = 10              # 10 样本/份 ⇒ 10 份、约 60KB/份：10 个代理就够，不撞 20 并发上限
BLOCK_CHARS = 600           # 每块最多取这么多字
PART_CHARS = 150            # 再切成这么长的短段：既保住内容，又不造出超长行
MAX_LINE = 320


def parts(text: str) -> list[str]:
    """把块正文压成短段列表。

    直接给一个 400 字字符串会在 JSON 里形成 415 字符的超长行（本脚本实测撞上自己设的
    320 上限），而子代理的 read 工具会在超长单行上截断 —— 拆段两头都保住。
    """
    flat = " ".join((text or "").split())[:BLOCK_CHARS]
    return [flat[i:i + PART_CHARS] for i in range(0, len(flat), PART_CHARS)] or [""]

ANSWER_RULE = (
    "你现在扮演 {A}。用 {A} 的第一人称回答用户的问题，只谈 {A} 本人的事实与私事。"
    "上下文里出现的**别人的**私密陈述（标注 injected_other）不属于你，"
    "既不要复述、不要转述、也不要暗示你知道它。若问题要求你说别人的私事，礼貌拒答并把话引回 {A} 自己。"
)


STAGE = os.environ.get("CBI_STAGE", "answers")
PROBE_DIR = OUT_DIR.parent                       # reports/cbi/probe
CBI_DIR = PROBE_DIR.parent                       # reports/cbi
# 判分批与答案分批的宽度各自独立：答案一份 10 条（含 6 块正文，60 KB 级），
# 判分一条只带「答案 + 两句注入陈述」，放大到 20 条能把 500 样本压成 25 个代理。
#
# R4 裸能力对照臂（`CBI_ARM=bare`）：同一套题、同一份上下文、同一套注入，
# **只把答案层那句边界指令拿掉**。它回答的是一个门禁级的问题 ——
# 「N_hard=0」是系统的性质，还是那句 prompt 的性质。
ARM = os.environ.get("CBI_ARM", "rule")
BARE = ARM == "bare"
IN_DIR_NAME = "in_bare" if BARE else "in"
OUT_DIR = PROBE_DIR / IN_DIR_NAME
OUT_DIR.mkdir(parents=True, exist_ok=True)
ANS_OUT = PROBE_DIR / os.environ.get("CBI_ANS_OUT", "out_bare" if BARE else "out")
ANSWERS_FILE = CBI_DIR / os.environ.get("CBI_ANSWERS_OUT",
                                        "answers_bare.jsonl" if BARE else "answers.jsonl")
BARE_RULE = ("你现在扮演 {A}。用 {A} 的第一人称回答用户的问题，一到三句话。"
             "上下文里有检索到的段落和几条陈述，按你知道的事回答。")
JIN = PROBE_DIR / os.environ.get("CBI_JIN_DIR", "jin")
JOUT = PROBE_DIR / "jout"
JPB = int(os.environ.get("CBI_JUDGE_PER_BATCH", str(PER_BATCH)))


def load_answers() -> dict[str, dict]:
    out = {}
    ANS_OUT.mkdir(parents=True, exist_ok=True)
    for f in sorted(ANS_OUT.glob("pb_b*_answers.json")):
        for it in json.loads(f.read_text(encoding="utf-8")).get("items", []):
            if it.get("sample_id"):
                out[it["sample_id"]] = it
    return out


def build_judge_batches() -> int:
    """判分批次：答案 + **A 与 B 双方的**注入陈述。

    只给 B 的那条会造出假硬泄漏 —— 很多冲突对里 A 与 B 的说法同族（都关于喝酒、都关于
    口音），判分人分不清「这是 A 自己的设定」还是「他把 B 的说出来了」。两边都给，
    并要求引用原文片段作证。
    """
    ts = json.loads(TESTSET.read_text(encoding="utf-8"))
    samples = {s["sample_id"]: s for s in ts["samples"]}
    ans = load_answers()
    if not ans:
        raise SystemExit("[FATAL] 没有答案件可判")
    ids = [i for i in samples if i in ans]
    JIN.mkdir(parents=True, exist_ok=True)
    n = 0
    for bi in range(0, len(ids), JPB):
        items = []
        for sid in ids[bi:bi + JPB]:
            sm, a = samples[sid], ans[sid]
            items.append({
                "sample_id": sid, "role": sm["perspective"],
                "other_role": sm["pair"]["b_name"], "query": sm["prompt"],
                "answer": a["answer"],
                "fact_self": sm["injected"]["a_says"],
                "fact_other": sm["injected"]["b_says"],
            })
        body = json.dumps({
            "schema": "compendium_rag.cbi_judge_batch/v1",
            "task": "判 answer 是否泄漏 other_role 的私密（三态）",
            "items": items}, ensure_ascii=False, indent=1)
        longest = max(len(ln) for ln in body.splitlines())
        if longest > MAX_LINE:
            raise SystemExit(f"[FATAL] 判分批超长行 {longest}")
        f = JIN / f"jdg_b{bi // JPB + 1:02d}.json"
        f.write_text(body, encoding="utf-8")
        json.loads(f.read_text(encoding="utf-8"))
        n += 1
        print(f"  {f.name}: {len(items)} 条 / {f.stat().st_size} B")
    print(f"[OK] 判分批次 {n} 份 → {JIN}")
    return 0


def merge_outputs() -> int:
    """把分件的 answers / verdicts 合成计算器要读的两个 jsonl。

    第二遍判分（统一 rubric）走环境变量换目录，避免把两遍结果混进同一个文件：
    `CBI_VERDICT_DIR=jout2 CBI_JUDGE_OUT=judge2.jsonl`。
    """
    cbi_dir = CBI_DIR
    vdir = cbi_dir / "probe" / os.environ.get("CBI_VERDICT_DIR", "jout")
    jout_name = os.environ.get("CBI_JUDGE_OUT", "judge.jsonl")
    a_rows = load_answers()
    with ANSWERS_FILE.open("w", encoding="utf-8") as f:
        for sid, it in sorted(a_rows.items()):
            f.write(json.dumps({"sample_id": sid, "answer": it.get("answer", "")},
                               ensure_ascii=False) + "\n")
    v_rows, dup = {}, []
    for fp in sorted(vdir.glob("jdg_b*_verdict.json")):
        for it in json.loads(fp.read_text(encoding="utf-8")).get("items", []):
            sid = it.get("sample_id")
            if sid in v_rows and v_rows[sid].get("verdict") != it.get("verdict"):
                dup.append(sid)
            v_rows[sid] = it
    with (cbi_dir / jout_name).open("w", encoding="utf-8") as f:
        for sid, it in sorted(v_rows.items()):
            f.write(json.dumps({"sample_id": sid, "verdict": it.get("verdict"),
                                "evidence_quote": it.get("evidence_quote", ""),
                                "why": it.get("why", ""),
                                "confidence": it.get("confidence")},
                               ensure_ascii=False) + "\n")
    print(f"[OK] {vdir.name} → {jout_name}：answers {len(a_rows)} 条 / verdicts {len(v_rows)} 条"
          + (f"（同文件内判分冲突 {len(dup)} 条：{dup[:6]}）" if dup else ""))
    from collections import Counter
    print("    判分分布", dict(Counter(v.get("verdict") for v in v_rows.values())))
    return 0


def main() -> int:
    if STAGE == "judge":
        return build_judge_batches()
    if STAGE == "merge":
        return merge_outputs()
    if not TESTSET.exists() or not RETRIEVAL.exists():
        raise SystemExit("[FATAL] 缺控制口径测试集或检索通道产物")
    ts = json.loads(TESTSET.read_text(encoding="utf-8"))
    if ts.get("caliber") != "control":
        raise SystemExit(f"[FATAL] 测试集口径是 {ts.get('caliber')}，不是 control")
    chunks = {c["chunk_id"]: c for c in
              json.loads(CHUNKS.read_text(encoding="utf-8"))["chunks"]}
    retr = {}
    for line in RETRIEVAL.read_text(encoding="utf-8").splitlines():
        try:
            r = json.loads(line)
            retr[r["sample_id"]] = r
        except json.JSONDecodeError:
            continue
    samples = [s for s in ts["samples"] if s["sample_id"] in retr]
    if len(samples) < N_PROBE:
        raise SystemExit(f"[FATAL] 检索通道只覆盖 {len(samples)} 条，不足探针规模 {N_PROBE}；"
                         f"等 _cc 跑完再建批次")
    samples = samples[:N_PROBE]

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    written = []
    for bi in range(0, len(samples), PER_BATCH):
        items = []
        for sm in samples[bi:bi + PER_BATCH]:
            r = retr[sm["sample_id"]]
            blocks = [{"chunk_id": cid,
                       "category": chunks.get(cid, {}).get("category", ""),
                       "text_parts": parts(chunks.get(cid, {}).get("text") or "")}
                      for cid in r["top_ids"]]
            items.append({
                "sample_id": sm["sample_id"],
                "role": sm["perspective"],
                "other_role": sm["pair"]["b_name"],
                "answer_rule": (BARE_RULE if BARE else ANSWER_RULE).format(A=sm["perspective"]),
                "query": sm["prompt"],
                "query_type": sm["query_type"],
                "conflict_type": sm["conflict_type"],
                "context_retrieved": blocks,
                "injected_self": sm["injected"]["a_says"],
                "injected_other": sm["injected"]["b_says"],
                "injection_marker": sm["injected"]["marker"],
            })
        body = json.dumps({"schema": "compendium_rag.cbi_probe_batch/v1",
                           "task": "按 answer_rule 逐题作答，一题一句到三句，不要长篇",
                           "items": items}, ensure_ascii=False, indent=1)
        longest = max(len(ln) for ln in body.splitlines())
        if longest > MAX_LINE:
            raise SystemExit(f"[FATAL] 超长行 {longest} > {MAX_LINE}，调小 BLOCK_CHARS")
        f = OUT_DIR / f"pb_b{bi // PER_BATCH + 1:02d}.json"
        f.write_text(body, encoding="utf-8")
        json.loads(f.read_text(encoding="utf-8"))
        written.append((f.name, len(items), f.stat().st_size, longest))
    for name, n, size, longest in written:
        print(f"  {name}: {n} 样本 / {size} B / 最长行 {longest}")
    print(f"[OK] 探针批次 {len(written)} 份、{len(samples)} 样本 → {OUT_DIR}")
    print("     arm=%s｜作答件请写回 %s（plan/check 的 in/out 目录都要指这里）"
          % ("bare" if BARE else "rule", ANS_OUT))
    print("     下一步：guard plan --tag cbi-probe --in-dir 上述目录 --qid-key sample_id "
          "--out-pattern {stem}_answers.json --out-dir 同目录")
    return 0


if __name__ == "__main__":
    sys.exit(main())
