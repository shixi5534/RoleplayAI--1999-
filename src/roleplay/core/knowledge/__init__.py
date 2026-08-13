"""持久化知识库与分层记忆层。

组成：
- embedder    : 文本向量化（Ollama 本地嵌入，失败回退 hashing）
- vector_store: 落盘的多命名空间向量库（KnowledgeBase，实现 VectorStore 接口）
- web_search  : 联网检索端口（DuckDuckGo 免 key / Tavily 需 key）
- ingest      : 联网结果切块→嵌入→入库
- memory_tier : 长期记忆合并 + 衰减 + 保留策略
- character_store: 多角色人设 CRUD + 激活 + 人设同步到知识库

设计目标：纯标准库、可离线运行、重启不丢、与现有 VectorStore/Orchestrator 兼容。
"""
from .embedder import EmbedderPort, HashingEmbedder, OllamaEmbedder, build_embedder
from .vector_store import KnowledgeBase
from .web_search import (
    BingAdapter,
    DuckDuckGoAdapter,
    FallbackWebSearch,
    TavilyAdapter,
    WebResult,
    WebSearchPort,
    build_web_search,
)
from .ingest import ingest_web
from .document_ingest import (
    chunk_markdown,
    ingest_directory,
    ingest_file,
    ingest_sqlite,
    ingest_url,
    lore_namespace,
    preprocess_text,
)
from .memory_tier import LongTermMemory
from .character_store import CharacterStore
from .profile_models import (
    PROFILE_TYPE_LABELS,
    ProfileEntry,
    ProfileType,
    normalize_key,
    now_iso,
)
from .profile import UserProfile
from .extractors import (
    LLMProfileExtractor,
    RuleProfileExtractor,
    build_profile_extractors,
    extract_profile_entries,
)
from .factory import KnowledgeServices, build_knowledge_base, build_services

__all__ = [
    "EmbedderPort",
    "HashingEmbedder",
    "OllamaEmbedder",
    "build_embedder",
    "KnowledgeBase",
    "BingAdapter",
    "DuckDuckGoAdapter",
    "FallbackWebSearch",
    "TavilyAdapter",
    "WebResult",
    "WebSearchPort",
    "build_web_search",
    "ingest_web",
    "chunk_markdown",
    "ingest_directory",
    "ingest_file",
    "ingest_sqlite",
    "ingest_url",
    "lore_namespace",
    "preprocess_text",
    "LongTermMemory",
    "CharacterStore",
    "ProfileEntry",
    "ProfileType",
    "PROFILE_TYPE_LABELS",
    "normalize_key",
    "now_iso",
    "UserProfile",
    "RuleProfileExtractor",
    "LLMProfileExtractor",
    "build_profile_extractors",
    "extract_profile_entries",
    "KnowledgeServices",
    "build_knowledge_base",
    "build_services",
]
