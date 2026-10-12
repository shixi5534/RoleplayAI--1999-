"""矩阵自检的负向测试：`cbi_r11_matrix_check` 必须能变红，而且破坏要打在**它真会读的东西**上。

§5-29 的教训在这一轮被当成设计约束用了：把破坏打在检查覆盖之外（改一个它不扫的字段、
改一条它不遍历的行），检查"抓不到"却什么也没说明，等于给它发一张没挣来的绿灯。
所以这里的红分别打在真实支路上：正文表里的数字串 / `ruler_v2.cbi` /
叠加列被塞进 MRR 字段 / 某仪器读数的某格子标准变 false / κ 详情不再写"未达成" /
报告 §4 不再指向 §R11 / **§2.13 名次暴露表的正文数字** / **产物里的 `exposure.at_rank1`** /
**"不可算"那行被填成数字** / **"两臂同"被推翻** / **§2.13 节锚被改名**。
配三例**该绿**的：κ 变 true（测量完成不该让检查变红）、
只改 `exposure.definition`（正文不印的字段，证明检查读的是那 8 个格子而不是整块 blob）、
以及首尾两次原件全绿（证明上面这些不是恒红）。共 15 例 = 11 红 + 4 绿。

用法：`PYTHONIOENCODING=utf-8 .venv/Scripts/python.exe scripts/cbi_r11_matrix_negtest.py`
"""
import importlib.util
import json
import sys
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

print("[N12] 恢复原样 ⇒ 必须重新全绿（证明上面这些不是恒红）")
run("control-again", False)

print("\nRESULT:", "全部符合预期" if not fails else "FAIL -> " + ", ".join(fails))
sys.exit(1 if fails else 0)
