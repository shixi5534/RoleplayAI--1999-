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
from .character_repo import CharacterRepo
from .persona_prompt import (
    build_roleplay_prompt,
    resolve_knowledge_namespaces,
)
from .emotion.detector import EmotionPort
from .emotion.mapping import Live2DEmotionMapper
from .knowledge.character_store import CharacterStore
from .knowledge.ingest import ingest_web
from .knowledge.memory_tier import LongTermMemory
from .knowledge.vector_store import KnowledgeBase
from .knowledge.web_search import WebSearchPort
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
from .session_memory import SessionMemory

logger = logging.getLogger(__name__)

DEFAULT_FOLLOW_UPS = ["能再多说一点吗？", "你今天还好吗？", "想聊聊别的吗？"]


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

    async def _prepare(self, req: ChatRequest) -> tuple[str, EmotionInfo, str | None]:
        """前置阶段（步骤 1–4）：人设 + 情感 + 联网 + 知识检索，拼装 system_prompt。

        返回 (system_prompt, emotion_info, character_id)。该阶段只读、可并发，
        不触碰会话历史，故置于会话锁之外。

        并行化（ADR-6）：情感检测与联网/知识检索用 asyncio.gather 并行；
        emotion 先于 chunk 的时序由 stream() 首推 emotion 事件保证（契约不变）。
        """
        # 1) 人设（请求携带角色卡 → 指定/激活角色 → 内置默认角色卡 → 简化模式）
        default_card = self._resolve_default_card(req)
        character_id = self._resolve_character_id(req)
        card_obj = (
            self._character_store.get(character_id)
            if (self._character_store is not None and character_id)
            else None
        )

        # 2) 情感检测（async）——与步骤 3-4 并行
        async def _emotion_task() -> EmotionInfo:
            if not self._enable_emotion:
                return EmotionInfo()
            return await self._emotion.detect(req.message)

        # 3) 联网检索（可选，本轮实时）：检索 → 切块 → 入库，随后并入知识库检索
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

            # 4) 知识库 / 记忆检索：检索范围由角色卡 knowledge_scope 决定
            #    （角色专属资料 lore_<cid> + 长期记忆 + 联网 + 情节片段）。
            # 注：persona（人设）命名空间不注入上下文——当前角色人设已在 system_prompt 中，
            #     重复注入既冗余，多角色并存时还可能造成角色串味；人设仍存于知识库供管理与调试。
            store = self._kb if self._kb is not None else self._rag
            if store is None:
                return []
            return await self._retrieve(store, req, card_obj, character_id)

        # 4.5) 用户画像检索（第三路并行，独立于 RAG chunks，不混排）+ 重要日期提醒（ADR-5/6）
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

        emotion_info, chunks, profile_chunks = await asyncio.gather(
            _emotion_task(), _retrieve_task(), _profile_task()
        )

        # 5) 拼装最终 system prompt（人设 → 语气 → 【用户资料】→ 【角色资料库】）
        # prompt_config 优先级：角色卡内嵌 > 全局文件 > 默认
        system_prompt = build_roleplay_prompt(
            card_json=req.character_card,
            fallback_prompt=req.system_prompt,
            default_card=default_card,
            message=req.message,
            chunks=chunks,
            card=card_obj,
            profile_chunks=profile_chunks,
            emotion=emotion_info.emotion,
            prompt_config=self._global_prompt_config,
        )
        return system_prompt, emotion_info, character_id

    def _session_lock(self, session_id: str) -> asyncio.Lock:
        """取（或创建）该会话的异步锁。

        容量守卫：会话条目只增不减（仅在 clear_session 时删除），
        长期运行可能缓慢泄漏。超过上限时清理最旧的一半条目——
        已被 clear 的会话锁不影响新会话；在途请求持有锁对象引用，
        清理旧 dict 条目不破坏并发安全（锁对象本身仍被持有者使用）。
        """
        lock = self._session_locks.get(session_id)
        if lock is None:
            lock = asyncio.Lock()
            self._session_locks[session_id] = lock
            if len(self._session_locks) > 500:
                # 清理最旧的一半（dict 保持插入序）
                for old_sid in list(self._session_locks)[: len(self._session_locks) // 2]:
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
            self._session_memory.append(req.session_id, "user", req.message)
            self._session_memory.append(req.session_id, "assistant", reply)
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
        """非流式入口（保留给测试与 POST /chat）。逻辑与 stream() 一致。"""
        system_prompt, emotion_info, character_id = await self._prepare(req)
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
                reply = await llm.generate(
                    system=system_prompt,
                    user=req.message,
                    history=history,
                    temperature=req.temperature if req.temperature is not None else self._temperature,
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
                    follow_ups=await self._make_follow_ups(system_prompt, reply, llm),
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
        """
        system_prompt, emotion_info, character_id = await self._prepare(req)
        # 先发情感事件：用户一发送即可见表情切换，消除「思考中」空窗
        yield {
            "type": "emotion",
            "emotion": emotion_info.emotion,
            "score": emotion_info.score,
        }
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
                reply_parts: list[str] = []
                async for token in llm.generate_stream(
                    system=system_prompt,
                    user=req.message,
                    history=history,
                    temperature=req.temperature if req.temperature is not None else self._temperature,
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
        self._session_locks.pop(session_id, None)
        return cleared
