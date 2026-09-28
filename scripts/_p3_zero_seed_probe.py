# -*- coding: utf-8 -*-
"""P3 探查：4 道「零种子」题的查询实体为何没进图？（别名缺口 vs 真缺实体）

依据（scripts/_miss_p3_triage.py）：R001/R094/R127/R171 的 link() 种子为空。
若属**别名缺口**（图里有实体、只是叫法不同），补一条 alias 即可救；
若属**真缺实体**，需抽取新节点（P3 的另一形态）。

本脚本只读：对每题列出查询里出现的候选词，并在图的实体名/别名里做模糊匹配。
"""
from __future__ import annotations

import difflib
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from compendium_rag import pipeline as P                      # noqa: E402
from compendium_rag.config import get_settings                # noqa: E402

ZERO = ["R001", "R094", "R127", "R171"]


def main() -> int:
    s = get_settings()
    kb = P.load_kb(s)
    g = kb.graph
    names = list(g.alias_index.keys())

    ts = json.loads((ROOT / "data/knowledge/_audit/rag_testset_300_cn.json").read_text(encoding="utf-8"))
    by = {str(c["id"]): c for c in ts["cases"]}

    for qid in ZERO:
        c = by[qid]
        q = c["q"]
        print("=" * 84)
        print(f"{qid}: {q}")
        print(f"  gold: {c.get('evidence')}")
        # 中文串（2-8 字）作为候选专名
        cands = set(re.findall(r"[\u4e00-\u9fff]{2,8}", q))
        # 去掉常见疑问/功能词
        stop = {"什么", "是什么", "真名", "中文", "译名", "所在", "哪里", "哪座",
                "怎么", "为什么", "多少", "这起", "那位", "哪个", "里面"}
        cands = [x for x in cands if x not in stop]
        hits = []
        for cand in cands:
            m = difflib.get_close_matches(cand, names, n=3, cutoff=0.5)
            if m:
                hits.append((cand, m))
        if hits:
            print("  **模糊匹配到图中实体（别名缺口候选）**:")
            for cand, m in hits:
                print(f"    {cand} -> {[(x, g.alias_index[x]) for x in m]}")
        else:
            print("  未匹配到任何图中实体 -> 疑似**真缺实体**（需抽取）")
        # 语料层：gold 所在块
        chunks = {ch.chunk_id: ch for ch in kb.chunks}
        blob = {cid: f"{ch.text}\n{ch.chapter_title}" for cid, ch in chunks.items()}
        kws = []
        for grp in (c.get("evidence") or []):
            items = grp if isinstance(grp, (list, tuple)) else [grp]
            kws.extend(str(x) for x in items if x)
        goldc = [cid for cid, t in blob.items() if any(k in t for k in kws)]
        print(f"  gold 块数 = {len(goldc)}  样例: {goldc[:2]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
