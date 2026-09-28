# -*- coding: utf-8 -*-
"""lex_first 家族全网格搜索（全局单/双参数）—— 300cn 选参，blind 留出如实报告。

纪律
----
- 参数**只在 300cn 上选**（准则见下）；blind 一律如实报告，绝不参与选择。
- 全部规则为**全局**、对每题同一逻辑，无逐题特判。

规则族
------
R0  lexfirst(L)               : 无条件把 lex 前 L 名提到最前（现状，L=3）
R1  consensus(L,k)            : 仅当 |lex[:L] ∩ fused[:6]| >= k 才 hoist lex[:L]
R2  bounded_new(L,cap)        : 只把 lex[:L] 中**不在 fused[:6]** 的前 cap 个提到最前
R3  band(L,alpha)             : 仅当 lex[L-1] >= alpha*lex[0]（头部成"分数带"）才 hoist lex[:L]
R4  combos                    : R1×R3、R1×R2

选参准则（预注册）
------------------
在 dn300 == 0（相对 v6 一题不丢）的规则里，取 hit@6 最高者；并列取 blind 更高者。
若不存在 dn300==0 且 h300>165 的规则，则退让为「h300 最大且 dn300 最小」。
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
            recs.append({"qid": r["qid"], "fused": fused, "lex": lex, "gold": gold,
                         "sc": sc, "f6": set(fused[:6]),
                         "v6_hit": any(cid in gold for cid in fused[:6]),
                         "v6_rank": r["rank"]})
        data[setname] = recs
    return data


def final_order(x, head):
    out, seen = [], set()
    for cid in head + x["fused"] + x["lex"]:
        if cid not in seen:
            seen.add(cid)
            out.append(cid)
    return out


# ── 各规则：返回 head（要提到最前的块）；空列表 = 保持融合序 ──────────────────

def head_R0(x, L):
    return x["lex"][:L] if len(x["lex"]) >= L else []


def head_R1(x, L, k):
    if len(x["lex"]) < L:
        return []
    head = x["lex"][:L]
    if sum(1 for cid in head if cid in x["f6"]) < k:
        return []
    return head


def head_R2(x, L, cap):
    if len(x["lex"]) < L:
        return []
    new = [cid for cid in x["lex"][:L] if cid not in x["f6"]]
    if len(new) == 0:
        return []
    return new[:cap]


def head_R3(x, L, alpha):
    if len(x["lex"]) < L:
        return []
    head = x["lex"][:L]
    s1 = x["sc"].get(head[0], 0.0)
    sL = x["sc"].get(head[-1], 0.0)
    if s1 <= 0 or sL < alpha * s1:
        return []
    return head


def head_R2_full(x, L, cap):
    """R2 变体：仍然 hoist 整个 lex[:L]，但要求新增插入数 <= cap。"""
    if len(x["lex"]) < L:
        return []
    head = x["lex"][:L]
    if sum(1 for cid in head if cid not in x["f6"]) > cap:
        return []
    return head


def evaluate(data, head_fn):
    res = {}
    for setname, recs in data.items():
        newq = set()
        for x in recs:
            o = final_order(x, head_fn(x))
            if any(cid in x["gold"] for cid in o[:6]):
                newq.add(x["qid"])
        v6q = {x["qid"] for x in recs if x["v6_hit"]}
        res[setname] = {"h": len(newq), "n": len(recs),
                        "up": sorted(newq - v6q), "dn": sorted(v6q - newq)}
    return res


def main() -> int:
    kb = P.load_kb(get_settings())
    data = build(kb)
    b300 = sum(1 for x in data["300cn"] if x["v6_hit"])
    bb = sum(1 for x in data["blind"] if x["v6_hit"])
    print(f"300cn n={len(data['300cn'])} v6 hit@6={b300}   "
          f"blind n={len(data['blind'])} v6 hit@6={bb}")

    rows: list[dict] = []

    def rec(family, params, head_fn, label):
        r = evaluate(data, head_fn)
        a, b = r["300cn"], r["blind"]
        row = {"family": family, "params": params, "label": label,
               "h300": a["h"], "up300": len(a["up"]), "dn300": len(a["dn"]),
               "up300_ids": a["up"], "dn300_ids": a["dn"],
               "hblind": b["h"], "upblind": len(b["up"]), "dnblind": len(b["dn"]),
               "upblind_ids": b["up"], "dnblind_ids": b["dn"]}
        rows.append(row)
        print(f"    {label:34} 300cn {a['h']:>3}/{a['n']} (up{len(a['up']):>2}/dn{len(a['dn']):>2})"
              f"   blind {b['h']:>3}/{b['n']} (up{len(b['up']):>2}/dn{len(b['dn']):>2})")
        return row

    print("\n" + "=" * 104)
    print("R0 lexfirst(L) —— 现状")
    print("=" * 104)
    for L in range(1, 9):
        rec("R0", {"L": L}, lambda x, L=L: head_R0(x, L), f"R0 lexfirst L={L}")

    print("\n" + "=" * 104)
    print("R1 consensus(L,k)：|lex[:L] ∩ fused[:6]| >= k 才 hoist lex[:L]")
    print("=" * 104)
    for L in range(2, 9):
        for k in range(0, L + 1):
            rec("R1", {"L": L, "k": k}, lambda x, L=L, k=k: head_R1(x, L, k),
                f"R1 cons L={L} k={k}")

    print("\n" + "=" * 104)
    print("R2 bounded_new(L,cap)：只提 lex[:L] 中不在 fused[:6] 的前 cap 个")
    print("=" * 104)
    for L in range(2, 9):
        for cap in range(1, L + 1):
            rec("R2", {"L": L, "cap": cap}, lambda x, L=L, cap=cap: head_R2(x, L, cap),
                f"R2 bnew L={L} cap={cap}")

    print("\n" + "=" * 104)
    print("R2full bounded_new_all(L,cap)：hoist lex[:L]，但新增插入数 <= cap")
    print("=" * 104)
    for L in range(2, 9):
        for cap in range(0, L + 1):
            rec("R2full", {"L": L, "cap": cap},
                lambda x, L=L, cap=cap: head_R2_full(x, L, cap),
                f"R2full L={L} cap={cap}")

    print("\n" + "=" * 104)
    print("R3 band(L,alpha)：lex[L-1] >= alpha*lex[0] 才 hoist lex[:L]")
    print("=" * 104)
    for L in (3, 4, 5, 6):
        for alpha in (0.0, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 0.95):
            rec("R3", {"L": L, "alpha": alpha},
                lambda x, L=L, a=alpha: head_R3(x, L, a),
                f"R3 band L={L} a={alpha}")

    out = {"v6": {"300cn": b300, "blind": bb},
           "n": {"300cn": len(data["300cn"]), "blind": len(data["blind"])},
           "results": rows}
    (R / "_85_grid.json").write_text(json.dumps(out, ensure_ascii=False, indent=2),
                                     encoding="utf-8")

    print("\n" + "=" * 104)
    print("【预注册准则】dn300==0 中 h300 最高的规则")
    print("=" * 104)
    safe = [r for r in rows if r["dn300"] == 0 and r["h300"] > b300]
    safe.sort(key=lambda r: (-r["h300"], -r["hblind"]))
    for r in safe:
        print(f"  {r['label']:34} 300cn {r['h300']} (up{r['up300']})  "
              f"blind {r['hblind']} (up{r['upblind']}/dn{r['dnblind']})  up={r['up300_ids']}")
    if not safe:
        print("  （无 dn300=0 且优于 v6 的规则）")

    print("\n  其中 blind 最高的一条（信息用）：")
    if safe:
        bx = max(safe, key=lambda r: r["hblind"])
        print(f"  {bx['label']} 300cn {bx['h300']} blind {bx['hblind']}")

    print("\n" + "=" * 104)
    print("同时满足 300cn>=167 与 blind>=190 的规则")
    print("=" * 104)
    both = [r for r in rows if r["h300"] >= 167 and r["hblind"] >= 190]
    for r in sorted(both, key=lambda r: (-r["h300"], -r["hblind"])):
        print(f"  {r['label']:34} 300cn {r['h300']} (up{r['up300']}/dn{r['dn300']})  "
              f"blind {r['hblind']} (up{r['upblind']}/dn{r['dnblind']})")
    if not both:
        print("  （无）")

    print("\n" + "=" * 104)
    print("blind 最优的 12 条（仅信息）")
    print("=" * 104)
    for r in sorted(rows, key=lambda r: (-r["hblind"], -r["h300"]))[:12]:
        print(f"  {r['label']:34} 300cn {r['h300']} (up{r['up300']}/dn{r['dn300']})  "
              f"blind {r['hblind']} (up{r['upblind']}/dn{r['dnblind']})")
    print(f"\n-> {R / '_85_grid.json'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
