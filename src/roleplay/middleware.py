"""安全基线中间件：为所有响应补齐安全响应头。

使用 Starlette 的 BaseHTTPMiddleware，在响应返回前注入安全头。
同源前端（pixi/live2d 本地脚本）满足 CSP 的 script-src 'self' 约束。
"""
import logging

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

SECURITY_HEADERS: dict[str, str] = {
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "DENY",
    "Referrer-Policy": "no-referrer",
    "Cross-Origin-Opener-Policy": "same-origin",
    # 同源脚本 + 内联样式（index.html 内联 <style>）+ data: 图片/模型纹理/字体
    # script-src 加 'unsafe-eval'：PIXI v6 的 Filter / 动态 shader 生成走 new Function()，
    # 否则 pixi-live2d-display 渲染管线会抛 "does not allow unsafe-eval"。
    # media-src 加 blob:：voice.js 用 URL.createObjectURL 播放 TTS 音频流，
    # 不加会被 default-src 'self' 拦截导致"语音合成失败/无法播放"。
    "Content-Security-Policy": (
        "default-src 'self'; "
        "img-src 'self' data:; "
        "font-src 'self' data:; "
        "media-src 'self' blob:; "
        "style-src 'self' 'unsafe-inline'; "
        "script-src 'self' 'unsafe-eval'; "
        "connect-src 'self'"
    ),
}


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        response = await call_next(request)
        for key, value in SECURITY_HEADERS.items():
            response.headers.setdefault(key, value)
        return response


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """请求日志中间件：记录方法、路径、状态码与耗时，便于排查与审计。

    对 /health 等高频探活端点降级为 DEBUG，避免日志刷屏。
    """

    _NOISY_PATHS = ("/health",)

    async def dispatch(self, request: Request, call_next) -> Response:
        import time

        start = time.perf_counter()
        try:
            response = await call_next(request)
        except Exception:
            elapsed = (time.perf_counter() - start) * 1000
            logger.warning(
                "请求异常 %s %s (%.1fms)",
                request.method,
                request.url.path,
                elapsed,
            )
            raise
        elapsed = (time.perf_counter() - start) * 1000
        level = logging.DEBUG if request.url.path in self._NOISY_PATHS else logging.INFO
        logger.log(
            level,
            "%s %s -> %d (%.1fms)",
            request.method,
            request.url.path,
            response.status_code,
            elapsed,
        )
        return response


logger = logging.getLogger(__name__)
