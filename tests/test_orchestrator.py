"""编排层（应用用例）测试。"""
import asyncio
import tempfile
from pathlib import Path

import pytest

from roleplay.core.emotion.detector import KeywordEmotionDetector
from roleplay.core.emotion.mapping import Live2DEmotionMapper
from roleplay.core.knowledge.embedder import HashingEmbedder
from roleplay.core.knowledge.profile import UserProfile
from roleplay.core.knowledge.profile_models import ProfileEntry
from roleplay.core.knowledge.vector_store import KnowledgeBase
from roleplay.core.llm.mock import MockLLMProvider
from roleplay.core.orchestrator import ChatOrchestrator
from roleplay.core.persona_prompt import build_profile_context
from roleplay.core.rag.base import RetrievedChunk
from roleplay.core.rag.memory import InMemoryVectorStore
from roleplay.core.session_memory import SessionMemory
from roleplay.models.chat import ChatRequest


async def test_run_detects_emotion():
    orch = ChatOrchestrator(
        llm=MockLLMProvider(),
        emotion=KeywordEmotionDetector(),
        rag=InMemoryVectorStore(),
    )
    res = await orch.run(ChatRequest(session_id="s", message="我很难过"))
    assert res.response.reply
    assert res.response.emotion.emotion == "sad"


async def test_run_injects_rag_context():
    orch = ChatOrchestrator(
        llm=MockLLMProvider(),
        emotion=KeywordEmotionDetector(),
        rag=InMemoryVectorStore(),
    )
    orch._rag.add(["专属知识：无名者害怕打雷。"])
    res = await orch.run(ChatRequest(session_id="s", message="打雷"))
    assert "无名者害怕打雷" in res.response.reply or "打雷" in res.response.reply


async def test_run_with_live2d_mapper():
    orch = ChatOrchestrator(
        llm=MockLLMProvider(),
        emotion=KeywordEmotionDetector(),
        rag=InMemoryVectorStore(),
        mapper=Live2DEmotionMapper(),
        model_id="wmz_314701",
    )
    res = await orch.run(ChatRequest(session_id="s", message="我好伤心"))
    assert res.live2d is not None
    assert res.live2d["expression"] == "e_nanguo"
    assert res.live2d["model_id"] == "wmz_314701"


async def test_run_low_score_no_live2d():
    orch = ChatOrchestrator(
        llm=MockLLMProvider(),
        emotion=KeywordEmotionDetector(enabled=False),  # 关闭情感 → neutral/0
        rag=InMemoryVectorStore(),
        mapper=Live2DEmotionMapper(),
    )
    res = await orch.run(ChatRequest(session_id="s", message="随便说点"))
    # 情感关闭时 score=0 < 阈值，不切换表情
    assert res.response.emotion.emotion == "neutral"
    assert res.live2d is None


async def test_run_new_emotion_love_detected():
    orch = ChatOrchestrator(
        llm=MockLLMProvider(),
        emotion=KeywordEmotionDetector(),
        rag=InMemoryVectorStore(),
    )
    res = await orch.run(ChatRequest(session_id="s", message="我爱你"))
    assert res.response.emotion.emotion == "love"


# ───────────────────────── 用户画像：注入 / 提取调度 / clear ─────────────────────────
def _profile_orchestrator(tmp_path, *, extract_every=2, top_k=3, enable=True):
    kb = KnowledgeBase(HashingEmbedder(dim=64), persist_dir=Path(tmp_path) / "kb")
    up = UserProfile(kb, namespace="profile", synonym_threshold=0.85)
    sm = SessionMemory(persist_dir=Path(tmp_path) / "sessions")
    orch = ChatOrchestrator(
        llm=MockLLMProvider(),
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


async def test_prepare_injects_profile_context():
    """_prepare 返回的 system prompt 含「【用户资料】」块，且 ≤ top_k 条。"""
    import tempfile

    with tempfile.TemporaryDirectory() as td:
        orch, up = _profile_orchestrator(td, top_k=3)
        await up.upsert(
            [
                ProfileEntry(type="preference", key="咖啡", value="喜欢喝拿铁", importance=0.9, confidence=0.9),
                ProfileEntry(type="habit", key="早起", value="每天6点起", importance=0.8, confidence=0.8),
                ProfileEntry(type="fact", key="猫", value="养了一只猫", importance=0.7, confidence=0.7),
                ProfileEntry(type="fact", key="狗", value="也养了一只狗", importance=0.6, confidence=0.6),
            ]
        )
        system_prompt, _, _ = await orch._prepare(
            ChatRequest(session_id="s", message="我喜欢喝咖啡")
        )
        assert "【用户资料】" in system_prompt
        # 块内条目行数 ≤ top_k=3（检索排序后截断）
        block = system_prompt.split("【用户资料】")[1].split("【角色资料库")[0]
        item_lines = [ln for ln in block.splitlines() if ln.startswith("- (")]
        assert len(item_lines) <= 3
        assert any("咖啡" in ln for ln in item_lines)


async def test_prepare_no_profile_block_when_empty():
    """画像为空时 system prompt 不含「【用户资料】」块。"""
    import tempfile

    with tempfile.TemporaryDirectory() as td:
        orch, _ = _profile_orchestrator(td)
        system_prompt, _, _ = await orch._prepare(
            ChatRequest(session_id="s", message="你好")
        )
        assert "【用户资料】" not in system_prompt


async def test_prepare_injects_reminder():
    """important_date ±3 天内 → 提醒行置顶注入。"""
    import tempfile
    from datetime import date, timedelta

    with tempfile.TemporaryDirectory() as td:
        orch, up = _profile_orchestrator(td)
        today = date.today()
        d = today + timedelta(days=1)
        await up.upsert(
            [ProfileEntry(type="important_date", key="生日", value=f"{d.month}月{d.day}日", importance=0.7)]
        )
        system_prompt, _, _ = await orch._prepare(
            ChatRequest(session_id="s", message="你好")
        )
        assert "【用户资料】" in system_prompt
        assert "生日" in system_prompt


async def test_persist_extracts_every_n_rounds():
    """聊满 profile_extract_every 轮后，画像命名空间有新增条目。"""
    import tempfile

    with tempfile.TemporaryDirectory() as td:
        orch, up = _profile_orchestrator(td, extract_every=2)
        # 第 1 轮：不提取
        await orch.run(ChatRequest(session_id="s1", message="我喜欢咖啡"))
        assert up.count() == 0
        # 第 2 轮：提取
        await orch.run(ChatRequest(session_id="s1", message="我习惯早起"))
        assert up.count() >= 1
        types = {e.type for e in up.list_entries()}
        assert "preference" in types or "habit" in types


async def test_persist_cursor_not_re_extract():
    """游标推进：同轮次不会重复提取（clear 后才重新计数）。"""
    import tempfile

    with tempfile.TemporaryDirectory() as td:
        orch, up = _profile_orchestrator(td, extract_every=2)
        await orch.run(ChatRequest(session_id="s2", message="我喜欢咖啡"))
        await orch.run(ChatRequest(session_id="s2", message="我习惯早起"))
        n_after_2 = up.count()
        # 第 3 轮：不是提取点，不新增
        await orch.run(ChatRequest(session_id="s2", message="随便聊聊"))
        assert up.count() == n_after_2
        # clear 后游标重置
        orch.clear_session("s2")
        assert "s2" not in orch._profile_cursor
        assert "s2" not in orch._turn_counts


async def test_profile_disabled_no_extract():
    import tempfile

    with tempfile.TemporaryDirectory() as td:
        orch, up = _profile_orchestrator(td, extract_every=1, enable=False)
        await orch.run(ChatRequest(session_id="s3", message="我喜欢咖啡"))
        assert up.count() == 0


# ───────────────────────── build_profile_context 纯函数 ─────────────────────────
def test_build_profile_context_format():
    chunks = [
        RetrievedChunk(
            text="（偏好）咖啡：喜欢喝拿铁",
            score=0.9,
            metadata={"namespace": "profile", "type": "preference"},
        )
    ]
    ctx = build_profile_context(chunks)
    assert "【用户资料】" in ctx
    assert "（偏好）咖啡：喜欢喝拿铁" in ctx
    assert "用户资料" in ctx


def test_build_profile_context_empty_returns_empty():
    assert build_profile_context([]) == ""
    low = [
        RetrievedChunk(text="低分噪声", score=0.01, metadata={"namespace": "profile"})
    ]
    assert build_profile_context(low) == ""  # 低于 MIN_CONTEXT_SCORE 过滤


def test_build_roleplay_prompt_orders_blocks():
    """块顺序：人设 → 语气 → 【用户资料】→ 【角色资料库】。"""
    from roleplay.core.persona_prompt import build_roleplay_prompt

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
    assert "【用户资料】" in prompt
    assert "【角色资料库" in prompt
    assert prompt.index("【用户资料】") < prompt.index("【角色资料库")
