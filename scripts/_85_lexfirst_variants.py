# -*- coding: utf-8 -*-
"""lex_first 家族**全局单参数**变体离线扫描（300cn 调参 / blind 留出）。

数据源（不依赖 _85_channel_cache.json）：
  - v6 融合序：rank_collect_v6c{300,blind}_top30.json 的 evidence（已按最终融合序排列，
    rrf top_n = max(top_k*4,24) = 120，落盘截断到 30）；
  - lex 通道序 + 原始分：**生产 LexicalIndex**（kb.retriever.lex_index，与 collect 同源同参）。

为什么够用：lex_first 家族的所有规则都只对 (v6 融合序, lex 序) 做重排，
不改变任一通道本身，故无需重算 graph/mention/vector。

纪律：
  - 参数只在 300cn 上选；blind 为留出集，**任何参数都如实报告**，绝不用 blind 选参；
  - 全部为**全局单参数**规则，无逐题特判；
  - 只读：不动 graph/题集/src。

hit 判定（官方口径）：blob = f"{text}\\n{chapter}\\n{scene}\\n{part}"，
任一 eval_keyword 命中即该块为 gold；hit@6 = 最终序前 6 内存在 gold 块。
gold 只需在 (融合 top30 ∪ lex top30) 上判定 —— 因为最终序的成员只来自这两个集合。
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
LEX_DEPTH = 30          # 生产 lex_top 默认 30
POOL = 30               # collect 落盘的 evidence 深度

SETS = {
    "300cn": (AUDIT / "rag_testset_300_cn.json", "rank_collect_v6c300_top30.json"),
    "blind": (AUDIT / "blind_v1/questions_strict.json", "rank_collect_v6cblind_top30.json"),
}

LOST7 = "R030 R043 R073 R080 R183 R242 R263".split()
GAIN7 = "R018 R052 R231 R241 R251 R268 R286".split()


def blob_of(c) -> str:
    return f"{c.text}\n{c.chapter_title}\n{c.scene_title}\n{c.part_title}"


# ── 规则（全部返回最终 chunk_id 序列）────────────────────────────────────────

def rule_base(fused: list[str], lex: list[str], s: dict) -> list[str]:
    return fused


def rule_lexfirst(fused, lex, s, L: int = 3) -> list[str]:
    out, seen = [], set()
    for cid in lex[:L] + fused + lex:
        if cid not in seen:
            seen.add(cid)
            out.append(cid)
    return out


def rule_gated(fused, lex, s, L: int = 3, thr: float = 0.02,
               feat: str = "gap12") -> list[str]:
    """V1 置信闸门：lex 头部“足够分离”才 hoist，否则完全保持 v6 序。"""
    if len(lex) < 2:
        return list(fused)
    sc = s["lex_scores"]
    s1 = sc.get(lex[0], 0.0)
    s2 = sc.get(lex[1], 0.0)
    if s1 <= 0:
        return list(fused)
    if feat == "gap12":
        val = (s1 - s2) / s1
    elif feat == "ratio12":
        val = s2 / s1
    elif feat == "gap1L":
        sL = sc.get(lex[min(L, len(lex)) - 1], 0.0)
        val = (s1 - sL) / s1
    else:
        raise ValueError(feat)
    return rule_lexfirst(fused, lex, s, L) if val >= thr else list(fused)


def rule_v4(fused, lex, s, L: int = 3, top: int = 6) -> list[str]:
    """V4：只 hoist **不在融合 top-6 内**的 lex 前列（L = 最多考察 lex 前 L 名）。"""
    head = set(fused[:top])
    hoist = [cid for cid in lex[:L] if cid not in head]
    out, seen = [], set()
    for cid in hoist + fused + lex:
        if cid not in seen:
            seen.add(cid)
            out.append(cid)
    return out


def rule_v2_additive(fused, lex, s, L: int = 3) -> list[str]:
    """V2：融合序整体在前（top-6 成员一个不动），lex 前 L 名只用于**补位**。

    注意：融合序全部排在前 ⟹ 前 6 是融合前 6 的超集不变 ⟹ hit@6 与 v6 逐题相同，
    故 down=0 且 up=0（构造性证明）。保留此实现以证实该结论。
    """
    out, seen = [], set()
    for cid in fused + lex[:L]:
        if cid not in seen:
            seen.add(cid)
            out.append(cid)
    return out


def rule_v4b(fused, lex, s, L: int = 3, top: int = 6) -> list[str]:
    """V4b：hoist 非 top-6 的 lex 前列，但**只补到 6 个位置**（不挤走 beyond）。"""
    head = set(fused[:top])
    hoist = [cid for cid in lex[:L] if cid not in head]
    k = len(hoist)
    if k == 0:
        return list(fused)
    # 保留融合序的前 (top-k) 名，再把 hoist 插到最前
    keep = fused[:max(0, top - k)]
    out, seen = [], set()
    for cid in hoist + keep + fused + lex:
        if cid not in seen:
            seen.add(cid)
            out.append(cid)
    return out


def rule_lexfirst_keep(fused, lex, s, L: int = 3, keep: int = 6) -> list[str]:
    """把 lex 前 L 名提到最前，但**保留融合序前 keep 名**都在最终前 keep 内。

    实现：hoist 只取「不在 fused[:keep]」的，且 hoist 数不超过 keep，
    且被挤出的 fused[:keep] 成员补回到前 keep 的尾部 —— 保证集合不变（down=up=0）。
    """
    raise NotImplementedError


# ── 评估 ────────────────────────────────────────────────────────────────────

def build_set(setname: str, lex_index) -> dict:
    cases = {c["qid"]: c for c in load_cases(SETS[setname][0])}
    coll = json.loads((R / SETS[setname][1]).read_text(encoding="utf-8"))
    rows = [r for r in coll["rows"] if r.get("mode") == "full" and r.get("answerable")]
    chunks = lex_index  # placeholder
    return {"cases": cases, "rows": rows}


def main() -> int:
    s = get_settings()
    kb = P.load_kb(s)
    chunks = kb.retriever.chunks
    lexidx = kb.retriever.lex_index
    assert lexidx is not None, "生产 lex 索引缺失"
    print(f"[corpus] chunks={len(chunks)}  lex_index=ok  lex_top={s.lex_top}")

    data: dict[str, list[dict]] = {}
    for setname in SETS:
        cases = {c["qid"]: c for c in load_cases(SETS[setname][0])}
        coll = json.loads((R / SETS[setname][1]).read_text(encoding="utf-8"))
        rows = [r for r in coll["rows"]
                if r.get("mode") == "full" and r.get("answerable")]
        recs = []
        for r in rows:
            c = cases.get(r["qid"])
            if c is None:
                continue
            fused = [e["chunk_id"] for e in r["evidence"]]
            lex_hits = lexidx.search(c["q"], LEX_DEPTH)
            lex = [cid for cid, _sc in lex_hits]
            pool = list(dict.fromkeys(fused[:POOL] + lex))
            gold = set()
            for cid in pool:
                ch = chunks.get(cid)
                if ch and any(k in blob_of(ch) for k in c["keywords"]):
                    gold.add(cid)
            recs.append({"qid": r["qid"], "fused": fused, "lex": lex,
                         "lex_scores": dict(lex_hits), "gold": gold,
                         "v6_rank": r["rank"]})
        data[setname] = recs
        n = len(recs)
        v6h = sum(1 for x in recs if any(c in x["gold"] for c in x["fused"][:6]))
        poolh = sum(1 for x in recs if any(c in x["gold"] for c in x["fused"]))
        print(f"[{setname}] n={n}  v6 hit@6={v6h}  池内 hit@30={poolh}")

    results: list[dict] = []

    def ev(tag: str, fn) -> dict:
        out = {}
        for setname, recs in data.items():
            hits, q = 0, set()
            for x in recs:
                order = fn(x["fused"], x["lex"], x)
                if any(c in x["gold"] for c in order[:6]):
                    hits += 1
                    q.add(x["qid"])
            out[setname] = {"h": hits, "n": len(recs), "q": q}
        base = out["300cn"]["q"]
        b = data["300cn"]
        v6q = {x["qid"] for x in b if any(c in x["gold"] for c in x["fused"][:6])}
        up = sorted(out["300cn"]["q"] - v6q)
        dn = sorted(v6q - out["300cn"]["q"])
        bb = data["blind"]
        v6qb = {x["qid"] for x in bb if any(c in x["gold"] for c in x["fused"][:6])}
        upb = sorted(out["blind"]["q"] - v6qb)
        dnb = sorted(v6qb - out["blind"]["q"])
        rec = {"tag": tag, "h300": out["300cn"]["h"], "n300": out["300cn"]["n"],
               "hblind": out["blind"]["h"], "nblind": out["blind"]["n"],
               "up300": len(up), "dn300": len(dn),
               "up300_ids": up, "dn300_ids": dn,
               "upblind": len(upb), "dnblind": len(dnb),
               "upblind_ids": upb, "dnblind_ids": dnb}
        results.append(rec)
        print(f"  {tag:34} 300cn {rec['h300']:>3}/{rec['n300']} "
              f"(up{rec['up300']}/dn{rec['dn300']})   "
              f"blind {rec['hblind']:>3}/{rec['nblind']} (up{rec['upblind']}/dn{rec['dnblind']})")
        return rec

    print("\n" + "=" * 108)
    print("基线 + V3（lex_first L 扫描，L=1..6）")
    print("=" * 108)
    ev("v6 baseline (fused)", rule_base)
    for L in range(1, 7):
        ev(f"V3 lexfirst L={L}", lambda f, l, x, L=L: rule_lexfirst(f, l, x, L))

    print("\n" + "=" * 108)
    print("V4（只 hoist 不在融合 top-6 的 lex 前列）+ L 扫描")
    print("=" * 108)
    for L in range(1, 7):
        ev(f"V4 hoist-not-in-top6 L={L}", lambda f, l, x, L=L: rule_v4(f, l, x, L))
    for L in range(1, 7):
        ev(f"V4b notop6+keep L={L}", lambda f, l, x, L=L: rule_v4b(f, l, x, L))

    print("\n" + "=" * 108)
    print("V2（只增不减：融合序在前，lex 补位）—— 预期 up=0/dn=0")
    print("=" * 108)
    for L in (1, 3, 6):
        ev(f"V2 additive L={L}", lambda f, l, x, L=L: rule_v2_additive(f, l, x, L))

    print("\n" + "=" * 108)
    print("V1 置信闸门（feat=gap12=(s1-s2)/s1，L=3）阈值扫描")
    print("=" * 108)
    thr_gap = [0.0, 0.004, 0.005, 0.006, 0.008, 0.01, 0.012, 0.015, 0.02, 0.025,
               0.03, 0.035, 0.04, 0.05, 0.06, 0.07, 0.08, 0.1, 0.12, 0.15, 0.2, 0.3]
    for t in thr_gap:
        ev(f"V1 gap12>={t} L=3", lambda f, l, x, t=t: rule_gated(f, l, x, 3, t, "gap12"))

    print("\n" + "=" * 108)
    print("V1 置信闸门（feat=ratio12=s2/s1，L=3）阈值扫描（<= 触发）")
    print("=" * 108)
    for t in (0.99, 0.98, 0.97, 0.96, 0.95, 0.93, 0.9, 0.85, 0.8):
        def fn(f, l, x, t=t):
            if len(l) < 2:
                return list(f)
            sc = x["lex_scores"]
            s1, s2 = sc.get(l[0], 0.0), sc.get(l[1], 0.0)
            if s1 <= 0:
                return list(f)
            return rule_lexfirst(f, l, x, 3) if (s2 / s1) <= t else list(f)
        ev(f"V1 ratio12<={t} L=3", fn)

    print("\n" + "=" * 108)
    print("V1 置信闸门（feat=gap1L，L=3 / L=6）")
    print("=" * 108)
    for L in (3, 6):
        for t in (0.05, 0.1, 0.15, 0.2, 0.25, 0.3, 0.4, 0.5):
            ev(f"V1 gap1L>={t} L={L}",
               lambda f, l, x, t=t, L=L: rule_gated(f, l, x, L, t, "gap1L"))

    out = {"lex_depth": LEX_DEPTH, "pool": POOL, "results": results}
    dest = R / "_85_lexfirst_variants.json"
    dest.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\n-> {dest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
