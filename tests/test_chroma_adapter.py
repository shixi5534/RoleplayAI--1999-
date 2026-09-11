"""Chroma 适配器轻量单测（fake chromadb，不触发真实依赖）。"""
from types import SimpleNamespace

import pytest

import roleplay.core.rag.chroma_store as cs


class _FakeCollection:
    def __init__(self):
        self.items = []

    def add(self, ids, documents, metadatas):
        for i, cid in enumerate(ids):
            self.items.append(
                {
                    "id": cid,
                    "text": documents[i],
                    "meta": metadatas[i] if metadatas else {},
                }
            )

    def query(self, query_texts, n_results):
        return {
            "ids": [[it["id"] for it in self.items[:n_results]]],
            "documents": [[it["text"] for it in self.items[:n_results]]],
            "distances": [[0.1 * (i + 1) for i in range(min(n_results, len(self.items)))]],
            "metadatas": [[it["meta"] for it in self.items[:n_results]]],
        }

    def get(self, where=None, include=None):
        return {
            "ids": [it["id"] for it in self.items],
            "documents": [it["text"] for it in self.items],
            "metadatas": [it["meta"] for it in self.items],
        }

    def delete(self, ids=None, where=None):
        if ids is not None:
            self.items = [it for it in self.items if it["id"] not in set(ids)]
        elif where is not None:
            self.items = [
                it for it in self.items if it["meta"].get("namespace") != where.get("namespace")
            ]


class _FakeClient:
    def __init__(self, path=None, **kwargs):
        pass

    def get_or_create_collection(self, name):
        return _FakeCollection()


@pytest.fixture
def store(monkeypatch):
    monkeypatch.setattr(cs, "_CHROMA_AVAILABLE", True)
    monkeypatch.setattr(
        cs, "chromadb", SimpleNamespace(PersistentClient=_FakeClient)
    )
    return cs.ChromaVectorStore(persist_dir="unused")


def test_chroma_add_injects_namespace(store):
    store.add(["hello world"], metadatas=[{"k": "v"}], namespace="docs")
    assert store._col.items[0]["meta"]["namespace"] == "docs"


def test_chroma_search_filters_namespace(store):
    store.add(["hello world"], namespace="docs")
    store.add(["hello 世界"], namespace="events")
    hits = store.search("hello", top_k=2, namespaces=["docs"])
    assert hits
    assert all(h.metadata.get("namespace") == "docs" for h in hits)


def test_chroma_hybrid_rerank_runs(store):
    store.add(["hello world"], namespace="docs")
    store.add(["hello there"], namespace="docs")
    hits = store.search("hello world", top_k=1, namespaces=["docs"], hybrid=True)
    assert len(hits) == 1


def test_chroma_clear_namespace(store):
    store.add(["hello"], namespace="docs")
    store.add(["世界"], namespace="events")
    store.clear_namespace("docs")
    assert all(it["meta"]["namespace"] != "docs" for it in store._col.items)
