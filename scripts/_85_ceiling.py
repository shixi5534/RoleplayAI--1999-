# -*- coding: utf-8 -*-
"""天花板分析：是否存在全局规则能「7 得全拿且 0 失」？以及 dn300=0 下的真实上界。

理论（命中集合视角）
--------------------
hit@6 只取决于**最终前 6 的集合**。把 lex 前 h 名提到最前，等价于：
  新增进前 6 的块 = lex[:h] 中**不在 fused[:6]** 的那些（记 n_new）；
  被挤出前 6 的 = fused[:6] 中排在最后的 n_new 个。
故对每题的「位移预算」有硬约束：
  - 若 v6 的 gold 在融合第 r 名（前 6 内唯一支撑），要保住它需 n_new <= 6-r；
  - 若 gold 在 lex 第 j 名且不在前 6，要吃进它需 h >= j（且 j <= 6）。

本脚本据此逐题算约束，并做**组合门控穷举**求 dn300=0 下的上界。
"""
from __future__ import annotations

import itertools
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


def blob_of(c):
    return f"{c.text}\n{c.chapter_title}\n{c.scene_title}\n{c.part_title}"


def build(kb):
    chunks, lexidx = kb.retriever.chunks, kb.retriever.lex_index
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
            lh = lexidx.search(c["q"], LEX_DEPTH)
            lex = [cid for cid, _ in lh]
            sc = dict(lh)
            pool = list(dict.fromkeys(fused[:30] + lex))
            gold = {cid for cid in pool
                    if chunks.get(cid) and any(k in blob_of(chunks[cid]) for k in c["keywords"])}
            f6 = fused[:6]
            # gold 在融合序中的名次 & 在 lex 序中的名次
            gfr = next((i + 1 for i, cid in enumerate(fused) if cid in gold), None)
            glr = next((i + 1 for i, cid in enumerate(lex) if cid in gold), None)
            recs.append({
                "qid": r["qid"], "fused": fused, "lex": lex, "gold": gold, "sc": sc,
                "f6": f6, "f6set": set(f6),
                "v6_hit": any(cid in gold for cid in f6),
                "gold_fused_rank": gfr, "gold_lex_rank": glr,
                "lex1_fr": (fused.index(lex[0]) + 1) if lex and lex[0] in fused else 999,
            })
        data[setname] = recs
    return data


def order_with_h(x, h):
    head = x["lex"][:h]
    out, seen = [], set()
    for cid in head + x["fused"] + x["lex"]:
        if cid not in seen:
            seen.add(cid)
            out.append(cid)
    return out


def hit(x, h):
    return any(cid in x["gold"] for cid in order_with_h(x, h)[:6])


def budget_table(data):
    print("=" * 112)
    print("位移预算表：hoist h 个 lex 前列时，保命/吃进 所需 h 的**可行区间**")
    print("=" * 112)
    print(f"  {'qid':7}{'类':6}{'gold_fr':>8}{'gold_lr':>8}{'n_new(h=1)':>11}"
          f"{'h 可行区间':>16}  说明")
    info = {}
    for qid in LOST7 + GAIN7:
        x = next(v for v in data["300cn"] if v["qid"] == qid)
        ok_h = [h for h in range(0, 7) if hit(x, h)]
        n_new1 = 0 if x["lex"][0] in x["f6set"] else 1
        info[qid] = {"ok_h": ok_h, "gold_fr": x["gold_fused_rank"],
                     "gold_lr": x["gold_lex_rank"], "n_new1": n_new1}
        tag = "LOST" if qid in LOST7 else "GAIN"
        note = ""
        if tag == "LOST":
            note = f"gold 在融合第 {x['gold_fused_rank']}，位移预算 {6-(x['gold_fused_rank'] or 0)}"
        else:
            note = f"gold 在 lex 第 {x['gold_lex_rank']}，需 h>={x['gold_lex_rank']} 才吃进"
        print(f"  {qid:7}{tag:6}{x['gold_fused_rank'] or 0:>8}{x['gold_lex_rank'] or 0:>8}"
              f"{n_new1:>11}{str(ok_h):>16}  {note}")
    print("\n  解读：")
    for q in LOST7 + GAIN7:
        tag = "LOST" if q in LOST7 else "GAIN"
        print(f"    {q} [{tag}] 使 hit 成立的 h = {info[q]['ok_h']}")
    return info


def main() -> int:
    kb = P.load_kb(get_settings())
    data = build(kb)
    info = budget_table(data)

    print("\n" + "=" * 112)
    print("矛盾证明：LOST 与 GAIN 的 h 约束是否相容（同一 h 只能取一个值）")
    print("=" * 112)
    lost_zero = [q for q in LOST7 if 0 in info[q]["ok_h"] and 1 not in info[q]["ok_h"]]
    gain_need1 = [q for q in GAIN7 if 0 not in info[q]["ok_h"]]
    print(f"  只接受 h=0 的 LOST（任何新增进前 6 就必丢）：{lost_zero}")
    print(f"  必须 h>=1 才能吃进的 GAIN：{gain_need1}")
    print(f"  => 二者直接冲突：全局规则对同题只能给一个 h。")

    # ── 组合门控穷举：gate = AND of up to 2 阈值条件；命中则 h=L，否则 h=0 ──
    print("\n" + "=" * 112)
    print("组合门控穷举（AND of ≤2 个阈值条件；通过则 hoist lex[:L]，否则保持 v6 序）")
    print("=" * 112)
    feats = {
        "gap12": lambda x: ((x["sc"].get(x["lex"][0], 0.0) - x["sc"].get(x["lex"][1], 0.0))
                            / x["sc"].get(x["lex"][0], 1.0)) if len(x["lex"]) > 1 else 0.0,
        "gap13": lambda x: ((x["sc"].get(x["lex"][0], 0.0) - x["sc"].get(x["lex"][2], 0.0))
                            / x["sc"].get(x["lex"][0], 1.0)) if len(x["lex"]) > 2 else 0.0,
        "cons3": lambda x: sum(1 for cid in x["lex"][:3] if cid in x["f6set"]),
        "cons5": lambda x: sum(1 for cid in x["lex"][:5] if cid in x["f6set"]),
        "cons6": lambda x: sum(1 for cid in x["lex"][:6] if cid in x["f6set"]),
        "new3": lambda x: sum(1 for cid in x["lex"][:3] if cid not in x["f6set"]),
        "freq1": lambda x: x["lex1_fr"],
        "s1": lambda x: x["sc"].get(x["lex"][0], 0.0) if x["lex"] else 0.0,
    }
    allrecs = [x for s in data.values() for x in s]
    thresholds = {}
    for name, fn in feats.items():
        vals = sorted({round(fn(x), 6) for x in allrecs})
        if len(vals) > 24:
            vals = vals[::max(1, len(vals) // 24)]
        thresholds[name] = vals

    cand_conds = []
    for name, vals in thresholds.items():
        for t in vals:
            cand_conds.append((name, ">=", t))
            cand_conds.append((name, "<=", t))
    print(f"  候选单条件 {len(cand_conds)} 个；AND 对 {len(cand_conds) * (len(cand_conds) - 1) // 2} 个")

    def mk_cond(name, op, t):
        fn = feats[name]
        if op == ">=":
            return lambda x, fn=fn, t=t: fn(x) >= t
        return lambda x, fn=fn, t=t: fn(x) <= t

    combos = [(c,) for c in cand_conds]
    for i in range(len(cand_conds)):
        for j in range(i + 1, len(cand_conds)):
            combos.append((cand_conds[i], cand_conds[j]))
    print(f"  合计 {len(combos)} 个门控（含单条件）")

    best = []
    for combo in combos:
        preds = [mk_cond(*c) for c in combo]
        for L in (3, 4, 5, 6):
            res = {}
            for setname, recs in data.items():
                newq = set()
                for x in recs:
                    h = L if all(p(x) for p in preds) else 0
                    if hit(x, h):
                        newq.add(x["qid"])
                v6q = {x["qid"] for x in recs if x["v6_hit"]}
                res[setname] = {"h": len(newq), "n": len(recs),
                                "up": sorted(newq - v6q), "dn": sorted(v6q - newq)}
            a, b = res["300cn"], res["blind"]
            if a["h"] >= 166:
                best.append({"gate": [list(c) for c in combo], "L": L,
                             "h300": a["h"], "up300": len(a["up"]), "dn300": len(a["dn"]),
                             "up300_ids": a["up"], "dn300_ids": a["dn"],
                             "hblind": b["h"], "dnblind": len(b["dn"])})

    safe = [r for r in best if r["dn300"] == 0]
    print(f"\n  评测完成；300cn >=166 的规则 {len(best)} 条，其中 dn300=0 的 {len(safe)} 条")
    print("\n  【dn300=0 且 300cn hit@6 最高】")
    for r in sorted(safe, key=lambda r: (-r["h300"], -r["hblind"]))[:15]:
        g = " & ".join(f"{c[0]}{c[1]}{c[2]}" for c in r["gate"])
        print(f"    L={r['L']}  [{g}]  -> 300cn {r['h300']} (up{r['up300']})  "
              f"blind {r['hblind']}  up={r['up300_ids']}")

    print("\n  【300cn>=167 且 dn300=0 的规则数】",
          len([r for r in safe if r["h300"] >= 167]))
    print("  【300cn>=169 且 dn300=0 的规则数】",
          len([r for r in safe if r["h300"] >= 169]))
    print("  【300cn>=170 且 dn300=0 的规则数】",
          len([r for r in safe if r["h300"] >= 170]))

    out = {"budget": info,
           "lost_zero_budget": lost_zero,
           "gain_need_h_ge_1": gain_need1,
           "safe_best": sorted(safe, key=lambda r: (-r["h300"], -r["hblind"]))[:40],
           "counts": {">=166 dn0": len(safe),
                      ">=167 dn0": len([r for r in safe if r["h300"] >= 167]),
                      ">=169 dn0": len([r for r in safe if r["h300"] >= 169]),
                      ">=170 dn0": len([r for r in safe if r["h300"] >= 170])},
           "v6": {"300cn": sum(1 for x in data["300cn"] if x["v6_hit"]),
                  "blind": sum(1 for x in data["blind"] if x["v6_hit"])}}
    (R / "_85_ceiling.json").write_text(json.dumps(out, ensure_ascii=False, indent=2),
                                        encoding="utf-8")
    print(f"\n-> {R / '_85_ceiling.json'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
