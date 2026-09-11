"""联网结果入库（Web → 切块 → 嵌入 → 知识库）。

同时提供一个通用的文本切块工具，供对话/人设等其它来源复用。
"""
from __future__ import annotations

import asyncio
import logging
import re
from typing import List

import httpx

from ...config import Settings
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


_MAX_FETCH_BYTES = 2 * 1024 * 1024  # 网页正文抓取上限，防超大响应撑爆内存

# web 命名空间条目上限：联网结果无跨请求去重（同一 URL 每轮都会重新入库），
# 若无上限会无限增长（内存全量驻留 + 检索全量扫描都随之劣化）。
# 超限后按时间戳淘汰最旧条目（LRU 式），保留最近检索的内容。
_WEB_NS_MAX_ITEMS = 2000


async def _afetch_text(url: str, timeout: float = 8) -> str:
    """抓取网页正文（极简：去标签 + 去脚本样式）。仅用于联网 RAG 的更精准切块。异步。

    抓取前做私有地址深度防御（SSRF）：解析为私有/保留地址则拒绝。
    同时校验 HTTP 状态并限制响应大小，避免把 404/500 页面或超大响应写入知识库。
    """
    assert_public_url(url)
    async with httpx.AsyncClient(
        headers={"User-Agent": "Mozilla/5.0"},
        timeout=httpx.Timeout(timeout),
        follow_redirects=False,  # 禁用重定向，避免借重定向绕过 allowlist
    ) as client:
        resp = await client.get(url)
        raise_status = getattr(resp, "raise_for_status", None)
        if raise_status is not None:
            raise_status()
        if hasattr(resp, "aiter_bytes"):
            parts: list[bytes] = []
            total = 0
            async for chunk in resp.aiter_bytes():
                total += len(chunk)
                if total > _MAX_FETCH_BYTES:
                    parts.append(chunk[: _MAX_FETCH_BYTES - (total - len(chunk))])
                    break
                parts.append(chunk)
            raw = b"".join(parts).decode("utf-8", errors="replace")
        else:
            # 兼容测试/最小 Response mock（仅 text 属性）
            raw = (resp.text or "").encode("utf-8", errors="replace")[: _MAX_FETCH_BYTES].decode(
                "utf-8", errors="replace"
            )
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
    results: List[WebResult] = (
        await web_search.search(query, max_results=max_results)
    )[:max_results]
    all_chunks: List[str] = []
    all_metas: List[dict] = []
    sources: List[dict] = []
    seen_urls: set[str] = set()

    # 并发抓取正文（限流 4），避免 max_results 较大时串行抓取累积为分钟级延迟
    sem = asyncio.Semaphore(4)

    async def _fetch_body(r: WebResult) -> str:
        base = r.snippet or r.title
        if not fetch_content:
            return base
        async with sem:
            try:
                body = await _afetch_text(r.url)
            except Exception as exc:  # noqa: BLE001
                logger.debug("抓取 %s 正文失败：%s", r.url, exc)
                return base
        return body if len(body) > len(base or "") else base

    bodies = (
        await asyncio.gather(*(_fetch_body(r) for r in results))
        if results
        else []
    )
    for r, text in zip(results, bodies):
        if not r.url:
            continue
        if r.url in seen_urls:
            continue
        seen_urls.add(r.url)
        if not text or not text.strip():
            continue
        chunks = chunk_text(text, size=chunk_size)
        if not chunks:
            continue
        all_chunks.extend(chunks)
        all_metas.extend(
            {
                "url": r.url,
                "title": r.title,
                "query": query,
                "source": "web",
            }
            for _ in chunks
        )
        sources.append({"url": r.url, "title": r.title})
    # 汇总为一次批量写入：每个搜索结果一次 aadd 会反复全量序列化/落盘 web 命名空间，
    # 结果多时文件 IO 呈 O(结果数 × 已入库总量)。
    if all_chunks:
        if hasattr(kb, "aadd"):
            await kb.aadd(all_chunks, metadatas=all_metas, namespace=namespace)
        else:
            kb.add(all_chunks, metadatas=all_metas, namespace=namespace)
        # 有界增长：超限则淘汰最旧条目（先于返回，避免占用检索内存）
        await _trim_web_namespace(kb, namespace)
    stored = len(all_chunks)
    logger.info("联网入库完成：query=%r 来源=%d 切块=%d", query, len(sources), stored)
    return {"stored": stored, "sources": sources}


async def _trim_web_namespace(kb: KnowledgeBase, namespace: str) -> int:
    """web 命名空间条目超上限时，按 ts 淘汰最旧（同步 IO 卸载到线程池）。返回清理条数。"""
    try:
        def _run() -> int:
            items = kb.list_items(namespace)
            if len(items) <= _WEB_NS_MAX_ITEMS:
                return 0
            over = len(items) - _WEB_NS_MAX_ITEMS
            # 按 ts 升序（最旧在前），只删超出部分
            ordered = sorted(items, key=lambda it: float(it.get("ts") or 0.0))
            drop_ids = {it.get("id") for it in ordered[:over] if it.get("id")}

            def _pred(it: dict) -> bool:
                return it.get("id") in drop_ids

            return kb.filter_remove(namespace, _pred)

        return await asyncio.to_thread(_run)
    except Exception as exc:  # noqa: BLE001
        logger.warning("web 命名空间裁剪失败（不影响本轮入库）：%s", exc)
        return 0
