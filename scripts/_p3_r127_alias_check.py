# -*- coding: utf-8 -*-
"""P3 验证：R127 的「福格先生」是否为「福葛先生」的**别名缺口**？补 alias 能否救回？

背景：
  - R4 已把 `福葛先生` 并入 `雾行者`（R4 提案记载「雾行者含福葛先生+福葛伙计」）。
  - R127 问「福格先生发明的大型装置是什么？」，gold = purifier/净化机/purification，
    语料层只有 1 块含该词（mainline__105_洞穴的囚徒:13.0.0）。
  - link() 种子为空 -> 零种子题。

判据（预注册）：
  1. 语料里 13.0.0 块是否同时含「福格」与「purifier/净化机」？
  2. `雾行者` 实体是否已有含该块的 chunk_ids？若无，则补 chunk + alias 才有效。
  3. 补 alias「福格先生」后，link() 是否得到 雾行者 种子，且该题是否进 top-6？

只读诊断；若结论成立则给出**最小提案**（add_alias + add_chunk_ids），不直接写图。
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from compendium_rag import pipeline as P                      # noqa: E402
from compendium_rag.config import get_settings                # noqa: E402


def main() -> int:
    s = get_settings()
    kb = P.load_kb(s)
    g = kb.graph
    chunks = {c.chunk_id: c for c in kb.chunks}

    TARGET = "mainline__105_洞穴的囚徒:13.0.0"
    print("=== 1) 目标块内容核查 ===")
    ch = chunks.get(TARGET)
    if ch is None:
        print(f"  [FAIL] 块不存在: {TARGET}")
        return 1
    t = ch.text
    for kw in ("福格", "福葛", "purifier", "purification", "净化"):
        idx = t.find(kw)
        print(f"  含 {kw!r}: {idx >= 0}  "
              f"{('…' + t[max(0, idx-40):idx+60] + '…') if idx >= 0 else ''}")

    print("\n=== 2) 雾行者 实体状态 ===")
    ent = g.entities.get("雾行者")
    if ent is None:
        print("  [FAIL] 无 雾行者 实体")
        return 1
    print(f"  name={ent.name}  aliases={ent.aliases}")
    print(f"  n_chunks={len(ent.chunk_ids)}  含目标块: {TARGET in ent.chunk_ids}")
    print(f"  别名含 福格先生? {'福格先生' in ent.aliases}")
    print(f"  别名含 福葛先生? {'福葛先生' in ent.aliases}")

    print("\n=== 3) 当前 link() 行为 ===")
    r = kb.retriever
    for q in ("福格先生发明的大型装置是什么？", "福葛先生发明的大型装置是什么？"):
        seeds = r.link(q, top_k=6)
        print(f"  {q!r:44} -> {[(x.eid, x.how) for x in seeds]}")

    print("\n=== 4) 模拟补 alias 后的效果（内存内，不写盘）===")
    import copy
    g2 = copy.deepcopy(g)
    e2 = g2.entities["雾行者"]
    if "福格先生" not in e2.aliases:
        e2.aliases = sorted(set(e2.aliases) | {"福格先生"})
    if TARGET not in e2.chunk_ids:
        e2.chunk_ids = list(e2.chunk_ids) + [TARGET]
        e2.mentions = len(e2.chunk_ids)
    g2.alias_index["福格先生"] = "雾行者"
    r2 = __import__("compendium_rag.retriever", fromlist=["GraphRetriever"]).GraphRetriever(g2, kb.chunks)
    q = "福格先生发明的大型装置是什么？"
    seeds2 = r2.link(q, top_k=6)
    print(f"  补后 link(): {[(x.eid, x.how) for x in seeds2]}")
    res = r2.retrieve(q, None, top_k=6, lex_weight=1.0)
    blob = {c.chunk_id: f"{c.text}\n{c.chapter_title}\n{c.scene_title}\n{c.part_title}"
            for c in kb.chunks}
    kws = ["purifier", "净化机", "purification"]
    hit = next((i for i, e in enumerate(res.evidence[:6], 1)
                if any(k in blob.get(e.chunk_id, "") for k in kws)), None)
    print(f"  gold 命中名次: {hit if hit else '未进 top-6'}")
    print(f"  前 6 证据块: {[e.chunk_id for e in res.evidence[:6]]}")
    print("\n  结论: " + ("**可救** —— 建议最小提案 add_alias + add_chunk_ids"
                        if hit else "补 alias 后仍未进 top-6（需更多证据或 P4）"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
