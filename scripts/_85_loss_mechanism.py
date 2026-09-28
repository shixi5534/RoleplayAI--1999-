# -*- coding: utf-8 -*-
"""Q1/Q2：lex_first=3 在 300cn 上丢掉 7 题的**逐题机理**（用 collect 文件，零重算）。

对每题回答：
  1. v6（无 lex_first）下 gold 块的融合名次是几？（用 rank 字段 = top_k 窗内首个 gold 名次）
  2. lex_first 把 lex 前 3 名提到了最前 —— 那 3 块是不是 gold？
  3. gold 块自身的 lex 名次是多少？（若在 1-3 就绝不该丢）
  4. gold 块被挤到了第几名（lex_first 序下）？

全部数据来自 rank_collect_v6c300_top30.json 的 evidence（已按 v6 融合序排列），
其中每条 evidence 的 reasons 给出该块在各通道的名次（如 "lex#3"）。
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
R = ROOT / "data/compendium_rag/reports"

LOST = "R030 R043 R073 R080 R183 R242 R263".split()
GAINED = "R018 R052 R231 R241 R251 R268 R286".split()


def load_collect(fname: str) -> dict[str, dict]:
    d = json.loads((R / fname).read_text(encoding="utf-8"))
    return {r["qid"]: r for r in d["rows"]
            if r.get("mode") == "full" and r.get("answerable")}


def chan_rank(ev: dict, ch: str):
    """从 reasons 里取出该块在通道 ch 上的名次（如 'lex#3' -> 3）。"""
    for r in ev.get("reasons") or []:
        if r.startswith(ch + "#"):
            try:
                return int(r.split("#", 1)[1])
            except ValueError:
                pass
    return None


def lex_order(rows: list[dict], n: int = 30):
    """按 evidence 中的 lex 名次重建 lex 通道序（前 n）。"""
    got = []
    for ev in rows:
        lr = chan_rank(ev, "lex")
        if lr is not None:
            got.append((lr, ev["chunk_id"]))
    got.sort()
    return [cid for _r, cid in got[:n]]


def lexfirst_order(rows: list[dict], L: int = 3):
    base = [e["chunk_id"] for e in rows]
    lex = lex_order(rows, 30)
    out, seen = [], set()
    for cid in lex[:L] + base + lex:
        if cid not in seen:
            seen.add(cid)
            out.append(cid)
    return out


def gold_rank_in(order: list[str], gold: set[str]):
    for i, cid in enumerate(order, start=1):
        if cid in gold:
            return i
    return None


def main() -> int:
    recs = load_collect("rank_collect_v6c300_top30.json")
    # 同时用实现里的 lex 名次推导 gold 集合：collect 文件不含 gold 列表，
    # 但 v6 的 rank 字段就是首个 gold 名次，足以定位 gold 块。
    print("=" * 100)
    print("Q1/Q2：7 道 LOST 的逐题机理（数据源 rank_collect_v6c300_top30.json，mode=full, answerable）")
    print("=" * 100)
    summary = {}
    for qid in LOST:
        r = recs[qid]
        rows = r["evidence"]
        v6_rank = r["rank"]                       # top_k 窗内首个 gold 名次
        lex = lex_order(rows, 30)
        hoisted = lex[:3]
        # gold 块的判定：用后续 _gold_probe 得到的集合；此处先用 rank 定位
        lf_order = lexfirst_order(rows, 3)
        # lex_first 后 gold 的新名次（用同样的"首个 gold"逻辑需 gold 集合）
        top3_lex_ranks = [chan_rank(next(e for e in rows if e["chunk_id"] == c), "lex")
                          for c in hoisted]
        summary[qid] = {
            "v6_rank": v6_rank,
            "v6_rank_ev": rows[v6_rank - 1]["chunk_id"] if v6_rank else None,
            "hoisted": hoisted,
            "hoisted_lex_ranks": top3_lex_ranks,
            "lex_order_top8": lex[:8],
            "v6_order_top8": [e["chunk_id"] for e in rows[:8]],
            "lf_order_top8": lf_order[:8],
        }
        print(f"\n--- {qid} ---  v6 首个 gold 名次 = {v6_rank}")
        print(f"    gold@v6 块 = {rows[v6_rank-1]['chunk_id']}" if v6_rank else "    (v6 无 gold in top30)")
        print(f"    lex 前 3（被 hoist 的）= ")
        for c, lr in zip(hoisted, top3_lex_ranks):
            print(f"        lex#{lr:<3} {c}")
        print(f"    v6 序前 6 = {[e['chunk_id'] for e in rows[:6]]}")
        print(f"    lf  序前 6 = {lf_order[:6]}")
        print(f"    lf  序前 8 = {lf_order[:8]}")
    out = R / "_85_loss_mechanism_raw.json"
    out.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\n-> {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
