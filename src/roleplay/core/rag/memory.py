"""内存向量库：纯 Python TF-IDF 余弦相似度，零依赖，便于离线测试。

生产环境用 build_vector_store 切换到 Chroma；接口完全一致。
"""
import math
from typing import Iterable

from .base import VectorStore, RetrievedChunk


def _tokenize(text: str) -> list[str]:
    """轻量中英混合分词：ASCII 字母数字按词、CJK 逐字。

    注意：str.isalnum() 对中文也返回 True，因此必须用 isascii() 过滤，
    否则整句中文会被当成一个英文词，导致检索完全失效。
    """
    tokens: list[str] = []
    buf: list[str] = []
    for ch in text.lower():
        if ch.isascii() and ch.isalnum():
            buf.append(ch)
        else:
            if buf:
                tokens.append("".join(buf))
                buf = []
            if ch.strip():
                tokens.append(ch)
    if buf:
        tokens.append("".join(buf))
    return tokens


def _tf(tokens: list[str]) -> dict[str, float]:
    vec: dict[str, float] = {}
    for t in tokens:
        vec[t] = vec.get(t, 0.0) + 1.0
    return vec


def _cosine(a: dict[str, float], b: dict[str, float]) -> float:
    common = set(a) & set(b)
    if not common:
        return 0.0
    num = sum(a[t] * b[t] for t in common)
    na = math.sqrt(sum(v * v for v in a.values()))
    nb = math.sqrt(sum(v * v for v in b.values()))
    if na == 0 or nb == 0:
        return 0.0
    return num / (na * nb)


class InMemoryVectorStore(VectorStore):
    def __init__(self) -> None:
        # 预计算文档向量：(归一化前的 tf 向量, 文本, 元数据)
        self._docs: list[tuple[dict[str, float], str, dict]] = []

    def add(self, texts: list[str], metadatas: list[dict] | None = None) -> None:
        for i, text in enumerate(texts):
            meta = metadatas[i] if metadatas else {}
            # 写入时即完成分词+TF，避免每次查询重复计算（性能优化）
            self._docs.append((_tf(_tokenize(text)), text, meta))

    def search(
        self,
        query: str,
        top_k: int = 3,
        namespaces: Iterable[str] | None = None,
        hybrid: bool = False,
        hybrid_alpha: float = 0.45,
        candidate_mult: int = 30,
    ) -> list[RetrievedChunk]:
        qv = _tf(_tokenize(query))
        scored = [
            RetrievedChunk(
                text=t,
                score=round(_cosine(qv, vec), 4),
                metadata=m,
            )
            for vec, t, m in self._docs
        ]
        scored.sort(key=lambda x: x.score, reverse=True)
        return [c for c in scored[:top_k] if c.score > 0.0]
