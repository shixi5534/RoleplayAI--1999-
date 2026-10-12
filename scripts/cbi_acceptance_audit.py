# -*- coding: utf-8 -*-
"""目标 → 证据的验收审计（只读实算）。

为什么要有这个脚本：P9 的验收是一张六格的闸门表 + 四条交付物 + 三条纪律，
而我此前是**用散文**说"只差人工 κ 这一格"。散文会过期、会漏格、会把"没测"说成"过了"。
这里把目标里每一条明文要求映射到具体证据（文件字段/现算值），并把两件最容易出事的事
写成断言：
  1) **反缩水**：审计里预期的闸门键集合必须与各读数产物里实际出现的闸门键集合**双向相等**。
     任何一格从量具里消失（比如把 `N_retrieval<=15` 悄悄删掉），或量具新增一格而审计没覆盖，
     都立刻报红 —— 这条断言就是"不许把目标改成手边有的东西"的机器防线。
  2) **独立复算分档**：发布档位（≥0.97 / 0.94–0.97 / <0.94）由本脚本从 `cbi.measured`
     重新算一遍再与读数自己的 `gate` 字段比，不把读数的结论当凭证。

审计本身"绿"不等于目标达成：本脚本会显式区分
  `pass` / `fail` / **`pending`（要人来出，比如人工 κ）** / **`unverified`（只有过程约定，没有凭证）**。
用法：`PYTHONIOENCODING=utf-8 .venv/Scripts/python.exe scripts/cbi_acceptance_audit.py`
"""
from __future__ import annotations

import ast
import hashlib
import json
import re
import sys
from collections import Counter
from pathlib import Path

for _stream in (sys.stdout, sys.stderr):
    if hasattr(_stream, "reconfigure"):
        _stream.reconfigure(errors="replace")

ROOT = Path(__file__).resolve().parents[1]
R = ROOT / "data" / "compendium_rag"
REPORTS = R / "reports"
CBI = REPORTS / "cbi"
OUT_JSON = CBI / "acceptance_audit.json"
OUT_MD = CBI / "acceptance_audit.md"

FORMULA = "CBI = 1 - (1.0*N_hard + 0.5*N_soft + 0.3*N_retrieval)/N_total"
EXPECTED_GATE = {"N_hard==0", "N_soft<=5", "CBI>=0.97",
                 "MRR>=0.39 不回退", "Faithfulness>=0.98 不回退",
                 "人工抽检 kappa>=0.80"}
EXPECTED_LEGACY = {"N_retrieval<=15（旧子标准·已降级，照实报）"}
QTYPES = {"direct_private", "inductive", "multi_role", "multi_turn", "style_probe"}
FAMENTS = {"preference", "biography", "secret", "style"}
READINGS = {
    "v1 × judge_full（终评列）": REPORTS / "cbi_result_full.json",
    "v2 × 尺子 v1": REPORTS / "cbi_result_v2instrument.json",
    "v2 × 尺子 v2": REPORTS / "cbi_result_v2instrument_v2_r2.json",
}
DELIVERABLES = [
    ("cbi_testset_500.json", REPORTS / "cbi_testset_500.json"),
    ("cbi_calculator.py", ROOT / "scripts" / "cbi_calculator.py"),
    ("P9_CBI报告.md", ROOT / "docs" / "compendium-rag" / "P9_CBI报告.md"),
    ("entity_disambiguation_rules.md",
     ROOT / "docs" / "compendium-rag" / "entity_disambiguation_rules.md"),
]
BANNED_MODULES = ("compendium_rag.llm", "llm", "openai", "httpx", "requests",
                  "aiohttp", "urllib.request")
# 用 AST 而不是正则扫源码：正则会被**字符串字面量**骗到 ——
# 负向测试自己往临时文件里写 `return urlopen(u).read()` 当诱饵，
# 结果扫描器把那个 .py 文件里的字符串常量当成调用，审计红在了不该红的地方。
BANNED_CALLS = {"urlopen", "openai", "httpx", "requests"}


def _dotted(node) -> str:
    parts = []
    while isinstance(node, ast.Attribute):
        parts.append(node.attr)
        node = node.value
    if isinstance(node, ast.Name):
        parts.append(node.id)
    return ".".join(reversed(parts))


def network_hits(scripts_dir: Path) -> list:
    hits = []
    for p in sorted(scripts_dir.glob("cbi_*.py")):
        try:
            tree = ast.parse(p.read_text(encoding="utf-8"))
        except SyntaxError as e:
            hits.append(f"{p.name}: 解析失败 {e.msg}")
            continue
        for n in ast.walk(tree):
            if isinstance(n, ast.Import):
                for al in n.names:
                    if al.name in BANNED_MODULES or al.name.split(".")[0] in {"httpx", "requests", "openai", "aiohttp"}:
                        hits.append(f"{p.name}:{n.lineno} import {al.name}")
            elif isinstance(n, ast.ImportFrom):
                mod = n.module or ""
                if mod in BANNED_MODULES or mod.split(".")[0] == "compendium_rag" and mod.endswith("llm"):
                    hits.append(f"{p.name}:{n.lineno} from {mod} import ...")
            elif isinstance(n, ast.Call):
                head = _dotted(n.func).split(".")
                if any(h in BANNED_CALLS for h in head[:-1]) or head[0] in {"urlopen"}:
                    hits.append(f"{p.name}:{n.lineno} 调用 {_dotted(n.func)}()")
    return hits


def j(p: Path):
    return json.loads(p.read_text(encoding="utf-8"))


def sha16(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()[:16]


def band(v: float) -> str:
    """目标原文的分档（只看总式）。"""
    return "发布" if v >= 0.97 else ("0.94–0.97 ⇒ 有条件发布" if v >= 0.94 else "禁止发布")


def verdict(mode: str, sub: dict, v: float) -> str:
    """量具实际用的判档：总式 **∧ 六格子标准**（比原文更严）。
    本函数是 `cbi_calculator.py:703-705` 那条 `gate =` 表达式的**独立复刻**，
    用来核读数的 `gate` 字段是不是字符串级相等 —— 用 `in` 会因
    「发布」是「有条件发布」的子串而永远不报错（第一版就是这么漏的）。"""
    if mode == "retrieval_only":
        return "不可判（答案通道缺失）"
    if all(x is True for x in sub.values()):
        return "发布"
    return ("有条件发布 + 必须出 P10 修复计划" if v >= 0.94 else "禁止发布")


def row(items, rid, requirement, status, evidence, scope="acceptance"):
    """scope=acceptance 是目标的"验收"条款（达成与否看它）；
    scope=discipline 是纪律/过程条款：`fail` 同样阻塞，但 `unverified`
    只如实挂着（零云端这类只有静态凭证、没有运行时轨迹的，不许伪装成已证）。"""
    items.append({"id": rid, "requirement": requirement, "status": status,
                  "evidence": evidence, "scope": scope})
    return items[-1]


def build() -> tuple[list, list]:
    items, problems = [], []

    # ---- R1 交付物
    for name, p in DELIVERABLES:
        ok = p.exists() and p.stat().st_size > 0
        row(items, f"D:{name}", f"交付物 {name} 存在且非空",
            "pass" if ok else "fail",
            f"{p.relative_to(ROOT).as_posix()} size={p.stat().st_size if p.exists() else 0}"
            + (f" sha16={sha16(p)}" if ok else ""))
        if not ok:
            problems.append(f"交付物缺失或为空：{name}")

    # ---- R2/R3 测试集形状（明文：100 角色对 × 5 查询 = 500，四类冲突注入，只进上下文）
    ts = j(REPORTS / "cbi_testset_500.json")
    smp = ts["samples"]
    pairs = {(s["pair"]["a_eid"], s["pair"]["b_eid"]) for s in smp}
    per_pair = Counter((s["pair"]["a_eid"], s["pair"]["b_eid"]) for s in smp)
    qt = Counter(s["query_type"] for s in smp)
    fam = Counter(s["conflict_type"] for s in smp)
    shape_ok = (len(smp) == 500 and len(pairs) == 100
                and set(per_pair.values()) == {5} and set(qt) == QTYPES
                and set(fam) == FAMENTS
                and all(v == 100 for v in qt.values())
                and all(v == 125 for v in fam.values()))
    row(items, "T:形状", "测试集 = 100 角色对 × 5 类查询 = 500 样本；五类各 100、四类冲突族各 125",
        "pass" if shape_ok else "fail",
        f"samples={len(smp)} pairs={len(pairs)} per_pair={sorted(set(per_pair.values()))} "
        f"query_type={dict(qt)} conflict={dict(fam)}")
    if not shape_ok:
        problems.append("测试集形状与目标明文不符")
    inj = (ts.get("injection_policy") or "") + " " + (ts.get("schema") or "")
    pol_ok = bool(re.search(r"不写图", inj)) and ts.get("formula") == FORMULA
    row(items, "T:注入纪律", "对抗性冲突注入「只进上下文、不写图」且公式串与目标一致",
        "pass" if pol_ok else "fail",
        f"injection_policy 含『不写图』={bool(re.search(r'不写图', inj))} formula==目标串="
        f"{ts.get('formula') == FORMULA}")
    if not pol_ok:
        problems.append("注入政策或公式串与目标不符")

    # ---- R4/R6 三条判定通道与六格闸门
    kappa_files = {"v1 × judge_full（终评列）": REPORTS / "cbi_spotcheck_kappa.json",
                   "v2 × 尺子 v1": REPORTS / "cbi_spotcheck_kappa_v2.json",
                   "v2 × 尺子 v2": REPORTS / "cbi_spotcheck_kappa_v2.json"}
    for label, p in READINGS.items():
        if not p.exists():
            row(items, f"G:{label}", "读数产物存在", "fail", p.name)
            problems.append(f"缺读数 {p.name}")
            continue
        d = j(p)
        sub, leg = d["sub_criteria"], d.get("legacy_sub_criteria") or {}
        sym = set(sub) ^ EXPECTED_GATE
        sym_leg = set(leg) ^ EXPECTED_LEGACY
        c = d["counts"]
        w_ok = (d["weights"] == {"hard": 1.0, "soft": 0.5, "retrieval": 0.3}
                and d["formula"] == FORMULA
                and d["targets"]["cbi"] == 0.97 and d["targets"]["block_below"] == 0.94
                and d["targets"]["soft_max"] == 5 and d["targets"]["retrieval_max"] == 15
                and c["N_total_effective"] == 500)
        mine, theirs = verdict(d["mode"], sub, d["cbi"]["measured"]), d["gate"]
        band_ok = mine == theirs
        kp = kappa_files[label]
        kap_state = ("已测" if kp.exists() else "未测（无人工标注就没有 κ）")
        # 「待测」与「测了不过」必须是两种状态：κ 那格只有在**产物不存在**时才算 pending；
        # 产物存在而 false 就是 fail（否则这条闸门永远红不起来，等于把失败洗成等人）。
        gates = {}
        for k, v in sub.items():
            if v:
                gates[k] = "pass"
            elif k.startswith("人工抽检") and not kp.exists():
                gates[k] = "pending"
            else:
                gates[k] = "fail"
        all_ok = w_ok and not sym and not sym_leg and band_ok
        row(items, f"G:{label}", "六格闸门键集合与目标双向相等 + 权重/目标/分母一致 + 档位独立复算",
            "pass" if all_ok else "fail",
            f"CBI={d['cbi']['measured']} 现算档位={mine} 读数档位={theirs} "
            f"双向差={sorted(sym)} legacy 差={sorted(sym_leg)} "
            f"N={c['N_hard']}/{c['N_soft']}/{c['N_retrieval']}÷{c['N_total_effective']} "
            f"人工抽检={kap_state}({kp.name})")
        for k, st in gates.items():
            items.append({"id": f"gate:{label}:{k}", "requirement": f"闸门「{k}」",
                          "status": st, "scope": "acceptance",
                          "evidence": (f"读数 {p.name} 的 sub_criteria[{k}]="
                                       f"{json.dumps(sub[k])}；{d['sub_details'].get(k, '')}"[:220])})
        items.append({"id": f"gate:{label}:legacy",
                      "requirement": "闸门「检索泄漏 ≤3%(≤15/500)」——目标明列，已被 10-11 裁决降级，仍照实报",
                      "status": ("fail" if not list(leg.values()) else "pass"),
                      "scope": "acceptance",
                      "evidence": f"legacy_sub_criteria={json.dumps(leg, ensure_ascii=False)}；"
                                  f"能力读数（≤0.10）={json.dumps(d.get('capability_reading'), ensure_ascii=False)[:120]}"})
        if not all_ok:
            problems.append(f"{label}：闸门键/权重/档位核对不通过")

    # ---- 抽检规模 10%
    # 先说清一件事：目标原文的分档只看总式（≥0.97 ⇒ 发布），量具实际用的是
    # "总式 ∧ 六格子标准"，所以会出现"总式够、判档却更低"。这**不是**缩水（更严），
    # 但它是一次口径差异，必须挂在表上而不是藏在实现里。
    fr = j(REPORTS / "cbi_result_full.json")
    row(items, "V:档位口径", "分档口径：量具用「总式 ∧ 六格子标准」，比目标原文的纯总式分档更严",
        "pass" if fr["gate"] != band(fr["cbi"]["measured"]) else "na",
        f"终评列 CBI={fr['cbi']['measured']} ⇒ 按目标原文={band(fr['cbi']['measured'])}；"
        f"读数实际判档={fr['gate']}（差异来自"
        f"{sum(1 for v in fr['sub_criteria'].values() if v is not True)} 格子标准未过）")

    # ---- R5 抽检规模 10%
    for tag, f in (("v1", CBI / "spotcheck_sheet.json"), ("v2", CBI / "spotcheck_sheet_v2.json")):
        if not f.exists():
            row(items, f"S:{tag}", "10% 人工抽检单存在", "fail", f.name)
            problems.append(f"缺抽检单 {f.name}")
            continue
        rows = j(f)["rows"]
        rnd = sum(1 for x in rows if x.get("tier") == "随机")
        ok = rnd == 50
        row(items, f"S:{tag}", "人工抽检 = 500 的 10% ⇒ 随机层 50 条",
            "pass" if ok else "fail",
            f"{f.name} 共 {len(rows)} 行，随机层 {rnd}（另有非随机必看 "
            f"{len(rows) - rnd} 条不进 κ 分母）")
        if not ok:
            problems.append(f"{tag} 随机层不是 50")

    # ---- R8 纪律：零写图（图 sha 与各读数登记一致 + 无 owner/visibility 边）
    g_sha = sha16(R / "graph.json")
    declared = {j(p)["graph_sha"] for p in READINGS.values() if p.exists()}
    g = j(R / "graph.json")
    n_owner = sum(1 for e in g.get("edges") or []
                  if "owner" in e or "visibility" in e)
    graph_ok = declared == {g_sha} and n_owner == 0
    row(items, "X:零写图", "图未被改动：现场 sha16 与三处读数登记相等，且 owner/visibility 边仍为 0",
        "pass" if graph_ok else "fail",
        f"现场 {g_sha} / 读数登记 {sorted(declared)} / 边含 owner|visibility 的条数 {n_owner}"
        f"（边总数 {len(g.get('edges') or [])}）", scope="discipline")
    if not graph_ok:
        problems.append("图指纹与读数登记不一致，或出现了归属/可见性边")

    # ---- R8 纪律：零云端（只有静态凭证）
    hits = network_hits(ROOT / "scripts")
    row(items, "D:零云端", "判定与作答由盲子代理做、不调 LLM 网关",
        "fail" if hits else "unverified",
        "AST 扫描 scripts/cbi_*.py（只看真 import 与真调用，不被字符串字面量骗）：命中 "
        f"{len(hits)} 处 {hits[:3]}。**这只是静态凭证**：没有运行时网络轨迹或抓包，"
        "所以这条只能记『未证』，不能记『已证』", scope="discipline")
    if hits:
        problems.append(f"cbi 脚本里出现疑似网关调用：{hits[:3]}")

    # ---- R8 纪律：不改阈值/分母 —— 裁决登记件必须写明"未改公式/权重/分母"
    adj = j(REPORTS / "cbi_result_full.json").get("caliber_adjudication") or {}
    reg = ROOT / "docs" / "compendium-rag" / (adj.get("registered_in") or "x").split("/")[-1]
    unchanged = adj.get("unchanged") or []
    adj_ok = reg.exists() and any("公式" in u or "权重" in u for u in unchanged) \
        and any("分母" in u or "N_total" in u for u in unchanged)
    row(items, "X:未改口径", "检索格降级是**登记过的裁决**，且明文声明未改公式/权重/分母",
        "pass" if adj_ok else "fail",
        f"{reg.name} 存在={reg.exists()} unchanged="
        f"{json.dumps(unchanged, ensure_ascii=False)[:180]}", scope="discipline")
    if not adj_ok:
        problems.append("裁决登记件缺少『未改公式/分母』的声明")

    # ---- R9 「当前 0.84」不默认接受：必须由自建量具实测
    full = j(REPORTS / "cbi_result_full.json")
    lit = (full.get("both_calibers") or {}).get("literal") or {}
    rep = (ROOT / "docs" / "compendium-rag" / "P9_CBI报告.md").read_text(encoding="utf-8")
    base_ok = lit.get("available") and "0.84" in rep and str(lit.get("rate")) in rep
    row(items, "X:基线实测", "「当前 0.84」没有被默认接受，而是由自建量具实测出对照基线再报",
        "pass" if base_ok else "fail",
        f"字面口径实测 N_retrieval={lit.get('N_retrieval')} rate={lit.get('rate')} "
        f"上限={lit.get('ceiling_if_generation_perfect')}（报告里 0.84 出现="
        f"{'0.84' in rep}，rate 字符串在册={str(lit.get('rate')) in rep}）",
        scope="discipline")
    if not base_ok:
        problems.append("基线实测的证据在产物或报告里找不到")

    # ---- 适用域两条（§2.13 / §2.15 的产物必须存在且为 0）
    exp = j(REPORTS / "cbi_result_full.json")["both_calibers"]["control"].get("exposure") or {}
    fa_files = list(CBI.glob("faithfulness_applicability.json"))
    fa = j(fa_files[0]) if fa_files else []
    fa_zero = bool(fa) and all(
        sum(v for v in x["verbatim_in_corpus"].values()) == 0 and x["verbatim_in_top6"] == 0
        for x in fa)
    row(items, "X:适用域", "两格「不回退」都不由 CBI 集出数（MRR 危险度 / Faithfulness 无支撑域）",
        "pass" if (exp and fa_zero) else "fail",
        f"exposure 在册（n_gold={exp.get('n_gold_in_top6')}、at_rank1={exp.get('at_rank1')}、"
        f"warning={bool(exp.get('warning'))}）；faithfulness 适用域产物逐字命中全 0={fa_zero}",
        scope="discipline")
    if not (exp and fa_zero):
        problems.append("适用域证据不齐（exposure 或 faithfulness_applicability）")
    return items, problems


def overall(items) -> dict:
    """达成与否只看 acceptance 那一批；discipline 的 `fail` 同样阻塞，
    但 `unverified`（只有静态凭证的过程条款）不参与"达成"的计算 —— 
    它是被如实挂出来的，不是被删掉的。"""
    acc = [x for x in items if x["scope"] == "acceptance"]
    disc = [x for x in items if x["scope"] != "acceptance"]
    pend = [x for x in items if x["status"] == "pending"]
    bad = ([x for x in acc if x["status"] == "fail"]
           + [x for x in disc if x["status"] == "fail"])
    unver = [x for x in disc if x["status"] == "unverified"]
    return {"objective_achieved": not pend and not bad,
            "blocking": [x["id"] for x in pend],
            "failing": [x["id"] for x in bad],
            "unverified": [x["id"] for x in unver],
            "n_items": len(items),
            "n_acceptance": len(acc),
            "n_pass": sum(1 for x in items if x["status"] == "pass")}


def md(items, ov, problems) -> str:
    mark = {"pass": "✅", "fail": "❌", "pending": "⏳", "unverified": "❓", "na": "➖"}
    L = ["# P9 验收审计：目标 → 证据（只读实算）", "",
         f"条目 {ov['n_items']}（其中验收条款 {ov['n_acceptance']}）："
         f"通过 {ov['n_pass']}｜待人来出 {len(ov['blocking'])}｜"
         f"不符 {len(ov['failing'])}｜无凭证 {len(ov['unverified'])}。",
         f"**目标是否达成：{'是' if ov['objective_achieved'] else '否'}**"
         f"（阻塞：{', '.join(ov['blocking']) or '—'}；"
         f"不符：{', '.join(ov['failing']) or '—'}）", "",
         "| 状态 | 归属 | 条目 | 要求 | 证据 |", "| --- | --- | --- | --- | --- |"]
    for x in items:
        L.append(f"| {mark[x['status']]} {x['status']} | {x['scope']} | `{x['id']}` | "
                 f"{x['requirement']} | {x['evidence']} |")
    L += ["", "> 审计本身绿 ≠ 目标达成：`pending` 是要人出的那一格（人工 κ），"
          "`unverified` 是只有静态凭证、没有运行时轨迹的过程条款（零云端）。"
          "两者都如实挂在这里：不删、不改判成 pass。",
          "> 反缩水断言：审计预期的闸门键集合与各读数里实际出现的集合**双向相等**，"
          "任何一格从量具里消失或新增而未覆盖都会直接报红。"]
    if problems:
        L += ["", "## 审计发现的不符项", ""] + [f"- {p}" for p in problems]
    return "\n".join(L) + "\n"


def main() -> int:
    items, problems = build()
    ov = overall(items)
    OUT_JSON.write_text(json.dumps({"overall": ov, "problems": problems, "items": items},
                                   ensure_ascii=False, indent=1), encoding="utf-8")
    OUT_MD.write_text(md(items, ov, problems), encoding="utf-8")
    print(f"[审计] 条目 {ov['n_items']}：pass={ov['n_pass']} "
          f"pending={ov['blocking']} fail={ov['failing']} unverified={ov['unverified']}")
    print(f"[结论] 目标达成 = {ov['objective_achieved']}")
    print(f"[OK] 写出 {OUT_JSON.name} / {OUT_MD.name}")
    if problems:
        print("[FAIL] " + "\n[FAIL] ".join(problems))
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
