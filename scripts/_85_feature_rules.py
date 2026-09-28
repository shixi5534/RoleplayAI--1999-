# -*- coding: utf-8 -*-
"""为 lex_first 家族设计**全局单参数**安全规则：逐题特征 + 规则穷举。

核心矛盾（已由 _85_loss_mechanism2.py 证实）：
  - 7 道 LOST 的 v6 唯一 gold 落在融合 rank 4..6，被 hoist 的非 gold lex 前列整体后移；
    其中 3 道 gold 本来就在 rank 6 —— hoist 任意 1 个非 gold 就必丢（结构性，无信号可救）。
  - 7 道 GAINED 的 gold 恰是 lex top-1/2/3 之一，必须 hoist 才能进前 6。
  => 唯一可行的方向是找一个**推断可用**的全局信号，把"lex 头部含 gold"与
     "lex 头部是一簇非 gold 近邻/冗余"区分开。

本脚本：
  1. 逐题算一组**推断可用**特征（只用 lex 原始分、lex 名次、融合名次、章节标题——无 gold）；
  2. 对每条全局单阈值规则穷举阈值，报告 300cn hit@6 与 up/down；
  3. 只用 300cn 选，blind 如实报告。
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


def blob_of(c) -> str:
    return f"{c.text}\n{c.chapter_title}\n{c.scene_title}\n{c.part_title}"


def hoist(fused, lex, L):
    out, seen = [], set()
    for cid in lex[:L] + fused + lex:
        if cid not in seen:
            seen.add(cid)
            out.append(cid)
    return out


def build(kb) -> dict:
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

            # ── 推断可用特征（不看 gold）──
            s = [sc.get(cid, 0.0) for cid in lex[:6]]
            s1 = s[0] if s else 0.0
            s2 = s[1] if len(s) > 1 else 0.0
            s3 = s[2] if len(s) > 2 else 0.0
            ch3 = [chunks[cid].chapter_title if cid in chunks else "" for cid in lex[:3]]
            frag = {
                "gap12": ((s1 - s2) / s1) if s1 > 0 else 0.0,
                "ratio12": (s2 / s1) if s1 > 0 else 1.0,
                "gap13": ((s1 - s3) / s1) if s1 > 0 else 0.0,
                "n_chap3": len(set(ch3)),
                "n_lex3_in_top6": sum(1 for cid in lex[:3] if cid in set(fused[:6])),
                "lex1_fused_rank": (fused.index(lex[0]) + 1) if lex and lex[0] in fused else 999,
                "s1": s1,
                "n_gold_lex3": sum(1 for cid in lex[:3] if cid in gold),
            }
            recs.append({"qid": r["qid"], "fused": fused, "lex": lex,
                         "gold": gold, "f": frag})
        data[setname] = recs
        print(f"[{setname}] n={len(recs)}")
    return data


def score_rule(data, decide, L=3):
    """decide(frag) -> bool（是否 hoist lex 前 L）。返回各集 hit 与 up/dn。"""
    res = {}
    for setname, recs in data.items():
        v6q, newq = set(), set()
        for x in recs:
            if any(c in x["gold"] for c in x["fused"][:6]):
                v6q.add(x["qid"])
            order = hoist(x["fused"], x["lex"], L) if decide(x["f"]) else x["fused"]
            if any(c in x["gold"] for c in order[:6]):
                newq.add(x["qid"])
        res[setname] = {"h": len(newq), "n": len(recs), "q": newq,
                        "up": sorted(newq - v6q), "dn": sorted(v6q - newq)}
    return res


def main() -> int:
    kb = P.load_kb(get_settings())
    data = build(kb)
    base300 = score_rule(data, lambda f: False)
    print(f"\nbase 300cn {base300['300cn']['h']}/{base300['300cn']['n']}  "
          f"blind {base300['blind']['h']}/{base300['blind']['n']}")

    print("\n" + "=" * 112)
    print("逐题特征（会受 hoist 影响的 14 题 + 基线命中数）")
    print("=" * 112)
    watch = set("R030 R043 R073 R080 R183 R242 R263".split()
                + "R018 R052 R231 R241 R251 R268 R286".split())
    for setname in ("300cn",):
        for x in data[setname]:
            if x["qid"] in watch:
                f = x["f"]
                ingold = [i + 1 for i, c in enumerate(x["lex"][:3]) if c in x["gold"]]
                print(f"  {x['qid']}  gold@lex3={ingold or '-'}  gap12={f['gap12']:.4f} "
                      f"ratio12={f['ratio12']:.4f} gap13={f['gap13']:.4f} "
                      f"nchap3={f['n_chap3']} lex3intop6={f['n_lex3_in_top6']} "
                      f"lex1_fr={f['lex1_fused_rank']} s1={f['s1']:.2f}")

    results = []

    def run(tag, decide, L=3):
        r = score_rule(data, decide, L)
        a, b = r["300cn"], r["blind"]
        rec = {"tag": tag, "L": L, "h300": a["h"], "up300": len(a["up"]), "dn300": len(a["dn"]),
               "up300_ids": a["up"], "dn300_ids": a["dn"],
               "hblind": b["h"], "upblind": len(b["up"]), "dnblind": len(b["dn"])}
        results.append(rec)
        print(f"  {tag:40} 300cn {a['h']:>3}/{a['n']} (up{len(a['up'])}/dn{len(a['dn'])})   "
              f"blind {b['h']:>3}/{b['n']} (up{len(b['up'])}/dn{len(b['dn'])})")
        return rec

    print("\n" + "=" * 112)
    print("族 A：lex 头部分离度闸门（单阈值）")
    print("=" * 112)
    for feat, cmp in (("gap12", "ge"), ("gap13", "ge")):
        vals = sorted({round(x["f"][feat], 4) for s in data.values() for x in s})
        for t in vals:
            if cmp == "ge":
                run(f"A {feat}>={t} L=3", lambda f, feat=feat, t=t: f[feat] >= t)
            else:
                run(f"A {feat}<={t} L=3", lambda f, feat=feat, t=t: f[feat] <= t)

    print("\n" + "=" * 112)
    print("族 B：章节多样性（lex top-3 跨几个章节）")
    print("=" * 112)
    for t in (1, 2, 3):
        run(f"B n_chap3>={t} L=3", lambda f, t=t: f["n_chap3"] >= t)

    print("\n" + "=" * 112)
    print("族 C：lex top-3 与融合 top-6 的重合数")
    print("=" * 112)
    for t in (0, 1, 2, 3):
        run(f"C n_lex3_in_top6>={t} L=3", lambda f, t=t: f["n_lex3_in_top6"] >= t)

    print("\n" + "=" * 112)
    print("族 D：组合（分离度 × 章节多样性；分离度 × 重合数）")
    print("=" * 112)
    gaps = sorted({round(x["f"]["gap12"], 4) for s in data.values() for x in s})
    for t in gaps[::2]:
        for nc in (2, 3):
            run(f"D gap12>={t} & n_chap3>={nc} L=3",
                lambda f, t=t, nc=nc: f["gap12"] >= t and f["n_chap3"] >= nc)
    print()
    for t in gaps[::2]:
        for k in (0, 1, 2):
            run(f"D gap12>={t} & lex3intop6>={k} L=3",
                lambda f, t=t, k=k: f["gap12"] >= t and f["n_lex3_in_top6"] >= k)

    out = {"features": {s: [{"qid": x["qid"], **x["f"]} for x in recs]
                        for s, recs in data.items()},
           "results": results,
           "base": {s: {"h": v["h"], "n": v["n"]} for s, v in base300.items()}}
    dest = R / "_85_lexfirst_features.json"
    dest.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\n-> {dest}")

    print("\n" + "=" * 112)
    print("300cn >=167 且 dn300 最小的规则（按 dn300, -h300, hblind 排序）")
    print("=" * 112)
    good = [r for r in results if r["h300"] >= 167]
    good.sort(key=lambda r: (r["dn300"], -r["h300"], -r["hblind"]))
    for r in good[:25]:
        print(f"  {r['tag']:40} 300cn {r['h300']} (up{r['up300']}/dn{r['dn300']})  "
              f"blind {r['hblind']} (up{r['upblind']}/dn{r['dnblind']})")
    if not good:
        print("  （无）")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
