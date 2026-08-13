"""LLM 配置查询与连通性测试路由（前端「模型切换」配套）。

- GET  /api/llm/config   返回当前全局 LLM 配置（脱敏）+ 可选项（云端预设/模型）
- POST /api/llm/test     用给定参数构建客户端做一次非流式连通性测试

设计约束（与 LLMOverride 一致）：
- 查询接口绝不返回 api_key（脱敏），前端只读「当前 provider/model/base_url」。
- 测试接口接收前端传入的 provider/model/base_url/api_key，仅本次请求使用，
  不写回全局 frozen Settings、不落盘、不进日志。
- Ollama 本地模型列表：调本地 Ollama /api/tags 获取（读操作，无需 key）。
"""
import logging
import socket
from typing import Annotated, Literal

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from ..config import Settings, get_settings
from ..models.chat import LLMOverride
from .deps import get_settings_dep

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/llm", tags=["llm"])

# 云端预设（与 openai_like._DEFAULT_BASE_URLS 保持一致，供前端下拉展示）
CLOUD_PRESETS: dict[str, dict] = {
    "openai": {
        "label": "OpenAI 云端",
        "base_url": "https://api.openai.com/v1",
        "models": ["gpt-4o", "gpt-4o-mini", "gpt-4.1", "gpt-4.1-mini"],
    },
    "deepseek": {
        "label": "DeepSeek 云端",
        "base_url": "https://api.deepseek.com/v1",
        "models": ["deepseek-chat", "deepseek-reasoner"],
    },
}

# Ollama 默认地址（供前端「本地 Ollama」模式）
OLLAMA_DEFAULT_URL = "http://localhost:11434"
# Ollama 拉取本地模型列表的地址（OpenAI 兼容端点的 /v1 前缀要去掉）
OLLAMA_TAGS_URL = OLLAMA_DEFAULT_URL + "/api/tags"


class LLMConfigResponse(BaseModel):
    """当前全局 LLM 配置（脱敏）+ 可选项。"""

    provider: str = "mock"
    model: str = "mock-model"
    base_url: str = ""
    has_api_key: bool = False  # 是否已配置 key（不返回 key 本身）
    cloud_presets: dict[str, dict] = Field(default_factory=dict)
    ollama_default_url: str = OLLAMA_DEFAULT_URL
    default_ollama_models: list[str] = Field(
        default_factory=lambda: ["qwen2.5:7b", "qwen2.5:14b", "llama3.1:8b", "deepseek-r1:7b"]
    )


class LLMTestRequest(BaseModel):
    """连通性测试请求（仅本次使用，不落盘）。"""

    provider: Literal["openai", "deepseek", "ollama"] = "ollama"
    model: str = Field(..., min_length=1, max_length=128)
    base_url: str = Field("", max_length=512)
    api_key: str = Field("", max_length=512)


class LLMTestResponse(BaseModel):
    ok: bool
    detail: str = ""
    model: str = ""
    provider: str = ""


@router.get("/config", response_model=LLMConfigResponse)
async def llm_config(
    settings: Settings = Depends(get_settings_dep),
) -> LLMConfigResponse:
    """返回脱敏后的全局 LLM 配置 + 前端可选项。"""
    return LLMConfigResponse(
        provider=settings.llm_provider,
        model=settings.llm_model,
        base_url=settings.llm_base_url,
        has_api_key=bool(settings.llm_api_key),
        cloud_presets=CLOUD_PRESETS,
    )


@router.get("/ollama/models")
async def ollama_models(
    settings: Settings = Depends(get_settings_dep),
) -> dict:
    """拉取本地 Ollama 已安装模型列表（/api/tags）。

    失败时返回空列表 + error 字段，前端回退默认清单，不阻塞 UI。
    """
    import httpx

    url = (settings.ollama_base_url or OLLAMA_DEFAULT_URL).rstrip("/") + "/api/tags"
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.get(url)
            resp.raise_for_status()
            models = [
                m.get("name", "")
                for m in (resp.json().get("models") or [])
                if m.get("name")
            ]
            return {"models": models, "error": ""}
    except Exception as exc:  # noqa: BLE001
        logger.warning("拉取 Ollama 模型列表失败: %s", exc)
        return {"models": [], "error": f"无法连接 Ollama：{exc}"}


@router.post("/test", response_model=LLMTestResponse)
async def llm_test(
    req: LLMTestRequest,
    settings: Settings = Depends(get_settings_dep),
) -> LLMTestResponse:
    """用给定参数构建一次性客户端，发一条最小请求验证连通性。

    - api_key 仅本次请求使用；后端不落盘、不进日志。
    - Ollama 空 key 自动兜底 "ollama"（与 build_llm 一致）。
    """
    import ipaddress
    import urllib.parse

    from ..core.llm.openai_like import OpenAILikeProvider, _DEFAULT_BASE_URLS

    provider = req.provider
    model = req.model.strip()
    base_url = req.base_url.strip() or _DEFAULT_BASE_URLS.get(provider, "")
    api_key = req.api_key.strip()
    if provider == "ollama" and not api_key:
        api_key = "ollama"

    # SSRF 防护：base_url 来自前端可任意指定，若不约束，可借 /test 探测内网
    # （127.0.0.1、云元数据 169.254.169.254、内网网段等）。规则：
    #   - scheme 仅允许 http/https，拒绝其它（file/gopher 等）；
    #   - host 解析后的 IP 允许两类：
    #       a) 环回 + RFC1918 内网（Ollama 本地/内网部署场景）；
    #       b) 公网 https 且主机在云端预设白名单内（openai/deepseek 官方地址）。
    #     云元数据 169.254.169.254、共享地址 100.64/10、公网非白名单一律拒绝。
    _LLM_ALLOWED_PRIVATE = [
        ipaddress.ip_network("127.0.0.0/8"),     # 环回（Ollama localhost）
        ipaddress.ip_network("10.0.0.0/8"),      # RFC1918
        ipaddress.ip_network("172.16.0.0/12"),   # RFC1918
        ipaddress.ip_network("192.168.0.0/16"),  # RFC1918
        ipaddress.ip_network("::1/128"),         # IPv6 环回
        ipaddress.ip_network("fc00::/7"),        # IPv6 唯一本地
    ]

    parsed = urllib.parse.urlparse(base_url)
    if parsed.scheme not in ("http", "https"):
        raise HTTPException(status_code=422, detail="base_url 仅允许 http/https 协议")
    host = (parsed.hostname or "").lower()
    if not host:
        raise HTTPException(status_code=422, detail="base_url 缺少主机名")
    try:
        infos = socket.getaddrinfo(host, parsed.port or (443 if parsed.scheme == "https" else 80))
    except socket.gaierror as exc:
        raise HTTPException(status_code=422, detail=f"无法解析主机：{host}") from exc

    def _is_allowed_private(ip_str: str) -> bool:
        try:
            ip = ipaddress.ip_address(ip_str)
        except ValueError:
            return False
        return any(ip in net for net in _LLM_ALLOWED_PRIVATE)

    is_llm_local = bool(infos) and all(_is_allowed_private(info[4][0]) for info in infos)
    if not is_llm_local:
        # 非 Ollama 本地地址：必须是 https 公网白名单云预设（含 key）
        if parsed.scheme != "https":
            raise HTTPException(status_code=422, detail="非本机/内网地址的 base_url 必须使用 https")
        allow_hosts = {
            urllib.parse.urlparse(u).hostname for u in _DEFAULT_BASE_URLS.values()
        }
        allow_hosts.discard(None)
        if host not in allow_hosts:
            raise HTTPException(
                status_code=422,
                detail=f"base_url 主机不在允许列表（{sorted(allow_hosts)}），仅支持官方云端地址",
            )
        if not api_key:
            raise HTTPException(status_code=422, detail="云端 provider 需要 api_key")

    client = OpenAILikeProvider(
        model=model,
        api_key=api_key,
        base_url=base_url,
        timeout=15.0,
        max_tokens=settings.max_tokens_per_reply,
    )
    try:
        # 最小请求：单 token 回复即可证明连通 + 鉴权通过
        reply = await client.generate(
            system="你是连通性测试助手。", user="请只回复：ok", history=None
        )
        return LLMTestResponse(
            ok=True,
            detail=reply[:80] or "ok",
            model=model,
            provider=provider,
        )
    except Exception as exc:  # noqa: BLE001
        logger.warning("LLM 连通性测试失败 provider=%s model=%s: %s", provider, model, exc)
        # 透传 ProviderError.details（含服务商原始错误体，如 401 key 无效 / 429 限流）
        detail = str(exc)[:200]
        if getattr(exc, "details", None):
            d = str(exc.details)
            if d and d != detail:
                detail = d[:200]
        return LLMTestResponse(
            ok=False,
            detail=detail,
            model=model,
            provider=provider,
        )
    finally:
        if hasattr(client, "aclose"):
            try:
                await client.aclose()
            except Exception:  # noqa: BLE001
                pass
