"""负向测试：MRR 基线的两处新断言必须能变红（缺字段不再静默补零、answerable 定义域要看得见）。"""
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
sys.path.insert(0, str(ROOT / "scripts"))
spec = importlib.util.spec_from_file_location("cc", ROOT / "scripts" / "cbi_calculator.py")
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

AUD = m.AUDIT_L2
REAL = json.loads(AUD.read_text(encoding="utf-8"))
fails = []


def with_audit(mutate):
    tmp = Path(tempfile.mkdtemp(prefix="cbi_mrr_pop_"))
    p = tmp / "audit_l2.json"
    d = json.loads(json.dumps(REAL))          # 深拷贝
    mutate(d)
    p.write_text(json.dumps(d, ensure_ascii=False), encoding="utf-8")
    m.AUDIT_L2 = p
    try:
        return m.baselines()
    finally:
        m.AUDIT_L2 = AUD


def check(name, got, want):
    ok = got == want
    if not ok:
        fails.append(name)
    print(("  ok   " if ok else "  FAIL ") + f"{name}: got={got!r} want={want!r}")


print("[C] 原件：三套值逐位不变 + 定义域断言")
base, prov = with_audit(lambda d: None)
check("三套 MRR 不变", base, {"300cn_full": 0.66528, "blind206_full": 0.6808,
                              "gen120_full": 0.82188})
pop = prov["mrr_population"]
check("answerable_only", pop["answerable_only"], True)
check("缺字段数", pop["n_missing_mrr_field"], 0)
check("含 mrr=0 的行数（300cn/blind/gen）",
      [pop["per_set"][s]["n_mrr_zero"] for s in ("300cn", "blind", "gen")], [23, 15, 0])
check("总行数 == 196+206+120", sum(v["n"] for v in pop["per_set"].values()), 522)
check("没有 mrr_incomplete 标记", "mrr_incomplete" in prov, False)

print("[N1] 把一行的 mrr@10 改成 null ⇒ 不能再被静默当 0：计数 + incomplete 标记")
base1, prov1 = with_audit(lambda d: d["per_case"][7].__setitem__("mrr@10", None))
check("缺字段计数=1", prov1["mrr_population"]["n_missing_mrr_field"], 1)
check("mrr_incomplete 有标记", "mrr_incomplete" in prov1, True)
check("300cn 均值只在 195 行上算（未被补零拉低）",
      prov1["mrr_population"]["per_set"]["300cn"]["n"], 195)
check("数值与原件不同（证明这一格真的会被缺数据影响）",
      base1["300cn_full"] != 0.66528, True)

print("[N2] 把一行的 mrr@10 改成字符串 ⇒ 同样算缺失，不能 int() 混过去")
base2, prov2 = with_audit(lambda d: d["per_case"][3].__setitem__("mrr@10", "0.5"))
check("非数值被计入缺失", prov2["mrr_population"]["n_missing_mrr_field"], 1)

print("[N3] 塞进一行 answerable=False ⇒ 排除出这一口径并计数（不悄悄混进均值）")
def add_unanswerable(d):
    row = json.loads(json.dumps(d["per_case"][0]))
    row["answerable"] = False
    row["mrr@10"] = 0.0
    row["qid"] = "synthetic-unanswerable"
    d["per_case"].append(row)

base3, prov3 = with_audit(add_unanswerable)
check("跳过数=1", prov3["mrr_population"]["n_unanswerable_rows_skipped"], 1)
check("answerable_only 变成 False（口径被破坏要可见）",
      prov3["mrr_population"]["answerable_only"], False)
check("三套数值不受这行影响", base3, base)

print("[N4] 删掉整套 gen 的行 ⇒ 必须整体拒绝，不能只报两套就继续判 ✅")
base4, prov4 = with_audit(lambda d: d.__setitem__(
    "per_case", [r for r in d["per_case"] if r.get("set") != "gen"]))
check("返回空基线（不可判）", base4, {})
check("error 说清缺哪套", "gen" in str(prov4.get("error", "")), True)

print("\nRESULT:", "全部符合预期" if not fails else "FAIL -> " + ", ".join(fails))
sys.exit(1 if fails else 0)
