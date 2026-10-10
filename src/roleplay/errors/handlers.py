"""FastAPI 全局异常处理器：将异常统一转换为 JSON 响应。

安全约束：任何情况下不得把敏感凭据（API key / token / 密码）透传给前端，
也不得记入日志。details 序列化前统一做敏感字段脱敏清洗。
"""
import json
import re

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from . import RoleplayError

# 敏感字段名（dict 键名命中即脱敏）+ 常见凭据形态（含 "key"/"token"/"secret"/"password"）
_SENSITIVE_KEYS = {"api_key", "apikey", "token", "secret", "password", "passwd", "authorization", "bearer"}
_SENSITIVE_VALUE_RE = re.compile(
    r"(Bearer\s+[A-Za-z0-9._~+/-]+=*|sk-[A-Za-z0-9-]+|"
    r"(?i:api[_-]?key|token|secret|password|passwd)[\"':=\s]+[^\s,}\"']+)",
    re.IGNORECASE,
)
# 超过深度上限的层级统一折叠为该占位符（S2b：绝不原样输出原始内容）
_DEPTH_LIMIT_PLACEHOLDER = "[深度超限已隐藏]"


def _sanitize(value: object, *, depth: int = 0) -> object:
    """递归脱敏：dict 键名敏感或值含凭据形态时替换为 '***'。

    - 字符串：正则扫描常见凭据形态（Authorization 头、sk- 开头的 API key 等）；
    - dict：敏感键名的值直接打码，其余键递归处理；
    - list：逐元素递归。
    - 超深嵌套（depth > 10）：**降级为打码，绝不原样输出**。

    S2b 修复背景：原先 ``depth > 10`` 时直接 ``return str(value)[:200]``，
    即「深度超限 = 跳过脱敏」——实测 12 层嵌套的 ``{"api_key": "sk-..."}``
    会原样穿透到错误响应/日志。现在超限层降级为固定占位符 ``"[深度超限已隐藏]"``：
    既不泄漏任何值，也保留「此处有嵌套」的结构信息；字典仍按键名判定，
    敏感键（api_key 等）在任何深度都只输出 ``***``。
    """
    if depth > 10:
        # 降级策略（不再原样输出内容）：
        # 1) 标量/容器一律折叠为固定占位符——不保留任何原始字符，
        #    深层 api_key 无论藏在哪一层都无法穿透；
        # 2) 若该层恰是 dict，先按**键名**打码，保证敏感键位可见且值为 ***。
        if isinstance(value, dict):
            return {
                str(k): ("***" if str(k).lower() in _SENSITIVE_KEYS else _DEPTH_LIMIT_PLACEHOLDER)
                for k in value
            }
        return _DEPTH_LIMIT_PLACEHOLDER
    if isinstance(value, dict):
        return {
            k: ("***" if str(k).lower() in _SENSITIVE_KEYS else _sanitize(v, depth=depth + 1))
            for k, v in value.items()
        }
    if isinstance(value, (list, tuple)):
        return [_sanitize(v, depth=depth + 1) for v in value]
    if isinstance(value, str):
        if _SENSITIVE_VALUE_RE.search(value):
            return _SENSITIVE_VALUE_RE.sub("***", value)
        return value
    return value


def _safe_details(details: object) -> object:
    """把 details 序列化前做安全清洗（脱敏 + 截断，防信息泄漏与响应膨胀）。

    - str：脱敏后截断到 500 字符；
    - dict/list：脱敏后按 JSON 序列化截断（保留结构化信息）。
    """
    cleaned = _sanitize(details)
    if cleaned is None:
        return None
    if isinstance(cleaned, str):
        return cleaned[:500]
    # dict/list 等结构化对象：统一截断到 500 字符，避免超长错误体
    return json.dumps(cleaned, ensure_ascii=False)[:500]


def register_exception_handlers(app: FastAPI) -> None:
    """注册统一异常处理器（在 app 工厂中调用一次）。"""

    @app.exception_handler(RoleplayError)
    async def _handle_roleplay(_: Request, exc: RoleplayError) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": {
                    "code": exc.code,
                    "message": exc.message,
                    "details": _safe_details(exc.details),
                }
            },
        )

    @app.exception_handler(HTTPException)
    async def _handle_http(_: Request, exc: HTTPException) -> JSONResponse:
        # S2a 修复：透传 exc.headers，保留 Retry-After 等协议头。
        # 此前丢弃 headers，导致限流 429（rate_limit 显式带 Retry-After）的退避
        # 提示消失，客户端只能盲目重试（放大压垮服务）。
        # 安全：仅透传框架/业务显式声明的头，不反射请求头，无凭据泄漏面。
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": {
                    "code": "http_error",
                    "message": str(exc.detail),
                    "details": None,
                }
            },
            headers=exc.headers,
        )

    @app.exception_handler(RequestValidationError)
    async def _handle_validation(_: Request, exc: RequestValidationError) -> JSONResponse:
        # 请求体/参数校验失败也走统一错误结构，前端无需区分异常类型。
        # 注意：exc.errors() 的 ctx 可能携带原始异常实例（如 field_validator
        # 抛出的 ValueError），不可直接 JSON 序列化，需抽取安全字段。
        safe_details = [
            {
                "loc": list(e.get("loc", [])),
                "msg": e.get("msg"),
                "type": e.get("type"),
            }
            for e in exc.errors()
        ]
        return JSONResponse(
            status_code=422,
            content={
                "error": {
                    "code": "validation_error",
                    "message": "请求参数校验失败",
                    "details": safe_details,
                }
            },
        )
