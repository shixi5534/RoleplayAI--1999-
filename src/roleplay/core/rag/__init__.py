"""向量检索端口与适配器。"""
from .base import VectorStore, RetrievedChunk
from .memory import InMemoryVectorStore
from .factory import build_vector_store

__all__ = [
    "VectorStore",
    "RetrievedChunk",
    "InMemoryVectorStore",
    "build_vector_store",
]
