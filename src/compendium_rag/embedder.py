# -*- coding: utf-8 -*-
"""嵌入客户端（本地 Ollama bge-m3）。

为什么嵌入留在本地而抽取走云端：云端网关（``127.0.0.1:7863``）实测**不提供**
``/v1/embeddings``（404），而本地 Ollama 已有 ``bge-m3``（1024 维，中文强）。
图谱的**语义**部分（实体链接、向量召回）用本地嵌入，语言理解与关系抽取全走云端。
"""
from __future__ import annotations

import asyncio
import logging

import httpx

logger = logging.getLogger(__name__)


class EmbedError(RuntimeError):
    pass


class OllamaEmbedder:
    """Ollama /api/embed 批量嵌入（异步，分批防超时）。"""

    BATCH = 16

    def __init__(self, base_url: str, model: str, timeout: float = 120.0,
                 concurrency: int = 4) -> None:
        self.base_url = base_url.rstrip("/")
        if self.base_url.endswith("/v1"):
            self.base_url = self.base_url[:-3]
        self.model = model
        self.timeout = timeout
        self.concurrency = max(1, concurrency)
        self._client: httpx.AsyncClient | None = None
        self._dim: int | None = None

    async def __aenter__(self) -> "OllamaEmbedder":
        self._client = httpx.AsyncClient(timeout=self.timeout)
        return self

    async def __aexit__(self, *exc) -> None:
        if self._client is not None:
            await self._client.aclose()
            self._client = None

    async def _one_batch(self, batch: list[str]) -> list[list[float]]:
        assert self._client is not None
        r = await self._client.post(self.base_url + "/api/embed",
                                    json={"model": self.model, "input": batch})
        if r.status_code != 200:
            raise EmbedError(f"HTTP {r.status_code}: {r.text[:200]}")
        data = r.json()
        embs = data.get("embeddings") or []
        if len(embs) != len(batch):
            raise EmbedError(f"返回数量不匹配：{len(embs)} != {len(batch)}")
        return embs

    async def embed(self, texts: list[str]) -> list[list[float]]:
        """批量嵌入（保序）。"""
        if not texts:
            return []
        batches = [texts[i:i + self.BATCH] for i in range(0, len(texts), self.BATCH)]
        sem = asyncio.Semaphore(self.concurrency)

        async def run(b: list[str]) -> list[list[float]]:
            async with sem:
                for attempt in range(3):
                    try:
                        return await self._one_batch(b)
                    except Exception as exc:  # noqa: BLE001
                        if attempt == 2:
                            raise
                        logger.warning("嵌入重试 %d: %s", attempt + 1, exc)
                        await asyncio.sleep(1.0 * (attempt + 1))
                return []

        results = await asyncio.gather(*(run(b) for b in batches))
        out: list[list[float]] = []
        done = 0
        for r in results:
            out.extend(r)
            done += len(r)
            if done % (self.BATCH * 16) < self.BATCH:
                logger.info("  嵌入进度 %d/%d", done, len(texts))
        if out:
            self._dim = len(out[0])
        return out

    async def embed_one(self, text: str) -> list[float]:
        return (await self.embed([text]))[0]

    async def probe(self) -> int:
        v = await self.embed_one("维度探测")
        self._dim = len(v)
        return self._dim

    @property
    def dim(self) -> int:
        return self._dim or 0


def cosine(a: list[float], b: list[float]) -> float:
    """余弦相似度（嵌入已归一化时等同点积，这里仍做完整计算以防万一）。"""
    if not a or not b or len(a) != len(b):
        return 0.0
    dot = na = nb = 0.0
    for x, y in zip(a, b):
        dot += x * y
        na += x * x
        nb += y * y
    if na <= 0 or nb <= 0:
        return 0.0
    return dot / ((na ** 0.5) * (nb ** 0.5))
