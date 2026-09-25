# -*- coding: utf-8 -*-
"""按版本枚举各分类进度（mainline / character / anecdote / activity）。

口径与 _progress_snapshot.py 一致：用 extract.cache_key 公式判定"已抽"。
"""
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT.parent.parent / "src"))

from compendium_rag.config import get_settings              # noqa: E402
from compendium_rag.pipeline import load_chunks             # noqa: E402
from compendium_rag.extract import PROMPT_VERSION, cache_key  # noqa: E402

s = get_settings()
chunks = load_chunks(s)
cache_keys = {p.stem for p in (ROOT / "cache").rglob("*.json")}
done_ids = {c.chunk_id for c in chunks
            if cache_key(c, s.llm_model, PROMPT_VERSION) in cache_keys}


def report(cat: str, show_all: bool = True) -> None:
    docs = defaultdict(lambda: [0, 0])
    for c in chunks:
        if c.category != cat:
            continue
        docs[c.doc_id][0] += 1
        if c.chunk_id in done_ids:
            docs[c.doc_id][1] += 1
    tot_all = sum(t for t, _ in docs.values())
    got_all = sum(g for _, g in docs.values())
    closed = sum(1 for t, g in docs.values() if t == g and t > 0)
    partial = sum(1 for t, g in docs.values() if 0 < g < t)
    print(f"\n{'='*78}")
    print(f"【{cat}】{len(docs)} 版｜{got_all}/{tot_all} 块"
          f"（{got_all/tot_all*100:.1f}%）｜闭环 {closed} 版｜"
          f"部分 {partial} 版｜未抽 {sum(1 for t,g in docs.values() if g==0)} 版")
    print(f"{'='*78}")
    if not show_all:
        docs = {k: v for k, v in docs.items() if v[1] > 0}
    for doc, (t, g) in sorted(docs.items()):
        if g == t and t > 0:
            mark = "✅ 闭环"
        elif g == 0:
            mark = "·  未抽"
        else:
            mark = f"△  {g}/{t}"
        print(f"  {doc:52s} {t:4d} 块  {mark}")


for cat in ("mainline", "character", "anecdote", "activity", "appendix_unbound"):
    report(cat)
