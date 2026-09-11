"""Character Card V2 数据模型与解析。

仅定义数据结构与纯函数解析（无副作用、不依赖任何 app 内部模块），
便于在 service / api 层复用，也便于单元测试。
"""
import json
import logging
from typing import Any

from pydantic import BaseModel, Field, field_validator

from .chat import EmotionLabel
from ..core.character_normalizer import normalize_character_text

logger = logging.getLogger(__name__)


def _normalize_field(v: str | None, info) -> str | None:
    """字段级标准化：文本统一空白/标点，空值收敛为空串（system_prompt 除外，保留 None）。"""
    if v is None:
        return None if info.field_name == "system_prompt" else ""
    return normalize_character_text(v, field=info.field_name)


def _normalize_anchor_list(v: Any) -> list[str] | None:
    """核心锚点列表清洗：逐条轻量标准化，丢弃非字符串/空白项。

    None / 非 list → None（未启用，不阻断卡片加载）。
    空 list 原样保留为 []：与 None 区分，让「清空该字段」这一意图能传到
    CharacterStore.update（那里 None 表示「不覆盖」，[] 表示「清掉」）。

    模块级函数：CharacterCard 与 CharacterUpsert 共用同一套语义，避免两处漂移。
    """
    if v is None:
        return None
    if not isinstance(v, list):
        return None
    out: list[str] = []
    for item in v:
        if not isinstance(item, str):
            continue
        text = normalize_character_text(item, field="core_anchors")
        if text:
            out.append(text)
    return out


def _normalize_strategy_map(v: Any) -> dict[str, str] | None:
    """情绪策略表清洗：键小写去空白，值轻量标准化；丢弃空键/空值。

    None / 非 dict → None；空 dict 原样保留（语义同 _normalize_anchor_list）。
    """
    if v is None:
        return None
    if not isinstance(v, dict):
        return None
    out: dict[str, str] = {}
    for key, val in v.items():
        k = str(key).strip().lower()
        text = (
            normalize_character_text(val, field="emotion_strategies")
            if isinstance(val, str)
            else ""
        )
        if k and text:
            out[k] = text
    return out


# P1-3：情感层次表的合法键（其余键丢弃，避免脏数据进入提示词）
_LAYER_TEXT_KEYS = ("surface", "trigger_reaction", "trust_reaction")
_LAYER_LIST_KEYS = ("trigger_topics", "trust_signals")
_LAYER_KEYS = _LAYER_TEXT_KEYS + _LAYER_LIST_KEYS


def _normalize_layers_map(v: Any) -> dict[str, Any] | None:
    """情感层次表（emotional_layers）清洗。

    结构：{surface, trigger_topics, trigger_reaction, trust_signals, trust_reaction}
    - 文本键（surface / *_reaction）→ 轻量标准化后的字符串；
    - 列表键（trigger_topics / trust_signals）→ 非空白字符串列表（去重保序）；
    - 未知键丢弃；空值项丢弃。

    None / 非 dict → None（未启用，不阻断卡片加载）。
    清洗后为空的 dict 原样保留为 {}：与 None 区分，语义同 _normalize_anchor_list
    （CharacterStore.update 里 None=不覆盖，{}=清掉）。
    """
    if v is None:
        return None
    if not isinstance(v, dict):
        return None
    out: dict[str, Any] = {}
    for key in _LAYER_TEXT_KEYS:
        raw = v.get(key)
        if not isinstance(raw, str):
            continue
        text = normalize_character_text(raw, field="emotional_layers")
        if text:
            out[key] = text
    for key in _LAYER_LIST_KEYS:
        raw = v.get(key)
        if not isinstance(raw, (list, tuple)):
            continue
        seen: set[str] = set()
        items: list[str] = []
        for item in raw:
            if not isinstance(item, str):
                continue
            text = item.strip()
            if text and text not in seen:
                seen.add(text)
                items.append(text)
        if items:
            out[key] = items
    return out


class CharacterCard(BaseModel):
    """Character Card V2 核心字段（按需扩展）。"""

    name: str = "默认助手"
    description: str = ""
    personality: str = ""
    scenario: str = ""
    background: str = ""  # 背景设定
    behavior_rules: str = ""  # 行为准则（行为约束）
    # 结构化 if-then 行为规则（升级方案 A，可选）：
    # [{id, condition: {type: text_contains|text_regex|emotion_is,
    #                   field: user_message|current_emotion,
    #                   pattern, case_sensitive}, action, priority, enabled, category}]
    # 非空时优先于 behavior_rules 文本注入；空/非法回落文本路径。
    behavior_rules_structured: list[dict] | None = None
    # 提示词拼装配置（升级方案 D，可选）：{enabled_fields, field_order,
    # custom_templates, header_templates}。None = 默认（输出与改造前一致）。
    prompt_config: dict | None = None
    tone: str = ""  # 语气/文风（RAG 提示词系统：说话风格约束）
    first_mes: str = ""
    mes_example: str = ""
    post_history_instructions: str = ""
    system_prompt: str | None = None
    # 二期扩展：Lorebook（关键词触发的按需知识库）
    character_book: dict[str, Any] | None = None
    # 三期扩展：知识范围——限定该角色检索哪些知识库命名空间。
    # None/空 = 默认公共范围（events/web/episodic）；
    # 例：["lore_wu_ming_zhe", "events", "episodic"] 绑定角色专属资料。
    knowledge_scope: list[str] | None = None
    # 五期扩展 P0-2：角色核心锚点（3-5 条，每条建议 ≤20 字）——最不可漂移的
    # 核心特质，每轮在 system prompt 最末尾重复注入，对抗长对话的角色漂移。
    # None/空 = 不启用（输出与改造前逐字节一致）。
    core_anchors: list[str] | None = None
    # 五期扩展 P0-3：情绪回应策略表 {情绪标签: 回应策略}。按当前轮检测到的
    # 用户情绪动态注入对应策略，使「用户难过」与「用户生气」得到差异化回应。
    # 键为 EmotionLabel（15 类）；未直接命中的键会回落到 EMOTION_PARENT 父类。
    # None/空 = 不启用（输出与改造前逐字节一致）。
    emotion_strategies: dict[str, str] | None = None
    # 六期扩展 P1-3：情感节奏/防备层。定义角色在不同话题与亲密度下的"敞开心扉程度"：
    #   surface          日常基线姿态（疏离/礼貌/轻讽）
    #   trigger_topics   敏感话题词表（命中 → 回避或轻描淡写）
    #   trigger_reaction 被触发时的应对方式
    #   trust_signals    用户侧的信任信号（命中 → 罕见地放下防备）
    #   trust_reaction   信任积累后的回应方式
    # 每轮按「是否命中敏感话题 / 是否积累信任」注入对应策略（≤200 字）。
    # None/空 = 不启用（输出与改造前逐字节一致）。
    emotional_layers: dict[str, Any] | None = None
    # 七期扩展（GraphRAG P0）：实体别名表 {canonical: [alias...]}。
    # 人工权威归并，优先级高于抽取自动收编的别名（bind_alias_table 首注册优先）；
    # 用于消解「格蕾丝/莉莉/凯拉/塞西莉 都是无名者」这类跨称呼歧义。
    # None/空 = 不启用（图谱按抽取结果自动归并）。
    entity_aliases: dict[str, list[str]] | None = None

    # 四期扩展：语音人设（角色专属音色/语速/音调/音量）。
    # voice_id 为空 = 未指定，由前端/后端各自默认音色兜底。
    voice_id: str = ""
    tts_speed: float = Field(1.0, ge=0.5, le=2.0)
    tts_pitch: float = Field(1.0, ge=0.5, le=2.0)
    tts_volume: float = Field(1.0, ge=0.0, le=1.0)

    # ── 角色设定标准化（模型层兜底） ──
    # 入库的任意文本字段统一走 normalize_character_text：空白/标点/列表结构化。
    # 调用链：前端表单 → CharacterUpsert → store._build_card → CharacterCard
    # —— 本 validator 与 store 层清洗互为冗余，保证任何入口构造出的卡都干净。
    @field_validator(
        "name", "description", "personality", "scenario", "background",
        "behavior_rules", "tone", "first_mes", "mes_example",
        "post_history_instructions",
    )
    @classmethod
    def _clean_text(cls, v: str | None, info) -> str:
        return _normalize_field(v, info)  # type: ignore[return-value]

    @field_validator("system_prompt")
    @classmethod
    def _clean_system_prompt(cls, v: str | None, info) -> str | None:
        # 空白 system_prompt → None（表示"未指定，走自动拼装"）
        if v is not None and not v.strip():
            return None
        return _normalize_field(v, info)  # type: ignore[return-value]

    @field_validator("core_anchors")
    @classmethod
    def _clean_core_anchors(cls, v: list[str] | None) -> list[str] | None:
        """锚点清洗：逐条轻量标准化，丢弃非法/空白项；全空收敛为 None。

        非法类型（非 list）→ None（等价于「未启用」，不阻断卡片加载）。
        """
        return _normalize_anchor_list(v)

    @field_validator("emotion_strategies")
    @classmethod
    def _clean_emotion_strategies(cls, v: dict | None) -> dict[str, str] | None:
        """策略表清洗：键小写去空白，值轻量标准化；全空收敛为 None。

        非 dict 输入 → None（不阻断卡片加载）。
        """
        return _normalize_strategy_map(v)

    @field_validator("emotional_layers", mode="before")
    @classmethod
    def _clean_emotional_layers(cls, v: Any) -> dict[str, Any] | None:
        """情感层次表清洗：文本键标准化、列表键去空白去重、未知键丢弃。

        用 mode="before"：非 dict 输入（脏数据、类型被改坏的旧卡）在正常类型校验
        **之前**就被收敛成 None，而不是抛 ValidationError 让整张卡加载失败。
        （比 core_anchors / emotion_strategies 更宽松是刻意的——情感层次是可选
        增强字段，不该因为一个坏值把整个人设打回默认提示词。）
        """
        return _normalize_layers_map(v)

    @classmethod
    def parse_raw_card(cls, raw: str | None) -> "CharacterCard | None":
        """解析角色卡 JSON 字符串（兼容 {"data": {...}} 包裹）。

        非法 / 缺失返回 None，调用方据此回落到默认提示词。
        """
        if not raw:
            return None
        try:
            data: Any = json.loads(raw)
        except (ValueError, TypeError):
            return None
        if not isinstance(data, dict):
            return None
        if isinstance(data.get("data"), dict):
            data = data["data"]
        try:
            return cls.model_validate(data)
        except Exception as exc:
            # 非法角色卡：回退默认，但记录原因便于排查（不抛异常，保持接口健壮性）
            logger.warning("角色卡解析失败，回落默认提示词：%s", exc)
            return None


class CharacterUpsert(BaseModel):
    """角色人设增改请求体（字段均可选，更新时仅覆盖提供的字段）。"""

    name: str | None = None
    description: str | None = None
    personality: str | None = None
    scenario: str | None = None
    background: str | None = None
    behavior_rules: str | None = None
    behavior_rules_structured: list[dict] | None = None
    prompt_config: dict | None = None
    tone: str | None = None
    first_mes: str | None = None
    mes_example: str | None = None
    post_history_instructions: str | None = None
    system_prompt: str | None = None
    character_book: dict[str, Any] | None = None
    knowledge_scope: list[str] | None = None
    # 五期扩展 P0-2/P0-3（与 CharacterCard 对应）
    core_anchors: list[str] | None = None
    emotion_strategies: dict[str, str] | None = None
    # 六期扩展 P1-3（与 CharacterCard 对应）
    emotional_layers: dict[str, Any] | None = None
    # 四期扩展：语音人设（与 CharacterCard 对应）
    voice_id: str | None = None
    tts_speed: float | None = Field(None, ge=0.5, le=2.0)
    tts_pitch: float | None = Field(None, ge=0.5, le=2.0)
    tts_volume: float | None = Field(None, ge=0.0, le=1.0)

    # 请求体同样走字段级标准化：避免"空白但非空"的字段（"  "）进入更新语义
    @field_validator(
        "name", "description", "personality", "scenario", "background",
        "behavior_rules", "tone", "first_mes", "mes_example",
        "post_history_instructions",
    )
    @classmethod
    def _clean_text(cls, v: str | None, info) -> str | None:
        return _normalize_field(v, info)

    @field_validator("system_prompt")
    @classmethod
    def _clean_system_prompt(cls, v: str | None, info) -> str | None:
        # 请求体里 system_prompt 为空白字符串 → None（表示"不覆盖/走自动拼装"）
        if v is not None and not v.strip():
            return None
        return _normalize_field(v, info)

    @field_validator("core_anchors")
    @classmethod
    def _clean_core_anchors(cls, v: list[str] | None) -> list[str] | None:
        return _normalize_anchor_list(v)

    @field_validator("emotion_strategies")
    @classmethod
    def _clean_emotion_strategies(cls, v: dict | None) -> dict[str, str] | None:
        return _normalize_strategy_map(v)

    @field_validator("emotional_layers", mode="before")
    @classmethod
    def _clean_emotional_layers(cls, v: Any) -> dict[str, Any] | None:
        return _normalize_layers_map(v)
