"""角色卡系统提示词解析（应用层纯函数，无副作用）。"""
import logging

from ..models.character import CharacterCard
from ..models.prompt_config import (
    ALL_FIELDS,
    CARD_FIELDS,
    PromptConfig,
)
from .behavior_rules import render_rules

logger = logging.getLogger(__name__)

DEFAULT_SYSTEM_PROMPT = "你是一个乐于助人的私人助手。"

# 字段默认渲染模板（与改造前硬编码输出逐字节一致 → 零回归）
_DEFAULT_TEMPLATES = {
    "name": "你是{value}。",
    "personality": "人设：{value}",
    "background": "背景：{value}",
    "behavior_rules": "行为准则：{value}",
    "scenario": "场景：{value}",
    "first_mes": "你的开场白示例（不要原样复述）：{value}",
    "mes_example": "对话示例：\n{value}",
}


def _render_field(card: CharacterCard, field: str, cfg: PromptConfig) -> str | None:
    """渲染单个字段：取值 → 套模板（自定义优先）→ 空值返回 None。

    behavior_rules 特殊：结构化规则命中时直接返回规则块（不套模板）。
    """
    if field == "behavior_rules":
        # 结构化规则由调用方注入（需要 message/emotion 上下文），此处只处理文本路径
        value = card.behavior_rules.strip()
        if not value:
            return None
        tpl = cfg.custom_templates.get(field) or _DEFAULT_TEMPLATES[field]
        return tpl.format(value=value)
    value = getattr(card, field, "").strip()
    if not value:
        return None
    tpl = cfg.custom_templates.get(field) or _DEFAULT_TEMPLATES[field]
    return tpl.format(value=value)


def _render_card_sections(
    card: CharacterCard,
    *,
    message: str | None,
    emotion: str | None,
    cfg: PromptConfig,
) -> list[str]:
    """按 PromptConfig（字段开关/顺序/自定义模板）渲染卡片字段段落。

    默认配置下输出与改造前硬编码拼装逐字节一致。
    """
    sections: list[str] = []
    for field in cfg.ordered_fields():
        if field not in CARD_FIELDS or not cfg.is_enabled(field):
            continue
        if field == "behavior_rules":
            # 结构化 if-then 规则优先（程序化判定，命中才注入）；否则用自由文本
            structured = render_rules(
                card.behavior_rules_structured,
                {"user_message": message or "", "current_emotion": emotion},
            )
            if structured:
                sections.append(structured)
                continue
        rendered = _render_field(card, field, cfg)
        if rendered:
            sections.append(rendered)
    return sections


def resolve_system_prompt(
    *,
    character_card: str | None,
    fallback_prompt: str | None,
    default_card: str | None = None,
    message: str | None = None,
    emotion: str | None = None,
    prompt_config: PromptConfig | None = None,
) -> str:
    """优先级链：卡内 system_prompt → V2 字段拼装 → 简化模式 fallback → 默认。

    - default_card：请求未携带角色卡时使用的内置默认角色卡（"深化单角色人设"）。
    - message：用于 Lorebook 关键词触发与结构化行为规则判定（user_message）。
    - emotion：当前轮检测出的情绪标签（结构化行为规则的 emotion_is 条件用）。
    - prompt_config：提示词拼装配置（字段开关/顺序/模板）；None 时取角色卡内嵌
      prompt_config，再缺省用默认（输出与改造前一致）。
    """
    raw = character_card or default_card
    card = CharacterCard.parse_raw_card(raw)
    if card is None:
        if fallback_prompt and fallback_prompt.strip():
            return fallback_prompt
        return DEFAULT_SYSTEM_PROMPT

    cfg = prompt_config or PromptConfig.from_any(card.prompt_config)

    if card.system_prompt and card.system_prompt.strip():
        # 卡内 system_prompt 完全覆盖字段拼装（原语义不变）
        prompt = card.system_prompt
    else:
        sections = _render_card_sections(card, message=message, emotion=emotion, cfg=cfg)
        prompt = "\n\n".join(sections).strip()

    # 注入 Lorebook（关键词触发的按需设定，避免一次性塞满 context）
    lore = _build_lorebook(card.character_book, message)
    if lore:
        prompt = (prompt + "\n\n" + lore) if prompt else lore

    if prompt.strip():
        # 卡内或默认角色卡生成成功
        return prompt
    if fallback_prompt and fallback_prompt.strip():
        return fallback_prompt
    return DEFAULT_SYSTEM_PROMPT


def _build_lorebook(book: dict | None, message: str | None) -> str:
    """从 character_book 中按 message 关键词匹配设定条目，拼为补充段落。

    无 message 时回退为「全部条目」（用于默认值兜底/调试）。无命中返回空串。
    """
    if not isinstance(book, dict):
        return ""
    entries = book.get("entries") or []
    if not entries:
        return ""
    matched: list[str] = []
    msg = message or ""
    for entry in entries:
        content = (entry.get("content") or "").strip()
        if not content:
            continue
        keys = entry.get("keys") or []
        if not msg:
            matched.append(content)
            continue
        for k in keys:
            if k and k in msg:
                matched.append(content)
                break
    if not matched:
        return ""
    return "【角色设定补充】\n" + "\n".join(f"- {m}" for m in matched)
