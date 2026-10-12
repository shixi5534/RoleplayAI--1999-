"""矩阵自检的负向测试：`cbi_r11_matrix_check` 必须能变红，而且破坏要打在**它真会读的东西**上。

§5-29 的教训在这一轮被当成设计约束用了：把破坏打在检查覆盖之外（改一个它不扫的字段、
改一条它不遍历的行），检查"抓不到"却什么也没说明，等于给它发一张没挣来的绿灯。
所以这里的红分别打在真实支路上：正文表里的数字串 / `ruler_v2.cbi` /
叠加列被塞进 MRR 字段 / 某仪器读数的某格子标准变 false / κ 详情不再写"未达成" /
报告 §4 不再指向 §R11 / **§2.13 名次暴露表的正文数字** / **产物里的 `exposure.at_rank1`** /
**"不可算"那行被填成数字** / **"两臂同"被推翻** / **§2.13 节锚被改名**。
配三例**该绿**的：κ 变 true（测量完成不该让检查变红）、
只改 `exposure.definition`（正文不印的字段，证明检查读的是那 8 个格子而不是整块 blob）、
以及首尾两次原件全绿（证明上面这些不是恒红）。§2.2 那一支又加 8 例（7 红 + 1 该绿），合计 **24 例 = 18 红 + 6 绿**。

用法：`PYTHONIOENCODING=utf-8 .venv/Scripts/python.exe scripts/cbi_r11_matrix_negtest.py`
"""
import importlib.util
import json
import sys
import tempfile
from pathlib import Path
# Windows 控制台常见 cp936：产物落盘后才抛 UnicodeEncodeError 最难查（写了一半、退出码非零）。
for _stream in (sys.stdout, sys.stderr):
    if hasattr(_stream, "reconfigure"):
        _stream.reconfigure(errors="replace")


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
spec = importlib.util.spec_from_file_location("mtx", ROOT / "scripts" / "cbi_r11_matrix_check.py")
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

REAL_LOAD, REAL_P10, REAL_REP = m.load, m.P10, m.REPORT
fails = []


def run(name, want_hit, needle=None):
    rc = m.main()
    hit = rc == 1
    ok = hit == want_hit and (needle is None or not needle or True)
    print(("  ok   " if ok else "  FAIL ") + f"{name}: rc={rc} 期望红={want_hit}")
    if not ok:
        fails.append(name)


print("[C] 原件 ⇒ 必须全绿")
run("control", False)

print("[N1] 正文表里把 0.9820 改成 0.9831 ⇒ 该红")
m.P10 = REAL_P10.replace("| 0 | 0 | 30 | 0.9820 |", "| 0 | 0 | 30 | 0.9831 |")
run("doc-number", True)
m.P10 = REAL_P10

print("[N2] 把 v2hard 的 ruler_v2.cbi 从 0.9764 改成 0.9844（叠加列不再破硬闸门）⇒ 该红")
def load_fake(name):
    d = REAL_LOAD(name)
    if name == "cbi_result_v2hard.json":
        d["ruler_v2"]["cbi"] = 0.9844
    return d
m.load = load_fake
run("overlay-cbi", True)

print("[N3] 叠加列里塞进 MRR 字段（推翻 R11 的『这条不在它字段里』）⇒ 该红")
def load_mrr(name):
    d = REAL_LOAD(name)
    if name == "cbi_result_v2hard.json":
        d["ruler_v2"]["gates"]["MRR>=0.39 不回退"] = True
    return d
m.load = load_mrr
run("overlay-mrr", True)
m.load = REAL_LOAD

print("[N4] 某个仪器读数的 κ 变 true（你标完且过了）⇒ **必须仍然全绿**："
      "§R11『只差人工 κ』在 κ=false(未测) 与 κ=true(已过) 两种状态下都成立，"
      "检查不许因为测量完成就自己变红")
def load_kappa(name):
    d = REAL_LOAD(name)
    if name == "cbi_result_v2instrument.json":
        d["sub_criteria"]["人工抽检 kappa>=0.80"] = True
    return d
m.load = load_kappa
run("kappa-true-stays-green", False)

print("[N4b] 把另一格子标准改成 false（`N_soft<=5` 破线）⇒ 该红")
def load_soft(name):
    d = REAL_LOAD(name)
    if name == "cbi_result_v2instrument.json":
        d["sub_criteria"]["N_soft<=5"] = False
    return d
m.load = load_soft
run("other-gate-false", True)
m.load = REAL_LOAD

print("[N5] κ 的详情不再写『未达成』（没测与测了不过混为一谈）⇒ 该红")
def load_detail(name):
    d = REAL_LOAD(name)
    if name == "cbi_result_full.json":
        d["sub_details"]["kappa"] = "已达成"
    return d
m.load = load_detail
run("kappa-wording", True)
m.load = REAL_LOAD

print("[N6] 报告 §4 不再指向 §R11 ⇒ 该红")
m.REPORT = REAL_REP.replace("§R11", "某节")
run("report-pointer", True)
m.REPORT = REAL_REP

print("[N7] §2.13 正文把 v1 控制的『严格』从 12 改成 13 ⇒ 该红")
m.REPORT = REAL_REP.replace("| 21 | **12** |", "| 21 | **13** |", 1)
run("expo-doc-number", True)
m.REPORT = REAL_REP

print("[N8] 产物里 exposure.at_rank1 被改（0→3）而正文没跟着改 ⇒ 该红")
def load_expo(name):
    d = REAL_LOAD(name)
    if name == "cbi_result_full.json":
        d["both_calibers"]["control"]["exposure"]["at_rank1"] = 3
    return d
m.load = load_expo
run("expo-artifact-mutation", True)
m.load = REAL_LOAD

print("[N8b] 只改 exposure.definition（正文不印的那句）⇒ **必须仍绿**："
      "检查读的是那 8 个格子，不是整块 blob；否则它红得没有道理")
def load_expo_text(name):
    d = REAL_LOAD(name)
    if name == "cbi_result_full.json":
        d["both_calibers"]["control"]["exposure"]["definition"] = "改了一句说明文字"
    return d
m.load = load_expo_text
run("expo-unprinted-field-stays-green", False)
m.load = REAL_LOAD

print("[N9] §2.13 里『v2 字面口径』那行被填成数字（其实该口径不可算）⇒ 该红")
m.REPORT = REAL_REP.replace("| v2 字面口径 | — |", "| v2 字面口径 | 9 |", 1)
run("expo-na-row-faked", True)
m.REPORT = REAL_REP

print("[N10] 把两臂 v2 的 exposure 改成不一样（正文写着『两臂同』）⇒ 该红")
def load_two(name):
    d = REAL_LOAD(name)
    if name == "cbi_result_v2instrument_v2_r2.json":
        d["both_calibers"]["control"]["exposure"]["mean_rank"] = 9.9
    return d
m.load = load_two
run("expo-two-arm-claim", True)
m.load = REAL_LOAD

print("[N11] §2.13 的标题被改名（表还在，但按节锚定位不到了）⇒ 该红，不许静默通过")
m.REPORT = REAL_REP.replace("### 2.13", "### 2.1X", 1)
run("expo-section-missing", True)
m.REPORT = REAL_REP


print("[N13] §2.2 的 Faithfulness 0.9845 改成 0.9846 ⇒ 该红（门面表与现算复算对不上）")
m.REPORT = REAL_REP.replace("L3.3 = **0.9845**", "L3.3 = **0.9846**", 1)
run("sec22-faith", True)
m.REPORT = REAL_REP

print("[N14] §2.2 的 MRR 第三个值 0.82188 改成 0.8219 ⇒ 该红")
m.REPORT = REAL_REP.replace("**0.66528 / 0.6808 / 0.82188**", "**0.66528 / 0.6808 / 0.8219**", 1)
run("sec22-mrr", True)
m.REPORT = REAL_REP

print("[N15] §2.2 的含零行数 23/15/0 改成 23/15/1 ⇒ 该红（定义域记账也是门面的一部分）")
m.REPORT = REAL_REP.replace("真为 0 的行 23/15/0 条", "真为 0 的行 23/15/1 条", 1)
run("sec22-mrr-zero", True)
m.REPORT = REAL_REP

print("[N16] §2.2 的联合判定退回缩写「+ P10 必修」⇒ 该红（必须与读数 gate 逐字一致）")
m.REPORT = REAL_REP.replace("**有条件发布 + 必须出 P10 修复计划**", "**有条件发布 + P10 必修**", 1)
run("sec22-verdict", True)
m.REPORT = REAL_REP

print("[N17] 把 §2.2 检索行里的「≤ 0.10」擦掉 ⇒ 该红（裁决后的能力线不许从门面表消失）")
_line = next(l for l in REAL_REP.splitlines() if l.startswith("| N_retrieval"))
assert "→ **能力读数 ≤ 0.10**" in _line, "锚文本变了，这一例要改"
m.REPORT = REAL_REP.replace(_line, _line.replace("→ **能力读数 ≤ 0.10**", "→ **能力读数**"), 1)
run("sec22-capability-line", True)
m.REPORT = REAL_REP

print("[N18] 节锚改名（### 2.2 → ### 2.X）⇒ 该红，不许因找不到段落而静默通过")
m.REPORT = REAL_REP.replace("### 2.2 答案通道", "### 2.X 答案通道", 1)
run("sec22-heading-missing", True)
m.REPORT = REAL_REP

print("[N19] κ 产物凭空出现而 §2.2 仍写「未标」⇒ 该红（门面过期要被抓）")
_fake = Path(tempfile.mkdtemp(prefix="kappa_fake_")) / "cbi_spotcheck_kappa.json"
_fake.write_text('{"gate_pass": true}', encoding="utf-8")
_kap_real = m.KAPPA_FILE_V1
m.KAPPA_FILE_V1 = _fake
run("sec22-kappa-stale", True)
m.KAPPA_FILE_V1 = _kap_real
print("     补一句：这一例只动内存里的路径，仓库里仍然不许有 κ 产物或人工标注")
_k = [f.name for f in (ROOT / "data" / "compendium_rag" / "reports").glob("cbi_spotcheck_kappa*")]
_l = [f.name for f in (ROOT / "data" / "compendium_rag" / "reports" / "cbi").glob("spotcheck_labels*")]
print(("  ok   " if not _k and not _l else "  FAIL ") + f"仓库内 κ 产物/标注文件计数 = {len(_k)}/{len(_l)}")
if _k or _l:
    fails.append("repo-artifact-leak")

print("[N20] 只改 §2.2 **之外**的一个数（§2.15 正文里的语料字符数）⇒ 不该红："
      "检查只管门面那张表，做成恒红同样不能采信")
_anchor = "3,392,739 字符"
assert _anchor in REAL_REP, "N20 的锚文本变了，这一例要改"
_line2 = next(l for l in REAL_REP.splitlines() if _anchor in l)
_sec = REAL_REP.split("### 2.2", 1)[1].split(chr(10) + "### ", 1)[0]
assert _line2 not in _sec, "N20 挑的行必须落在 §2.2 之外"
m.REPORT = REAL_REP.replace(_line2, _line2.replace("3,392,739", "3,392,740"), 1)
run("sec22-outside-untouched", False)
m.REPORT = REAL_REP

print("[N21] 恢复原样 ⇒ 必须重新全绿（证明上面这些不是恒红）")
run("control-again", False)

print("\nRESULT:", "全部符合预期" if not fails else "FAIL -> " + ", ".join(fails))
sys.exit(1 if fails else 0)
