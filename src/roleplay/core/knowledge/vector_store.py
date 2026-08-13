"""持久化知识库（多命名空间向量库）。

- 实现 VectorStore 接口（add / search / aadd / asearch），与现有 Orchestrator 兼容。
- 内部用注入的 EmbedderPort 做向量化，余弦相似度检索。
- 按命名空间分区：persona（人设）/ events（长期记忆）/ web（联网）/ episodic（情节片段）。
- 落盘到 <knowledge_dir>/<namespace>.json，原子写；启动时自动加载。
- 进程内线程安全（RLock）。
- 异步路径（aadd / asearch）使用 EmbedderPort.aembed / aembed_query，避免阻塞事件循环。
"""
from __future__ import annotations

import asyncio
import json
import math
import re
import threading
import time
from pathlib import Path
from typing import Iterable
from urllib.parse import quote, unquote

from ..rag.base import RetrievedChunk, VectorStore
from .embedder import EmbedderPort

# 默认参与检索的命名空间及其权重（persona 权重最高，保证角色一致性）
DEFAULT_NAMESPACES = ["persona", "events", "web", "episodic"]
NAMESPACE_WEIGHTS = {"persona": 1.3, "events": 1.0, "web": 1.0, "episodic": 0.9}


def _cosine(a: list[float], b: list[float]) -> float:
    if not a or not b:
        return 0.0
    common = min(len(a), len(b))
    num = sum(a[i] * b[i] for i in range(common))
    na = math.sqrt(sum(v * v for v in a))
    nb = math.sqrt(sum(v * v for v in b))
    if na == 0 or nb == 0:
        return 0.0
    return num / (na * nb)


# ── BM25 稀疏检索（混合重排用，零依赖实现）──
# 中文按单字切分、英文/数字按词切分，兼顾中英混排语料的关键词命中。
_CJK_RE = re.compile(r"[一-鿿]")


def _tokenize(text: str) -> list[str]:
    if not text:
        return []
    toks: list[str] = []
    for ch in text:
        if _CJK_RE.match(ch):
            toks.append(ch)  # 中文：字级 token，命中关键词任意字
        elif ch.isalnum():
            toks.append(ch.lower())  # 英文/数字：归并到当前词
        else:
            toks.append(" ")  # 分隔符
    # 把连续英文/数字字符合成词
    words: list[str] = []
    buf = ""
    for t in toks:
        if t == " ":
            if buf:
                words.append(buf)
                buf = ""
            continue
        if len(t) == 1 and t.isalnum() and (buf and buf[-1].isalnum()):
            buf += t
        else:
            if buf:
                words.append(buf)
                buf = ""
            words.append(t)
    if buf:
        words.append(buf)
    return [w for w in words if w.strip()]


class _BM25:
    """紧凑 Okapi BM25（k1=1.5, b=0.75），语料规模小，内存索引足够。"""

    def __init__(self, corpus: list[str]) -> None:
        self._docs = [_tokenize(d) for d in corpus]
        self._n = len(self._docs)
        self._avgdl = (sum(len(d) for d in self._docs) / self._n) if self._n else 0.0
        self._idf: dict[str, float] = {}
        df: dict[str, int] = {}
        for d in self._docs:
            for t in set(d):
                df[t] = df.get(t, 0) + 1
        for t, c in df.items():
            # 平滑 idf，避免罕见词爆炸
            self._idf[t] = math.log(1 + (self._n - c + 0.5) / (c + 0.5))
        self._k1 = 1.5
        self._b = 0.75

    def scores(self, query: str) -> list[float]:
        q = _tokenize(query)
        out = [0.0] * self._n
        for term in set(q):
            idf = self._idf.get(term)
            if idf is None:
                continue
            for i, d in enumerate(self._docs):
                f = d.count(term)
                if f == 0:
                    continue
                denom = f + self._k1 * (1 - self._b + self._b * len(d) / (self._avgdl or 1))
                out[i] += idf * (f * (self._k1 + 1)) / denom
        return out


class KnowledgeBase(VectorStore):
    def __init__(
        self,
        embedder: EmbedderPort,
        persist_dir: str | Path | None = None,
        retrieval_namespaces: Iterable[str] | None = None,
    ) -> None:
        self._emb = embedder
        self._dir = Path(persist_dir) if persist_dir else None
        self._namespaces = list(retrieval_namespaces or DEFAULT_NAMESPACES)
        self._lock = threading.RLock()
        # ns -> list[{id, text, vec, meta, ts}]
        self._data: dict[str, list[dict]] = {ns: [] for ns in DEFAULT_NAMESPACES}
        self._seq = 0
        # BM25 索引缓存：key=(命名空间元组, 版本号) -> (all_items, _BM25)
        # 数据变更（add/remove/clear/load）会递增 _version 使缓存失效。
        self._version = 0
        self._bm25_cache: dict[tuple, tuple[list, _BM25]] = {}
        if self._dir:
            try:
                self._dir.mkdir(parents=True, exist_ok=True)
                self._load()
            except OSError:
                self._dir = None  # 不可写则退化为纯内存

    # ── 写入 ──
    def _bump_version(self) -> None:
        self._version += 1
        self._bm25_cache.clear()

    def add(
        self,
        texts: list[str],
        metadatas: list[dict] | None = None,
        namespace: str = "episodic",
    ) -> list[str]:
        metas = metadatas or [{} for _ in texts]
        if len(metas) != len(texts):
            metas = [{} for _ in texts]
        vecs = self._emb.embed(texts)
        ids: list[str] = []
        with self._lock:
            bucket = self._data.setdefault(namespace, [])
            for t, m, v in zip(texts, metas, vecs):
                self._seq += 1
                cid = f"{namespace}-{self._seq}"
                bucket.append(
                    {
                        "id": cid,
                        "text": t,
                        "vec": v,
                        "meta": m,
                        "ts": time.time(),
                    }
                )
                ids.append(cid)
            self._bump_version()
            self._save_ns(namespace)
        return ids

    async def aadd(
        self,
        texts: list[str],
        metadatas: list[dict] | None = None,
        namespace: str = "episodic",
    ) -> list[str]:
        metas = metadatas or [{} for _ in texts]
        if len(metas) != len(texts):
            metas = [{} for _ in texts]
        vecs = await self._emb.aembed(texts)  # 异步嵌入（网络/CPU，循环内 await）
        # 写入 + 落盘属 CPU/同步 IO，卸载到线程池，避免阻塞事件循环
        def _run() -> list[str]:
            ids: list[str] = []
            with self._lock:
                bucket = self._data.setdefault(namespace, [])
                for t, m, v in zip(texts, metas, vecs):
                    self._seq += 1
                    cid = f"{namespace}-{self._seq}"
                    bucket.append(
                        {
                            "id": cid,
                            "text": t,
                            "vec": v,
                            "meta": m,
                            "ts": time.time(),
                        }
                    )
                    ids.append(cid)
                self._bump_version()
                self._save_ns(namespace)
            return ids
        return await asyncio.to_thread(_run)

    def remove(self, namespace: str, item_id: str) -> bool:
        with self._lock:
            bucket = self._data.get(namespace)
            if not bucket:
                return False
            before = len(bucket)
            bucket[:] = [it for it in bucket if it["id"] != item_id]
            removed = len(bucket) != before
            if removed:
                self._bump_version()
                self._save_ns(namespace)
            return removed

    def clear_namespace(self, namespace: str) -> None:
        with self._lock:
            self._data[namespace] = []
            self._bump_version()
            self._save_ns(namespace)

    def filter_remove(self, namespace: str, predicate) -> int:
        """在锁内移除满足 predicate(item)->bool 的条目，返回移除条数。"""
        with self._lock:
            bucket = self._data.get(namespace)
            if not bucket:
                return 0
            before = len(bucket)
            bucket[:] = [it for it in bucket if not predicate(it)]
            removed = before - len(bucket)
            if removed:
                self._bump_version()
                self._save_ns(namespace)
            return removed

    # ── 检索 ──
    def _collect(
        self, ns: list[str], query_vec: list[float], min_score: float
    ) -> tuple[list[RetrievedChunk], list[dict]]:
        """按命名空间聚合候选，返回 (结果列表, 全量 item 列表)。"""
        results: list[RetrievedChunk] = []
        all_items: list[dict] = []
        with self._lock:
            for n in ns:
                for item in self._data.get(n, []):
                    all_items.append(item)
                    base = _cosine(query_vec, item["vec"])
                    if base <= 0:
                        continue
                    w = NAMESPACE_WEIGHTS.get(n, 1.0)
                    score = round(base * w, 4)
                    if score < min_score:
                        continue
                    meta = dict(item.get("meta", {}))
                    meta.setdefault("namespace", n)
                    meta.setdefault("id", item["id"])
                    # 时间戳透传进 metadata，供长期记忆时间衰减重排使用
                    meta.setdefault("ts", item.get("ts", 0.0))
                    results.append(
                        RetrievedChunk(text=item["text"], score=score, metadata=meta)
                    )
        return results, all_items

    def _bm25_scores(
        self, all_items: list[dict], ns_key: tuple, query: str
    ) -> dict[str, float]:
        """返回 {item_id: bm25_score}，BM25 索引按 (ns, 版本) 缓存，避免每次请求重复建索引。

        加锁保护缓存读写（asearch 经 asyncio.to_thread 在多线程并发时安全）。
        """
        key = (ns_key, self._version)
        with self._lock:
            cached = self._bm25_cache.get(key)
            if cached is None:
                docs = [it["text"] for it in all_items]
                bm = _BM25(docs)
                self._bm25_cache[key] = (all_items, bm)
                # 控制缓存规模
                if len(self._bm25_cache) > 32:
                    self._bm25_cache.pop(next(iter(self._bm25_cache)))
            items_cached, bm = self._bm25_cache[key]
        scores = bm.scores(query)
        return {
            items_cached[i]["id"]: scores[i] for i in range(len(items_cached))
        }

    def _rerank(
        self,
        results: list[RetrievedChunk],
        all_items: list[dict],
        ns: list[str],
        query: str,
        top_k: int,
        hybrid: bool,
        hybrid_alpha: float,
        candidate_mult: int,
    ) -> list[RetrievedChunk]:
        if not results:
            return []
        # 关键修复：先按稠密分降序排序，再取候选集，
        # 否则按命名空间遍历序切片会漏掉出现在靠后命名空间的高分结果。
        results.sort(key=lambda c: c.score, reverse=True)
        if hybrid and len(results) > top_k:
            cand = results[: max(top_k, min(len(results), top_k * candidate_mult))]
            # 混合重排：稠密向量分 + BM25 稀疏分，各自按最大值相对归一化后加权融合，
            # 提升关键词命中精度（相对归一化避免被 min-max 把弱稠密项清零）。
            bm25_by_id = self._bm25_scores(all_items, tuple(ns), query)
            bvals = [bm25_by_id.get(c.metadata["id"], 0.0) for c in cand]
            dmax = max(c.score for c in cand) or 1.0
            bmax = max(bvals) or 1.0
            for c, b in zip(cand, bvals):
                dn = c.score / dmax
                bn = b / bmax
                c.score = round((1.0 - hybrid_alpha) * dn + hybrid_alpha * bn, 4)
            cand.sort(key=lambda x: x.score, reverse=True)
            return cand[:top_k]
        return results[:top_k]

    def search(
        self,
        query: str,
        top_k: int = 3,
        namespaces: Iterable[str] | None = None,
        min_score: float = 0.0,
        hybrid: bool = False,
        hybrid_alpha: float = 0.3,
        candidate_mult: int = 12,
    ) -> list[RetrievedChunk]:
        ns = list(namespaces or self._namespaces)
        qv = self._emb.embed_query(query)  # 同步查询嵌入（离线/测试路径）
        results, all_items = self._collect(ns, qv, min_score)
        return self._rerank(
            results, all_items, ns, query, top_k, hybrid, hybrid_alpha, candidate_mult
        )

    async def asearch(
        self,
        query: str,
        top_k: int = 3,
        namespaces: Iterable[str] | None = None,
        min_score: float = 0.0,
        hybrid: bool = False,
        hybrid_alpha: float = 0.3,
        candidate_mult: int = 12,
    ) -> list[RetrievedChunk]:
        ns = list(namespaces or self._namespaces)
        qv = await self._emb.aembed_query(query)  # 异步查询嵌入（请求路径，不阻塞循环）
        # 全量余弦 + BM25 重排属 CPU 密集，卸载到线程池，避免阻塞事件循环
        def _run() -> list[RetrievedChunk]:
            results, all_items = self._collect(ns, qv, min_score)
            return self._rerank(
                results, all_items, ns, query, top_k, hybrid, hybrid_alpha, candidate_mult
            )
        return await asyncio.to_thread(_run)

    def count(self, namespace: str | None = None) -> dict[str, int]:
        with self._lock:
            if namespace:
                return {namespace: len(self._data.get(namespace, []))}
            return {ns: len(b) for ns, b in self._data.items()}

    def list_items(self, namespace: str) -> list[dict]:
        """返回某命名空间全部条目（含 id/text/meta/ts），供按 key 查重等全量扫描。

        - 锁内读取，返回拷贝：item dict 与 meta dict 均复制（vec 引用即可，
          调用方只读不写；meta 复制避免调用方误改污染内部数据）。
        - 若需检索语义请用 search/asearch；本方法专为「元数据扫描」设计
          （如 UserProfile 按去重键查重、提醒扫描），条目数受硬上限约束，成本可控。
        """
        with self._lock:
            bucket = self._data.get(namespace, [])
            return [{**it, "meta": dict(it.get("meta", {}))} for it in bucket]

    # ── 持久化 ──
    def _path(self, ns: str) -> Path:
        # 命名空间可能含 Windows 非法文件名字符（如 events:<character_id> 的冒号），
        # 落盘时统一做 URL 编码转义，加载时反向解码，保证跨平台持久化不丢数据。
        return self._dir / f"{quote(ns, safe='')}.json"

    def _save_ns(self, ns: str) -> None:
        if not self._dir:
            return
        try:
            tmp = self._dir / f".{quote(ns, safe='')}.tmp"
            data = self._data.get(ns, [])
            tmp.write_text(
                json.dumps(data, ensure_ascii=False),
                encoding="utf-8",
            )
            tmp.replace(self._path(ns))  # 原子替换
        except OSError:
            pass

    def _load(self) -> None:
        try:
            for f in self._dir.glob("*.json"):
                if f.stem.startswith("."):
                    continue
                # 文件名是 URL 编码后的命名空间，解码还原（兼容历史未编码文件）
                try:
                    ns = unquote(f.stem)
                except Exception:  # noqa: BLE001
                    ns = f.stem
                try:
                    data = json.loads(f.read_text(encoding="utf-8"))
                    if isinstance(data, list):
                        self._data[ns] = data
                        # 维持自增 id 不回退
                        for it in data:
                            try:
                                num = int(str(it.get("id", "")).split("-")[-1])
                                self._seq = max(self._seq, num)
                            except (ValueError, TypeError):
                                pass
                except (OSError, ValueError, TypeError):
                    continue
            # 加载完成，重置版本（使 BM25 缓存失效，重新基于磁盘内容建索引）
            self._version = 0
            self._bm25_cache.clear()
        except OSError:
            pass
