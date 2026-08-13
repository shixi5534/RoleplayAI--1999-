"""联网结果入库（Web → 切块 → 嵌入 → 知识库）。

同时提供一个通用的文本切块工具，供对话/人设等其它来源复用。
"""
from __future__ import annotations

import asyncio
import logging
import re
from typing import List

import httpx

from ...config import Settings, get_settings
from .security_utils import assert_public_url
from .web_search import WebResult, WebSearchPort
from .vector_store import KnowledgeBase

logger = logging.getLogger(__name__)

_split_re = re.compile(r"(?<=[。！？!?\n])|\s+")


def chunk_text(text: str, size: int = 600, overlap: int = 80) -> List[str]:
    """按句子/空白切分为约 size 字符的块，相邻块保留 overlap 重叠以维持上下文。"""
    text = (text or "").strip()
    if not text:
        return []
    pieces: List[str] = []
    # 先按标点/换行粗切，避免把长句劈断
    segs = [s.strip() for s in _split_re.split(text) if s and s.strip()]
    buf = ""
    for seg in segs:
        if len(buf) + len(seg) <= size:
            buf = (buf + " " + seg).strip()
        else:
            if buf:
                pieces.append(buf)
            buf = seg
    if buf:
        pieces.append(buf)
    if overlap <= 0 or len(pieces) <= 1:
        return pieces
    # 重叠衔接：把当前块头部 overlap 字符桥接到上一块末尾，作为跨块上下文桥。
    # 注意：当前块正文必须完整保留（原实现用 p[-overlap:] 覆盖后 continue，
    # 导致除第一块外的正文大面积丢失——这是 P0 数据完整性 bug；
    # 后续修复曾误把当前块「尾部」接到上一块末尾，造成尾部字符冗余重复）。
    merged: List[str] = []
    for p in pieces:
        if merged:
            prev = merged[-1]
            if len(prev) < size:
                merged[-1] = (prev + " " + p[:overlap]).strip()
        merged.append(p)
    return merged


async def _afetch_text(url: str, timeout: float = 8) -> str:
    """抓取网页正文（极简：去标签 + 去脚本样式）。仅用于联网 RAG 的更精准切块。异步。

    抓取前做私有地址深度防御（SSRF）：解析为私有/保留地址则拒绝。
    """
    assert_public_url(url)
    async with httpx.AsyncClient(
        headers={"User-Agent": "Mozilla/5.0"},
        timeout=httpx.Timeout(timeout),
        follow_redirects=False,  # 禁用重定向，避免借重定向绕过 allowlist
    ) as client:
        resp = await client.get(url)
        raw = resp.text
    raw = re.sub(r"<script[\s\S]*?</script>", " ", raw, flags=re.I)
    raw = re.sub(r"<style[\s\S]*?</style>", " ", raw, flags=re.I)
    raw = re.sub(r"<[^>]+>", " ", raw)
    raw = re.sub(r"&[a-z]+;", " ", raw)
    raw = re.sub(r"\s+", " ", raw)
    return raw.strip()


def _fetch_text(url: str, timeout: float = 8) -> str:
    """同步桥接：离线/脚本用，内部经事件循环运行器调用 _afetch_text。"""
    return asyncio.run(_afetch_text(url, timeout=timeout))


async def ingest_web(
    kb: KnowledgeBase,
    web_search: WebSearchPort,
    query: str,
    max_results: int = 5,
    fetch_content: bool = False,
    chunk_size: int = 600,
    namespace: str = "web",
    settings: Settings | None = None,
) -> dict:
    """联网检索并入库，返回统计与来源列表。异步。"""
    s = settings or get_settings()
    results: List[WebResult] = await web_search.search(query, max_results=max_results)
    stored = 0
    sources: List[dict] = []
    for r in results:
        if not r.url:
            continue
        text = r.snippet or r.title
        if fetch_content:
            try:
                body = await _afetch_text(r.url)
                if len(body) > len(text or ""):
                    text = body
            except Exception as exc:  # noqa: BLE001
                logger.debug("抓取 %s 正文失败：%s", r.url, exc)
        if not text or not text.strip():
            continue
        chunks = chunk_text(text, size=chunk_size)
        metas = [
            {
                "url": r.url,
                "title": r.title,
                "query": query,
                "source": "web",
            }
            for _ in chunks
        ]
        if hasattr(kb, "aadd"):
            await kb.aadd(chunks, metadatas=metas, namespace=namespace)
        else:
            kb.add(chunks, metadatas=metas, namespace=namespace)
        stored += len(chunks)
        sources.append({"url": r.url, "title": r.title})
    logger.info("联网入库完成：query=%r 来源=%d 切块=%d", query, len(sources), stored)
    return {"stored": stored, "sources": sources}
