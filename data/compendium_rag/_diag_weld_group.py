# -*- coding: utf-8 -*-
"""诊断：strip 之后仍把两组写法焊在一起的**具体边**是哪几条。

只读；从 `--cache` 指定的 cache 根目录加载 raw 块，复刻 _fix_alias_welds 的
「宿主→alias 双向剥离」口径，然后打印目标组的成员与每条边的声明块。
"""
import json
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path("src").resolve()))
sys.path.insert(0, str(Path("data/compendium_rag").resolve()))

from _fix_alias_welds import DROP_MAP, _norm_name          # noqa: E402
from compendium_rag.graph_store import _merge_candidates   # noqa: E402

args = sys.argv[1:]
cache_dir = Path(args[0]) if args and Path(args[0]).is_dir() else Path("data/compendium_rag/cache")
targets = [t for t in args if not Path(t).is_dir()] or ["苏菲亚", "无名者"]

edges = []          # (holder, alias) 声明边（strip 后仍存留）
obs = defaultdict(int)
for p in sorted(cache_dir.glob("*/*.json")):
    raw = json.loads(p.read_text(encoding="utf-8")).get("raw") or {}
    for e in raw.get("entities") or []:
        nm = e.get("name") or ""
        if not nm:
            continue
        obs[_norm_name(nm)] += 1
        bad = DROP_MAP.get(_norm_name(nm), set())
        for a in e.get("aliases") or []:
            if a in bad or _norm_name(a) in bad:
                continue
            edges.append((nm, a))

dsu = _merge_candidates(sorted(obs), edges)
groups = defaultdict(list)
for n in obs:
    groups[dsu.find(n)].append(n)

for t in targets:
    root = dsu.find(t)
    mem = sorted(groups.get(root) or [])
    print(f"== 目标 {t}｜组大小 {len(mem)}｜{mem[:40]}")
    for (h, a) in edges:
        if h in mem or a in mem:
            print(f"   边 {h} → alias {a}")
