# -*- coding: utf-8 -*-
"""未命中题判别（只读）：排序缺口 vs 召回缺口 vs 「语料用了另一个 attest 过的写法」。

用法：_diag_miss.py <testset.json> <report.json> [topk_wide=30]
report 里取 mode=full 且 answerable 且 hit=False 的题，逐题：
  1. 期望词只用**正名**时，宽窗（top-30）里有没有含答案词的块 → 有=排序缺口，无=召回缺口；
  2. 把期望词扩成「正名 + 图谱里该实体已登记的 alias + 其 mention 变体」后再看**前 6**：
     若这样就有块命中 → 说明**语料/图谱本来就认这个别名**，是「期望词写窄了」而不是检索失败。
"""
from __future__ import annotations

import asyncio
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from compendium_rag import pipeline as P  # noqa: E402
from compendium_rag.config import get_settings  # noqa: E402

RE_CN = re.compile(r"[一-鿿]")


def flat(ev):
    out = []
    for g in ev or []:
        out += [g] if isinstance(g, str) else [str(x) for x in g]
    seen, res = set(), []
    for k in out:
        k = k.strip()
        if k and k not in seen:
            seen.add(k)
            res.append(k)
    return res


def blob_of(c) -> str:
    return f"{c.text}\n{c.chapter_title}\n{c.scene_title}\n{c.part_title}"


async def main() -> int:
    ts_path, rep_path = Path(sys.argv[1]), Path(sys.argv[2])
    wide = int(sys.argv[3]) if len(sys.argv) > 3 else 30
    s = get_settings()
    kb = P.load_kb(s)
    g = kb.graph
    ts = json.loads(ts_path.read_text(encoding="utf-8"))
    cases = {c["id"]: c for c in (ts["cases"] if isinstance(ts, dict) else ts)}
    rep = json.loads(rep_path.read_text(encoding="utf-8"))
    miss = [r["qid"] for r in rep["rows"]
            if r["mode"] == "full" and r["answerable"] and not r["hit"]]
    print(f"{ts_path.name} × {rep_path.name}: answerable 未命中 {len(miss)} 题")

    n_rank = n_recall = n_alias_top6 = 0
    lines = []
    for qid in miss:
        c = cases.get(qid) or {}
        kws = flat(c.get("evidence"))
        res = await kb.retrieve(c.get("q", ""), top_k=wide, use_vector=True)
        evs = res.get("evidence", [])
        blobs = [blob_of(kb.retriever.chunks[e["chunk_id"]])
                 for e in evs if e["chunk_id"] in kb.retriever.chunks]
        best = next((i for i, b in enumerate(blobs, 1) if any(k in b for k in kws)), None)
        # 期望词扩到图谱已登记的 alias/写法
        alias = set()
        for k in kws:
            eid = g.resolve(k)
            if eid:
                e = g.entities[eid]
                alias |= {x for x in ([e.name] + list(e.aliases or []))
                          if len(x) >= 2 and RE_CN.search(x)}
        alias -= set(kws)
        hit6_alias = any(any(k in b for k in (list(kws) + list(alias))) for b in blobs[:6])
        if hit6_alias and best is None:
            n_alias_top6 += 1
        if best:
            n_rank += 1
        else:
            n_recall += 1
        tag = ("排序" if best else ("别名" if hit6_alias else "召回"))
        lines.append(f"[{tag}] {qid} 宽窗最好名次={best}｜前6含alias变体块={hit6_alias}"
                     f"｜alias={sorted(alias)[:4]}｜{c.get('q','')[:34]}")
    print("\n".join(lines))
    print(f"\n汇总：排序缺口 {n_rank}｜前6有已登记别名可解释 {n_alias_top6}｜纯召回缺口 "
          f"{n_recall - n_alias_top6}")
    out = Path("C:/Users/Lenovo/AppData/Local/Temp/_diag_") / (rep_path.stem + ".txt")
    out.parent.mkdir(exist_ok=True)
    out.write_text("\n".join(lines), encoding="utf-8")
    print(f"明细 → {out}")
    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
