"""提示词组装配置（升级方案 D）：字段开关 / 顺序 / 自定义模板。

默认配置的输出与改造前逐字节一致（零回归）；角色卡内嵌 prompt_config
可覆盖；全局层由 config.py 的 prompt_config_path 提供文件级默认。
"""
from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

# 卡片字段（resolve_system_prompt 拼装的 V2 字段）
CARD_FIELDS = (
    "name",
    "personality",
    "background",
    "behavior_rules",
    "scenario",
    "first_mes",
    "mes_example",
)

# 外层块字段（build_roleplay_prompt 追加的块）
BLOCK_FIELDS = ("tone", "profile", "rag")

ALL_FIELDS = CARD_FIELDS + BLOCK_FIELDS

# 默认字段顺序（与改造前硬编码顺序一致 → 零回归）
DEFAULT_ORDER = (
    "name",
    "personality",
    "background",
    "behavior_rules",
    "scenario",
    "first_mes",
    "mes_example",
    "tone",
    "profile",
    "rag",
)


class PromptConfig(BaseModel):
    """提示词拼装配置。

    - enabled_fields：启用的字段（None = 全部启用）。关闭的字段完全跳过渲染。
    - field_order：渲染顺序（None = DEFAULT_ORDER）。未列入的启用字段按默认顺序排后。
    - custom_templates：字段级自定义模板，{value} 占位符。仅覆盖默认模板。
    - header_templates：块头自定义（profile / rag），{header} 不支持，直接给整块头部文本。
    """

    enabled_fields: list[str] | None = None
    field_order: list[str] | None = None
    custom_templates: dict[str, str] = Field(default_factory=dict)
    header_templates: dict[str, str] = Field(default_factory=dict)

    @classmethod
    def from_any(cls, raw: Any) -> "PromptConfig":
        """宽松解析：None/非法输入 → 默认配置（不抛异常）。"""
        if raw is None:
            return cls()
        if isinstance(raw, str):
            import json

            try:
                raw = json.loads(raw)
            except (ValueError, TypeError):
                return cls()
        if not isinstance(raw, dict):
            return cls()
        try:
            return cls.model_validate(raw)
        except Exception:  # noqa: BLE001
            return cls()

    def is_enabled(self, field: str) -> bool:
        if self.enabled_fields is None:
            return True
        return field in self.enabled_fields

    def ordered_fields(self) -> list[str]:
        """有效渲染顺序：field_order 优先，其余启用字段按 DEFAULT_ORDER 补尾。"""
        order = [f for f in (self.field_order or DEFAULT_ORDER) if f in ALL_FIELDS]
        rest = [f for f in DEFAULT_ORDER if f not in order]
        return order + rest


DEFAULT_CONFIG = PromptConfig()
