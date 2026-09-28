# -*- coding: utf-8 -*-
"""盲测偏置检查（关键完整性核验）：盲测题是否**字面泄漏**了 gold 块的措辞？

为什么必须查：
  盲测题由子代理**阅读语料后**撰写。若它们把原文的独特措辞直接搬进问题，
  词面通道（BM25）会**平凡命中**，从而系统性高估 lex 通道、并让"lex-only 0.9320"
  这类结论失真。

方法（对两套题集做同样测量，直接可比）：
  对每题取 gold 块（含答案关键词的块），计算
    overlap = |question 的 bigram ∩ gold 块 bigram| / |question bigram|
  比较高/中/低重叠的分布。
  若盲测的重叠显著高于 300cn -> 盲测存在字面偏置，其 lex 结论需打折。
"""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def grams(s: str) -> set[str]:
    s = (s or "").lower()
    toks = set(re.findall(r"[a-z0-9]+", s))
    zh = re.findall(r"[\u4e00-\u9fff]", s)
    toks |= {"".join(zh[i:i + 2]) for i in range(len(zh) - 1)}
    return toks


def load(p: Path):
    d = json.loads(p.read_text(encoding="utf-8"))
    out = []
    for r in (d if isinstance(d, list) else d.get("cases", [])):
        kws = []
        for g in (r.get("evidence") or []):
            if isinstance(g, str):
                kws.append(g)
            elif isinstance(g, (list, tuple)):
                kws.extend(str(x) for x in g if x)
        kws = [k.strip() for k in kws if k.strip()]
        if kws:
            out.append({"qid": str(r.get("id", "")), "q": r.get("q", ""), "kws": kws})
    return out


def main() -> int:
    chunks = json.loads((ROOT / "data/compendium_rag/chunks.json").read_text(encoding="utf-8"))["chunks"]
    blob = {c["chunk_id"]: f"{c['text']}\n{c['chapter_title']}\n{c.get('scene_title','')}\n{c.get('part_title','')}"
            for c in chunks}

    for label, path in (("300cn", ROOT / "data/knowledge/_audit/rag_testset_300_cn.json"),
                        ("盲测206", ROOT / "data/knowledge/_audit/blind_v1/questions_strict.json")):
        cases = load(path)
        ans = "\n".join(c["text"] for c in chunks)
        cases = [c for c in cases if any(k in ans for k in c["kws"])]
        rows = []
        for c in cases:
            qg = grams(c["q"])
            if not qg:
                continue
            gold = [cid for cid, t in blob.items() if any(k in t for k in c["kws"])]
            if not gold:
                continue
            # 该题最"像"的 gold 块（重叠最高者）
            best = 0.0
            for cid in gold[:40]:
                gg = grams(blob[cid])
                if not gg:
                    continue
                best = max(best, len(qg & gg) / len(qg))
            rows.append((best, c["qid"]))
        n = len(rows)
        avg = sum(r[0] for r in rows) / n if n else 0
        hi = sum(1 for r in rows if r[0] >= 0.5)
        mid = sum(1 for r in rows if 0.25 <= r[0] < 0.5)
        lo = sum(1 for r in rows if r[0] < 0.25)
        print(f"=== {label} (n={n}) ===")
        print(f"  题面↔gold 块 bigram 重叠：均值 {avg:.3f}")
        print(f"    ≥0.50（高，疑似字面泄漏）: {hi} ({hi/n:.1%})")
        print(f"    0.25–0.50（中）          : {mid} ({mid/n:.1%})")
        print(f"    <0.25（低，真需语义/词面推理）: {lo} ({lo/n:.1%})")
        top = sorted(rows, reverse=True)[:5]
        print(f"    最高重叠样例: {[(q, round(v,2)) for v,q in top]}")
        print()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
