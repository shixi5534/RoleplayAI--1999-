# -*- coding: utf-8 -*-
"""R6 落盘后**冷启动**复评：GA-25 闸门 + 三集全量命中数对照（v7 -> v8）。

纪律（§4bis）：落盘后一律冷启动复评，禁暖进程自评。
本脚本在新进程内从磁盘重新加载图与索引，因此**天然冷启动**。
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

from compendium_rag import pipeline as P                       # noqa: E402
from compendium_rag.config import get_settings                 # noqa: E402
from _r5_variant_scan import clear_ppr_cache                   # noqa: E402

AUDIT = ROOT / "data/knowledge/_audit"
kb = P.load_kb(get_settings())
rets = kb.retriever
chunks = rets.chunks

print("=" * 84)
print("① 冷启动图状态")
print("=" * 84)
print(f"  entities = {len(rets.graph.entities)}")
print(f"  '诊疗' 仍在 graph.alias_index = {'诊疗' in rets.graph.alias_index}")
print(f"  诊所.aliases = {rets.graph.entities['诊所'].aliases}")


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
        kws: list[str] = []
        for grp in ev:
            if isinstance(grp, list):
                kws += [k for k in grp if k]
            elif grp:
                kws.append(grp)
        if kws:
            out.append({"qid": str(r.get("id")), "q": r.get("q", ""), "kws": kws})
    return out


SETS = {
    "300cn": AUDIT / "rag_testset_300_cn.json",
    "gen120": AUDIT / "rag_testset_gen_r1r2.json",
    "blind206": AUDIT / "blind_v1/questions_strict.json",
}

print()
print("=" * 84)
print("② GA-25 预注册闸门（新图冷启动）")
print("=" * 84)
ga = [c for c in load_cases(SETS["gen120"]) if c["qid"] == "GA-25"][0]
clear_ppr_cache()
r = rets.retrieve(ga["q"], None, top_k=6, entity_link_top=6,
                  seed_threshold=0.34, lex_weight=1.0, lex_top=30, rrf_k=1)
order = [e.chunk_id for e in r.evidence]
hit = any(any(k in blob(cid) for k in ga["kws"]) for cid in order[:6])
print(f"  seeds = {[s.name for s in r.seeds]}")
print(f"  GA-25 hit = {hit}")
print(f"  -> {'闸门 PASS（保持命中）' if hit else '闸门 FAIL（需回滚）'}")

print()
print("=" * 84)
print("③ 三集命中数：v8(本次) vs v7（对照既有工件，非重跑）")
print("=" * 84)
V7 = {"300cn": (167, 196), "blind206": (184, 206), "gen120": (118, 120)}
for name, path in SETS.items():
    cases = load_cases(path)
    # 只判 answerable：gold 关键词在当前语料中至少出现一次
    ans = [c for c in cases if any(k in "\n".join(
        blob(cid) for cid in list(chunks)[:0]) or True for k in c["kws"])]
    corpus = "\n".join(blob(cid) for cid in chunks)
    ans = [c for c in cases if any(k in corpus for k in c["kws"])]
    h = 0
    for c in ans:
        clear_ppr_cache()
        rr = rets.retrieve(c["q"], None, top_k=6, entity_link_top=6,
                           seed_threshold=0.34, lex_weight=1.0, lex_top=30,
                           rrf_k=1)
        o = [e.chunk_id for e in rr.evidence]
        if any(any(k in blob(cid) for k in c["kws"]) for cid in o[:6]):
            h += 1
    v7h, v7n = V7[name]
    mark = "✓ 一致" if (h, len(ans)) == (v7h, v7n) else f"⚠ 变化 {h}/{len(ans)}"
    print(f"  {name:9} v8 = {h}/{len(ans)} = {h/len(ans):.4f}   "
          f"v7 = {v7h}/{v7n} = {v7h/v7n:.4f}   {mark}")
