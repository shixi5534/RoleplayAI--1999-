# -*- coding: utf-8 -*-
"""先探路：既有 300 题在 Compendium 新库里的可答性。

关键风险：这 300 题是为**旧语料**（B站转写 + 灰机 wiki）造的，
其中不少问题（英文名、灰机小径页细节）在 Compendium 里可能根本没有答案。
因此先做**证据接地率**统计，再决定评测口径。
"""
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

TESTSETS = [
    ROOT / "data" / "knowledge" / "_audit" / "rag_testset_300_clean.json",
    ROOT / "data" / "knowledge" / "_audit" / "rag_testset_300.json",
]


def load_cases(path: Path) -> list[dict]:
    d = json.loads(path.read_text(encoding="utf-8"))
    return d if isinstance(d, list) else d.get("cases", [])


def flatten_evidence(ev) -> list[str]:
    """evidence 形如 [["Charlotte","夏洛蒂",...]] —— 展平为关键词列表。"""
    out: list[str] = []
    if not ev:
        return out
    for grp in ev:
        if isinstance(grp, str):
            out.append(grp)
        elif isinstance(grp, (list, tuple)):
            out.extend(str(x) for x in grp if x)
    return [x for x in out if x]


def main() -> int:
    s = get_settings()
    kb = P.load_kb(s)
    chunks = kb.chunks
    print(f"新库：块={len(chunks)}  实体={len(kb.graph.entities)}  "
          f"边={len(kb.graph.edges)}")

    # 全语料文本（用于判断"答案是否存在于语料"）
    corpus_blob = "\n".join(c.text for c in chunks)
    print(f"语料文本长度={len(corpus_blob):,}")

    for path in TESTSETS:
        if not path.exists():
            print(f"\n跳过（不存在）：{path}")
            continue
        cases = load_cases(path)
        print(f"\n{'=' * 78}\n{path.name}  n={len(cases)}\n{'=' * 78}")

        present = 0
        absent = []
        by_chapter = Counter()
        by_type = Counter()
        for c in cases:
            kws = flatten_evidence(c.get("evidence"))
            if not kws:
                continue
            # 任一关键词出现在语料中 → 视为"语料里可能有答案"
            hit = any(k in corpus_blob for k in kws)
            if hit:
                present += 1
                dims = c.get("dims") or {}
                by_chapter[dims.get("chapter", "?")] += 1
                by_type[dims.get("type", "?")] += 1
            else:
                absent.append(c)

        total = len(cases)
        print(f"答案关键词出现在 Compendium 语料中：{present}/{total} "
              f"({present / total:.1%})")
        print(f"完全找不到关键词（新库无法回答）：{len(absent)}/"
              f"{total} ({len(absent) / total:.1%})")

        print(f"\n可答题的章节分布（top 10）：")
        for ch, n in by_chapter.most_common(10):
            print(f"    {ch:>6}  {n}")
        print(f"\n可答题的题型分布：")
        for t, n in by_type.most_common():
            print(f"    {t:>12}  {n}")

        print(f"\n无法回答的样例（前 12 题）：")
        for c in absent[:12]:
            kws = flatten_evidence(c.get("evidence"))
            print(f"    [{c.get('id')}] {c.get('q')[:46]}")
            print(f"          期望关键词: {kws[:4]}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
