"""向量库抽象端口。

业务层只依赖此接口；具体实现（内存 / Chroma / 其他）可热插拔。
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Iterable


@dataclass
class RetrievedChunk:
    text: str
    score: float
    metadata: dict = field(default_factory=dict)


class VectorStore(ABC):
    @abstractmethod
    def add(self, texts: list[str], metadatas: list[dict] | None = None) -> None:
        """写入文档（实现负责切分/嵌入）。"""

    @abstractmethod
    def search(
        self,
        query: str,
        top_k: int = 3,
        namespaces: Iterable[str] | None = None,
        hybrid: bool = False,
        hybrid_alpha: float = 0.3,
        candidate_mult: int = 12,
    ) -> list[RetrievedChunk]:
        """返回与 query 最相关的 top_k 个片段（按相似度降序）。

        hybrid / hybrid_alpha / candidate_mult 为混合重排参数，
        由具体实现决定是否采纳（持久化 KnowledgeBase 采用稠密+BM25 混合重排）。
        """
