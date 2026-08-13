"""聊天相关的数据传输对象（DTO）。

仅描述 API 边界上的数据结构，不含业务逻辑。遵循分层原则：
API 层负责与这些模型互转，业务层不直接耦合 HTTP 框架。
"""
from typing import Literal

import re
from pydantic import BaseModel, Field, field_validator

from ..config import get_settings

# 统一情绪枚举（详见 ARCHITECTURE.md：原两包前后端枚举错位的修正结果）
# 15 类 = 原 7 类（happy/sad/angry/anxious/surprise/fear/neutral）+ 新增 8 类
# （love/grateful/excited/disappointed/lonely/embarrassed/confused/sleepy）。
# 本处是后端唯一事实源；前端 EMOTION_CN 与 emotion_map.json 手工镜像。
EmotionLabel = Literal[
    "happy", "sad", "angry", "anxious", "surprise", "fear", "neutral",
    "love", "grateful", "excited", "disappointed", "lonely", "embarrassed", "confused", "sleepy",
]

# 父类表：新增 8 类的三级兜底映射（用于 Live2D 表情回退与展示分组）。
# 以本常量为准（架构师 ADR-7 已定：confused→anxious，与前端 json 表一致）。
EMOTION_PARENT: dict[str, str] = {
    "love": "happy",
    "grateful": "happy",
    "excited": "happy",
    "disappointed": "sad",
    "lonely": "sad",
    "embarrassed": "anxious",
    "confused": "anxious",
    "sleepy": "neutral",
}

# 可选大字段上限，防止超大角色卡/提示词造成内存或解析压力
_MAX_LONG_TEXT = 20_000


class LLMOverride(BaseModel):
    """请求级 LLM 接入覆盖（前端「模型切换」功能）。

    设计约束：
    - 纯请求级：仅本请求生效，绝不写回全局 frozen Settings（零后端代码改动）。
    - 字段全可选，缺省由构建侧回退到全局配置（如 provider 缺省沿用 settings.llm_provider）。
    - api_key 仅在请求体内传递，后端不落盘、不进日志。
    """

    provider: Literal["mock", "openai", "deepseek", "ollama"] | None = Field(
        None, description="提供方：mock/openai/deepseek/ollama（OpenAI 兼容协议）"
    )
    model: str | None = Field(None, description="模型名", max_length=128)
    base_url: str | None = Field(None, description="OpenAI 兼容 base_url", max_length=512)
    api_key: str | None = Field(None, description="API Key（仅本次请求使用）", max_length=512)
    timeout: float | None = Field(None, description="超时秒数", gt=0, le=300)


class ChatRequest(BaseModel):
    session_id: str = Field(..., min_length=1, max_length=128)
    message: str = Field(..., min_length=1, max_length=get_settings().max_message_length)
    character_card: str | None = Field(
        None, description="可选：Character Card V2 JSON 字符串", max_length=_MAX_LONG_TEXT
    )
    system_prompt: str | None = Field(
        None, description="可选：简化模式系统提示词", max_length=_MAX_LONG_TEXT
    )
    temperature: float | None = Field(
        None,
        description="可选：覆盖默认生成温度（0–2）。前端快捷键实时调节创意度。",
        ge=0.0,
        le=2.0,
    )
    use_web: bool = Field(
        False,
        description="可选：本轮是否实时联网检索并把结果注入知识库/RAG 上下文。",
    )
    character_id: str | None = Field(
        None,
        description="可选：指定使用的角色人设 id（覆盖当前激活角色）。",
    )
    llm: LLMOverride | None = Field(
        None,
        description="可选：请求级 LLM 接入覆盖（前端模型切换；不回写全局配置）。",
    )

    @field_validator("message")
    @classmethod
    def _strip_message(cls, v: str) -> str:
        # 安全过滤：移除控制字符（NUL、DEL、未定义 C0/C1 等），
        # 仅保留可见字符与常见的换行/制表，避免注入或解析异常。
        cleaned = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]", "", v or "")
        # 纯空白消息无意义且会触发空回复，去空白后判空
        stripped = cleaned.strip()
        if not stripped:
            raise ValueError("消息不能为空")
        return stripped


class EmotionInfo(BaseModel):
    emotion: EmotionLabel = "neutral"
    score: float = 0.0
    # 检测来源（仅日志/内部使用，不进入 SSE emotion 事件体；协议字段仍为 emotion+score）
    source: Literal["llm", "classifier", "keyword", "none"] = "none"


class ChatResponse(BaseModel):
    reply: str
    emotion: EmotionInfo = Field(default_factory=EmotionInfo)
    follow_ups: list[str] = Field(default_factory=list)


class ChatClearRequest(BaseModel):
    """清空某会话记忆的请求体（前端「清空记忆」按钮调用）。"""

    session_id: str = Field(..., min_length=1, max_length=128)
