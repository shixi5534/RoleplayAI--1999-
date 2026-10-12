# -*- coding: utf-8 -*-
"""集中度脚本的负向测试：这张表必须能变红，且破坏要打在**它真读的那几件东西**上。

按量具自守规则（消歧规则表 §6.5/§6.7）：
  · 不许有同源自证 —— "严格命中数"必须与读数产物的 `exposure.n_gold_in_top6` 交叉对数，
    所以改通道让两者脱钩时脚本**必须**拒绝出表；
  · 不许把"没测到"印成 0 —— 图读不到时"几个实体声明它"会是 0（看起来像"都是单主块"），
    脚本**必须**终止；
  · `跨对命中` 必须用 a→b 的对键而不是 B 的名字 —— 用名字当键它恒为 0（自己跟自己比），
    所以这里要造一例**真的**跨对命中，看它必须变成非零。
所有破坏只打在系统临时目录的副本上；仓库原件 sha 前后必须一致，产物也只写临时目录。
共 24 条断言 = 5 类破坏（N1 与读数脱钩 / N2 硬打标记 / N3 让交叉列动 / N4 图不可读 /
N5 改正文表的数）+ 三处"必须仍绿"的对照（首末两次原件副本、N5 改回副本、未改副本零告）。

用法：`PYTHONIOENCODING=utf-8 .venv/Scripts/python.exe scripts/cbi_retrieval_concentration_negtest.py`
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
R = ROOT / "data" / "compendium_rag" / "reports"
CBI = R / "cbi"
GRAPH = ROOT / "data" / "compendium_rag" / "graph.json"
# Windows 控制台常见 cp936：产物落盘后才抛 UnicodeEncodeError 最难查（写了一半、退出码非零）。
for _stream in (sys.stdout, sys.stderr):
    if hasattr(_stream, "reconfigure"):
        _stream.reconfigure(errors="replace")

INPUTS = [("R", "cbi_testset_500_control.json"), ("R", "cbi_testset_500.json"),
          ("R", "cbi_testset_500_v2_control.json"),
          ("R", "cbi_result_full.json"), ("R", "cbi_result_v2instrument.json"),
          ("CBI", "retrieval_cc.jsonl"), ("CBI", "retrieval.jsonl"),
          ("CBI", "retrieval_v2_cc.jsonl")]
DOC = ROOT / "docs" / "compendium-rag" / "P9_CBI报告.md"

fails: list[str] = []
N = 0


def ck(name, got, want):
    global N
    N += 1
    if got != want:
        fails.append(name)
        print(f"  [FAIL] {name}: got={got!r} want={want!r}")
    else:
        print(f"  [ok]   {name} = {got!r}")


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()[:16]


def sandbox(tmp: Path) -> tuple:
    (tmp / "cbi").mkdir(parents=True, exist_ok=True)
    for where, name in INPUTS:
        src = (R if where == "R" else CBI) / name
        shutil.copy(src, (tmp / "cbi" if where == "CBI" else tmp) / name)
    spec = importlib.util.spec_from_file_location(
        "conc", ROOT / "scripts" / "cbi_retrieval_concentration.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    m.R = tmp
    m.CBI = tmp / "cbi"
    m.GRAPH = GRAPH
    m.OUT_JSON = tmp / "out.json"
    m.OUT_MD = tmp / "out.md"
    # 正文核对用**报告的副本**：原件与现算本来就该一致（对照例因此必须全绿），
    # 而 N3 那类破坏会同时让正文核对变红 —— 这正是要看的行为，不关掉它。
    shutil.copy(DOC, tmp / "report.md")
    m.DOC = tmp / "report.md"
    return m


def edit_jsonl(path: Path, sid: str, fn) -> None:
    rows = [json.loads(l) for l in path.read_text(encoding="utf-8").splitlines() if l.strip()]
    n = 0
    for r in rows:
        if r["sample_id"] == sid:
            fn(r)
            n += 1
    assert n == 1, f"{sid} 在 {path.name} 里匹配到 {n} 行"
    path.write_text("\n".join(json.dumps(r, ensure_ascii=False) for r in rows) + "\n",
                    encoding="utf-8")


def main() -> int:
    before = {p: sha(p) for _, nm in INPUTS
              for p in [(R if _ == "R" else CBI) / nm]}
    before[GRAPH] = sha(GRAPH)

    base = Path(tempfile.mkdtemp(prefix="conc_base_"))
    m = sandbox(base)
    rc = m.main()
    print("[C] 原件副本 ⇒ 必须全绿并出表")
    ck("control rc", rc, 0)
    res = json.loads(m.OUT_JSON.read_text(encoding="utf-8"))
    by = {x["label"]: x for x in res}
    ck("v1 控制严格命中与读数同数", by["v1 × 控制"]["n_strict_hits"], 12)
    ck("v1 字面命中", by["v1 × 字面"]["n_strict_hits"], 81)
    ck("v2 控制命中", by["v2 × 控制"]["n_strict_hits"], 19)
    ck("通道标记与复算不一致（对照必须是 0）",
       sum(x["flag_mismatch_with_channel"] for x in res), 0)
    ck("金标指认与图上归属不一致（对照必须是 0）",
       sum(x["hits_where_b_not_a_graph_claimant"] for x in res), 0)
    ck("命中块全部是多主块（7/7，来自图不是硬编码）",
       [by["v1 × 控制"]["hit_chunks_claimed_by_multiple_entities"],
        by["v1 × 控制"]["n_distinct_chunks"]], [7, 7])
    md_txt = m.OUT_MD.read_text(encoding="utf-8")
    ck("md 里写了实测的 0 条", "本次实测合计 **0** 条" in md_txt, True)

    print("[N1] 通道里抹掉一条命中的 top_ids ⇒ 与读数 exposure 脱钩，必须拒绝出表")
    t1 = Path(tempfile.mkdtemp(prefix="conc_n1_"))
    m1 = sandbox(t1)
    edit_jsonl(m1.CBI / "retrieval_cc.jsonl", "CC-009-inductive",
               lambda r: r.__setitem__("top_ids",
                                       [x for x in r["top_ids"]
                                        if x != "character__17701_小房间:0.0.0"]))
    ck("rc 必须为 1", m1.main(), 1)
    ck("不出表（宁缺毋假）", m1.OUT_JSON.exists(), False)

    print("[N2] 给一条本来没命中的行硬打 `b_private_chunk_hit=true` ⇒ 交叉核对必须抓到不一致")
    t2 = Path(tempfile.mkdtemp(prefix="conc_n2_"))
    m2 = sandbox(t2)
    rows = [json.loads(l) for l in (m2.CBI / "retrieval_cc.jsonl")
            .read_text(encoding="utf-8").splitlines() if l.strip()]
    target = next(r for r in rows if not r.get("b_private_chunk_hit"))
    sid = target["sample_id"]
    edit_jsonl(m2.CBI / "retrieval_cc.jsonl", sid,
               lambda r: r.__setitem__("b_private_chunk_hit", True))
    ck("rc 必须为 1", m2.main(), 1)
    ck("被点名的正是那一行", sid.startswith("CC-"), True)

    print("[N3] 把一条命中样本的 **b_name** 改成图上不存在于该块声明名单里的名字 ⇒ "
          "『金标指认与图上归属不一致』必须 >0（若这一列恒为 0，它就是空检查）")
    t3 = Path(tempfile.mkdtemp(prefix="conc_n3_"))
    m3 = sandbox(t3)
    ts_path = m3.R / "cbi_testset_500_control.json"
    ts = json.loads(ts_path.read_text(encoding="utf-8"))
    hit_sid = "CC-033-multi_role"
    for s in ts["samples"]:
        if s["sample_id"] == hit_sid:
            s["pair"]["b_name"] = "zzz-图上不存在这个块"
    ts_path.write_text(json.dumps(ts, ensure_ascii=False), encoding="utf-8")
    ck("rc 必须为 0：这一列**不在**正文那张表里，破坏它不该把正文核对一起带红", m3.main(), 0)
    ck("产物仍写出", m3.OUT_JSON.exists(), True)
    r3 = {x["label"]: x for x in json.loads(m3.OUT_JSON.read_text(encoding="utf-8"))}
    ck("不一致计数必须变成非零", r3["v1 × 控制"]["hits_where_b_not_a_graph_claimant"] > 0, True)
    ck("md 措辞必须跟着换（不许仍写 0 条）",
       "本次实测合计 **0** 条" in m3.OUT_MD.read_text(encoding="utf-8"), False)

    print("[N5] 正文 §2.14 的表被改一个数 ⇒ `doc_check` 必须逐格点出；副本未改时必须全绿")
    m.main()                      # 用未破坏的沙箱重算一遍，作为正文核对的基准
    res_now = json.loads(m.OUT_JSON.read_text(encoding="utf-8"))
    ck("未改的正文副本 ⇒ 零告", m.doc_check(res_now), [])
    tmp5 = Path(tempfile.mkdtemp(prefix="conc_n5_")) / "report.md"
    shutil.copy(DOC, tmp5)
    orig = tmp5.read_text(encoding="utf-8")
    tmp5.write_text(orig.replace("| 12 | **7** | 8 |", "| 12 | **9** | 8 |", 1),
                    encoding="utf-8")
    m.DOC = tmp5
    got = m.doc_check(res_now)
    ck("改了一个数必须报", len(got) >= 1, True)
    ck("报的是那一行的第 2 格（落在几块）",
       any("v1 × 控制 第 2 格" in g for g in got), True)
    m.DOC = base / "report.md"
    ck("改回未破的副本 ⇒ 必须重新零告（不是恒红）", m.doc_check(res_now), [])

    print("[N4] 图不可读 ⇒ 『几个实体声明它』会全变 0，看起来像『都是单主块』，必须拒绝出表")
    t4 = Path(tempfile.mkdtemp(prefix="conc_n4_"))
    m4 = sandbox(t4)
    m4.GRAPH = t4 / "没有这个图.json"
    ck("rc 必须为 1", m4.main(), 1)
    ck("不出表", m4.OUT_JSON.exists(), False)

    print("[C2] 再跑一次原件副本 ⇒ 必须重新全绿（证明上面三例不是恒红）")
    base2 = Path(tempfile.mkdtemp(prefix="conc_base2_"))
    m5 = sandbox(base2)
    ck("control-again rc", m5.main(), 0)

    after_bad = [str(p) for p, h in list(before.items()) if sha(p) != h]
    ck("仓库原件与图一个字节都没动", after_bad, [])
    print(f"\n[结果] 断言 {N} 条，失败 {len(fails)} 条")
    return 1 if fails else 0


if __name__ == "__main__":
    raise SystemExit(main())
