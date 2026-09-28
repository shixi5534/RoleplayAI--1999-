# -*- coding: utf-8 -*-
"""85% 目标：在**已验证**的离线重放数据上穷扫融合规则。

信任基础：_85_validate_replay.py 证明本重放器对 v6/L=3 在两集上**逐题一致**。

纪律：
  - 规则**只在 300cn 上选**；盲测 206 为**留出集**，如实报数；
  - 只做**全局单参数**改动，不做逐题特判；
  - 评分子集 = 官方 answerable 集合（保证与官方 eval 可比）。

本轮新扫前序未试的杠杆：
  A) RRF **k 常数**（前序只扫权重，未扫 k）
  B) 通道权重
  C) lex_first 的 L
  D) **非破坏式**变体：lex 前列只**补位**不**移位**（结构上保证 down=0）
  E) 置信度闸门：仅当 lex 分数分离时才 hoist
"""
from __future__ import annotations

import json
import math
from pathlib import Path

R = Path("data/compendium_rag/reports")
D = json.loads((R / "_85_replay_data.json").read_text(encoding="utf-8"))
K_RRF, TOPN = 60, 24


def official_ans(fname: str) -> set[str]:
    d = json.loads((R / fname).read_text(encoding="utf-8"))
    return {x["qid"] for x in d["rows"]
            if x.get("mode") == "full" and x.get("answerable")}


ANS = {"300cn": official_ans("eval_300cn_lex_tiebreak.json"),
       "blind": official_ans("eval_blind_lex_tiebreak.json")}
print(f"官方 answerable: 300cn={len(ANS['300cn'])}  blind={len(ANS['blind'])}")


def fuse(rec, weights, k=K_RRF, top_n=TOPN) -> list[str]:
    agg = {}
    for cid, chans in rec["per"].items():
        agg[cid] = sum(weights.get(ch, 1.0) * (1.0 / (k + rk))
                       for ch, rk in chans.items())
    return sorted(agg, key=lambda c: (-agg[c], c))[:top_n]


def base_order(rec):
    return fuse(rec, {"lex": 1.0})


def hit(order, gold):
    return any(c in gold for c in order[:6])


# ---------- 规则变体 ----------

def r_lexfirst(rec, L):
    """现行 lex_first：把 lex 前 L 名**移到最前**（破坏性）。"""
    if L <= 0:
        return base_order(rec)
    out, seen = [], set()
    for cid in rec["lex_order"][:L] + base_order(rec) + rec["lex_order"]:
        if cid not in seen:
            seen.add(cid); out.append(cid)
    return out


def r_additive(rec, L):
    """非破坏式：融合序**原样保留在前**，lex 前列只补融合序没有的块。

    结构上保证：前 6 位不因 hoist 而改变 → 300cn down 恒为 0。
    但 up 也只在"融合序前 6 有空缺"时才可能发生 → 需实测。
    """
    base = base_order(rec)
    out, seen = [], set()
    for cid in base:
        if cid not in seen:
            seen.add(cid); out.append(cid)
    for cid in rec["lex_order"][:L]:
        if cid not in seen:
            seen.add(cid); out.append(cid)
    return out


def r_interleave(rec, L, stride=2):
    """交错：融合序第 1 名，然后 lex 前 L 名逐个插入，其余按融合序。"""
    base = base_order(rec)
    lex_top = rec["lex_order"][:L]
    out, seen = [], set()
    li = 0
    for i, cid in enumerate(base):
        if cid not in seen:
            seen.add(cid); out.append(cid)
        if (i + 1) % stride == 0 and li < len(lex_top):
            c = lex_top[li]; li += 1
            if c not in seen:
                seen.add(c); out.append(c)
    while li < len(lex_top):
        c = lex_top[li]; li += 1
        if c not in seen:
            seen.add(c); out.append(c)
    return out


def r_gate(rec, L, ratio_thr):
    """置信度闸门：仅当 lex 分数分离够大时才 hoist，否则用融合序。

    需要 lex 分数 —— 重放数据只存了顺序，故用「lex 前 L 是否全部已在融合 top-6」
    作为代理：若 lex 榜首已被融合采纳，说明融合没在稀释它，无需 hoist。
    """
    base = base_order(rec)
    top6 = set(base[:6])
    lex_top = rec["lex_order"][:L]
    if all(c in top6 for c in lex_top):
        return base
    return r_lexfirst(rec, L)


def r_hoist_missing(rec, L):
    """只 hoist 融合 top-6 **之外**的 lex 前列（把缺的补进来，不移走已有的）。"""
    base = base_order(rec)
    top6 = set(base[:6])
    missing = [c for c in rec["lex_order"][:L] if c not in top6]
    if not missing:
        return base
    # 把缺失的 lex 块插到最前，其余保持融合序（会挤掉原 top-6 末位）
    out, seen = [], set()
    for cid in missing + base + rec["lex_order"]:
        if cid not in seen:
            seen.add(cid); out.append(cid)
    return out


def evaluate(setname, rule) -> tuple[int, int, set]:
    recs, ans = D[setname], ANS[setname]
    h, hits = 0, set()
    for qid in ans:
        rec = recs[qid]
        if hit(rule(rec), set(rec["gold"])):
            h += 1; hits.add(qid)
    return h, len(ans), hits


rows = []
def rec_row(tag, rule):
    h3, n3, q3 = evaluate("300cn", rule)
    hb, nb, qb = evaluate("blind", rule)
    rows.append({"tag": tag, "h300": h3, "n300": n3, "r300": h3 / n3,
                 "hblind": hb, "nblind": nb, "rblind": hb / nb,
                 "q300": q3, "qblind": qb})
    flag = "  <== 300cn PASS" if h3 / n3 >= 0.85 else ""
    print(f"  {tag:34} 300cn {h3:>3}/{n3} = {h3/n3:.4f}   "
          f"blind {hb:>3}/{nb} = {hb/nb:.4f}{flag}")
    return rows[-1]


print("\n" + "=" * 96)
print("[基线] v6（无 lex_first）")
print("=" * 96)
base = rec_row("v6 baseline", lambda r: base_order(r))

print("\n" + "=" * 96)
print("A) RRF k 常数扫描（w=1，无 lex_first）")
print("=" * 96)
for k in (1, 3, 5, 8, 10, 15, 20, 30, 45, 60, 80, 120, 200):
    rec_row(f"k={k}", lambda r, k=k: fuse(r, {"lex": 1.0}, k))

print("\n" + "=" * 96)
print("B) lex_first L 扫描（k=60）")
print("=" * 96)
for L in (1, 2, 3, 4, 5, 6, 8, 10, 15):
    rec_row(f"lexfirst L={L}", lambda r, L=L: r_lexfirst(r, L))

print("\n" + "=" * 96)
print("C) 非破坏式 additive（融合序前置，lex 只补缺）")
print("=" * 96)
for L in (1, 2, 3, 5, 8, 12, 20, 40):
    rec_row(f"additive L={L}", lambda r, L=L: r_additive(r, L))

print("\n" + "=" * 96)
print("D) 交错 interleave（stride 扫描，L=3/5/8）")
print("=" * 96)
for L in (3, 5, 8):
    for st in (1, 2, 3):
        rec_row(f"interleave L={L} stride={st}", lambda r, L=L, st=st: r_interleave(r, L, st))

print("\n" + "=" * 96)
print("E) hoist 缺失项（只补 top-6 外的 lex 前列）")
print("=" * 96)
for L in (1, 2, 3, 4, 5, 6, 8):
    rec_row(f"hoist_missing L={L}", lambda r, L=L: r_hoist_missing(r, L))

print("\n" + "=" * 96)
print("F) 组合：k × lexfirst L")
print("=" * 96)


def _combo(rec, L, k):
    base = fuse(rec, {"lex": 1.0}, k)
    if L <= 0:
        return base
    out, seen = [], set()
    for cid in rec["lex_order"][:L] + base + rec["lex_order"]:
        if cid not in seen:
            seen.add(cid); out.append(cid)
    return out


for k in (5, 10, 20, 30):
    for L in (2, 3, 4):
        rec_row(f"k={k} lexfirst L={L}", lambda r, k=k, L=L: _combo(r, L, k))

print("\n" + "=" * 96)
print("汇总：满足 **300cn ≥0.85 且 blind ≥0.85** 的配置")
print("=" * 96)
good = [r for r in rows if r["r300"] >= 0.85 and r["rblind"] >= 0.85]
if good:
    for r in sorted(good, key=lambda x: -(x["r300"] + x["rblind"])):
        print(f"  {r['tag']:34} 300cn {r['h300']}/{r['n300']}={r['r300']:.4f}  "
              f"blind {r['hblind']}/{r['nblind']}={r['rblind']:.4f}")
else:
    b3 = max(rows, key=lambda x: x["r300"])
    print(f"  无。300cn 最高 = {b3['tag']} {b3['r300']:.4f} (blind {b3['rblind']:.4f})")

out = [{k: v for k, v in r.items() if k not in ("q300", "qblind")} for r in rows]
(R / "_85_sweep.json").write_text(json.dumps(out, ensure_ascii=False, indent=2),
                                 encoding="utf-8")
print(f"\n-> {R / '_85_sweep.json'}")
