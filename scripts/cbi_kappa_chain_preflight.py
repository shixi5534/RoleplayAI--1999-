"""κ 链预检：证明"人工标注一到位，闸门就能正确读出"，而不用等真标完才发现意外。

为什么要有这个脚本：报告里"结论函数"给了容忍度（多抓 ≤5 过 / 6 条败），
但那只是抽检单生产端的算术。真闸门在另一个文件里（`cbi_calculator.kappa_block()`），
两边各存一份判据字符串，改一边忘一边就会让这一格变成"判据漂移 ⇒ 不判"。
这里把 `spotcheck → 产物 → calculator` 整链灌一遍。

**合成标注只写在系统临时目录**：人工那一臂的定义就是人怎么判，造标注进仓库 = 自己糊闸门。
运行前后都会断言仓库里 `spotcheck_labels*` / `cbi_spotcheck_kappa*` 的文件数为 0。

用法：`PYTHONIOENCODING=gbk .venv/Scripts/python.exe scripts/cbi_kappa_chain_preflight.py`
（强制 gbk 是故意的：这一步同时验证控制台编码不会让真流程在落盘后抛 UnicodeEncodeError。）
"""
from __future__ import annotations

import importlib.util
import json
import shutil
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CBI = ROOT / "data" / "compendium_rag" / "reports" / "cbi"
REPORTS = ROOT / "data" / "compendium_rag" / "reports"
sys.path.insert(0, str(ROOT / "scripts"))


def load(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / "scripts" / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


FAILS = []


def check(name, got, want):
    if got != want:
        FAILS.append(name)
    print(("  ok   " if got == want else "  FAIL ") + f"{name}   got={got!r} want={want!r}")


def repo_artifacts():
    return (len(list(CBI.glob("spotcheck_labels*")))
            + len(list(REPORTS.glob("cbi_spotcheck_kappa*"))))


def run_chain(sc, calc, inst, n_extra, tmp):
    """人工 = 照抄机判，再在随机层多标 n_extra 条 soft_leak，走完整链。"""
    iv = sc._INSTRUMENTS[inst]
    sc.INSTRUMENT = calc.INSTRUMENT = inst
    sc.SHEET_JSON, sc.JUDGE = CBI / iv["sheet_json"], CBI / iv["judge"]
    rows = json.loads(sc.SHEET_JSON.read_text(encoding="utf-8"))["rows"]
    verdict = {r["sample_id"]: r["machine_verdict"] for r in rows}
    for sid in [r["sample_id"] for r in rows if r["tier"] == "随机"][:n_extra]:
        verdict[sid] = "soft_leak"
    sc.LABELS = tmp / f"labels_{inst}.json"
    sc.LABELS.write_text(json.dumps([{"sample_id": k, "human_verdict": v}
                                     for k, v in verdict.items()], ensure_ascii=False),
                         encoding="utf-8")
    sc.RESULT = tmp / f"cbi_spotcheck_kappa{'_v2' if inst == 'v2' else ''}.json"
    assert sc.compute_kappa() == 0
    rep = tmp / f"reports_{inst}"
    rep.mkdir(exist_ok=True)
    shutil.copyfile(sc.RESULT, rep / sc.RESULT.name)
    calc.REPORTS = rep
    art = json.loads(sc.RESULT.read_text(encoding="utf-8"))
    return art, calc.kappa_block()


def main() -> int:
    check("运行前仓库里没有人工标注/κ 产物", repo_artifacts(), 0)
    sc, calc = load("cbi_spotcheck"), load("cbi_calculator")
    print("[0] 两个脚本各存一份的判据字符串")
    check("GATE_RULE == KAP_RULE（否则一落标就报漂移）", sc.GATE_RULE, calc.KAP_RULE)

    with tempfile.TemporaryDirectory(prefix="cbi_kappa_chain_") as td:
        tmp = Path(td)
        print("[1] v1 · 人工照抄机判 ⇒ 非退化，走 κ 线")
        art, blk = run_chain(sc, calc, "v1", 0, tmp)
        check("arm_A 的字段名被计算器认出来 (n=50)", blk.get("n"), 50)
        check("没有报判据漂移", "漂移" in blk.get("route", ""), False)
        check("计算器 ok=True", blk.get("ok"), True)
        check("产物 gate_pass 与计算器同值", art["gate_pass"], blk["ok"])
        check("v1 上字面 κ 规格线能给 True（让 v2 的『必然为假』可与坏掉区分）",
              art.get("gate_pass_strict_spec"), True)

        print("[2] v2 · 人工照抄机判 ⇒ 单一类别退化，走一致率线")
        art, blk = run_chain(sc, calc, "v2", 0, tmp)
        arm = art["arm_A_random_only"]
        check("退化被标出", arm["degenerate"], True)
        check("一致率 1.0", arm["observed_agreement"], 1.0)
        check("计算器 ok=True", blk.get("ok"), True)
        check("route 说明走的是退化线", "退化" in blk.get("route", ""), True)
        check("字面 κ 规格线在 v2 上为 False（定义含 not degenerate）",
              art.get("gate_pass_strict_spec"), False)

        print("[3] 负例 · 阈值方向没写反：多标 5 条过、6 条不过")
        a5, _ = run_chain(sc, calc, "v2", 5, tmp)
        a6, b6 = run_chain(sc, calc, "v2", 6, tmp)
        check("5 条 ⇒ 一致率 0.90", a5["arm_A_random_only"]["observed_agreement"], 0.9)
        check("5 条 ⇒ 产物过", a5["gate_pass"], True)
        check("6 条 ⇒ 一致率 0.88", a6["arm_A_random_only"]["observed_agreement"], 0.88)
        check("6 条 ⇒ 产物不过", a6["gate_pass"], False)
        check("6 条 ⇒ 计算器不过（整链一致）", b6.get("ok"), False)

    check("运行后仓库里仍然没有人工标注/κ 产物", repo_artifacts(), 0)
    print("\nRESULT:", "全部通过" if not FAILS else "FAIL -> " + ", ".join(FAILS))
    return 1 if FAILS else 0


if __name__ == "__main__":
    raise SystemExit(main())
