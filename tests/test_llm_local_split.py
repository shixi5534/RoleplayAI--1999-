"""LLM 端点本地性检测 + 本地/非本地参数分流回归测试。

背景：项目原有采样参数（max_tokens_per_reply / llm_top_p / llm_repetition_penalty /
llm_temperature）是按**本地小显存**模型实测调出来的，不应被云端场景沿用，也不应被改动。
本测试锁定新加的「检测 + 分流」契约：

- 检测：**只有 provider=ollama 算本地**。地址在本机 ≠ 本地推理——
  本机聚合网关（如 127.0.0.1:7863）背后是云端模型、不占本地显存，算非本地。
- 分流：本地档**逐字段等于**本地适配参数；非本地档走 cloud_* 那组。
- 任何情况下本地适配参数本身不被改写。

全部为纯函数断言：不发网络请求。
"""
import pytest

from roleplay.config import Settings, is_local_llm_endpoint


# ───────────────────────── 检测逻辑 ─────────────────────────
@pytest.mark.parametrize(
    "provider,base_url,expected",
    [
        # 本地：只有 ollama
        ("ollama", "", True),
        ("ollama", "http://localhost:11434/v1", True),
        ("ollama", "http://127.0.0.1:11434/v1", True),
        ("ollama", "https://api.openai.com/v1", True),  # provider 优先
        ("OLLAMA", "", True),
        # 非本地：本机地址上的网关/代理也算非本地（关键修正）
        ("deepseek", "http://127.0.0.1:7863/v1", False),
        ("openai", "http://127.0.0.1:7863/v1", False),
        ("openai", "http://localhost:8000/v1", False),
        ("openai", "http://192.168.1.5:8000/v1", False),
        ("openai", "http://10.0.0.7/v1", False),
        # 非本地：公网 / 未填
        ("openai", "", False),
        ("deepseek", "https://api.deepseek.com/v1", False),
        ("openai", "https://api.openai.com/v1", False),
        ("openai", "https://my-gateway.example.com/v1", False),
        ("", "", False),
    ],
)
def test_is_local_llm_endpoint_matrix(provider, base_url, expected):
    assert is_local_llm_endpoint(provider, base_url) is expected


# ───────────────────────── 参数分流 ─────────────────────────
def _settings(**kw) -> Settings:
    """一套「本地适配参数」基准；用 kw 只覆盖端点相关字段。"""
    base = dict(
        llm_temperature=0.6,
        max_tokens_per_reply=240,
        llm_top_p=0.92,
        llm_repetition_penalty=1.10,
    )
    base.update(kw)
    return Settings(**base)


def test_local_profile_equals_local_adapted_values():
    """本地端点（ollama）：逐字段等于本地适配参数（一个字都不能变）。"""
    s = _settings(llm_provider="ollama", llm_model="qwen2.5:1.5b",
                  llm_base_url="http://localhost:11434/v1")
    p = s.llm_profile()
    assert p.is_local is True
    assert (p.max_tokens, p.top_p, p.repetition_penalty, p.temperature) == (240, 0.92, 1.10, 0.6)


def test_localhost_gateway_is_not_local():
    """本机地址上的聚合网关（127.0.0.1:7863）→ 非本地 → 用云端档，不再被 240 压死。"""
    s = _settings(llm_provider="openai", llm_model="cn:deepseek-v4.1-flash",
                  llm_base_url="http://127.0.0.1:7863/v1", llm_api_key="k")
    p = s.llm_profile()
    assert p.is_local is False
    assert p.max_tokens == s.cloud_max_tokens_per_reply == 2048
    assert (p.top_p, p.repetition_penalty, p.temperature) == (0.95, None, 0.8)


def test_non_local_profile_uses_cloud_values():
    """公网端点：同样走 cloud_*，repetition_penalty 默认不发送（None）。"""
    s = _settings(llm_provider="openai", llm_model="gpt-4o",
                  llm_base_url="https://api.openai.com/v1", llm_api_key="sk-x")
    p = s.llm_profile()
    assert p.is_local is False
    assert p.max_tokens == s.cloud_max_tokens_per_reply == 2048
    assert p.top_p == s.cloud_llm_top_p == 0.95
    assert p.repetition_penalty is None  # 标准 OpenAI 接口不认该字段
    assert p.temperature == s.cloud_llm_temperature == 0.8


def test_local_adapted_fields_are_never_rewritten():
    """分流不得改写本地适配参数本身（只是「不用」，不是「改掉」）。"""
    s = _settings(llm_provider="openai", llm_model="gpt-4o",
                  llm_base_url="https://api.openai.com/v1")
    assert s.max_tokens_per_reply == 240
    assert s.llm_top_p == 0.92
    assert s.llm_repetition_penalty == 1.10
    assert s.llm_temperature == 0.6
    # 非本地档生效的同时，本地档字段仍原样躺在配置里
    assert s.llm_profile().max_tokens == 2048


def test_request_level_profile_follows_overridden_provider():
    """请求级 override：按 override 的 provider 判定，而不是全局 provider。"""
    # 全局非本地，但本次请求用的是 ollama → 回落本地档
    s = _settings(llm_provider="openai", llm_model="gpt-4o",
                  llm_base_url="https://api.openai.com/v1")
    p = s.llm_profile_for("ollama", "http://localhost:11434/v1")
    assert p.is_local is True and p.max_tokens == 240
    # 反过来：全局 ollama，本次请求打到云端 → 用云端档
    s2 = _settings(llm_provider="ollama", llm_model="qwen2.5:1.5b",
                   llm_base_url="http://localhost:11434/v1")
    p2 = s2.llm_profile_for("openai", "https://api.openai.com/v1")
    assert p2.is_local is False and p2.max_tokens == 2048
    # 本机网关同样按 provider 判定：非 ollama → 云端档
    p3 = s2.llm_profile_for("openai", "http://127.0.0.1:7863/v1")
    assert p3.is_local is False and p3.max_tokens == 2048


def test_provider_only_detection_ignores_base_url():
    """检测只看 provider：base_url 怎么变都不影响结论。"""
    assert is_local_llm_endpoint("ollama", "https://anything.example.com/v1") is True
    assert is_local_llm_endpoint("openai", "http://127.0.0.1:1/v1") is False

