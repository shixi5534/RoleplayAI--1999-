"""LLM 配置查询与连通性测试路由（前端「模型切换」配套）。

- GET  /api/llm/config   返回当前全局 LLM 配置（脱敏）+ 可选项（云端预设/模型）
- POST /api/llm/test     用给定参数构建客户端做一次非流式连通性测试
- POST /api/llm/switch   持久化切换全局 LLM（写 .env + 热重载，QQ 渠道同步生效）

设计约束（与 LLMOverride 一致）：
- 查询接口绝不返回 api_key（脱敏），前端只读「当前 provider/model/base_url」。
- 测试接口接收前端传入的 provider/model/base_url/api_key，仅本次请求使用，
  不写回全局 frozen Settings、不落盘、不进日志。
- 切换接口仅持久化 provider/model/base_url（无密钥风险）；api_key 由前端
  每次请求携带（走请求级 override），或写入独立密钥存储（不在本文件）。
- Ollama 本地模型列表：调本地 Ollama /api/tags 获取（读操作，无需 key）。
"""
import logging
import re
from pathlib import Path
from typing import Annotated, Literal

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from ..config import Settings, get_settings
from ..core.llm.mock import MockLLMProvider
from ..errors.handlers import _safe_details
from ..models.chat import LLMOverride
from .deps import get_settings_dep
from .ratelimit import rate_limit

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/llm", tags=["llm"], dependencies=[Depends(rate_limit)]
)

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


class LLMSwitchRequest(BaseModel):
    """持久化切换全局 LLM（写 .env + 热重载，QQ 渠道同步生效）。

    - provider/model/base_url 落盘（.env），api_key 不落盘。
    - api_key 可同时传入：仅在本次热重载时用于构建新全局客户端（内存），
      不写入 .env（与「前端每请求携带 key」的既有安全模型一致）。
    """

    provider: Literal["openai", "deepseek", "ollama"] = "ollama"
    model: str = Field(..., min_length=1, max_length=128)
    base_url: str = Field("", max_length=512)
    api_key: str = Field("", max_length=512)


class LLMSwitchResponse(BaseModel):
    ok: bool
    detail: str = ""
    model: str = ""
    provider: str = ""


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

    # 与 build_embedder 对齐：优先 ollama_base_url，回退 llm_base_url，
    # 并剥离 OpenAI 兼容后缀 /v1，避免拼接出 /v1/api/tags。
    base = (settings.ollama_base_url or settings.llm_base_url or OLLAMA_DEFAULT_URL).rstrip("/")
    base = re.sub(r"/v1/?$", "", base)
    url = base + "/api/tags"
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


def _validate_base_url(provider: str, base_url: str, api_key: str = "") -> None:
    """SSRF 防护：校验 base_url 合法性（/test 与 /switch 共用）。

    base_url 来自前端可任意指定，若不约束，可借接口探测内网
    （127.0.0.1、云元数据 169.254.169.254、内网网段等）。规则：
      - scheme 仅允许 http/https，拒绝其它（file/gopher 等）；
      - host 为 IP 字面量：静态判定（零网络开销、不阻塞事件循环），
        仅放行环回 + RFC1918 内网 + IPv6 本地（Ollama 本地/内网部署场景）；
      - host 为域名：仅放行 localhost 与云端预设白名单主机
        （openai/deepseek 官方地址，需 https + 非空 api_key）。
        不做 DNS 解析——避免内网主机名探测与 getaddrinfo 同步阻塞，
        内网部署请直接填 IP 字面量。
      云元数据 169.254.169.254、共享地址 100.64/10、公网非白名单一律拒绝。
    """
    import ipaddress
    import urllib.parse

    from ..core.llm.openai_like import _DEFAULT_BASE_URLS

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

    def _is_allowed_private(ip_str: str) -> bool:
        try:
            ip = ipaddress.ip_address(ip_str)
        except ValueError:
            return False
        return any(ip in net for net in _LLM_ALLOWED_PRIVATE)

    # localhost 域名：环回，直接放行（Ollama 默认地址）
    if host == "localhost" or host.endswith(".localhost"):
        return

    # IP 字面量：静态判定（零网络开销）
    try:
        ipaddr = ipaddress.ip_address(host)
    except ValueError:
        ipaddr = None
    if ipaddr is not None:
        if _is_allowed_private(host):
            return
        raise HTTPException(
            status_code=422,
            detail="非本机/内网 IP 地址的 base_url 仅支持云端预设白名单（https）",
        )

    # 域名：必须 https + 云端预设白名单 + 非空 api_key（不做 DNS 解析）
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


@router.post("/test", response_model=LLMTestResponse)
async def llm_test(
    req: LLMTestRequest,
    settings: Settings = Depends(get_settings_dep),
) -> LLMTestResponse:
    """用给定参数构建一次性客户端，发一条最小请求验证连通性。

    - api_key 仅本次请求使用；后端不落盘、不进日志。
    - Ollama 空 key 自动兜底 "ollama"（与 build_llm 一致）。
    """
    from ..core.llm.openai_like import OpenAILikeProvider, _DEFAULT_BASE_URLS

    provider = req.provider
    model = req.model.strip()
    base_url = req.base_url.strip() or _DEFAULT_BASE_URLS.get(provider, "")
    api_key = req.api_key.strip()
    if provider == "ollama" and not api_key:
        api_key = "ollama"

    # SSRF 防护（与 /switch 共用）
    _validate_base_url(provider, base_url, api_key)

    client = OpenAILikeProvider(
        model=model,
        api_key=api_key,
        base_url=base_url,
        timeout=15.0,
        max_tokens=settings.max_tokens_per_reply,
        top_p=settings.llm_top_p,
        repetition_penalty=settings.llm_repetition_penalty,
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
        # 透传 ProviderError.details（含服务商原始错误体，如 401 key 无效 / 429 限流）；
        # 返回前必须走统一脱敏，防止服务商错误体回显请求中的 API key。
        detail = str(exc)[:200]
        safe = _safe_details(getattr(exc, "details", None))
        if safe and str(safe) != detail:
            detail = str(safe)[:200]
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


def _persist_llm_env(
    provider: str, model: str, base_url: str
) -> tuple[bool, str]:
    """把全局 LLM 配置写入 .env（api_key 不落盘）。

    仅在 .env 存在且可写时生效；环境变量注入方式（无 .env）跳过并告警。
    返回 (ok, detail)。
    """
    env_path = Path(".env")
    if not env_path.exists():
        return False, ".env 不存在，无法持久化（当前为环境变量注入模式）"
    try:
        lines = env_path.read_text(encoding="utf-8").splitlines()
    except OSError as exc:
        return False, f"读取 .env 失败：{exc}"

    updates = {
        "ROLEPLAY_LLM_PROVIDER": provider,
        "ROLEPLAY_LLM_MODEL": model,
    }
    if base_url:
        updates["ROLEPLAY_LLM_BASE_URL"] = base_url

    out: list[str] = []
    seen: set[str] = set()
    for line in lines:
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            out.append(line)
            continue
        key = stripped.split("=", 1)[0].strip()
        if key in updates:
            out.append(f"{key}={updates[key]}")
            seen.add(key)
        else:
            out.append(line)
    # 缺失的键补在末尾（带分组注释）
    for key, val in updates.items():
        if key not in seen:
            out.append(f"{key}={val}")
    try:
        env_path.write_text("\n".join(out) + "\n", encoding="utf-8")
    except OSError as exc:
        return False, f"写入 .env 失败：{exc}"
    return True, "已写入 .env"


@router.post("/switch", response_model=LLMSwitchResponse)
async def llm_switch(
    req: LLMSwitchRequest,
    settings: Settings = Depends(get_settings_dep),
) -> LLMSwitchResponse:
    """持久化切换全局 LLM（写 .env + 热重载）。

    - 不传 api_key 时复用全局既有 key（ollama 空 key 兜底 "ollama"）。
    - 热重载：清 settings 缓存 + 清全局 LLM 缓存 → 下一请求按新配置重建。
      服务无需重启，QQ 渠道（走全局实例）同步生效。
    - 失败不破坏现状：写 .env 失败时返回错误，缓存不动。
    """
    import os

    from ..core.llm.factory import _GLOBAL_LLM_CACHE, build_llm
    from ..core.llm.openai_like import OpenAILikeProvider, _DEFAULT_BASE_URLS

    provider = req.provider
    model = req.model.strip()
    base_url = req.base_url.strip()
    api_key = req.api_key.strip()

    # SSRF/安全复用 llm_test 的 base_url 校验逻辑（抽离后共用）
    # 云端 provider 必须带 api_key 才能放行（白名单主机 + https + key 三重校验）
    _validate_base_url(provider, base_url, api_key)

    # 1) 先写 .env（失败则中止，不热重载）
    ok, detail = _persist_llm_env(provider, model, base_url)
    if not ok:
        return LLMSwitchResponse(ok=False, detail=detail, model=model, provider=provider)

    # 2) 热重载：清配置缓存 + 全局 LLM 缓存。
    # 注意：旧客户端不能在这里 aclose——LLMProfileExtractor/LLMEventExtractor
    # 在启动时捕获了同一个实例，此处关闭会让之后每次画像/事件抽取打到已关闭的
    # httpx 客户端上，被 except Exception 吞掉，记忆抽取静默失效直到重启；
    # 同时也会砍断仍在途的对话请求。旧实例由持有方（extractor）随进程生命周期
    # 释放，单次切换最多滞留一个客户端，属可接受的有限占用。
    get_settings.cache_clear()
    _GLOBAL_LLM_CACHE.clear()

    # 3) 用新配置预热一次全局客户端（api_key 仅在内存，不落盘）
    fresh = get_settings()
    new_key = api_key or fresh.llm_api_key
    if provider == "ollama" and not new_key:
        new_key = "ollama"
    try:
        if provider == "mock":
            client = MockLLMProvider(model=model)
        else:
            client = OpenAILikeProvider(
                model=model,
                api_key=new_key,
                base_url=base_url or _DEFAULT_BASE_URLS.get(provider, ""),
                timeout=30.0,
                max_tokens=fresh.max_tokens_per_reply,
                top_p=fresh.llm_top_p,
                repetition_penalty=fresh.llm_repetition_penalty,
            )
        _GLOBAL_LLM_CACHE[provider] = client
    except Exception as exc:  # noqa: BLE001
        logger.warning("切换后预热新 LLM 失败（配置已生效，回复将报错）：%s", exc)
    return LLMSwitchResponse(
        ok=True,
        detail="已切换并热重载（QQ 渠道同步生效）",
        model=model,
        provider=provider,
    )
