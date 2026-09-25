"""知识层装配工厂。

build_knowledge_base  : 嵌入器 + 落盘向量库。
build_services        : 一次性装配「知识库 + 角色仓库 + 联网检索 + 长期记忆
                        +（可选）剧情图谱注册表」，并把人设同步进知识库，
                        供 lifespan / 依赖注入复用。

剧情图谱（plot 层）与 lore 向量 RAG 相互独立：仅在 plot_graph_enabled 打开时
装配注册表，且注册表只读自己的两个文件（plot_corpus_<cid>.json /
plot_graph_<cid>.json），不触碰 KnowledgeBase。
"""
from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path

from ...config import Settings, get_settings
from .embedder import build_embedder
from .vector_store import KnowledgeBase
from .web_search import build_web_search
from .memory_tier import LongTermMemory
from .character_store import CharacterStore
from .profile import UserProfile
from .plot_graph import PlotGraphRegistry
from .graph_ppr import parse_exempt_sources
from .graph_search import GraphSearchRegistry


@dataclass
class KnowledgeServices:
    knowledge_base: KnowledgeBase
    character_store: CharacterStore
    web_search: object
    long_term_memory: LongTermMemory
    user_profile: UserProfile | None = None
    plot_graph: PlotGraphRegistry | None = None
    graph_registry: GraphSearchRegistry | None = None

    async def aclose(self) -> None:
        """释放嵌入器等长生命周期资源（应用 shutdown 时调用）。"""
        await self.knowledge_base.aclose()


def build_knowledge_base(settings: Settings | None = None) -> KnowledgeBase:
    s = settings or get_settings()
    emb = build_embedder(s)
    return KnowledgeBase(embedder=emb, persist_dir=s.knowledge_dir)


def build_services(settings: Settings | None = None) -> KnowledgeServices:
    s = settings or get_settings()
    kb = build_knowledge_base(s)
    character_store = CharacterStore(settings=s)
    # 人设同步到知识库（检索时可召回相关人设，维持角色一致性）
    # 同步方法可能触发 Chroma/落盘同步 IO：API 层（characters.py）已用
    # asyncio.to_thread 卸载到线程池；应用启动/测试路径在事件循环之外，
    # 无阻塞并发风险。因此这里保持同步调用，由调用方决定执行上下文。
    try:
        character_store.sync_persona_to_kb(kb)
    except Exception as exc:  # noqa: BLE001
        # 某些极简嵌入器未实现 namespace 参数时也尽量兼容
        logger_sync(exc)
    web_search = build_web_search(s)
    ltm = LongTermMemory(
        kb,
        decay_lambda=s.memory_decay_lambda,
        retention_days=s.memory_retention_days,
    )
    profile = UserProfile(
        kb,
        namespace=s.profile_namespace,
        decay_lambda=s.memory_decay_lambda,
        synonym_threshold=s.profile_synonym_threshold,
        reminder_days=s.profile_reminder_days,
        max_items=s.profile_max_items,
        top_k=s.profile_top_k,
    )
    plot_graph: PlotGraphRegistry | None = None
    if getattr(s, "plot_graph_enabled", False):
        try:
            plot_graph = build_plot_registry(s)
        except Exception as exc:  # noqa: BLE001 —— 剧情层永不拖垮主链路
            logging.getLogger(__name__).warning("剧情图谱注册表装配失败：%s", exc)
    graph_registry: GraphSearchRegistry | None = None
    if getattr(s, "graph_enabled", False):
        try:
            graph_registry = build_graph_registry(s, kb)
        except Exception as exc:  # noqa: BLE001 —— 图谱层永不拖垮主链路
            logging.getLogger(__name__).warning("lore 图谱注册表装配失败：%s", exc)
    return KnowledgeServices(
        knowledge_base=kb,
        character_store=character_store,
        web_search=web_search,
        long_term_memory=ltm,
        user_profile=profile,
        plot_graph=plot_graph,
        graph_registry=graph_registry,
    )


def _build_plot_embedder(s: Settings):
    """剧情层嵌入器：``plot_embed_model`` 非空时用它，否则跟随全局 ``embed_model``。

    为什么必须能分开（M8 实测教训）：全局 ``embed_model`` 同时被 lore 向量库使用，
    而 lore 库的向量是按 nomic-embed-text（768 维）建的。为了让剧情语义层用上
    真正跨语言的 bge-m3（1024 维）而把全局一改，lore 检索会因维度失配整体失效。
    分开配置后各用各的，互不影响。
    """
    model = str(getattr(s, "plot_embed_model", "") or "").strip()
    if not model or model == getattr(s, "embed_model", ""):
        return build_embedder(s)
    # 复制一份设置、只换模型名：其余嵌入参数（base_url / timeout）保持一致
    try:
        clone = s.model_copy(update={"embed_model": model})
    except AttributeError:  # pragma: no cover - pydantic v1 兜底
        clone = s.copy(update={"embed_model": model})
    return build_embedder(clone)


def _build_entity_expander(s):
    """按配置构造「查询侧实体扩展器」。

    未启用 / 配置不完整 / 构造异常 ⇒ 一律返回 **None**（等价于功能关闭，零回归）。
    识别后端必须**懂该作品设定**：本地 qwen2.5:7b 实测只有 15.0% 命中率，强模型 62.7%。
    """
    if not bool(getattr(s, "plot_entity_expand_enabled", False)):
        return None
    try:
        from roleplay.core.knowledge.plot_entity_expand import (  # noqa: PLC0415
            EntityExpander, LLMEntityIdentifier, NullIdentifier, StaticMapIdentifier,
        )

        backend = str(getattr(s, "plot_entity_expand_backend", "static") or "static")
        top_k = int(getattr(s, "plot_entity_expand_top", 3))
        if backend == "static":
            path = str(getattr(s, "plot_entity_expand_static_path", "") or "")
            if not path:
                logging.getLogger(__name__).warning(
                    "实体扩展启用了 static 后端但未配置 plot_entity_expand_static_path，"
                    "本次不扩展")
                return None
            ident = StaticMapIdentifier(path)
        elif backend == "llm":
            base = str(getattr(s, "plot_entity_expand_llm_base_url", "")
                       or getattr(s, "llm_base_url", ""))
            key = str(getattr(s, "plot_entity_expand_llm_api_key", "")
                      or getattr(s, "llm_api_key", ""))
            model = str(getattr(s, "plot_entity_expand_llm_model", "")
                        or getattr(s, "llm_model", ""))
            if not (base and model):
                logging.getLogger(__name__).warning(
                    "实体扩展启用了 llm 后端但缺少 base_url/model，本次不扩展")
                return None
            ident = LLMEntityIdentifier(base_url=base, api_key=key, model=model,
                                        top_k=top_k)
        else:
            ident = NullIdentifier()

        exp = EntityExpander(
            identifier=ident,
            top_k=top_k,
            min_conf=float(getattr(s, "plot_entity_expand_min_conf", 0.0)),
            max_append=int(getattr(s, "plot_entity_expand_max_append", 4)),
            enforce_whitelist=bool(getattr(s, "plot_entity_expand_whitelist", True)),
        )
        logging.getLogger(__name__).info(
            "查询侧实体扩展已启用：backend=%s top_k=%d min_conf=%.2f whitelist=%s",
            backend, top_k, exp.min_conf, exp.enforce_whitelist)
        return exp
    except Exception as exc:  # noqa: BLE001 —— 剧情层永不拖垮主链路
        logging.getLogger(__name__).warning("实体扩展器构造失败：%s", exc)
        return None


def build_plot_registry(settings: Settings | None = None) -> PlotGraphRegistry:
    """剧情图谱注册表（独立于 KnowledgeBase / 嵌入器）。"""
    s = settings or get_settings()
    return PlotGraphRegistry(
        corpus_dir=Path(s.plot_corpus_dir),
        graph_dir=Path(s.plot_graph_dir),
        alias_dir=Path(s.plot_lore_dir),
        min_confidence=float(getattr(s, "plot_edge_min_confidence", 0.6)),
        # 默认与 Settings.plot_include_weak 一致（True）：真实语料里 99.7% 的边
        # 只有 1 条证据，若为 False 图谱检索几乎无边可用。
        include_weak=bool(getattr(s, "plot_include_weak", True)),
        max_edges=int(getattr(s, "plot_max_edges", 10)),
        max_hops=int(getattr(s, "plot_max_hops", 2)),
        damping=float(getattr(s, "plot_ppr_damping", 0.85)),
        link_threshold=float(getattr(s, "plot_link_threshold", 0.5)),
        # P2 三通道 RRF 融合参数（默认值与 Settings 一致，避免直接构造注册表时行为漂移）
        fuse_k=int(getattr(s, "plot_fuse_k", 3)),
        weight_edge=float(getattr(s, "plot_weight_edge", 1.0)),
        weight_mention=float(getattr(s, "plot_weight_mention", 1.0)),
        weight_lexical=float(getattr(s, "plot_weight_lexical", 0.6)),
        diversity_per_doc=int(getattr(s, "plot_diversity_per_doc", 1)),
        mention_cache_size=int(getattr(s, "plot_mention_cache_size", 512)),
        # P3 种子门控
        require_anchored_token_seeds=bool(
            getattr(s, "plot_require_anchored_token_seeds", True)
        ),
        filter_generic_seeds=bool(getattr(s, "plot_filter_generic_seeds", True)),
        mention_scoring=str(getattr(s, "plot_mention_scoring", "count")),
        cooccurrence_bonus=bool(getattr(s, "plot_cooccurrence_bonus", True)),
        mention_group_by_entity=bool(getattr(s, "plot_mention_group_by_entity", True)),
        alias_trust_ratio=float(getattr(s, "plot_alias_trust_ratio", 0.25)),
        untrusted_extra_per_entity=int(
            getattr(s, "plot_untrusted_extra_per_entity", 1)
        ),
        weight_mention_entity=float(getattr(s, "plot_weight_mention_entity", 1.0)),
        entity_query_max_len=int(getattr(s, "plot_entity_query_max_len", 14)),
        alias_trust_chained_min_df=int(
            getattr(s, "plot_alias_trust_chained_min_df", 3)
        ),
        name_salience=bool(getattr(s, "plot_name_salience", False)),
        ppr_max_iter=int(getattr(s, "plot_ppr_max_iter", 20)),
        # M7 篇章路由
        chapter_routing=bool(getattr(s, "plot_chapter_routing", True)),
        chapter_top=int(getattr(s, "plot_chapter_top", 3)),
        chapter_max_names=int(getattr(s, "plot_chapter_max_names", 2)),
        weight_chapter=float(getattr(s, "plot_weight_chapter", 1.0)),
        lexical_topup=bool(getattr(s, "plot_lexical_topup", False)),
        lexical_always=bool(getattr(s, "plot_lexical_always", False)),
        mention_per_entity=int(getattr(s, "plot_mention_per_entity", 3)),
        mention_total_cap=int(getattr(s, "plot_mention_total_cap", 6)),
        # M8 语义通道：嵌入器在此构建一次，索引加载由注册表按 mtime 懒加载 + 指纹校验。
        # 剧情层可单独指定模型（plot_embed_model）——全局 embed_model 同时被 lore 向量库
        # 使用，而 lore 向量是按旧模型维度建的，一改就整体失配。
        embedder=_build_plot_embedder(s),
        semantic_enabled=bool(getattr(s, "plot_semantic_enabled", True)),
        semantic_top=int(getattr(s, "plot_semantic_top", 5)),
        weight_semantic=float(getattr(s, "plot_weight_semantic", 1.0)),
        semantic_link_min=float(getattr(s, "plot_semantic_link_min", 0.0)),
        semantic_link_top=int(getattr(s, "plot_semantic_link_top", 3)),
        semantic_langs=str(getattr(s, "plot_semantic_langs", "") or ""),
        semantic_min_score=float(getattr(s, "plot_semantic_min_score", 0.0)),
        # P1-4 召回率修复：融合层保底保留名额（语义/篇章两通道各自至少入选 N 块）
        min_semantic_kept=int(getattr(s, "plot_min_semantic_kept", 0)),
        min_chapter_kept=int(getattr(s, "plot_min_chapter_kept", 0)),
        # 60 题 never_candidate 专项：融合后语义补位重排（默认关 = 现状逐位一致）
        rerank_topup_enabled=bool(getattr(s, "plot_rerank_topup_enabled", False)),
        rerank_topup_keep=int(getattr(s, "plot_rerank_topup_keep", 3)),
        # P0-1 / P0-4：弱证豁免来源集合（逗号分隔 -> frozenset）+ node specificity 开关
        exempt_sources=parse_exempt_sources(
            getattr(s, "plot_weak_exempt_sources", "manual")
        ),
        node_specificity=bool(getattr(s, "plot_ppr_node_specificity", False)),
        trace_enabled=bool(getattr(s, "plot_trace_enabled", False)),
        # 查询侧实体扩展（默认关；构造失败返回 None ⇒ 零回归）
        entity_expander=_build_entity_expander(s),
        trace_dir=Path(getattr(s, "plot_corpus_dir", "./data/knowledge")),
        # P4 人工别名表权威性（仅剧情层；lore 层保持 GraphStore 默认 skip 语义）
        alias_authoritative=bool(getattr(s, "plot_alias_authoritative", True)),
    )


def logger_sync(exc: Exception) -> None:  # pragma: no cover - 防御性日志
    import logging

    logging.getLogger(__name__).warning("人设同步到知识库时异常：%s", exc)


def build_graph_registry(
    settings: Settings | None = None, kb: KnowledgeBase | None = None
) -> GraphSearchRegistry:
    """lore 图谱检索注册表（复用 KnowledgeBase 做证据回查 + 实体名向量链接）。"""
    s = settings or get_settings()
    if kb is None:
        kb = build_knowledge_base(s)
    embedder = getattr(kb, "_emb", None)
    return GraphSearchRegistry(
        directory=s.graph_dir,
        kb=kb,
        embedder=embedder,
        min_confidence=float(getattr(s, "graph_edge_min_confidence", 0.55)),
        include_weak=bool(getattr(s, "graph_include_weak", False)),
        link_threshold=float(getattr(s, "graph_entity_link_threshold", 0.82)),
        damping=float(getattr(s, "graph_ppr_damping", 0.85)),
        max_iter=int(getattr(s, "graph_ppr_max_iter", 50)),
        max_hops=int(getattr(s, "graph_max_hops", 2)),
        max_edges=int(getattr(s, "graph_max_edges", 12)),
        top_chunks=int(getattr(s, "graph_max_chunks", 3)),
    )
