"""LLM base_url 端点安全校验（SSRF 防护）——无框架依赖的唯一下沉实现。

背景（S1，2026-QA 安全修复）：此前同一套校验逻辑只存在于
``api/llm_config.py::_validate_base_url``，仅服务于 ``/api/llm/test``、
``/api/llm/models`` 与 ``/api/llm/switch``；而 ``/chat`` 的 ``req.llm.base_url``
走的是 ``core/llm/factory.build_llm_from_config``，**从未被校验**——请求体里
填 ``http://169.254.169.254/latest/meta-data`` 会被直接构建成 OpenAILikeProvider
并发起请求（云元数据 SSRF）。本模块把校验下沉到 core 层（不 import fastapi），
让 api 层与 core 层共用同一份策略；``api/llm_config.py`` 的死代码由主代理接线复用。

分层约定：
- 本模块只依赖标准库 + ``openai_like._DEFAULT_BASE_URLS``（云端白名单来源）。
- 拒绝时抛 ``ValueError``（消息即拒绝原因）。api 层在边界转 ``HTTPException(422)``；
  core 层（factory）转 ``EndpointNotAllowedError``（422，见 errors/__init__.py）。
- **不使用 fastapi.HTTPException**：core 层不得耦合 HTTP 框架。

策略（与既有 ``_validate_base_url`` 逐条一致，**刻意不改**）：
  - scheme 仅允许 http/https，拒绝其它（file/gopher/ftp 等）；
  - host 为 IP 字面量：静态判定（零网络开销、不阻塞事件循环），放行环回 +
    RFC1918 内网 + IPv6 本地。这是**有意的设计**：本机/内网 Ollama 部署
    （``http://127.0.0.1:11434``、``http://192.168.1.50:11434``）必须可用；
  - host 为域名：仅放行 localhost 与云端预设白名单主机（openai/deepseek 官方地址，
    需 https + 非空 api_key）。不做 DNS 解析——避免内网主机名探测与
    getaddrinfo 同步阻塞，内网部署请直接填 IP 字面量；
  - 云元数据 169.254.169.254（169.254/16）、共享地址 100.64/10、公网非白名单
    一律拒绝。
"""
from __future__ import annotations

import ipaddress
import urllib.parse

from .openai_like import _DEFAULT_BASE_URLS

# 允许的「本机 / 内网」网段：本地与内网 Ollama（及自建 OpenAI 兼容网关）部署场景。
# 注意 169.254.0.0/16 **不在**其中：链路本地段含云元数据 169.254.169.254。
ALLOWED_PRIVATE_NETWORKS = (
    ipaddress.ip_network("127.0.0.0/8"),     # 环回（Ollama localhost）
    ipaddress.ip_network("10.0.0.0/8"),      # RFC1918
    ipaddress.ip_network("172.16.0.0/12"),   # RFC1918
    ipaddress.ip_network("192.168.0.0/16"),  # RFC1918
    ipaddress.ip_network("::1/128"),         # IPv6 环回
    ipaddress.ip_network("fc00::/7"),        # IPv6 唯一本地
)

# 云端预设白名单主机（openai / deepseek 官方地址）
ALLOWED_CLOUD_HOSTS = frozenset(
    h for h in (urllib.parse.urlparse(u).hostname for u in _DEFAULT_BASE_URLS.values()) if h
)


def _is_allowed_private(ip_str: str) -> bool:
    """IP 字面量是否落在放行的环回/内网网段内（静态判定，零网络开销）。"""
    try:
        ip = ipaddress.ip_address(ip_str)
    except ValueError:
        return False
    return any(ip in net for net in ALLOWED_PRIVATE_NETWORKS)


def _reject(reason: str) -> None:
    raise ValueError(reason)


def validate_llm_base_url(
    provider: str,
    base_url: str,
    api_key: str = "",
    *,
    require_api_key: bool = True,
) -> None:
    """校验 LLM ``base_url`` 是否允许被发起请求；不合法则抛 ``ValueError``。

    Args:
        provider: 端点提供方（openai/deepseek/ollama/mock）；当前仅用于日志语义，
            策略本身按 host 判定（云端白名单对 openai/deepseek 都成立）。
        base_url: 待校验地址（来自请求体 override 或服务端配置）。
        api_key: 仅用于「云端白名单域名必须带 key」这一条。
        require_api_key: 云端白名单域名缺 key 时是否硬失败。
            - api 层（``/api/llm/test``、``/switch``）保持 True：测试连通性前先拦下
              明显无效的请求；
            - core 层（``factory.build_llm_from_config``）传 False：缺 key 的云端
              override 由 ProviderError 在 generate 时显式报错（既有语义与
              ``tests/test_llm_override.py`` 已锁定的行为），此处只做地址安全判定，
              避免改变「无 key 云端 override 构建成功、调用时才失败」的契约。
    """
    parsed = urllib.parse.urlparse(base_url or "")
    if parsed.scheme not in ("http", "https"):
        _reject("base_url 仅允许 http/https 协议")
    host = (parsed.hostname or "").lower()
    if not host:
        _reject("base_url 缺少主机名")

    # localhost 域名：环回，直接放行（Ollama 默认地址）
    if host == "localhost" or host.endswith(".localhost"):
        return

    # IP 字面量：静态判定（零网络开销）；内网/环回放行，其余（含 169.254.169.254）拒绝
    try:
        ipaddress.ip_address(host)
        is_ip_literal = True
    except ValueError:
        is_ip_literal = False
    if is_ip_literal:
        if _is_allowed_private(host):
            return
        _reject("非本机/内网 IP 地址的 base_url 仅支持云端预设白名单（https）")

    # 域名：必须 https + 云端预设白名单 + 非空 api_key（不做 DNS 解析）
    if parsed.scheme != "https":
        _reject("非本机/内网地址的 base_url 必须使用 https")
    if host not in ALLOWED_CLOUD_HOSTS:
        _reject(f"base_url 主机不在允许列表（{sorted(ALLOWED_CLOUD_HOSTS)}），仅支持官方云端地址")
    if require_api_key and not (api_key or "").strip():
        _reject("云端 provider 需要 api_key")


def is_llm_base_url_allowed(
    provider: str,
    base_url: str,
    api_key: str = "",
    *,
    require_api_key: bool = True,
) -> bool:
    """``validate_llm_base_url`` 的布尔封装（供测试/只读判定使用）。"""
    try:
        validate_llm_base_url(
            provider, base_url, api_key, require_api_key=require_api_key
        )
    except ValueError:
        return False
    return True
