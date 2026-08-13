"""聊天路由（接口适配层）。

职责仅限：请求校验 → 调用 Orchestrator → 响应。不含业务规则。
- POST /chat        同步返回 ChatResponse
- POST /chat/stream  SSE 流式：event: chunk / emotion / done
  （emotion 事件契约与原 rag 项目一致，前端 live2d.js 可直接对接）

安全约束：SSE error 事件透传的异常信息须经脱敏，防止 API key 等凭据泄漏到前端。
"""
import asyncio
import json
import logging

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse

from ..core.orchestrator import ChatOrchestrator
from ..errors.handlers import _safe_details
from ..models.chat import ChatClearRequest, ChatRequest, ChatResponse
from .deps import get_orchestrator_dep
from .ratelimit import rate_limit

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/chat", tags=["chat"], dependencies=[Depends(rate_limit)])


@router.post("", response_model=ChatResponse)
async def chat(
    req: ChatRequest,
    orch: ChatOrchestrator = Depends(get_orchestrator_dep),
) -> ChatResponse:
    result = await orch.run(req)
    return result.response


@router.post("/stream")
async def chat_stream(
    req: ChatRequest,
    orch: ChatOrchestrator = Depends(get_orchestrator_dep),
) -> StreamingResponse:
    async def event_gen():
        # 真流式：编排器逐 token 产出，前端按 event 实时渲染
        try:
            async for ev in orch.stream(req):
                if ev["type"] == "emotion":
                    yield (
                        "event: emotion\n"
                        f"data: {json.dumps({'emotion': ev['emotion'], 'score': ev['score']}, ensure_ascii=False)}\n\n"
                    )
                elif ev["type"] == "chunk":
                    # data 为 JSON 编码的字符串，前端 JSON.parse 还原（与历史契约一致）
                    yield f"event: chunk\ndata: {json.dumps(ev['text'], ensure_ascii=False)}\n\n"
                elif ev["type"] == "done":
                    # 末事件补齐 live2d 最终表情/动作映射，供前端 live2d.js 应用
                    yield (
                        "event: done\n"
                        f"data: {json.dumps({'follow_ups': ev['follow_ups'], 'live2d': ev['live2d']}, ensure_ascii=False)}\n\n"
                    )
        except (asyncio.CancelledError, GeneratorExit):
            # 客户端断开（断流）：优雅停止推送，记录日志，不向上抛异常
            logger.info("SSE 客户端断开，停止推送 session=%s", req.session_id)
            return
        except Exception as exc:  # noqa: BLE001
            logger.warning("SSE 推送异常：%s", exc)
            # 先发 error 事件再结束流：否则前端收不到 done 也无错误提示，
            # UI 永久卡在「生成中」状态。
            try:
                # 以 message（人类可读）为主，details 仅作补充；透传前统一脱敏
                # （防 API key/凭据泄漏到前端）
                msg = str(getattr(exc, "message", None) or exc)
                det = _safe_details(getattr(exc, "details", None) or "")
                yield (
                    "event: error\n"
                    f"data: {json.dumps({'detail': msg[:200], 'details': det}, ensure_ascii=False)}\n\n"
                )
            except Exception:  # noqa: BLE001
                pass
            return

    return StreamingResponse(event_gen(), media_type="text/event-stream")


@router.post("/clear", tags=["chat"])
async def clear_session(
    req: ChatClearRequest,
    orch: ChatOrchestrator = Depends(get_orchestrator_dep),
) -> dict:
    """清空某会话的对话记忆（角色「忘记」聊过的内容）。"""
    cleared = orch.clear_session(req.session_id)
    return {"cleared": cleared}
