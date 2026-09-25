# -*- coding: utf-8 -*-
"""Compendium GraphRAG 命令行入口。

用法：
    python -m compendium_rag.cli corpus          # 解析语料并落盘 + 统计
    python -m compendium_rag.cli chunks          # 分块统计
    python -m compendium_rag.cli sample -n 3     # 抽样预览块与抽取提示词
    python -m compendium_rag.cli extract -n 20   # 小批量抽取质量验证
    python -m compendium_rag.cli build           # 全量构建（云端抽取 + 图谱 + 索引）
    python -m compendium_rag.cli stats           # 图谱统计
    python -m compendium_rag.cli query "…"       # 检索
    python -m compendium_rag.cli entity "…"      # 实体邻域
"""
from __future__ import annotations

import argparse
import asyncio
import json
import logging
import sys
from pathlib import Path

from .chunker import chunk_corpus, chunks_stats
from .config import get_settings
from .corpus import corpus_fingerprint, corpus_stats
from .extract import PROMPT_VERSION, build_user_prompt, SYSTEM_PROMPT
from .graph_store import fingerprint_of
from . import pipeline as P


def _setup_log(verbose: bool) -> None:
    logging.basicConfig(
        level=logging.DEBUG if verbose else logging.INFO,
        format="%(asctime)s %(levelname)-7s %(message)s",
        datefmt="%H:%M:%S")


def cmd_corpus(args) -> int:
    s = get_settings()
    chapters, st = P.build_corpus(s, write=True)
    print(f"语料落盘 → {s.corpus_path}")
    print(json.dumps(st, ensure_ascii=False, indent=2)[:2500])
    return 0


def cmd_chunks(args) -> int:
    s = get_settings()
    chunks = P.load_chunks(s)
    st = chunks_stats(chunks)
    print(json.dumps(st, ensure_ascii=False, indent=2))
    if args.write:
        P.save_chunks(chunks, s.data_dir / "chunks.json")
        print(f"分块落盘 → {s.data_dir / 'chunks.json'}")
    return 0


def cmd_sample(args) -> int:
    s = get_settings()
    chunks = P.load_chunks(s)
    step = max(1, len(chunks) // max(1, args.n))
    for i in range(0, len(chunks), step):
        c = chunks[i]
        print("=" * 78)
        print(f"chunk_id={c.chunk_id}  chars={len(c.text)}  turns={c.n_turns}")
        print(f"chapter={c.chapter_title} | {c.part_title} | {c.scene_title}")
        print(f"speakers={c.speakers[:10]}")
        print("-" * 78)
        print(c.text[:1400])
    print("\n" + "=" * 78)
    print("SYSTEM PROMPT:")
    print(SYSTEM_PROMPT)
    return 0


async def _extract_sample(args) -> int:
    s = get_settings()
    chunks = P.load_chunks(s)
    step = max(1, len(chunks) // max(1, args.n))
    picked = [chunks[i] for i in range(0, len(chunks), step)][:args.n]
    print(f"抽样 {len(picked)} 块，模型={s.llm_model} 并发={s.llm_concurrency}\n")

    out_path = s.reports_dir / "extract_sample.json"
    s.ensure_dirs()
    results, rep = await P.extract_all(
        s.with_(llm_concurrency=args.concurrency), picked,
        limit=None, progress_every=5)
    payload = {"model": s.llm_model, "prompt_version": PROMPT_VERSION,
               "report": rep.to_dict(),
               "summary": P.extraction_summary(results),
               "results": []}
    for c in picked:
        ex = results.get(c.chunk_id)
        payload["results"].append({
            "chunk_id": c.chunk_id, "chapter": c.chapter_title,
            "scene": c.scene_title, "chars": len(c.text),
            "speakers": c.speakers[:10],
            "extraction": ex.to_dict() if ex else None})
    out_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2),
                        encoding="utf-8")

    sumry = P.extraction_summary(results)
    print(json.dumps(sumry, ensure_ascii=False, indent=2))
    print(f"\n报告 → {out_path}")
    print("\n--- 抽样明细 ---")
    for r in payload["results"]:
        ex = r["extraction"] or {}
        if not ex.get("ok", False):
            print(f"\n[{r['chunk_id']}] FAILED: {ex.get('error')}")
            continue
        ents = ex.get("entities", [])
        rels = ex.get("relations", [])
        print(f"\n[{r['chunk_id']}] {r['chapter']} / {r['scene']} "
              f"({r['chars']}字) → {len(ents)}实体 {len(rels)}关系")
        print("  实体: " + "、".join(
            f"{e['name']}({e['type']})" for e in ents[:14]))
        for x in rels[:10]:
            print(f"   · {x['src']} —{x['relation']}→ {x['dst']} "
                  f"({x['confidence']}) 「{x['evidence'][:36]}」")
    print("\nusage:", json.dumps(rep.usage, ensure_ascii=False))
    return 0


def cmd_extract(args) -> int:
    return asyncio.run(_extract_sample(args))


async def _build(args) -> int:
    s = get_settings()
    s.ensure_dirs()
    chapters, cstats = P.build_corpus(s, write=True)
    chunks = chunk_corpus(chapters, s)
    P.save_chunks(chunks, s.data_dir / "chunks.json")
    print(f"[1/4] 语料 {cstats['chapters']} 篇 / {cstats['turns']:,} 行 / "
          f"{cstats['chars']:,} 字 → {len(chunks):,} 块")

    api_key = s.llm_api_key
    if not api_key:
        print("错误：未配置 CMPRAG_LLM_API_KEY 或 ROLEPLAY_LLM_API_KEY", file=sys.stderr)
        return 2

    print(f"[2/4] 云端抽取（模型={s.llm_model} 并发={s.llm_concurrency} "
          f"块数={len(chunks):,}）…")
    results, rep = await P.extract_all(s, chunks)
    sumry = P.extraction_summary(results)
    print("       " + json.dumps(sumry, ensure_ascii=False))
    print("       " + json.dumps(rep.usage, ensure_ascii=False))
    if rep.stages.get("quota_exhausted"):
        print("\n  ⚠ 抽取因**整批性故障**提前结束（云端额度耗尽 / 网关不可达）。")
        print(f"    本次成功 {sumry['ok']} 块，已全部落缓存；"
              f"剩余 {sumry['failed']} 块待补。")
        print("    排除故障后重跑 `build` 即可**续传**（已完成块零成本跳过）。")
        print("    本次仍用已成功的部分建图，产物可用但覆盖不完整。\n")

    print("[3/4] 构图…")
    graph, gstats = P.build_graph(s, chunks, results)
    ok, why = P.safe_save_graph(graph, s.graph_path)
    if ok:
        print("       " + json.dumps(gstats, ensure_ascii=False)[:600])
        print(f"       图谱 → {s.graph_path}")
    else:
        print(f"       ⚠ {why}")
        print("       已保留原图谱不动。请先补齐抽取再重跑 build。")

    print("[4/4] 向量索引（本地 bge-m3）…")
    istats = await P.build_indexes(s, chunks, graph)
    print("       " + json.dumps(istats, ensure_ascii=False))

    report = {"corpus": cstats, "chunks": chunks_stats(chunks),
              "extract": rep.to_dict(), "extract_summary": sumry,
              "graph": gstats, "index": istats,
              "fingerprint": graph.fingerprint}
    rp = s.reports_dir / "build_report.json"
    rp.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\n构建完成，报告 → {rp}")
    return 0


def cmd_build(args) -> int:
    return asyncio.run(_build(args))


def cmd_rebuild(args) -> int:
    """只用本地抽取缓存重建图谱（零云端调用）。

    用途：调整去噪 / 实体归并规则后立即生效，不必重跑昂贵的云端抽取。
    """
    s = get_settings()
    chunks = P.load_chunks(s)
    graph, gstats, info = P.rebuild_from_cache(s, chunks)
    print(f"缓存：命中 {info['cached']}/{info['chunks']} "
          f"缺失 {info['missing']}")
    if info["missing"]:
        print(f"注意：{info['missing']} 块无缓存，未参与建图")
    ok, why = P.safe_save_graph(graph, s.graph_path)
    if not ok:
        print(f"⚠ {why}")
        return 1
    print(json.dumps(gstats, ensure_ascii=False, indent=2)[:900])
    print(f"\n图谱 → {s.graph_path}")
    print(f"指纹 → {graph.fingerprint}")
    return 0


def cmd_stats(args) -> int:
    s = get_settings()
    kb = P.load_kb(s)
    print(json.dumps(kb.graph.stats(), ensure_ascii=False, indent=2))
    ok, why = P.verify_fingerprint(s, kb.graph)
    print(f"\nfingerprint: {'OK' if ok else 'MISMATCH'} — {why}")
    print(f"chunks={len(kb.chunks)} chunk_index={kb.chunk_index.size if kb.chunk_index else 0} "
          f"entity_index={len(kb.entity_index.eids) if kb.entity_index else 0}")
    return 0


async def _query(args) -> int:
    s = get_settings()
    kb = P.load_kb(s)
    res = await kb.retrieve(args.text, top_k=args.top_k,
                            use_vector=not args.no_vector)
    if args.json:
        print(json.dumps(res, ensure_ascii=False, indent=2))
        return 0
    print(f"查询：{res['query']}\n")
    print("种子实体：")
    for x in res["seeds"]:
        print(f"  - {x['name']} ({x['how']}, {x['score']:.3f})")
    if not res["seeds"]:
        print("  （无）")
    print("\n关系脉络：")
    for e in res["edges"][:14]:
        print(f"  {e['src']} —{e['relation']}→ {e['dst']}  ppr={e['ppr']:.3f}")
    print("\n证据块：")
    for e in res["evidence"][:args.top_k]:
        c = kb.retriever.chunks.get(e["chunk_id"])
        loc = f"{c.chapter_title}/{c.scene_title}" if c else "?"
        print(f"  [{e['chunk_id']}] score={e['score']:.5f} "
              f"channels={e['channels']} ppr={e['ppr']:.3f}")
        print(f"      {loc}")
        if c:
            print("      " + c.text[:180].replace("\n", " / "))
    return 0


def cmd_query(args) -> int:
    return asyncio.run(_query(args))


def cmd_entity(args) -> int:
    s = get_settings()
    kb = P.load_kb(s)
    g = kb.graph
    eid = g.resolve(args.name)
    if not eid:
        hits = [e for e in g.entities.values() if args.name in e.name][:20]
        if not hits:
            print(f"未找到实体：{args.name}")
            return 1
        print(f"未精确命中，模糊匹配 {len(hits)} 个：")
        for e in hits:
            print(f"  - {e.name} ({e.type}) mentions={e.mentions}")
        return 0
    ent = g.entities[eid]
    print(f"实体：{ent.name}  [{ent.type}]  mentions={ent.mentions}")
    print(f"别名：{'、'.join(ent.aliases) or '（无）'}")
    print(f"说明：{ent.desc or '（无）'}")
    print(f"提及块：{len(ent.chunk_ids)}")
    edges = g.neighbors(eid)
    print(f"\n邻居（{len(edges)} 条边）：")
    for e in sorted(edges, key=lambda x: -x.confidence)[:args.limit]:
        other = e.dst if e.src == eid else e.src
        arrow = f"{e.src} —{e.relation}→ {e.dst}"
        print(f"  {arrow}   conf={e.confidence:.2f} count={e.count}")
        if e.evidence:
            print(f"      证据：{e.evidence[:60]}")
    return 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="compendium_rag",
                                 description="Compendium GraphRAG 独立库")
    ap.add_argument("-v", "--verbose", action="store_true")
    sub = ap.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("corpus", help="解析语料并落盘")
    p.set_defaults(fn=cmd_corpus)

    p = sub.add_parser("chunks", help="分块统计")
    p.add_argument("--write", action="store_true")
    p.set_defaults(fn=cmd_chunks)

    p = sub.add_parser("sample", help="抽样预览")
    p.add_argument("-n", type=int, default=3)
    p.set_defaults(fn=cmd_sample)

    p = sub.add_parser("extract", help="小批量抽取质量验证")
    p.add_argument("-n", type=int, default=20)
    p.add_argument("--concurrency", type=int, default=6)
    p.set_defaults(fn=cmd_extract)

    p = sub.add_parser("build", help="全量构建")
    p.set_defaults(fn=cmd_build)

    p = sub.add_parser("rebuild", help="只用本地缓存重建图谱（零云端调用）")
    p.set_defaults(fn=cmd_rebuild)

    p = sub.add_parser("stats", help="图谱统计")
    p.set_defaults(fn=cmd_stats)

    p = sub.add_parser("query", help="检索")
    p.add_argument("text")
    p.add_argument("--top-k", type=int, default=6)
    p.add_argument("--no-vector", action="store_true")
    p.add_argument("--json", action="store_true")
    p.set_defaults(fn=cmd_query)

    p = sub.add_parser("entity", help="实体邻域")
    p.add_argument("name")
    p.add_argument("--limit", type=int, default=25)
    p.set_defaults(fn=cmd_entity)

    args = ap.parse_args(argv)
    _setup_log(args.verbose)
    return args.fn(args)


if __name__ == "__main__":
    sys.exit(main())
