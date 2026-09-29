# -*- coding: utf-8 -*-
"""R4-K01 摘除的**全量影响面**实测（内存模拟，不写盘、不改图）。

前一步已证 GA-25 闸门 PASS。本步回答：摘除 `诊疗@诊所` 对三套题集是否**零回归**？
只重跑可能受影响的题（种子集变化只可能来自含「诊疗」串的题），并报告 300cn/gen120
的子集差异；同时给出该别名在语料中的真实分布，佐证"死别名"定性。
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
s = get_settings()
kb = P.load_kb(s)
rets = kb.retriever
chunks = rets.chunks


def blob(cid: str) -> str:
    c = chunks.get(cid)
    return (f"{c.text}\n{c.chapter_title}\n{c.scene_title}\n{c.part_title}"
            if c else "")


def load_cases(path: Path) -> list[dict]:
    d = json.loads(path.read_text(encoding="utf-8"))
    rows = d if isinstance(d, list) else d.get("cases", [])
    out = []
    for r in rows:
        ev = r.get("evidence") or []
        kws = []
        for grp in ev:
            if isinstance(grp, list):
                kws += [k for k in grp if k]
            elif grp:
                kws.append(grp)
        if not kws:
            continue
        out.append({"qid": str(r.get("id")), "q": r.get("q", ""), "kws": kws})
    return out


SETS = {
    "300cn": ROOT / "data/knowledge/_audit/rag_testset_300_cn.json",
    "gen120": ROOT / "data/knowledge/_audit/rag_testset_gen_r1r2.json",
    "blind206": ROOT / "data/knowledge/_audit/blind_v1/questions_strict.json",
}


def run(cases: list[dict]) -> dict[str, dict]:
    out = {}
    for c in cases:
        clear_ppr_cache()
        r = rets.retrieve(c["q"], None, top_k=6, entity_link_top=6,
                          seed_threshold=0.34, lex_weight=1.0, lex_top=30,
                          rrf_k=1)
        order = [e.chunk_id for e in r.evidence]
        hit = any(any(k in blob(cid) for k in c["kws"]) for cid in order[:6])
        out[c["qid"]] = {"hit": hit, "seeds": [x.name for x in r.seeds][:6]}
    return out


# ── 语料层：'诊疗' 的真实分布（佐证"死别名/子串"）──
print("=" * 88)
print("① 语料层分布（'诊疗' 与 '诊所'）")
print("=" * 88)
for kw in (ALIAS, OWNER, "诊疗室"):
    n = sum(1 for cid in chunks if kw in blob(cid))
    print(f"   {kw!r:8} 命中块数 = {n}")

# ── 影响面：只测含 '诊疗' 的题（种子变化仅可能发生在这些题）──
focus_cases = []
for name, path in SETS.items():
    for c in load_cases(path):
        if ALIAS in c["q"]:
            focus_cases.append({**c, "set": name})
print(f"\n② 含『{ALIAS}』的题 = {len(focus_cases)}")
for c in focus_cases:
    print(f"   [{c['set']}] {c['qid']}: {c['q'][:56]}")

print("\n" + "=" * 88)
print("③ 摘除前 / 摘除后（仅内存）")
print("=" * 88)
before = run(focus_cases)
ent = rets.graph.entities[OWNER]
rets.graph.alias_index.pop(ALIAS, None)
ent.aliases = [a for a in ent.aliases if a != ALIAS]
after = run(focus_cases)

flips = 0
for c in focus_cases:
    q = c["qid"]
    b, a = before[q], after[q]
    same = b["hit"] == a["hit"]
    if not same:
        flips += 1
    print(f"   {q:10} hit {b['hit']} -> {a['hit']}   {'✓' if same else '⚠ 翻动'}")
    if b["seeds"] != a["seeds"]:
        print(f"              seeds: {b['seeds']} -> {a['seeds']}")

print()
print("=" * 88)
print("④ 判定")
print("=" * 88)
print(f"   翻动题数 = {flips}")
print(f"   -> {'零回归：可安全摘除' if flips == 0 else '存在回归：保持 keep_with_note'}")
print(f"   备注：摘除只改变含『诊疗』串的题的种子集；其余题集不受影响（别名索引键被移除）。")
