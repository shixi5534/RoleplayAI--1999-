"""情感检测端口与适配器、Live2D 表情映射。"""
from .classifier import LocalClassifierDetector
from .detector import (
    EmotionPort,
    FallbackChainDetector,
    KeywordEmotionDetector,
    LLMEmotionDetector,
    build_emotion_detector,
    normalize_emotion_label,
)
from .mapping import Live2DEmotionMapper

__all__ = [
    "EmotionPort",
    "KeywordEmotionDetector",
    "LLMEmotionDetector",
    "LocalClassifierDetector",
    "FallbackChainDetector",
    "normalize_emotion_label",
    "build_emotion_detector",
    "Live2DEmotionMapper",
]
