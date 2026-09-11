# -*- coding: utf-8 -*-
"""lore 知识图谱构建 CLI（GraphRAG 数据底座，离线、幂等、可重跑）。

数据源：``lore_<cid>``（+ ``lore_<cid>_spoken``）向量库里的**文本块**。
产物：``data/knowledge/graph_<cid>.json``（实体 / 边 / 别名索引 / 证据 hash / 指纹）。

与剧情图谱（``build_plot_graph.py``）的区别：本层证据回查走 KnowledgeBase，
实体名向量用于在线链接（故落盘前会为实体名预计算向量）。

用法（项目根目录执行）：
  python scripts/build_graph.py --character wu_ming_zhe --stats
  python scripts/build_graph.py --character wu_ming_zhe --dry-run --limit 5
  python scripts/build_graph.py --character wu_ming_zhe --build
  python scripts/build_graph.py --character wu_ming_zhe --rebuild
  python scripts/build_graph.py --character wu_ming_zhe --build --namespaces lore_wu_ming_zhe

幂等：每个 chunk 的文本 sha1 作为缓存键，重跑只处理新增/变更块（缓存命中不调 LLM）。
"""
from __future__ import annotations

import argparse
import asyncio
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from roleplay.config import get_settings  # noqa: E402
from roleplay.core.knowledge.character_store import CharacterStore  # noqa: E402
from roleplay.core.knowledge.embedder import build_embedder  # noqa: E402
from roleplay.core.knowledge.graph_extract import (  # noqa: E402
    GraphCache,
    GraphExtractor,
    build_graph_from_chunks,
)
from roleplay.core.knowledge.graph_store import (  # noqa: E402
    GRAPH_SCHEMA_VERSION,
    GraphStore,
)
from roleplay.core.knowledge.vector_store import KnowledgeBase  # noqa: E402


def _paths(settings, character_id: str) -> tuple[Path, Path]:
    """(图谱落盘, 缓存目录)"""
    return (
        Path(settings.graph_dir) / f"graph_{character_id}.json",
        Path(settings.graph_cache_dir) / character_id,
    )


def _default_namespaces(character_id: str) -> list[str]:
    return [f"lore_{character_id}", f"lore_{character_id}_spoken"]


def _load_chunks(kb: KnowledgeBase, namespaces: list[str]) -> list[tuple[str, dict]]:
    """从向量库读取待抽取块（注入 namespace/doc_id 供证据溯源）。"""
    out: list[tuple[str, dict]] = []
    for ns in namespaces:
        items = kb.list_items(ns)
        for it in items:
            text = str(it.get("text") or "").strip()
            if not text:
                continue
            meta = dict(it.get("meta") or {})
            out.append(
                (
                    text,
                    {
                        "ns": ns,
                        # build_graph_from_chunks 读的是 "namespace" 键；历史上只传了
                        # "ns" 导致全部证据 ns 落到兜底 "lore"，lore 层证据回查恒空。
                        "namespace": ns,
                        "doc_id": str(meta.get("doc_id") or meta.get("title") or ns),
                    },
                )
            )
    return out


def _build_extract_llm(settings):
    """抽取专用 LLM 客户端（放宽 max_tokens：默认 240 会把抽取 JSON 截断）。"""
    from roleplay.core.llm.factory import build_llm
    from roleplay.core.llm.openai_like import OpenAILikeProvider, _DEFAULT_BASE_URLS

    if settings.llm_provider == "mock":
        return build_llm(settings)
    base_url = settings.llm_base_url or _DEFAULT_BASE_URLS.get(settings.llm_provider, "")
    api_key = settings.llm_api_key or (
        "ollama" if settings.llm_provider == "ollama" else ""
    )
    return OpenAILikeProvider(
        model=settings.llm_model,
        api_key=api_key,
        base_url=base_url,
        max_tokens=int(settings.graph_extract_max_tokens),
    )


def _cmd_stats(settings, character_id: str) -> int:
    gpath, cache_dir = _paths(settings, character_id)
    if gpath.exists():
        store = GraphStore(gpath)
        print(f"[graph] {json.dumps(store.stats(), ensure_ascii=False, indent=2)}")
    else:
        print(f"[graph] 未构建：{gpath}")
    n_cache = len(list(cache_dir.glob("*.json"))) if cache_dir.exists() else 0
    print(f"[cache] {n_cache} 条（{cache_dir}）")
    return 0


def _cmd_dry_run(settings, character_id: str, namespaces: list[str], limit: int) -> int:
    kb = KnowledgeBase(embedder=build_embedder(settings), persist_dir=settings.knowledge_dir)
    chunks = _load_chunks(kb, namespaces)
    if not chunks:
        print(f"[error] 命名空间为空：{namespaces}")
        return 1
    extractor = GraphExtractor(
        llm=_build_extract_llm(settings), timeout=float(settings.graph_extract_timeout)
    )
    if not extractor.available:
        print("[error] LLM 不可用：请设置 ROLEPLAY_LLM_PROVIDER/ROLEPLAY_LLM_MODEL")
        return 1
    print(f"[dry-run] 抽样 {min(limit, len(chunks))} / {len(chunks)} 块（不落盘）")
    for text, meta in chunks[: max(1, limit)]:
        result = asyncio.run(extractor.extract(text))
        print(f"\n--- {meta['ns']} / {meta['doc_id']} ---")
        print(text[:120].replace("\n", " "))
        print(json.dumps(result, ensure_ascii=False))
    return 0


def _cmd_build(
    settings,
    character_id: str,
    namespaces: list[str],
    limit: int | None,
    rebuild: bool,
) -> int:
    gpath, cache_dir = _paths(settings, character_id)
    kb = KnowledgeBase(embedder=build_embedder(settings), persist_dir=settings.knowledge_dir)
    chunks = _load_chunks(kb, namespaces)
    if not chunks:
        print(f"[error] 命名空间为空：{namespaces}（请先导入 lore 资料）")
        return 1
    cache = GraphCache(cache_dir)
    if rebuild:
        n = cache.clear()
        if gpath.exists():
            gpath.unlink()
        print(f"[rebuild] 清缓存 {n} 条 + 删除旧图谱")
    store = GraphStore(
        gpath, min_confidence=float(settings.graph_edge_min_confidence)
    )
    # 角色卡 entity_aliases（人工权威别名表，最高归并优先级）
    try:
        card = CharacterStore(settings=settings).get(character_id)
        aliases = getattr(card, "entity_aliases", None) if card else None
        if aliases:
            n = store.bind_alias_table(aliases)
            print(f"[alias] 绑定角色卡别名 {n} 条")
    except Exception as exc:  # noqa: BLE001 —— 别名表缺失不影响构建
        print(f"[alias] 跳过（{exc}）")

    extractor = GraphExtractor(
        llm=_build_extract_llm(settings), timeout=float(settings.graph_extract_timeout)
    )
    if not extractor.available:
        print("[error] LLM 不可用：请设置 ROLEPLAY_LLM_PROVIDER/ROLEPLAY_LLM_MODEL")
        return 1
    print(
        f"[graph] 开始构建：{len(chunks)} 块"
        + (f"｜limit {limit}" if limit else "")
        + f"｜并发 {settings.graph_extract_batch}"
    )
    stats = asyncio.run(
        build_graph_from_chunks(
            chunks,
            store,
            extractor,
            cache,
            batch=int(settings.graph_extract_batch),
            limit=limit,
        )
    )
    print(f"[graph] {json.dumps(stats, ensure_ascii=False)}")
    # 实体名向量（在线链接用；失败不阻断落盘）
    emb = build_embedder(settings)
    n_vec = store.ensure_entity_vectors(emb)
    print(f"[graph] 实体向量 {n_vec} 条")
    store.set_fingerprint(
        embedder=getattr(emb, "name", ""),
        embed_dim=int(getattr(emb, "_dim", 0) or settings.embed_dim),
        extract_llm=f"{settings.llm_provider}:{settings.llm_model}",
    )
    store.save()
    if store.load_error:
        # save() 内部会因「文件损坏/结构非法」直接 return（M0-2 安全网），
        # 一个字节都没写。不检查就会打印「落盘成功」并返回 0 —— 安静的假成功。
        print(f"[error] 图谱加载失败，已拒绝落盘（防空图覆盖）：{store.load_error}")
        return 1
    print(
        f"[graph] 落盘 {gpath}（schema={GRAPH_SCHEMA_VERSION}，"
        f"实体 {len(store.entities())}，边 {len(store.all_edges())}）"
    )
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="lore 知识图谱构建（GraphRAG）")
    parser.add_argument("--character", required=True, help="角色 id，如 wu_ming_zhe")
    parser.add_argument("--namespaces", default="", help="逗号分隔；默认 lore_<cid>,lore_<cid>_spoken")
    parser.add_argument("--build", action="store_true", help="构建/增量构建")
    parser.add_argument("--rebuild", action="store_true", help="清缓存 + 重建")
    parser.add_argument("--dry-run", action="store_true", help="抽样预览抽取 JSON，不落盘")
    parser.add_argument("--limit", type=int, default=None, help="仅处理前 N 块")
    parser.add_argument("--stats", action="store_true", help="查看图谱统计")
    args = parser.parse_args(argv)

    settings = get_settings()
    cid = args.character.strip()
    namespaces = (
        [x.strip() for x in args.namespaces.split(",") if x.strip()]
        if args.namespaces
        else _default_namespaces(cid)
    )
    if args.stats:
        return _cmd_stats(settings, cid)
    if args.dry_run:
        return _cmd_dry_run(settings, cid, namespaces, args.limit or 5)
    if args.build or args.rebuild:
        return _cmd_build(settings, cid, namespaces, args.limit, args.rebuild)
    parser.print_help()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
