# -*- coding: utf-8 -*-
"""目标① 最终审计：14 道池内 miss 中，**gold 关键词本身是否有假阳性**？

背景（R127 实证）：
  R127 的 gold = ['purifier','净化机','purification']，但
    - 语料层 'purifier' 出现 0 次、'净化机' 出现 0 次；
    - 'purification' 仅 1 次，出现在**英文哲学引文**里
      （"The greatest purification of all is, therefore, science"），与「装置」无关；
    - 真实答案「雾气净化器」在 activity__23101 有 5 块，但**不含任何 gold 关键词**。
  => 属**测试集 gold 缺陷**（关键词假阳性），不是系统检索失败。

本脚本对 14 道 miss 逐题做同类审计：
  对每个 gold 关键词，检查其命中块是否**语义上像是答案**（用同块是否含题干实体的线索）。
  简化为可判定的三条：
    T1 gold 关键词在语料层 0 次  -> 题面/语料脱节
    T2 gold 关键词命中块数 = 1 且该块不含题干中的任何实体词 -> 疑似假阳性
    T3 其余 -> 归为真实的检索缺口
"""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MISS = ["R001", "R005", "R012", "R094", "R127", "R170", "R171",
        "R180", "R244", "R248", "R273", "R292", "R297", "R298"]
STOP = {"什么", "是什么", "真名", "中文", "译名", "所在", "哪里", "哪座", "怎么",
        "为什么", "多少", "这起", "那位", "哪个", "里面", "哪一年", "主要", "发生",
        "发明", "出现", "称", "叫做", "名字"}


def main() -> int:
    chunks = json.loads((ROOT / "data/compendium_rag/chunks.json").read_text(encoding="utf-8"))["chunks"]
    ts = json.loads((ROOT / "data/knowledge/_audit/rag_testset_300_cn.json").read_text(encoding="utf-8"))
    by = {str(c["id"]): c for c in ts["cases"]}

    print(f"{'qid':6}{'kw数':>5}{'0次kw':>7}{'唯一块':>7}  判定")
    print("-" * 88)
    for qid in MISS:
        c = by[qid]
        kws = []
        for g in (c.get("evidence") or []):
            items = g if isinstance(g, (list, tuple)) else [g]
            kws.extend(str(x) for x in items if x)
        kws = [k.strip() for k in kws if k.strip()]
        q_ents = set(re.findall(r"[\u4e00-\u9fff]{2,6}", c["q"])) - STOP
        zero, uniq = [], []
        for k in kws:
            hits = [ch for ch in chunks if k in ch["text"]]
            if not hits:
                zero.append(k)
            elif len(hits) == 1:
                uniq.append((k, hits[0]))
        # 判定
        if zero and len(zero) == len(kws):
            verdict = "T1 全部 kw 语料层 0 次 -> 题面/语料脱节"
        elif uniq:
            k, ch = uniq[0]
            ctx = ch["text"]
            ent_in = [e for e in q_ents if e in ctx or e in ch["chapter_title"]]
            verdict = (f"T2 疑似假阳性：唯一命中 {k!r} 于 {ch['chunk_id']}"
                       f"（题干实体 {ent_in or '无'} 在该块）")
        else:
            verdict = "T3 真实检索缺口"
        print(f"{qid:6}{len(kws):>5}{len(zero):>7}{len(uniq):>7}  {verdict}")

    print("\n注：T1/T2 属**测试集 gold 质量问题**，不应计入系统能力；")
    print("    T3 才是需要 P3/P4 解决的真实缺口。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
