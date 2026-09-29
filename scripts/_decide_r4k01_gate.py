# -*- coding: utf-8 -*-
"""R4-K01 预注册闸门实测（**不改图**，内存内模拟摘除别名）。

背景：R4-K01 = 死别名 `诊疗@诊所`。
  - 提案原判 keep_with_note（保留）
  - 2026-09-27 仲裁改为 remove（摘除），并**预注册闸门**：
      「摘除后置闸门：gen-120 复跑 GA-25 必须保持命中，破则回滚」
  - 该仲裁因 Applier fail-closed **未落盘**（NOT-APPLIED），故 live 图仍含 '诊疗'。

本脚本回答：**若真摘除，GA-25 是否仍命中？** 并同时量化对 300cn/盲测的影响面。
做法：加载 KB 后，从内存 alias_index 与实体别名表中摘掉 `诊疗@诊所`，
再跑 GA-25（及其它可能受影响的题），与未摘除基线逐题对比。

判据（照抄预注册）：GA-25 摘除后仍命中 → 可执行摘除；否则回滚（保持 keep_with_note）。
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

from compendium_rag import pipeline as P                      # noqa: E402
from compendium_rag.config import get_settings                # noqa: E402
from _r5_variant_scan import clear_ppr_cache                  # noqa: E402

ALIAS, OWNER = "诊疗", "诊所"
EVAL = ROOT / "data/compendium_rag/reports"

s = get_settings()
kb = P.load_kb(s)
rets = kb.retriever
chunks = rets.chunks

print(f"[graph] entities={len(rets.graph.entities)}")
ent = rets.graph.entities.get(OWNER)
print(f"[owner] {OWNER}.aliases = {ent.aliases if ent else 'MISSING'}")
print(f"[live]  graph.alias_index 含 {ALIAS!r} = {ALIAS in rets.graph.alias_index}")


def blob(cid: str) -> str:
    c = chunks.get(cid)
    return (f"{c.text}\n{c.chapter_title}\n{c.scene_title}\n{c.part_title}"
            if c else "")


def ask(q: str, kws: list[str]) -> dict:
    clear_ppr_cache()
    r = rets.retrieve(q, None, top_k=6, entity_link_top=6,
                      seed_threshold=0.34, lex_weight=1.0, lex_top=30,
                      rrf_k=1)
    order = [e.chunk_id for e in r.evidence]
    hit = any(any(k in blob(c) for k in kws) for c in order[:6])
    rr = 0.0
    for i, c in enumerate(order[:6], 1):
        if any(k in blob(c) for k in kws):
            rr = 1.0 / i
            break
    return {"hit": hit, "rr": rr, "seeds": [x.name for x in r.seeds][:6],
            "top6": order[:6]}


def load_cases(path: Path) -> list[dict]:
    d = json.loads(path.read_text(encoding="utf-8"))
    rows = d if isinstance(d, list) else d.get("cases", [])
    out = []
    for r in rows:
        ev = r.get("evidence") or []
        kws = [k for grp in ev for k in (grp if isinstance(grp, list) else [grp]) if k]
        out.append({"qid": str(r.get("id")), "q": r.get("q", ""), "kws": kws})
    return out


SETS = {
    "gen120": ROOT / "data/knowledge/_audit/rag_testset_gen_r1r2.json",
    "300cn": ROOT / "data/knowledge/_audit/rag_testset_300_cn.json",
    "blind206": ROOT / "data/knowledge/_audit/blind_v1/questions_strict.json",
}

# 焦点题：GA-25（闸门） + 任何含「诊疗」的题
focus: list[dict] = []
for name, path in SETS.items():
    for c in load_cases(path):
        if "诊疗" in c["q"] or c["qid"] == "GA-25":
            focus.append({**c, "set": name})
print(f"\n[focus] 含『诊疗』或 GA-25 的题 = {len(focus)}")
for c in focus:
    print(f"   [{c['set']}] {c['qid']}: {c['q'][:60]}")

print("\n" + "=" * 92)
print("① 基线（live 图：含 诊疗@诊所）")
print("=" * 92)
base = {}
for c in focus:
    r = ask(c["q"], c["kws"])
    base[c["qid"]] = r
    print(f"   {c['qid']:8} hit={r['hit']}  rr={r['rr']:.3f}  seeds={r['seeds']}")

# ── 内存内摘除别名 ──
print("\n" + "=" * 92)
print(f"② 模拟摘除 {ALIAS}@{OWNER}（仅内存，不写盘）")
print("=" * 92)
removed_idx = rets.graph.alias_index.pop(ALIAS, None)
if ent is not None:
    before_aliases = list(ent.aliases)
    ent.aliases = [a for a in ent.aliases if a != ALIAS]
print(f"   alias_index.pop({ALIAS!r}) -> {removed_idx}")
print(f"   {OWNER}.aliases: {before_aliases} -> {ent.aliases}")

after = {}
for c in focus:
    r = ask(c["q"], c["kws"])
    after[c["qid"]] = r
    print(f"   {c['qid']:8} hit={r['hit']}  rr={r['rr']:.3f}  seeds={r['seeds']}")

print("\n" + "=" * 92)
print("③ 闸门判定（预注册：GA-25 摘除后必须保持命中）")
print("=" * 92)
g = "GA-25"
if g in base and g in after:
    b, a = base[g]["hit"], after[g]["hit"]
    print(f"   GA-25 基线 hit={b} / 摘除后 hit={a}")
    print(f"   -> {'PASS：可执行摘除' if a else 'FAIL：必须回滚（保持 keep_with_note）'}")
for c in focus:
    q = c["qid"]
    if base[q]["hit"] != after[q]["hit"]:
        print(f"   ⚠ {q} 翻动: {base[q]['hit']} -> {after[q]['hit']}")
