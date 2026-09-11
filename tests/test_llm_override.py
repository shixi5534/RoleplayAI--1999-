"""build_llm_from_config 请求级 override 回归测试。

背景：用户反馈「配置了云端请保存，否则浏览器缓存显示错误，实际是本地模型，
但显示的是云端」。前端已修复（llm-switch.js 回填 api_key），本测试保证后端
决策逻辑不回归：

- 带 key 的 override 必须构建一次性客户端（needs_aclose=True），且 key 透传。
- 云端 override 无 key 时不得静默回退本地 ollama 兜底（api_key 必须为空，
  请求时在 ProviderError 层显式报「缺少 API Key」而非换用本地模型）。
- 本地 ollama override 无 key 时兜底 "ollama"（与全局 build_llm 一致）。
- override 全空时复用全局实例（needs_aclose=False）。
"""
import pytest

from roleplay.config import Settings
from roleplay.core.llm.factory import (
    aclose_global_llm,
    build_llm_from_config,
    reset_global_llm,
)
from roleplay.models.chat import LLMOverride


def make_settings(**kw) -> Settings:
    base = dict(
        llm_provider="ollama",
        llm_model="qwen2.5:1.5b",
        llm_api_key="",
        llm_base_url="http://localhost:11434/v1",
        max_tokens_per_reply=2000,
    )
    base.update(kw)
    return Settings(**base)


@pytest.fixture(autouse=True)
def _clean_global_llm():
    reset_global_llm()
    yield


async def test_cloud_override_with_key_builds_oneoff_client():
    """场景1: 云端 override 带 key → 构建 DeepSeek 一次性客户端，key 透传。"""
    s = make_settings()
    ov = LLMOverride(
        provider="deepseek",
        model="deepseek-chat",
        base_url="https://api.deepseek.com/v1",
        api_key="sk-test-123",
    )
    llm, needs_aclose = build_llm_from_config(s, ov)
    try:
        assert needs_aclose is True
        assert llm._model == "deepseek-chat"
        assert llm._api_key == "sk-test-123"
        assert llm._base_url == "https://api.deepseek.com/v1"
    finally:
        await llm.aclose()


async def test_cloud_override_without_key_does_not_fallback_to_global():
    """场景2: 云端 override 无 key → 不得静默回退本地（api_key 空，不留 ollama 兜底）。"""
    s = make_settings()
    ov = LLMOverride(
        provider="deepseek",
        model="deepseek-chat",
        base_url="https://api.deepseek.com/v1",
        api_key=None,
    )
    llm, needs_aclose = build_llm_from_config(s, ov)
    try:
        assert needs_aclose is True
        # 关键：provider 与全局不同且无 key → 不能带全局 ollama 的 "ollama" 兜底
        assert llm._api_key == ""
        assert llm._base_url == "https://api.deepseek.com/v1"
    finally:
        await llm.aclose()


async def test_ollama_override_without_key_same_as_global_reuses_instance():
    """场景3: 本地 ollama override 无 key 且与全局一致 → 复用全局实例（零连接池开销）。"""
    s = make_settings()
    ov = LLMOverride(
        provider="ollama",
        model="qwen2.5:1.5b",
        base_url="http://localhost:11434/v1",
        api_key=None,
    )
    global_llm, _ = build_llm_from_config(s, None)
    try:
        llm, needs_aclose = build_llm_from_config(s, ov)
        assert needs_aclose is False
        assert llm is global_llm
    finally:
        await aclose_global_llm()


async def test_ollama_override_with_different_model_builds_oneoff():
    """场景3b: 本地 ollama override 无 key 但模型与全局不同 → 构建一次性客户端。"""
    s = make_settings()
    ov = LLMOverride(
        provider="ollama",
        model="qwen2.5:7b",
        base_url="http://localhost:11434/v1",
        api_key=None,
    )
    llm, needs_aclose = build_llm_from_config(s, ov)
    try:
        assert needs_aclose is True
        assert llm._api_key == "ollama"
        assert llm._model == "qwen2.5:7b"
    finally:
        await llm.aclose()


async def test_empty_override_reuses_global_instance():
    """场景4: override 全空 → 复用全局实例，needs_aclose=False。"""
    s = make_settings()
    g1, _ = build_llm_from_config(s, None)
    g2, needs_aclose = build_llm_from_config(s, LLMOverride())
    try:
        assert g2 is g1
        assert needs_aclose is False
    finally:
        await aclose_global_llm()


async def test_cloud_override_without_key_raises_on_generate():
    """场景5: 云端 override 无 key 请求时必抛错（而非静默回退本地）。

    这是用户实测「显示云端、实际本地、官网无记录」的根因链闭环：
    前端若发出无 key 的云端 override（旧版 localStorage 残留坏配置），
    后端必须显式失败，绝不能静默用本地模型顶上——否则用户以为在云端，
    实际是本地回复，且云端官网无任何调用记录。
    """
    from roleplay.core.llm.openai_like import ProviderError

    s = make_settings()
    ov = LLMOverride(
        provider="deepseek",
        model="deepseek-chat",
        base_url="https://api.deepseek.com/v1",
        api_key=None,
    )
    llm, needs_aclose = build_llm_from_config(s, ov)
    try:
        assert needs_aclose is True
        # generate() 首行即校验 api_key，空 key 立即抛 ProviderError，绝不发网络请求
        with pytest.raises(ProviderError) as exc_info:
            await llm.generate(system="s", user="u", history=None)
        assert exc_info.value.details == {"provider": "deepseek-chat"}
    finally:
        await llm.aclose()
