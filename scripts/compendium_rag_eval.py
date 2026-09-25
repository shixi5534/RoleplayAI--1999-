# -*- coding: utf-8 -*-
"""新库检索质量评测（只针对 compendium_rag，不涉及既有系统）。

评测协议
--------
- **金标准**：题目由 Compendium 语料本身构造，每题的 ``expect_any`` 是
  该题答案应当出现的**章节/场景关键词**（人工从语料确认真值），
  ``expect_entities`` 是应当被链接到的图谱实体。
- **指标**：
  - ``seed_recall``：期望实体被正确链接的比例（实体链接能力）
  - ``hit@k``：top-k 证据块中命中任一期望关键词的比例（检索能力）
  - ``MRR``：首个命中块的排名倒数均值
  - ``graph_only``：纯图谱（关闭向量通道）时的 hit@k —— 用于判断图谱本身是否有效
  - ``evidence_grounded``：返回块确实出自语料（防幻觉）
- 题目覆盖**单跳属性**、**多跳关系**、**跨篇章**三类。
"""
from __future__ import annotations

import asyncio
import json
import logging
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from compendium_rag import pipeline as P  # noqa: E402
from compendium_rag.config import get_settings  # noqa: E402

logger = logging.getLogger("eval")


@dataclass
class Case:
    qid: str
    query: str
    kind: str                 # 单跳 | 多跳 | 跨篇章
    expect_any: list[str]     # 证据块中应出现的关键词（任一命中即可）
    expect_entities: list[str] = field(default_factory=list)
    note: str = ""


# 题目人工从 vendor 语料核对而来（章节名/场景名/角色名均可在语料中检索到）
CASES: list[Case] = [
    # ── 单跳：主角身份与归属 ──
    Case("s1", "维尔汀是谁，她属于哪个组织？", "单跳",
         ["维尔汀", "基金会"], ["维尔汀", "圣洛夫基金会"],
         "主角身份，应命中主线语料"),
    Case("s2", "星锑的船叫什么名字？", "单跳",
         ["APPLe", "星锑"], ["星锑"],
         "主角船名，序章出现"),
    Case("s3", "伊索尔德是谁？", "单跳",
         ["伊索尔德"], ["伊索尔德"],
         "106 今夜星光灿烂登场角色"),
    Case("s4", "重塑之手是什么组织？", "单跳",
         ["重塑之手"], ["重塑之手"],
         "主要敌对组织"),

    # ── 多跳：需要跨实体连线 ──
    Case("m1", "星锑和重塑之手之间发生了什么冲突？", "多跳",
         ["星锑", "重塑之手", "炮击", "APPLe"], ["星锑", "重塑之手"],
         "序章海盗船被炮击"),
    Case("m2", "伊索尔德在诊疗中遭遇了什么？", "多跳",
         ["伊索尔德", "施瓦茨", "电击", "诊疗"], ["伊索尔德"],
         "106 电疗场景"),
    Case("m3", "雾行者的父亲是做什么的？", "多跳",
         ["雾行者", "父亲", "福葛"], ["雾行者"],
         "轶事 1901 角色故事"),
    Case("m4", "J和玛蒂尔达是什么关系？", "多跳",
         ["J", "玛蒂尔达"], ["J", "玛蒂尔达"],
         "飞驰！明日之城 2.0 角色"),

    # ── 跨篇章 ──
    Case("c1", "有哪些角色隶属于圣洛夫基金会？", "跨篇章",
         ["基金会"], ["圣洛夫基金会", "基金会"],
         "需要跨多篇聚合"),
    Case("c2", "暴雨是什么？", "跨篇章",
         ["暴雨"], ["暴雨"],
         "世界观核心概念，多篇出现"),
    Case("c3", "维尔汀和十四行诗一起出现过吗？", "跨篇章",
         ["维尔汀", "十四行诗"], ["维尔汀", "十四行诗"],
         "跨篇章共现"),
    Case("c4", "使徒米修斯是谁？", "跨篇章",
         ["使徒米修斯", "受苦者"], ["使徒米修斯"],
         "飞驰！明日之城 反派"),
    Case("c5", "海特街在哪里被提到？", "跨篇章",
         ["海特街", "J", "保利娜"], ["海特街"],
         "J 的家乡"),
]


async def run_case(kb, case: Case, top_k: int, use_vector: bool) -> dict:
    t0 = time.time()
    res = await kb.retrieve(case.query, top_k=top_k, use_vector=use_vector)
    dt = time.time() - t0

    seed_names = [s["name"] for s in res.get("seeds", [])]
    seed_hits = [e for e in case.expect_entities
                 if any(e == n or e in n or n in e for n in seed_names)]
    seed_recall = len(seed_hits) / len(case.expect_entities) \
        if case.expect_entities else 1.0

    rr = 0.0
    hit = False
    for rank, ev in enumerate(res.get("evidence", [])[:top_k], start=1):
        c = kb.retriever.chunks.get(ev["chunk_id"])
        blob = (c.text if c else "") + (c.chapter_title if c else "") + \
               (c.scene_title if c else "")
        if any(k in blob for k in case.expect_any):
            hit = True
            if rr == 0.0:
                rr = 1.0 / rank
            break

    # 证据必须出自语料（防幻觉）
    grounded = all(ev["chunk_id"] in kb.retriever.chunks
                   for ev in res.get("evidence", [])[:top_k])

    return {
        "qid": case.qid, "kind": case.kind, "query": case.query,
        "seeds": seed_names, "seed_hits": seed_hits,
        "seed_recall": seed_recall, "hit": hit, "rr": rr,
        "n_evidence": len(res.get("evidence", [])),
        "n_edges": len(res.get("edges", [])),
        "grounded": grounded, "seconds": round(dt, 3),
        "note": res.get("note", ""),
    }


async def main() -> int:
    logging.basicConfig(level=logging.WARNING)
    s = get_settings()
    top_k = int(sys.argv[1]) if len(sys.argv) > 1 else 6
    print(f"加载库：{s.data_dir}")
    kb = P.load_kb(s)
    gst = kb.graph.stats()
    print(f"图谱：实体={gst['entities']} 边={gst['edges']} "
          f"孤立率={gst['isolated_ratio']}")
    print(f"块数={len(kb.chunks)} 块索引="
          f"{kb.chunk_index.size if kb.chunk_index else 0} 实体索引="
          f"{len(kb.entity_index.eids) if kb.entity_index else 0}")

    rows = []
    for mode, use_vec in (("full", True), ("graph_only", False)):
        print(f"\n{'=' * 80}\n模式：{mode}（top_k={top_k}）\n{'=' * 80}")
        for case in CASES:
            r = await run_case(kb, case, top_k, use_vec)
            r["mode"] = mode
            rows.append(r)
            mark = "✓" if r["hit"] else "✗"
            print(f"  {mark} [{r['kind']}] {r['qid']:<4} "
                  f"seed={r['seed_recall']:.2f} rr={r['rr']:.2f} "
                  f"ev={r['n_evidence']} edges={r['n_edges']} "
                  f"{r['seconds']:.2f}s  {r['query'][:34]}")
            if not r["hit"]:
                print(f"       期望含：{case.expect_any}｜种子：{r['seeds'][:5]}")

    # 汇总
    summary = {}
    for mode in ("full", "graph_only"):
        sub = [r for r in rows if r["mode"] == mode]
        n = len(sub) or 1
        summary[mode] = {
            "cases": len(sub),
            "hit@k": round(sum(1 for r in sub if r["hit"]) / n, 4),
            "MRR": round(sum(r["rr"] for r in sub) / n, 4),
            "seed_recall": round(sum(r["seed_recall"] for r in sub) / n, 4),
            "grounded": round(sum(1 for r in sub if r["grounded"]) / n, 4),
            "avg_seconds": round(sum(r["seconds"] for r in sub) / n, 3),
        }
        by_kind = {}
        for r in sub:
            d = by_kind.setdefault(r["kind"], {"n": 0, "hit": 0})
            d["n"] += 1
            d["hit"] += 1 if r["hit"] else 0
        summary[mode]["by_kind"] = {
            k: round(v["hit"] / v["n"], 3) for k, v in by_kind.items()}

    print(f"\n{'=' * 80}\n汇总\n{'=' * 80}")
    print(json.dumps(summary, ensure_ascii=False, indent=2))

    out = s.reports_dir / "eval_report.json"
    s.ensure_dirs()
    out.write_text(json.dumps({"summary": summary, "cases": [c.__dict__
                                                             for c in CASES],
                               "graph_stats": gst, "rows": rows},
                              ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\n报告 → {out}")
    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
