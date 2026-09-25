# -*- coding: utf-8 -*-
"""只读探查：原生题集未命中是否集中在「题面实体是高频 hub」上。

用法：_diag_df.py <testset.json> <report.json>
对 mode=full 且 answerable 且未命中的题，统计
  - 题面里「」引用的实体在语料中的**块频次**（DF）；
  - 该题事实来源块 `_from_chunk` 的文本长度；
再与**命中**题的同一分布对比，判断缺口是「词形/数据」还是「判别力（同名块太多）」。
"""
from __future__ import annotations

import json
import re
import statistics
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from compendium_rag import pipeline as P  # noqa: E402
from compendium_rag.config import get_settings  # noqa: E402

RE_Q = re.compile(r"「([^」]+)」")


def main() -> int:
    ts_path, rep_path = Path(sys.argv[1]), Path(sys.argv[2])
    s = get_settings()
    chunks = P.load_chunks(s)
    texts = [f"{c.text}\n{c.chapter_title}\n{c.scene_title}\n{c.part_title}" for c in chunks]
    ts = json.loads(ts_path.read_text(encoding="utf-8"))
    cases = {c["id"]: c for c in (ts["cases"] if isinstance(ts, dict) else ts)}
    rep = json.loads(rep_path.read_text(encoding="utf-8"))
    rows = [r for r in rep["rows"] if r["mode"] == "full" and r["answerable"]]

    df_cache: dict[str, int] = {}

    def df(name: str) -> int:
        if name not in df_cache:
            df_cache[name] = sum(1 for t in texts if name in t)
        return df_cache[name]

    buckets = {}
    for hitflag, key in [(False, "miss"), (True, "hit")]:
        sub = [r for r in rows if bool(r["hit"]) is hitflag]
        dfs, names = [], Counter()
        for r in sub:
            c = cases.get(r["qid"]) or {}
            for n in RE_Q.findall(c.get("q", "")):
                d = df(n)
                dfs.append(d)
                if d >= 30:
                    names[n] = d
        buckets[key] = (len(sub), dfs, names)
        if dfs:
            print(f"{key}: 题 n={len(sub)} 题面实体数={len(dfs)} "
                  f"DF 中位={statistics.median(dfs):.0f} "
                  f"P25={statistics.quantiles(dfs, n=4)[0]:.0f} "
                  f"P75={statistics.quantiles(dfs, n=4)[2]:.0f} "
                  f"max={max(dfs)}  DF>=30 占比={sum(1 for d in dfs if d >= 30) / len(dfs):.2f}")
    print("\n未命中题里的高频(DF>=30)题面实体 TOP15：")
    for n, d in buckets["miss"][2].most_common(15):
        print(f"   {n}  DF={d}")
    print("\n命中题里的高频(DF>=30)题面实体 TOP15：")
    for n, d in buckets["hit"][2].most_common(15):
        print(f"   {n}  DF={d}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
