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

from pydantic import Field
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
    llm_temperature: float = Field(0.8, ge=0.0, le=2.0)
    # ---- 采样参数（角色扮演质量的关键旋钮）----
    # top_p：行业共识 0.9-0.95 过滤低概率废词。
    llm_top_p: float = Field(0.92, ge=0.0, le=1.0)
    # repetition_penalty：抑制"复读/照背 few-shot 原句/口头禅"。
    # 共识区间 1.05-1.15；**>1.2 为禁区**（会连角色名这类正常重复一起回避）。
    llm_repetition_penalty: float = Field(1.10, ge=1.0, le=2.0)

    # ---- 情感 / Live2D ----
    enable_emotion: bool = True
    enable_live2d: bool = False
    live2d_model_path: str = ""  # model3.json 所在目录（相对或绝对）
    live2d_default_model_id: str = "wmz_314701"

    # ---- 情感检测升级（15 类 + LLM/分类器辅助）----
    # auto = LLM 可用(非mock且api_key非空)时 LLM→classifier→keyword；
    #        LLM 不可用且分类器可用时 classifier→keyword；否则 keyword
    emotion_detector: Literal["keyword", "classifier", "llm", "auto"] = "auto"
    emotion_llm_timeout: float = Field(8.0, gt=0.0)  # LLM 检测调用超时（秒）
    emotion_confidence_threshold: float = Field(0.4, ge=0.0, le=1.0)  # 置信度下限
    emotion_classifier_backend: Literal["hashing", "jina"] = "hashing"  # P1.5 时切 jina
    emotion_jina_model: str = "jina-embeddings-v2-base-zh"

    # ---- RAG ----
    rag_impl: Literal["memory", "chroma"] = "memory"
    chroma_persist_dir: str = "./data/chroma"
    chunk_size: int = Field(600, ge=50, le=20_000)
    # 注入条数：检索在本项目无判别力（实测相关/无关两组原始余弦完全重叠：
    # 0.702 vs 0.695），故用"少注入"代替阈值过滤来降噪。
    top_k: int = Field(2, ge=1, le=100)
    rag_hybrid: bool = True  # 稠密向量 + BM25 稀疏混合重排（提升检索精度）
    # alpha：0=纯 BM25，1=纯向量。角色对话多为口语/改写，语义权重应更高。
    # 行业经验：关键词型 0.3-0.4、语义型 0.7-0.8、均衡 0.5。
    rag_hybrid_alpha: float = Field(0.45, ge=0.0, le=1.0)
    # 混合检索候选池大小：top_k 太小时候选池会被长块"吸引子"占满，
    # 导致真正相关条目（如"暴雨"）漏召。实测 candidate_mult >= 30 才稳定命中，
    # 默认取 30（top_k=2 -> 60 候选，足够覆盖噪声）。
    rag_hybrid_candidates: int = Field(30, ge=1, le=200)

    # ---- 嵌入 / 持久化知识库 ----
    embedder: Literal["ollama", "hashing"] = "ollama"
    embed_model: str = "nomic-embed-text"
    embed_dim: int = Field(768, ge=16, le=32_768)
    ollama_base_url: str = ""  # 留空则用 llm_base_url 或默认 http://localhost:11434
    knowledge_dir: str = "./data/knowledge"  # 知识库（向量+文本）持久化目录
    characters_dir: str = "./data/characters"  # 多角色人设持久化目录

    # ---- 分层记忆（长期 / 短期） ----
    memory_decay_lambda: float = Field(0.05, ge=0.0, le=1.0)
    memory_retention_days: int = Field(60, ge=1, le=3_650)
    longterm_consolidate_every: int = Field(6, ge=1)
    event_extract_enabled: bool = True  # 结构化事实/事件提取（升级方案 C）；关闭则整段合并

    # ---- 用户画像（UserProfile） ----
    profile_enabled: bool = True  # 总开关
    profile_extract_every: int = Field(10, ge=1)
    profile_top_k: int = Field(5, ge=1, le=100)
    profile_max_items: int = Field(200, ge=1, le=100_000)
    profile_llm_timeout: float = Field(8.0, gt=0.0)
    profile_synonym_threshold: float = Field(0.85, ge=0.0, le=1.0)
    profile_reminder_days: int = Field(3, ge=0, le=365)
    profile_namespace: str = "profile"  # 画像命名空间（预留 profile:<uid>）

    # ---- 联网 / Web RAG ----
    enable_web: bool = True
    # duckduckgo=免key DDG（部分网络不可达）；bing=免key Bing（国内可达，推荐）；
    # tavily=需 key 的 Tavily API（最稳）。默认 duckduckgo，运行时自动回退 bing。
    web_provider: Literal["duckduckgo", "bing", "tavily"] = "duckduckgo"
    tavily_api_key: str = ""
    web_max_results: int = Field(5, ge=1, le=50)
    web_fetch_content: bool = True  # 联网时是否抓取页面正文（更准但更慢）

    # ---- 剧情图谱（PlotGraph：GraphRAG 存实际剧情，独立于 lore 向量 RAG） ----
    # 默认关闭：剧情层与 lore 层文件/索引/开关/预算完全隔离，关闭时行为与现状一致。
    plot_graph_enabled: bool = False
    plot_lore_dir: str = "./data/lore"  # 剧情语料源（<dir>/<cid>/视频文案/）
    plot_corpus_dir: str = "./data/knowledge"  # 剧情语料落盘（plot_corpus_<cid>.json）
    plot_graph_dir: str = "./data/knowledge"  # 剧情图谱落盘（plot_graph_<cid>.json）
    plot_cache_dir: str = "./data/knowledge/plot_cache"  # 抽取缓存（按角色分子目录）
    plot_max_chunks: int = Field(3, ge=0, le=20)  # 单次注入剧情证据块上限
    plot_lexical_fallback: int = Field(2, ge=0, le=10)  # 图零命中时的词法兜底条数
    plot_max_edges: int = Field(10, ge=1, le=100)  # 单次参与检索的边上限
    plot_max_hops: int = Field(2, ge=1, le=5)  # 证据边跳距上限
    plot_edge_min_confidence: float = Field(0.6, ge=0.0, le=1.0)
    # 是否启用「孤证」边（evidence < WEAK_EVIDENCE_MIN）。
    # 实测 4302 条边里 4289 条只有 1 条证据（99.7%）——每块独立抽取，同一条边在不同
    # 块里谓语措辞略有差异，几乎无法自然累积到 2 条。默认值 False 会让图谱检索
    # 实际只能用上 13 条边，等于关掉图谱、退化成纯词法兜底。孤证边在检索时已打
    # 0.5 折排序降权，且仍受 plot_edge_min_confidence 约束，故默认改为 True。
    plot_include_weak: bool = True
    # 图谱命中不足 top_chunks 时是否仍用词法兜底补齐（旧行为）。
    # 默认 False：词法兜底只在图谱零命中时启用——BM25 原始分与图谱 PPR 分不同量纲，
    # 补齐会在无关查询上注入大量转写噪声（实测「今天天气怎么样」注入 2 段无关碎片）。
    plot_lexical_topup: bool = False
    plot_context_max_chars: int = Field(1000, ge=0, le=20_000)  # 独立注入预算
    plot_link_threshold: float = Field(0.5, ge=0.0, le=1.0)  # 词元实体链接阈值（0.35 实测过松）
    plot_ppr_damping: float = Field(0.85, ge=0.1, le=0.99)
    # ---- 剧情检索排序（P2：三通道 RRF 融合）----
    # 三条通道分数量纲互不可比（边证据≈0.2 / 提及≈1.2 / 词法 BM25 30–75），
    # 旧实现直接混排排序，导致图结构证据被提及路稳压、且进不了提示词（组内 0.85 相对门）。
    # RRF 只用名次，天然免疫量纲问题。
    # k 必须取**小值**：k=60（RRF 论文默认）时 1/(60+rank) 几乎不随名次变化，
    # 通道权重会完全压过名次——实测 k=60 时边证据霸占全部名额（路径占比 87%），
    # 严格通过率只有 42%；k=3 时两路真正交错，回到 46%（=旧实现水平）。
    plot_fuse_k: int = Field(3, ge=1, le=1000)
    plot_weight_edge: float = Field(1.0, ge=0.0, le=10.0)  # 边证据（结构化关系路径）
    plot_weight_mention: float = Field(1.0, ge=0.0, le=10.0)  # 实体提及块（属性题）
    plot_weight_lexical: float = Field(0.6, ge=0.0, le=10.0)  # 词法兜底（BM25）
    plot_diversity_per_doc: int = Field(1, ge=0, le=10)  # 同一 doc 的软上限（先按此去冗余）
    plot_mention_cache_size: int = Field(512, ge=16, le=100_000)  # 名字命中表缓存条数
    # 提及块打分口径（300 题消融实测）：
    #   count = Σ 权重×出现次数（旧口径）→ 严格通过 46.0%
    #   idf   = Σ 权重×idf×(1+0.3·ln 次数)（稀有名字加权）→ 42.0%
    # 结论：ASR 语料里"反复提到某角色"的块往往就是该角色的主场戏（答案块），
    # 稀有别名命中多为顺带一提——故默认保留旧口径，idf 仅供换语料时复评。
    plot_mention_scoring: Literal["count", "idf"] = "count"
    # 多实体共现加成：块命中 ≥2 个目标实体时 ×(1+0.5·(k−1))（关系/多跳题的答案特征）
    plot_cooccurrence_bonus: bool = True
    # 提及块是否按**实体分组**输出（种子按 PPR 降序 → 邻居，组内按命中分降序）。
    # 旧实现所有提及块共用同一分数、靠稳定排序自然形成该分组；实测（300 题）改为
    # "全局按分数交错"会让严格通过率掉约 6pt，故默认保持分组序。
    plot_mention_group_by_entity: bool = True
    # ---- 剧情检索精度门控（P3：种子卫生）----
    # 词元兜底种子必须被人工别名表锚定：实测 300 题只有 7 题走该路径（种子全是碎片），
    # 而离题问句几乎全靠它蹭上 restaurant / this place 这类实体。
    plot_require_anchored_token_seeds: bool = True
    # 丢弃命中「世界常识泛词」的非锚定种子（天气/经济/故事…），
    # 泛词表见 plot_graph.GENERIC_SEED_NAMES（只收与作品无关的日常词）。
    plot_filter_generic_seeds: bool = True
    # ---- 剧情图谱加载期语义（P4）----
    # 人工别名表冲突时改指人工规范实体（merge），而不是被抽取实体反压（skip）。
    # 仅作用于剧情层；GraphStore 默认仍是 skip，lore 层与既有测试语义不变。
    plot_alias_authoritative: bool = True
    # 并发数：本地 CPU 小模型（7B）实测 8 并发会把单块耗时推过 60s 超时，
    # 默认 4（≈ 单块 20-30s、成功率 >90%）；纯 CPU 机器可 env 调到 2-3。
    plot_extract_concurrency: int = Field(4, ge=1, le=64)
    plot_extract_max_tokens: int = Field(800, ge=64, le=32_768)  # 抽取 JSON 专用（默认 240 会截断）
    plot_extract_timeout: float = Field(60.0, gt=0.0)  # 单块抽取超时（本地 CPU 小模型需放宽）

    # ---- lore 知识图谱（GraphRAG：实体关系子图，独立于剧情层与向量检索） ----
    # 默认关闭（零回归）：关闭 / 图谱文件缺失 / 实体链接零命中 → 静默回退纯向量路径。
    graph_enabled: bool = False
    graph_dir: str = "./data/knowledge"  # graph_<cid>.json 落盘目录
    graph_cache_dir: str = "./data/knowledge/graph_cache"  # 抽取缓存（按角色分子目录）
    graph_max_chunks: int = Field(3, ge=0, le=20)  # 单次注入图谱证据块上限
    graph_max_edges: int = Field(12, ge=1, le=100)  # 单次参与检索的边上限
    graph_max_hops: int = Field(2, ge=1, le=5)  # 证据边跳距上限
    graph_edge_min_confidence: float = Field(0.55, ge=0.0, le=1.0)
    graph_include_weak: bool = False  # lore 层证据较密，孤证边默认不参与
    graph_entity_link_threshold: float = Field(0.82, ge=0.0, le=1.0)  # 实体名向量链接阈值
    graph_ppr_damping: float = Field(0.85, ge=0.1, le=0.99)
    graph_ppr_max_iter: int = Field(50, ge=1, le=500)
    graph_context_max_chars: int = Field(1200, ge=0, le=20_000)  # 关系脉络块独立预算
    graph_extract_batch: int = Field(8, ge=1, le=64)  # 离线抽取并发
    graph_extract_max_tokens: int = Field(800, ge=64, le=32_768)  # 抽取 JSON 专用
    graph_extract_timeout: float = Field(60.0, gt=0.0)  # 单块抽取超时

    # ---- 角色卡 / 对话记忆 ----
    character_card_path: str = ""  # 留空则使用内置默认角色卡（无名者）
    enable_session_memory: bool = True  # 跨轮次/跨会话记住对话
    session_memory_dir: str = "./data/sessions"  # 记忆持久化目录
    prompt_config_path: str = ""  # 全局提示词拼装配置 JSON（留空=默认，输出与改造前一致）

    # ---- 复读抑制（repetition guard，动态负向提示 + 生成后校验） ----
    # 问题：模型会把 mes_example 示范句逐字复现、同一意象连用多轮（用户反馈「复读机」），
    # repetition_penalty（token 级）无法根治整句照抄。
    # 方案（echoproof 思路）：把最近几轮角色说过的话 + 角色卡示例句提取为禁用短语，
    # 注入提示词末尾明令禁止；非流式路径（QQ/POST /chat）生成后命中还会重写重试。
    repetition_guard_enabled: bool = True  # 总开关（关闭后提示词输出与改造前一致）
    repetition_guard_window: int = Field(8, ge=1, le=200)  # 统计最近 N 条 assistant 消息
    repetition_guard_max_phrases: int = Field(8, ge=1, le=50)  # 每轮最多注入的禁用短语数
    repetition_guard_max_retries: int = Field(1, ge=0, le=3)  # 非流式路径重写重试上限

    # ---- 两阶段生成（P2-3，draft + refine） ----
    # 规则重试耗尽仍复读/出戏时，用更低温度按 SELF-CHECK 指令自检重写一次，
    # 精炼稿通过全部校验才采纳。默认关闭（零回归）；开启后仅影响问题回复的延迟。
    refine_enabled: bool = False
    refine_temperature: float = Field(0.3, gt=0.0, lt=1.0)  # 精炼稿用低温稳住格式

    # ---- 安全 / 限流 ----
    max_message_length: int = Field(4000, ge=1, le=100_000)
    # 回复长度硬闸（无 .env 覆盖时的默认值）。
    # 中文按约 1.5 字/token 换算：最坏可接受 = 6 条 × 40 字 = 240 字 ≈ 160 token，
    # 再留 50% 余量 → 240 token（≈360 字）。过长会让模型退回长篇说教/跑题，
    # 是角色扮演自然度的常见杀手。换模型或换语种时需按实际字/token 比重新校准。
    max_tokens_per_reply: int = Field(240, ge=1, le=1_000_000)
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
    history_summary_threshold: int = Field(40, ge=2, le=10_000)
    # 本地开发默认禁用前端缓存；生产部署可设 false 恢复浏览器缓存（建议配合版本化资源）
    static_no_cache: bool = True

    # ---- 语音（STT / TTS 后端，均为可选回退） ----
    # 默认全部关闭：前端优先用浏览器原生 Web Speech API；
    # 仅当显式开启后，/voice/* 才走后端适配器（faster-whisper / Edge-TTS）。
    stt_backend_enabled: bool = False
    whisper_model: str = "base"  # faster-whisper 模型大小: tiny/base/small/medium/large-v3
    whisper_model_path: str = ""  # 本地模型目录路径（为空则用 faster-whisper 内置下载）
    tts_backend_enabled: bool = False
    edge_tts_default_voice: str = "zh-CN-XiaoxiaoNeural"
    tts_default_format: str = "mp3"
    voice_request_timeout: float = Field(30.0, gt=0.0)  # 语音后端调用超时（秒）

    # ---- QQ 渠道（NapCatQQ / OneBot v11） ----
    # 让一个 QQ 号（建议小号）通过 NapCat 协议端登录，把消息转成 OneBot v11
    # 交给本服务处理，回复再发回 QQ。大脑（人设/RAG/情感/记忆）全部复用。
    qq_enabled: bool = False  # 总开关（默认关，不影响现有功能）
    qq_napcat_ws_url: str = "ws://127.0.0.1:3001"  # NapCat 正向 OneBot v11 WebSocket 地址
    qq_ws_token: str = ""  # OneBot WebSocket 鉴权 token（NapCat 配置一致；空=不鉴权）
    qq_bot_uin: str = ""  # 机器人 QQ 号（空则启动时用 get_login_info 自动获取）
    qq_admin_uin: str = ""  # 管理员 QQ 号（指令权限校验；空=不限制）
    qq_character_id: str = ""  # QQ 上默认扮演的角色 id（空=当前激活角色）
    qq_group_at_only: bool = True  # 群内仅当被 @机器人 时才回复（避免扰群）
    qq_command_prefix: str = "!"  # 指令前缀（!clear / !help / !char）
    qq_allow_from: str = ""  # 私聊白名单 QQ 号（逗号分隔；空=允许所有人）

    # ---- QQ 语音回复（情感命中时以角色原声切片回复；默认全关，零回归） ----
    # 详见 docs/QQ语音回复方案.md。P0 仅原声切片链路；TTS 兜底 / 随机概率 /
    # 文本净化 / 启动自检为 P1，对应配置项随实现一并加入。
    qq_voice_enabled: bool = False  # 总开关（!voice on/off 可按会话覆盖）
    qq_voice_lang: Literal["zh", "en"] = "zh"  # 全局默认配音（!lang zh/en 可按会话覆盖）
    qq_voice_clip_manifest: str = ""  # 切片 manifest 路径；空=自动定位 frontend/assets/voice/wu_ming_zhe/
    # 情感触发阈值。注意 score 口径随检测来源不同（LLM/分类器为置信分，关键词层为
    # 权重累加且单命中仅 0.3~0.5）——keyword 来源的真实命中在 voice_reply 中视为已达标。
    qq_voice_emotion_threshold: float = Field(0.6, ge=0.0, le=1.0)
    qq_voice_cooldown_sec: float = Field(60.0, ge=0.0)  # 同一会话两次语音的最小间隔
    # QQ 语音普通用户上限 60s；切片库实测最长 62.6s，故放宽到 65 兜住全部官方切片
    qq_voice_max_sec: float = Field(65.0, ge=1.0)
    qq_voice_group_enabled: bool = False  # 群聊是否允许自动出声（防扰群，默认关）
    qq_voice_tts_voice_en: str = "en-US-AriaNeural"  # 英文 TTS 音色（P1 兜底链路用，P0 预留）


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """解析并缓存配置单例；测试中调用 get_settings.cache_clear() 重置。"""
    return Settings()
