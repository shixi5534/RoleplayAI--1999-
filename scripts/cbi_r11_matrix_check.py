"""闸门矩阵自检（纯只读）：P10 §R11 那张表的每个数字都必须能直接从读数产物里取到。

为什么要单独留这个脚本：R11 是**汇总表面**，它是这一轮里最容易被后续改动悄悄带偏的一类文字
—— 读数重跑一次、子标准多一格，正文不会报错，只有表会开始说谎。所以把三件事变成断言：
  1) 表里四行的 counts / CBI 与产物字段逐一相等（三个仪器读数 + 叠加列的两把尺子）；
  2) 三个仪器读数里 **除 κ 以外没有第二格 false**（刻意不写成"false 的那格必须等于 κ"——
     那样写会在你标完、κ 变 true 之后无端报红；一条会因为测量完成而失效的检查不是检查），
     且 κ 为 false 时其详情必须写"未达成"（没测 ≠ 测了不过，这是 §R11 的立论前提）；
  3) 叠加列 `cbi_result_v2hard.json` **不含** MRR / Faithfulness 字段 ——
     那两条是三个仪器读数共用的基线，引用叠加列时不能顺手替它答。
另外核正文里的四个数字串确实出现在表里（防止脚本与文字各说各话）。

2026-10-12 两次扩容：`check_expo()` 管报告 §2.13 那张名次暴露表；
`check_22()` 管**§2.2 门面表**（发布判定就是从这张表读出去的，此前它是纯手写散文）——
MRR 与 Faithfulness 两格**从 audit_l2/audit_l3 现算复算**（含定义域与含零行数），
总式也由 counts 再算一遍，联合判定要求与读数 `gate` **逐字**一致，
而「κ 未标」必须与 κ 产物的在册状态一致。

用法：`PYTHONIOENCODING=utf-8 .venv/Scripts/python.exe scripts/cbi_r11_matrix_check.py`
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

# Windows 控制台常见 cp936：产物落盘后才抛 UnicodeEncodeError 最难查（写了一半、退出码非零）。
for _stream in (sys.stdout, sys.stderr):
    if hasattr(_stream, "reconfigure"):
        _stream.reconfigure(errors="replace")

ROOT = Path(__file__).resolve().parents[1]
R = ROOT / "data" / "compendium_rag" / "reports"
P10 = (ROOT / "docs" / "compendium-rag" / "P10修复计划_CBI收口.md").read_text(encoding="utf-8")
REPORT = (ROOT / "docs" / "compendium-rag" / "P9_CBI报告.md").read_text(encoding="utf-8")

INSTRUMENT_READINGS = {
    "cbi_result_full.json": (0, 3, 21, 0.9844),
    "cbi_result_v2instrument.json": (0, 0, 30, 0.982),
    "cbi_result_v2instrument_v2_r2.json": (0, 0, 30, 0.982),
}
KAPPA_KEY = "人工抽检 kappa>=0.80"
# κ 产物的**真名**不写在这里：它按 (读数登记的 instrument, judge_arm) 两维现推（见 check_22）。
# 这个变量只是负向测试 N19 的注入点 —— 不写死文件名，是因为写死的文件名会在换臂时看错凭证。
KAPPA_FILE_OVERRIDE = None
AUDIT_L2 = R / "audit_l2.json"
AUDIT_L3 = R / "audit_l3.json"
FAITH_SETS = ("300cn", "blind", "gen")


def kappa_file_for(d: dict) -> Path:
    """这一列读数的 κ 凭证文件名 = **(读数登记的仪器, 判分臂)** 两维现推。

    与 `cbi_spotcheck.kappa_result_path` / `cbi_calculator.kappa_artifact_path` 同一条规则；
    写死只按仪器的旧名（`cbi_spotcheck_kappa_v2.json`）在两把尺子之间会看错凭证 ——
    门面表上「人工 κ」那一格就跟着过期不报。负向套件里 N19b 直接断言这个函数的输出。
    """
    return R / f"cbi_spotcheck_kappa_{d['instrument']}_" \
               f"{str(d['judge_arm']).removesuffix('.jsonl')}.json"


def sec_22() -> str:
    if "### 2.2" not in REPORT:
        return ""
    return REPORT.split("### 2.2", 1)[-1].split("\n### ", 1)[0]


def row_of(sec: str, label: str) -> str:
    return next((ln for ln in sec.splitlines()
                 if ln.startswith("|") and label in ln), "")


def recompute_l3() -> tuple:
    """Faithfulness 两个口径**从 audit_l3.json 现算**，不抄读数的字符串。"""
    pc = json.loads(AUDIT_L3.read_text(encoding="utf-8"))["per_case"]
    ins = [r.get("faithfulness") for r in pc if r.get("set") in FAITH_SETS]
    allo = [r.get("faithfulness") for r in pc]
    if not ins or not allo:
        raise SystemExit("[FATAL] audit_l3.per_case 里没有 faithfulness 字段 ⇒ 无从复算")
    return (round(sum(ins) / len(ins), 4), round(sum(allo) / len(allo), 4),
            len(ins), len(allo))


def recompute_l2() -> tuple:
    """MRR 三套均值/定义域/含零行数，同样现算（含 answerable 过滤与缺字段跳过）。"""
    per, zero, n_miss, n_un = {}, {}, 0, 0
    for r in json.loads(AUDIT_L2.read_text(encoding="utf-8"))["per_case"]:
        if not r.get("answerable", True):
            n_un += 1
            continue
        v = r.get("mrr@10", None)
        if not isinstance(v, (int, float)):
            n_miss += 1
            continue
        per.setdefault(r["set"], []).append(float(v))
        zero[r["set"]] = zero.get(r["set"], 0) + (1 if v == 0 else 0)
    means = {k: round(sum(v) / len(v), 5) for k, v in per.items()}
    ns = {k: len(v) for k, v in per.items()}
    return means, ns, zero, n_miss, n_un


def check_22(fails: list) -> None:
    """报告 §2.2 是**门面表**：发布判定就是从这张表读出去的，
    可它此前是纯手写散文 —— 没有一格回到产物核过。这一条把它变成机器可核。"""
    sec = sec_22()
    if not sec:
        fails.append("报告里没有 §2.2（门面闸门表的唯一落点）")
        return
    d = load("cbi_result_full.json")
    c, cb = d["counts"], d["cbi"]
    # 总式自己再算一遍：0.9844 必须是 (0,3,21)/500 的结果，而不是抄来的小数
    mine = round(1 - (1.0 * c["N_hard"] + 0.5 * c["N_soft"]
                      + 0.3 * c["N_retrieval"]) / c["N_total_effective"], 4)
    want_rows = {
        "**CBI 实测**": [f"{cb['measured']}"],
        "N_hard": [f"{c['N_hard']}"],
        "N_soft": [f"{c['N_soft']}", f"{c['N_soft'] / c['N_total_effective']:.1%}"],
        "N_retrieval": [f"{c['N_retrieval']}",
                        f"{c['N_retrieval'] / c['N_total_effective']:.1%}",
                        "≤ 15", "≤ 0.10"],
    }
    if mine != cb["measured"]:
        fails.append(f"§2.2 的 CBI 与总式现算不符：现算 {mine} vs 读数 {cb['measured']}")
    for lab, toks in want_rows.items():
        line = row_of(sec, lab)
        if not line:
            fails.append(f"§2.2 找不到「{lab}」那一行")
            continue
        for t in toks:
            if t not in line:
                fails.append(f"§2.2「{lab}」行缺 {t!r}：{line[:120]}")
    f_in, f_all, n_in, n_all = recompute_l3()
    m_means, m_ns, m_zero, m_miss, m_un = recompute_l2()
    line = row_of(sec, "MRR")
    for t in [str(m_means["300cn"]), str(m_means["blind"]), str(m_means["gen"]),
              f"300cn {m_ns['300cn']}/300", f"blind {m_ns['blind']}", f"gen {m_ns['gen']}",
              f"{m_zero['300cn']}/{m_zero['blind']}/{m_zero['gen']}"]:
        if t not in line:
            fails.append(f"§2.2 的 MRR 行缺现算值 {t!r}（现算 {m_means} n={m_ns} 含零={m_zero}）")
    if m_miss or m_un:
        fails.append(f"§2.2 的 MRR 是在缺字段 {m_miss} 行 / 跳过非 answerable {m_un} 行的情况下算的，"
                     "这张表没写")
    line = row_of(sec, "Faithfulness")
    for t in [str(f_in), str(n_in), str(f_all), str(n_all)]:
        if t not in line:
            fails.append(f"§2.2 的 Faithfulness 行缺现算值 {t!r}（现算 in-scope={f_in}(n={n_in}) "
                         f"全体={f_all}(n={n_all})）")
    # 「未标」必须与真凭证同步：产物出现了却还写"未标"，就是门面在撒谎。
    # 文件名不写死 —— 从读数自己登记的 (instrument, judge_arm) 现推：
    # κ 产物按两维命名，一台仪器两把尺子各有各的凭证（写死会在换臂时悄悄看错文件）。
    line = row_of(sec, "人工 κ")
    kap_v1 = KAPPA_FILE_OVERRIDE or kappa_file_for(d)
    if kap_v1.exists() and "未标" in line:
        fails.append(f"§2.2 仍写「未标」，但 {kap_v1.name} 已在册 ⇒ 这张表过期了")
    if not kap_v1.exists() and "未标" not in line:
        fails.append("§2.2 的 κ 行没写「未标」，可 κ 产物根本不存在（没测不能含糊）")
    if row_of(sec, "联合判定") and d["gate"] not in row_of(sec, "联合判定"):
        fails.append(f"§2.2 的联合判定与读数的 gate 不一致：读数={d['gate']!r}")


# §2.13 那张名次暴露表是**正文里的数字**，按 §5-28 的纪律它必须有资格变红：
# 每个格子都回到读数产物的 `both_calibers.<口径>.exposure` 去取。
EXPO_ROWS = [
    ("v1 控制（验收口径", "cbi_result_full.json", "control"),
    ("v1 字面口径", "cbi_result_full.json", "literal"),
    ("v2 控制（尺 v1 与尺 v2 两臂同", "cbi_result_v2instrument.json", "control"),
]
EXPO_NA_ROWS = [("v2 字面口径", "cbi_result_v2instrument.json", "literal")]
EMO = str.maketrans({"*": None, "`": None})


def cellize(line: str) -> list:
    return [c.translate(EMO).strip() for c in line.strip().strip("|").split("|")]


def find_row(label: str) -> str:
    """只在 §2.13 那一节里找 —— 标签里的词（如"字面口径"）在正文别处也出现，
    全篇扫会抓到别的表，那种抓错会表现成"检查无理由报红"。"""
    sec = REPORT.split("### 2.13")[-1].split("\n## ")[0]
    for ln in sec.splitlines():
        if ln.startswith("|") and label in ln:
            return ln
    return ""


def parse_hist(txt: str) -> dict:
    out = {}
    for part in txt.strip("{}").split(","):
        if part.strip():
            k, v = part.split(":")
            out[int(k)] = int(v)
    return out


def check_expo(fails: list) -> None:
    if "### 2.13" not in REPORT:
        fails.append("报告里没有 §2.13（那张名次暴露表的唯一落点）")
        return
    for label, fname, cal in EXPO_ROWS:
        line = find_row(label)
        if not line:
            fails.append(f"§2.13 找不到 {label} 那一行")
            continue
        blk = load(fname)["both_calibers"][cal]
        e = blk.get("exposure")
        if not e:
            fails.append(f"{fname}:{cal} 读数里没有 exposure 块（正文那张表成了无源之水）")
            continue
        c = cellize(line)
        want = [str(blk["N_retrieval"]), str(e["n_gold_in_top6"]), None,
                str(e["mean_rank"]), str(e["at_rank1"]), str(e["exposure_by_k"]["top3"]),
                f"{e['reciprocal_rank_hazard_cond']} / {e['reciprocal_rank_hazard_all']}",
                str(e["flag_mismatch_with_channel"])]
        got = c[1:9]
        # 第 3 格是名次分布：正文写 `{2:1,...}`、产物是 {"2":1,...}，单独按字典比，
        # 留在 want 里当 None 让下面的逐格循环跳过它（否则字符串永远不等于字典）。
        if parse_hist(got[2]) != {int(k): v for k, v in e["rank_hist"].items()}:
            fails.append(f"§2.13 {label[:14]} 名次分布正文={got[2]!r} 产物={e['rank_hist']!r}")
        print(f"§2.13 {label[:12]}… 格子 vs 产物："
              f"{all(g == w for g, w in zip(got, want) if w is not None)}")
        for i, (g, w) in enumerate(zip(got, want), start=1):
            if w is not None and g != w:
                fails.append(f"§2.13 {label[:14]} 第 {i + 1} 格正文={g!r} 产物={w!r}")
        # 三源同数：正文 `严格` 列 ≡ exposure.n_gold ≡ 通道标记计数
        if not (e["n_gold_in_top6"] == blk["gold_anchor_in_top6"] == int(c[2])):
            fails.append(f"§2.13 {label[:14]} 严格列与两个内部来源不同数")
    for label, fname, cal in EXPO_NA_ROWS:
        line = find_row(label)
        blk = load(fname)["both_calibers"][cal]
        c = cellize(line) if line else []
        if blk.get("available"):
            fails.append(f"正文把 {label} 写成『不可算』，但读数的该口径是 available=True")
        if not line:
            fails.append(f"§2.13 找不到 {label} 那一行")
        elif "不可算" not in c[-1] or any(x not in ("—", "") for x in c[1:8]):
            fails.append(f"§2.13 {label} 行格式与『不可算』不符：{c}")
    a = load("cbi_result_v2instrument.json")["both_calibers"]["control"]["exposure"]
    b = load("cbi_result_v2instrument_v2_r2.json")["both_calibers"]["control"]["exposure"]
    if a != b:
        fails.append("正文写『两臂同』，但 v2 两臂的 exposure 块不同")



def load(name: str) -> dict:
    return json.loads((R / name).read_text(encoding="utf-8"))


def main() -> int:
    fails: list[str] = []
    for name, expect in INSTRUMENT_READINGS.items():
        d = load(name)
        c = d["counts"]
        got = (c["N_hard"], c["N_soft"], c["N_retrieval"], d["cbi"]["measured"])
        sub = d["sub_criteria"]
        other_false = sorted(k for k, v in sub.items() if not v and k != KAPPA_KEY)
        kappa_state = "false（未达成）" if not sub.get(KAPPA_KEY, True) else "true"
        print(f"{name}: {got} == 表值 {expect} 除 κ 外 false 的格子 {other_false} κ={kappa_state}")
        if got != expect:
            fails.append(f"{name} 计数/CBI 与表不符：{got} != {expect}")
        # 注意这里断言的是"除 κ 以外不许有第二格 false"，**不是**"false 的那格必须等于 κ"。
        # 后者会在你标完、κ 变 true 的那一刻起无端报红——一条会因为测量完成而失效的检查，
        # 本身就不是检查。§R11 的立论"只差人工 κ"在 κ=false(未测) 与 κ=true(已过) 两种状态下都成立。
        if other_false:
            fails.append(f"{name} 除 κ 之外还有 false 的子标准：{other_false}")
        if (not sub.get(KAPPA_KEY, True)
                and "未达成" not in json.dumps(d.get("sub_details"), ensure_ascii=False)):
            fails.append(f"{name} 的 κ 是 false 却没写成『未达成』（没测与测了不过必须能区分）")

    hv = load("cbi_result_v2hard.json")
    rv2, rv1 = hv["ruler_v2"], hv["ruler_v1"]
    print(f"叠加列: ruler_v2 {rv2['counts']} {rv2['cbi']} failed={rv2['failed_gates']}")
    if (rv2["counts"]["hard"], rv2["cbi"]) != (4, 0.9764):
        fails.append("叠加列 hard=4 / CBI=0.9764 与表不符")
    if rv2["gates"]["N_hard=0"] is not False:
        fails.append("叠加列 N_hard=0 应为 false")
    if (rv1["counts"]["hard"], rv1["cbi"]) != (0, 0.9844):
        fails.append("叠加列的 ruler_v1 应与 cbi_result_full 同值")
    if "MRR" in json.dumps(hv, ensure_ascii=False):
        fails.append("叠加列里出现了 MRR 字段 —— §R11 说它不该有，得改文字或改产物")

    for pat in (r"\| 0 \| 3 \| 21 \| 0\.9844 \|",
                r"\| \*\*4\*\* \| 3 \| 21 \| 0\.9764 \|",
                r"\| 0 \| 0 \| 30 \| 0\.9820 \|"):
        if not re.search(pat, P10):
            fails.append(f"§R11 表里找不到 {pat}")
    if "§R11" not in REPORT:
        fails.append("报告 §4 没有指向 §R11")
    if "判分尺子的条款号" not in REPORT:
        fails.append("报告里 R2/R3 的命名冲突（尺子条款 vs P10 项）没被澄清")

    check_expo(fails)
    check_22(fails)

    print("\nRESULT:", "§R11 的每个数都来自产物" if not fails else "FAIL -> " + " | ".join(fails))
    return 1 if fails else 0


if __name__ == "__main__":
    raise SystemExit(main())
