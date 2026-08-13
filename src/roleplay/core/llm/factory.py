"""LLM 工厂：依据配置构建对应 Provider（工厂方法模式）。

两个入口：
- build_llm(settings)：全局默认 LLM，长生命周期，应用 lifespan 期 aclose。
- build_llm_from_config(settings, override)：请求级 override，支持前端模型切换。
  无 api_key 时复用全局实例（性能）；带 api_key 时构建一次性客户端（安全）。

性能/资源说明：
- build_llm() 对非 mock 全局实例做单例缓存（含 httpx 连接池），避免每请求新建
  AsyncClient 导致连接池/FD 泄漏；lifespan 期统一 aclose。
- build_llm_from_config() 快速路径复用该缓存实例；带 override 时才建一次性客户端。
"""
from __future__ import annotations

import logging

from ...config import Settings, get_settings
from ...errors import ConfigurationError
from ...models.chat import LLMOverride
from .base import LLMPort
from .mock import MockLLMProvider
from .openai_like import OpenAILikeProvider, _DEFAULT_BASE_URLS

logger = logging.getLogger(__name__)

# 全局 LLM 单例缓存（非 mock）：复用连接池，lifespan 期统一 aclose。
# 键为 provider，防 provider 变更后复用错实例；测试用 reset_global_llm() 清空。
_GLOBAL_LLM_CACHE: dict[str, LLMPort] = {}


def build_llm(settings: Settings | None = None) -> LLMPort:
    s = settings or get_settings()
    if s.llm_provider == "mock":
        return MockLLMProvider(model=s.llm_model)
    if s.llm_provider in ("openai", "deepseek", "ollama"):
        cached = _GLOBAL_LLM_CACHE.get(s.llm_provider)
        if cached is not None:
            return cached
        base_url = s.llm_base_url or _DEFAULT_BASE_URLS.get(s.llm_provider, "")
        api_key = s.llm_api_key
        # Ollama 的 OpenAI 兼容端点接受任意 Bearer（含 "ollama"），
        # 缺省空 key 会触发 ProviderError；此处兜底，避免 ollama + 空 key 直接 502。
        if s.llm_provider == "ollama" and not api_key:
            api_key = "ollama"
        client = OpenAILikeProvider(
            model=s.llm_model,
            api_key=api_key,
            base_url=base_url,
            max_tokens=s.max_tokens_per_reply,
        )
        _GLOBAL_LLM_CACHE[s.llm_provider] = client
        return client
    raise ConfigurationError(
        "不支持的 LLM provider", details={"provider": s.llm_provider}
    )


async def aclose_global_llm() -> None:
    """lifespan 关闭期统一释放缓存的全局 LLM 客户端（连接池）。"""
    for client in _GLOBAL_LLM_CACHE.values():
        if hasattr(client, "aclose"):
            try:
                await client.aclose()
            except Exception:  # noqa: BLE001
                logger.warning("关闭全局 LLM 客户端失败", exc_info=True)
    _GLOBAL_LLM_CACHE.clear()


def reset_global_llm() -> None:
    """测试辅助：清空全局 LLM 缓存（不关闭，仅丢弃引用）。"""
    _GLOBAL_LLM_CACHE.clear()


def build_llm_from_config(
    settings: Settings | None = None,
    override: LLMOverride | None = None,
) -> tuple[LLMPort, bool]:
    """请求级 LLM 构建（前端「模型切换」功能核心）。

    返回 ``(llm, needs_aclose)``：
    - needs_aclose=False：复用全局长生命周期实例，调用方 **无需** aclose。
    - needs_aclose=True ：一次性客户端（含 api_key），调用方 **必须** 在 finally 中 aclose。

    决策逻辑：
    1. override 为 None / 全字段缺省 → 回退全局 build_llm(settings)。
    2. override 有值但 api_key 为空 → 也走全局实例（安全：无密钥泄漏风险）。
       但若 override 指定了 provider/model/base_url 与全局不同，
       仍需构建新实例——此时用 override 值 + 全局 fallback 构建无 key 客户端，
       由调用方 aclose。
    3. override 带 api_key → 必然构建一次性客户端（不缓存密钥），调用方 aclose。

    简化策略（实际实现）：
    - override 为 None 或全字段为 None → 全局实例，needs_aclose=False。
    - 否则 → 构建新 OpenAILikeProvider，needs_aclose=True。
      （无 api_key 时 ollama 兜底 "ollama"，与 build_llm 一致。）
    """
    s = settings or get_settings()

    # 快速路径：无 override 或 override 全空 → 复用全局
    if override is None or all(
        v is None for v in (override.provider, override.model, override.base_url, override.api_key, override.timeout)
    ):
        return build_llm(s), False

    # 解析 override 各字段，缺省回退全局 settings
    provider = override.provider or s.llm_provider
    model = override.model or s.llm_model
    base_url = override.base_url or s.llm_base_url or _DEFAULT_BASE_URLS.get(provider, "")
    timeout = override.timeout or 30.0
    api_key = override.api_key

    if provider == "mock":
        # mock 无连接池，无需 aclose
        return MockLLMProvider(model=model), False

    if provider in ("openai", "deepseek", "ollama"):
        # ollama + 空 key 兜底（与 build_llm 一致）
        if provider == "ollama" and not api_key:
            api_key = "ollama"
        # override 无 api_key 时回退全局 key（provider 一致时），
        # 否则 model/base_url 变了但无 key 会必抛「缺少 LLM API Key」（与 docstring 决策矛盾）
        if not api_key and provider == s.llm_provider:
            api_key = s.llm_api_key
        client = OpenAILikeProvider(
            model=model,
            api_key=api_key or "",
            base_url=base_url,
            timeout=timeout,
            max_tokens=s.max_tokens_per_reply,
        )
        return client, True

    raise ConfigurationError(
        "不支持的 LLM provider (override)", details={"provider": provider}
    )
