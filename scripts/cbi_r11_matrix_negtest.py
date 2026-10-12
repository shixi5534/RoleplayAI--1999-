"""矩阵自检的负向测试：`cbi_r11_matrix_check` 必须能变红，而且破坏要打在**它真会读的东西**上。

§5-29 的教训在这一轮被当成设计约束用了：把破坏打在检查覆盖之外（改一个它不扫的字段、
改一条它不遍历的行），检查"抓不到"却什么也没说明，等于给它发一张没挣来的绿灯。
所以这里五例红分别打在这五条真实支路上：正文表里的数字串 / `ruler_v2.cbi` /
叠加列被塞进 MRR 字段 / 某仪器读数的 κ 变 true / κ 详情不再写"未达成"；
外加一例红打"报告 §4 不再指向 §R11"。
两头各留一次原件全绿（首尾各一遍），证明这五例不是恒红。

用法：`PYTHONIOENCODING=utf-8 .venv/Scripts/python.exe scripts/cbi_r11_matrix_negtest.py`
"""
import importlib.util
import json
import sys
from pathlib import Path

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

print("[N4] 某个仪器读数的 κ 变成 true（那 §R11『只差 κ』的立论就作废）⇒ 该红")
def load_kappa(name):
    d = REAL_LOAD(name)
    if name == "cbi_result_v2instrument.json":
        d["sub_criteria"]["人工抽检 kappa>=0.80"] = True
    return d
m.load = load_kappa
run("kappa-true", True)

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

print("[N7] 恢复原样 ⇒ 必须重新全绿（证明上面五例不是恒红）")
run("control-again", False)

print("\nRESULT:", "全部符合预期" if not fails else "FAIL -> " + ", ".join(fails))
sys.exit(1 if fails else 0)
