# -*- coding: utf-8 -*-
"""适用域脚本的负向测试：那两个 0 必须是**量出来的**，不是"根本没在读"。

按量具自守规则（消歧规则表 §6.5 / §6.7 / 第 8 条）：
  · 报"注入整句在语料逐字出现 = 0"的检查，必须有一例**能把它变成非零**的破坏，
    否则它可能只是路径写错、字段名读空、或者滑窗根本没跑（恒 0 比报错更危险）；
  · 反过来，往语料里加**无关文本**不该让它红，否则这检查是恒红、同样不能采信；
  · `chunks.json` 缺失/为空时必须**拒绝出表**，不许把"没读到"印成"一条都没有"。
所有破坏只打在系统临时目录的副本上；仓库原件与图 sha 前后必须一致。
共 19 条断言 = 6 条对照（含『滑窗真的在跑』『通道行 500/500/500』两条反空转）
+ 5 类破坏（塞入注入整句 / 塞无关文本必须不红 / 塞进该题 top-6 那块 / 语料读空 /
改正文 §2.15 一个数）+ 收尾原件副本再全绿。

用法：`PYTHONIOENCODING=utf-8 .venv/Scripts/python.exe scripts/cbi_faithfulness_applicability_negtest.py`
"""
from __future__ import annotations

import hashlib
import importlib.util
import json
import shutil
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
R = ROOT / "data" / "compendium_rag"
for _stream in (sys.stdout, sys.stderr):
    if hasattr(_stream, "reconfigure"):
        _stream.reconfigure(errors="replace")

N = 0
FAILS = []


def ck(name, got, want):
    global N
    N += 1
    if got != want:
        FAILS.append(name)
        print(f"  [FAIL] {name}: got={got!r} want={want!r}")
    else:
        print(f"  [ok]   {name} = {got!r}")


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()[:16]


def sandbox(tmp: Path):
    shutil.copytree(R / "reports", tmp / "reports")
    shutil.copy(R / "chunks.json", tmp / "chunks.json")
    spec = importlib.util.spec_from_file_location(
        "fa", ROOT / "scripts" / "cbi_faithfulness_applicability.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    m.R = tmp
    m.REPORTS = tmp / "reports"
    m.CBI = tmp / "reports" / "cbi"
    m.OUT_JSON = tmp / "out.json"
    m.OUT_MD = tmp / "out.md"
    shutil.copy(ROOT / "docs" / "compendium-rag" / "P9_CBI报告.md", tmp / "report.md")
    m.DOC = tmp / "report.md"
    return m


def main() -> int:
    watched = [R / "chunks.json", R / "reports" / "cbi_testset_500_control.json",
               R / "graph.json"]
    before = {p: sha(p) for p in watched}

    tmp = Path(tempfile.mkdtemp(prefix="fa_base_"))
    m = sandbox(tmp)
    rc = m.main()
    print("[C] 原件副本 ⇒ 必须全绿并出表")
    ck("control rc", rc, 0)
    res = json.loads(m.OUT_JSON.read_text(encoding="utf-8"))
    ck("三套读数都算了", len(res), 3)
    ck("逐字命中全是 0（这就是第 1 层要报的数）",
       sum(sum(x["verbatim_in_corpus"].values()) + x["verbatim_in_top6"] for x in res), 0)
    ck("10 字窗口确实在跑（重叠例子 >0，否则滑窗可能根本没执行）",
       sum(x["n_overlap_examples"] for x in res) > 0, True)
    ck("语料不是空的（空表会把一切伪装成 0）", res[0]["n_chunks"] > 1000, True)
    ck("top-6 通道行对齐了（channel_rows 必须非零，否则第 3 层的 0 是没数据的 0）",
       [x["channel_rows"] for x in res], [500, 500, 500])

    print("[N1] 往语料里塞进一条**真的注入整句** ⇒ 逐字命中必须非零、脚本必须判红")
    t1 = Path(tempfile.mkdtemp(prefix="fa_n1_"))
    m1 = sandbox(t1)
    ts = json.loads((m1.REPORTS / "cbi_testset_500_control.json").read_text(encoding="utf-8"))
    fact = ts["samples"][3]["injected"]["b_says"]
    ck("被塞的是一句正常长度的注入", len(fact) > 10, True)
    ck("这句原本在语料里逐字不存在",
       fact in "".join(m1.load_chunks().values()), False)
    cp = t1 / "chunks.json"
    d = json.loads(cp.read_text(encoding="utf-8"))
    d["chunks"][0]["text"] = d["chunks"][0]["text"] + "\n" + fact
    cp.write_text(json.dumps(d, ensure_ascii=False), encoding="utf-8")
    ck("rc 必须为 1", m1.main(), 1)
    ck("不出表（宁缺毋假）", (t1 / "out.json").exists(), False)

    print("[N2] 往语料里塞进一句**与任何注入无关**的话 ⇒ 不该红（防恒红）")
    t2 = Path(tempfile.mkdtemp(prefix="fa_n2_"))
    m2 = sandbox(t2)
    cp = t2 / "chunks.json"
    d = json.loads(cp.read_text(encoding="utf-8"))
    d["chunks"][0]["text"] = d["chunks"][0]["text"] + "\n今天天气不错，食堂供应红烧茄子。"
    cp.write_text(json.dumps(d, ensure_ascii=False), encoding="utf-8")
    ck("rc 必须为 0", m2.main(), 0)

    print("[N3] 把注入句塞进**该题 top-6 的那一块**（不进全语料检索不到的位置）"
          " ⇒ 第 3 层必须抓到，且第 1 层也得同步非零")
    t3 = Path(tempfile.mkdtemp(prefix="fa_n3_"))
    m3 = sandbox(t3)
    ts = json.loads((m3.REPORTS / "cbi_testset_500_control.json").read_text(encoding="utf-8"))
    s = ts["samples"][7]
    rows = {}
    rp = m3.CBI / "retrieval_cc.jsonl"
    for ln in rp.read_text(encoding="utf-8").splitlines():
        if ln.strip():
            r = json.loads(ln)
            rows[r["sample_id"]] = r
    first_top = rows[s["sample_id"]]["top_ids"][0]
    cp = t3 / "chunks.json"
    d = json.loads(cp.read_text(encoding="utf-8"))
    for c in d["chunks"]:
        if c["chunk_id"] == first_top:
            c["text"] += "\n" + s["injected"]["a_says"]
    cp.write_text(json.dumps(d, ensure_ascii=False), encoding="utf-8")
    ck("rc 必须为 1", m3.main(), 1)

    print("[N4] 语料读空 ⇒ 必须拒绝出表，不许把『没读到』印成『一条都没有』")
    t4 = Path(tempfile.mkdtemp(prefix="fa_n4_"))
    m4 = sandbox(t4)
    cp = t4 / "chunks.json"
    d = json.loads(cp.read_text(encoding="utf-8"))
    d["chunks"] = []
    cp.write_text(json.dumps(d, ensure_ascii=False), encoding="utf-8")
    ck("rc 必须为 1", m4.main(), 1)
    ck("不出表", (t4 / "out.json").exists(), False)

    print("[N5] 报告 §2.15 的表被改一个数 ⇒ `doc_check` 必须逐格点出；未改副本必须零告")
    res_now = json.loads(m.OUT_JSON.read_text(encoding="utf-8"))
    ck("未改的正文副本 ⇒ 零告", m.doc_check(res_now), [])
    t5 = Path(tempfile.mkdtemp(prefix="fa_n5_"))
    m5 = sandbox(t5)
    bad_doc = m5.DOC
    orig = bad_doc.read_text(encoding="utf-8")
    bad_doc.write_text(orig.replace("| 500 | 0 / 0 | 500 / 495 | 5 | 0 |",
                                    "| 500 | 0 / 0 | 500 / 494 | 5 | 0 |", 1),
                       encoding="utf-8")
    got = m5.doc_check(res_now)
    ck("改了一个数必须报", len(got) >= 1, True)
    ck("报的正是被改的那一列（按列名报，不按格子序号）",
       any("v1 × 控制 的「10 字窗口零重叠」列" in g for g in got), True)

    print("[C2] 原件副本再跑一次 ⇒ 必须重新全绿")
    t5 = Path(tempfile.mkdtemp(prefix="fa_base2_"))
    ck("control-again rc", sandbox(t5).main(), 0)

    changed = [str(p) for p, h in before.items() if sha(p) != h]
    ck("仓库语料/测试集/图一个字节都没动", changed, [])

    print(f"\n[结果] 断言 {N} 条，失败 {len(FAILS)} 条")
    return 1 if FAILS else 0


if __name__ == "__main__":
    raise SystemExit(main())
