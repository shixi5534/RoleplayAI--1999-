"""OpenAI 兼容 LLM Provider（适配 openai / deepseek / ollama）。

通过 base_url + api_key 切换不同厂商；统一封装为 LLMPort。
所有外部错误转为 ProviderError，由全局异常处理器统一返回。

日志安全：服务商原始错误体可能回显请求内容（含 Authorization/API key），
写入日志前统一脱敏，避免凭据泄漏到 server.log。
"""
import asyncio
import json
import logging
import re

import httpx

from ...config import get_settings
from ...errors import ProviderError
from .base import LLMPort

logger = logging.getLogger(__name__)

# 常见凭据形态：Authorization 头、sk- 开头的 API key、显式键名
_REDACT_RE = re.compile(
    r"(Bearer\s+[A-Za-z0-9._~+/-]+=*|sk-[A-Za-z0-9-]+|"
    r"(?i:api[_-]?key|token|secret|password|passwd)[\"':=\s]+[^\s,}\"']+)",
    re.IGNORECASE,
)


def _redact(text: str) -> str:
    """日志脱敏：把文本中的凭据形态替换为 '***'。"""
    if not text:
        return text
    return _REDACT_RE.sub("***", text)


_DEFAULT_BASE_URLS = {
    "openai": "https://api.openai.com/v1",
    "deepseek": "https://api.deepseek.com/v1",
    "ollama": "http://localhost:11434/v1",
}

# 瞬时故障（超时/连接/5xx/429）重试 1 次；业务错误（401/402/403/404）不重试
_MAX_RETRIES = 2
_RETRY_DELAY = 0.5


async def _error_body(exc: httpx.HTTPStatusError) -> str:
    """安全读取 HTTP 错误响应体（前 300 字）。

    非流式响应已读 body，直接用 .text；
    流式响应（client.stream）未读 body 时 .text 抛 ResponseNotRead，
    需 await aread() 兜底，再失败则回退空串。
    """
    if exc.response is None:
        return ""
    try:
        return exc.response.text[:300]
    except Exception:  # noqa: BLE001
        try:
            raw = await exc.response.aread()
            return raw.decode("utf-8", errors="replace")[:300]
        except Exception:  # noqa: BLE001
            return ""


def _build_messages(*, system: str, user: str, history: list[dict] | None) -> list[dict]:
    """把 system / history / user 拼成 OpenAI 格式的 messages。

    history 仅保留 user/assistant 角色，防止异常角色污染请求。
    """
    messages: list[dict] = [{"role": "system", "content": system}]
    if history:
        for h in history:
            role = (h or {}).get("role")
            content = (h or {}).get("content")
            if role in ("user", "assistant") and content:
                messages.append({"role": role, "content": str(content)})
    messages.append({"role": "user", "content": user})
    return messages


class OpenAILikeProvider(LLMPort):
    def __init__(
        self,
        *,
        model: str,
        api_key: str,
        base_url: str,
        timeout: float = 30.0,
        max_tokens: int | None = None,
    ) -> None:
        self._model = model
        self._api_key = api_key
        self._base_url = base_url.rstrip("/")
        self._timeout = timeout
        self._max_tokens = max_tokens
        # 复用长生命周期客户端，避免每次请求新建连接（性能/连接管理）
        self._client = httpx.AsyncClient(timeout=timeout)

    @property
    def model_name(self) -> str:
        return self._model

    async def aclose(self) -> None:
        """释放底层连接池；由应用 lifespan 在关闭期调用。"""
        await self._client.aclose()

    async def generate(
        self,
        *,
        system: str,
        user: str,
        history: list[dict] | None = None,
        temperature: float | None = None,
    ) -> str:
        if not self._api_key:
            raise ProviderError(
                "缺少 LLM API Key", details={"provider": self._model}
            )
        messages = _build_messages(system=system, user=user, history=history)
        payload: dict = {
            "model": self._model,
            "messages": messages,
            "temperature": temperature if temperature is not None else 0.8,
        }
        if self._max_tokens:
            payload["max_tokens"] = self._max_tokens
        headers = {
            "Authorization": f"Bearer {self._api_key}",
            "Content-Type": "application/json",
        }
        # 超时/连接类瞬时错误重试 1 次；4xx 业务错误（401/402/403/404）不重试
        for attempt in range(1, _MAX_RETRIES + 1):
            try:
                resp = await self._client.post(
                    f"{self._base_url}/chat/completions",
                    json=payload,
                    headers=headers,
                )
                resp.raise_for_status()
                data = resp.json()
                return data["choices"][0]["message"]["content"]
            except httpx.HTTPStatusError as exc:
                status = exc.response.status_code if exc.response else 0
                body = await _error_body(exc)
                detail = body or f"HTTP {status or '?'}"
                logger.error(
                    "LLM HTTP 错误 provider=%s status=%s body=%s",
                    self._model,
                    status or "?",
                    _redact(body),
                )
                if status in (429, 500, 502, 503, 504) and attempt < _MAX_RETRIES:
                    await asyncio.sleep(_RETRY_DELAY)
                    continue
                raise ProviderError(
                    f"LLM 调用失败（HTTP {status or '?'}）",
                    details=detail,
                ) from exc
            except httpx.HTTPError as exc:
                # 超时（timeout=30s 已在客户端配置）/ 连接错误：瞬时故障，重试 1 次
                if attempt < _MAX_RETRIES:
                    logger.warning(
                        "LLM 网络错误 provider=%s（%s），%.1fs 后重试...",
                        self._model,
                        type(exc).__name__,
                        _RETRY_DELAY,
                    )
                    await asyncio.sleep(_RETRY_DELAY)
                    continue
                # 连接/超时是常见运维场景（如 Ollama 未启动），简洁记录即可，
                # 不打堆栈刷屏；堆栈保留给真正需要排查的意外错误。
                # 同时给出可读的中文原因：连接被拒=服务未启动，超时=服务无响应
                is_timeout = isinstance(exc, (httpx.TimeoutException, asyncio.TimeoutError))
                reason = (
                    "连接超时（服务无响应，可能负载过高）"
                    if is_timeout
                    else "连接失败（服务未启动或地址不可达）"
                )
                logger.warning(
                    "LLM 调用失败 provider=%s（%s）：%s。请检查 LLM 服务是否已启动、"
                    "base_url=%s 是否可达。",
                    self._model,
                    type(exc).__name__,
                    str(exc),
                    self._base_url,
                )
                raise ProviderError(
                    f"LLM 调用失败（{reason}）",
                    details={"provider": self._model, "base_url": self._base_url, "error": str(exc)},
                ) from exc
            except (KeyError, IndexError, ValueError) as exc:
                logger.exception("LLM 响应解析失败 provider=%s", self._model)
                raise ProviderError("LLM 响应解析失败", details=str(exc)) from exc
        raise ProviderError("LLM 调用失败（重试耗尽）")  # 理论不可达

    async def generate_stream(
        self,
        *,
        system: str,
        user: str,
        history: list[dict] | None = None,
        temperature: float | None = None,
    ):
        """真流式：走 OpenAI 兼容的 SSE 接口，逐 token yield 文本片段。"""
        if not self._api_key:
            raise ProviderError(
                "缺少 LLM API Key", details={"provider": self._model}
            )
        messages = _build_messages(system=system, user=user, history=history)
        payload: dict = {
            "model": self._model,
            "messages": messages,
            "temperature": temperature if temperature is not None else 0.8,
            "stream": True,
        }
        if self._max_tokens:
            payload["max_tokens"] = self._max_tokens
        headers = {
            "Authorization": f"Bearer {self._api_key}",
            "Content-Type": "application/json",
        }
        # 流式连接阶段的瞬时错误（超时/连接/5xx/429）重试 1 次；
        # 一旦开始 yield token 便无法重试（客户端可能已渲染部分文本，
        # 重试会产生重复内容），此时任何异常直接上抛。
        started = False
        for attempt in range(1, _MAX_RETRIES + 1):
            try:
                async with self._client.stream(
                    "POST",
                    f"{self._base_url}/chat/completions",
                    json=payload,
                    headers=headers,
                ) as resp:
                    resp.raise_for_status()
                    async for raw in resp.aiter_lines():
                        line = raw.strip()
                        if not line or not line.startswith("data:"):
                            continue
                        data = line[len("data:"):].strip()
                        if data == "[DONE]":
                            return
                        try:
                            chunk = json.loads(data)
                        except (json.JSONDecodeError, ValueError):
                            continue
                        try:
                            delta = chunk["choices"][0]["delta"].get("content")
                        except (KeyError, IndexError, TypeError):
                            continue
                        if delta:
                            started = True
                            yield delta
                return
            except httpx.HTTPStatusError as exc:
                status = exc.response.status_code if exc.response else 0
                body = await _error_body(exc)
                detail = body or f"HTTP {status or '?'}"
                logger.error(
                    "LLM 流式 HTTP 错误 provider=%s status=%s body=%s",
                    self._model,
                    status or "?",
                    _redact(body),
                )
                if (
                    not started
                    and status in (429, 500, 502, 503, 504)
                    and attempt < _MAX_RETRIES
                ):
                    await asyncio.sleep(_RETRY_DELAY)
                    continue
                raise ProviderError(
                    f"LLM 调用失败（HTTP {status or '?'}）",
                    details=detail,
                ) from exc
            except httpx.HTTPError as exc:
                # 超时/连接错误：仅当尚未向客户端 yield 任何 token 时重试 1 次
                if not started and attempt < _MAX_RETRIES:
                    logger.warning(
                        "LLM 流式网络错误 provider=%s（%s），%.1fs 后重试...",
                        self._model,
                        type(exc).__name__,
                        _RETRY_DELAY,
                    )
                    await asyncio.sleep(_RETRY_DELAY)
                    continue
                # 连接/超时是常见运维场景（如 Ollama 未启动），简洁记录即可
                is_timeout = isinstance(exc, (httpx.TimeoutException, asyncio.TimeoutError))
                reason = (
                    "连接超时（服务无响应，可能负载过高）"
                    if is_timeout
                    else "连接失败（服务未启动或地址不可达）"
                )
                logger.warning(
                    "LLM 流式调用失败 provider=%s（%s）：%s。请检查 LLM 服务是否已启动、"
                    "base_url=%s 是否可达。",
                    self._model,
                    type(exc).__name__,
                    str(exc),
                    self._base_url,
                )
                raise ProviderError(
                    f"LLM 调用失败（{reason}）",
                    details={"provider": self._model, "base_url": self._base_url, "error": str(exc)},
                ) from exc
