"""Chroma 向量库适配器（可选、生产级持久化）。

- 仅在配置 `rag_impl=chroma` 且已 `pip install chromadb` 时使用。
- 未安装 chromadb 时构造即抛出清晰的 ConfigurationError（由 factory 转译给运维），
  绝不让 import 失败拖垮整个应用启动。
- 注意：当前编排器实际检索走自研 `KnowledgeBase`（多命名空间 + 余弦，零依赖、重启不丢）。
  `rag` 这一路是历史兼容/可替换后端；选 chroma 时由本适配器提供真实持久化向量检索。
"""
import hashlib
import logging
from typing import Iterable

from ...errors import ConfigurationError
from .base import RetrievedChunk, VectorStore

logger = logging.getLogger(__name__)

try:
    import chromadb

    _CHROMA_AVAILABLE = True
except ImportError:  # pragma: no cover - 取决于是否安装 chromadb
    _CHROMA_AVAILABLE = False


def _stable_id(text: str) -> str:
    """内容 → 稳定 id：用 md5 而非内建 hash()。

    内建 hash() 受 PYTHONHASHSEED 随机化影响，进程重启后同一文档 id 变化，
    导致 Chroma 持久化跨重启重复入库（产生重复文档）；同批内哈希碰撞还会
    触发 DuplicateIDError。md5 确定性、跨进程/跨重启稳定。
    """
    return hashlib.md5(text.encode("utf-8")).hexdigest()[:16]


class ChromaVectorStore(VectorStore):
    def __init__(self, persist_dir: str, collection: str = "roleplay") -> None:
        if not _CHROMA_AVAILABLE:
            raise ConfigurationError(
                "未安装 chromadb，无法使用 Chroma 向量库。请执行 pip install chromadb，"
                "或将配置 rag_impl 改为 memory（零依赖内存库）。",
            )
        self._client = chromadb.PersistentClient(path=persist_dir)
        # 首次创建会拉起 chroma 内置的默认嵌入函数（onnx all-MiniLM），需联网下载一次
        self._col = self._client.get_or_create_collection(name=collection)

    def add(self, texts: list[str], metadatas: list[dict] | None = None) -> None:
        if not texts:
            return
        ids = [f"doc_{i}_{_stable_id(texts[i])}" for i in range(len(texts))]
        self._col.add(ids=ids, documents=texts, metadatas=metadatas)

    def search(
        self,
        query: str,
        top_k: int = 3,
        namespaces: Iterable[str] | None = None,
        hybrid: bool = False,
        hybrid_alpha: float = 0.3,
        candidate_mult: int = 12,
    ) -> list[RetrievedChunk]:
        if not query:
            return []
        res = self._col.query(query_texts=[query], n_results=top_k)
        if not res or not res.get("ids"):
            return []
        ids = res["ids"][0]
        docs = res["documents"][0]
        dists = (res.get("distances") or [[]])[0]
        metas = (res.get("metadatas") or [[]])[0]
        out: list[RetrievedChunk] = []
        for i, doc in enumerate(docs):
            # Chroma 返回 L2/余弦距离（越小越近），换算成相似度分数（越大越好）
            dist = dists[i] if i < len(dists) else 1.0
            score = max(0.0, 1.0 - float(dist))
            meta = metas[i] if i < len(metas) else {}
            out.append(RetrievedChunk(text=doc, score=round(score, 4), metadata=meta or {}))
        return out
