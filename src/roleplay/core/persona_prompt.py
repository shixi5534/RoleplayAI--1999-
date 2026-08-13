"""角色扮演提示词系统（人设 / 语气 / 知识范围 / 行为约束 + RAG 动态注入）。

职责（纯函数，无副作用）：
1. resolve_knowledge_namespaces：由角色卡 knowledge_scope 决定检索命名空间
   —— "知识范围"约束落到检索层，而非仅提示词层。
2. build_rag_context：把检索结果格式化为「角色记忆/资料」提示词块，
   附带来源与使用守则（保持角色口吻、不暴露检索机制、资料缺失不编造）。
3. build_roleplay_prompt：人设提示词（复用 resolve_system_prompt）
   + 语气段 + RAG 上下文块 → 最终 system prompt。

与导入管线的无缝集成：
  document_ingest 按 lore_<character_id> 命名空间入库
  → 角色卡 knowledge_scope 引用同名命名空间
  → 对话时 Orchestrator 按该范围检索并经本模块注入提示词。
"""
from __future__ import annotations

from ..models.character import CharacterCard
from ..models.prompt_config import PromptConfig
from .character_card import resolve_system_prompt
from .rag.base import RetrievedChunk

# 未指定知识范围时的公共检索范围（不含 persona：人设已在 system prompt 中）
DEFAULT_RETRIEVAL_NAMESPACES = ["events", "web", "episodic"]

# 注入上下文的最低相似度阈值：低于此分的检索结果视为噪声不注入
MIN_CONTEXT_SCORE = 0.05

_CONTEXT_HEADER = (
    "【角色资料库（检索所得，按相关度排序）】\n"
    "以下资料是「你」的记忆、经历与设定依据。使用守则：\n"
    "- 以第一人称视角消化这些资料，用角色自己的口吻自然引用，"
    "不要说「根据资料」「检索到」等暴露系统机制的话；\n"
    "- 回答须与资料一致，资料未覆盖的细节可以合理演绎，但不得与已知设定矛盾；\n"
    "- 资料与对话无关时忽略即可，不要生硬引用。"
)

# 用户画像块头（ADR-5：人设 → 语气 → 【用户资料】→ 【角色资料库】）
_PROFILE_HEADER = (
    "【用户资料】\n"
    "以下是你对这位用户的了解（来自历史对话的沉淀），自然运用，不要提及系统机制；"
    "与当前话题无关时忽略即可。"
)


def _events_ns(character_id: str | None) -> str:
    """长期记忆命名空间：按角色隔离（namespace-per-tenant）。

    无角色（单角色/默认模式）时回退公共 events，避免隔离落空。
    """
    return f"events:{character_id}" if character_id else "events"


def resolve_knowledge_namespaces(
    card: CharacterCard | None, character_id: str | None = None
) -> list[str]:
    """知识范围 → 检索命名空间列表。空/未设置回退公共范围。

    character_id 非空时，把占位 "events" 映射到该角色的隔离命名空间
    events:<character_id>，实现跨角色长期记忆严格隔离（同角色跨会话仍共享）。
    """
    events = _events_ns(character_id)
    if card is not None and card.knowledge_scope:
        scoped = [ns.strip() for ns in card.knowledge_scope if ns and ns.strip()]
        if scoped:
            return [events if ns == "events" else ns for ns in scoped]
    return [events if ns == "events" else ns for ns in DEFAULT_RETRIEVAL_NAMESPACES]


def _source_label(meta: dict) -> str:
    """检索块 → 简短来源标签（供模型分辨资料出处层级）。"""
    ns = meta.get("namespace", "")
    if ns.startswith("lore_"):
        base = "角色设定资料"
    elif ns == "events" or ns.startswith("events:"):
        base = "长期记忆"
    elif ns == "episodic":
        base = "对话情节"
    elif ns == "web":
        base = "联网资料"
    elif ns == "profile" or ns.startswith("profile:"):
        base = "用户资料"
    else:
        base = "资料"
    section = meta.get("section") or meta.get("title") or ""
    return f"{base}·{section}" if section else base


def build_rag_context(
    chunks: list[RetrievedChunk], max_chars: int = 3200, header: str | None = None
) -> str:
    """检索结果 → 提示词上下文块。空结果返回空串（调用方直接跳过）。"""
    usable = [c for c in chunks if c.score >= MIN_CONTEXT_SCORE and c.text.strip()]
    if not usable:
        return ""
    lines: list[str] = [header or _CONTEXT_HEADER, ""]
    used = 0
    for i, c in enumerate(usable, 1):
        text = c.text.strip()
        if used + len(text) > max_chars and used > 0:
            break
        used += len(text)
        lines.append(f"[{i}] ({_source_label(c.metadata)}) {text}")
    return "\n".join(lines)


def build_profile_context(
    chunks: list[RetrievedChunk], max_chars: int = 1200, header: str | None = None
) -> str:
    """画像检索结果 → 「【用户资料】」提示词块。

    - 复用 MIN_CONTEXT_SCORE 过滤低分噪声；
    - 每行 ``- (来源) 画像句``（提醒行/检索行统一）；
    - 无条目返回空串（调用方直接跳过，不产生空块）。
    """
    usable = [c for c in chunks if c.score >= MIN_CONTEXT_SCORE and c.text.strip()]
    if not usable:
        return ""
    lines: list[str] = [header or _PROFILE_HEADER, ""]
    used = 0
    for i, c in enumerate(usable, 1):
        text = c.text.strip()
        if used + len(text) > max_chars and used > 0:
            break
        used += len(text)
        lines.append(f"- ({_source_label(c.metadata)}) {text}")
    return "\n".join(lines)


def build_roleplay_prompt(
    *,
    card_json: str | None,
    fallback_prompt: str | None,
    default_card: str | None,
    message: str,
    chunks: list[RetrievedChunk] | None = None,
    card: CharacterCard | None = None,
    profile_chunks: list[RetrievedChunk] | None = None,
    emotion: str | None = None,
    prompt_config: PromptConfig | None = None,
) -> str:
    """拼装最终 system prompt：人设 → 语气 → 【用户资料】→ 【角色资料库】。

    - card_json/default_card/fallback_prompt：与 resolve_system_prompt 语义一致；
    - card：已解析的角色卡对象（用于 tone 追加与 prompt_config，可为 None）；
    - chunks：本轮 RAG 检索结果，格式化后追加在末尾；
    - profile_chunks：本轮用户画像检索结果 + 提醒行，插在语气之后、RAG 之前；
    - emotion：当前轮情绪标签（结构化行为规则 emotion_is 条件用）；
    - prompt_config：显式配置（全局层传入）；角色卡内嵌 prompt_config 优先于它。

    字段开关（升级方案 D）：enabled_fields/field_order/custom_templates 控制
    tone / profile / rag 块；默认配置输出与改造前逐字节一致。
    """
    # 优先级：角色卡内嵌 > 显式传入（全局）> 默认
    if card is not None and card.prompt_config is not None:
        cfg = PromptConfig.from_any(card.prompt_config)
    else:
        cfg = prompt_config or PromptConfig()
    prompt = resolve_system_prompt(
        character_card=card_json,
        fallback_prompt=fallback_prompt,
        default_card=default_card,
        message=message,
        emotion=emotion,
        prompt_config=cfg,
    )
    # 外层块按配置顺序组装（默认：tone → profile → rag，与改造前一致）
    blocks: dict[str, str] = {}
    if card is not None and card.tone and card.tone.strip():
        blocks["tone"] = (
            cfg.custom_templates.get("tone") or "【语气要求】{value}"
        ).format(value=card.tone.strip())
    profile_ctx = build_profile_context(
        profile_chunks or [],
        header=cfg.header_templates.get("profile"),
    )
    if profile_ctx:
        blocks["profile"] = profile_ctx
    context = build_rag_context(
        chunks or [],
        header=cfg.header_templates.get("rag"),
    )
    if context:
        blocks["rag"] = context
    for field in cfg.ordered_fields():
        if field not in ("tone", "profile", "rag"):
            continue
        if not cfg.is_enabled(field):
            continue
        text = blocks.get(field)
        if text:
            prompt += f"\n\n{text}"
    return prompt
