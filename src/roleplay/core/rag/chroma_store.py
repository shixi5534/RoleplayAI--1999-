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
    chromadb = None  # 保持模块始终暴露 chromadb 名称，便于测试注入 fake 后端
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

    def add(
        self,
        texts: list[str],
        metadatas: list[dict] | None = None,
        namespace: str = "default",
    ) -> None:
        if not texts:
            return
        ids = [f"doc_{i}_{_stable_id(texts[i])}" for i in range(len(texts))]
        metas: list[dict] = []
        for i in range(len(texts)):
            meta = dict(metadatas[i]) if metadatas and i < len(metadatas) else {}
            meta["namespace"] = namespace
            metas.append(meta)
        self._col.add(ids=ids, documents=texts, metadatas=metas)

    @staticmethod
    def _hybrid_rerank(
        candidates: list[RetrievedChunk],
        top_k: int,
        hybrid_alpha: float,
        query: str,
    ) -> list[RetrievedChunk]:
        """对 Chroma 稠密候选做轻量 BM25 重排（候选集内 IDF）。

        持久化语义检索仍建议使用 KnowledgeBase；此处提供与接口一致的基础混合能力。
        """
        if len(candidates) <= top_k:
            return candidates
        from ..knowledge.vector_store import _BM25

        bm = _BM25([c.text for c in candidates])
        bvals = bm.scores(query)
        dmax = max(c.score for c in candidates) or 1.0
        bmax = max(bvals) or 1.0
        for c, b in zip(candidates, bvals):
            c.score = round(
                (1.0 - hybrid_alpha) * (c.score / dmax)
                + hybrid_alpha * (b / bmax),
                4,
            )
        candidates.sort(key=lambda c: c.score, reverse=True)
        return candidates[:top_k]

    def search(
        self,
        query: str,
        top_k: int = 3,
        namespaces: Iterable[str] | None = None,
        hybrid: bool = False,
        hybrid_alpha: float = 0.45,
        candidate_mult: int = 30,
    ) -> list[RetrievedChunk]:
        if not query:
            return []
        wanted = set(namespaces) if namespaces is not None else None
        # 有命名空间过滤时多取候选，避免命中结果全落在少数 namespace 导致截断
        fetch_n = top_k if wanted is None else max(top_k * 4, top_k * candidate_mult)
        res = self._col.query(query_texts=[query], n_results=fetch_n)
        if not res or not res.get("ids"):
            return []
        docs = res["documents"][0]
        dists = (res.get("distances") or [[]])[0]
        metas = (res.get("metadatas") or [[]])[0]
        out: list[RetrievedChunk] = []
        for i, doc in enumerate(docs):
            meta = metas[i] if i < len(metas) else {}
            meta = meta or {}
            if wanted is not None and meta.get("namespace") not in wanted:
                continue
            # Chroma 返回距离（越小越近），换算成相似度分数（越大越好）
            dist = dists[i] if i < len(dists) else 1.0
            score = max(0.0, 1.0 - float(dist))
            out.append(
                RetrievedChunk(text=doc, score=round(score, 4), metadata=meta or {})
            )
        out.sort(key=lambda c: c.score, reverse=True)
        if hybrid:
            return self._hybrid_rerank(out, top_k, hybrid_alpha, query)
        return out[:top_k]

    async def asearch(
        self,
        query: str,
        top_k: int = 3,
        namespaces: Iterable[str] | None = None,
        hybrid: bool = False,
        hybrid_alpha: float = 0.45,
        candidate_mult: int = 30,
    ) -> list[RetrievedChunk]:
        """Chroma 同步客户端封装为异步，供 Orchestrator 统一 await。"""
        import asyncio

        return await asyncio.to_thread(
            self.search,
            query,
            top_k=top_k,
            namespaces=namespaces,
            hybrid=hybrid,
            hybrid_alpha=hybrid_alpha,
            candidate_mult=candidate_mult,
        )

    def clear_namespace(self, namespace: str) -> None:
        """按 namespace 删除 Chroma 文档（KnowledgeBase 兼容接口）。"""
        try:
            self._col.delete(where={"namespace": namespace})
        except Exception as exc:  # noqa: BLE001
            logger.warning("Chroma 清空命名空间 %s 失败：%s", namespace, exc)

    def filter_remove(self, namespace: str, predicate) -> int:
        """按 predicate 删除指定 namespace 内的文档；返回删除条数。"""
        try:
            data = self._col.get(
                where={"namespace": namespace},
                include=["documents", "metadatas"],
            )
        except Exception as exc:  # noqa: BLE001
            logger.warning("Chroma 查询命名空间 %s 失败：%s", namespace, exc)
            return 0
        ids = data.get("ids") or []
        to_delete: list[str] = []
        for i, cid in enumerate(ids):
            item = {
                "id": cid,
                "text": (data.get("documents") or [])[i] if i < len(data.get("documents") or []) else "",
                "meta": (data.get("metadatas") or [])[i] if i < len(data.get("metadatas") or []) else {},
            }
            try:
                matched = bool(predicate(item))
            except Exception:  # noqa: BLE001
                matched = False
            if matched:
                to_delete.append(cid)
        if to_delete:
            try:
                self._col.delete(ids=to_delete)
            except Exception as exc:  # noqa: BLE001
                logger.warning("Chroma 删除命名空间 %s 文档失败：%s", namespace, exc)
                return 0
        return len(to_delete)
