"""负向测试 `cbi_rules_doc_facts`：破坏必须打在它**真读的东西**上 —— 文档正文与四个产物。

三例改正文（簇数写错 / 退回过期表述 / 项数写旧值），三例改**产物副本**
（spec 项数 12→11、提案数 8→9、把 v2 的未过项改成通过），
首尾各一次原件全绿。产物那三例是关键：只把正文当断言对象的话，
"文档自洽但已与读数脱节"这种情况永远抓不到 —— 而那是这张交付物最可能的失效方式。
所有产物破坏都打在系统临时目录的副本上，仓库原件只读。

用法：`PYTHONIOENCODING=utf-8 .venv/Scripts/python.exe scripts/cbi_rules_doc_facts_negtest.py`
"""
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
spec = importlib.util.spec_from_file_location("rdf", ROOT / "scripts" / "cbi_rules_doc_facts.py")
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

REAL_R, REAL_DOC = m.R, m.DOC
FILES = ["p9_entity_census.json", "p9_entity_proposals.json",
         "cbi_result_full.json", "cbi_result_v2instrument.json"]
fails = []


def fresh(tmp):
    r = tmp / "reports"
    if r.exists():
        shutil.rmtree(r)
    r.mkdir(parents=True)
    for f in FILES:
        shutil.copyfile(REAL_R / f, r / f)
    m.R = r
    m.DOC = REAL_DOC
    return r


def run(name, want_red, doc_mutate=None, json_mutate=None):
    tmp = Path(tempfile.mkdtemp(prefix="rdf_neg_"))
    r = fresh(tmp)
    if doc_mutate:
        m.DOC = doc_mutate(m.DOC)
    if json_mutate:
        json_mutate(r)
    red = m.main() == 1
    print(("  ok   " if red == want_red else "  FAIL ") + f"{name}: 红={red} 期望={want_red}")
    if red != want_red:
        fails.append(name)
    shutil.rmtree(tmp, ignore_errors=True)


print("[C] 原件 ⇒ 绿")
run("control", False)

print("[D1] 正文把簇数写错（146→145）⇒ 红")
run("wrong-cluster-count", True, lambda d: d.replace("当前 146 簇", "当前 145 簇"))

print("[D2] 正文退回过期表述『把 11 项规格要求』⇒ 红")
run("stale-phrasing", True,
    lambda d: d.replace("把 **12 项**规格要求", "把 11 项规格要求"))

print("[J1] 产物里 spec 项数变成 11 ⇒ 正文那句 12 项就对不上，必须红")
def drop_check(r):
    p = r / "cbi_result_full.json"
    d = json.loads(p.read_text(encoding="utf-8"))
    checks = d["spec_conformance"]["checks"]
    checks.pop(list(checks)[0])
    p.write_text(json.dumps(d, ensure_ascii=False), encoding="utf-8")
run("artifact-spec-drift", True, json_mutate=drop_check)

print("[J2] 产物里提案数变成 9（正文仍写 8）⇒ 红")
def bump_prop(r):
    p = r / "p9_entity_proposals.json"
    d = json.loads(p.read_text(encoding="utf-8"))
    d["counts"]["entries"] = 9
    p.write_text(json.dumps(d, ensure_ascii=False), encoding="utf-8")
run("artifact-proposals", True, json_mutate=bump_prop)

print("[J3] 产物里把未过项改掉（v2 变成 12/12）⇒ 正文那句 'v2 读数 **11/12**' 必须红")
def fix_v2(r):
    p = r / "cbi_result_v2instrument.json"
    d = json.loads(p.read_text(encoding="utf-8"))
    for k in d["spec_conformance"]["checks"]:
        d["spec_conformance"]["checks"][k] = True
    p.write_text(json.dumps(d, ensure_ascii=False), encoding="utf-8")
run("artifact-quota-fixed", True, json_mutate=fix_v2)

print("[C2] 全部恢复 ⇒ 必须重新绿（证明上面几例不是恒红）")
m.R, m.DOC = REAL_R, REAL_DOC
run("control-again", False)

print("\nRESULT:", "全部符合预期" if not fails else "FAIL -> " + ", ".join(fails))
sys.exit(1 if fails else 0)
