"""Live2D 映射层测试：15 类 + 父类链回退（ADR-7）。"""
import pytest

from roleplay.core.emotion.mapping import Live2DEmotionMapper


def test_resolve_parent_fallback_love_to_happy():
    # love 无独立 expression → 回退父类 happy 的 expression
    r = Live2DEmotionMapper().resolve("love", score=0.8)
    assert r is not None
    assert r["expression"] == "e_weixiao"
    assert r["motion"] == "t_weixiao"  # motion 细分保留


def test_resolve_parent_fallback_confused_to_anxious():
    # confused → anxious（以 EMOTION_PARENT 常量链为准）
    r = Live2DEmotionMapper().resolve("confused", score=0.9)
    assert r is not None
    assert r["expression"] == "e_yihuo"


def test_resolve_parent_fallback_disappointed_to_sad():
    r = Live2DEmotionMapper().resolve("disappointed", score=0.9)
    assert r is not None
    assert r["expression"] == "e_nanguo"


def test_resolve_parent_fallback_sleepy_to_neutral():
    r = Live2DEmotionMapper().resolve("sleepy", score=0.9)
    assert r is not None
    assert r["expression"] == "e_idle"


def test_resolve_unknown_emotion_to_default():
    # 非法 emotion（理论上不会出现，后端已归一化）→ default
    r = Live2DEmotionMapper().resolve("not-an-emotion", score=0.9)
    assert r is not None
    assert r["expression"] == "e_idle"


def test_resolve_below_threshold_returns_none():
    assert Live2DEmotionMapper().resolve("love", score=0.1) is None


def test_resolve_base_emotion_direct():
    r = Live2DEmotionMapper().resolve("happy", score=0.8)
    assert r["expression"] == "e_weixiao"
    assert r["motion"] == "b_diantou"


@pytest.mark.parametrize(
    "emotion",
    [
        "happy", "sad", "angry", "anxious", "surprise", "fear", "neutral",
        "love", "grateful", "excited", "disappointed", "lonely",
        "embarrassed", "confused", "sleepy",
    ],
)
def test_all_15_classes_resolve(emotion):
    # 15 类全部可解析（不抛异常、返回映射）
    r = Live2DEmotionMapper().resolve(emotion, score=0.9)
    assert r is not None
    assert "expression" in r
