"""`cbi_spotcheck.py` 的 `label` stage（人工落标）正负例测试。

**只在系统临时目录里跑**：把 `LABELS` / `SHEET_JSON` 打桩到 temp，
所以仓库里绝不会因此出现 `spotcheck_labels*.json` —— 人工那一臂只能由人出，
在这里造出来的任何标注都只是为了验证解析器，不是测量数据。

用法：`PYTHONIOENCODING=gbk .venv/Scripts/python.exe scripts/cbi_labels_negtest.py`
（强制 gbk 是故意的：顺带验证 Windows 控制台编码不会让真流程在**文件已落盘之后**抛异常。）
"""
from __future__ import annotations

import importlib.util
import json
import os
import sys
import tempfile
from pathlib import Path
# Windows 控制台常见 cp936：产物落盘后才抛 UnicodeEncodeError 最难查（写了一半、退出码非零）。
for _stream in (sys.stdout, sys.stderr):
    if hasattr(_stream, "reconfigure"):
        _stream.reconfigure(errors="replace")


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
_spec = importlib.util.spec_from_file_location("cbi_spotcheck", ROOT / "scripts" / "cbi_spotcheck.py")
m = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(m)

TMP = Path(tempfile.mkdtemp(prefix="cbi_label_test_"))
SHEET = TMP / "sheet.json"
LAB = TMP / "labels.json"
ROWS = ([{"sample_id": f"C2-{i:03d}-direct", "tier": "随机"} for i in range(1, 51)]
        + [{"sample_id": f"C2-{i:03d}-style_probe", "tier": "争议"} for i in (22, 47)])
SHEET.write_text(json.dumps({"rows": ROWS}, ensure_ascii=False), encoding="utf-8")
m.SHEET_JSON, m.LABELS = SHEET, LAB

fails: list[str] = []


def check(name, got, want):
    ok = got == want
    if not ok:
        fails.append(name)
        print(f"  FAIL {name}\n        got  {got}\n        want {want}")
    else:
        print(f"  ok   {name}")


def run(labels=None, pre=None, reset=True):
    if reset:
        if pre is None:
            LAB.unlink(missing_ok=True)
        else:
            LAB.write_text(json.dumps(pre, ensure_ascii=False), encoding="utf-8")
    if labels is None:
        os.environ.pop("CBI_LABELS", None)
    else:
        os.environ["CBI_LABELS"] = labels
    try:
        rc = m.apply_labels()
    except SystemExit as e:
        return "EXIT", str(e)[:30]
    content = (json.loads(LAB.read_text(encoding="utf-8")) if LAB.exists() else None)
    return rc, ({p["sample_id"]: p["human_verdict"] for p in content} if content is not None else None)


print("[1] 合法：行号 + sample_id + 大小写/空格混写")
rc, got = run("12=soft_leak; C2-047-style_probe=Hard Leak")
check("rc=0", rc, 0)
check("两条落盘", got, {"C2-012-direct": "soft_leak", "C2-047-style_probe": "hard_leak"})

for nm, tok, why in (("[2] 非法 verdict", "12=soft_leak; 13=maybe", "13=maybe"),
                     ("[3] 缺 =", "12", "12"),
                     ("[4] 行号 0", "0=clean", "0=clean"),
                     ("[5] 行号越界", "53=clean", "53=clean"),
                     ("[6] 未知 sid", "C2-999-direct=clean", "C2-999-direct=clean")):
    rc, got = run(tok)
    check(f"{nm} ⇒ rc=1 且不写（{why}）", (rc, got), (1, None))

print("[7] 混合批：49 条合法 + 1 条非法 ⇒ 整批不落盘（最关键的一条）")
rc, got = run("; ".join([f"{i}=clean" for i in range(1, 50)] + ["50=typo"]))
check("rc=1 且一个字节都没写", (rc, got), (1, None))

print("[8] 没给 CBI_LABELS ⇒ SystemExit，不写")
check("SystemExit", run(None)[0], "EXIT")
check("未落盘", LAB.exists(), False)

print("[9] 分批合并：第二批不覆盖第一批；同键后者胜")
run("1=clean")
rc, got = run("2=soft_leak", reset=False)
check("两批共存", got, {"C2-001-direct": "clean", "C2-002-direct": "soft_leak"})
rc, got = run("1=hard_leak", reset=False)
check("同键后者胜", got["C2-001-direct"], "hard_leak")
check("没连带改掉别的行", got["C2-002-direct"], "soft_leak")

print("[10] 落盘顺序按抽检单行号，不按字母序")
rc, _ = run("5=clean; 3=clean; 4=clean")
check("按行号", [p["sample_id"] for p in json.loads(LAB.read_text(encoding="utf-8"))],
      ["C2-003-direct", "C2-004-direct", "C2-005-direct"])

print("[11] 旧标注里有不在本表上的 sid ⇒ 丢弃并 WARN（不静默吃人工测量）")
rc, got = run("10=clean", pre=[{"sample_id": "C9-001-direct", "human_verdict": "clean"},
                               {"sample_id": "C2-009-direct", "human_verdict": "soft_leak"}])
check("rc=0", rc, 0)
check("脏 sid 被丢", "C9-001-direct" in got, False)
check("好 sid 保住", got["C2-009-direct"], "soft_leak")

print("[12] 争议行的行号解析与卡片/宽表同源")
rc, got = run("52=clean")
check("第 52 行 = 第二条争议行", got, {"C2-047-style_probe": "clean"})

print("[13] 未填语法：? / tbd / none 被跳过并报数，不算错误")
rc, got = run("1=clean; 2=?; 3=tbd; 4=none; 5=hard_leak")
check("rc=0", rc, 0)
check("只落两条已定的", got, {"C2-001-direct": "clean", "C2-005-direct": "hard_leak"})

print("[14] 整段粘回文末答题块的样子（大部分 ? ，少数定了）⇒ 定的那些落盘")
rc, got = run("; ".join([f"{i}=?" for i in range(1, 20)] + ["7=soft_leak", "8=clean"]))
check("rc=0", rc, 0)
check("只落两条", got, {"C2-007-direct": "soft_leak", "C2-008-direct": "clean"})

print("[15] 全批未填且原本没有标注 ⇒ **不创建空文件**（空文件会被误读成'人标了但都 clean'）")
rc, got = run("1=?; 2=?; 3=?")
check("rc=0", rc, 0)
check("LABELS 不存在", LAB.exists(), False)

print("[16] 未填的行号打错也要当场说（键仍然校验，只是值不算标注）")
rc, got = run("999=?")
check("rc=1 且不写", (rc, got), (1, None))
rc, got = run("NOPE-SID=?")
check("rc=1（未知 sid 的未填项）", (rc, got), (1, None))

print("[17] 抽检单不存在 ⇒ SystemExit 且旧标注原样保住")
LAB.write_text(json.dumps([{"sample_id": "C2-001-direct", "human_verdict": "clean"}],
                          ensure_ascii=False), encoding="utf-8")
m.SHEET_JSON = TMP / "nope.json"
rc, _ = run("2=clean", reset=False)
check("SystemExit", rc, "EXIT")
m.SHEET_JSON = SHEET
check("旧标注未被动", json.loads(LAB.read_text(encoding="utf-8")),
      [{"sample_id": "C2-001-direct", "human_verdict": "clean"}])

print("\nRESULT:", "全部通过" if not fails else "FAIL -> " + ", ".join(fails))
print(f"（临时目录 {TMP}；仓库里 spotcheck_labels* 文件数应为 0）")
repo_labels = len(list((ROOT / "data/compendium_rag/reports/cbi").glob("spotcheck_labels*")))
print("仓库核查:", repo_labels)
sys.exit(1 if fails or repo_labels else 0)
