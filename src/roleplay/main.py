"""应用入口：FastAPI 应用工厂 + 生命周期 + 路由装配。

启动：uvicorn roleplay.main:app --reload --port 8000
"""
import asyncio
import logging
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, PlainTextResponse

from .api.chat import router as chat_router
from .api.desktop_pet import router as desktop_pet_router
from .api.characters import router as characters_router
from .api.knowledge import router as knowledge_router
from .api.llm_config import router as llm_config_router
from .api.sessions import router as sessions_router
from .api.voice import router as voice_router
from .api.deps import build_orchestrator
from .core.knowledge import build_services
from .channels.qq_onebot import start_qq_channel
from .config import get_settings
from .errors.handlers import register_exception_handlers
from .middleware import RequestLoggingMiddleware, SecurityHeadersMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

logger = logging.getLogger(__name__)


def _cors_allow_origins(settings) -> tuple[list[str], bool]:
    """解析 CORS 配置。

    规范约束：Access-Control-Allow-Origin: * 与 Access-Control-Allow-Credentials: true
    是非法组合（浏览器拒绝，部分框架静默无视即变可利用）。因此：
    - 通配 '*' → 返回 ["*"] 且 credentials=False；
    - 显式源列表 → 返回该列表且 credentials=True（Starlette 会按匹配源回写并加 Vary: Origin）。
    """
    raw = (settings.cors_origins or "").strip()
    if raw in ("", "*"):
        return ["*"], False
    origins = [o.strip() for o in raw.split(",") if o.strip()]
    return origins, True


class NoCacheMiddleware(BaseHTTPMiddleware):
    """本地开发用：禁止浏览器缓存前端静态资源。

    否则改了 JS 后浏览器仍按 304 复用旧缓存，导致“明明改了却没生效”。
    仅对前端资源生效，不影响 /chat/stream 等业务接口。
    """

    _NO_CACHE_SUFFIXES = (".html", ".js", ".css", ".json", ".map")
    _NO_CACHE_PREFIXES = ("/assets/", "/js/")

    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        path = request.url.path
        if (
            path in ("/", "/index.html")
            or path.endswith(self._NO_CACHE_SUFFIXES)
            or path.startswith(self._NO_CACHE_PREFIXES)
        ):
            response.headers["Cache-Control"] = "no-store, max-age=0"
            try:
                response.headers.delete("etag")
                response.headers.delete("last-modified")
            except Exception:
                pass
        return response


@asynccontextmanager
async def lifespan(app: FastAPI):
    # 启动期：预热配置（校验 env / .env）+ 基础日志
    settings = get_settings()
    logging.basicConfig(
        level=logging.DEBUG if settings.debug else logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )
    # 装配重型依赖并存入 app.state，供路由通过 Depends 注入
    services = build_services(settings)
    app.state.services = services
    app.state.orchestrator = build_orchestrator(settings, services=services)
    logger.info("RoleplayAI 启动，provider=%s", settings.llm_provider)
    # QQ 渠道（NapCatQQ / OneBot v11）：默认关闭，开启后独立任务运行，复用 Orchestrator
    if settings.qq_enabled:
        app.state.qq_task = asyncio.create_task(
            start_qq_channel(app), name="qq-channel"
        )
        logger.info("QQ 渠道任务已启动（NapCat: %s）", settings.qq_napcat_ws_url)
    yield
    # 关闭期：释放 LLM 客户端连接池（若有），并清空构建缓存
    orch = getattr(app.state, "orchestrator", None)
    if orch is not None:
        aclose = getattr(orch._llm, "aclose", None)
        if aclose:
            try:
                await aclose()
            except Exception as exc:  # noqa: BLE001
                logger.warning("关闭 LLM 客户端时出错：%s", exc)
    # 释放 factory 缓存的全局 LLM 客户端（与注入的 _llm 可能同一实例，幂等）
    from .core.llm.factory import aclose_global_llm
    try:
        await aclose_global_llm()
    except Exception as exc:  # noqa: BLE001
        logger.warning("关闭全局 LLM 缓存时出错：%s", exc)
    # 释放知识层资源（Ollama 嵌入器 AsyncClient 等）
    services = getattr(app.state, "services", None)
    if services is not None:
        aclose_services = getattr(services, "aclose", None)
        if aclose_services:
            try:
                await aclose_services()
            except Exception as exc:  # noqa: BLE001
                logger.warning("关闭知识层资源时出错：%s", exc)
    logger.info("RoleplayAI 已关闭")
    # 关闭 QQ 渠道任务（若存在）：取消并等待优雅退出（断开 WS）
    qq_task = getattr(app.state, "qq_task", None)
    if qq_task is not None:
        qq_task.cancel()
        try:
            await qq_task
        except (asyncio.CancelledError, Exception):  # noqa: BLE001
            pass


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(
        title=settings.app_name,
        version="0.1.0",
        lifespan=lifespan,
        description=(
            "角色扮演 AI 整合服务：RAG 检索增强 + 情感编排 + Live2D 表现层对接。"
            "提供 /chat（同步）与 /chat/stream（SSE 流式）两类对话接口，"
            "以及 /api/knowledge 知识库管理、/api/characters 多角色人设等。\n\n"
            "SSE 事件契约：emotion → chunk* → done（done 含 follow_ups 与 live2d 映射）。"
        ),
    )

    # CORS：支持前后端分离部署。通配 '*' 不带凭据；显式源列表才带凭据。
    allow_origins, allow_credentials = _cors_allow_origins(settings)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=allow_origins,
        allow_credentials=allow_credentials,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    register_exception_handlers(app)
    app.add_middleware(SecurityHeadersMiddleware)
    app.add_middleware(RequestLoggingMiddleware)
    if settings.static_no_cache:
        # 本地开发默认禁用前端缓存；生产部署可设 ROLEPLAY_STATIC_NO_CACHE=false
        app.add_middleware(NoCacheMiddleware)
    app.include_router(chat_router)
    app.include_router(characters_router)
    app.include_router(knowledge_router)
    app.include_router(llm_config_router)
    app.include_router(sessions_router)
    app.include_router(voice_router)
    app.include_router(desktop_pet_router)

    @app.get("/health", tags=["meta"])
    async def health() -> dict:
        return {"status": "ok"}

    # 本地说明文档：让安装引导可以直接打开仓库内 docs 文件（避免跳到外部 GitHub）。
    @app.get("/docs/DESKTOP_PET_DESIGN.md", include_in_schema=False)
    async def desktop_pet_docs():
        docs_file = Path(__file__).resolve().parent.parent.parent / "docs" / "DESKTOP_PET_DESIGN.md"
        if docs_file.is_file():
            return FileResponse(str(docs_file), media_type="text/markdown; charset=utf-8")
        return PlainTextResponse("未找到本地说明文件", status_code=404)

    # 前端静态托管：同源访问，免跨域与额外静态服务器。
    # 挂载在 API 路由之后，/chat 等接口优先匹配。
    frontend_dir = Path(__file__).resolve().parent.parent.parent / "frontend"
    if frontend_dir.is_dir():
        app.mount("/", StaticFiles(directory=str(frontend_dir), html=True), name="frontend")

    return app


app = create_app()
