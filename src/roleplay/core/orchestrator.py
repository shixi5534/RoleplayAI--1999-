"""应用层用例：一次对话的编排（ChatOrchestrator）。

依赖倒置：构造函数注入 LLMPort / EmotionPort / VectorStore，均依赖抽象。
流程：解析人设 → 检测情感 → 知识库/记忆检索 → 拼装 → LLM 生成 →（可选）Live2D 映射。

增强（持久化知识库 + 分层记忆 + 联网）：
- knowledge_base：多命名空间持久化向量库（人设/长期记忆/联网/情节），优先于 rag 用于检索。
- character_store：多角色人设；请求可指定 character_id，否则用当前激活角色作为默认人设。
- web_search + use_web：本轮实时联网检索并入库（联网 RAG）。
- memory_tier：每隔若干轮把近期对话合并为长期记忆，并按衰减/保留策略清理。
"""
import asyncio
import logging
import time
from dataclasses import dataclass

from ..config import get_settings
from ..models.chat import ChatRequest, ChatResponse, EmotionInfo
from ..models.character import CharacterCard
from .character_repo import CharacterRepo
from .persona_prompt import (
    PromptLayers,
    build_roleplay_messages,
    build_roleplay_prompt,
    resolve_knowledge_namespaces,
    resolve_prompt_config,
)
from .emotion.detector import EmotionPort
from .emotion.mapping import Live2DEmotionMapper
from .knowledge.character_store import CharacterStore
from .knowledge.ingest import ingest_web
from .knowledge.memory_tier import LongTermMemory
from .knowledge.vector_store import KnowledgeBase
from .knowledge.web_search import WebSearchPort
from .knowledge.plot_graph import PlotGraphRegistry
from .knowledge.graph_search import GraphSearchRegistry
from .knowledge.profile import UserProfile
from .knowledge.extractors import (
    RuleProfileExtractor,
    LLMProfileExtractor,
    build_profile_extractors,
    extract_profile_entries,
)
from .knowledge.event_extractor import (
    RuleEventExtractor,
    LLMEventExtractor,
    build_event_extractors,
    extract_event_entries,
)
from .llm.base import LLMPort
from .llm.factory import build_llm_from_config
from .rag.base import RetrievedChunk, VectorStore
from .quality_guard import (
    find_quality_violations,
    quality_retry_hint,
    refine_instruction,
)
from .repetition_guard import (
    build_repetition_block,
    extract_recent_phrases,
    find_violations,
    retry_hint,
)
from .session_memory import SessionMemory

logger = logging.getLogger(__name__)

# 静态兜底追问（未开 enable_dynamic_followups 时使用）。
# 注意语义：这些文案会被前端渲染成「建议按钮」，点击后作为**用户**的下一句话发出，
# 因此要写成用户会说的话，而不是角色的台词；同时避开「你今天还好吗？」这类客服腔。
DEFAULT_FOLLOW_UPS = ["然后呢？", "再多说一点", "换个话题聊聊"]


@dataclass
class OrchestratorResult:
    response: ChatResponse
    live2d: dict | None = None  # 情绪→表情映射（启用 Live2D 时非空）


class ChatOrchestrator:
    def __init__(
        self,
        *,
        llm: LLMPort,
        emotion: EmotionPort,
        rag: VectorStore,
        mapper: Live2DEmotionMapper | None = None,
        top_k: int = 3,
        temperature: float = 0.8,
        enable_emotion: bool = True,
        model_id: str | None = None,
        character_repo: CharacterRepo | None = None,
        session_memory: SessionMemory | None = None,
        # —— 新增：知识层（均为可选，便于测试以最小依赖构造） ——
        knowledge_base: KnowledgeBase | None = None,
        character_store: CharacterStore | None = None,
        web_search: WebSearchPort | None = None,
        memory_tier: LongTermMemory | None = None,
        enable_web: bool = False,
        enable_longterm: bool = True,
        web_max_results: int = 5,
        web_fetch_content: bool = True,
        chunk_size: int = 600,
        consolidate_every: int = 6,
        # —— 混合检索（稠密 + BM25 稀疏重排） ——
        rag_hybrid: bool = True,
        rag_hybrid_alpha: float = 0.3,
        rag_hybrid_candidates: int = 12,
        # —— 体验优化（可配置，默认保守）——
        enable_dynamic_followups: bool = False,
        enable_history_summary: bool = True,
        history_summary_threshold: int = 40,
        # —— 用户画像（UserProfile） ——
        user_profile: UserProfile | None = None,
        enable_profile: bool = True,
        profile_extract_every: int = 10,
        profile_top_k: int = 5,
        # —— 结构化事件提取（升级方案 C） ——
        enable_event_extract: bool = True,
        # —— 复读抑制（repetition guard：负向提示 + 生成后校验） ——
        repetition_guard_enabled: bool = True,
        repetition_guard_window: int = 8,
        repetition_guard_max_phrases: int = 8,
        repetition_guard_max_retries: int = 1,
        # —— 生成后角色一致性自检（P1-4，纯规则、无 LLM） ——
        # 命中「自称 AI / 客服腔 / 写了对方动作」时追加重写指令重试。
        # 与复读抑制共用同一轮回复，自检独立计次（上限 quality_guard_max_retries）。
        quality_guard_enabled: bool = True,
        quality_guard_max_retries: int = 2,
        # —— 两阶段生成（P2-3，draft + refine） ——
        # 规则校验仍有残留（重试耗尽 / 未启用重试）时，用更低的温度按
        # SELF-CHECK 指令自检重写一次；精炼稿通过全部校验才采纳，否则保留
        # 原回复。默认关闭（零回归）。
        refine_enabled: bool = False,
        refine_temperature: float = 0.3,
        # —— 剧情图谱（PlotGraph，独立于 lore 向量 RAG；默认关闭，零回归）——
        plot_graph: PlotGraphRegistry | None = None,
        plot_graph_enabled: bool = False,
        plot_max_chunks: int = 3,
        plot_lexical_fallback: int = 2,
        plot_context_max_chars: int = 1000,
        # —— lore 知识图谱（GraphRAG 第三路检索；默认关闭，零回归）——
        graph_registry: GraphSearchRegistry | None = None,
        graph_enabled: bool = False,
        graph_max_chunks: int = 3,
        graph_context_max_chars: int = 1200,
    ) -> None:
        self._llm = llm
        self._emotion = emotion
        self._rag = rag
        self._mapper = mapper
        self._top_k = top_k
        self._temperature = temperature
        self._enable_emotion = enable_emotion
        self._model_id = model_id
        self._character_repo = character_repo
        self._session_memory = session_memory
        # 知识层
        self._kb = knowledge_base
        self._character_store = character_store
        self._web_search = web_search
        self._memory_tier = memory_tier
        self._enable_web = enable_web
        self._enable_longterm = enable_longterm
        self._web_max_results = web_max_results
        self._web_fetch_content = web_fetch_content
        self._chunk_size = chunk_size
        self._consolidate_every = max(1, consolidate_every)
        # 混合检索配置
        self._rag_hybrid = rag_hybrid
        self._rag_hybrid_alpha = rag_hybrid_alpha
        self._rag_hybrid_candidates = rag_hybrid_candidates
        # 体验优化配置
        self._enable_dynamic_followups = enable_dynamic_followups
        self._enable_history_summary = enable_history_summary
        self._history_summary_threshold = history_summary_threshold
        # 用户画像配置
        self._user_profile = user_profile
        self._enable_profile = enable_profile
        self._profile_extract_every = max(1, profile_extract_every)
        self._profile_top_k = max(1, profile_top_k)
        # 全局提示词拼装配置（升级方案 D）：角色卡内嵌 prompt_config 优先，
        # 否则用全局 prompt_config_path 文件（留空=默认，零回归）
        self._global_prompt_config = self._load_global_prompt_config()
        # 画像提取器：规则层恒有；LLM 层按配置（非 mock 且 api_key）构建
        self._rule_extractor = RuleProfileExtractor()
        self._profile_llm: LLMProfileExtractor | None = None
        if self._user_profile is not None and self._enable_profile:
            self._rule_extractor, self._profile_llm = build_profile_extractors(
                get_settings(), self._llm
            )
        # 事件提取器（升级方案 C）：规则层恒有；LLM 层按配置构建；
        # 开关关闭时回退整段合并（consolidate 原路径）
        self._enable_event_extract = enable_event_extract
        self._event_rule = RuleEventExtractor()
        self._event_llm: LLMEventExtractor | None = None
        if enable_event_extract and self._memory_tier is not None:
            self._event_rule, self._event_llm = build_event_extractors(
                get_settings(), self._llm
            )
        # 复读抑制配置
        self._repetition_guard_enabled = repetition_guard_enabled
        self._repetition_guard_window = max(1, repetition_guard_window)
        self._repetition_guard_max_phrases = max(1, repetition_guard_max_phrases)
        self._repetition_guard_max_retries = max(0, repetition_guard_max_retries)
        self._quality_guard_enabled = quality_guard_enabled
        self._quality_guard_max_retries = max(0, quality_guard_max_retries)
        # 两阶段生成（P2-3）：默认关闭（零回归）；精炼温度钳制在 [0.05, 1]。
        self._refine_enabled = refine_enabled
        self._refine_temperature = min(1.0, max(0.05, refine_temperature))
        # 剧情图谱（独立链路：开关关闭时完全不参与检索与提示词拼装）
        self._plot_graph = plot_graph
        self._plot_enabled = bool(plot_graph_enabled and plot_graph is not None)
        self._plot_max_chunks = max(0, int(plot_max_chunks))
        self._plot_lexical_fallback = max(0, int(plot_lexical_fallback))
        self._plot_context_max_chars = max(0, int(plot_context_max_chars))
        # lore 知识图谱（第三路检索；独立预算与来源标签，不挤占向量 top_k）
        self._graph_registry = graph_registry
        self._graph_enabled = bool(graph_enabled and graph_registry is not None)
        self._graph_max_chunks = max(0, int(graph_max_chunks))
        self._graph_context_max_chars = max(0, int(graph_context_max_chars))
        self._turn_counts: dict[str, int] = {}
        # 长期记忆沉淀游标：记录每个会话已沉淀的历史条数，避免相邻周期整段重复写入
        self._consolidated_cursor: dict[str, int] = {}
        # 用户画像提取游标：记录每个会话已提取画像的历史条数（独立推进，ADR-8）
        self._profile_cursor: dict[str, int] = {}
        # 会话级异步锁：保证同一会话的「读历史→生成→落盘」串行，避免并发交错轮次
        self._session_locks: dict[str, asyncio.Lock] = {}

    def _resolve_default_card(self, req: ChatRequest) -> str | None:
        """确定默认人设 JSON：优先请求指定角色 → 激活角色 → 内置默认角色卡。"""
        if self._character_store is not None:
            target_id = req.character_id or self._character_store.get_active_id()
            if target_id:
                card = self._character_store.get(target_id)
                if card is not None:
                    return card.model_dump_json()
        if self._character_repo is not None:
            return self._character_repo.card_json
        return None

    @staticmethod
    def _load_global_prompt_config():
        """加载全局提示词拼装配置（config.py prompt_config_path）。

        文件缺失/非法 → 默认配置（输出与改造前一致），不抛异常。
        """
        from pathlib import Path

        from ..models.prompt_config import PromptConfig

        s = get_settings()
        if not s.prompt_config_path:
            return PromptConfig()
        try:
            raw = Path(s.prompt_config_path).read_text(encoding="utf-8")
            return PromptConfig.from_any(raw)
        except OSError as exc:
            logger.warning("全局提示词配置加载失败，使用默认：%s", exc)
            return PromptConfig()

    def _resolve_character_id(self, req: ChatRequest) -> str | None:
        if self._character_store is None:
            return None
        return req.character_id or self._character_store.get_active_id()

    def _resolve_context(self, req: ChatRequest) -> tuple[str | None, str | None, object | None]:
        """人设解析：默认角色卡 + 角色 id + 角色卡对象（同步、廉价）。"""
        default_card = self._resolve_default_card(req)
        character_id = self._resolve_character_id(req)
        card_obj = (
            self._character_store.get(character_id)
            if (self._character_store is not None and character_id)
            else None
        )
        return default_card, character_id, card_obj

    async def _detect_emotion(self, req: ChatRequest) -> EmotionInfo:
        """情感检测（独立异步，供 stream() 提前拿到 emotion 事件）。"""
        if not self._enable_emotion:
            return EmotionInfo()
        try:
            return await self._emotion.detect(req.message)
        except Exception as exc:  # noqa: BLE001
            logger.warning("情感检测失败（回落 neutral）：%s", exc)
            return EmotionInfo()

    async def _plot_retrieve(self, query: str, character_id: str | None) -> list:
        """剧情图谱检索（第四路，独立于 lore 向量 RAG）。

        纯 CPU（实体链接 + PPR + 词法），丢线程池不阻塞事件循环；
        任何异常只告警并返回空——永不影响 lore 检索与对话主链路。
        """
        if not self._plot_enabled or self._plot_graph is None:
            return []
        try:
            retriever = self._plot_graph.get(character_id)
        except Exception as exc:  # noqa: BLE001
            logger.warning("剧情图谱加载失败，本轮跳过：%s", exc)
            return []
        if retriever is None:
            return []
        try:
            return await asyncio.to_thread(
                retriever.retrieve,
                query,
                top_chunks=self._plot_max_chunks,
                lexical_fallback=self._plot_lexical_fallback,
            )
        except Exception as exc:  # noqa: BLE001
            logger.warning("剧情图谱检索失败，本轮跳过：%s", exc)
            return []

    async def _graph_retrieve(self, query: str, character_id: str | None) -> list:
        """lore 知识图谱检索（第三路，独立于向量 RAG 与剧情层）。

        实体链接 + PPR + 证据回查均为 CPU 工作，丢线程池不阻塞事件循环；
        任何异常只告警并返回空——图谱层永不拖垮主链路（降级=纯向量路径）。
        """
        if not self._graph_enabled or self._graph_registry is None:
            return []
        try:
            searcher = self._graph_registry.get(character_id)
        except Exception as exc:  # noqa: BLE001
            logger.warning("知识图谱加载失败，本轮跳过：%s", exc)
            return []
        if searcher is None:
            return []
        try:
            return await asyncio.to_thread(searcher.retrieve, query)
        except Exception as exc:  # noqa: BLE001
            logger.warning("知识图谱检索失败，本轮跳过：%s", exc)
            return []

    async def _gather_context(
        self,
        req: ChatRequest,
        card_obj: object | None,
        character_id: str | None,
    ) -> tuple[list, list, list, list]:
        """联网 + 知识库/记忆检索 + 用户画像 + 剧情图谱 + lore 图谱（五路并行，只读）。

        返回 ``(chunks, profile_chunks, plot_chunks, graph_chunks)``；剧情块与图谱块
        各自单独一路返回，与 lore 块在提示词里分块渲染、独立预算，互不挤占。
        与情感检测相互独立，可并行启动；stream() 先等情感、再等本结果。
        """
        # 联网检索（可选，本轮实时）：检索 → 切块 → 入库，随后并入知识库检索
        async def _retrieve_task() -> list:
            if (
                req.use_web
                and self._enable_web
                and self._web_search is not None
                and self._kb is not None
            ):
                try:
                    await ingest_web(
                        self._kb,
                        self._web_search,
                        req.message,
                        max_results=self._web_max_results,
                        fetch_content=self._web_fetch_content,
                        chunk_size=self._chunk_size,
                    )
                except Exception as exc:  # noqa: BLE001
                    logger.warning("联网检索入库失败（不影响本轮回复）：%s", exc)

            # 知识库 / 记忆检索：检索范围由角色卡 knowledge_scope 决定
            #    （角色专属资料 lore_<cid> + 长期记忆 + 联网 + 情节片段）。
            # 注：persona（人设）命名空间不注入上下文——当前角色人设已在 system_prompt 中，
            #     重复注入既冗余，多角色并存时还可能造成角色串味；人设仍存于知识库供管理与调试。
            store = self._kb if self._kb is not None else self._rag
            if store is None:
                return []
            return await self._retrieve(store, req, card_obj, character_id)

        # 用户画像检索（第三路并行，独立于 RAG chunks，不混排）+ 重要日期提醒（ADR-5/6）
        async def _profile_task() -> list:
            if not self._enable_profile or self._user_profile is None:
                return []
            try:
                profile_chunks = await self._user_profile.retrieve(
                    req.message, top_k=self._profile_top_k
                )
                reminders = self._user_profile.check_reminders()
                if reminders:
                    for line in reminders:
                        profile_chunks.insert(
                            0,
                            RetrievedChunk(
                                text=line,
                                score=1.0,
                                metadata={
                                    "namespace": self._user_profile.namespace,
                                    "type": "reminder",
                                },
                            ),
                        )
                return profile_chunks
            except Exception as exc:  # noqa: BLE001
                logger.warning("用户画像检索失败（不影响本轮回复）：%s", exc)
                return []

        # 剧情图谱检索（第四路并行；未启用时为零成本空列表）
        async def _plot_task() -> list:
            return await self._plot_retrieve(req.message, character_id)

        # lore 知识图谱检索（第五路并行；未启用/无图谱文件时为空列表）
        async def _graph_task() -> list:
            return await self._graph_retrieve(req.message, character_id)

        rag_chunks, profile_chunks, plot_chunks, graph_chunks = await asyncio.gather(
            _retrieve_task(), _profile_task(), _plot_task(), _graph_task()
        )
        return rag_chunks, profile_chunks, plot_chunks, graph_chunks

    def _build_prompt(
        self,
        req: ChatRequest,
        default_card: str | None,
        card_obj: object | None,
        chunks: list,
        profile_chunks: list,
        emotion: str,
        plot_chunks: list | None = None,
        graph_chunks: list | None = None,
    ) -> tuple[str, "PromptLayers | None"]:
        """拼装本轮提示词。返回 ``(system_prompt, layers)``。

        - system_prompt：单 system 模式（默认）下的完整提示词，与改造前逐字节一致；
        - layers：P1-1 分层模式下非空，承载 system_blocks / user_prefix；
          此时 system_prompt 退化为「核心人设」主串（作为端点不支持多 system 时的兜底）。

        分层开关（``message_layering``）在角色卡内嵌 prompt_config 或全局配置里；
        turn_count 传给 P1-3 情感节奏做信任层判据。
        """
        turn_count = self._turn_counts.get(req.session_id, 0)
        cfg = resolve_prompt_config(
            card_json=req.character_card,
            default_card=default_card,
            card=card_obj,
            prompt_config=self._global_prompt_config,
        )
        if getattr(cfg, "message_layering", False):
            layers = build_roleplay_messages(
                card_json=req.character_card,
                fallback_prompt=req.system_prompt,
                default_card=default_card,
                message=req.message,
                chunks=chunks,
                card=card_obj,
                profile_chunks=profile_chunks,
                plot_chunks=plot_chunks,
                plot_max_chars=self._plot_context_max_chars,
                graph_chunks=graph_chunks,
                graph_max_chars=self._graph_context_max_chars,
                emotion=emotion,
                prompt_config=self._global_prompt_config,
                turn_count=turn_count,
            )
            return (layers.system_blocks[0] if layers.system_blocks else ""), layers
        return (
            build_roleplay_prompt(
                card_json=req.character_card,
                fallback_prompt=req.system_prompt,
                default_card=default_card,
                message=req.message,
                chunks=chunks,
                card=card_obj,
                profile_chunks=profile_chunks,
                plot_chunks=plot_chunks,
                plot_max_chars=self._plot_context_max_chars,
                graph_chunks=graph_chunks,
                graph_max_chars=self._graph_context_max_chars,
                emotion=emotion,
                prompt_config=self._global_prompt_config,
                turn_count=turn_count,
            ),
            None,
        )

    def _repetition_guard(
        self,
        history: list[dict] | None,
        card_obj: object | None,
        request_card_json: str | None = None,
    ) -> tuple[str | None, list[str]]:
        """构建复读抑制素材：返回 (负向提示块, 禁用短语列表)。

        - 禁用短语 = 最近 N 条 assistant 消息的句子 + 角色卡示例句
          （mes_example / first_mes，防止首轮照抄示例原句）；
        - 示例句来源与 build_roleplay_prompt 的 source_card 优先级一致：
          请求携带的 character_card 优先，其次 store 激活卡；
        - 未启用 / 无素材 → (None, [])：提示词输出与改造前一致（零回归）。
        """
        if not self._repetition_guard_enabled:
            return None, []
        source = card_obj
        if request_card_json:
            parsed = CharacterCard.parse_raw_card(request_card_json)
            if parsed is not None:
                source = parsed
        extra: list[str] = []
        if source is not None:
            for field in ("mes_example", "first_mes"):
                value = getattr(source, field, "") or ""
                if value.strip():
                    extra.append(value)
        phrases = extract_recent_phrases(
            history,
            window=self._repetition_guard_window,
            max_phrases=self._repetition_guard_max_phrases,
            extra_phrases=extra,
        )
        return build_repetition_block(phrases), phrases

    async def _prepare_full(
        self, req: ChatRequest
    ) -> tuple[str, EmotionInfo, str | None, PromptLayers | None]:
        """前置阶段（步骤 1–4）：人设 + 情感 + 联网 + 知识检索，拼装提示词。

        返回 (system_prompt, emotion_info, character_id, layers)。
        layers 仅 P1-1 分层模式下非空（见 _build_prompt）。

        该阶段只读、可并发，不触碰会话历史，故置于会话锁之外。

        并行化（ADR-6）：情感检测与联网/知识检索用 asyncio.gather 并行；
        emotion 先于 chunk 的时序由 stream() 首推 emotion 事件保证（契约不变）。
        """
        default_card, character_id, card_obj = self._resolve_context(req)
        emotion_task = asyncio.ensure_future(self._detect_emotion(req))
        ctx_task = asyncio.ensure_future(
            self._gather_context(req, card_obj, character_id)
        )
        emotion_info = await emotion_task
        chunks, profile_chunks, plot_chunks, graph_chunks = await ctx_task
        system_prompt, layers = self._build_prompt(
            req,
            default_card,
            card_obj,
            chunks,
            profile_chunks,
            emotion_info.emotion,
            plot_chunks,
            graph_chunks,
        )
        return system_prompt, emotion_info, character_id, layers

    async def _prepare(self, req: ChatRequest) -> tuple[str, EmotionInfo, str | None]:
        """向后兼容的 3 元组入口：丢弃 layers（测试与旧调用方使用）。

        内部主路径（run/stream）走 _prepare_full 以拿到 P1-1 分层结构。
        """
        prompt, emotion, character_id, _layers = await self._prepare_full(req)
        return prompt, emotion, character_id

    def _llm_extra(
        self, layers: PromptLayers | None, repetition_block: str | None
    ) -> dict:
        """P1-1 分层参数：仅分层模式下返回 system_blocks / user_prefix。

        未启用时返回**空 dict**——调用方用 ``**extra`` 展开，因而不传这两个
        关键字参数，行为与改造前逐字节一致（零回归，且兼容不认识这两个参数的
        第三方 LLMPort 实现与测试替身）。

        复读抑制块在分层模式下并入 user_prefix（而非 system 串）：
        它同样属于「紧贴生成点」的动态指令。
        """
        if layers is None:
            return {}
        prefix = layers.user_prefix
        if repetition_block:
            prefix = f"{prefix}\n\n{repetition_block}" if prefix else repetition_block
        extra: dict = {"system_blocks": list(layers.system_blocks)}
        if prefix:
            extra["user_prefix"] = prefix
        return extra

    def _session_lock(self, session_id: str) -> asyncio.Lock:
        """取（或创建）该会话的异步锁。

        容量守卫：会话条目只增不减（仅在 clear_session 时删除），
        长期运行可能缓慢泄漏。超过上限时仅清理「空闲且无等待者」的最旧条目：
        若把持锁/等待中的会话锁直接弹出，同一 session 的后续请求会拿到新锁对象，
        从而与在途请求并发进入临界区（旧锁仍被旧请求持有，但新请求已不可见）。
        """
        lock = self._session_locks.get(session_id)
        if lock is None:
            lock = asyncio.Lock()
            self._session_locks[session_id] = lock
            if len(self._session_locks) > 500:
                # 清理最旧一半中的空闲锁（dict 保持插入序）
                for old_sid in list(self._session_locks)[: len(self._session_locks) // 2]:
                    old_lock = self._session_locks.get(old_sid)
                    if (
                        old_lock is not None
                        and not old_lock.locked()
                        and not getattr(old_lock, "_waiters", None)
                    ):
                        self._session_locks.pop(old_sid, None)
        return lock

    async def _retrieve(self, store, req: ChatRequest, card_obj, character_id: str | None = None) -> list:
        """知识检索（异步、不阻塞事件循环）。

        - KnowledgeBase 提供 asearch：在事件循环内 await 调用（含真正的异步嵌入）。
        - 其它 VectorStore（如测试用 InMemoryVectorStore）无 asearch：丢到线程池跑同步 search。
        - 长期记忆（events）按 character_id 隔离检索，跨角色不串台；
          且经 LongTermMemory.retrieve 做 相似度×时间衰减×重要性 综合排序（若有 memory_tier）。
        """
        ns = resolve_knowledge_namespaces(card_obj, character_id)
        has_asearch = hasattr(store, "asearch")

        # 长期记忆命名空间（events / events:<cid>）单独走衰减检索；其余命名空间常规检索
        event_ns = f"events:{character_id}" if character_id else "events"
        if event_ns in ns and self._memory_tier is not None:
            other_ns = [n for n in ns if n != event_ns]
            chunks: list = []
            if other_ns:
                if has_asearch:
                    chunks += await store.asearch(
                        req.message,
                        top_k=self._top_k,
                        namespaces=other_ns,
                        hybrid=self._rag_hybrid,
                        hybrid_alpha=self._rag_hybrid_alpha,
                        candidate_mult=self._rag_hybrid_candidates,
                    )
                else:
                    chunks += await asyncio.to_thread(
                        store.search,
                        req.message,
                        top_k=self._top_k,
                        namespaces=other_ns,
                        hybrid=self._rag_hybrid,
                        hybrid_alpha=self._rag_hybrid_alpha,
                        candidate_mult=self._rag_hybrid_candidates,
                    )
            mem = await self._memory_tier.retrieve(
                req.message, top_k=self._top_k, character_id=character_id
            )
            return chunks + mem

        if has_asearch:
            return await store.asearch(
                req.message,
                top_k=self._top_k,
                namespaces=ns,
                hybrid=self._rag_hybrid,
                hybrid_alpha=self._rag_hybrid_alpha,
                candidate_mult=self._rag_hybrid_candidates,
            )
        return await asyncio.to_thread(
            store.search,
            req.message,
            top_k=self._top_k,
            namespaces=ns,
            hybrid=self._rag_hybrid,
            hybrid_alpha=self._rag_hybrid_alpha,
            candidate_mult=self._rag_hybrid_candidates,
        )

    async def _make_follow_ups(self, system_prompt: str, reply: str, llm: LLMPort | None = None) -> list[str]:
        """生成后续追问。默认返回静态兜底；开启 enable_dynamic_followups 时由 LLM 动态生成。

        llm 参数：请求级 override 客户端（如有），缺省用全局 self._llm。
        """
        if not self._enable_dynamic_followups:
            return list(DEFAULT_FOLLOW_UPS)
        gen = llm or self._llm
        try:
            text = await gen.generate(
                system=(
                    "你是角色扮演AI的提问生成器。根据角色刚刚的回复，生成至多 3 个自然的后续追问，"
                    "每句不超过 18 字，用换行分隔，不要编号、不要引号、不要解释。"
                ),
                user=f"角色回复：{reply}",
            )
            items = [
                ln.strip("0123456789.、.）) ").strip()
                for ln in (text or "").splitlines()
                if ln.strip()
            ]
            items = [it for it in items if it][:3]
            return items or list(DEFAULT_FOLLOW_UPS)
        except Exception as exc:  # noqa: BLE001
            logger.warning("动态后续问题生成失败，回退静态：%s", exc)
            return list(DEFAULT_FOLLOW_UPS)

    async def _summarize_history(
        self,
        history: list[dict] | None,
        llm: LLMPort | None = None,
        session_id: str | None = None,
    ) -> list[dict] | None:
        """对话历史过长时，把较旧的一半压缩为一段摘要，保留最近若干轮，避免上下文溢出。

        仅在 enable_history_summary 且长度超过阈值时触发；失败则原样返回。
        llm 参数：请求级 override 客户端（如有），缺省用全局 self._llm。
        session_id：用于摘要落盘复用——已覆盖的旧片段直接复用上次摘要，
        只对新片段做增量压缩，避免每轮重复烧 token。
        """
        if not self._enable_history_summary or not history:
            return history
        if len(history) <= self._history_summary_threshold:
            return history
        keep = max(self._history_summary_threshold // 2, 2)
        old, recent = history[:-keep], history[-keep:]
        gen = llm or self._llm

        # 增量复用：读取上次摘要，跳过已覆盖的旧片段
        saved = (
            self._session_memory.get_summary(session_id)
            if self._session_memory and session_id
            else None
        )
        old_summary = (saved or {}).get("summary_text", "")
        covered = max(0, int((saved or {}).get("covered_turns", 0)))
        new_segment = old[covered:]
        # 已覆盖全部旧片段 → 直接复用旧摘要，零 LLM 调用
        if old_summary and not new_segment:
            return [{"role": "user", "content": "【历史摘要】" + old_summary}] + recent

        try:
            blob = "\n".join(f"{t.get('role', '?')}: {t.get('content', '')}" for t in new_segment)
            if old_summary:
                # 增量模式：旧摘要作为上下文，让 LLM 输出合并后的完整摘要（长度稳定）
                blob = f"已有摘要：{old_summary}\n\n新增对话：\n{blob}"
            summary = await gen.generate(
                system=(
                    "把以下对话压缩成一段简洁的要点摘要（中文，不超过 120 字），"
                    "保留关键人设、约定与重要事件。"
                ),
                user=blob,
            )
            if summary and summary.strip():
                merged = summary.strip()
                if self._session_memory and session_id:
                    self._session_memory.save_summary(
                        session_id,
                        {
                            "summary_text": merged,
                            "covered_turns": len(old),
                            "updated_at": time.time(),
                            "model": getattr(gen, "model_name", ""),
                        },
                    )
                return [
                    {"role": "user", "content": "【历史摘要】" + merged}
                ] + recent
        except Exception as exc:  # noqa: BLE001
            logger.warning("对话历史摘要失败，使用原历史：%s", exc)
        # 增量失败回退旧摘要（若有）；否则原历史
        if old_summary:
            return [{"role": "user", "content": "【历史摘要】" + old_summary}] + recent
        return history

    async def _persist(self, req: ChatRequest, reply: str, character_id: str | None) -> None:
        """在会话锁内调用：写历史 + 长期记忆合并/清理 + 用户画像提取。"""
        if self._session_memory:
            # 批量写盘：一轮对话一次落盘（写放大减半，减少事件循环内同步 IO）
            self._session_memory.append_many(
                req.session_id,
                [("user", req.message), ("assistant", reply)],
            )
        # 轮次计数（长期记忆与画像提取共用；仅在启用任一时有意义）
        sid = req.session_id
        self._turn_counts[sid] = self._turn_counts.get(sid, 0) + 1
        if len(self._turn_counts) > 500:
            for old_sid in list(self._turn_counts)[: len(self._turn_counts) // 2]:
                self._turn_counts.pop(old_sid, None)
                self._consolidated_cursor.pop(old_sid, None)
                self._profile_cursor.pop(old_sid, None)
        # 6) 长期记忆合并 + 衰减清理
        if self._enable_longterm and self._memory_tier is not None and self._session_memory:
            if self._turn_counts[sid] % self._consolidate_every == 0:
                try:
                    history = self._session_memory.get_history(sid)
                    cursor = self._consolidated_cursor.get(sid, 0)
                    # 只沉淀「游标之后」的新轮次，避免整段重复写入（旧实现每次都写最近8条，冗余膨胀）
                    turns = [
                        {"role": t["role"], "content": t["content"]}
                        for t in history[cursor:]
                    ]
                    if turns:
                        if self._enable_event_extract:
                            # 结构化提取（升级方案 C）：事实/事件逐条写入
                            entries = await extract_event_entries(
                                turns,
                                rule=self._event_rule,
                                llm=self._event_llm,
                                llm_available=self._event_llm is not None,
                            )
                            if entries:
                                await self._memory_tier.consolidate_entries(
                                    sid, entries, character_id=character_id
                                )
                            else:
                                # 提取为空（如无重要性内容）：回退整段合并保底
                                await self._memory_tier.consolidate(
                                    sid, turns, character_id=character_id
                                )
                        else:
                            await self._memory_tier.consolidate(
                                sid, turns, character_id=character_id
                            )
                        self._consolidated_cursor[sid] = len(history)
                    self._memory_tier.prune(character_id=character_id)
                except Exception as exc:  # noqa: BLE001
                    logger.warning("长期记忆合并失败：%s", exc)
        # 7) 用户画像提取（独立调度：每 profile_extract_every 轮一次；异常不影响主流程）
        if (
            self._enable_profile
            and self._user_profile is not None
            and self._session_memory
            and self._turn_counts[sid] % self._profile_extract_every == 0
        ):
            try:
                history = self._session_memory.get_history(sid)
                cursor = self._profile_cursor.get(sid, 0)
                # 只提取「游标之后」的新轮次（复用 consolidate 的切片语义，独立推进）
                turns = [
                    {"role": t["role"], "content": t["content"]}
                    for t in history[cursor:]
                ]
                if turns:
                    entries = await extract_profile_entries(
                        turns,
                        rule=self._rule_extractor,
                        llm=self._profile_llm,
                        llm_available=self._profile_llm is not None,
                    )
                    if entries:
                        await self._user_profile.upsert(
                            entries, source_round=len(history)
                        )
                    self._profile_cursor[sid] = len(history)
            except Exception as exc:  # noqa: BLE001
                logger.warning("用户画像提取失败（不影响主流程）：%s", exc)

    async def run(self, req: ChatRequest) -> OrchestratorResult:
        """非流式入口（POST /chat 与 QQ 通道主路径）。

        与 stream() 的差别：生成后做复读抑制校验 + P1-4 角色一致性自检——
        命中时追加「重写指令」重试（流式 token 已发出无法撤回，故仅此路径重试）。
        """
        system_prompt, emotion_info, character_id, layers = await self._prepare_full(
            req
        )
        # 复读抑制需要角色卡示例句：轻量同步重取（_prepare 未返回 card_obj）
        _, _, card_obj = self._resolve_context(req)
        # 请求级 LLM override：前端模型切换
        llm, needs_aclose = build_llm_from_config(get_settings(), req.llm)
        try:
            async with self._session_lock(req.session_id):
                history = (
                    self._session_memory.get_history(req.session_id)
                    if self._session_memory
                    else None
                )
                history = await self._summarize_history(history, llm, req.session_id)
                # 复读抑制（负向提示）：历史/角色卡示例 → 禁用短语 → 注入提示词末尾。
                # 直接追加在 _prepare 产出的 system_prompt 末尾（与 build_roleplay_prompt
                # 的追加位置一致，均位于最末位、紧贴生成点）；无禁用短语时零变化。
                block, guard_phrases = self._repetition_guard(
                    history, card_obj, request_card_json=req.character_card
                )
                # P1-1：分层模式下 system 保持「核心人设」主串，复读抑制块并入
                # user_prefix；未分层时沿用原语义——追加在 system_prompt 末尾。
                extra = self._llm_extra(layers, block)
                prompt = (
                    system_prompt
                    if layers is not None
                    else (f"{system_prompt}\n\n{block}" if block else system_prompt)
                )
                temp = (
                    req.temperature
                    if req.temperature is not None
                    else self._temperature
                )

                async def _gen(
                    hint: str = "", temperature: float | None = None
                ) -> str:
                    """发起一次生成；hint 非空时按当前模式追加到对应位置。

                    分层模式 → 追加到 user_prefix 末尾（近因效应最强处）；
                    单 system 模式 → 追加到 system 串末尾（改造前语义）。
                    temperature 非空时覆盖本轮温度（P2-3 精炼段用低温度）。
                    """
                    t = temperature if temperature is not None else temp
                    if layers is not None:
                        ex = dict(extra)
                        if hint:
                            base = ex.get("user_prefix", "")
                            ex["user_prefix"] = (
                                f"{base}\n\n{hint}" if base else hint
                            )
                        return await llm.generate(
                            system=prompt,
                            user=req.message,
                            history=history,
                            temperature=t,
                            **ex,
                        )
                    return await llm.generate(
                        system=f"{prompt}\n\n{hint}" if hint else prompt,
                        user=req.message,
                        history=history,
                        temperature=t,
                    )

                reply = await _gen()
                # 生成后校验 1/2：复读抑制。命中禁用短语 → 追加重写指令重试（有上限）。
                # exclude_in=req.message：用户本轮引用了角色原话时（如「你上次说的
                # X 是什么意思」），模型解释性回复中的复述不算违规（引用回环误伤）。
                if guard_phrases:
                    for _ in range(self._repetition_guard_max_retries):
                        violations = find_violations(
                            reply, guard_phrases, exclude_in=req.message
                        )
                        if not violations:
                            break
                        logger.info(
                            "复读抑制：回复命中禁用短语 %s，重写重试",
                            violations,
                        )
                        reply = await _gen(retry_hint(violations))
                    else:
                        left = find_violations(
                            reply, guard_phrases, exclude_in=req.message
                        )
                        if left:
                            logger.warning(
                                "复读抑制：重试后仍命中禁用短语，接受当前回复：%s",
                                left,
                            )
                # 生成后校验 2/2（P1-4）：角色一致性自检（纯规则、零 LLM 开销）。
                # 命中「自称 AI / 客服腔 / 写了对方动作」→ 追加重写指令重试，
                # 与复读抑制独立计次；重试耗尽仍出戏则接受当前回复（不无限重试）。
                if self._quality_guard_enabled and self._quality_guard_max_retries:
                    for _ in range(self._quality_guard_max_retries):
                        issues = find_quality_violations(reply)
                        if not issues:
                            break
                        logger.info(
                            "角色一致性自检：命中 %s，重写重试",
                            [v.kind for v in issues],
                        )
                        reply = await _gen(quality_retry_hint(issues))
                    else:
                        left = find_quality_violations(reply)
                        if left:
                            logger.warning(
                                "角色一致性自检：重试后仍命中 %s，接受当前回复",
                                [v.kind for v in left],
                            )
                # 两阶段生成（P2-3）：draft 的规则校验仍有残留（重试耗尽或未启用
                # 重试）时，低温度按 SELF-CHECK 指令自检重写一次；精炼稿通过全部
                # 校验才采纳，否则保留原回复（宁缺毋滥，不引入新回归）。
                left_rep = (
                    find_violations(reply, guard_phrases, exclude_in=req.message)
                    if guard_phrases
                    else []
                )
                left_quality = find_quality_violations(reply)
                if self._refine_enabled and (left_rep or left_quality):
                    logger.info(
                        "P2-3 精炼段：校验残留 %s，低温度自检重写",
                        [v.kind for v in left_quality] or ["repetition"],
                    )
                    refined = await _gen(
                        refine_instruction(left_quality),
                        temperature=self._refine_temperature,
                    )
                    still_rep = (
                        find_violations(refined, guard_phrases, exclude_in=req.message)
                        if guard_phrases
                        else []
                    )
                    still_quality = find_quality_violations(refined)
                    if not still_rep and not still_quality:
                        reply = refined
                    else:
                        logger.warning(
                            "P2-3 精炼段未通过自检（%s），保留原回复",
                            [v.kind for v in still_quality] or ["repetition"],
                        )
                await self._persist(req, reply, character_id)
            live2d = (
                self._mapper.resolve(
                    emotion_info.emotion,
                    score=emotion_info.score,
                    model_id=self._model_id,
                )
                if self._mapper is not None
                else None
            )
            return OrchestratorResult(
                response=ChatResponse(
                    reply=reply,
                    emotion=emotion_info,
                    # 与 stream() 一致：follow-up 生成也看到注入后的 prompt
                    follow_ups=await self._make_follow_ups(prompt, reply, llm),
                ),
                live2d=live2d,
            )
        finally:
            if needs_aclose and hasattr(llm, "aclose"):
                await llm.aclose()

    async def stream(self, req: ChatRequest):
        """流式入口：异步生成器，逐事件 yield 字典。

        事件契约：
        - {"type": "emotion", "emotion": str, "score": float}  先发（驱动 Live2D 表情）
        - {"type": "chunk", "text": str}                       每个 token 一片
        - {"type": "done", "follow_ups": [...], "live2d": ...} 末发

        时序优化（B3）：情感检测与联网/知识检索**并行启动**，emotion 一就绪立即发出，
        不再等 _prepare 全部完成（use_web 联网抓取可达数十秒，此前客户端长时间零数据，
        易被误判为挂起）。检索结果在情感事件之后继续 await，不影响 chunk 时序契约。
        """
        default_card, character_id, card_obj = self._resolve_context(req)
        emotion_task = asyncio.ensure_future(self._detect_emotion(req))
        ctx_task = asyncio.ensure_future(
            self._gather_context(req, card_obj, character_id)
        )
        # 先发情感事件：用户一发送即可见表情切换，消除「思考中」空窗
        emotion_info = await emotion_task
        yield {
            "type": "emotion",
            "emotion": emotion_info.emotion,
            "score": emotion_info.score,
        }
        # 继续等待检索（与情感检测并行中），随后拼装 prompt
        chunks, profile_chunks, plot_chunks, graph_chunks = await ctx_task
        system_prompt, layers = self._build_prompt(
            req,
            default_card,
            card_obj,
            chunks,
            profile_chunks,
            emotion_info.emotion,
            plot_chunks,
            graph_chunks,
        )
        # 请求级 LLM override：前端模型切换
        llm, needs_aclose = build_llm_from_config(get_settings(), req.llm)
        try:
            async with self._session_lock(req.session_id):
                history = (
                    self._session_memory.get_history(req.session_id)
                    if self._session_memory
                    else None
                )
                history = await self._summarize_history(history, llm, req.session_id)
                # 复读抑制（负向提示）：预防注入；流式 token 已发出无法撤回，
                # 故不做生成后重试（重试仅在非流式 run() 路径）。
                block, _ = self._repetition_guard(
                    history, card_obj, request_card_json=req.character_card
                )
                # P1-1：分层模式下复读抑制块并入 user_prefix；否则追加到 system 串。
                # 流式路径不做生成后重试（token 已发出不可撤回），故只做预防注入。
                extra = self._llm_extra(layers, block)
                if layers is None and block:
                    system_prompt = f"{system_prompt}\n\n{block}"
                reply_parts: list[str] = []
                async for token in llm.generate_stream(
                    system=system_prompt,
                    user=req.message,
                    history=history,
                    temperature=req.temperature if req.temperature is not None else self._temperature,
                    **extra,
                ):
                    reply_parts.append(token)
                    yield {"type": "chunk", "text": token}
                reply = "".join(reply_parts)
                await self._persist(req, reply, character_id)
            live2d = (
                self._mapper.resolve(
                    emotion_info.emotion,
                    score=emotion_info.score,
                    model_id=self._model_id,
                )
                if self._mapper is not None
                else None
            )
            follow_ups = await self._make_follow_ups(system_prompt, reply, llm)
            yield {
                "type": "done",
                "follow_ups": follow_ups,
                "live2d": live2d,
            }
        finally:
            if needs_aclose and hasattr(llm, "aclose"):
                await llm.aclose()

    def clear_session(self, session_id: str) -> bool:
        """清空某会话的记忆（前端「清空记忆」按钮调用）。

        同时回收该会话的轮次计数与异步锁，避免长期运行下的内存泄漏。
        """
        cleared = self._session_memory.clear(session_id) if self._session_memory else False
        self._turn_counts.pop(session_id, None)
        self._consolidated_cursor.pop(session_id, None)
        self._profile_cursor.pop(session_id, None)
        # 若有请求仍持有/等待该会话锁，保留锁对象，避免新请求拿到新锁后与在途请求并发。
        lock = self._session_locks.get(session_id)
        if lock is not None and not lock.locked() and not getattr(lock, "_waiters", None):
            self._session_locks.pop(session_id, None)
        return cleared
