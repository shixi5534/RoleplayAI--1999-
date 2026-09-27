# -*- coding: utf-8 -*-
"""盲测完整性核验：证明盲测集与 300cn **无题目重叠**，且答案不由"抄题"得来。

三重检查：
  1. 问题文本重叠：盲测 q vs 300cn q 的字符级相似度（正常化后）
  2. 证据关键词重叠：盲测 evidence 关键词集合 vs 300cn 的
  3. 子代理是否可能读过 300cn：检查盲测 JSON 内是否残留 300cn 题号/字段名
"""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
D = ROOT / "data/knowledge/_audit/blind_v1"


def norm(s: str) -> str:
    return re.sub(r"[\s，。？！、：；“”\"'（）()《》·\-—…,\.\?!:;]", "", s or "")


def bigrams(s: str) -> set[str]:
    return {s[i:i + 2] for i in range(len(s) - 1)}


def main() -> int:
    ts = json.loads((ROOT / "data/knowledge/_audit/rag_testset_300_cn.json").read_text(encoding="utf-8"))
    ref_q = [(str(c.get("id")), norm(c.get("q", ""))) for c in ts["cases"]]
    ref_kw = set()
    for c in ts["cases"]:
        for g in (c.get("evidence") or []):
            items = g if isinstance(g, (list, tuple)) else [g]
            for x in items:
                if x:
                    ref_kw.add(str(x).strip())

    blind = json.loads((D / "questions_strict.json").read_text(encoding="utf-8"))
    bc = blind["cases"]
    print(f"盲测题数 = {len(bc)}；300cn 题数 = {len(ref_q)}")

    # 1) 问题文本相似
    worst = []
    for c in bc:
        bq = norm(c["q"])
        bset = bigrams(bq)
        best = 0.0
        bestid = None
        for rid, rq in ref_q:
            rset = bigrams(rq)
            if not bset or not rset:
                continue
            j = len(bset & rset) / len(bset | rset)
            if j > best:
                best, bestid = j, rid
        worst.append((best, c["id"], bestid))
    worst.sort(reverse=True)
    print("\n=== 与 300cn 最相似的盲测题（Jaccard bigram）===")
    for j, bid, rid in worst[:8]:
        print(f"  {bid} ~ {rid}: J={j:.3f}")
    print(f"  最高相似度 = {worst[0][0]:.3f}（>0.6 才算可疑重复）")
    dup = [x for x in worst if x[0] > 0.6]
    print(f"  判定重复(>0.6)的题数 = {len(dup)}")

    # 2) 关键词重叠
    bkw = set()
    for c in bc:
        for g in (c.get("evidence") or []):
            items = g if isinstance(g, (list, tuple)) else [g]
            for x in items:
                if x:
                    bkw.add(str(x).strip())
    inter = bkw & ref_kw
    print(f"\n=== 关键词集合 ===")
    print(f"  盲测关键词 {len(bkw)}；300cn 关键词 {len(ref_kw)}")
    print(f"  交集 {len(inter)}")
    if inter:
        print(f"  交集样例（可能是同名实体，属正常）: {sorted(inter)[:15]}")

    # 3) 残留痕迹
    raw = (D / "questions_strict.json").read_text(encoding="utf-8")
    for probe in ["R001", "rag_testset", "300_cn", "_asks_english_name", "oracle_min_blocks"]:
        print(f"  残留 {probe!r}: {probe in raw}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
