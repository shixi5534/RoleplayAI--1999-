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
