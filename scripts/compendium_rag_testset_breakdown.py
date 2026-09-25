# -*- coding: utf-8 -*-
"""拆解 300 题的性质：哪些题因为「中文语料 vs 英文名查询」而结构上不可答。"""
from __future__ import annotations

import json
import re
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from compendium_rag import pipeline as P  # noqa: E402
from compendium_rag.config import get_settings  # noqa: E402

RE_CN = re.compile(r"[\u4e00-\u9fff]")


def flatten(ev) -> list[str]:
    out = []
    for g in (ev or []):
        if isinstance(g, str):
            out.append(g)
        elif isinstance(g, (list, tuple)):
            out.extend(str(x) for x in g if x)
    seen, res = set(), []
    for k in out:
        k = k.strip()
        if k and k not in seen:
            seen.add(k); res.append(k)
    return res


def main() -> int:
    s = get_settings()
    kb = P.load_kb(s)
    blob = "\n".join(c.text for c in kb.chunks)

    p = ROOT / "data" / "knowledge" / "_audit" / "rag_testset_300.json"
    cases = json.loads(p.read_text(encoding="utf-8"))

    stats = Counter()
    cn_absent_examples, en_only = [], []
    for c in cases:
        kws = flatten(c.get("evidence"))
        if not kws:
            stats["no_keywords"] += 1
            continue
        present = [k for k in kws if k in blob]
        cn_kws = [k for k in kws if RE_CN.search(k)]
        en_kws = [k for k in kws if not RE_CN.search(k)]

        if present:
            stats["answerable"] += 1
            if any(RE_CN.search(k) for k in present):
                stats["answerable_via_cn"] += 1
            else:
                stats["answerable_via_en_only"] += 1
                en_only.append(c)
        else:
            stats["absent"] += 1
            if cn_kws and not any(k in blob for k in cn_kws):
                # 中文关键词也不在语料里 → 该篇内容可能未收录
                stats["absent_even_cn"] += 1
                cn_absent_examples.append(c)

    n = len(cases)
    print(f"总计 {n} 题\n")
    for k in ("answerable", "answerable_via_cn", "answerable_via_en_only",
              "absent", "absent_even_cn"):
        v = stats[k]
        print(f"  {k:26} {v:>4}  ({v/n:.1%})")

    print(f"\n=== 中文关键词也找不到的题（语料未覆盖，非检索问题）{len(cn_absent_examples)} 题 ===")
    for c in cn_absent_examples[:15]:
        print(f"  [{c.get('id')}] {c.get('q')[:52]}")
        print(f"       dims={json.dumps(c.get('dims'), ensure_ascii=False)}")

    print(f"\n=== 仅靠英文关键词才判为可答的题 {len(en_only)} 题 ===")
    for c in en_only[:10]:
        print(f"  [{c.get('id')}] {c.get('q')[:52]}")
        print(f"       关键词={flatten(c.get('evidence'))[:4]}")

    # 章节覆盖对照
    print("\n=== 按章节：可答 / 不可答 ===")
    per = {}
    for c in cases:
        ch = (c.get("dims") or {}).get("chapter", "?")
        d = per.setdefault(ch, {"n": 0, "ok": 0})
        d["n"] += 1
        if any(k in blob for k in flatten(c.get("evidence"))):
            d["ok"] += 1
    for ch, d in sorted(per.items(), key=lambda kv: -kv[1]["n"])[:16]:
        print(f"  {ch:>8}  {d['ok']:>3}/{d['n']:<3} "
              f"({d['ok']/d['n']:.0%})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
