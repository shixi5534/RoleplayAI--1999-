# -*- coding: utf-8 -*-
"""剧情图谱构建 CLI（GraphRAG 存实际剧情，独立于 lore 向量 RAG）。

数据源：``data/lore/<角色>/视频文案/`` 下的机器转写 md（B站 whisper 转写，
含中英混排；9 份手工整理 md 在角色目录根，天然被三重白名单排除）。

产物（全部独立于 lore 层，不写 KnowledgeBase、不依赖嵌入器）：
  data/knowledge/plot_corpus_<cid>.json  剧情语料（文本 + 剧情元数据，无向量）
  data/knowledge/plot_graph_<cid>.json   剧情图谱（实体/边/别名/证据 hash）
  data/knowledge/plot_cache/<cid>/       抽取缓存（chunk hash → 抽取结果，幂等续跑）

用法（项目根目录执行）：
  python scripts/build_plot_graph.py --character wu_ming_zhe --build-corpus
  python scripts/build_plot_graph.py --character wu_ming_zhe --stats
  python scripts/build_plot_graph.py --character wu_ming_zhe --build-graph --limit 20
  python scripts/build_plot_graph.py --character wu_ming_zhe --build-graph --lang en --limit 100
  python scripts/build_plot_graph.py --character wu_ming_zhe --mine-entities
  python scripts/build_plot_graph.py --character wu_ming_zhe --rebuild
"""
from __future__ import annotations

import argparse
import asyncio
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from roleplay.config import get_settings  # noqa: E402
from roleplay.core.knowledge.graph_extract import GraphCache, GraphExtractor  # noqa: E402
from roleplay.core.knowledge.graph_store import GraphStore  # noqa: E402
from roleplay.core.knowledge.plot_corpus import (  # noqa: E402
    PlotCorpus,
    plot_namespace,
)
from roleplay.core.knowledge.plot_graph import (  # noqa: E402
    PLOT_GRAPH_SCHEMA,
    build_plot_graph,
    load_alias_table_with_stats,
    mine_entity_candidates,
)

# no-op 判定：图谱文件存在且构建前后「sha256 + 实体数 + 边数」一次都没变，
# 说明这一轮抽取没产出任何新东西（缓存全命中 / LLM 全失败 / 抽取器静默空转）。
NOOP_EXIT_CODE = 2


def _paths(settings, character_id: str) -> tuple[Path, Path, Path, Path]:
    """(语料源目录, 语料落盘, 图谱落盘, 缓存目录)"""
    src = Path(settings.plot_lore_dir) / character_id / "视频文案"
    corpus = Path(settings.plot_corpus_dir) / f"plot_corpus_{character_id}.json"
    graph = Path(settings.plot_graph_dir) / f"plot_graph_{character_id}.json"
    cache = Path(settings.plot_cache_dir) / character_id
    return src, corpus, graph, cache


def _sha256(path: Path) -> str:
    """文件 sha256（分块读，避免大图谱一次性进内存）。"""
    digest = hashlib.sha256()
    try:
        with path.open("rb") as fp:
            for block in iter(lambda: fp.read(1 << 20), b""):
                digest.update(block)
    except OSError:
        return ""
    return digest.hexdigest()


def _is_noop(before: dict, after: dict) -> bool:
    """no-op 判定：图谱文件前后都存在，且 sha256 / 实体数 / 边数一次都没变。"""
    return bool(
        before.get("exists")
        and after.get("exists")
        and before.get("sha256")
        and before.get("sha256") == after.get("sha256")
        and before.get("entities") == after.get("entities")
        and before.get("edges") == after.get("edges")
    )


def _graph_snapshot(path: Path) -> dict:
    """图谱文件的「内容指纹 + 规模」快照（no-op 判定用）。

    只数不做实体级 diff：size/sha256 已足够判定"一次都没变"，且对 5000 实体级
    的图谱零额外开销。
    """
    if not path.exists():
        return {"exists": False, "sha256": "", "entities": 0, "edges": 0, "size": 0}
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        # 解析失败也记快照（sha256 仍有效）：让 no-op 判定不被损坏文件带偏
        raw = {}
    entities = raw.get("entities") if isinstance(raw, dict) else None
    edges = raw.get("edges") if isinstance(raw, dict) else None
    return {
        "exists": True,
        "sha256": _sha256(path),
        "entities": len(entities) if isinstance(entities, dict) else 0,
        "edges": len(edges) if isinstance(edges, list) else 0,
        "size": path.stat().st_size,
    }


def _cmd_build_corpus(settings, character_id: str, chunk_size: int) -> int:
    src, cpath, _gpath, _cache = _paths(settings, character_id)
    if not src.is_dir():
        print(f"[error] 转写目录不存在：{src}")
        return 1
    corpus = PlotCorpus(cpath, character_id=character_id)
    stat = corpus.build(src, chunk_size=chunk_size)
    corpus.save()
    print(f"[corpus] 源目录 {src}")
    print(
        f"[corpus] 文件 {stat['files']}（采纳 {stat['kept']} / 拒绝 {stat['rejected']}）"
        f"→ 切块 {stat['chunks']} 条"
    )
    if stat["rejected_samples"]:
        print(f"[corpus] 被拒样例（非转写产物）：{stat['rejected_samples']}")
    print(f"[corpus] 语种分布 {stat['by_lang']}")
    print(f"[corpus] 来源分级 {stat.get('by_source_kind') or {}}")
    print(f"[corpus] 落盘 {cpath}（{cpath.stat().st_size / 1024:.0f} KB）")
    return 0


def _cmd_stats(settings, character_id: str) -> int:
    _src, cpath, gpath, cache_dir = _paths(settings, character_id)
    if cpath.exists():
        print(f"[corpus] {json.dumps(PlotCorpus(cpath).stats(), ensure_ascii=False, indent=2)}")
    else:
        print(f"[corpus] 未构建：{cpath}")
    if gpath.exists():
        store = GraphStore(gpath)
        print(f"[graph]  {json.dumps(store.stats(), ensure_ascii=False, indent=2)}")
    else:
        print(f"[graph]  未构建：{gpath}")
    n_cache = len(list(cache_dir.glob("*.json"))) if cache_dir.exists() else 0
    print(f"[cache]  {n_cache} 条（{cache_dir}）")
    return 0


def _cmd_mine(settings, character_id: str, top_n: int) -> int:
    """挖掘英文专名候选，生成人工/LLM 译名对照草稿（中文别名表的关键输入）。"""
    _src, cpath, _gpath, _cache = _paths(settings, character_id)
    if not cpath.exists():
        print("[error] 请先 --build-corpus")
        return 1
    corpus = PlotCorpus(cpath, character_id=character_id)
    cands = mine_entity_candidates(corpus, top_n=top_n)
    out = ROOT / "data" / "knowledge" / f"plot_entity_candidates_{character_id}.md"
    lines = [
        f"# 剧情实体候选（英文专名 → 中文译名对照草稿）",
        "",
        f"- 角色：{character_id} ｜ 候选数：{len(cands)} ｜ 来源：英文转写块词频统计",
        "- 用法：确认后把译名填进 `data/lore/<cid>/plot_aliases.json`",
        "  （格式 {\"中文名\": [\"English Name\", ...]}），重建图谱时自动归并。",
        "",
        "| # | 英文候选 | 频次 | 中文译名（待填） |",
        "|---|---|---|---|",
    ]
    for i, (name, n) in enumerate(cands, 1):
        lines.append(f"| {i} | {name} | {n} |  |")
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"[mine] {len(cands)} 条候选 → {out}")
    return 0


def _build_extract_llm(settings):
    """抽取专用 LLM 客户端：与对话主模型解耦，且放宽 max_tokens。

    对话默认 240 token 会把抽取 JSON 截断（实测 third-party 输出被切成
    ``{"entities":[{"n``），故剧情抽取单独用一个大 max_tokens 的实例。
    """
    from roleplay.core.llm.factory import build_llm
    from roleplay.core.llm.openai_like import OpenAILikeProvider, _DEFAULT_BASE_URLS

    if settings.llm_provider == "mock":
        return build_llm(settings)
    base_url = settings.llm_base_url or _DEFAULT_BASE_URLS.get(settings.llm_provider, "")
    api_key = settings.llm_api_key or ("ollama" if settings.llm_provider == "ollama" else "")
    return OpenAILikeProvider(
        model=settings.llm_model,
        api_key=api_key,
        base_url=base_url,
        max_tokens=int(settings.plot_extract_max_tokens),
    )


class _ReplayOnlyExtractor:
    """零 LLM 重放专用抽取器：永不发起模型调用，缓存未命中即判失败。

    ``build_plot_graph`` 只在缓存 miss 时才调 ``extract``，返回 ``None`` 会让该块
    计入 ``stats["failed"]`` 并跳过——正好是「只重放已有抽取结果」要的语义。
    """

    available = True

    async def extract(self, text: str, system: str | None = None):  # noqa: ARG002
        return None


async def _cmd_build_graph(
    settings,
    character_id: str,
    limit: int | None,
    lang: str | None,
    rebuild: bool,
    allow_noop: bool = False,
    rebuild_graph_only: bool = False,
) -> int:
    _src, cpath, gpath, cache_dir = _paths(settings, character_id)
    if not cpath.exists():
        print("[error] 请先 --build-corpus")
        return 1
    corpus = PlotCorpus(cpath, character_id=character_id)
    if not corpus.chunks:
        print("[error] 剧情语料为空")
        return 1
    # no-op 判定的「前」快照必须在 --rebuild 删图之前取，否则永远判不出来
    before = _graph_snapshot(gpath)
    cache = GraphCache(cache_dir)
    if rebuild_graph_only:
        # 只重建图谱、保住缓存（删图但不 clear）。
        # 这是别名归并（M1）**唯一能真正生效**的路径：在旧图上 bind_alias_table
        # 会因 first-write-wins 把已被其它实体占用的别名全部跳过，脚本仍报成功
        # ——即 B2「静默 no-op」。必须先删图，让别名表成为首个注册者。
        if gpath.exists():
            gpath.unlink()
        print("[rebuild-graph-only] 已删除旧图谱，抽取缓存保留")
    if rebuild:
        n = cache.clear()
        if gpath.exists():
            gpath.unlink()
        print(f"[rebuild] 清缓存 {n} 条 + 删除旧图谱")

    store = GraphStore(
        gpath,
        min_confidence=float(getattr(settings, "plot_edge_min_confidence", 0.6)),
    )
    # 双语别名表（人工权威，最高归并优先级）
    alias_file = Path(settings.plot_lore_dir) / character_id / "plot_aliases.json"
    table, alias_stats = load_alias_table_with_stats(alias_file)
    if table:
        n = store.bind_alias_table(table)
        print(
            f"[alias] 绑定双语别名 {n} 条（{alias_file}）"
            f"｜条目 {alias_stats['kept']}/{alias_stats['total']}"
            f"｜跳过元数据键 {alias_stats['dropped_underscore']}"
            f"｜丢弃非法类型 {alias_stats['dropped_bad_type']}"
        )
        if store.alias_ambiguous_dropped:
            print(
                f"[alias][warn] {store.alias_ambiguous_dropped} 条别名因已被其他实体"
                "占有而跳过（首注册优先，需人工合并）"
            )
    else:
        print(f"[alias] 未找到双语别名表（可选）：{alias_file}")
    if store.load_error:
        print(f"[error] 图谱加载失败，已拒绝落盘（防空图覆盖）：{store.load_error}")
        return 1

    if rebuild_graph_only:
        extractor = _ReplayOnlyExtractor()
        miss = [c.hash for c in corpus.chunks if cache.get(c.hash) is None]
        hit = len(corpus.chunks) - len(miss)
        print(
            f"[rebuild-graph-only] 缓存覆盖 {hit}/{len(corpus.chunks)} 块"
            "｜零 LLM，未命中块直接跳过"
        )
        if miss:
            print(f"[rebuild-graph-only][warn] {len(miss)} 块无缓存，本次不会写入")
            print(f"[rebuild-graph-only] 缺失样例：{miss[:5]}")
    else:
        llm = _build_extract_llm(settings)
        extractor = GraphExtractor(llm=llm, timeout=float(settings.plot_extract_timeout))
        if not extractor.available:
            print("[error] LLM 不可用：请设置 ROLEPLAY_LLM_PROVIDER/ROLEPLAY_LLM_MODEL")
            return 1
    ns = plot_namespace(character_id)
    print(
        f"[graph] 开始构建：语料 {len(corpus.chunks)} 块"
        + (f"（仅 {lang} 块）" if lang else "")
        + (f"｜limit {limit}" if limit else "")
        + f"｜并发 {settings.plot_extract_concurrency}｜ns={ns}"
    )
    stats = await build_plot_graph(
        corpus,
        store,
        extractor,
        cache,
        namespace=ns,
        batch=int(settings.plot_extract_concurrency),
        limit=limit,
        only_lang=lang,
    )
    store.set_fingerprint(
        embedder="none", embed_dim=0, extract_llm=f"{settings.llm_provider}:{settings.llm_model}"
    )
    store.save()
    print(
        f"[graph] 完成：{json.dumps(stats, ensure_ascii=False)}"
    )
    # 两道口径都要看：store.load_error（本次落盘被拒）+ stats["save_error"]
    # （build_plot_graph 内部那次 save() 被拒）。任一非空都不能报「落盘成功」。
    if store.load_error or stats.get("save_error"):
        print(
            "[error] 图谱加载失败，已拒绝落盘（防空图覆盖）："
            f"{store.load_error or stats.get('save_error')}"
        )
        return 1
    print(f"[graph] 落盘 {gpath}（schema={PLOT_GRAPH_SCHEMA}）")
    # ── no-op 检测（M0-4）：跑了一大轮却一个字节都没变 = 白跑，明确报错 ──
    after = _graph_snapshot(gpath)
    # --rebuild 与 --rebuild-graph-only 都是「先删图再重建」，同内容属正常，不判 no-op
    if not rebuild and not rebuild_graph_only and _is_noop(before, after):
        print(
            "[no-op][warn] 图谱构建前后完全一致："
            f"sha256={after['sha256'][:12]}…｜实体 {after['entities']}｜边 {after['edges']}"
            "｜本轮抽取零新增（缓存全命中 / LLM 全失败 / 抽取器静默空转）"
        )
        if allow_noop:
            print("[no-op] 已由 --allow-noop 豁免")
            return 0
        print(f"[no-op] 退出码 {NOOP_EXIT_CODE}（确认无碍可加 --allow-noop 豁免）")
        return NOOP_EXIT_CODE
    print(
        f"[graph] 规模变化：实体 {before['entities']}→{after['entities']}"
        f"｜边 {before['edges']}→{after['edges']}"
    )
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="剧情图谱（GraphRAG）构建 CLI")
    ap.add_argument("--character", default="wu_ming_zhe", help="角色 id")
    ap.add_argument("--build-corpus", action="store_true", help="扫描转写目录重建剧情语料")
    ap.add_argument("--build-graph", action="store_true", help="LLM 抽取实体关系构建图谱")
    ap.add_argument("--stats", action="store_true", help="查看语料/图谱/缓存统计")
    ap.add_argument("--mine-entities", action="store_true", help="挖掘英文专名候选（译名对照草稿）")
    ap.add_argument("--rebuild", action="store_true", help="配合 --build-graph：清缓存与旧图谱")
    ap.add_argument(
        "--rebuild-graph-only",
        action="store_true",
        help="配合 --build-graph：只删图谱、保留抽取缓存，零 LLM 重放重建。"
        "别名表改动后必须用这个才生效（否则合并会被 first-write-wins 静默跳过）",
    )
    ap.add_argument(
        "--allow-noop",
        action="store_true",
        help="豁免 no-op 检测：图谱构建前后完全一致时仍返回 0（默认返回 2）",
    )
    ap.add_argument("--limit", type=int, help="只处理前 N 块（分批/试跑）")
    ap.add_argument("--lang", choices=["zh", "en", "other"], help="只处理指定语种块")
    ap.add_argument("--chunk-size", type=int, default=600, help="切块字符数")
    ap.add_argument("--top", type=int, default=300, help="--mine-entities 候选条数")
    args = ap.parse_args()

    if args.rebuild and args.rebuild_graph_only:
        ap.error("--rebuild 与 --rebuild-graph-only 互斥（前者清缓存，后者保留）")

    settings = get_settings()
    if args.build_corpus:
        return _cmd_build_corpus(settings, args.character, args.chunk_size)
    if args.mine_entities:
        return _cmd_mine(settings, args.character, args.top)
    if args.build_graph:
        return asyncio.run(
            _cmd_build_graph(
                settings,
                args.character,
                args.limit,
                args.lang,
                args.rebuild,
                allow_noop=args.allow_noop,
                rebuild_graph_only=args.rebuild_graph_only,
            )
        )
    if args.stats:
        return _cmd_stats(settings, args.character)
    ap.print_help()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
