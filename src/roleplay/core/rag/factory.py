"""向量库工厂：依据配置构建具体实现（Chroma 可选、延迟导入）。"""
from ...config import Settings, get_settings
from ...errors import ConfigurationError
from .base import VectorStore
from .memory import InMemoryVectorStore


def build_vector_store(settings: Settings | None = None) -> VectorStore:
    s = settings or get_settings()
    if s.rag_impl == "memory":
        return InMemoryVectorStore()
    if s.rag_impl == "chroma":
        # 延迟导入，避免未安装 chromadb 时应用无法启动
        try:
            from .chroma_store import ChromaVectorStore

            return ChromaVectorStore(persist_dir=s.chroma_persist_dir)
        except ImportError as exc:
            raise ConfigurationError(
                "未安装 chromadb，请执行 pip install chromadb", details=str(exc)
            ) from exc
    raise ConfigurationError(
        "不支持的 RAG 实现", details={"rag_impl": s.rag_impl}
    )
