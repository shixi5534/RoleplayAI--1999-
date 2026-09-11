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
    "post_history_instructions": "【对话风格】{value}",
}


# ───────────────────────── P2-1：动态压缩与重排（按会话轮次精简人设） ─────────────────────────
# 长对话中完整人设 + 完整示范会持续挤占 context，而历史摘要与 RAG 的信息密度更高。
# 三档策略（cfg.dynamic_compression 开启时生效；关闭时任何轮次输出与改造前逐字节一致）：
#   band 0（<6 轮） ：完整人设（零压缩）
#   band 1（6–20 轮）：mes_example 只保留第一组对话对——长对话后示范的教学价值
#                     集中在第一组（语气定调），后续组只会重复占用 context；
#   band 2（≥20 轮） ：只留 name + 一句话概括的人设 + 核心规则；scenario/background/
#                     first_mes/mes_example 全部撤下——设定细节由 RAG / Lorebook
#                     关键词触发按需带回，core_anchors 置底锚定身份不漂移。
# 刻意偏离计划处：band 2 保留 behavior_rules——行为约束字数少，且长对话恰恰是
# 最需要规则锚定的阶段（对抗角色漂移），删它省不了多少 context 还添风险。


def _compression_band(turn_count: int) -> int:
    """会话轮次 → 压缩档位：0=完整（<6）/ 1=精简示例（6–20）/ 2=精简人设（≥20）。"""
    t = max(0, int(turn_count or 0))
    if t < 6:
        return 0
    if t < 20:
        return 1
    return 2


def _one_line_summary(text: str) -> str:
    """人设「一句话概括」：取第一句（。！？；结尾），无句读时截前 60 字。"""
    text = text.strip()
    for sep in ("。", "！", "？", "；"):
        i = text.find(sep)
        if i != -1 and i + 1 <= 120:
            return text[: i + 1]
    return text[:60]


def _compress_card(card: CharacterCard, band: int) -> CharacterCard:
    """按档位返回压缩后的卡片副本（band 0 → 原卡对象，零开销）。

    用 model_copy 生成浅更新副本，绝不改原卡（卡片可能被 store 层复用）。
    字段清空后 _render_field 自然跳过（None），不会产生空块。
    """
    if band <= 0:
        return card
    update: dict = {}
    if band == 1:
        example = card.mes_example.strip()
        if "\n\n" in example:
            update["mes_example"] = example.split("\n\n", 1)[0]
    else:  # band 2
        update["mes_example"] = ""
        update["first_mes"] = ""
        update["scenario"] = ""
        update["background"] = ""
        personality = card.personality.strip()
        if personality:
            update["personality"] = _one_line_summary(personality)
    if not update:
        return card
    return card.model_copy(update=update)


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


def _render_behavior_rules(
    card: CharacterCard,
    *,
    message: str | None,
    emotion: str | None,
    cfg: PromptConfig,
) -> list[str]:
    """行为规则渲染：结构化 if-then（本轮命中的）+ 自由文本（核心规则）。

    两种模式（cfg.merge_structured_rules）：
    - False（默认）：命中即替换——有命中时只注入结构化块，文本仅在「零命中」
      时回落。与改造前语义逐字节一致（零回归）。
    - True（P0-5）：合并——文本核心规则常驻，再叠加本轮命中的条件规则。
      适合「核心 6 条常驻 + 4 条场景规则按需触发」的分层用法。
    """
    structured = render_rules(
        card.behavior_rules_structured,
        {"user_message": message or "", "current_emotion": emotion},
    )
    text = _render_field(card, "behavior_rules", cfg)
    if getattr(cfg, "merge_structured_rules", False):
        return [s for s in (structured, text) if s]
    return [structured] if structured else ([text] if text else [])


def _footer_set(cfg: PromptConfig) -> frozenset[str]:
    """置底字段集合（非法/未配置 → 空集，等价于不启用）。"""
    raw = cfg.footer_fields
    if not isinstance(raw, (list, tuple)):
        return frozenset()
    return frozenset(str(f) for f in raw if str(f) in CARD_FIELDS)


def render_footer_sections(
    card: CharacterCard,
    *,
    message: str | None,
    emotion: str | None,
    cfg: PromptConfig,
) -> list[str]:
    """渲染「置底字段」段落（footer_fields），顺序同 ordered_fields。

    与 _render_card_sections 的唯一差别是只渲染 footer_fields 命中的字段；
    调用方（build_roleplay_prompt）把它们追加到提示词最末尾。
    """
    footer = _footer_set(cfg)
    if not footer:
        return []
    sections: list[str] = []
    for field in cfg.ordered_fields():
        if field not in CARD_FIELDS or not cfg.is_enabled(field):
            continue
        if field not in footer:
            continue
        if field == "behavior_rules":
            sections.extend(
                _render_behavior_rules(card, message=message, emotion=emotion, cfg=cfg)
            )
            continue
        rendered = _render_field(card, field, cfg)
        if rendered:
            sections.append(rendered)
    return sections


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
    footer = _footer_set(cfg)
    sections: list[str] = []
    for field in cfg.ordered_fields():
        if field not in CARD_FIELDS or not cfg.is_enabled(field):
            continue
        if field in footer:
            continue  # 置底字段由 build_roleplay_prompt 追加在最末尾
        if field == "behavior_rules":
            # 结构化 if-then 规则（程序化判定，命中才注入）+ 自由文本规则，
            # 两者的组合方式由 cfg.merge_structured_rules 决定（见函数注释）。
            sections.extend(
                _render_behavior_rules(card, message=message, emotion=emotion, cfg=cfg)
            )
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
    turn_count: int = 0,
) -> str:
    """优先级链：卡内 system_prompt → V2 字段拼装 → 简化模式 fallback → 默认。

    - default_card：请求未携带角色卡时使用的内置默认角色卡（"深化单角色人设"）。
    - message：用于 Lorebook 关键词触发与结构化行为规则判定（user_message）。
    - emotion：当前轮检测出的情绪标签（结构化行为规则的 emotion_is 条件用）。
    - prompt_config：提示词拼装配置（字段开关/顺序/模板）；None 时取角色卡内嵌
      prompt_config，再缺省用默认（输出与改造前一致）。
    - turn_count：本会话累计轮次（P2-1 动态压缩的档位判据；默认 0 = 完整人设）。
    """
    raw = character_card or default_card
    card = CharacterCard.parse_raw_card(raw)
    if card is None:
        if fallback_prompt and fallback_prompt.strip():
            return fallback_prompt
        return DEFAULT_SYSTEM_PROMPT

    cfg = prompt_config or PromptConfig.from_any(card.prompt_config)

    # P2-1 动态压缩：长对话按档位精简人设字段，把 context 让给历史摘要与 RAG。
    # 压缩在渲染前作用于卡片副本，字段开关/顺序/模板逻辑完全复用。
    band = _compression_band(turn_count) if getattr(cfg, "dynamic_compression", False) else 0
    card = _compress_card(card, band)

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
    if not isinstance(entries, list) or not entries:
        return ""
    matched: list[str] = []
    used_chars = 0
    msg = message or ""
    for entry in entries:
        if len(matched) >= 40 or used_chars >= 4000:
            break
        if not isinstance(entry, dict):
            continue
        content = (entry.get("content") or "").strip()
        if not content:
            continue
        keys = entry.get("keys") or []
        if not isinstance(keys, (list, tuple, set)):
            continue
        if not msg:
            matched.append(content[:2000])
            used_chars += len(content[:2000])
            continue
        for k in keys:
            if isinstance(k, str) and k and k in msg:
                matched.append(content[:2000])
                used_chars += len(content[:2000])
                break
    if not matched:
        return ""
    return "【角色设定补充】\n" + "\n".join(f"- {m}" for m in matched)
