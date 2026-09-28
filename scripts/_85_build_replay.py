# -*- coding: utf-8 -*-
"""离线重放器（基于**已验证**的 collect 工件 + 现算 lex 通道）。

为什么可信：
  - collect 的 score 可由 reasons 精确重建（已验证 2400/2400 一致，见 _85_validate_rrf.py）；
  - 故池内每块的 (channel, rank) 已知，融合序可离线重算；
  - 只有 PPR 通道耗时，词面 BM25 很便宜 → lex 全序现算补齐池外部分。

提供 evaluate(rule)：对 300cn 与 blind 各报 hit@6 与逐题 up/down。
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

R = ROOT / "data/compendium_rag/reports"
K_RRF = 60
TOPN = 24


def load_collect(fname: str) -> dict[str, dict]:
    d = json.loads((R / fname).read_text(encoding="utf-8"))
    out = {}
    for r in d["rows"]:
        if r.get("mode") != "full":
            continue
        out[r["qid"]] = r
    return out


def parse_ranks(row: dict) -> dict[str, dict[str, int]]:
    """从 reasons 复原每块在各通道的名次：{chunk_id: {channel: rank}}。"""
    per: dict[str, dict[str, int]] = {}
    for e in row.get("evidence") or []:
        cid = e["chunk_id"]
        for rs in (e.get("reasons") or []):
            if "#" not in rs:
                continue
            ch, rk = rs.rsplit("#", 1)
            try:
                per.setdefault(cid, {})[ch] = int(rk)
            except ValueError:
                pass
    return per


def fuse(per: dict[str, dict[str, int]], weights: dict[str, float],
         k: float = K_RRF, top_n: int = TOPN) -> list[str]:
    agg: dict[str, float] = {}
    for cid, chans in per.items():
        s = 0.0
        for ch, rk in chans.items():
            s += weights.get(ch, 1.0) * (1.0 / (k + rk))
        agg[cid] = s
    return sorted(agg, key=lambda c: (-agg[c], c))[:top_n]


def main() -> int:
    # 词面通道全序（现算，便宜）
    from compendium_rag import pipeline as P
    from compendium_rag.config import get_settings
    from _lex_channel_full import LexIndex

    kb = P.load_kb(get_settings())
    lex = LexIndex(kb.chunks)
    chunks = kb.retriever.chunks
    print("[lex] index ready", flush=True)

    out: dict = {}
    for setname, fname in [("300cn", "rank_collect_v6c300_top30.json"),
                           ("blind", "rank_collect_v6cblind_top30.json")]:
        rows = load_collect(fname)
        recs = {}
        for qid, row in rows.items():
            kws = row.get("eval_keywords") or []
            gold = [cid for cid, c in chunks.items()
                    if any(k in f"{c.text}\n{c.chapter_title}\n{c.scene_title}\n{c.part_title}"
                           for k in kws)]
            lex_hits = [cid for cid, _s in lex.search(row.get("q_used") or row["query"], 60)]
            recs[qid] = {
                "query": row.get("q_used") or row["query"],
                "answerable": bool(row.get("answerable")),
                "per": parse_ranks(row),
                "gold": gold,
                "lex_order": lex_hits,
            }
        out[setname] = recs
        n_ans = sum(1 for r in recs.values() if r["gold"])
        print(f"[{setname}] q={len(recs)} answerable={n_ans}", flush=True)

    dest = R / "_85_replay_data.json"
    dest.write_text(json.dumps(out, ensure_ascii=False), encoding="utf-8")
    print(f"-> {dest} ({dest.stat().st_size/1e6:.1f} MB)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
