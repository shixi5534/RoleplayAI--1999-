"""全局配置中心（集中管理，运行时不可变）。

设计要点（对齐 2026 最佳实践）：
- pydantic-settings BaseSettings：单一配置入口，杜绝散落的 os.getenv。
- env_prefix="ROLEPLAY_"：环境变量与代码解耦，生产用真实环境变量注入。
- extra="ignore"：容忍 .env 中的无关项（脚手架阶段更友好）。
- frozen=True：配置仅在启动时解析一次，运行期不可篡改（防意外副作用）。
- 默认 llm_provider="mock"：无需任何 API Key 即可离线运行与测试。
"""
from functools import lru_cache
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="ROLEPLAY_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        frozen=True,
    )

    app_name: str = "RoleplayAI"
    debug: bool = False

    # ---- LLM ----
    llm_provider: Literal["mock", "openai", "deepseek", "ollama"] = "mock"
    llm_model: str = "mock-model"
    llm_api_key: str = ""
    llm_base_url: str = ""
    llm_temperature: float = 0.8

    # ---- 情感 / Live2D ----
    enable_emotion: bool = True
    enable_live2d: bool = False
    live2d_model_path: str = ""  # model3.json 所在目录（相对或绝对）
    live2d_default_model_id: str = "wmz_314701"

    # ---- 情感检测升级（15 类 + LLM/分类器辅助）----
    # auto = LLM 可用(非mock且api_key非空)时 LLM→classifier→keyword；
    #        LLM 不可用且分类器可用时 classifier→keyword；否则 keyword
    emotion_detector: Literal["keyword", "classifier", "llm", "auto"] = "auto"
    emotion_llm_timeout: float = 8.0  # LLM 检测调用超时（秒），独立于对话生成超时
    emotion_confidence_threshold: float = 0.4  # LLM/分类器结果置信度下限；低于则下沉下一级
    emotion_classifier_backend: Literal["hashing", "jina"] = "hashing"  # P1.5 时切 jina
    emotion_jina_model: str = "jina-embeddings-v2-base-zh"

    # ---- RAG ----
    rag_impl: Literal["memory", "chroma"] = "memory"
    chroma_persist_dir: str = "./data/chroma"
    chunk_size: int = 600
    top_k: int = 3
    rag_hybrid: bool = True  # 稠密向量 + BM25 稀疏混合重排（提升检索精度）
    rag_hybrid_alpha: float = 0.3  # 混合权重：final = (1-alpha)*dense + alpha*bm25
    rag_hybrid_candidates: int = 12  # 进入重排的稠密候选数（top_k 的倍数空间）

    # ---- 嵌入 / 持久化知识库 ----
    embedder: Literal["ollama", "hashing"] = "ollama"
    embed_model: str = "nomic-embed-text"
    embed_dim: int = 768
    ollama_base_url: str = ""  # 留空则用 llm_base_url 或默认 http://localhost:11434
    knowledge_dir: str = "./data/knowledge"  # 知识库（向量+文本）持久化目录
    characters_dir: str = "./data/characters"  # 多角色人设持久化目录

    # ---- 分层记忆（长期 / 短期） ----
    memory_decay_lambda: float = 0.05  # 长期记忆每日衰减系数（exp(-λ·天数)）
    memory_retention_days: int = 60  # 长期记忆最长保留天数（超期低分则清理）
    longterm_consolidate_every: int = 6  # 每 N 轮对话合并一次长期记忆
    event_extract_enabled: bool = True  # 结构化事实/事件提取（升级方案 C）；关闭则整段合并

    # ---- 用户画像（UserProfile） ----
    profile_enabled: bool = True  # 总开关
    profile_extract_every: int = 10  # 每 N 轮提取一次画像（独立于 longterm_consolidate_every）
    profile_top_k: int = 5  # 每轮注入画像条数上限
    profile_max_items: int = 200  # 画像条目硬上限（超出淘汰低 importance）
    profile_llm_timeout: float = 8.0  # LLM 提取超时（秒），独立于对话生成
    profile_synonym_threshold: float = 0.85  # 同义判定相似度阈值
    profile_reminder_days: int = 3  # important_date 提醒窗口（±天）
    profile_namespace: str = "profile"  # 画像命名空间（预留 profile:<uid>）

    # ---- 联网 / Web RAG ----
    enable_web: bool = True
    # duckduckgo=免key DDG（部分网络不可达）；bing=免key Bing（国内可达，推荐）；
    # tavily=需 key 的 Tavily API（最稳）。默认 duckduckgo，运行时自动回退 bing。
    web_provider: Literal["duckduckgo", "bing", "tavily"] = "duckduckgo"
    tavily_api_key: str = ""
    web_max_results: int = 5
    web_fetch_content: bool = True  # 联网时是否抓取页面正文（更准但更慢）

    # ---- 角色卡 / 对话记忆 ----
    character_card_path: str = ""  # 留空则使用内置默认角色卡（无名者）
    enable_session_memory: bool = True  # 跨轮次/跨会话记住对话
    session_memory_dir: str = "./data/sessions"  # 记忆持久化目录
    prompt_config_path: str = ""  # 全局提示词拼装配置 JSON（留空=默认，输出与改造前一致）

    # ---- 安全 / 限流 ----
    max_message_length: int = 4000
    max_tokens_per_reply: int = 2000
    rate_limit_per_minute: int = 60  # <=0 表示关闭限流
    cors_origins: str = "*"  # 允许跨域的前端源（逗号分隔；* 表示全部，生产应收紧）

    # ---- 资料导入边界（防任意文件读 / SSRF）----
    # 允许导入的本地根目录（逗号分隔）；API 层对 path 做 realpath 收敛，越界即拒。
    ingest_allowed_roots: str = "./data/knowledge"
    # 允许 URL 导入的主机白名单（逗号分隔，空=禁止一切 URL 导入）；仅 https。
    allowed_ingest_hosts: str = ""
    # 是否开启联网导入（/web-ingest 与 ingest type=url）；生产默认关。
    enable_url_ingest: bool = False

    # ---- 体验优化（可配置） ----
    enable_dynamic_followups: bool = False  # 由 LLM 动态生成后续追问（默认关闭，用静态兜底）
    enable_history_summary: bool = True  # 对话历史超阈值时自动摘要，避免上下文溢出
    history_summary_threshold: int = 40  # 触发摘要的历史消息条数阈值

    # ---- 语音（STT / TTS 后端，均为可选回退） ----
    # 默认全部关闭：前端优先用浏览器原生 Web Speech API；
    # 仅当显式开启后，/api/voice/* 才走后端适配器（Whisper / Edge-TTS）。
    stt_backend_enabled: bool = False
    whisper_model: str = "base"  # faster-whisper 模型大小: tiny/base/small/medium/large-v3
    whisper_model_path: str = ""  # 本地模型目录路径（为空则用 faster-whisper 内置下载）
    tts_backend_enabled: bool = False
    edge_tts_default_voice: str = "zh-CN-XiaoxiaoNeural"
    tts_default_format: str = "mp3"
    voice_request_timeout: float = 30.0  # 语音后端调用超时（秒）


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """解析并缓存配置单例；测试中调用 get_settings.cache_clear() 重置。"""
    return Settings()
