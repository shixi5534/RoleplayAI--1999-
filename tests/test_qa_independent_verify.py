"""QA 独立验证（不采信工程师自我验证）：边界 + 击穿尝试。

覆盖：
- B1 归一化边界（大小写/空白/别名/空/None/非字符串/未知）
- B2 责任链穿透（LLM/classifier 双异常 → keyword；LLM neutral → classifier 接住）
- B3 父类回退（15 类逐一 + 阈值 + 未知名）
- B4 SSE 契约（事件体严格 {emotion, score}，无 source 泄漏；15 类可序列化）
- B6 async 正确性（orchestrator 确实 await detect）
- C1 并发/超时路径（wait_for 生效，不阻塞主回复流）
- C2 分类器/关键词空输入与超长文本
- C3 LLM 输出解析畸形（纯文本/数组/非法 emotion/越界 score/字符串 score）
"""
import asyncio
import json
import re
import time

import pytest

from roleplay.core.emotion.classifier import LocalClassifierDetector
from roleplay.core.emotion.detector import (
    FallbackChainDetector,
    KeywordEmotionDetector,
    LLMEmotionDetector,
    normalize_emotion_label,
)
from roleplay.core.emotion.mapping import Live2DEmotionMapper
from roleplay.core.llm.mock import MockLLMProvider
from roleplay.core.orchestrator import ChatOrchestrator
from roleplay.core.rag.memory import InMemoryVectorStore
from roleplay.models.chat import ChatRequest, EMOTION_PARENT, EmotionLabel, EmotionInfo

ALL_15 = [
    "happy", "sad", "angry", "anxious", "surprise", "fear", "neutral",
    "love", "grateful", "excited", "disappointed", "lonely",
    "embarrassed", "confused", "sleepy",
]


class _JsonLLM(MockLLMProvider):
    def __init__(self, reply: str) -> None:
        super().__init__()
        self._reply = reply

    async def generate(self, *, system, user, history=None, temperature=None) -> str:
        return self._reply


class _SlowLLM(MockLLMProvider):
    """generate 挂起直到超时（模拟 LLM 卡死）。"""

    def __init__(self, delay: float = 5.0) -> None:
        super().__init__()
        self._delay = delay

    async def generate(self, *, system, user, history=None, temperature=None) -> str:
        await asyncio.sleep(self._delay)
        return '{"emotion": "happy", "score": 0.9}'


class _BoomDetector:
    async def detect(self, text):
        raise RuntimeError("boom")


# ───────────────────────── B1 归一化边界 ─────────────────────────
@pytest.mark.parametrize(
    "raw,expected",
    [
        ("LOVE", "love"),          # 大写
        ("Happy", "happy"),        # 首字母大写
        ("JOY", "happy"),          # 大写别名
        ("TERRIFIED", "fear"),     # 大写别名
        ("TIRED", "sleepy"),       # 大写别名
        (" love ", "love"),        # 首尾空格
        ("disappointed", "disappointed"),
        ("confused", "confused"),
        ("embarrassed", "embarrassed"),
        ("grateful", "grateful"),
        ("excited", "excited"),
        ("lonely", "lonely"),
        ("sleepy", "sleepy"),
        ("surprised", "surprise"),
        ("afraid", "fear"),
        ("worried", "anxious"),
        ("mad", "angry"),
        ("unhappy", "sad"),
        ("", "neutral"),
        ("   ", "neutral"),
        (None, "neutral"),
        (123, "neutral"),          # 非字符串
        (["happy"], "neutral"),    # 非字符串（list）
        ("banana", "neutral"),     # 未知词
        ("not-a-real-emotion", "neutral"),
    ],
)
def test_b1_normalize_boundary(raw, expected):
    assert normalize_emotion_label(raw) == expected


def test_b1_normalize_multiword_no_crash():
    # 多词标签不抛异常；回退值必须是 15 类之一（合法标签）
    for raw in ["love love", "happy sad", "I am happy", "disappointed!", "happy!!"]:
        r = normalize_emotion_label(raw)
        assert r in ALL_15, f"{raw!r} -> {r!r} 不在 15 类"


# ───────────────────────── B2 责任链穿透 ─────────────────────────
async def test_b2_chain_double_exception_then_keyword():
    """LLM 抛异常 → classifier 抛异常 → keyword 兜底：返回 EmotionInfo 且 source=keyword。"""
    d = FallbackChainDetector(chain=[_BoomDetector(), _BoomDetector(), KeywordEmotionDetector()])
    r = await d.detect("我好难过")
    assert isinstance(r, EmotionInfo)
    assert r.emotion == "sad"
    assert r.source == "keyword"


async def test_b2_chain_llm_neutral_then_classifier():
    """LLM 返回 neutral → classifier 能接住显式情绪（不直接落 keyword）。"""
    d = FallbackChainDetector(
        chain=[
            LLMEmotionDetector(llm=_JsonLLM('{"emotion": "neutral", "score": 0.5}'), enabled=True),
            LocalClassifierDetector(enabled=True, backend="hashing"),
            KeywordEmotionDetector(),
        ]
    )
    r = await d.detect("我爱你")
    assert isinstance(r, EmotionInfo)
    assert r.emotion != "neutral"
    assert r.source in ("classifier", "keyword")


async def test_b2_chain_all_fail_returns_neutral_none():
    d = FallbackChainDetector(chain=[_BoomDetector(), _BoomDetector()])
    r = await d.detect("随便")
    assert r.emotion == "neutral"
    assert r.score == 0.0
    assert r.source == "none"


# ───────────────────────── B3 父类回退 ─────────────────────────
@pytest.mark.parametrize(
    "emotion,parent,expected_expr",
    [
        ("love", "happy", "e_weixiao"),
        ("grateful", "happy", "e_weixiao"),
        ("excited", "happy", "e_weixiao"),
        ("disappointed", "sad", "e_nanguo"),
        ("lonely", "sad", "e_nanguo"),
        ("embarrassed", "anxious", "e_yihuo"),
        ("confused", "anxious", "e_yihuo"),
        ("sleepy", "neutral", "e_idle"),
    ],
)
def test_b3_parent_fallback(emotion, parent, expected_expr):
    assert EMOTION_PARENT[emotion] == parent
    r = Live2DEmotionMapper().resolve(emotion, score=0.9)
    assert r is not None
    assert r["expression"] == expected_expr


def test_b3_below_threshold_returns_none():
    # 默认 score_threshold=0.3；score=0.3 恰好等于阈值应返回映射，0.29 返回 None
    m = Live2DEmotionMapper()
    assert m.resolve("love", score=0.3) is not None
    assert m.resolve("love", score=0.29) is None


def test_b3_unknown_emotion_to_default():
    r = Live2DEmotionMapper().resolve("alien-emotion", score=0.9)
    assert r is not None
    assert r["expression"] == "e_idle"


# ───────────────────────── B4 SSE 契约 ─────────────────────────
async def test_b4_emotion_event_strict_contract():
    """emotion 事件体严格只含 {emotion, score}——source 不泄漏。"""
    orch = ChatOrchestrator(
        llm=MockLLMProvider(),
        emotion=KeywordEmotionDetector(),
        rag=InMemoryVectorStore(),
    )
    events = []
    async for ev in orch.stream(ChatRequest(session_id="s", message="我好难过")):
        events.append(ev)
    emo_events = [e for e in events if e["type"] == "emotion"]
    assert len(emo_events) == 1
    assert set(emo_events[0].keys()) == {"type", "emotion", "score"}
    assert "source" not in emo_events[0]
    assert emo_events[0]["emotion"] == "sad"
    assert 0.0 <= emo_events[0]["score"] <= 1.0
    assert any(e["type"] == "done" for e in events)


async def test_b4_all_15_emotions_serialize_via_sse():
    """15 类任意 emotion 都能通过 stream 事件（无 pydantic 校验错误）。"""
    class _FixedEmotion:
        def __init__(self, emotion, score):
            self._emotion = emotion
            self._score = score

        async def detect(self, text):
            return EmotionInfo(emotion=self._emotion, score=self._score, source="keyword")

    for emo in ALL_15:
        orch = ChatOrchestrator(
            llm=MockLLMProvider(),
            emotion=_FixedEmotion(emo, 0.9),
            rag=InMemoryVectorStore(),
        )
        seen = []
        async for ev in orch.stream(ChatRequest(session_id="s", message="测试")):
            seen.append(ev)
        emo_ev = next(e for e in seen if e["type"] == "emotion")
        # SSE 序列化（模拟 api/chat.py 的 json.dumps）
        payload = json.dumps(
            {"emotion": emo_ev["emotion"], "score": emo_ev["score"]}, ensure_ascii=False
        )
        parsed = json.loads(payload)
        assert parsed["emotion"] == emo
        assert parsed["score"] == 0.9


# ───────────────────────── B6 async 正确性 ─────────────────────────
async def test_b6_orchestrator_awaits_detect():
    """确认 orchestrator 真正 await 了 emotion.detect（async 调用无遗漏）。"""
    calls = []

    class _SpyDetector:
        async def detect(self, text):
            calls.append(text)
            return EmotionInfo(emotion="angry", score=0.8, source="keyword")

    orch = ChatOrchestrator(
        llm=MockLLMProvider(),
        emotion=_SpyDetector(),
        rag=InMemoryVectorStore(),
        mapper=Live2DEmotionMapper(),
    )
    res = await orch.run(ChatRequest(session_id="s", message="我真的很生气"))
    assert calls == ["我真的很生气"]
    assert res.response.emotion.emotion == "angry"


# ───────────────────────── C1 超时路径 ─────────────────────────
async def test_c1_llm_timeout_does_not_block():
    """LLM 挂起 → wait_for 生效快速返回 neutral/none，不抛异常。"""
    d = LLMEmotionDetector(llm=_SlowLLM(delay=5.0), timeout=0.05, enabled=True)
    t0 = time.monotonic()
    r = await d.detect("测试")
    elapsed = time.monotonic() - t0
    assert elapsed < 2.0, f"超时未生效，耗时 {elapsed:.2f}s"
    assert r.emotion == "neutral"
    assert r.source == "none"


async def test_c1_timeout_not_blocking_main_reply_stream():
    """orchestrator 主回复流在 LLM 检测超时后仍正常产出 done 事件。"""
    slow_llm_det = LLMEmotionDetector(llm=_SlowLLM(delay=5.0), timeout=0.05, enabled=True)
    orch = ChatOrchestrator(
        llm=MockLLMProvider(),
        emotion=slow_llm_det,
        rag=InMemoryVectorStore(),
    )
    t0 = time.monotonic()
    events = []
    async for ev in orch.stream(ChatRequest(session_id="s", message="测试超时")):
        events.append(ev)
    elapsed = time.monotonic() - t0
    assert elapsed < 3.0, f"主回复流被 LLM 超时阻塞：{elapsed:.2f}s"
    assert any(e["type"] == "emotion" for e in events)
    assert any(e["type"] == "done" for e in events)


# ───────────────────────── C2 空输入 / 超长文本 ─────────────────────────
async def test_c2_empty_and_blank_inputs():
    kw = KeywordEmotionDetector()
    cls = LocalClassifierDetector(enabled=True, backend="hashing")
    for text in ["", "   ", "\n\t"]:
        r_kw = await kw.detect(text)
        assert r_kw.emotion == "neutral" and r_kw.score == 0.0
        r_cls = await cls.detect(text)
        assert r_cls.emotion == "neutral"


async def test_c2_long_text_10k_no_crash():
    text = "我很开心 " * 2000  # 10000+ 字符
    kw = KeywordEmotionDetector()
    cls = LocalClassifierDetector(enabled=True, backend="hashing")
    r_kw = await kw.detect(text)
    assert r_kw.emotion in ALL_15 and 0.0 <= r_kw.score <= 1.0
    r_cls = await cls.detect(text)
    assert r_cls.emotion in ALL_15 and 0.0 <= r_cls.score <= 1.0


# ───────────────────────── C3 LLM 输出解析畸形 ─────────────────────────
@pytest.mark.parametrize(
    "raw_output,expect_emotion",
    [
        ("纯文本不是 JSON", "neutral"),                      # 纯文本非 JSON
        ("[1, 2, 3]", "neutral"),                            # JSON 数组
        ('{"emotion": "banana", "score": 0.9}', "neutral"),  # emotion 非法 → neutral
        ('{"emotion": "HAPPY", "score": 0.9}', "happy"),     # 大写 emotion
        ('{"emotion": "joy", "score": 0.9}', "happy"),       # 别名 emotion
        ('{"emotion": "happy", "score": 5}', "happy"),       # score 越界 >1 → 钳制 1.0（≥阈值采纳）
        ('{"emotion": "happy", "score": -2}', "neutral"),    # score 越界 <0 → 钳制 0 → 低置信下沉
        ('{"emotion": "happy", "score": "abc"}', "neutral"), # score 非数字 → 0 → 低置信下沉
        ('{"emotion": "happy", "score": "0.8"}', "happy"),   # score 数字字符串 → 0.8（≥阈值采纳）
        ('{"emotion": "happy", "score": null}', "neutral"),  # score null → 0 → 低置信下沉
        ("{'emotion': 'happy', 'score': 0.8}", "neutral"),   # 单引号 JSON → 解析失败
    ],
)
async def test_c3_malformed_llm_output(raw_output, expect_emotion):
    d = LLMEmotionDetector(llm=_JsonLLM(raw_output), enabled=True)
    r = await d.detect("随便")
    assert r.emotion == expect_emotion
    assert 0.0 <= r.score <= 1.0, f"score 违反 [0,1] 契约: {r.score}"
    assert r.emotion in ALL_15


async def test_c3_score_string_with_regex_fallback():
    """正则兜底路径：score 抽到即钳制 [0,1]。"""
    d = LLMEmotionDetector(
        llm=_JsonLLM('garbage {"emotion": "sad", "score": 9.9} trailing'), enabled=True
    )
    r = await d.detect("难过")
    assert r.emotion == "sad"
    assert r.score == 1.0  # 9.9 钳制到 1.0
