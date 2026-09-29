# -*- coding: utf-8 -*-
"""R4-K01 摘除的**影响范围上界**论证（为什么只需评估含「诊疗」的题）。

`link()` 的机制（src/compendium_rag/retriever.py:375）：
    cands = sorted(self.graph.alias_index.keys(), key=lambda k: (-len(k), k))
    for name in cands:
        if name in query:            # 子串匹配
            eid = self.graph.alias_index[name]

即别名**只在该别名字符串出现于 query 时**才被命中。
故摘除 `诊疗` 只会改变「query 中含 `诊疗` 串」的题的种子集 ——
其余题的结果与摘除无关。本脚本对该上界做机械核验。
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT / "data/knowledge/_audit"

SETS = {
    "300cn": AUDIT / "rag_testset_300_cn.json",
    "gen120": AUDIT / "rag_testset_gen_r1r2.json",
    "blind206": AUDIT / "blind_v1/questions_strict.json",
}

ALIAS = "诊疗"
print("=" * 80)
print(f"含「{ALIAS}」的题（= 摘除可能影响的**全部**题目）")
print("=" * 80)
total = 0
for name, path in SETS.items():
    d = json.loads(path.read_text(encoding="utf-8"))
    rows = d if isinstance(d, list) else d.get("cases", [])
    hits = [r for r in rows if ALIAS in (r.get("q") or "")]
    total += len(hits)
    print(f"  [{name:9}] n={len(rows):4}  含『{ALIAS}』= {len(hits)}  "
          f"{[str(r.get('id')) for r in hits]}")
print(f"\n  合计 = {total} 道")
print()
print("结论：摘除的影响范围**恰好**是这", total, "道题；其余题集的种子集不可能因此改变")
print("     （alias_index 命中要求别名字面出现在 query 中）。")
