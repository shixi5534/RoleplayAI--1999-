# -*- coding: utf-8 -*-
"""召回改进探索（不改 src/）：用**候选生成**视角找出「gold 块根本没进池」的解法空间。

诊断结论（_miss_rootcause.py 实测）14 道 full 口径池内 miss 分四类：
  T1 语料层仅 1 块含答案 + 该块与种子无图关联（R005/R127/R297）
  T2 金标答案块与种子实体不同篇/无路径（R012/R170/R244/R248）
  T3 种子为空或错误（R094「Noire」/R127/R171/R251 种子=[]）
  T4 描述性指代型：种子里出现的是通用词（R018 伙计/猎人、R273 教师/神秘术）

本脚本量化一个**关键的可行性问题**：
  若引入"词面通道"（把查询词直接与块文本做词面匹配，不依赖实体链接/图谱），
  gold 是否可达？这决定 85% 目标能否靠**检索侧**达成，还是必须走查询侧供给。

方法：对每题算 BM25-类词面分（字符 bigram + 词），看 gold 块的词面排名。
"""
from __future__ import annotations

import json
import math
import re
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from compendium_rag import pipeline as P                      # noqa: E402
from compendium_rag.config import get_settings                # noqa: E402

MISS = ["R005", "R012", "R018", "R094", "R127", "R170", "R171",
        "R231", "R244", "R248", "R251", "R273", "R297", "R298"]


def grams(s: str) -> list[str]:
    """中文按字符 bigram + 英文数字按词，做轻量分词。"""
    s = s.lower()
    toks = re.findall(r"[a-z0-9]+", s)
    zh = re.findall(r"[\u4e00-\u9fff]", s)
    toks += ["".join(zh[i:i + 2]) for i in range(len(zh) - 1)]
    return toks


def main() -> int:
    s = get_settings()
    kb = P.load_kb(s)
    chunks = list(kb.chunks)
    blob = {c.chunk_id: f"{c.text}\n{c.chapter_title}\n{c.scene_title}\n{c.part_title}"
            for c in chunks}

    ts = json.loads((ROOT / "data/knowledge/_audit/rag_testset_300_cn.json").read_text(encoding="utf-8"))
    cases = {str(c.get("id")): c for c in ts["cases"]}

    def kws_of(c):
        out = []
        for grp in (c.get("evidence") or []):
            if isinstance(grp, str):
                out.append(grp)
            elif isinstance(grp, (list, tuple)):
                out.extend(str(x) for x in grp if x)
        return [k.strip() for k in out if k and k.strip()]

    # 全库 df
    print("[build] 统计 df …")
    df = Counter()
    doc_toks = {}
    for c in chunks:
        t = grams(blob[c.chunk_id])
        doc_toks[c.chunk_id] = Counter(t)
        for g in set(t):
            df[g] += 1
    N = len(chunks)
    avg = sum(sum(v.values()) for v in doc_toks.values()) / N

    def bm25(qtoks, cid, k1=1.2, b=0.6):
        d = doc_toks[cid]
        L = sum(d.values()) or 1
        sc = 0.0
        for g in qtoks:
            f = d.get(g, 0)
            if not f:
                continue
            idf = math.log(1 + (N - df[g] + 0.5) / (df[g] + 0.5))
            sc += idf * (f * (k1 + 1)) / (f + k1 * (1 - b + b * L / avg))
        return sc

    print(f"\n{'qid':6} {'gold块数':>7} {'词面最佳排名':>12}  gold块样例")
    reachable = 0
    for qid in MISS:
        c = cases[qid]
        kws = kws_of(c)
        gold = [cid for cid, t in blob.items() if any(k in t for k in kws)]
        if not gold:
            print(f"{qid:6} {'0':>7}  语料层无答案（题面/语料脱节）")
            continue
        qt = grams(c["q"])
        scores = [(bm25(qt, cid), cid) for cid in blob]
        scores.sort(reverse=True)
        rank = None
        for i, (_, cid) in enumerate(scores, 1):
            if cid in set(gold):
                rank = i
                break
        ok = rank is not None and rank <= 30
        reachable += ok
        print(f"{qid:6} {len(gold):>7} {str(rank):>12}  {gold[0]}")
    print(f"\n[结论] 14 道 miss 中，纯词面通道可进 top-30 的: {reachable}/14")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
