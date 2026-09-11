"""知识库 / 联网 RAG API（需求 3 + 联网 + 多格式导入 + 文档级管理）。

- POST /api/knowledge/web-ingest  联网检索并切块入库，返回来源与切块数
- POST /api/knowledge/ingest       多格式资料导入（file/url/sqlite/directory）
- GET  /api/knowledge/search       按 query 检索知识库（调试 / 前端可展示来源）
- GET  /api/knowledge/stats        各命名空间条目数
- GET  /api/knowledge/documents    按 doc_id 聚合的文档列表（文档级管理）
- DELETE /api/knowledge/documents/{doc_id}  删除整篇文档
- GET  /api/knowledge/chunks       某文档的知识块预览
- POST /api/knowledge/upload       multipart 文件上传导入（浏览器拖拽上传）
- GET  /api/knowledge/plot-graph/stats   剧情图谱统计（独立于 lore 向量库）
- GET  /api/knowledge/plot-graph/search  剧情图谱检索调试（实体链接 + PPR + 词法）
"""
from __future__ import annotations

import asyncio
import logging
import tempfile
import time
import uuid
from pathlib import Path
from typing import Any, Literal

from pydantic import BaseModel, Field

from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File, Form

from ..core.knowledge import KnowledgeBase

logger = logging.getLogger(__name__)
from ..core.knowledge.document_ingest import (
    SUPPORTED_SUFFIXES,
    ingest_directory,
    ingest_file,
    ingest_sqlite,
    ingest_url,
    lore_namespace,
)
from ..core.knowledge.ingest import ingest_web
from ..core.knowledge.web_search import WebSearchPort
from .deps import (
    get_knowledge_base_dep,
    get_settings_dep,
    get_web_search_dep,
)
from .ratelimit import rate_limit

router = APIRouter(prefix="/api/knowledge", tags=["knowledge"])


class WebIngestRequest(BaseModel):
    query: str = Field(..., min_length=1, description="联网检索并入库的查询词")
    max_results: int | None = Field(None, ge=1, le=20)


class IngestRequest(BaseModel):
    type: Literal["file", "url", "sqlite", "directory"]
    path: str | None = None
    url: str | None = None
    namespace: str | None = None
    character_id: str | None = None
    table: str | None = None
    query: str | None = None


def _ns_or_default(namespace: str | None, character_id: str | None = None) -> str:
    """命名空间归一：显式传参优先，否则角色映射，否则默认 docs。"""
    if character_id:
        return lore_namespace(character_id)
    return (namespace or "").strip() or "docs"


async def _list_items_safe(kb: KnowledgeBase, ns: str) -> list[dict]:
    """list_items 是同步 IO，卸载到线程池（与 asearch 一致）。"""
    return await asyncio.to_thread(kb.list_items, ns)


@router.post("/web-ingest")
async def web_ingest(
    body: WebIngestRequest,
    kb: KnowledgeBase = Depends(get_knowledge_base_dep),
    web: WebSearchPort = Depends(get_web_search_dep),
    settings=Depends(get_settings_dep),
    _: None = Depends(rate_limit),
):
    if not settings.enable_url_ingest:
        raise HTTPException(
            status_code=403, detail="联网导入已禁用（enable_url_ingest=false）"
        )
    max_results = body.max_results or settings.web_max_results
    result = await ingest_web(
        kb,
        web,
        body.query,
        max_results=max_results,
        fetch_content=settings.web_fetch_content,
        chunk_size=settings.chunk_size,
    )
    return result


@router.post("/ingest")
async def ingest(
    body: IngestRequest,
    kb: KnowledgeBase = Depends(get_knowledge_base_dep),
    settings=Depends(get_settings_dep),
    _: None = Depends(rate_limit),
):
    """多格式资料导入（路径收敛到 allowlist 根、URL 需 https + 主机白名单）。

    请求体：
      {"type": "file|url|sqlite|directory", "path"/"url": ...,
       "namespace": 可选, "character_id": 可选（自动映射 lore_<cid> 命名空间）,
       "table"/"query": sqlite 专用}
    """
    character_id = (body.character_id or "").strip() or None
    namespace = _ns_or_default(body.namespace, character_id)
    roots = [r.strip() for r in (settings.ingest_allowed_roots or "").split(",") if r.strip()]
    hosts = [h.strip() for h in (settings.allowed_ingest_hosts or "").split(",") if h.strip()]
    try:
        if body.type == "file":
            if not body.path:
                raise ValueError("file 类型需要提供 path")
            if not roots:
                raise ValueError("未配置允许导入的根目录（ingest_allowed_roots 为空），禁止本地文件导入")
            return await asyncio.to_thread(
                ingest_file,
                kb, body.path, namespace=namespace,
                character_id=character_id, chunk_size=settings.chunk_size,
                allowed_roots=roots,
            )
        if body.type == "url":
            if not body.url:
                raise ValueError("url 类型需要提供 url")
            # 与 /web-ingest 对齐：全局 kill-switch 关闭时禁止一切 URL 导入
            if not settings.enable_url_ingest:
                raise HTTPException(
                    status_code=403, detail="联网导入已禁用（enable_url_ingest=false）"
                )
            if not hosts:
                raise ValueError("未配置允许导入的主机（allowed_ingest_hosts 为空）")
            return await asyncio.to_thread(
                ingest_url,
                kb, body.url, namespace=namespace,
                character_id=character_id, chunk_size=settings.chunk_size,
                allowed_hosts=hosts,
            )
        if body.type == "sqlite":
            if not body.path:
                raise ValueError("sqlite 类型需要提供 path")
            if not roots:
                raise ValueError("未配置允许导入的根目录（ingest_allowed_roots 为空），禁止本地文件导入")
            return await asyncio.to_thread(
                ingest_sqlite,
                kb, body.path, table=body.table,
                query=body.query, namespace=namespace,
                character_id=character_id, allowed_roots=roots,
            )
        if body.type == "directory":
            if not body.path:
                raise ValueError("directory 类型需要提供 path")
            if not roots:
                raise ValueError("未配置允许导入的根目录（ingest_allowed_roots 为空），禁止本地文件导入")
            return await asyncio.to_thread(
                ingest_directory,
                kb, body.path, namespace=namespace,
                character_id=character_id, chunk_size=settings.chunk_size,
                allowed_roots=roots,
            )
        raise HTTPException(
            status_code=422, detail="type 必须是 file/url/sqlite/directory 之一"
        )
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@router.get("/search")
async def search(
    q: str = Query(..., min_length=1),
    top_k: int = Query(3, ge=1, le=20),
    ns: str | None = Query(None, description="逗号分隔的命名空间过滤，如 lore_wu_ming_zhe,events"),
    hybrid: bool = Query(True, description="稠密向量 + BM25 稀疏混合重排"),
    kb: KnowledgeBase = Depends(get_knowledge_base_dep),
    _: None = Depends(rate_limit),
):
    namespaces = [x.strip() for x in ns.split(",") if x.strip()] if ns else None
    chunks = await kb.asearch(q, top_k=top_k, namespaces=namespaces, hybrid=hybrid)
    return {
        "query": q,
        "hybrid": hybrid,
        "results": [
            {
                "text": c.text,
                "score": c.score,
                "namespace": c.metadata.get("namespace"),
                "meta": c.metadata,
            }
            for c in chunks
        ],
    }


@router.get("/stats")
async def stats(
    kb: KnowledgeBase = Depends(get_knowledge_base_dep),
):
    return {"counts": kb.count()}


# ────────────────────── 剧情图谱（PlotGraph，独立于 lore 向量 RAG） ──────────────────────


def _plot_registry(settings):
    """按当前配置构建剧情图谱注册表（只读自己的两个文件，不触碰知识库）。"""
    from ..core.knowledge.factory import build_plot_registry

    return build_plot_registry(settings)


@router.get("/plot-graph/stats")
async def plot_graph_stats(
    character_id: str | None = Query(None),
    settings=Depends(get_settings_dep),
    _: None = Depends(rate_limit),
):
    """剧情语料 / 剧情图谱统计（未构建时返回 exists=False，不报错）。"""
    reg = _plot_registry(settings)
    info = await asyncio.to_thread(reg.peek, character_id)
    info["enabled"] = bool(getattr(settings, "plot_graph_enabled", False))
    return info


# ────────────────────── lore 知识图谱（GraphRAG 第三路检索） ──────────────────────


def _graph_registry(settings, kb):
    """按当前配置构建 lore 图谱注册表（只读自己的 graph_<cid>.json）。"""
    from ..core.knowledge.factory import build_graph_registry

    return build_graph_registry(settings, kb)


@router.get("/graph/stats")
async def graph_stats(
    character_id: str | None = Query(None),
    kb: KnowledgeBase = Depends(get_knowledge_base_dep),
    settings=Depends(get_settings_dep),
    _: None = Depends(rate_limit),
):
    """lore 图谱统计（未构建时 exists=False，不报错）。"""
    reg = _graph_registry(settings, kb)
    info = await asyncio.to_thread(reg.peek, character_id)
    info["enabled"] = bool(getattr(settings, "graph_enabled", False))
    return info


@router.get("/graph/entity")
async def graph_entity(
    q: str = Query(..., min_length=1, max_length=200, description="实体名 / 别名 / 查询"),
    character_id: str | None = Query(None),
    hops: int = Query(1, ge=1, le=3),
    kb: KnowledgeBase = Depends(get_knowledge_base_dep),
    settings=Depends(get_settings_dep),
    _: None = Depends(rate_limit),
):
    """实体邻域子图（人工校验抽取质量）：实体链接 → 邻域边列表。"""
    reg = _graph_registry(settings, kb)

    def _run() -> dict | None:
        searcher = reg.get(character_id)
        if searcher is None:
            return None
        store = searcher.store
        seeds = searcher.link(q)
        nodes: list[dict] = []
        edges: list[dict] = []
        seen_e: set[tuple] = set()
        frontier = set(seeds)
        visited = set(seeds)
        for _ in range(hops):
            nxt: set[str] = set()
            for eid in frontier:
                for e, _dir in store.neighbors(eid):
                    key = (e.get("src"), e.get("dst"), e.get("relation"))
                    if key not in seen_e:
                        seen_e.add(key)
                        edges.append(
                            {
                                "src": searcher._name_of(str(e.get("src"))),
                                "dst": searcher._name_of(str(e.get("dst"))),
                                "relation": e.get("relation"),
                                "confidence": e.get("confidence"),
                                "evidence": len(e.get("evidence") or []),
                            }
                        )
                    for n in (str(e.get("src")), str(e.get("dst"))):
                        if n not in visited:
                            visited.add(n)
                            nxt.add(n)
            frontier = nxt
        for eid in visited:
            ent = store.get_entity(eid) or {}
            nodes.append(
                {
                    "name": ent.get("name"),
                    "type": ent.get("type"),
                    "aliases": ent.get("aliases"),
                    "mentions": ent.get("mentions"),
                    "seed": eid in seeds,
                }
            )
        return {"seeds": [searcher._name_of(e) for e in seeds], "nodes": nodes, "edges": edges}

    try:
        payload = await asyncio.to_thread(_run)
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=500, detail=f"图谱邻域查询失败：{exc}") from exc
    if payload is None:
        raise HTTPException(
            status_code=404,
            detail="lore 图谱未构建，请先运行 scripts/build_graph.py --character <cid>",
        )
    return {"query": q, **payload}


@router.get("/plot-graph/search")
async def plot_graph_search(
    # max_length：不限长时，超长 query 会在 HTTP 请求行阶段被 uvicorn 拒绝，
    # 客户端拿到的是「连接被重置」而非可读的 4xx（验收 R17 实测复现）。
    # 200 字足以覆盖正常剧情提问，超出一律 422。
    q: str = Query(..., min_length=1, max_length=200),
    character_id: str | None = Query(None),
    top_k: int = Query(3, ge=1, le=20),
    settings=Depends(get_settings_dep),
    _: None = Depends(rate_limit),
):
    """剧情图谱检索调试：实体链接 → PPR → 证据块（含 via=plot_graph/plot_lexical 标记）。"""
    reg = _plot_registry(settings)

    def _run():
        retr = reg.get(character_id)
        if retr is None:
            return None
        return retr.retrieve(q, top_chunks=top_k)

    try:
        chunks = await asyncio.to_thread(_run)
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=500, detail=f"剧情图谱检索失败：{exc}") from exc
    if chunks is None:
        raise HTTPException(
            status_code=404,
            detail="剧情图谱未构建，请先运行 scripts/build_plot_graph.py --character <cid> --build-corpus",
        )
    return {
        "query": q,
        "results": [
            {
                "text": c.text,
                "score": c.score,
                "namespace": c.metadata.get("namespace"),
                "edge": c.metadata.get("edge"),
                "meta": c.metadata,
            }
            for c in chunks
        ],
    }


# ────────────────────────── 文档级管理（知识库可视化） ──────────────────────────

_LEGACY_DOC_ID = "legacy"


def _item_created_at(item: dict) -> float:
    return float(item.get("ts") or 0.0)


@router.get("/documents")
async def list_documents(
    ns: str = Query("docs", description="命名空间，如 docs / persona / lore_xxx"),
    kb: KnowledgeBase = Depends(get_knowledge_base_dep),
):
    """按 meta.doc_id 聚合的文档列表，供知识库管理界面展示。

    无 doc_id 的历史条目归入 doc_id="legacy" 的虚拟文档（title="历史数据"）。
    返回 [{doc_id, title, chunk_count, size, created_at}]，按创建时间倒序。
    """
    items = await _list_items_safe(kb, ns)
    docs: dict[str, dict] = {}
    for it in items:
        meta = it.get("meta", {})
        doc_id = meta.get("doc_id") or _LEGACY_DOC_ID
        d = docs.setdefault(
            doc_id,
            {
                "doc_id": doc_id,
                "title": "历史数据" if doc_id == _LEGACY_DOC_ID else meta.get("title") or doc_id,
                "chunk_count": 0,
                "size": 0,
                "created_at": 0.0,
                "format": meta.get("format") or "",
            },
        )
        d["chunk_count"] += 1
        d["size"] += len(it.get("text") or "")
        d["created_at"] = max(d["created_at"], _item_created_at(it))
    # 排序：创建时间倒序（无 ts 的 legacy 排最后）
    out = sorted(
        docs.values(),
        key=lambda x: (x["created_at"] == 0.0, x["created_at"]),
        reverse=True,
    )
    return {"namespace": ns, "documents": out}


@router.delete("/documents/{doc_id}")
async def delete_document(
    doc_id: str,
    ns: str = Query("docs", description="命名空间，如 docs / persona / lore_xxx"),
    kb: KnowledgeBase = Depends(get_knowledge_base_dep),
):
    """删除整篇文档（按 meta.doc_id 匹配，filter_remove 逐个移除并落盘）。"""
    if doc_id == _LEGACY_DOC_ID:

        def pred(item: dict) -> bool:
            return not item.get("meta", {}).get("doc_id")

    else:

        def pred(item: dict) -> bool:
            return item.get("meta", {}).get("doc_id") == doc_id

    removed = await asyncio.to_thread(kb.filter_remove, ns, pred)
    if removed == 0:
        raise HTTPException(status_code=404, detail=f"未找到文档 {doc_id}（ns={ns}）")
    return {"doc_id": doc_id, "namespace": ns, "removed": removed}


@router.get("/chunks")
async def list_chunks(
    ns: str = Query("docs", description="命名空间，如 docs / persona / lore_xxx"),
    doc_id: str = Query(..., description="文档标识（doc_id）"),
    kb: KnowledgeBase = Depends(get_knowledge_base_dep),
):
    """某文档的全部知识块（文本 + 元数据），供块预览弹窗展示。"""
    items = await _list_items_safe(kb, ns)
    if doc_id == _LEGACY_DOC_ID:
        filtered = [it for it in items if not it.get("meta", {}).get("doc_id")]
    else:
        filtered = [it for it in items if it.get("meta", {}).get("doc_id") == doc_id]
    if not filtered:
        raise HTTPException(status_code=404, detail=f"未找到文档 {doc_id}（ns={ns}）")
    chunks = [
        {
            "text": it.get("text", ""),
            "meta": it.get("meta", {}),
            "ts": it.get("ts"),
        }
        for it in sorted(filtered, key=_item_created_at)
    ]
    title = (
        "历史数据"
        if doc_id == _LEGACY_DOC_ID
        else (filtered[0].get("meta", {}).get("title") or doc_id)
    )
    return {"doc_id": doc_id, "namespace": ns, "title": title, "chunks": chunks}


@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    ns: str = Form("docs", description="目标命名空间"),
    character_id: str | None = Form(None, description="角色 id（可选，自动映射 lore_<cid>）"),
    kb: KnowledgeBase = Depends(get_knowledge_base_dep),
    settings=Depends(get_settings_dep),
    _: None = Depends(rate_limit),
):
    """multipart 文件上传导入（浏览器拖拽上传）。

    - 校验扩展名白名单（SUPPORTED_SUFFIXES）
    - 临时落盘 → 复用 ingest_file 管线（同款解析/分块/向量化）
    - 注入 doc_id=uuid4 供文档级管理
    - 返回 {doc_id, title, format, stored}
    """
    filename = (file.filename or "").strip()
    if not filename:
        raise HTTPException(status_code=400, detail="缺少文件名")
    suffix = Path(filename).suffix.lower()
    if suffix not in SUPPORTED_SUFFIXES:
        raise HTTPException(
            status_code=400,
            detail=f"不支持的格式 {suffix or '(无扩展名)'}，支持：{sorted(SUPPORTED_SUFFIXES)}",
        )
    namespace = _ns_or_default(ns, (character_id or "").strip() or None)
    doc_id = str(uuid.uuid4())

    # 上传大小上限（与 /voice/stt 的 25MB 同思路；64MB 覆盖绝大多数文档/PPT/PDF 场景）
    MAX_UPLOAD_BYTES = 64 * 1024 * 1024

    tmp_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            prefix="kb_upload_", suffix=suffix, delete=False
        ) as tmpf:
            # 流式写入，避免大文件占满内存；累计超限即中断并返回 413
            total = 0
            while chunk := await file.read(1024 * 1024):
                total += len(chunk)
                if total > MAX_UPLOAD_BYTES:
                    logger.warning("上传超限：%s (%d bytes)", filename, total)
                    raise HTTPException(
                        status_code=413,
                        detail=f"文件过大（上限 {MAX_UPLOAD_BYTES // (1024 * 1024)}MB）",
                    )
                tmpf.write(chunk)
            tmp_path = Path(tmpf.name)
        result = await asyncio.to_thread(
            ingest_file,
            kb, tmp_path, namespace=namespace,
            chunk_size=settings.chunk_size,
            extra_meta={"doc_id": doc_id, "uploaded_at": time.time()},
        )
        return {
            "doc_id": doc_id,
            "title": Path(filename).stem,
            "format": suffix.lstrip("."),
            "stored": result["stored"],
            "namespace": namespace,
        }
    except HTTPException:
        raise
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    finally:
        if tmp_path and tmp_path.exists():
            try:
                tmp_path.unlink()
            except OSError:  # pragma: no cover - 清理失败不影响结果
                pass
