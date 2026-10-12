"""`cbi_sheet_integrity.py` 的负向测试：血缘检查与独立重算检查**必须能变红**。
所有破坏都在系统临时目录的**副本**上做，仓库原件一个字节都不动。

这一轮负向测试自己产出两条发现（不是我事先想到的）：
  A) 头两版破坏打在 `judge_full/judge_v2_r1` 的第 0 行与测试集 samples[7] 上，结果"抓不到"——
     查下去是**那两条样本不在 53 行抽检单里**，血缘检查按设计只覆盖抽到的行。
     所以这里把边界测出来了写成断言：抽检单覆盖的行 ⇒ 血缘抓；不覆盖的行 ⇒ 血缘放过、
     由独立重算的**全 500 条计数**抓（N2 / N2b 成对出现）。
  B) 权重那例必须打在 **v1** 上：v2 那一列 N_hard=0 且 N_soft=0，改 1.0/0.5 两个权重
     **读数纹丝不动** ⇒ 在 v2 上"权重被调"这件事不可证伪，只能靠还有非零项的 v1 那列来守。

用法：`PYTHONIOENCODING=utf-8 .venv/Scripts/python.exe scripts/cbi_sheet_integrity_negtest.py`
"""
import importlib.util
import json
import re
import shutil
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
spec = importlib.util.spec_from_file_location("csi", ROOT / "scripts" / "cbi_sheet_integrity.py")
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

SRC_R = ROOT / "data/compendium_rag/reports"
SRC_C = SRC_R / "cbi"
SET = {
    "v2": {"top": ["cbi_testset_500_v2_control.json", "cbi_result_v2instrument.json"],
           "cbi": ["spotcheck_sheet_v2.json", "spotcheck_sheet_v2.md",
                   "spotcheck_sheet_v2_cards.md", "answers_v2.jsonl", "judge_v2_r1.jsonl",
                   "retrieval_v2_cc.jsonl"],
           "read": "cbi_result_v2instrument.json", "sheet": "spotcheck_sheet_v2.json",
           "md": "spotcheck_sheet_v2.md", "judge": "judge_v2_r1.jsonl"},
    "v1": {"top": ["cbi_testset_500_control.json", "cbi_result_full.json"],
           "cbi": ["spotcheck_sheet.json", "spotcheck_sheet.md", "spotcheck_sheet_cards.md",
                   "answers.jsonl", "judge_full.jsonl", "retrieval_cc.jsonl"],
           "read": "cbi_result_full.json", "sheet": "spotcheck_sheet.json",
           "md": "spotcheck_sheet.md", "judge": "judge_full.jsonl"},
}
fails = []


def fresh(tmp, inst):
    s = SET[inst]
    r, c = tmp / "reports", tmp / "reports/cbi"
    if r.exists():
        shutil.rmtree(r)
    c.mkdir(parents=True)
    for f in s["top"]:
        shutil.copyfile(SRC_R / f, r / f)
    for f in s["cbi"]:
        shutil.copyfile(SRC_C / f, c / f)
    m.REPORTS, m.CBI = r, c
    return r, c


def patch_json(p, mutate):
    d = json.loads(p.read_text(encoding="utf-8"))
    mutate(d)
    p.write_text(json.dumps(d, ensure_ascii=False), encoding="utf-8")


def flip_verdict(jp, sid):
    ln = jp.read_text(encoding="utf-8").splitlines()
    for i, s in enumerate(ln):
        row = json.loads(s)
        if row["sample_id"] == sid:
            row["verdict"] = "hard_leak" if row["verdict"] != "hard_leak" else "clean"
            ln[i] = json.dumps(row, ensure_ascii=False)
            break
    jp.write_text("\n".join(ln) + "\n", encoding="utf-8")


def expect_fail(name, fn, needle):
    fs = []
    fn(fs)
    hit = bool(fs) and any(needle in x for x in fs)
    print(("  ok   " if hit else "  FAIL ") + f"{name} -> {fs[:1]}")
    if not hit:
        fails.append(name)


with tempfile.TemporaryDirectory(prefix="cbi_integ_") as t:
    tmp = Path(t)
    print("[C] 原件（v1 与 v2）：血缘与重算都必须全绿，否则这检查恒红、不能采信")
    for inst in ("v1", "v2"):
        fresh(tmp, inst)
        fs = []
        m.lineage(inst, fs)
        m.rederive(inst, fs)
        m.cards(inst, fs)
        print(("  ok   " if not fs else "  FAIL ") + f"control {inst} -> {fs[:2]}")
        if fs:
            fails.append("control-" + inst)

    print("[N1] 改一行「被试答案」（界面与原始件分家）⇒ 血缘必须抓到")
    r, c = fresh(tmp, "v2")

    def cut_answer(d):
        row = d["rows"][3]
        row["answer"] = row["answer"][:-8]

    patch_json(c / SET["v2"]["sheet"], cut_answer)
    expect_fail("答案被改", lambda fs: m.lineage("v2", fs), "血缘断裂")

    print("[N2] 翻一条**在抽检单上的** verdict ⇒ 血缘必须抓到（machine_verdict 不再同源）")
    r, c = fresh(tmp, "v2")
    sheet_sid = json.loads((c / SET["v2"]["sheet"]).read_text(encoding="utf-8"))["rows"][2]["sample_id"]
    flip_verdict(c / SET["v2"]["judge"], sheet_sid)
    expect_fail("抽检单覆盖的行被改", lambda fs: m.lineage("v2", fs), "血缘断裂")

    print("[N2b] 翻一条**不在抽检单上的** verdict ⇒ 血缘**抓不到**（它只管 53 行），"
          "但独立重算的计数必须抓到 —— 这两条检查是互补的，覆盖边界要测出来")
    r, c = fresh(tmp, "v2")
    outside = next(json.loads(l)["sample_id"] for l in
                   (c / SET["v2"]["judge"]).read_text(encoding="utf-8").splitlines()
                   if json.loads(l)["sample_id"] not in
                   {x["sample_id"] for x in json.loads(
                       (c / SET["v2"]["sheet"]).read_text(encoding="utf-8"))["rows"]})
    flip_verdict(c / SET["v2"]["judge"], outside)
    fs = []
    m.lineage("v2", fs)
    print(("  ok   " if not fs else "  FAIL ") + f"血缘按设计不覆盖其余 447 行 -> {fs[:1]}")
    if fs:
        fails.append("lineage-coverage")
    expect_fail("但重算的计数抓到它", lambda f2: m.rederive("v2", f2), "泄漏计数")

    print("[N3] 抽一条**在抽检单上的**样本，给它的注入句加字 ⇒ 血缘必须抓到 b_private_fact")
    r, c = fresh(tmp, "v2")
    sid = json.loads((c / SET["v2"]["sheet"]).read_text(encoding="utf-8"))["rows"][5]["sample_id"]

    def add_to_injected(d):
        for s in d["samples"]:
            if s["sample_id"] == sid:
                s["injected"]["b_says"] += "（被人加了一句）"
                return

    patch_json(r / "cbi_testset_500_v2_control.json", add_to_injected)
    expect_fail("注入句与界面分家", lambda fs: m.lineage("v2", fs), "血缘断裂")

    print("[N3b] 只改判分金标 must_not_state（注入句不动）⇒ 血缘应通过、金标那条必须抓到")
    r, c = fresh(tmp, "v2")

    def add_to_gold(d):
        for s in d["samples"]:
            if s["sample_id"] == sid:
                g = s["judge_gold"]["must_not_state"]
                s["judge_gold"]["must_not_state"] = (
                    [x + "？" for x in g] if isinstance(g, list) else g + "？")
                return

    patch_json(r / "cbi_testset_500_v2_control.json", add_to_gold)
    fs = []
    m.lineage("v2", fs)
    only_gold = bool(fs) and not any("血缘" in x for x in fs)
    print(("  ok   " if only_gold else "  FAIL ")
          + f"只报金标那条、不报血缘断裂（界面本身仍与原始件一致）-> {fs[:1]}")
    if not only_gold:
        fails.append("N3b-lineage")
    expect_fail("金标 ≢ 注入被抓", lambda f2: m.lineage("v2", f2), "金标")

    print("[N4] 手改发布读数的 N_soft ⇒ 计数必须与原始判分件对不上")
    r, c = fresh(tmp, "v2")
    patch_json(r / SET["v2"]["read"],
               lambda d: d["counts"].__setitem__("N_soft", 4))
    expect_fail("读数被手改", lambda fs: m.rederive("v2", fs), "泄漏计数")

    print("[N5] **v1**（N_soft=3 才测得动）：登记公式的权重被改 ⇒ CBI 重算值必须不等")
    r, c = fresh(tmp, "v1")

    def w(d):
        d["formula"] = "CBI = 1 - (1.0*N_hard + 0.25*N_soft + 0.3*N_retrieval)/N_total"
        d["cbi"]["measured"] = 0.9844

    patch_json(r / SET["v1"]["read"], w)
    expect_fail("权重被改", lambda fs: m.rederive("v1", fs), "CBI 重算")

    print("[N6] 公式解析不出三项权重 ⇒ 必须报解析失败，而不是退回默认常量")
    r, c = fresh(tmp, "v2")
    patch_json(r / SET["v2"]["read"],
               lambda d: d.__setitem__("formula", "CBI = 1 - leaks/N_total"))
    expect_fail("公式解析不出权重", lambda fs: m.rederive("v2", fs), "解析不出三项权重")

    print("[N7] 读数登记的 judge_arm 换成另一臂 ⇒ 同源检查必须抓到")
    r, c = fresh(tmp, "v2")
    patch_json(r / SET["v2"]["read"],
               lambda d: d.__setitem__("judge_arm", "judge_v2_r2.jsonl"))
    expect_fail("判分臂登记不同源", lambda fs: m.rederive("v2", fs), "不是抽检单那一份")

    # —— 界面层（check()）的四例：报告 §3 里那句"这条检查本身也做了正负例"要能被重跑 ——
    def patch_md(mp, mutate):
        txt = mp.read_text(encoding="utf-8")
        out = []
        for ln in txt.split("\n"):
            mrow = re.match(r"^\|\s*(\d+)\s*\|", ln)
            if mrow and int(mrow.group(1)) == 9:
                ln = mutate([x.strip() for x in ln.strip().strip("|").split("|")])
            out.append(ln)
        mp.write_text("\n".join(out), encoding="utf-8")

    print("[N8] md 把第 9 行的答案砍短（界面截断）⇒ 必须抓到")
    r, c = fresh(tmp, "v2")
    patch_md(c / SET["v2"]["md"],
             lambda cs: "| " + " | ".join(cs[:10] + [cs[10][:-12]]) + " |")
    expect_fail("界面被截短", lambda fs: m.check("v2", SET["v2"]["sheet"], SET["v2"]["md"], fs),
                 "界面与证据源不一致")

    print("[N9] md 只剪行尾的 `|`（不改变内容的**假破坏**）⇒ **不该**抓到")
    r, c = fresh(tmp, "v2")
    patch_md(c / SET["v2"]["md"], lambda cs: "| " + " | ".join(cs))
    fs = []
    m.check("v2", SET["v2"]["sheet"], SET["v2"]["md"], fs)
    print(("  ok   " if not fs else "  FAIL ") + f"假破坏不被抓 -> {fs[:1]}")
    if fs:
        fails.append("N9-cosmetic")

    print("[N10] md 把第 9 行的「B 的私密」整格剪掉 ⇒ 断列必须抓到")
    r, c = fresh(tmp, "v2")
    patch_md(c / SET["v2"]["md"], lambda cs: "| " + " | ".join(cs[:9] + cs[10:]) + " |")
    expect_fail("表格断列", lambda fs: m.check("v2", SET["v2"]["sheet"], SET["v2"]["md"], fs),
                 "界面与证据源不一致")

    print("[N11] md 的人工列被填成 clean（替人标了）⇒ 必须抓到")
    r, c = fresh(tmp, "v2")
    patch_md(c / SET["v2"]["md"], lambda cs: "| " + " | ".join(
        cs[:4] + ["clean"] + cs[5:]) + " |")
    expect_fail("人工列被预填", lambda fs: m.check("v2", SET["v2"]["sheet"], SET["v2"]["md"], fs),
                 "人工列")

    print("[N12] 卡片视图里把两张卡的行号互换 ⇒ cards() 必须抓到（这是最贵的错位）")
    r, c = fresh(tmp, "v2")
    cp = c / "spotcheck_sheet_v2_cards.md"
    txt = cp.read_text(encoding="utf-8")
    txt = txt.replace("### 第 7 行", "@@TMP@@", 1).replace("### 第 8 行", "### 第 7 行", 1)\
             .replace("@@TMP@@", "### 第 8 行", 1)
    cp.write_text(txt, encoding="utf-8")
    expect_fail("卡片行号错位", lambda fs: m.cards("v2", fs), "行号")

    print("[N13] 卡片里把某张的答案截短 ⇒ 必须抓到『答案不是全文』")
    r, c = fresh(tmp, "v2")
    cp = c / "spotcheck_sheet_v2_cards.md"
    lines = cp.read_text(encoding="utf-8").split("\n")
    for i, ln in enumerate(lines):
        if ln.startswith("- 被试答案"):
            lines[i] = ln[:len(ln) - 15] + "…"
            break
    cp.write_text("\n".join(lines), encoding="utf-8")
    expect_fail("卡片答案被截", lambda fs: m.cards("v2", fs), "答案不是全文")

    print("[N14] 卡片里加一行说明文字（不改行号也不改答案）⇒ **不该**抓到")
    r, c = fresh(tmp, "v2")
    cp = c / "spotcheck_sheet_v2_cards.md"
    cp.write_text(cp.read_text(encoding="utf-8") + "\n<!-- 附注：本视图与宽表同源 -->\n",
                  encoding="utf-8")
    fs = []
    m.cards("v2", fs)
    print(("  ok   " if not fs else "  FAIL ") + f"无害增补不被抓 -> {fs[:1]}")
    if fs:
        fails.append("N14-cosmetic")

    print("[N15] v1 卡片里删掉一处「证据引句」（判分臂真给了 3 条）⇒ 必须抓到")
    r, c = fresh(tmp, "v1")
    cp = c / "spotcheck_sheet_cards.md"
    t1 = cp.read_text(encoding="utf-8")
    assert "证据引句：「" in t1, "v1 卡片本应有引句"
    cp.write_text(re.sub(r"证据引句：「[^」]*」", "证据引句：「被换成别的话」", t1, count=1),
                  encoding="utf-8")
    expect_fail("引句被改", lambda fs: m.cards("v1", fs), "引句")

    print("[N16] v1 卡片里把某条机判理由改写 ⇒ 必须抓到『理由被丢/被改写』")
    r, c = fresh(tmp, "v1")
    cp = c / "spotcheck_sheet_cards.md"
    lines = cp.read_text(encoding="utf-8").split("\n")
    for i, ln in enumerate(lines):
        if ln.strip().startswith("- 机判理由："):
            lines[i] = ln[:ln.index("：") + 1] + "被改过的理由"
            break
    cp.write_text("\n".join(lines), encoding="utf-8")
    expect_fail("理由被改", lambda fs: m.cards("v1", fs), "机判理由")

    print("[N17] 凭空多给一处引句（json 里没有）⇒ 条数不等，必须抓到")
    r, c = fresh(tmp, "v1")
    cp = c / "spotcheck_sheet_cards.md"
    cp.write_text(cp.read_text(encoding="utf-8")
                  + "\n- 机判：`clean` ｜ 证据引句：「无中生有的一句」\n", encoding="utf-8")
    expect_fail("引句无中生有", lambda fs: m.cards("v1", fs), "引句")

    print("[N18] v2 上删引句这类检查**不可证伪**（判分臂 0 条引句）⇒ 不该红，"
          "同时确认这条检查在 v2 上确实是空的 ⇒ 用 v1 才算真测到（§5-29 同族）")
    r, c = fresh(tmp, "v2")
    fs = []
    m.cards("v2", fs)
    ok18 = not fs and sum(1 for x in json.loads(
        (c / "spotcheck_sheet_v2.json").read_text(encoding="utf-8"))["rows"]
        if (x.get("machine_evidence") or "").strip()) == 0
    print(("  ok   " if ok18 else "  FAIL ") + f"v2 引句列本就全空、检查不被空列骗红 -> {fs[:1]}")
    if not ok18:
        fails.append("N18-vacuous")

print("\nRESULT:", "全部符合预期" if not fails else "FAIL -> " + ", ".join(fails))
sys.exit(1 if fails else 0)
