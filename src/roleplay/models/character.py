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
