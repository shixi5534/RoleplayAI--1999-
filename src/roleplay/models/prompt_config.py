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
    "post_history_instructions",
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
    "post_history_instructions",
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
    # 置底字段（升级方案 E）：这些字段不参与正常顺序渲染，而是统一追加到
    # 提示词**最末尾**（tone / profile / rag 三个块之后）。
    # 用途：把「对话风格 / 输出格式」类指令放在检索资料块之后，对抗
    # lost-in-the-middle 与近因效应——否则模型会模仿紧邻其前的百科/剧本文体。
    # None / 空 = 不启用（默认输出与改造前逐字节一致，零回归）。
    footer_fields: list[str] | None = None
    # 结构化行为规则与自由文本的合并模式（P0-5）：
    #   False（默认）= 命中即替换——structured 有命中时只注入它，回落文本仅
    #     在「一条都没命中」时使用（改造前的既有语义，零回归）；
    #   True = 合并——文本规则（核心）始终注入，再叠加本轮命中的条件规则。
    # 用途：把「核心规则常驻 + 场景规则按需触发」两种用法都保留，由角色卡自选。
    merge_structured_rules: bool = False
    # 分层消息结构（P1-1）：
    #   False（默认）= 单 system 模式——所有块拼进一个 system 消息，
    #     与改造前逐字节一致（零回归，且兼容不支持多 system 的端点）；
    #   True = 分层模式——核心人设 / 用户画像 / RAG 资料各自成为独立 system 消息，
    #     而「情绪策略 + 风格指令 + 核心锚点 + 复读抑制」移到当前 user 消息前缀
    #     （近因效应最强的位置，对抗 lost-in-the-middle）。
    # 仅在 build_roleplay_messages 使用；build_roleplay_prompt 恒定单串输出。
    message_layering: bool = False
    # 动态长度提示（P1-2）：按当前用户消息长度/情绪，在提示词里给出本轮目标句数。
    #   False（默认）= 不注入长度指令（零回归，长度由角色卡 post_history_instructions 决定）；
    #   True = 追加「本轮回复目标句数」提示（<10字→1-2句，10-30字→2-4句，>30字或情绪激烈→3-6句）。
    dynamic_length: bool = False
    # 动态压缩与重排（P2-1）：按会话轮次精简人设，长对话把 context 让给历史与 RAG。
    #   False（默认）= 不压缩（零回归，任何轮次输出一致）；
    #   True = 三档压缩（见 character_card._compression_band）：
    #     <6 轮   完整人设 + 完整 mes_example + 全部规则（与关闭时逐字节一致）；
    #     6–20 轮 mes_example 只保留第一组对话对（精简示范）；
    #     ≥20 轮  只留 name + 一句话概括的人设 + 核心规则，scenario/background/
    #             first_mes/mes_example 全部撤下（细节由 RAG / Lorebook 按需带回）。
    dynamic_compression: bool = False

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
