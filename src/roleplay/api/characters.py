"""角色人设管理 API（需求 1 + 5：人设管理 + 多角色切换）。

- GET  /api/characters            列出全部角色（含 active 标记）
- GET  /api/characters/active      当前激活角色
- GET  /api/characters/{id}        获取单个角色完整 JSON
- POST /api/characters             新建角色
- PUT  /api/characters/{id}        更新角色（仅覆盖提供的字段）
- POST /api/characters/{id}/activate 切换为当前激活角色
- DELETE /api/characters/{id}      删除角色（至少保留一个）
"""
import asyncio

from fastapi import APIRouter, Depends, HTTPException

from ..core.knowledge import CharacterStore
from ..models.character import CharacterUpsert
from .deps import get_character_store_dep, get_knowledge_base_dep

router = APIRouter(prefix="/api/characters", tags=["characters"])


@router.get("")
async def list_characters(
    store: CharacterStore = Depends(get_character_store_dep),
):
    return {"characters": store.list(), "active_id": store.get_active_id()}


@router.get("/active")
async def active_character(
    store: CharacterStore = Depends(get_character_store_dep),
):
    cid = store.get_active_id()
    card = store.get_active()
    return {"id": cid, "name": card.name if card else None}


@router.get("/{cid}")
async def get_character(
    cid: str,
    store: CharacterStore = Depends(get_character_store_dep),
):
    card = store.get(cid)
    if card is None:
        raise HTTPException(status_code=404, detail="角色不存在")
    return {"id": cid, "card": card.model_dump()}


@router.post("")
async def create_character(
    payload: CharacterUpsert,
    store: CharacterStore = Depends(get_character_store_dep),
    kb=Depends(get_knowledge_base_dep),
):
    data = {k: v for k, v in payload.model_dump().items() if v is not None}
    if not data.get("name"):
        raise HTTPException(status_code=422, detail="name 不能为空")
    cid = store.create(data)
    # 人设嵌入属同步 CPU/IO（Ollama 场景会经线程池 .result() 阻塞），
    # 卸载到线程池避免阻塞事件循环（否则 /chat 等并发请求全部卡住）
    await asyncio.to_thread(store.sync_persona_to_kb, kb)
    return {"id": cid, "ok": True}


@router.put("/{cid}")
async def update_character(
    cid: str,
    payload: CharacterUpsert,
    store: CharacterStore = Depends(get_character_store_dep),
    kb=Depends(get_knowledge_base_dep),
):
    if store.get(cid) is None:
        raise HTTPException(status_code=404, detail="角色不存在")
    data = {k: v for k, v in payload.model_dump().items() if v is not None}
    ok = store.update(cid, data)
    await asyncio.to_thread(store.sync_persona_to_kb, kb)
    return {"ok": ok}


@router.post("/{cid}/activate")
async def activate_character(
    cid: str,
    store: CharacterStore = Depends(get_character_store_dep),
):
    if store.get(cid) is None:
        raise HTTPException(status_code=404, detail="角色不存在")
    ok = store.set_active(cid)
    return {"ok": ok, "active_id": store.get_active_id()}


@router.delete("/{cid}")
async def delete_character(
    cid: str,
    store: CharacterStore = Depends(get_character_store_dep),
    kb=Depends(get_knowledge_base_dep),
):
    if store.get(cid) is None:
        raise HTTPException(status_code=404, detail="角色不存在")
    try:
        ok = store.delete(cid)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    await asyncio.to_thread(store.sync_persona_to_kb, kb)
    return {"ok": ok, "active_id": store.get_active_id()}
