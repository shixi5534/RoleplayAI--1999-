# -*- coding: utf-8 -*-
"""Q1/Q2（精确版）：用**语料 + 生产 lex 索引**逐题复现 lex_first=3 的 7 失 7 得。

与 _85_loss_mechanism.py 的区别：本脚本不依赖 collect 文件里"是否落在 top30"的限制，
对每题重建 lex 前 30（生产 LexicalIndex，与 collect 的 lex 通道同源同参），
并计算精确 gold 集合，因此可以断言"被 hoist 的 3 块是不是 gold"。

只读：不动图、不动题集、不动 src。
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

from compendium_rag import pipeline as P            # noqa: E402
from compendium_rag.config import get_settings      # noqa: E402
from _lex_channel_full import load_cases            # noqa: E402

R = ROOT / "data/compendium_rag/reports"

LOST = "R030 R043 R073 R080 R183 R242 R263".split()
GAINED = "R018 R052 R231 R241 R251 R268 R286".split()


def blob_of(c) -> str:
    return f"{c.text}\n{c.chapter_title}\n{c.scene_title}\n{c.part_title}"


def main() -> int:
    kb = P.load_kb(get_settings())
    chunks = kb.retriever.chunks
    lex = kb.retriever.lex_index
    print(f"[corpus] chunks={len(chunks)}  lex_index={'ok' if lex else 'MISSING'}")

    cases = {c["qid"]: c for c in load_cases(ROOT / "data/knowledge/_audit/rag_testset_300_cn.json")}

    coll = json.loads((R / "rank_collect_v6c300_top30.json").read_text(encoding="utf-8"))
    recs = {r["qid"]: r for r in coll["rows"]
            if r.get("mode") == "full" and r.get("answerable")}

    out: dict = {"lost": {}, "gained": {}, "checks": {}}

    def analyze(qid: str, tag: str) -> None:
        c = cases.get(qid)
        r = recs.get(qid)
        if not c or not r:
            print(f"  !! {qid} missing case/row")
            return
        kws = c["keywords"]
        gold = {cid for cid, ch in chunks.items() if any(k in blob_of(ch) for k in kws)}
        rows = r["evidence"]
        v6_order = [e["chunk_id"] for e in rows]

        lex_hits = lex.search(c["q"], 30)
        lex_order = [cid for cid, _s in lex_hits]
        lex_scores = dict(lex_hits)
        hoisted = lex_order[:3]

        def first_gold(order):
            for i, cid in enumerate(order, start=1):
                if cid in gold:
                    return i
            return None

        lf_order, seen = [], set()
        for cid in hoisted + v6_order + lex_order:
            if cid not in seen:
                seen.add(cid)
                lf_order.append(cid)

        v6_rank = first_gold(v6_order)
        lf_rank = first_gold(lf_order)
        gold_lex_rank = None
        for i, cid in enumerate(lex_order, start=1):
            if cid in gold:
                gold_lex_rank = i
                break

        # v6 序里第 1 个 gold 块（= 决定 hit 的那个）
        gold_chunk_v6 = None
        for cid in v6_order:
            if cid in gold:
                gold_chunk_v6 = cid
                break

        rec = {
            "qid": qid, "query": c["q"], "keywords": kws, "n_gold": len(gold),
            "v6_rank": v6_rank, "lf_rank": lf_rank,
            "v6_gold_chunk": gold_chunk_v6,
            "v6_gold_chunk_lex_rank": (lex_order.index(gold_chunk_v6) + 1
                                       if gold_chunk_v6 in lex_order else None),
            "gold_lex_rank_first": gold_lex_rank,
            "hoisted": [{"chunk_id": cid, "lex_rank": i + 1,
                         "lex_score": round(lex_scores.get(cid, 0.0), 4),
                         "is_gold": cid in gold,
                         "v6_fused_rank": (v6_order.index(cid) + 1
                                           if cid in v6_order else None)}
                        for i, cid in enumerate(hoisted)],
            "v6_top6": v6_order[:6],
            "lf_top6": lf_order[:6],
            "v6_top6_gold": [cid in gold for cid in v6_order[:6]],
            "lf_top6_gold": [cid in gold for cid in lf_order[:6]],
            "lex_top3_scores": [round(s, 4) for _c, s in lex_hits[:3]],
            "lex_gap_s1s2": (round((lex_hits[0][1] - lex_hits[1][1]) / lex_hits[0][1], 4)
                             if len(lex_hits) >= 2 and lex_hits[0][1] > 0 else None),
        }
        out[tag][qid] = rec

        print(f"\n--- {qid} [{tag}] --- {c['q']}")
        print(f"    gold 块数={len(gold)}   v6 首个gold名次={v6_rank}  lex_first后={lf_rank}")
        print(f"    v6 gold 块 = {gold_chunk_v6}")
        print(f"    该 gold 块自身 lex 名次 = {rec['v6_gold_chunk_lex_rank']}   (lex 序中首个 gold = {gold_lex_rank})")
        print(f"    hoisted lex top3:")
        for h in rec["hoisted"]:
            print(f"        lex#{h['lex_rank']}  score={h['lex_score']:<9} gold={h['is_gold']!s:<5} "
                  f"v6fused#{h['v6_fused_rank']}  {h['chunk_id']}")
        print(f"    v6 top6 gold? {rec['v6_top6_gold']}")
        print(f"    lf top6 gold? {rec['lf_top6_gold']}")

    print("\n" + "=" * 100)
    print("LOST 7（v6 命中 -> lex_first=3 miss）")
    print("=" * 100)
    for q in LOST:
        analyze(q, "lost")
    print("\n" + "=" * 100)
    print("GAINED 7（v6 miss -> lex_first=3 命中）")
    print("=" * 100)
    for q in GAINED:
        analyze(q, "gained")

    # 一致性：离线复现 collect 的 v6 rank 与 rank_collect/官方数字
    bad = [q for q in list(out["lost"]) + list(out["gained"])
           if out["lost"].get(q, out["gained"].get(q))["v6_rank"] != recs[q]["rank"]]
    print(f"\n[check] v6_rank 与 collect rank 不一致的题：{bad}")
    out["checks"]["v6_rank_mismatch"] = bad

    # 7 题总体：确认机制
    mech = []
    for q in LOST:
        rec = out["lost"][q]
        mech.append({
            "qid": q,
            "v6_rank": rec["v6_rank"],
            "gold_lex_rank": rec["v6_gold_chunk_lex_rank"],
            "hoisted_all_nongold": all(not h["is_gold"] for h in rec["hoisted"]),
            "hoisted_gold_count": sum(1 for h in rec["hoisted"] if h["is_gold"]),
            "n_hoisted_present_in_v6": sum(1 for h in rec["hoisted"] if h["v6_fused_rank"]),
        })
    out["checks"]["mechanism"] = mech

    dest = R / "_85_lexfirst_diag.json"
    dest.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\n-> {dest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
