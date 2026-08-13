"""知识层装配工厂。

build_knowledge_base  : 嵌入器 + 落盘向量库。
build_services        : 一次性装配「知识库 + 角色仓库 + 联网检索 + 长期记忆」，
                        并把人设同步进知识库，供 lifespan / 依赖注入复用。
"""
from __future__ import annotations

from dataclasses import dataclass

from ...config import Settings, get_settings
from .embedder import build_embedder
from .vector_store import KnowledgeBase
from .web_search import build_web_search
from .memory_tier import LongTermMemory
from .character_store import CharacterStore
from .profile import UserProfile


@dataclass
class KnowledgeServices:
    knowledge_base: KnowledgeBase
    character_store: CharacterStore
    web_search: object
    long_term_memory: LongTermMemory
    user_profile: UserProfile | None = None


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
    return KnowledgeServices(
        knowledge_base=kb,
        character_store=character_store,
        web_search=web_search,
        long_term_memory=ltm,
        user_profile=profile,
    )


def logger_sync(exc: Exception) -> None:  # pragma: no cover - 防御性日志
    import logging

    logging.getLogger(__name__).warning("人设同步到知识库时异常：%s", exc)
