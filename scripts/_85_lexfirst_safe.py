# -*- coding: utf-8 -*-
"""lex_first 家族「安全化」穷举（全局单/双参数）+ 可分离性判定。

已由 _85_loss_mechanism2.py 证实的核心机理：
  - 7 LOST：v6 的唯一 gold 落在融合 rank 4..6；lex 前 3 **全部非 gold**，
    hoist 把它们整体后移 3 位，gold 掉出前 6。其中 3 道 gold 本就在 rank 6
    —— hoist 任意 1 个非 gold 就必丢（纯结构性，任何推断信号都救不了）。
  - 7 GAINED：gold 恰是 lex 前 3 之一、且在融合 rank 9..14，
    必须 hoist 才能进前 6。

本脚本：
  1. 证明「lex 前 3 与融合前 6 的重合数」（共识信号）为何能分开两类；
  2. 穷举所有单参数 + 常见双参数安全规则；
  3. 判定是否存在能把 7 得与 7 失完全分开的全局单参数阈值（不可分离性证明）。
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

from compendium_rag import pipeline as P          # noqa: E402
from compendium_rag.config import get_settings    # noqa: E402
from _lex_channel_full import load_cases          # noqa: E402

R = ROOT / "data/compendium_rag/reports"
AUDIT = ROOT / "data/knowledge/_audit"
LEX_DEPTH = 30
SETS = {
    "300cn": (AUDIT / "rag_testset_300_cn.json", "rank_collect_v6c300_top30.json"),
    "blind": (AUDIT / "blind_v1/questions_strict.json", "rank_collect_v6cblind_top30.json"),
}
LOST7 = "R030 R043 R073 R080 R183 R242 R263".split()
GAIN7 = "R018 R052 R231 R241 R251 R268 R286".split()


def blob_of(c) -> str:
    return f"{c.text}\n{c.chapter_title}\n{c.scene_title}\n{c.part_title}"


def hoist(fused, lex, L):
    out, seen = [], set()
    for cid in lex[:L] + fused + lex:
        if cid not in seen:
            seen.add(cid)
            out.append(cid)
    return out


def load_all(kb):
    chunks = kb.retriever.chunks
    lexidx = kb.retriever.lex_index
    data = {}
    for setname, (spath, cfile) in SETS.items():
        cases = {c["qid"]: c for c in load_cases(spath)}
        coll = json.loads((R / cfile).read_text(encoding="utf-8"))
        rows = [r for r in coll["rows"] if r.get("mode") == "full" and r.get("answerable")]
        recs = []
        for r in rows:
            c = cases.get(r["qid"])
            if c is None:
                continue
            fused = [e["chunk_id"] for e in r["evidence"]]
            lex_hits = lexidx.search(c["q"], LEX_DEPTH)
            lex = [cid for cid, _ in lex_hits]
            sc = dict(lex_hits)
            pool = list(dict.fromkeys(fused[:30] + lex))
            gold = {cid for cid in pool
                    if chunks.get(cid) and any(k in blob_of(chunks[cid]) for k in c["keywords"])}
            s = [sc.get(cid, 0.0) for cid in lex[:6]] + [0.0] * 6
            f6 = set(fused[:6])
            recs.append({
                "qid": r["qid"], "fused": fused, "lex": lex, "gold": gold,
                "n_lex3_in_top6": sum(1 for cid in lex[:3] if cid in f6),
                "n_lexL_in_top6": {},
                "gap12": ((s[0] - s[1]) / s[0]) if s[0] > 0 else 0.0,
                "gap13": ((s[0] - s[2]) / s[0]) if s[0] > 0 else 0.0,
                "gap16": ((s[0] - s[5]) / s[0]) if s[0] > 0 else 0.0,
                "lex1_fused_rank": (fused.index(lex[0]) + 1) if lex and lex[0] in fused else 999,
                "n_gold_lex3": sum(1 for cid in lex[:3] if cid in gold),
                "v6_hit": any(cid in gold for cid in fused[:6]),
            })
        data[setname] = recs
        print(f"[{setname}] n={len(recs)}  v6 hit@6="
              f"{sum(1 for x in recs if x['v6_hit'])}")
    return data


def evaluate(data, decide, L=3):
    res = {}
    for setname, recs in data.items():
        newq = set()
        for x in recs:
            order = hoist(x["fused"], x["lex"], L) if decide(x) else x["fused"]
            if any(c in x["gold"] for c in order[:6]):
                newq.add(x["qid"])
        v6q = {x["qid"] for x in recs if x["v6_hit"]}
        res[setname] = {"h": len(newq), "n": len(recs),
                        "up": sorted(newq - v6q), "dn": sorted(v6q - newq)}
    return res


def main() -> int:
    kb = P.load_kb(get_settings())
    data = load_all(kb)

    print("\n" + "=" * 108)
    print("① 可分离性检查：14 道受影响题在候选信号上的取值")
    print("=" * 108)
    print(f"  {'qid':6} {'类':6} {'ngold@lex3':>10} {'lex3∩f6':>8} {'gap12':>8} "
          f"{'gap13':>8} {'gap16':>8} {'lex1_fr':>8}")
    byq = {x["qid"]: x for x in data["300cn"]}
    for tag, qs in (("GAIN", GAIN7), ("LOST", LOST7)):
        for q in qs:
            x = byq[q]
            print(f"  {q:6} {tag:6} {x['n_gold_lex3']:>10} {x['n_lex3_in_top6']:>8} "
                  f"{x['gap12']:>8.4f} {x['gap13']:>8.4f} {x['gap16']:>8.4f} "
                  f"{x['lex1_fused_rank']:>8}")

    print("\n  单信号可分性（同一阈值能否把 7 得全放行、7 失全拦掉）：")
    signals = ["n_gold_lex3", "n_lex3_in_top6", "gap12", "gap13", "gap16", "lex1_fused_rank"]
    sep_report = {}
    for sig in signals:
        gv = [byq[q][sig] for q in GAIN7]
        lv = [byq[q][sig] for q in LOST7]
        # 尝试 ">=" 与 "<=" 两个方向
        best = None
        for direction in (">=", "<="):
            vals = sorted({byq[q][sig] for q in set(GAIN7 + LOST7)})
            cands = [min(vals) - 1e-9] + vals if direction == ">=" else vals + [max(vals) + 1e-9]
            for t in cands:
                ok = lambda v: (v >= t) if direction == ">=" else (v <= t)
                if all(ok(v) for v in gv) and not any(ok(v) for v in lv):
                    best = (direction, t)
                    break
        sep_report[sig] = best
        print(f"    {sig:18} -> {'可分 ' + str(best) if best else '**不可分**'}")
    # oracle-ish: n_gold_lex3 is not deployable (uses gold). Note it.

    print("\n" + "=" * 108)
    print("② 可部署规则的穷举（只用推断可用信号）")
    print("=" * 108)
    results = []

    def run(tag, decide, L=3):
        r = evaluate(data, decide, L)
        a, b = r["300cn"], r["blind"]
        rec = {"tag": tag, "L": L,
               "h300": a["h"], "up300": len(a["up"]), "dn300": len(a["dn"]),
               "up300_ids": a["up"], "dn300_ids": a["dn"],
               "hblind": b["h"], "upblind": len(b["up"]), "dnblind": len(b["dn"])}
        results.append(rec)
        print(f"  {tag:38} 300cn {a['h']:>3}/{a['n']} (up{len(a['up'])}/dn{len(a['dn'])}) "
              f"{str(a['up'])[:26]:26} blind {b['h']:>3}/{b['n']} (up{len(b['up'])}/dn{len(b['dn'])})")
        return rec

    print("\n  [共识闸门 n_lex3_in_top6 >= k]  （k=0 等价于原 lex_first）")
    for L in (3, 4, 6):
        for k in (0, 1, 2, 3):
            run(f"consensus L={L} k={k}",
                lambda x, k=k, L=L: sum(1 for cid in x["lex"][:L]
                                        if cid in set(x["fused"][:6])) >= k, L)

    print("\n  [共识闸门，用 L 与 k 解耦：考察 lex 前 L 名，要求其中 ≥k 个已在融合前 6]")
    for L in (3, 4, 5, 6, 8, 10):
        for k in (1, 2, 3, 4):
            run(f"consensus2 L={L} k={k}",
                lambda x, k=k, L=L: sum(1 for cid in x["lex"][:L]
                                        if cid in set(x["fused"][:6])) >= k, L)

    print("\n  [分离度 × 共识 双闸门]")
    for t in (0.005, 0.01, 0.02, 0.03, 0.05, 0.08, 0.12):
        for k in (0, 1, 2):
            run(f"gap12>={t} & cons>= {k}",
                lambda x, t=t, k=k: x["gap12"] >= t and x["n_lex3_in_top6"] >= k)

    print("\n  [lex1 已在融合前 6：直接保持融合序（冗余 hoist 无意义）]")
    for L in (1, 3, 4, 6):
        run(f"skip-if-lex1-in-top6 L={L}",
                lambda x, L=L: x["lex1_fused_rank"] > 6, L)

    print("\n  [仅 hoist lex 前 L 中不在融合前 6 的，且数量受限]")
    for L in (3, 6):
        for cap in (1, 2, 3):
            def fn(x, L=L, cap=cap):
                notin = [cid for cid in x["lex"][:L] if cid not in set(x["fused"][:6])]
                return 0 < len(notin) <= cap
            run(f"notin-top6 1..{cap} of lex{L}", fn)

    out = {"separable_single_signal": sep_report, "results": results,
           "v6": {s: sum(1 for x in recs if x["v6_hit"]) for s, recs in data.items()},
           "note": "n_gold_lex3 使用 gold，仅用于可分离性上界诊断，不可部署"}
    dest = R / "_85_lexfirst_safe.json"
    dest.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\n-> {dest}")

    print("\n" + "=" * 108)
    print("③ 汇总：300cn >=167 的规则（按 dn300 升序，再按 h300/hblind 降序）")
    print("=" * 108)
    good = [r for r in results if r["h300"] >= 167]
    good.sort(key=lambda r: (r["dn300"], -r["h300"], -r["hblind"]))
    for r in good:
        print(f"  {r['tag']:38} 300cn {r['h300']} (up{r['up300']}/dn{r['dn300']})  "
              f"blind {r['hblind']} (up{r['upblind']}/dn{r['dnblind']})")
    if not good:
        print("  （无）")

    print("\n  最佳 dn300=0 且 h300 最高的规则：")
    z = [r for r in results if r["dn300"] == 0 and r["h300"] > 165]
    z.sort(key=lambda r: -r["h300"])
    for r in z[:10]:
        print(f"  {r['tag']:38} 300cn {r['h300']} (up{r['up300']}/dn{r['dn300']}) "
              f"up={r['up300_ids']}  blind {r['hblind']} (up{r['upblind']}/dn{r['dnblind']})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
