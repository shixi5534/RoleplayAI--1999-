"""SSRF / 路径穿越 防护单测（security_utils）。

覆盖 OWASP A10 关键控制：路径收敛到 allowlist 根、URL 正向 allowlist、
私有/保留地址拦截、禁用凭据通配。
"""
import socket

import pytest

from roleplay.core.knowledge.security_utils import (
    assert_public_url,
    is_blocked_ip,
    safe_local_path,
    safe_url,
)


def test_is_blocked_ip_ranges():
    assert is_blocked_ip("127.0.0.1")
    assert is_blocked_ip("10.0.0.5")
    assert is_blocked_ip("192.168.1.1")
    assert is_blocked_ip("172.16.0.1")
    assert is_blocked_ip("169.254.169.254")  # 云元数据
    assert is_blocked_ip("::1")
    assert not is_blocked_ip("93.184.216.34")  # 公网


def test_safe_local_path_blocks_traversal(tmp_path):
    root = tmp_path / "data"
    root.mkdir()
    secret = tmp_path / "secret" / "pass.txt"
    secret.parent.mkdir()
    # 越过 root 的相对越界
    with pytest.raises(ValueError):
        safe_local_path(root / ".." / "secret" / "pass.txt", [str(root)])
    # 绝对路径越界
    with pytest.raises(ValueError):
        safe_local_path("/etc/passwd", [str(root)])
    # 跨盘符/根外
    with pytest.raises(ValueError):
        safe_local_path(tmp_path.parent / "outside.txt", [str(root)])
    # 根内路径放行
    ok = root / "ok.txt"
    assert safe_local_path(ok, [str(root)]) == ok.resolve()


def test_safe_url_rejects_non_https():
    with pytest.raises(ValueError):
        safe_url("http://allowed.example.com/x", ["allowed.example.com"])


def test_safe_url_rejects_unlisted_host():
    with pytest.raises(ValueError):
        safe_url("https://evil.com/x", ["allowed.com"])


def test_safe_url_empty_allowlist_blocks_all():
    with pytest.raises(ValueError):
        safe_url("https://anything.example.com/x", [])


def test_safe_url_rejects_private_ip():
    # host 在白名单但解析到云元数据地址 → 拒绝
    with pytest.raises(ValueError):
        safe_url("https://169.254.169.254/latest/meta-data/", ["169.254.169.254"])


def test_safe_url_allows_listed_public_host(monkeypatch):
    def fake_getaddrinfo(host, port, *a, **k):
        return [(socket.AF_INET, None, None, None, ("93.184.216.34", 0))]

    monkeypatch.setattr(
        "roleplay.core.knowledge.security_utils.socket.getaddrinfo", fake_getaddrinfo
    )
    assert (
        safe_url("https://allowed.example.com/x", ["allowed.example.com"])
        == "https://allowed.example.com/x"
    )


def test_assert_public_url_blocks_metadata():
    with pytest.raises(ValueError):
        assert_public_url("http://169.254.169.254/")


# ===========================================================================
# S1 — SSRF：请求体 llm.base_url 绕过校验（QA 2026-09-29 安全修复）
#
# 缺陷：api/llm_config._validate_base_url 只服务于 /api/llm/test|models|switch，
# core/llm/factory.build_llm_from_config（/chat 的 req.llm.base_url 通道）
# **从未引用**，于是请求体里 http://169.254.169.254/latest/meta-data 会被直接
# 构建成 OpenAILikeProvider 并真发请求（云元数据 SSRF）。
#
# 修复：校验逻辑下沉到 core/llm/endpoint_guard.py，factory 在「端点由本次请求
# 决定」时调用它（策略与 api 层既有校验器逐条一致，**刻意不改**——环回与
# RFC1918 是有意放行，用于本地/内网 Ollama 部署）。
# ===========================================================================
from roleplay.config import Settings as _Settings  # noqa: E402
from roleplay.core.llm.endpoint_guard import (  # noqa: E402
    is_llm_base_url_allowed,
    validate_llm_base_url,
)
from roleplay.core.llm.factory import (  # noqa: E402
    aclose_global_llm,
    build_llm_from_config,
    reset_global_llm,
)
from roleplay.errors import EndpointNotAllowedError  # noqa: E402
from roleplay.models.chat import LLMOverride  # noqa: E402

# ── 允许清单（防误伤：这些必须继续可用）──
_ALLOWED_URLS = [
    "http://127.0.0.1:11434",        # Ollama 本地（本次修复的高危误伤点）
    "http://127.0.0.1:11434/v1",     # Ollama OpenAI 兼容端点（_DEFAULT_BASE_URLS）
    "http://localhost:11434/v1",     # 默认地址写法
    "http://192.168.1.50:11434/v1",  # 内网部署
    "http://10.0.0.1:8080",          # 内网部署
    "http://172.16.5.5:1234",        # 内网部署
    "http://[::1]:11434",            # IPv6 环回
    "https://api.deepseek.com/v1",   # 云端白名单
    "https://api.openai.com/v1",     # 云端白名单
]

# ── 拦截清单（SSRF 目标与非法协议）──
_BLOCKED_URLS = [
    "http://169.254.169.254/latest/meta-data",  # 云元数据（风险最高）
    "http://169.254.1.1",                       # 169.254.0.0/16 链路本地
    "http://100.64.0.1",                        # 运营商级 NAT 共享地址
    "http://93.184.216.34/v1",                  # 公网 IP（非白名单）
    "https://evil.example.com/v1",              # 非白名单域名
    "http://evil.example.com/v1",               # 非白名单域名 + http
    "file:///c:/windows/win.ini",               # 非 http(s) 协议
    "gopher://169.254.169.254:80/_x",           # 非 http(s) 协议
    "ftp://127.0.0.1/x",                        # 非 http(s) 协议
]


@pytest.mark.parametrize("url", _ALLOWED_URLS)
def test_endpoint_guard_allows_local_and_cloud(url):
    """放行清单：本地 Ollama / 内网 / 官方云端地址不得被误伤。"""
    assert is_llm_base_url_allowed("ollama", url, "k") is True, (
        f"合法端点被拦截（误伤）：{url}"
    )
    validate_llm_base_url("ollama", url, "k")  # 不抛异常


@pytest.mark.parametrize("url", _BLOCKED_URLS)
def test_endpoint_guard_blocks_metadata_and_bad_scheme(url):
    """拦截清单：云元数据 / 链路本地 / 共享地址 / 非白名单 / 非 http(s)。"""
    assert is_llm_base_url_allowed("ollama", url, "k") is False, (
        f"危险端点未被拦截：{url}"
    )
    with pytest.raises(ValueError):
        validate_llm_base_url("ollama", url, "k")


def test_endpoint_guard_cloud_host_requires_https_and_key():
    """云端白名单域名仍需 https + 非空 api_key（与既有 api 层策略一致）。"""
    # 白名单域名但 http → 拒
    assert is_llm_base_url_allowed("deepseek", "http://api.deepseek.com/v1", "sk-x") is False
    # 白名单域名 + https 但无 key → 拒（require_api_key 默认 True，api 层语义）
    assert is_llm_base_url_allowed("deepseek", "https://api.deepseek.com/v1", "") is False
    # core 层（factory）放宽 key 要求：地址安全判定与「缺 key 由 ProviderError 报错」解耦
    assert (
        is_llm_base_url_allowed(
            "deepseek", "https://api.deepseek.com/v1", "", require_api_key=False
        )
        is True
    )


@pytest.fixture
def _clean_global_llm():
    reset_global_llm()
    yield
    reset_global_llm()


def _override_settings() -> _Settings:
    """全局=mock，确保「provider 不同 → 走 override 分支」被触发。"""
    return _Settings(
        llm_provider="mock",
        llm_model="mock-model",
        llm_base_url="",
        llm_api_key="",
        rag_impl="memory",
    )


@pytest.mark.parametrize(
    "url",
    [
        "http://169.254.169.254/latest/meta-data",
        "http://169.254.1.1",
        "http://100.64.0.1",
        "file:///c:/windows/win.ini",
        "gopher://169.254.169.254:80/_x",
        "ftp://127.0.0.1/x",
        "https://evil.example.com/v1",
        "http://93.184.216.34/v1",
    ],
)
def test_build_llm_from_config_blocks_ssrf_override(url, _clean_global_llm):
    """S1 核心回归：/chat 的 override.base_url 必须过 SSRF 校验。"""
    with pytest.raises(EndpointNotAllowedError) as exc_info:
        build_llm_from_config(
            _override_settings(),
            LLMOverride(provider="ollama", model="qwen2.5:7b", base_url=url),
        )
    # 422：与 api 层既有校验器的 HTTPException(422) 语义对齐（而非 500）
    assert exc_info.value.status_code == 422
    # 错误详情不得回显 api_key
    assert "api_key" not in str(exc_info.value.details)


def test_build_llm_from_config_blocks_metadata_via_provider_switch(_clean_global_llm):
    """不带 base_url，仅切换 provider 也不能绕过：仍按解析后的端点校验。

    全局 base_url 指向 169.254.169.254（服务端配置被投毒的场景），
    override 只改 provider → 有效地址仍是元数据地址 → 必须拦截。
    """
    bad = _Settings(
        llm_provider="deepseek",
        llm_model="deepseek-chat",
        llm_base_url="http://169.254.169.254/latest/meta-data",
        llm_api_key="sk-x",
        rag_impl="memory",
    )
    with pytest.raises(EndpointNotAllowedError):
        build_llm_from_config(
            bad, LLMOverride(provider="ollama", model="qwen2.5:7b", base_url=None)
        )


def test_build_llm_from_config_keeps_local_ollama_usable(_clean_global_llm):
    """★防误伤★ 本地 Ollama override 必须仍然可用（本次修复最关键的回归点）。

    127.0.0.1 / localhost / RFC1918 是**有意放行**的合法部署形态，
    factory 侧校验不得把它们误判为 SSRF。
    """
    s = _override_settings()
    for url in ("http://127.0.0.1:11434", "http://127.0.0.1:11434/v1"):
        llm, needs_aclose = build_llm_from_config(
            s,
            LLMOverride(provider="ollama", model="qwen2.5:7b", base_url=url),
        )
        assert llm._base_url == url
        assert llm._model == "qwen2.5:7b"
        assert llm._api_key == "ollama"  # ollama 空 key 兜底不变
        assert needs_aclose is True


def test_ollama_local_default_base_url_still_usable(_clean_global_llm):
    """★防误伤★ 不传 base_url 的 ollama override（回退到本地默认地址）仍可用。

    这是前端最常见的「切到本地 Ollama」路径：req.llm = {provider: ollama, model: X}，
    base_url 缺省 → 回退 _DEFAULT_BASE_URLS["ollama"] = http://localhost:11434/v1，
    然后被 override 校验放行。
    """
    s = _override_settings()
    llm, needs_aclose = build_llm_from_config(
        s, LLMOverride(provider="ollama", model="qwen2.5:14b")
    )
    assert needs_aclose is True
    assert llm._base_url == "http://localhost:11434/v1"
    assert llm._model == "qwen2.5:14b"


def test_build_llm_from_config_allows_internal_and_cloud(_clean_global_llm):
    """内网（RFC1918）与官方云端 override 继续放行。"""
    s = _override_settings()
    cases = [
        ("ollama", "http://192.168.1.50:11434/v1"),
        ("ollama", "http://10.0.0.1:8080"),
        ("ollama", "http://172.16.5.5:1234"),
        ("deepseek", "https://api.deepseek.com/v1"),
    ]
    for provider, url in cases:
        llm, _ = build_llm_from_config(
            s, LLMOverride(provider=provider, model="m", base_url=url)
        )
        assert llm._base_url == url, f"合法端点被误伤：{url}"


def test_build_llm_from_config_trusted_settings_path_unchanged():
    """无 override 的服务端配置路径零改动（不新增校验，避免误伤运维配置）。

    校验只对「请求体可控的 override」生效；纯 settings 路径（build_llm）
    沿用旧行为——这是本次修复把风险面收敛到最小、又不破坏既有部署的关键。
    """
    s = _Settings(
        llm_provider="ollama",
        llm_model="qwen2.5:7b",
        llm_base_url="http://127.0.0.1:11434/v1",
        llm_api_key="",
        rag_impl="memory",
    )
    reset_global_llm()
    llm, needs_aclose = build_llm_from_config(s, None)
    assert needs_aclose is False
    assert llm._base_url == "http://127.0.0.1:11434/v1"


# ===========================================================================
# S2b — _sanitize 深度超限时跳过脱敏（深层 api_key 原样穿透）
# ===========================================================================
def test_sanitize_redacts_key_nested_beyond_depth_limit():
    """12 层嵌套的 api_key 必须不再原样输出（原实现在 depth>10 时原样返回）。

    降级语义（允许「打码」或「丢弃该层」，均不得泄漏原值）：
    超过 depth 上限的层级被折叠为固定占位符，原始字符串不再进入结果。
    """
    from roleplay.errors.handlers import _sanitize

    value: object = {"api_key": "sk-LEAK-DEEP-1234567890"}
    for _ in range(12):
        value = {"nested": value}
    out = str(_sanitize(value))
    assert "sk-LEAK-DEEP-1234567890" not in out, "深层 api_key 穿透了脱敏"
    assert "深度超限已隐藏" in out, "超限层应降级为占位符（丢弃该层）"
    # 结构化信息保留到上限层（不是整棵丢弃）
    assert out.count("nested") == 12


def test_sanitize_masks_sensitive_key_at_depth_boundary():
    """恰好落在深度边界的敏感键仍应「打码」为 ***（而非仅丢弃）。"""
    from roleplay.errors.handlers import _sanitize

    value: object = {"api_key": "sk-LEAK-BOUNDARY-1234567890"}
    for _ in range(11):
        value = {"nested": value}
    out = str(_sanitize(value))
    assert "sk-LEAK-BOUNDARY-1234567890" not in out
    assert "'api_key': '***'" in out


def test_sanitize_depth_limit_never_returns_raw_payload():
    """深度超限层不得原样输出任意内容（降级为固定占位符/打码）。"""
    from roleplay.errors.handlers import _sanitize

    secret = "TOPSECRET-beyond-depth-9999"
    value: object = secret
    for _ in range(15):
        value = {"w": value}
    out = str(_sanitize(value))
    assert secret not in out


def test_sanitize_depth_limit_handles_extreme_nesting():
    """超深嵌套（100 层）不得抛异常，且原始内容不泄漏。"""
    from roleplay.errors.handlers import _sanitize

    value: object = {"api_key": "sk-EXTREME-1234567890"}
    for _ in range(100):
        value = {"k": value}
    out = str(_sanitize(value))
    assert "sk-EXTREME-1234567890" not in out


def test_sanitize_still_redacts_shallow_and_bearer():
    """既有浅层行为不回归：敏感键、Bearer/sk- 形态值。"""
    from roleplay.errors.handlers import _sanitize

    out = _sanitize(
        {
            "token": "abc123",
            "ok": "hello",
            "hdr": "Authorization: Bearer sk-live-abcdef",
        }
    )
    assert out["token"] == "***"
    assert out["ok"] == "hello"
    assert "sk-live-abcdef" not in out["hdr"]


# ===========================================================================
# S2a — 自定义 HTTPException 处理器丢弃 exc.headers（Retry-After 消失）
# ===========================================================================
def test_http_exception_handler_preserves_retry_after():
    """429 的 Retry-After 必须透传到响应头，客户端才能正确退避。"""
    from fastapi import FastAPI, HTTPException
    from fastapi.testclient import TestClient

    from roleplay.errors.handlers import register_exception_handlers

    app = FastAPI()
    register_exception_handlers(app)

    @app.get("/limited")
    async def _limited():
        raise HTTPException(
            status_code=429,
            detail="请求过于频繁，请稍后再试",
            headers={"Retry-After": "42", "X-Custom": "v"},
        )

    client = TestClient(app)
    resp = client.get("/limited")
    assert resp.status_code == 429
    assert resp.headers.get("Retry-After") == "42"
    assert resp.headers.get("X-Custom") == "v"
    # 统一错误结构不变
    assert resp.json()["error"]["code"] == "http_error"


def test_http_exception_handler_without_headers_ok():
    """无自定义头的 HTTPException 行为不变（headers=None 不得报错）。"""
    from fastapi import FastAPI, HTTPException
    from fastapi.testclient import TestClient

    from roleplay.errors.handlers import register_exception_handlers

    app = FastAPI()
    register_exception_handlers(app)

    @app.get("/boom")
    async def _boom():
        raise HTTPException(status_code=404, detail="nope")

    client = TestClient(app)
    resp = client.get("/boom")
    assert resp.status_code == 404
    assert resp.json()["error"]["message"] == "nope"
