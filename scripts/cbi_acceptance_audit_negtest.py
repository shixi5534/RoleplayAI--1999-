# -*- coding: utf-8 -*-
"""验收审计的负向测试：这张"目标→证据"的表必须**能红**，而且红在该红的地方。

审计最容易犯的两种错：① 永远绿（没在读东西），② 永远红（读的东西与预期对不上却没人发现）。
所以这里两头都测：
  · 该红的 9 例，各自打在审计真会读的一条支路上：闸门键被删 / 旧子标准整块消失 /
    权重被改 / 分母被改 / 交付物缺失 / 测试集少一类题 / 图上出现 owner 边 /
    脚本里出现真实网络调用形状 / 裁决登记件被抽走；外加三例语义题：
    κ 产物存在但为 false ⇒ 必须是 **fail** 而不是"等人"（把失败洗成等人的那种写法要被抓），
    读数档位与现算不符 ⇒ 必须抓到（分档是独立复算的，不是抄 `gate` 字段）。
  · 该绿的 4 例：原件全绿且只挂 3 条 pending + 3 条 waived（`检索泄漏<=15` 那格永远不许是 pass）；
    把 κ 产物补成真 ⇒ pending 清零；
    扫描器不能被**自己的正则定义行**抓红（第一版就是自我误伤）。
所有破坏只打在系统临时目录的副本上；仓库原件与图 sha 前后必须一致。

用法：`PYTHONIOENCODING=utf-8 .venv/Scripts/python.exe scripts/cbi_acceptance_audit_negtest.py`
"""
from __future__ import annotations

import hashlib
import importlib.util
import json
import shutil
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
R = ROOT / "data" / "compendium_rag"
for _stream in (sys.stdout, sys.stderr):
    if hasattr(_stream, "reconfigure"):
        _stream.reconfigure(errors="replace")

N = 0
FAILS = []


def ck(name, got, want):
    global N
    N += 1
    if got != want:
        FAILS.append(name)
        print(f"  [FAIL] {name}: got={got!r} want={want!r}")
    else:
        print(f"  [ok]   {name} = {got!r}")


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()[:16]


def sandbox(tmp: Path, with_graph: bool = True):
    (tmp / "reports" / "cbi").mkdir(parents=True)
    (tmp / "docs" / "compendium-rag").mkdir(parents=True)
    (tmp / "scripts").mkdir(parents=True)
    for f in ("cbi_testset_500.json", "cbi_result_full.json",
              "cbi_result_v2instrument.json", "cbi_result_v2instrument_v2_r2.json"):
        shutil.copyfile(R / "reports" / f, tmp / "reports" / f)
    for f in ("spotcheck_sheet.json", "spotcheck_sheet_v2.json",
              "faithfulness_applicability.json"):
        shutil.copyfile(R / "reports" / "cbi" / f, tmp / "reports" / "cbi" / f)
    for f in ("P9_CBI报告.md", "entity_disambiguation_rules.md",
              "P10口径裁决_N_retrieval能力读数.md"):
        shutil.copyfile(ROOT / "docs" / "compendium-rag" / f,
                        tmp / "docs" / "compendium-rag" / f)
    shutil.copyfile(ROOT / "scripts" / "cbi_calculator.py",
                    tmp / "scripts" / "cbi_calculator.py")
    # 审计件里「标哪张表清哪一列」的表名是从这张注册表**现读**的（AST 取字面量），
    # 所以沙箱必须带上出表的那个脚本本身，否则审计会直接 fatal —— 而不是悄悄用一份旧表。
    shutil.copyfile(ROOT / "scripts" / "cbi_spotcheck.py",
                    tmp / "scripts" / "cbi_spotcheck.py")
    if with_graph:
        shutil.copyfile(R / "graph.json", tmp / "graph.json")
    spec = importlib.util.spec_from_file_location(
        "aud", ROOT / "scripts" / "cbi_acceptance_audit.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    m.ROOT, m.R = tmp, tmp
    m.REPORTS = tmp / "reports"
    m.CBI = tmp / "reports" / "cbi"
    m.OUT_JSON, m.OUT_MD = tmp / "out.json", tmp / "out.md"
    m.DELIVERABLES = [("cbi_testset_500.json", m.REPORTS / "cbi_testset_500.json"),
                      ("cbi_calculator.py", tmp / "scripts" / "cbi_calculator.py"),
                      ("P9_CBI报告.md", tmp / "docs" / "compendium-rag" / "P9_CBI报告.md"),
                      ("entity_disambiguation_rules.md",
                       tmp / "docs" / "compendium-rag" / "entity_disambiguation_rules.md")]
    m.READINGS = {k: m.REPORTS / p.name for k, p in m.READINGS.items()}
    return m


def patch(p: Path, mutate):
    d = json.loads(p.read_text(encoding="utf-8"))
    mutate(d)
    p.write_text(json.dumps(d, ensure_ascii=False), encoding="utf-8")


def result(m):
    items, problems = m.build()
    return items, problems, m.overall(items)


def failing_ids(items):
    return {x["id"] for x in items if x["status"] == "fail"}


def main() -> int:
    watched = [R / "graph.json", R / "reports" / "cbi_result_full.json",
               R / "reports" / "cbi_testset_500.json"]
    before = {p: sha(p) for p in watched}

    base = Path(tempfile.mkdtemp(prefix="aud_base_"))
    m = sandbox(base)
    items, problems, ov = result(m)
    print("[C] 原件 ⇒ 绿，且只挂三条 pending（人工 κ）")
    ck("problems 为空", problems, [])
    ck("达成 = False", ov["objective_achieved"], False)
    ck("pending 恰好是三列的 κ", len(ov["blocking"]), 3)
    ck("全部 pending 都是人工抽检那格",
       all("人工抽检" in b for b in ov["blocking"]), True)
    ck("无 fail", ov["failing"], [])
    ck("零云端记为 unverified 而不是 pass", ov["unverified"], ["D:零云端"])
    ck("审计确实覆盖了目标的六格（每列 6 条 gate 条目 + 1 条 legacy）",
       sum(1 for x in items if x["id"].startswith("gate:")), 3 * 7)
    ck("反空转：条目数够", len(items) >= 30, True)

    print("[N1] 删掉一个闸门键 ⇒ 双向相等必须炸")
    t = Path(tempfile.mkdtemp(prefix="aud_n1_"))
    m1 = sandbox(t)
    patch(m1.REPORTS / "cbi_result_full.json",
          lambda d: d["sub_criteria"].pop("N_soft<=5"))
    _, _, ov1 = result(m1)
    ck("出现 fail", "G:v1 × judge_full（终评列）" in " ".join(ov1["failing"]), True)

    print("[N2] 把旧子标准整块删掉（= 目标明列的那格从量具里消失）⇒ 必须炸")
    t = Path(tempfile.mkdtemp(prefix="aud_n2_"))
    m2 = sandbox(t)
    patch(m2.REPORTS / "cbi_result_v2instrument.json",
          lambda d: d.pop("legacy_sub_criteria"))
    _, _, ov2 = result(m2)
    ck("出现 fail", any("v2 × 尺子 v1" in f for f in ov2["failing"]), True)

    print("[N3] 权重被改 0.3→0.35 ⇒ 必须炸（不为达标调权重这条纪律的反向验证）")
    t = Path(tempfile.mkdtemp(prefix="aud_n3_"))
    m3 = sandbox(t)
    patch(m3.REPORTS / "cbi_result_full.json", lambda d: d["weights"].__setitem__("retrieval", 0.35))
    items3, _, _ = result(m3)
    ck("被点名的正是那一列", any("judge_full" in x for x in failing_ids(items3)), True)

    print("[N4] 分母 500→450 ⇒ 必须炸（不许改分母）")
    t = Path(tempfile.mkdtemp(prefix="aud_n4_"))
    m4 = sandbox(t)
    patch(m4.REPORTS / "cbi_result_full.json",
          lambda d: d["counts"].__setitem__("N_total_effective", 450))
    items4, _, _ = result(m4)
    ck("被抓到", any("judge_full" in x for x in failing_ids(items4)), True)

    print("[N5] 少一件交付物 ⇒ 必须炸")
    t = Path(tempfile.mkdtemp(prefix="aud_n5_"))
    m5 = sandbox(t)
    (t / "docs" / "compendium-rag" / "entity_disambiguation_rules.md").unlink()
    items5, prob5, _ = result(m5)
    ck("交付物条目为 fail", "D:entity_disambiguation_rules.md" in failing_ids(items5), True)
    ck("同时进 problems", any("交付物" in p for p in prob5), True)

    print("[N6] 测试集少一类题（把 100 条 style_probe 改成别的类型）⇒ 必须炸")
    t = Path(tempfile.mkdtemp(prefix="aud_n6_"))
    m6 = sandbox(t)
    def kill(d):
        for s in d["samples"]:
            if s["query_type"] == "style_probe":
                s["query_type"] = "inductive"
    patch(m6.REPORTS / "cbi_testset_500.json", kill)
    items6, _, _ = result(m6)
    ck("形状条目为 fail", "T:形状" in failing_ids(items6), True)

    print("[N7] 图上出现 owner 边 ⇒ 『零写图』必须炸")
    t = Path(tempfile.mkdtemp(prefix="aud_n7_"))
    m7 = sandbox(t)
    def add_owner(d):
        d["edges"][0]["owner"] = "某人"
    patch(t / "graph.json", add_owner)
    items7, _, _ = result(m7)
    ck("零写图条目为 fail", "X:零写图" in failing_ids(items7), True)

    print("[N8] 脚本里出现真实网络调用形状 ⇒ 零云端必须从 unverified 变 fail")
    t = Path(tempfile.mkdtemp(prefix="aud_n8_"))
    m8 = sandbox(t)
    (t / "scripts" / "cbi_sneaky.py").write_text(
        "from urllib.request import urlopen\n\ndef go(u):\n    return urlopen(u).read()\n",
        encoding="utf-8")
    items8, prob8, ov8 = result(m8)
    ck("零云端条目为 fail", "D:零云端" in failing_ids(items8), True)
    ck("不再挂 unverified", ov8["unverified"], [])

    print("[N9] κ 产物存在但 gate_pass=false ⇒ 必须是 fail，不许记成『等人』")
    t = Path(tempfile.mkdtemp(prefix="aud_n9_"))
    m9 = sandbox(t)
    nm9 = m9.kappa_name("v1", "judge_full.jsonl")
    (t / "reports" / nm9).write_text(
        json.dumps({"gate_pass": False, "instrument": "v1", "judge_arm": "judge_full.jsonl",
                    "result_path": nm9, "arm_A_random_only": {"n": 50, "kappa": 0.42}}),
        encoding="utf-8")
    items9, _, ov9 = result(m9)
    ck("该列 κ 记 fail",
       "gate:v1 × judge_full（终评列）:人工抽检 kappa>=0.80" in failing_ids(items9), True)
    ck("不再是 pending",
       any(b.endswith("kappa>=0.80") and b.startswith("gate:v1") for b in ov9["blocking"]),
       False)

    print("[N9b] κ 产物在**旧命名**（只按仪器命名）的位置、或出自别的判分臂 ⇒ 这一列不许记 pass，"
          "也不许记『等人出』；它是别人的凭证")
    t = Path(tempfile.mkdtemp(prefix="aud_n9b_"))
    m9b = sandbox(t)
    wrong = t / "reports" / m9b.kappa_name("v2", "judge_v2_r2.jsonl")
    wrong.write_text(json.dumps({"gate_pass": True, "instrument": "v2",
                                 "judge_arm": "judge_v2_r1.jsonl",   # 臂登记成了另一把尺子
                                 "result_path": wrong.name,
                                 "arm_A_random_only": {"n": 50, "kappa": 0.9}}),
                     encoding="utf-8")
    # 读数里把这一格改成 true（= 有人手抖或用了旧计算器）：审计必须因为凭证不可归属而判 fail
    patch(m9b.REPORTS / "cbi_result_v2instrument_v2_r2.json",
          lambda d: d["sub_criteria"].__setitem__("人工抽检 kappa>=0.80", True))
    items9b, _, ov9b = result(m9b)
    ck("臂不可归属 ⇒ 第三列不许 pass",
       any(x["id"] == "gate:v2 × 尺子 v2:人工抽检 kappa>=0.80" and x["status"] == "fail"
           for x in items9b), True)
    ck("也不许记成等人（blocking 里没有它）",
       any(b.startswith("gate:v2 × 尺子 v2:人工抽检") for b in ov9b["blocking"]), False)
    ck("另一臂那一列不受影响，仍是 pending",
       any(x["id"] == "gate:v2 × 尺子 v1:人工抽检 kappa>=0.80" and x["status"] == "pending"
           for x in items9b), True)

    print("[N9c] 凭证自报的文件名与实际不符（命名分叉）⇒ 同样不许过")
    t = Path(tempfile.mkdtemp(prefix="aud_n9c_"))
    m9c = sandbox(t)
    nm9c = m9c.kappa_name("v2", "judge_v2_r1.jsonl")
    (t / "reports" / nm9c).write_text(
        json.dumps({"gate_pass": True, "instrument": "v2", "judge_arm": "judge_v2_r1.jsonl",
                    "result_path": "cbi_spotcheck_kappa_v2.json",   # 自报了个旧名
                    "arm_A_random_only": {"n": 50, "kappa": 0.9}}), encoding="utf-8")
    patch(m9c.REPORTS / "cbi_result_v2instrument.json",
          lambda d: d["sub_criteria"].__setitem__("人工抽检 kappa>=0.80", True))
    items9c, _, _ = result(m9c)
    ck("命名分叉 ⇒ fail", any(x["id"] == "gate:v2 × 尺子 v1:人工抽检 kappa>=0.80"
                              and x["status"] == "fail" for x in items9c), True)

    print("[N10a] κ 产物补齐且 sub_criteria 也改了，但**读数没重跑**（gate 仍是旧判档）⇒ 必须炸："
          "这是『拿新产物配旧读数』那种假绿，审计不许让它过")
    t = Path(tempfile.mkdtemp(prefix="aud_n10a_"))
    m10 = sandbox(t)
    for inst, arm, g in (("v1", "judge_full.jsonl", "cbi_result_full.json"),
                        ("v2", "judge_v2_r1.jsonl", "cbi_result_v2instrument.json"),
                        ("v2", "judge_v2_r2.jsonl", "cbi_result_v2instrument_v2_r2.json")):
        nm = m10.kappa_name(inst, arm)
        (t / "reports" / nm).write_text(
            json.dumps({"gate_pass": True, "instrument": inst, "judge_arm": arm,
                        "result_path": nm,
                        "arm_A_random_only": {"n": 50, "kappa": 0.9, "degenerate": False,
                                              "observed_agreement": 1.0}}), encoding="utf-8")

    def clear_kappa(d):
        d["sub_criteria"]["人工抽检 kappa>=0.80"] = True
    for nm in ("cbi_result_full.json", "cbi_result_v2instrument.json",
               "cbi_result_v2instrument_v2_r2.json"):
        patch(t / "reports" / nm, clear_kappa)
    items10a, _, ov10a = result(m10)
    ck("pending 清零（产物在了，这一格不再是等人）", ov10a["blocking"], [])
    ck("但因为判档字符串与现算不符而 fail",
       sum(1 for f in ov10a["failing"] if f.startswith("G:")), 3)

    print("[N10b] 再把三列读数的 gate 一起更新（= 真的重跑过）⇒ 此时才允许『达成』")
    def retrack(d):
        d["gate"] = "发布"
    for nm in ("cbi_result_full.json", "cbi_result_v2instrument.json",
               "cbi_result_v2instrument_v2_r2.json"):
        patch(t / "reports" / nm, retrack)
    _, prob10b, ov10b = result(m10)
    ck("problems 为空", prob10b, [])
    ck("达成 = True（六格全绿 + 交付物齐；纪律的 unverified 不挡达成）",
       ov10b["objective_achieved"], True)

    print("[N11] 读数档位与现算不符（cbi 被改成 0.90 而 gate 仍写有条件发布）⇒ 必须炸")
    t = Path(tempfile.mkdtemp(prefix="aud_n11_"))
    m11 = sandbox(t)
    patch(m11.REPORTS / "cbi_result_full.json",
          lambda d: d["cbi"].__setitem__("measured", 0.90))
    items11, _, _ = result(m11)
    ck("被抓到", "G:v1 × judge_full（终评列）" in failing_ids(items11), True)

    print("[N12] 目标原文的 `检索泄漏<=15` 那格：实际 false ⇒ 只许记 `waived`（靠登记裁决），"
          "**永远不许记 pass**；把裁决登记件抽掉 ⇒ 必须立刻退回 fail")
    ck("对照：三列都记 waived 而不是 pass",
       sum(1 for x in items if x["id"].endswith(":legacy") and x["status"] == "waived"), 3)
    ck("对照：没有任何 legacy 行是 pass",
       any(x["id"].endswith(":legacy") and x["status"] == "pass" for x in items), False)
    ck("对照：waived 不计入 fail，所以此刻仍不算『目标原文全过』但也不阻塞",
       (ov["waived"] and not ov["failing"]) is True, True)
    t = Path(tempfile.mkdtemp(prefix="aud_n12_"))
    m12 = sandbox(t)
    patch(m12.REPORTS / "cbi_result_full.json",
          lambda d: d.__setitem__("caliber_adjudication", {}))
    items12, _, ov12 = result(m12)
    ck("裁决登记件没了 ⇒ 三列的该格全变 fail",
       sum(1 for f in ov12["failing"] if f.endswith(":legacy")), 3)
    ck("且不再有任何 waived", ov12["waived"], [])

    print("[C2] 原件再跑一次 ⇒ 必须回到只有三条 pending")
    items_c2, prob_c2, ov_c2 = result(sandbox(Path(tempfile.mkdtemp(prefix="aud_c2_"))))
    ck("control-again problems", prob_c2, [])
    ck("control-again blocking 数", len(ov_c2["blocking"]), 3)

    print("[N21] κ 命名三处实现（抽检 / 计算器 / 审计）必须逐字相等，且**同一仪器两臂不许同名**："
          "命名一分叉，计算器就找不到凭证 -> 失败关闭；同名则第二臂覆盖第一臂")

    def load_mod(mod_name, file_name):
        spec = importlib.util.spec_from_file_location(mod_name, ROOT / "scripts" / file_name)
        mm = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mm)
        return mm

    SPm, CA = load_mod("sp_for_n21", "cbi_spotcheck.py"), load_mod("calc_for_n21", "cbi_calculator.py")
    combos = [("v1", "judge_full.jsonl"), ("v1", "judge.jsonl"), ("v1", "judge2.jsonl"),
              ("v2", "judge_v2_r1.jsonl"), ("v2", "judge_v2_r2.jsonl")]
    ck("三处逐字相等（全部 5 个组合）",
       {(SPm.kappa_result_path(i, a).name, CA.kappa_artifact_path(i, a).name,
         m.kappa_name(i, a)) for i, a in combos},
       {(m.kappa_name(i, a), m.kappa_name(i, a), m.kappa_name(i, a)) for i, a in combos})
    ck("名字里带着臂：同一仪器两臂不许撞名",
       len({SPm.kappa_result_path("v2", a).name for a in
            ("judge_v2_r1.jsonl", "judge_v2_r2.jsonl")}), 2)
    # 反例（构造得出来才说明上面两条断言有变红的资格）：把计算器那一侧改回"只按仪器命名"，
    # 两臂就撞在同一个文件名上 —— 只改 tmp 副本，仓库原件一个字节都不动。
    t = Path(tempfile.mkdtemp(prefix="aud_n21_"))
    src = (ROOT / "scripts" / "cbi_calculator.py").read_text(encoding="utf-8")
    OLD = '''f"cbi_spotcheck_kappa_{instrument}_{judge_arm.removesuffix('.jsonl')}.json"'''
    NEW = '''f"cbi_spotcheck_kappa_{instrument}.json"'''
    mut = src.replace(OLD, NEW)
    assert mut != src, "命名变异没落地：原串对不上"
    (t / "calc_mut.py").write_text(mut, encoding="utf-8")
    spec = importlib.util.spec_from_file_location("calc_mut_n21", t / "calc_mut.py")
    CAm = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(CAm)
    try:
        ck("把计算器改回旧命名后，两臂确实撞在同一个文件名上",
           CAm.kappa_artifact_path("v2", "judge_v2_r1.jsonl").name
           == CAm.kappa_artifact_path("v2", "judge_v2_r2.jsonl").name, True)
        ck("且改过的命名与真计算器不再相等（所以 N21 第一条断言真的能红）",
           CAm.kappa_artifact_path("v2", "judge_v2_r2.jsonl").name
           == CA.kappa_artifact_path("v2", "judge_v2_r2.jsonl").name, False)
    finally:
        shutil.rmtree(t, ignore_errors=True)
    # 变异件是从 tmp 文件按**另一个模块名**加载的：真模块不许被它带跑。
    # 这一条守的是"负向测试自己污染了被测对象"这类事故（sys.modules 撞名时会发生）。
    ck("变异件加载后，真计算器的命名仍然与审计/抽检相等",
       (CA.kappa_artifact_path("v2", "judge_v2_r2.jsonl").name,
        SPm.kappa_result_path("v2", "judge_v2_r2.jsonl").name,
        m.kappa_name("v2", "judge_v2_r2.jsonl")),
       ("cbi_spotcheck_kappa_v2_judge_v2_r2.json",) * 3)

    ck("仓库三件原件未被动过",
       [str(p) for p, h in before.items() if sha(p) != h], [])
    print(f"\n[结果] 断言 {N} 条，失败 {len(FAILS)} 条")
    return 1 if FAILS else 0


if __name__ == "__main__":
    raise SystemExit(main())
