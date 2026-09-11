"""情感检测单元测试（async 化 + 15 类 + 责任链 + LLM 归一化/降级）。"""
import pytest

from roleplay.core.emotion.classifier import LocalClassifierDetector
from roleplay.core.emotion.detector import (
    FallbackChainDetector,
    KeywordEmotionDetector,
    LLMEmotionDetector,
    build_emotion_detector,
    normalize_emotion_label,
)
from roleplay.core.llm.mock import MockLLMProvider


async def test_detect_sad(detector):
    r = await detector.detect("我好难过啊")
    assert r.emotion == "sad"
    assert r.score > 0
    assert r.source == "keyword"


async def test_detect_anxious():
    d = KeywordEmotionDetector()
    assert (await d.detect("我很担心明天的考试")).emotion == "anxious"


async def test_detect_fear():
    d = KeywordEmotionDetector()
    assert (await d.detect("这个地方好恐怖，我很害怕")).emotion == "fear"


async def test_negation_returns_neutral():
    d = KeywordEmotionDetector()
    # 否定词前缀应抑制愤怒判定
    assert (await d.detect("其实我不生气")).emotion == "neutral"


async def test_neutral_default():
    d = KeywordEmotionDetector()
    assert (await d.detect("今天就是普通的一天")).emotion == "neutral"


async def test_disabled_returns_neutral():
    d = KeywordEmotionDetector(enabled=False)
    assert (await d.detect("我好难过")).emotion == "neutral"


async def test_score_capped_at_one():
    # 多个同类关键词命中时，分数应封顶在 1.0（[0,1] 契约）
    d = KeywordEmotionDetector()
    r = await d.detect("我好难过好难过好难过好难过好难过")
    assert 0.0 <= r.score <= 1.0


# ───────────────────────── 15 类关键词全覆盖 ─────────────────────────
@pytest.mark.parametrize(
    "text,expected",
    [
        ("我好开心啊", "happy"),
        ("我好难过", "sad"),
        ("我真的很生气", "angry"),
        ("我很担心明天的考试", "anxious"),
        ("天哪！居然是真的", "surprise"),
        ("这地方好恐怖", "fear"),
        ("今天就是普通的一天", "neutral"),
        ("我爱你", "love"),
        ("太感谢你了", "grateful"),
        ("好激动啊", "excited"),
        ("我好失望", "disappointed"),
        ("好孤独", "lonely"),
        ("好尴尬", "embarrassed"),
        ("我搞不懂", "confused"),
        ("好困啊", "sleepy"),
    ],
)
async def test_keyword_15_classes(text, expected):
    d = KeywordEmotionDetector()
    assert (await d.detect(text)).emotion == expected


# ───────────────────────── normalize_emotion_label ─────────────────────────
def test_normalize_alias():
    assert normalize_emotion_label("joy") == "happy"
    assert normalize_emotion_label("Joy") == "happy"
    assert normalize_emotion_label("terrified") == "fear"
    assert normalize_emotion_label("tired") == "sleepy"
    assert normalize_emotion_label("love") == "love"


def test_normalize_invalid_to_neutral():
    assert normalize_emotion_label("not-a-real-emotion") == "neutral"
    assert normalize_emotion_label("") == "neutral"
    assert normalize_emotion_label(None) == "neutral"
    assert normalize_emotion_label("nonsense!") == "neutral"


# ───────────────────────── LLM 检测器（复用 MockLLMProvider） ─────────────────────────
class _JsonLLM(MockLLMProvider):
    """可控 Mock：按 user 文本返回预置 JSON 字符串。"""

    def __init__(self, reply: str) -> None:
        super().__init__()
        self._reply = reply

    async def generate(self, *, system, user, history=None, temperature=None) -> str:
        return self._reply


async def test_llm_detector_valid_json():
    d = LLMEmotionDetector(
        llm=_JsonLLM('{"emotion": "love", "score": 0.9, "reason": "表白"}'),
        enabled=True,
    )
    r = await d.detect("我喜欢你")
    assert r.emotion == "love"
    assert r.score == 0.9
    assert r.source == "llm"


async def test_llm_detector_json_block_and_alias():
    d = LLMEmotionDetector(
        llm=_JsonLLM('```json\n{"emotion": "joy", "score": 0.8}\n```'),
        enabled=True,
    )
    r = await d.detect("开心")
    assert r.emotion == "happy"  # joy → happy 别名归一化
    assert r.score == 0.8


async def test_llm_detector_regex_fallback():
    d = LLMEmotionDetector(
        llm=_JsonLLM('garbage {"emotion": "sad", "score": 0.7} trailing'),
        enabled=True,
    )
    r = await d.detect("难过")
    assert r.emotion == "sad"
    assert r.score == 0.7


async def test_llm_detector_parse_fail_to_neutral():
    d = LLMEmotionDetector(llm=_JsonLLM("完全不是 JSON"), enabled=True)
    r = await d.detect("随便")
    assert r.emotion == "neutral"
    assert r.source == "llm"


async def test_llm_detector_exception_to_neutral():
    class _BoomLLM(MockLLMProvider):
        async def generate(self, *, system, user, history=None, temperature=None) -> str:
            raise RuntimeError("boom")

    d = LLMEmotionDetector(llm=_BoomLLM(), enabled=True)
    r = await d.detect("难过")
    assert r.emotion == "neutral"
    assert r.source == "none"  # 异常 → 不抛，source=none


async def test_llm_detector_low_confidence_sinks():
    d = LLMEmotionDetector(
        llm=_JsonLLM('{"emotion": "love", "score": 0.2}'),
        enabled=True,
        confidence=0.4,
    )
    r = await d.detect("我喜欢你")
    assert r.emotion == "neutral"  # 低置信 → 中性（责任链继续下沉）


# ───────────────────────── 本地分类器 ─────────────────────────
def test_classifier_hashing_available():
    d = LocalClassifierDetector(enabled=True, backend="hashing")
    assert d.available is True


async def test_classifier_jina_disabled():
    # P1.5 接口位：jina 本期不实现 → 自动禁用
    d = LocalClassifierDetector(enabled=True, backend="jina")
    assert d.available is False
    r = await d.detect("随便")
    assert r.emotion == "neutral"
    assert r.source == "none"


async def test_classifier_detect_returns_some_label():
    d = LocalClassifierDetector(enabled=True, backend="hashing")
    # 只要不抛异常、来源正确即可（内置权重为启发式常量，不保证精度）
    r = await d.detect("我爱你")
    assert r.source in ("classifier", "none")
    assert r.emotion in ("love", "happy", "neutral")


# ───────────────────────── 责任链降级 ─────────────────────────
class _FailingDetector:
    async def detect(self, text):
        raise RuntimeError("fail")


class _NeutralDetector:
    async def detect(self, text):
        from roleplay.models.chat import EmotionInfo

        return EmotionInfo(emotion="neutral", score=0.0, source="none")


async def test_chain_first_hit_wins():
    d = FallbackChainDetector(
        chain=[
            LLMEmotionDetector(llm=_JsonLLM('{"emotion": "angry", "score": 0.9}'), enabled=True),
            KeywordEmotionDetector(),
        ]
    )
    r = await d.detect("生气")
    assert r.emotion == "angry"
    assert r.source == "llm"


async def test_chain_llm_fail_then_keyword():
    d = FallbackChainDetector(
        chain=[_FailingDetector(), KeywordEmotionDetector()]
    )
    r = await d.detect("我好难过")
    assert r.emotion == "sad"
    assert r.source == "keyword"


async def test_chain_all_neutral_falls_to_none():
    d = FallbackChainDetector(chain=[_NeutralDetector(), _NeutralDetector()])
    r = await d.detect("随便")
    assert r.emotion == "neutral"
    assert r.source == "none"


async def test_chain_llm_neutral_then_keyword():
    # LLM 说 neutral 不算失败，但会继续让关键词尝试
    d = FallbackChainDetector(
        chain=[
            LLMEmotionDetector(llm=_JsonLLM('{"emotion": "neutral", "score": 0.1}'), enabled=True),
            KeywordEmotionDetector(),
        ]
    )
    r = await d.detect("好孤独")
    assert r.emotion == "lonely"
    assert r.source == "keyword"


# ───────────────────────── 工厂组装 ─────────────────────────
def test_build_keyword_mode():
    from roleplay.config import Settings

    s = Settings(emotion_detector="keyword", llm_provider="mock", llm_api_key="")
    det = build_emotion_detector(enabled=True, settings=s)
    assert isinstance(det, KeywordEmotionDetector)


def test_build_auto_mock_llm_disabled():
    # auto 模式 + mock provider → LLM 层不可用（隐私：不私自外发）
    # → classifier→keyword 责任链（ADR-5：LLM 不可用但分类器可用时）
    from roleplay.config import Settings

    s = Settings(emotion_detector="auto", llm_provider="mock", llm_api_key="")
    det = build_emotion_detector(enabled=True, settings=s)
    assert isinstance(det, FallbackChainDetector)
    assert len(det.chain) == 2
    assert isinstance(det.chain[0], LocalClassifierDetector)
    assert isinstance(det.chain[1], KeywordEmotionDetector)


def test_build_llm_mode_with_key():
    # llm 模式 + 非 mock + 有 key → 责任链（LLM → classifier → keyword）
    from roleplay.config import Settings

    s = Settings(
        emotion_detector="llm",
        llm_provider="openai",
        llm_api_key="sk-test",
        llm_base_url="https://api.openai.com/v1",
    )
    det = build_emotion_detector(enabled=True, settings=s)
    assert isinstance(det, FallbackChainDetector)
    assert len(det.chain) == 3


def test_build_disabled_returns_keyword():
    from roleplay.config import Settings

    s = Settings(emotion_detector="auto", llm_provider="mock")
    det = build_emotion_detector(enabled=False, settings=s)
    assert isinstance(det, KeywordEmotionDetector)
