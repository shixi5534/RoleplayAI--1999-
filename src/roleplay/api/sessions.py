"""会话历史恢复 API（需求 2：对话历史持久化 + 会话中断/重启后无缝恢复）。

- GET /api/sessions/{session_id}/history  返回该会话的全部历史（角色轮次），
  前端启动时拉取以恢复上下文显示。
"""
from fastapi import APIRouter, Depends, HTTPException

from ..core.session_memory import SessionMemory
from .deps import get_orchestrator_dep

router = APIRouter(prefix="/api/sessions", tags=["sessions"])


@router.get("/{session_id}/history")
async def session_history(
    session_id: str,
    orch=Depends(get_orchestrator_dep),
):
    mem: SessionMemory | None = getattr(orch, "_session_memory", None)
    if mem is None:
        raise HTTPException(status_code=404, detail="未启用会话记忆")
    history = mem.get_history(session_id)
    if not history:
        return {"session_id": session_id, "history": []}
    return {"session_id": session_id, "history": history}
