"""交付物 `entity_disambiguation_rules.md` 的事实核对（纯只读）。

为什么要有：交付物四件里，报告有 §R11 矩阵自检、计算器与测试集各有自己的 spec 块，
只有这张规则表里的数字是**纯文字** —— 它引用了 6 个产物的读数（普查、提案、spec 项数、
κ 退化路线、判分尺子 v2 是否存在）。数字过期时不会报错，只会让下一个人按旧数行动
（本表确实过期过：§6 写"11 项规格断言"而 `spec_block` 已是 12 项，写"8 例人为破坏"而实为 14 例）。

用法：`PYTHONIOENCODING=utf-8 .venv/Scripts/python.exe scripts/cbi_rules_doc_facts.py`
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

# Windows 控制台常见 cp936：产物落盘后才抛 UnicodeEncodeError 最难查（写了一半、退出码非零）。
for _stream in (sys.stdout, sys.stderr):
    if hasattr(_stream, "reconfigure"):
        _stream.reconfigure(errors="replace")

ROOT = Path(__file__).resolve().parents[1]
R = ROOT / "data" / "compendium_rag" / "reports"
DOC = (ROOT / "docs" / "compendium-rag" / "entity_disambiguation_rules.md").read_text(encoding="utf-8")

# 过期表述要打到**具体句子**上，不能用宽泛子串：本表头部有一段"曾经写成 11 项、现已更正为 12 项"的
# 自省文字，用 "11 项规格" 这种短子串会把它误判成过期（负向测试的同一条纪律：断言要落在真被检查的东西上）。
STALE = ["把 11 项规格要求", "五条自守规则", "本轮 8 例人为破坏"]


def need(needle: str, why: str, fails: list[str]) -> None:
    if needle not in DOC:
        fails.append(f"{why}：正文里找不到 {needle!r}")


def main() -> int:
    fails: list[str] = []

    census = json.loads((R / "p9_entity_census.json").read_text(encoding="utf-8"))["counts"]
    kinds = census["b_family_kinds"]
    print(f"普查: clusters={census['b_clusters']} kinds={kinds} "
          f"entities={census['entities']} edges={census['edges']}")
    need(f"当前 {census['b_clusters']} 簇", "§4 簇总数与产物不符", fails)
    need(f"仅 **{kinds['cross_lang_alias'] + kinds['honorific_or_modifier']} 簇**",
         "§4 真别名簇数与产物不符", fails)
    need(f"其余 **{kinds['numbering']} 簇是编号群演**", "§4 编号群演数与产物不符", fails)
    if census["entities"] != 7033 or census["edges"] != 27110:
        fails.append(f"冻结图规模与产物不符：{census['entities']}/{census['edges']}")

    prop = json.loads((R / "p9_entity_proposals.json").read_text(encoding="utf-8"))["counts"]
    print(f"提案: {prop}")
    need(f"{prop['entries']} 条 `merge_entities`（tier_A {prop['tier_A']} / tier_B {prop['tier_B']}）"
         f"+ {prop['rejected']} 条拦截或判负留痕", "§7 提案数与产物不符", fails)

    spec_state = {}
    for name in ("cbi_result_full.json", "cbi_result_v2instrument.json"):
        sc = json.loads((R / name).read_text(encoding="utf-8"))["spec_conformance"]
        n = len(sc["checks"])
        passed = sum(1 for v in sc["checks"].values() if v)
        failed = [k for k, v in sc["checks"].items() if not v]
        spec_state[name] = (passed, n, failed)
        print(f"{name}: spec {passed}/{n} 未过={failed}")
        need(f"把 **{n} 项**规格要求", f"§6.5 的 spec 项数与产物不符（{name}）", fails)
    v1p, v1n, _ = spec_state["cbi_result_full.json"]
    v2p, v2n, v2failed = spec_state["cbi_result_v2instrument.json"]
    # 通过数也要对上：只核项数的话，"12 项"这句话在 12/12 与 11/12 两种状态下都一样绿
    need(f"v1 读数 **{v1p}/{v1n}** 全过", "§6.5 的 v1 通过数与产物不符", fails)
    need(f"v2 读数 **{v2p}/{v2n}**", "§6.5 的 v2 通过数与产物不符", fails)
    if v2failed and v2failed != ["四类冲突各 125 条（4 类折算）"]:
        fails.append(f"v2 未过项变了：{v2failed}（正文与 #14 的验收判据都要跟着改）")

    for f in ("判分尺子_CBI统一rubric.md", "判分尺子_CBI统一rubric_v2.md"):
        if not (ROOT / "docs" / "compendium-rag" / f).exists():
            fails.append(f"§9 引用的尺子文件不存在：{f}")
        need(f, f"正文未引用 {f}", fails)

    for s in STALE:
        if s in DOC:
            fails.append(f"正文仍有过期表述 {s!r}")

    print("\nRESULT:", "规则表的数字全部与产物一致" if not fails else "FAIL -> " + " | ".join(fails))
    return 1 if fails else 0


if __name__ == "__main__":
    raise SystemExit(main())
