"""文本嵌入端口。

- OllamaEmbedder：调用本地 Ollama 的 /api/embed（如 nomic-embed-text），真实语义向量。
- HashingEmbedder：零依赖的特征哈希兜底，Ollama 不可用时保证系统仍可运行（检索质量较低）。

build_embedder 在启动时探测 Ollama 可用性，失败自动回退 hashing，保证单进程内向量一致。

并发模型（修复「同步 IO 阻塞事件循环」）：
- 异步路径（请求处理期）：使用 httpx.AsyncClient，提供 async aembed / aembed_query，
  由 KnowledgeBase.asearch / aadd 在事件循环内 await 调用，不阻塞事件循环。
- 同步路径（离线脚本 / 测试）：保留同步 embed / embed_query，内部通过事件循环运行器
  （无运行循环时 asyncio.run；已有运行循环时丢到独立线程）桥接同一套 AsyncClient 实现，
  避免重复实现两套 HTTP 逻辑。
"""
from __future__ import annotations

import asyncio
import concurrent.futures
import hashlib
import logging
import re
import threading
from abc import ABC, abstractmethod
from typing import List

import httpx

from ...config import Settings, get_settings

logger = logging.getLogger(__name__)


def _run_async(coro):
    """在「无运行循环」时直接 asyncio.run；在「已有运行循环」（如被同步调用卷入
    异步请求处理）时，丢到独立线程里跑一个全新事件循环，避免『事件循环已运行』错误。"""
    try:
        running = asyncio.get_running_loop()
    except RuntimeError:
        running = None
    if running is None:
        return asyncio.run(coro)
    with concurrent.futures.ThreadPoolExecutor(max_workers=1) as ex:
        return ex.submit(lambda: asyncio.run(coro)).result()


class EmbedderPort(ABC):
    @abstractmethod
    def embed(self, texts: List[str]) -> List[List[float]]:
        """批量将文本（文档侧）转为向量（同步路径：离线/测试）。"""

    async def aembed(self, texts: List[str]) -> List[List[float]]:
        """异步批量嵌入（请求路径，避免阻塞事件循环）。默认回退到线程池跑同步实现。"""
        return await asyncio.to_thread(self.embed, texts)

    def embed_query(self, text: str) -> List[float]:
        """查询侧嵌入（同步）。非对称检索模型（如 nomic）可覆写加任务前缀；
        默认与文档侧一致，保证对称模型/哈希兜底行为不变。"""
        return self.embed([text])[0]

    async def aembed_query(self, text: str) -> List[float]:
        """查询侧嵌入（异步）。默认回退到线程池跑同步实现。"""
        return (await self.aembed([text]))[0]

    @property
    @abstractmethod
    def dim(self) -> int:
        """向量维度。"""

    @property
    def name(self) -> str:
        return "embedder"


class HashingEmbedder(EmbedderPort):
    """特征哈希向量（定长、确定性、零依赖）。离线兜底用。"""

    _TOKEN = re.compile(r"[A-Za-z0-9_]+|[一-鿿]")

    def __init__(self, dim: int | None = None) -> None:
        # 维度默认取自配置 embed_dim（768）；显式传入时优先（测试常用小维度加速）。
        self._dim = dim if dim is not None else get_settings().embed_dim

    def embed(self, texts: List[str]) -> List[List[float]]:
        out: List[List[float]] = []
        for t in texts:
            vec = [0.0] * self._dim
            toks = self._TOKEN.findall((t or "").lower())
            if not toks:
                toks = [t or " "]
            for tok in toks:
                h = int(hashlib.md5(tok.encode("utf-8")).hexdigest(), 16)
                idx = h % self._dim
                vec[idx] += 1.0
            norm = sum(v * v for v in vec) ** 0.5 or 1.0
            out.append([v / norm for v in vec])
        return out

    @property
    def dim(self) -> int:
        return self._dim

    @property
    def name(self) -> str:
        return "hashing"


class OllamaEmbedder(EmbedderPort):
    """Ollama /api/embed 嵌入（异步优先，httpx.AsyncClient）。"""

    # 单批最大文本数：CPU 推理下大批量易超时，分批稳妥
    _BATCH = 16

    def __init__(self, model: str, base_url: str, timeout: float = 60.0) -> None:
        self._model = model
        self._url = base_url.rstrip("/") + "/api/embed"
        self._timeout = timeout
        self._dim: int | None = None
        self._lock = threading.Lock()

    async def _acall(self, texts: List[str]) -> List[List[float]]:
        """真正的 HTTP 调用（异步，httpx.AsyncClient）。"""
        payload = {"model": self._model, "input": texts or [""]}
        async with httpx.AsyncClient(timeout=self._timeout) as client:
            try:
                resp = await client.post(self._url, json=payload)
                resp.raise_for_status()
                data = resp.json()
            except Exception as exc:  # noqa: BLE001
                raise RuntimeError(f"Ollama 嵌入调用失败：{exc}") from exc
        embs = data.get("embeddings") or []
        if len(embs) != len(texts or [""]):
            raise RuntimeError("Ollama 嵌入返回数量与输入不匹配")
        return embs

    def _call(self, texts: List[str]) -> List[List[float]]:
        """同步桥接：离线脚本 / 测试用，内部经事件循环运行器调用 _acall。"""
        return _run_async(self._acall(texts))

    def _probe_dim(self) -> None:
        vec = self._call(["维度探测"])[0]
        self._dim = len(vec)

    def _prefixed(self, text: str, role: str) -> str:
        """nomic-embed-text 系列为非对称检索模型，需任务前缀才能发挥检索性能：
        文档侧 search_document: / 查询侧 search_query:。其它模型不加前缀。"""
        if "nomic" in self._model.lower():
            return f"{role}: {text}"
        return text

    def embed(self, texts: List[str]) -> List[List[float]]:
        items = [self._prefixed(t, "search_document") for t in (texts or [""])]
        return self._call(items)

    async def aembed(self, texts: List[str]) -> List[List[float]]:
        items = [self._prefixed(t, "search_document") for t in (texts or [""])]
        return await self._acall(items)

    def embed_query(self, text: str) -> List[float]:
        return self._call([self._prefixed(text, "search_query")])[0]

    async def aembed_query(self, text: str) -> List[float]:
        return (await self._acall([self._prefixed(text, "search_query")]))[0]

    @property
    def dim(self) -> int:
        if self._dim is None:
            with self._lock:
                if self._dim is None:
                    self._probe_dim()
        return self._dim

    @property
    def name(self) -> str:
        return f"ollama:{self._model}"


def build_embedder(settings: Settings | None = None) -> EmbedderPort:
    """按配置构建嵌入器：优先 Ollama，探测不可用时回退 hashing。"""
    s = settings or get_settings()
    if s.embedder == "ollama":
        base = s.ollama_base_url or s.llm_base_url or "http://localhost:11434"
        # llm_base_url 常带 OpenAI 兼容后缀 /v1，但 /api/embed 是 Ollama 原生接口，
        # 直接拼接会得到 /v1/api/embed → 404，这里剥离后缀。
        base = re.sub(r"/v1/?$", "", base.rstrip("/"))
        emb = OllamaEmbedder(model=s.embed_model, base_url=base, timeout=60.0)
        try:
            _ = emb.dim  # 触发探测（冷启动阶段完成维度探测，失败直接回退 hashing）
            logger.info("嵌入器：使用 Ollama (%s, dim=%d)", s.embed_model, emb.dim)
            # 探测到的真实维度同步回配置，供下游组件保持一致（frozen 配置做受控写回）
            try:
                object.__setattr__(s, "embed_dim", emb.dim)
            except Exception:  # noqa: BLE001
                pass
            return emb
        except Exception as exc:  # noqa: BLE001
            logger.warning("Ollama 嵌入不可用，回退 hashing 嵌入：%s", exc)
            return HashingEmbedder(dim=s.embed_dim)
    logger.info("嵌入器：使用 hashing（离线兜底）")
    return HashingEmbedder(dim=s.embed_dim)
