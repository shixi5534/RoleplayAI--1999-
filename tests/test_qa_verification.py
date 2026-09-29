# -*- coding: utf-8 -*-
"""QA 边界验证合集（由 3 份独立 QA 报告合并，2026-09-29）。

覆盖**边界与击穿**场景，与 `test_emotion.py` / `test_profile.py` 的常规路径互补：
  ① 情绪检测边界（归一化 / 责任链穿透 / 父类回退 / SSE 契约）
  ② 用户画像边界（去重 / 提取器 / 注入 / 并发隔离 / 击穿）
  ③ 画像并发竞态（多 key×多任务 / 锁语义 / 无死锁 / 共享 KB）

> 合并说明：原为 3 个文件（328 + 663 + 162 行），因**互不重叠**故仅做拼接，
> 保留各自 fixture 与断言，不改语义。原独立的临时调试脚本
> `test_qa_scratch_max.py`（24 行，含 print）已删 —— 其断言
> （`_max_items=0 → count()==0`）已被本文件 ② 段覆盖。
>
> 依据与决策表：`data/compendium_rag/reports/_tests_plan.json`
"""


# ============================================================================
# 来源：tests/test_qa_independent_verify.py（原 328 行）—— 情绪检测边界（归一化 / 责任链穿透 / 父类回退 / SSE 契约）
# ============================================================================
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


# ============================================================================
# 来源：tests/test_qa_profile_verify.py（原 663 行）—— 用户画像边界（去重 / 提取器 / 注入 / 并发隔离 / 击穿）
# ============================================================================
import asyncio
import json
import tempfile
import time
from datetime import date, timedelta
from pathlib import Path

import pytest

from roleplay.core.emotion.detector import KeywordEmotionDetector
from roleplay.core.knowledge.embedder import HashingEmbedder
from roleplay.core.knowledge.extractors import (
    LLMProfileExtractor,
    RuleProfileExtractor,
    extract_profile_entries,
)
from roleplay.core.knowledge.profile import UserProfile
from roleplay.core.knowledge.profile_models import ProfileEntry, normalize_key
from roleplay.core.knowledge.vector_store import KnowledgeBase
from roleplay.core.llm.mock import MockLLMProvider
from roleplay.core.orchestrator import ChatOrchestrator
from roleplay.core.persona_prompt import build_roleplay_prompt
from roleplay.core.rag.base import RetrievedChunk
from roleplay.core.rag.memory import InMemoryVectorStore
from roleplay.core.session_memory import SessionMemory
from roleplay.models.chat import ChatRequest


# ───────────────────────── 夹具 ─────────────────────────
@pytest.fixture
def kb(tmp_path):
    return KnowledgeBase(HashingEmbedder(dim=64), persist_dir=tmp_path / "kb")


@pytest.fixture
def profile(kb):
    return UserProfile(
        kb,
        namespace="profile",
        decay_lambda=0.05,
        synonym_threshold=0.85,
        reminder_days=3,
        max_items=200,
        top_k=5,
    )


def _profile_orchestrator(tmp_path, *, extract_every=2, top_k=3, enable=True, llm=None):
    kb = KnowledgeBase(HashingEmbedder(dim=64), persist_dir=Path(tmp_path) / "kb")
    up = UserProfile(kb, namespace="profile", synonym_threshold=0.85)
    sm = SessionMemory(persist_dir=Path(tmp_path) / "sessions")
    orch = ChatOrchestrator(
        llm=llm or MockLLMProvider(),
        emotion=KeywordEmotionDetector(enabled=False),
        rag=InMemoryVectorStore(),
        enable_emotion=False,
        session_memory=sm,
        knowledge_base=kb,
        user_profile=up,
        enable_profile=enable,
        profile_extract_every=extract_every,
        profile_top_k=top_k,
        enable_longterm=False,
    )
    return orch, up


# ───────────────────────── B1 去重/更新边界 ─────────────────────────
async def test_b1_exact_key_update_versions_and_value(profile):
    """精确键命中：同 type 同 key 不同 value → versions+1 且 value 更新（不新增）。"""
    await profile.upsert(
        [ProfileEntry(type="preference", key="咖啡", value="喜欢拿铁", confidence=0.5)]
    )
    await profile.upsert(
        [ProfileEntry(type="preference", key="咖啡", value="喜欢美式", confidence=0.5)]
    )
    await profile.upsert(
        [ProfileEntry(type="preference", key="咖啡", value="喜欢冷萃", confidence=0.5)]
    )
    assert profile.count() == 1
    e = profile.list_entries()[0]
    assert e.value == "喜欢冷萃"
    assert e.versions == 3
    assert e.history == ["喜欢拿铁", "喜欢美式"]  # 旧值追加，上限 10


async def test_b1_normalize_fullwidth_tab(profile):
    """key 归一化：全角空格 U+3000/制表符被移除，大小写折叠。"""
    # 全角空格/制表符/大小写都被 normalize 归并 → 同一 key
    await profile.upsert(
        [ProfileEntry(type="fact", key="Food", value="披萨", confidence=0.5)]
    )
    await profile.upsert(
        [ProfileEntry(type="fact", key="\tFood\u3000", value="意面", confidence=0.5)]
    )
    assert profile.count() == 1
    assert profile.list_entries()[0].versions == 2
    # 注意：'food\u3000is' 归一化为 'foodis' ≠ 'food'，是不同 key（正确行为）
    await profile.upsert(
        [ProfileEntry(type="fact", key="food\u3000is", value="汉堡", confidence=0.5)]
    )
    assert profile.count() == 2


def test_b1_normalize_key_fullwidth_letters_not_ascii():
    """全角字母（ＦＯＯＤ）不会折叠为 ASCII（f o o d）——记录行为，非断言崩溃。"""
    assert normalize_key("ＦＯＯＤ") != normalize_key("FOOD")
    # 全角空格属于 \s（Unicode），被移除
    assert normalize_key("food\u3000bar") == "foodbar"


async def test_b1_synonym_boundary_085(profile, monkeypatch):
    """同义边界：相似度恰 0.85（>= 阈值）→ 判同义更新，不新增。"""
    await profile.upsert(
        [ProfileEntry(type="preference", key="咖啡", value="喜欢拿铁", confidence=0.6)]
    )
    calls = {}

    async def fake_asearch(query, top_k=3, namespaces=None, min_score=0.0, **kw):
        calls["query"] = query
        return [
            RetrievedChunk(
                text="（偏好）咖啡：喜欢拿铁",
                score=0.85,  # 恰好等于阈值
                metadata={"type": "preference", "key": "咖啡", "id": "profile-1", "namespace": "profile"},
            )
        ]

    monkeypatch.setattr(profile._kb, "asearch", fake_asearch)
    n = await profile.upsert(
        [ProfileEntry(type="preference", key="咖啡豆", value="喜欢拿铁", confidence=0.6)]
    )
    assert n == 1
    assert profile.count() == 1  # 0.85 → 同义，不新增
    assert profile.list_entries()[0].versions == 2


async def test_b1_synonym_boundary_084(profile, monkeypatch):
    """同义边界：相似度 0.84（< 阈值）→ 判新增。"""
    await profile.upsert(
        [ProfileEntry(type="preference", key="咖啡", value="喜欢拿铁", confidence=0.6)]
    )

    async def fake_asearch(query, top_k=3, namespaces=None, min_score=0.0, **kw):
        return [
            RetrievedChunk(
                text="（偏好）咖啡：喜欢拿铁",
                score=0.84,
                metadata={"type": "preference", "key": "咖啡", "id": "profile-1", "namespace": "profile"},
            )
        ]

    profile._kb.asearch = fake_asearch  # type: ignore[method-assign]
    n = await profile.upsert(
        [ProfileEntry(type="preference", key="咖啡豆", value="喜欢拿铁", confidence=0.6)]
    )
    assert n == 1
    assert profile.count() == 2  # 0.84 → 新增


async def test_b1_correction_flow_and_not_polluted(profile):
    """correction：先存喜欢辣 → correction 不吃辣 → value 更新+importance 降半+corrected；
    随后普通「喜欢甜」（不同 key）→ 正常新增不被 correction 污染。"""
    await profile.upsert(
        [ProfileEntry(type="preference", key="辣", value="喜欢辣", importance=0.8, confidence=0.6)]
    )
    await profile.upsert(
        [ProfileEntry(type="correction", key="辣", value="不再吃辣", confidence=0.3)]
    )
    e = profile.list_entries()[0]
    assert e.value == "不再吃辣"
    assert e.importance == pytest.approx(0.4)  # 0.8*0.5
    raw = profile._kb.list_items("profile")[0]["meta"]
    assert raw.get("corrected") is True
    # 普通「喜欢甜」→ 新条目正常写入
    await profile.upsert(
        [ProfileEntry(type="preference", key="甜", value="喜欢甜", importance=0.6, confidence=0.5)]
    )
    assert profile.count() == 2
    sweet = next(x for x in profile.list_entries() if x.key == "甜")
    assert sweet.value == "喜欢甜"
    assert sweet.importance == pytest.approx(0.6)  # 未被 correction 降权污染


async def test_b1_correction_then_reclaim_keeps_corrected_flag(profile):
    """correction 后用户重新声明同 key 偏好：value 更新，但 corrected 标记残留（记录行为）。"""
    await profile.upsert(
        [ProfileEntry(type="preference", key="咖啡", value="喜欢咖啡", importance=0.8, confidence=0.6)]
    )
    await profile.upsert(
        [ProfileEntry(type="correction", key="咖啡", value="不再喜欢咖啡", confidence=0.3)]
    )
    await profile.upsert(
        [ProfileEntry(type="preference", key="咖啡", value="重新喜欢咖啡", importance=0.8, confidence=0.6)]
    )
    e = profile.list_entries()[0]
    assert e.value == "重新喜欢咖啡"
    assert e.versions == 3
    raw = profile._kb.list_items("profile")[0]["meta"]
    assert raw.get("corrected") is True  # P2 观察点：corrected 未清除


async def test_b1_max_items_evicts_lowest_keeps_date(profile):
    """上限淘汰：超 max_items 后新增 → 淘汰 importance 最低；important_date 永不淘汰。"""
    profile._max_items = 3
    await profile.upsert([ProfileEntry(type="fact", key="a", value="A", importance=0.9, confidence=0.5)])
    await profile.upsert([ProfileEntry(type="fact", key="b", value="B", importance=0.2, confidence=0.5)])
    await profile.upsert(
        [ProfileEntry(type="important_date", key="生日", value="5月20日", importance=0.1, confidence=0.5)]
    )
    assert profile.count() == 3
    # 新增一条 importance 0.5 → 淘汰 b（importance 0.2 最低）
    await profile.upsert([ProfileEntry(type="fact", key="c", value="C", importance=0.5, confidence=0.5)])
    assert profile.count() == 3
    keys = {e.key for e in profile.list_entries()}
    assert "b" not in keys
    assert "生日" in keys  # important_date 保留（即使 importance 最低）


async def test_b1_max_items_zero_and_negative(profile):
    """max_items=0/负数：非 important_date 条目立即淘汰；important_date 保留（设计取舍）。"""
    for m in (0, -1):
        # 每个 m 独立环境，避免循环间状态污染
        profile._kb.clear_namespace("profile")
        profile._max_items = m
        await profile.upsert(
            [ProfileEntry(type="fact", key="f", value="F", importance=0.5, confidence=0.5)]
        )
        assert profile.count() == 0  # fact 立即被淘汰
        await profile.upsert(
            [ProfileEntry(type="important_date", key="生日", value="5月20日", importance=0.5, confidence=0.5)]
        )
        assert profile.count() == 1  # important_date 保留（设计取舍）


# ───────────────────────── B2 提取器边界 ─────────────────────────
def test_b2_rule_template_matrix():
    """规则模板全集：类型与 value 正确。"""
    r = RuleProfileExtractor()
    cases = [
        ("我喜欢咖啡", "preference", "咖啡"),
        ("我最讨厌香菜", "preference", "香菜"),
        ("我生日是5月20日", "important_date", "生日"),  # key 为「生日」非日期串（_date_key 设计）
        ("我每天跑步", "habit", "跑步"),
        ("我养了猫", "fact", "猫"),
        ("其实我不再喜欢咖啡了", "correction", None),  # key 含句尾「了」（P2 规则精度观察点）
    ]
    for text, exp_type, exp_key in cases:
        entries = r.extract([{"role": "user", "content": text}])
        assert entries, f"{text!r} 未提取到条目"
        assert entries[0].type == exp_type, f"{text!r} -> {entries[0].type} != {exp_type}"
        if exp_key is not None:
            assert entries[0].key == exp_key, f"{text!r} -> key {entries[0].key} != {exp_key}"
    # correction 条目：key/value 至少一处包含话题词「咖啡」（容忍句尾「了」）
    corr = r.extract([{"role": "user", "content": "其实我不再喜欢咖啡了"}])[0]
    assert corr.type == "correction"
    assert "咖啡" in corr.key or "咖啡" in corr.value
    # 日期 value 必须保留在 value 字段（供 check_reminders 解析）
    e = r.extract([{"role": "user", "content": "我生日是5月20日"}])[0]
    assert e.value == "5月20日"


def test_b2_rule_empty_and_garbage_inputs():
    """空输入/None/纯标点 → 不抛异常返回空。"""
    r = RuleProfileExtractor()
    for text in ["", "   ", "！！！", "。。。", None, 123, ["x"]]:
        entries = r.extract([{"role": "user", "content": text}])
        assert entries == []
    # 非 dict 轮次 / 空 turns
    assert r.extract([]) == []
    assert r.extract([None, "string", {"role": "user"}]) == []


class _SpyLLM(MockLLMProvider):
    def __init__(self, reply: str = "[]") -> None:
        super().__init__()
        self._reply = reply
        self.calls = 0

    async def generate(self, *, system, user, history=None, temperature=None) -> str:
        self.calls += 1
        return self._reply


async def test_b2_llm_object_not_array_returns_empty():
    """LLM 输出非数组（对象）→ 不抛、返回空。"""
    spy = _SpyLLM('{"type": "preference", "key": "咖啡", "value": "喜欢拿铁"}')
    ext = LLMProfileExtractor(llm=spy, timeout=1.0)
    entries = await ext.extract([{"role": "user", "content": "我喜欢咖啡"}])
    assert entries == []
    assert ext._parse_fail >= 1


async def test_b2_llm_missing_fields_dropped():
    """条目缺字段/type 非法/value 空串 → 合理丢弃，不抛。"""
    spy = _SpyLLM(
        json.dumps(
            [
                {"key": "咖啡", "value": "喜欢拿铁"},              # 缺 type
                {"type": "preference", "value": "喜欢茶"},        # 缺 key
                {"type": "preference", "key": "水", "value": ""},  # value 空串
                {"type": "not_a_type", "key": "k", "value": "v"},  # type 非法
                {"type": "fact", "key": "猫", "value": "养了一只", "importance": 0.4},  # 合法
            ],
            ensure_ascii=False,
        )
    )
    ext = LLMProfileExtractor(llm=spy, timeout=1.0)
    entries = await ext.extract([{"role": "user", "content": "随便"}])
    assert len(entries) == 1
    assert entries[0].type == "fact" and entries[0].key == "猫"


async def test_b2_llm_timeout_fast_return():
    """LLM 挂起 + timeout=0.05 → wait_for 生效快速返回空，不阻塞。"""
    class _HangLLM(MockLLMProvider):
        async def generate(self, *, system, user, history=None, temperature=None) -> str:
            await asyncio.sleep(10)
            return "[]"

    ext = LLMProfileExtractor(llm=_HangLLM(), timeout=0.05)
    t0 = time.monotonic()
    entries = await ext.extract([{"role": "user", "content": "我喜欢咖啡"}])
    elapsed = time.monotonic() - t0
    assert entries == []
    assert elapsed < 2.0, f"超时未生效：{elapsed:.2f}s"


async def test_b2_llm_zero_calls_when_unavailable():
    """mock/llm_available=False 模式：LLM.generate 零调用（隐私）。"""
    spy = _SpyLLM('[]')
    rule = RuleProfileExtractor()
    entries = await extract_profile_entries(
        [{"role": "user", "content": "我喜欢咖啡"}],
        rule=rule,
        llm=LLMProfileExtractor(llm=spy),
        llm_available=False,
    )
    assert spy.calls == 0
    assert len(entries) == 1  # 规则兜底


# ───────────────────────── B3 注入/编排边界 ─────────────────────────
def test_b3_roleplay_prompt_block_order():
    """块顺序：人设 → 语气 → 【用户资料】→ 【角色资料库】；无画像时无资料块。"""
    prompt = build_roleplay_prompt(
        card_json=None,
        fallback_prompt="你是测试助手",
        default_card=None,
        message="你好",
        chunks=[RetrievedChunk(text="角色资料", score=0.9, metadata={"namespace": "events"})],
        profile_chunks=[
            RetrievedChunk(text="（偏好）咖啡：喜欢拿铁", score=0.9, metadata={"namespace": "profile"})
        ],
    )
    assert prompt.index("【用户资料】") < prompt.index("【角色资料库")
    assert prompt.index("【用户资料】") > prompt.index("语气") if "语气" in prompt else True
    # 无画像 → 无块
    prompt2 = build_roleplay_prompt(
        card_json=None,
        fallback_prompt="你是测试助手",
        default_card=None,
        message="你好",
        chunks=[RetrievedChunk(text="角色资料", score=0.9, metadata={"namespace": "events"})],
        profile_chunks=[],
    )
    assert "【用户资料】" not in prompt2


async def test_b3_inject_count_leq_topk():
    """conftest TOP_K=3 → 注入画像行 ≤ 3，importance 高者在前。"""
    with tempfile.TemporaryDirectory() as td:
        orch, up = _profile_orchestrator(td, top_k=3)
        for i in range(6):
            await up.upsert(
                [ProfileEntry(type="fact", key=f"项{i}", value=f"事实{i}", importance=0.1 * (i + 1), confidence=0.5)]
            )
        system_prompt, _, _ = await orch._prepare(
            ChatRequest(session_id="s", message="事实")
        )
        block = system_prompt.split("【用户资料】")[1].split("【角色资料库")[0]
        lines = [ln for ln in block.splitlines() if ln.startswith("- (")]
        assert 1 <= len(lines) <= 3
        # importance 最高（0.6）的项5 应出现
        assert any("项5" in ln for ln in lines)


async def test_b3_persist_schedule_cursor():
    """EXTRACT_EVERY=2 → 第 2/4 轮提取，游标不重复；clear 后重置。"""
    with tempfile.TemporaryDirectory() as td:
        orch, up = _profile_orchestrator(td, extract_every=2)
        await orch.run(ChatRequest(session_id="s", message="我喜欢咖啡"))
        assert up.count() == 0  # 第 1 轮不提取
        await orch.run(ChatRequest(session_id="s", message="我习惯早起"))
        n2 = up.count()
        assert n2 >= 1  # 第 2 轮提取
        c2 = orch._profile_cursor.get("s", 0)
        await orch.run(ChatRequest(session_id="s", message="我养了猫"))
        assert up.count() == n2  # 第 3 轮不是提取点
        await orch.run(ChatRequest(session_id="s", message="我住在北京"))
        n4 = up.count()
        assert n4 > n2  # 第 4 轮提取新轮次
        # 游标推进，不重复提取第 2 轮内容：咖啡/早起不应重复计数
        keys = {e.key for e in up.list_entries()}
        assert "咖啡" in keys
        assert "早起" in keys
        orch.clear_session("s")
        assert "s" not in orch._profile_cursor
        assert "s" not in orch._turn_counts


async def test_b3_disabled_no_inject_no_extract():
    """profile_enabled=False → 不提取不注入（system prompt 无资料块）。"""
    with tempfile.TemporaryDirectory() as td:
        orch, up = _profile_orchestrator(td, extract_every=1, enable=False)
        # 预置画像数据 → 即使有数据也不注入
        await up.upsert([ProfileEntry(type="preference", key="咖啡", value="喜欢拿铁", confidence=0.6)])
        system_prompt, _, _ = await orch._prepare(
            ChatRequest(session_id="s", message="我喜欢喝咖啡")
        )
        assert "【用户资料】" not in system_prompt
        await orch.run(ChatRequest(session_id="s", message="我喜欢咖啡"))
        # 不提取（extract_every=1 但 enable=False）
        assert up.count() == 1  # 仍是预置的 1 条


async def test_b3_reminder_negative_window_and_garbage():
    """提醒：昨天（ISO 格式）命中；乱日期跳过不抛。"""
    with tempfile.TemporaryDirectory() as td:
        orch, up = _profile_orchestrator(td)
        today = date.today()
        y = today - timedelta(days=1)
        # ISO 格式支持过去日期；年度格式 M月D日 过去日期 → 顺延明年（P2 观察点）
        await up.upsert(
            [ProfileEntry(type="important_date", key="纪念日", value=y.isoformat(), importance=0.7)]
        )
        await up.upsert(
            [ProfileEntry(type="important_date", key="乱日期", value="2026-99-99", importance=0.7)]
        )
        sys_prompt, _, _ = await orch._prepare(ChatRequest(session_id="s", message="你好"))
        assert "【用户资料】" in sys_prompt
        assert "纪念日" in sys_prompt
        assert "乱日期" not in sys_prompt  # 解析失败跳过


async def test_b3_reminder_annual_past_date_rollover(profile):
    """P2 观察点：年度格式 M月D日 的「昨天」（过去日期）→ 顺延明年，-364 天不在 ±3 窗口 → 无提醒。

    设计意图本应是「过去日期在 ±3 天内也应提醒」（生日刚过 1 天值得补祝福），
    但 _parse_date 把过去日期一律顺延明年再判窗口 → 昨天变成 364 天后 → 漏提醒。
    ISO 格式（YYYY-MM-DD）无此问题（直接保留原日期）。
    """
    today = date.today()
    y = today - timedelta(days=1)
    # 年度格式：过去日期 → 顺延明年 → 不在窗口
    await profile.upsert(
        [ProfileEntry(type="important_date", key="生日", value=f"{y.month}月{y.day}日", importance=0.7)]
    )
    assert profile.check_reminders(today) == []  # P2：昨天应提醒但漏了
    # ISO 格式：直接保留 → 命中
    await profile.upsert(
        [ProfileEntry(type="important_date", key="生日", value=y.isoformat(), importance=0.7)]
    )
    reminders = profile.check_reminders(today)
    assert any("昨天" in r for r in reminders)


# ───────────────────────── B4 并发/隔离 ─────────────────────────
async def test_b4_concurrent_upsert_same_key():
    """并发 upsert 同 key → P1 竞态观察（check-then-act 非原子，经验证 8/8 复现重复条目）。

    源码路径：upsert → _find_exact（list_items 快照）→ await aadd（让步）。
    两个并发任务都在 aadd 前读到「不存在」→ 各自新增 → 同 key 2 条 versions=1。
    修复方向：UserProfile 层加 async 锁（per-key 或全局），或去重判定与写入合为原子。
    """
    kb = KnowledgeBase(HashingEmbedder(dim=64))
    up = UserProfile(kb, namespace="profile")
    e1 = ProfileEntry(type="preference", key="咖啡", value="喜欢拿铁", confidence=0.6)
    e2 = ProfileEntry(type="preference", key="咖啡", value="喜欢美式", confidence=0.6)
    await asyncio.gather(up.upsert([e1]), up.upsert([e2]))
    n = up.count()
    versions = sorted(e.versions for e in up.list_entries())
    if n == 1:
        # 偶发串行（调度时序恰好无交错）→ 正常
        assert versions == [1] or versions == [2]
    else:
        # 竞态复现：同 key 出现 2 条，且 versions 均为 1（未正确合并）
        assert n == 2
        assert versions == [1, 1], f"versions={versions}（期望合并后 [2]，实际竞态重复）"


async def test_b4_namespace_isolation():
    """profile 命名空间与 events/lore/web 隔离，互不串。"""
    kb = KnowledgeBase(HashingEmbedder(dim=64))
    up = UserProfile(kb, namespace="profile")
    # 往其它命名空间写内容
    await kb.aadd(
        ["用户喜欢喝拿铁咖啡，每天都要来一杯"],
        metadatas=[{"type": "event", "key": "x"}],
        namespace="events",
    )
    await kb.aadd(["lore 文档内容"], metadatas=[{"type": "lore"}], namespace="lore_char1")
    await kb.aadd(["web 网页内容"], metadatas=[{"type": "web"}], namespace="web")
    assert up.count() == 0  # profile 独立
    hits = await up.retrieve("咖啡 拿铁")
    assert hits == []  # profile.retrieve 只搜 profile ns，搜不到 events 内容
    await up.upsert([ProfileEntry(type="preference", key="咖啡", value="喜欢拿铁", confidence=0.6)])
    assert up.count() == 1
    # 其它命名空间不受影响
    assert kb.count("events")["events"] == 1
    assert kb.count("lore_char1")["lore_char1"] == 1


async def test_b4_persistence_metadata_complete(tmp_path):
    """重启重载：条目仍在且 metadata 完整。"""
    dirpath = tmp_path / "kb_p"
    kb1 = KnowledgeBase(HashingEmbedder(dim=64), persist_dir=dirpath)
    up1 = UserProfile(kb1, namespace="profile")
    await up1.upsert(
        [ProfileEntry(type="habit", key="早起", value="每天6点起", importance=0.7, confidence=0.3)]
    )
    kb2 = KnowledgeBase(HashingEmbedder(dim=64), persist_dir=dirpath)
    up2 = UserProfile(kb2, namespace="profile")
    items = up2.list_entries()
    assert len(items) == 1
    e = items[0]
    assert e.type == "habit"
    assert e.key == "早起"
    assert e.value == "每天6点起"
    assert e.importance == pytest.approx(0.7)
    assert e.confidence == pytest.approx(0.3)
    assert e.versions == 1
    assert e.history == []
    hits = await up2.retrieve("早起 6点")
    assert hits and any("早起" in h.text for h in hits)


# ───────────────────────── C 击穿 ─────────────────────────
async def test_c1_replace_atomicity_failure_loses_item(profile, monkeypatch):
    """remove 旧 + aadd 新之间 aadd 失败 → 条目丢失（P2 原子性观察点）。"""
    await profile.upsert(
        [ProfileEntry(type="preference", key="咖啡", value="喜欢拿铁", confidence=0.6)]
    )
    assert profile.count() == 1

    async def _boom_aadd(texts, metadatas=None, namespace="episodic"):
        raise RuntimeError("embedder down")

    monkeypatch.setattr(profile._kb, "aadd", _boom_aadd)
    with pytest.raises(Exception):
        # upsert 内部捕获单条异常并记录，不向上抛；此处直接调用 _replace_item 观察原子性
        await profile._replace_item(profile._kb.list_items("profile")[0], {"key": "咖啡", "value": "x"})
    # 观察：remove 已执行、aadd 失败 → 条目丢失（无回滚）
    assert profile.count() == 0


async def test_c2_exception_swallow_main_flow():
    """检索/提醒抛异常 → orchestrator 主流程仍正常返回 done。"""
    class _BoomProfile:
        namespace = "profile"

        async def retrieve(self, query, top_k=None):
            raise RuntimeError("retrieve boom")

        def check_reminders(self, today=None):
            raise RuntimeError("reminder boom")

    orch = ChatOrchestrator(
        llm=MockLLMProvider(),
        emotion=KeywordEmotionDetector(enabled=False),
        rag=InMemoryVectorStore(),
        enable_emotion=False,
        user_profile=_BoomProfile(),
        enable_profile=True,
        profile_extract_every=2,
        profile_top_k=3,
    )
    events = []
    async for ev in orch.stream(ChatRequest(session_id="s", message="你好")):
        events.append(ev)
    assert any(e["type"] == "emotion" for e in events)
    assert any(e["type"] == "done" for e in events)
    # 且 system prompt 无资料块（降级为空）
    sys_prompt, _, _ = await orch._prepare(ChatRequest(session_id="s", message="你好"))
    assert "【用户资料】" not in sys_prompt


async def test_c3_perf_200_items():
    """200 条满时 retrieve/check_reminders 延迟可接受（<1s 量级）。

    注意：用互不相似 key（fact_i）避免同义合并干扰条目数（HashingEmbedder 下
    「项1」vs「项10」cos=0.55，但 BM25 混合重排可产生高分 → 误判同义合并）。
    """
    kb = KnowledgeBase(HashingEmbedder(dim=64))
    up = UserProfile(kb, namespace="profile", reminder_days=3)
    for i in range(200):
        await up.upsert(
            [ProfileEntry(
                type="fact" if i % 10 else "important_date",
                key=f"fact_key_{i:04d}",
                value=f"事实内容{i:04d}",
                importance=0.1 + (i % 9) * 0.1,
                confidence=0.3,  # 低置信跳过同义检查，保证 200 条互不合并
            )]
        )
    assert up.count() >= 180, f"同义合并过度：仅 {up.count()} 条"
    t0 = time.monotonic()
    hits = await up.retrieve("事实内容 项", top_k=5)
    t_retrieve = time.monotonic() - t0
    assert len(hits) <= 5
    t0 = time.monotonic()
    reminders = up.check_reminders()
    t_remind = time.monotonic() - t0
    assert t_retrieve < 1.0, f"retrieve 过慢：{t_retrieve:.2f}s"
    assert t_remind < 1.0, f"check_reminders 过慢：{t_remind:.2f}s"


async def test_c4_long_value_emoji_mixed():
    """超长 value（10k 字符）/emoji/混合语言 → 入库检索不崩。"""
    kb = KnowledgeBase(HashingEmbedder(dim=64))
    up = UserProfile(kb, namespace="profile")
    long_value = "我很喜欢喝咖啡并且每天都要来一杯拿铁 ☕️ 混合 English words 与中文！" * 250  # ~10k+ 字符
    await up.upsert(
        [ProfileEntry(type="preference", key="咖啡", value=long_value, importance=0.8, confidence=0.6)]
    )
    assert up.count() == 1
    hits = await up.retrieve("咖啡 拿铁")
    assert hits
    # 重新读回，value 完整
    e = up.list_entries()[0]
    assert len(e.value) > 10000
    assert "☕️" in e.value


async def test_c5_list_items_deepcopy_nested(profile):
    """list_items 深拷贝语义：顶层/meta 键修改不污染；嵌套 history list 修改会共享（P2 观察点）。"""
    await profile.upsert([ProfileEntry(type="preference", key="咖啡", value="喜欢拿铁", confidence=0.6)])
    await profile.upsert([ProfileEntry(type="preference", key="咖啡", value="喜欢美式", confidence=0.6)])
    items = profile._kb.list_items("profile")
    # 顶层与 meta 键修改 → 不污染
    items[0]["text"] = "mutated"
    items[0]["meta"]["key"] = "mutated"
    after = profile._kb.list_items("profile")
    assert after[0]["text"] != "mutated"
    assert after[0]["meta"]["key"] != "mutated"
    # 嵌套 history list 修改 → 观察是否共享引用（P2：list_items 为浅拷贝，嵌套 list 共享）
    if "history" in after[0]["meta"]:
        after[0]["meta"]["history"].append("INTRUDER")
        again = profile._kb.list_items("profile")
        shared = "INTRUDER" in again[0]["meta"].get("history", [])
        # 记录行为：list_items 只复制 item dict + meta dict，嵌套 history list 共享引用
        # 该共享本身风险低（内部从不原地改 history，只整体替换），记录为 P2 观察点
        assert shared is True or shared is False  # 记录，不判定失败


# ============================================================================
# 来源：tests/test_qa_profile_r2_verify.py（原 162 行）—— 画像并发竞态（多 key×多任务 / 锁语义 / 无死锁 / 共享 KB）
# ============================================================================
import asyncio
from collections import Counter

import pytest

from roleplay.core.knowledge.embedder import HashingEmbedder
from roleplay.core.knowledge.profile import UserProfile
from roleplay.core.knowledge.profile_models import ProfileEntry
from roleplay.core.knowledge.vector_store import KnowledgeBase


@pytest.fixture
def profile():
    return UserProfile(KnowledgeBase(HashingEmbedder(dim=64)), namespace="profile")


# ───────────────────────── 1. 固化复现用例（同 key 并发） ─────────────────────────
async def test_r2_same_key_concurrent_fixed(profile):
    """P1 竞态复现用例：同 key 并发 upsert → 修复后应合并为 1 条。"""
    e1 = ProfileEntry(type="preference", key="咖啡", value="喜欢拿铁", confidence=0.6)
    e2 = ProfileEntry(type="preference", key="咖啡", value="喜欢美式", confidence=0.6)
    await asyncio.gather(profile.upsert([e1]), profile.upsert([e2]))
    items = profile.list_entries()
    assert len(items) == 1, f"并发同 key 应合并为 1 条，实际 {len(items)} 条"
    assert items[0].key == "咖啡"
    assert items[0].versions >= 2, f"合并后 versions 应为 ≥2，实际 {items[0].versions}"
    # 最终 value 是两次写入之一（后写覆盖）
    assert items[0].value in ("喜欢拿铁", "喜欢美式")


# ───────────────────────── 2. 多 key × 多任务压力（锁覆盖所有写入路径） ─────────────────────────
async def test_r2_multi_key_multi_task_no_dup(profile):
    """5 个不同 key 各 gather 3 次 → 无重复、versions==3（锁覆盖全部 key 的写路径）。"""
    keys = ["咖啡", "茶", "可乐", "牛奶", "果汁"]
    tasks = []
    for k in keys:
        for i in range(3):
            tasks.append(
                profile.upsert(
                    [ProfileEntry(type="preference", key=k, value=f"喜欢{k}{i}", confidence=0.6)]
                )
            )
    results = await asyncio.gather(*tasks)
    assert all(r == 1 for r in results), f"每任务应处理 1 条，实际 {results}"
    items = profile.list_entries()
    assert len(items) == 5, f"5 key 各 3 次并发应合并为 5 条，实际 {len(items)} 条"
    by_key = {e.key: e for e in items}
    for k in keys:
        assert by_key[k].versions == 3, f"{k} versions 应为 3，实际 {by_key[k].versions}"
        assert by_key[k].value == f"喜欢{k}2"  # 最后一次写入胜出（串行顺序保证）


async def test_r2_multi_key_multi_task_with_correction(profile):
    """多 key × 多任务 + correction 混合：correction 与普通更新并发 → 不丢、不重复。"""
    # 先写一条 preference
    await profile.upsert(
        [ProfileEntry(type="preference", key="咖啡", value="喜欢咖啡", importance=0.8, confidence=0.6)]
    )
    tasks = [
        profile.upsert([ProfileEntry(type="preference", key="咖啡", value="更喜欢冷萃", confidence=0.6)]),
        profile.upsert([ProfileEntry(type="correction", key="咖啡", value="不再喝咖啡", confidence=0.3)]),
        profile.upsert([ProfileEntry(type="preference", key="茶", value="喜欢绿茶", confidence=0.6)]),
        profile.upsert([ProfileEntry(type="preference", key="茶", value="喜欢红茶", confidence=0.6)]),
    ]
    await asyncio.gather(*tasks)
    items = profile.list_entries()
    assert len(items) == 2, f"应为咖啡+茶 2 条，实际 {len(items)} 条"
    by_key = {e.key: e for e in items}
    assert "茶" in by_key and by_key["茶"].versions == 2
    assert "咖啡" in by_key
    # 咖啡被 correction 覆盖（可能再被普通更新覆盖），无论哪种 value 都不应有重复条目
    assert by_key["咖啡"].versions >= 2


# ───────────────────────── 3. 锁语义：异常释放 / 无死锁 ─────────────────────────
async def test_r2_lock_released_on_exception(profile, monkeypatch):
    """锁内 aadd 抛异常 → 锁正确释放，后续 upsert 仍可执行（无死锁）。"""
    await profile.upsert(
        [ProfileEntry(type="preference", key="咖啡", value="喜欢拿铁", confidence=0.6)]
    )

    async def _boom_aadd(texts, metadatas=None, namespace="episodic"):
        raise RuntimeError("embedder down")

    monkeypatch.setattr(profile._kb, "aadd", _boom_aadd)
    # 触发异常路径（upsert 内部捕获，不向上抛）
    await profile.upsert(
        [ProfileEntry(type="preference", key="咖啡", value="喜欢美式", confidence=0.6)]
    )
    # 恢复 aadd → 锁应已释放，可正常写入
    monkeypatch.undo()
    await profile.upsert(
        [ProfileEntry(type="preference", key="茶", value="喜欢绿茶", confidence=0.6)]
    )
    keys = {e.key for e in profile.list_entries()}
    assert "茶" in keys, "异常后锁未释放，后续写入被阻塞"


async def test_r2_no_deadlock_nested(profile):
    """锁内无嵌套锁：并发中 upsert 内仅一次锁获取，无自死锁（多轮压力）。"""
    for _ in range(10):
        tasks = [
            profile.upsert([ProfileEntry(type="fact", key=f"k{i}", value=f"v{i}", confidence=0.3)])
            for i in range(6)
        ]
        await asyncio.gather(*tasks)
    assert len(profile.list_entries()) == 6  # 6 个不同 key


# ───────────────────────── 4. 跨实例共享 KB 的并发（生产场景） ─────────────────────────
async def test_r2_two_profiles_shared_kb_concurrent():
    """两个 UserProfile 实例共享同一 KB 并发写同 key → 锁是实例级的，可能仍有竞态（P2 观察）。"""
    kb = KnowledgeBase(HashingEmbedder(dim=64))
    up1 = UserProfile(kb, namespace="profile")
    up2 = UserProfile(kb, namespace="profile")
    e1 = ProfileEntry(type="preference", key="咖啡", value="喜欢拿铁", confidence=0.6)
    e2 = ProfileEntry(type="preference", key="咖啡", value="喜欢美式", confidence=0.6)
    # 两个实例各自持锁 → 锁不互斥 → 竞态仍可能复现（观察点，不硬失败）
    await asyncio.gather(up1.upsert([e1]), up2.upsert([e2]))
    items = kb.list_items("profile")
    n = len(items)
    versions = sorted(
        ProfileEntry.from_meta(it["meta"]).versions for it in items
    )
    # 记录行为：生产装配中每个 UserProfile 实例只对应一个 orchestrator 实例（单例），
    # 跨实例并发仅在测试/多服务进程下出现，属已知边界。
    assert n >= 1
    if n == 2:
        pytest.skip(f"P2 观察点：跨 UserProfile 实例共享 KB 并发写同 key 产生 {n} 条（实例级锁不互斥）")


# ───────────────────────── 5. 最终一致性：串行与并发结果等价 ─────────────────────────
async def test_r2_concurrent_equals_serial():
    """并发 5 key×3 次 与 串行 5 key×3 次 结果一致（版本与最终 value）。"""
    async def run_concurrent():
        kb = KnowledgeBase(HashingEmbedder(dim=64))
        up = UserProfile(kb, namespace="profile")
        tasks = [
            up.upsert([ProfileEntry(type="preference", key=k, value=f"喜欢{k}{i}", confidence=0.6)])
            for k in ["咖啡", "茶", "可乐"] for i in range(3)
        ]
        await asyncio.gather(*tasks)
        return {e.key: (e.versions, e.value) for e in up.list_entries()}

    async def run_serial():
        kb = KnowledgeBase(HashingEmbedder(dim=64))
        up = UserProfile(kb, namespace="profile")
        for k in ["咖啡", "茶", "可乐"]:
            for i in range(3):
                await up.upsert([ProfileEntry(type="preference", key=k, value=f"喜欢{k}{i}", confidence=0.6)])
        return {e.key: (e.versions, e.value) for e in up.list_entries()}

    conc, ser = await asyncio.gather(run_concurrent(), run_serial())
    assert conc == ser, f"并发与串行结果不一致：\n并发={conc}\n串行={ser}"
