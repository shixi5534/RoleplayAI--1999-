"""API 层依赖注入：把配置 + 端口适配器装配成 Orchestrator 与知识层服务。

装配发生在应用 lifespan（见 main.py），产物存入 app.state，供路由通过 Depends 注入。
- app.state.orchestrator：对话编排器（含知识库/角色仓库/联网/长期记忆）
- app.state.services：知识层服务单例（角色仓库、知识库、联网检索、长期记忆）

测试可用 FastAPI 的 dependency_overrides 替换为 Mock 实现。
"""
from pathlib import Path

from fastapi import Depends, Request

from ..config import Settings, get_settings
from ..core.character_repo import CharacterRepo
from ..core.emotion.detector import build_emotion_detector
from ..core.emotion.mapping import Live2DEmotionMapper
from ..core.knowledge import (
    CharacterStore,
    KnowledgeBase,
    KnowledgeServices,
    build_knowledge_base,
    build_services,
)
from ..core.knowledge.memory_tier import LongTermMemory
from ..core.llm.factory import build_llm
from ..core.orchestrator import ChatOrchestrator
from ..core.rag.factory import build_vector_store
from ..core.session_memory import SessionMemory


def build_orchestrator(
    settings: Settings | None = None,
    services: KnowledgeServices | None = None,
) -> ChatOrchestrator:
    """构建编排器（重型依赖）。services 为空时自行装配知识层。"""
    s = settings or get_settings()
    if services is None:
        services = build_services(s)
    mapper = (
        Live2DEmotionMapper(s.live2d_model_path or None)
        if s.enable_live2d
        else None
    )
    character_repo = CharacterRepo(
        Path(s.character_card_path) if s.character_card_path else None
    )
    session_memory = (
        SessionMemory(Path(s.session_memory_dir)) if s.enable_session_memory else None
    )
    return ChatOrchestrator(
        llm=build_llm(s),
        emotion=build_emotion_detector(enabled=s.enable_emotion, settings=s),
        rag=build_vector_store(s),
        knowledge_base=services.knowledge_base,
        character_store=services.character_store,
        web_search=services.web_search,
        memory_tier=services.long_term_memory,
        mapper=mapper,
        top_k=s.top_k,
        temperature=s.llm_temperature,
        enable_emotion=s.enable_emotion,
        enable_web=s.enable_web,
        enable_longterm=True,
        web_max_results=s.web_max_results,
        web_fetch_content=s.web_fetch_content,
        chunk_size=s.chunk_size,
        consolidate_every=s.longterm_consolidate_every,
        rag_hybrid=s.rag_hybrid,
        rag_hybrid_alpha=s.rag_hybrid_alpha,
        rag_hybrid_candidates=s.rag_hybrid_candidates,
        enable_dynamic_followups=s.enable_dynamic_followups,
        enable_history_summary=s.enable_history_summary,
        history_summary_threshold=s.history_summary_threshold,
        user_profile=services.user_profile,
        enable_profile=s.profile_enabled,
        profile_extract_every=s.profile_extract_every,
        profile_top_k=s.profile_top_k,
        enable_event_extract=s.event_extract_enabled,
        model_id=s.live2d_default_model_id or None,
        character_repo=character_repo,
        session_memory=session_memory,
    )


def get_orchestrator_dep(request: Request) -> ChatOrchestrator:
    """FastAPI 依赖入口：优先取 lifespan 注入的 app.state，缺失则回退构建。

    回退结果缓存到 app.state，否则每次请求都新建 LLM 客户端（连接池无人 aclose）
    + 新建 SessionMemory（内存泄漏）；且与 get_services_dep 回退建的是两套实例，
    chat 与 characters/knowledge 接口操作不同角色仓库，写入互相不可见。
    注意：本函数是同步 def，FastAPI 会在线程池中执行，因此内部同步构建
    （人设入库 / Chroma 连接等阻塞 IO）不会阻塞事件循环。
    """
    orch = getattr(request.app.state, "orchestrator", None)
    if orch is None:
        orch = build_orchestrator()
        request.app.state.orchestrator = orch  # 缓存，避免每请求重建
    return orch


def get_services_dep(request: Request) -> KnowledgeServices:
    svc = getattr(request.app.state, "services", None)
    if svc is None:
        svc = build_services()
        request.app.state.services = svc  # 缓存，避免每请求重建 + 与 orchestrator 回退实例分离
    return svc


def get_character_store_dep(request: Request) -> CharacterStore:
    return get_services_dep(request).character_store


def get_knowledge_base_dep(request: Request) -> KnowledgeBase:
    return get_services_dep(request).knowledge_base


def get_web_search_dep(request: Request):
    return get_services_dep(request).web_search


def get_long_term_memory_dep(request: Request) -> LongTermMemory:
    return get_services_dep(request).long_term_memory


def get_settings_dep(request: Request) -> Settings:
    return get_settings()
