"""数据模型包：API 边界 DTO 与领域模型。"""
from .chat import ChatRequest, ChatResponse, EmotionInfo, EmotionLabel
from .character import CharacterCard

__all__ = [
    "ChatRequest",
    "ChatResponse",
    "EmotionInfo",
    "EmotionLabel",
    "CharacterCard",
]
