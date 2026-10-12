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
# Windows 控制台常见 cp936：产物落盘后才抛 UnicodeEncodeError 最难查（写了一半、退出码非零）。
for _stream in (sys.stdout, sys.stderr):
    if hasattr(_stream, "reconfigure"):
        _stream.reconfigure(errors="replace")


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


def run_chain(sc, calc, inst, n_extra, tmp, arm=None):
    """人工 = 照抄机判，再在随机层多标 n_extra 条 soft_leak，走完整链。

    `arm` 显式指定判分臂：一台仪器两把尺子时，κ 产物必须各自落盘（见 [4]）。
    """
    iv = sc._INSTRUMENTS[inst]
    arm = arm or iv["judge"]
    sc.INSTRUMENT = calc.INSTRUMENT = inst
    sc.SHEET_JSON, sc.JUDGE = CBI / iv["sheet_json"], CBI / arm
    # 计算器侧的两个全局量决定它去哪儿取凭证、以及凭证的臂必须等于什么：
    # κ 产物文件名 = (仪器, 判分臂) 两维，所以这里必须成对设置，不能只设 INSTRUMENT。
    calc.JUDGE_ARM = arm
    rows = json.loads(sc.SHEET_JSON.read_text(encoding="utf-8"))["rows"]
    verdict = {r["sample_id"]: r["machine_verdict"] for r in rows}
    for sid in [r["sample_id"] for r in rows if r["tier"] == "随机"][:n_extra]:
        verdict[sid] = "soft_leak"
    sc.LABELS = tmp / f"labels_{inst}_{arm}.json"
    sc.LABELS.write_text(json.dumps([{"sample_id": k, "human_verdict": v}
                                     for k, v in verdict.items()], ensure_ascii=False),
                         encoding="utf-8")
    # 名字由那两维规则现算，但**落盘位置必须在临时目录**：合成标注进仓库 = 自己糊闸门。
    sc.RESULT = tmp / sc.kappa_result_path(inst, arm).name
    assert sc.compute_kappa() == 0
    rep = tmp / f"reports_{inst}_{arm}"
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

        print("[4] 一台仪器两把尺子 ⇒ κ 产物按 (仪器, 判分臂) 两维命名，两臂共存、谁也不覆盖谁")
        art_r1, blk_r1 = run_chain(sc, calc, "v2", 0, tmp, arm="judge_v2_r1.jsonl")
        rep_r1 = tmp / "reports_v2_judge_v2_r1.jsonl"
        f_r1 = rep_r1 / art_r1["result_path"]
        bytes_r1 = f_r1.read_bytes()
        art_r2, blk_r2 = run_chain(sc, calc, "v2", 0, tmp, arm="judge_v2_r2.jsonl")
        f_r2 = tmp / "reports_v2_judge_v2_r2.jsonl" / art_r2["result_path"]
        check("两臂产物不同名", art_r1["result_path"] != art_r2["result_path"], True)
        check("名字里带着各自的臂",
              ("judge_v2_r1" in art_r1["result_path"], "judge_v2_r2" in art_r2["result_path"]),
              (True, True))
        check("先算的那一臂没有被后算的覆盖（字节级）", f_r1.read_bytes(), bytes_r1)
        check("两份各自登记了自己的判分臂",
              (art_r1["judge_arm"], art_r2["judge_arm"]),
              ("judge_v2_r1.jsonl", "judge_v2_r2.jsonl"))
        check("两臂的计算器读数都拿到自己的凭证（ok=True 而不是读不到）",
              (blk_r1.get("ok"), blk_r2.get("ok")), (True, True))
        # 关键负例：拿 r1 臂的凭证去问 r2 那一列过没过 —— 必须**读不到**，绝不能因为
        # "同目录里有个 κ 文件"就判过。旧命名（只按仪器）在这一格上会直接给 True。
        calc.REPORTS = rep_r1
        calc.JUDGE_ARM = "judge_v2_r2.jsonl"
        blk_foreign = calc.kappa_block()
        check("跨臂取凭证 ⇒ available=False、ok=False（失败关闭）",
              (blk_foreign.get("available"), blk_foreign.get("ok")), (False, False))

        print("[5] 负例 · 抽检单的机判列出自另一把尺子 ⇒ compute_kappa 拒绝出数")
        # v2 两臂逐行一致率实测 1.0000，真文件里挑不出不一致，所以在临时目录造一把"翻了 1 行"的尺子。
        # 翻的必须是**单子里真有的那一行**（500 行里只抽了 53 行）：随便翻 lines[0] 有 90% 概率
        # 翻在单子之外，那时守卫不响是**对的** —— 上一版就是这么"过"不了的。
        sc.SHEET_JSON = CBI / sc._INSTRUMENTS["v2"]["sheet_json"]   # 这张单子是 r1 臂烤出来的
        sids = {r["sample_id"] for r in json.loads(sc.SHEET_JSON.read_text(encoding="utf-8"))["rows"]}
        jlines = (CBI / "judge_v2_r2.jsonl").read_text(encoding="utf-8").splitlines()
        hit = next(i for i, s in enumerate(jlines)
                   if json.loads(s)["sample_id"] in sids)
        flip = json.loads(jlines[hit])
        flip["verdict"] = "hard_leak" if flip["verdict"] == "clean" else "clean"
        jlines[hit] = json.dumps(flip, ensure_ascii=False)
        fake = tmp / "judge_v2_r2_flipped.jsonl"
        fake.write_text("\n".join(jlines) + "\n", encoding="utf-8")
        sc.JUDGE = fake
        sc.RESULT = tmp / "kappa_must_not_be_written.json"
        fired = ""
        try:
            sc.compute_kappa()
        except SystemExit as e:
            fired = str(e)
        check("臂与单子不符 ⇒ 拒绝出数，并说明怎么修（重出 plan）",
              ("机判列与当前判分臂不符" in fired, "CBI_STAGE=plan" in fired), (True, True))
        check("守卫在写盘之前：没留下半份 κ 产物", sc.RESULT.exists(), False)

    check("运行后仓库里仍然没有人工标注/κ 产物", repo_artifacts(), 0)
    print("\nRESULT:", "全部通过" if not FAILS else "FAIL -> " + ", ".join(FAILS))
    return 1 if FAILS else 0


if __name__ == "__main__":
    raise SystemExit(main())
