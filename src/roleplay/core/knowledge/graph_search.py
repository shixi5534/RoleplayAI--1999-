"""lore 知识图谱检索（GraphRAG 在线层）。

与剧情层（``plot_graph``）的区别：本层面向 ``lore_<cid>`` 向量库的手工资料，
证据回查走 **KnowledgeBase**（按 chunk 文本 sha1 反查原文块），实体链接在别名
精确匹配之外多了「实体名向量 top-m」兜底（复用 EmbedderPort，查询侧一次嵌入）。

链路（docs/GRAPHRAG加强计划书.md §3 在线检索层）：
    query ──► ① 实体链接（别名精确 / 实体名向量）
          ──► ② PPR 展开激活（graph_ppr，边权 = confidence × importance）
          ──► ③ 证据收集（边上的 evidence hash → KnowledgeBase 原文块）
          ──► ④ 渲染为 RetrievedChunk（metadata.via="graph"、edge="A —关系→ B"）

降级策略（零回归）：图谱文件缺失 / 指纹失配 / 实体链接零命中 / 开关关闭
→ 返回空列表，调用方（编排器）静默回退纯向量路径。
"""
from __future__ import annotations

import logging
import math
import re

from ...core.rag.base import RetrievedChunk
from .graph_ppr import hop_distance, personalized_pagerank
from .graph_store import GraphStore, chunk_text_hash, norm_name

logger = logging.getLogger(__name__)


def _cosine(a: list[float], b: list[float]) -> float:
    if not a or not b or len(a) != len(b):
        return 0.0
    num = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(v * v for v in a))
    nb = math.sqrt(sum(v * v for v in b))
    if na == 0 or nb == 0:
        return 0.0
    return num / (na * nb)


class GraphSearcher:
    """单角色 lore 图谱检索器（实体链接 → PPR → 证据回查）。"""

    def __init__(
        self,
        store: GraphStore,
        kb,
        *,
        namespace: str = "",
        embedder=None,
        min_confidence: float = 0.55,
        include_weak: bool = False,
        link_threshold: float = 0.82,
        damping: float = 0.85,
        max_iter: int = 50,
        max_hops: int = 2,
        max_edges: int = 12,
        top_chunks: int = 3,
    ) -> None:
        self.store = store
        self.kb = kb
        self.namespace = namespace or "graph"
        self.embedder = embedder
        self.min_confidence = min_confidence
        self.include_weak = include_weak
        self.link_threshold = link_threshold
        self.damping = damping
        self.max_iter = max_iter
        self.max_hops = max_hops
        self.max_edges = max_edges
        self.top_chunks = max(0, int(top_chunks))
        self._entities_cache: list[dict] | None = None
        self._evidence_index: dict[str, dict] | None = None
        self._evidence_index_version: object = None

    # ── 实体链接 ──
    def _entities(self) -> list[dict]:
        if self._entities_cache is None:
            self._entities_cache = self.store.entities()
        return self._entities_cache

    def link(self, query: str) -> dict[str, float]:
        """查询 → {eid: weight}：别名/正名精确匹配优先，实体名向量 top-m 兜底。"""
        q = (query or "").strip()
        if not q:
            return {}
        exact = self._link_exact(q)
        if exact:
            return exact
        return self._link_vector(q)

    def _link_exact(self, query: str) -> dict[str, float]:
        """子串精确匹配：取**最长**命中（避免「露西」抢走「露西娅」的查询）。"""
        qn = norm_name(query)
        best_len = 0
        matches: dict[str, str] = {}
        for ent in self._entities():
            names = [str(ent.get("name") or "")] + [
                str(a) for a in (ent.get("aliases") or [])
            ]
            eid = str(ent.get("id"))
            for n in names:
                nn = norm_name(n)
                if not nn or len(nn) < 2 or nn not in qn:
                    continue
                # 拉丁名按词边界匹配，避免 "ania" 命中 "mania"
                if re.fullmatch(r"[a-z0-9 ]+", nn) and not re.search(
                    r"(?<![a-z0-9])" + re.escape(nn) + r"(?![a-z0-9])", qn
                ):
                    continue
                if len(nn) > best_len:
                    best_len = len(nn)
                    matches = {eid: nn}
                elif len(nn) == best_len:
                    matches.setdefault(eid, nn)
        if not matches:
            return {}
        def _rank(eid: str) -> tuple[int, int]:
            ent = self.store.get_entity(eid) or {}
            is_canon = norm_name(str(ent.get("name") or "")) == matches.get(eid)
            return (0 if is_canon else 1, -int(ent.get("mentions") or 0))

        return {eid: 1.0 for eid in sorted(matches, key=_rank)[:3]}

    def _link_vector(self, query: str) -> dict[str, float]:
        """实体名向量链接（离线预算好 vec；查询侧一次嵌入）。"""
        if self.embedder is None:
            return {}
        vecs = [
            (str(e.get("id")), e.get("vec"))
            for e in self._entities()
            if e.get("vec")
        ]
        if not vecs:
            return {}
        try:
            qv = self.embedder.embed_query(query)
        except Exception as exc:  # noqa: BLE001 —— 嵌入失败不影响主链路
            logger.warning("图谱实体链接嵌入失败（跳过图谱路）：%s", exc)
            return {}
        scored = [
            (eid, _cosine(qv, vec))
            for eid, vec in vecs
        ]
        scored.sort(key=lambda kv: kv[1], reverse=True)
        return {
            eid: round(s, 4)
            for eid, s in scored[:3]
            if s >= self.link_threshold
        }

    # ── 证据回查 ──
    def _evidence(self) -> dict[str, dict]:
        """chunk 文本哈希 → 知识库条目（按 kb.version 缓存失效）。"""
        version = getattr(self.kb, "version", None)
        if self._evidence_index is not None and self._evidence_index_version == version:
            return self._evidence_index
        idx: dict[str, dict] = {}
        namespaces = {
            str(x.get("ns"))
            for e in self.store.all_edges()
            for x in (e.get("evidence") or [])
            if x.get("ns")
        }
        for ns in namespaces:
            try:
                items = self.kb.list_items(ns)
            except Exception as exc:  # noqa: BLE001
                logger.warning("图谱证据索引读取命名空间 %s 失败：%s", ns, exc)
                continue
            for it in items:
                text = str(it.get("text") or "")
                if not text:
                    continue
                idx.setdefault(
                    chunk_text_hash(text),
                    {
                        "text": text,
                        "meta": {**dict(it.get("meta") or {}), "namespace": ns},
                    },
                )
        self._evidence_index = idx
        self._evidence_index_version = version
        return idx

    def _name_of(self, eid: str) -> str:
        ent = self.store.get_entity(eid) or {}
        return str(ent.get("name") or eid)

    # ── 检索入口 ──
    def retrieve(self, query: str) -> list[RetrievedChunk]:
        """实体链接 → PPR → 证据块（零命中返回空列表）。"""
        if not self.top_chunks:
            return []
        seeds = self.link(query)
        if not seeds:
            return []
        edges = self.store.all_edges()
        ranks = personalized_pagerank(
            edges,
            seeds,
            min_confidence=self.min_confidence,
            include_weak=self.include_weak,
            damping=self.damping,
            max_iter=self.max_iter,
        )
        dist = hop_distance(
            edges,
            set(seeds),
            self.max_hops,
            min_confidence=self.min_confidence,
            include_weak=self.include_weak,
        )
        scored: list[tuple[float, dict]] = []
        for e in edges:
            if float(e.get("confidence", 0.0)) < self.min_confidence:
                continue
            if not self.include_weak and len(e.get("evidence") or []) < 2:
                continue
            s, d = str(e.get("src")), str(e.get("dst"))
            if s not in dist or d not in dist:
                continue
            if max(dist[s], dist[d]) > self.max_hops:
                continue
            score = (ranks.get(s, 0.0) + ranks.get(d, 0.0)) * float(
                e.get("confidence", 0.0)
            )
            if score > 0:
                scored.append((score, e))
        if not scored:
            return []
        scored.sort(key=lambda kv: kv[0], reverse=True)
        idx = self._evidence()
        out: list[RetrievedChunk] = []
        seen: set[str] = set()
        for score, e in scored[: self.max_edges]:
            for ev in e.get("evidence") or []:
                h = str(ev.get("hash") or "")
                if not h or h in seen:
                    continue
                item = idx.get(h)
                if item is None:
                    continue
                seen.add(h)
                meta = dict(item["meta"])
                meta.update(
                    {
                        "via": "graph",
                        "source_type": "graph_evidence",
                        "edge": f"{self._name_of(str(e.get('src')))}"
                        f" —{e.get('relation')}→ "
                        f"{self._name_of(str(e.get('dst')))}",
                        "edge_score": round(float(score), 4),
                    }
                )
                out.append(
                    RetrievedChunk(text=item["text"], score=float(score), metadata=meta)
                )
                break  # 每条边只取一条代表证据
            if len(out) >= self.top_chunks:
                break
        return out


class GraphSearchRegistry:
    """按角色的 lore 图谱检索器注册表（懒加载 + mtime 热重载 + 指纹校验）。"""

    def __init__(
        self,
        directory: str,
        kb,
        *,
        embedder=None,
        min_confidence: float = 0.55,
        include_weak: bool = False,
        link_threshold: float = 0.82,
        damping: float = 0.85,
        max_iter: int = 50,
        max_hops: int = 2,
        max_edges: int = 12,
        top_chunks: int = 3,
    ) -> None:
        self._dir = directory
        self._kb = kb
        self._embedder = embedder
        self._embedder_name = getattr(embedder, "name", "") if embedder else ""
        self._embed_dim = int(getattr(embedder, "_dim", 0) or 0)
        self._cfg = dict(
            min_confidence=min_confidence,
            include_weak=include_weak,
            link_threshold=link_threshold,
            damping=damping,
            max_iter=max_iter,
            max_hops=max_hops,
            max_edges=max_edges,
            top_chunks=top_chunks,
        )
        self._cache: dict[str, tuple[float, GraphSearcher]] = {}
        self._stale_warned: set[str] = set()

    def _path(self, character_id: str | None):
        from pathlib import Path

        cid = (character_id or "").strip() or "default"
        safe = cid.replace("/", "_").replace("\\", "_")
        return Path(self._dir) / f"graph_{safe}.json"

    def get(self, character_id: str | None) -> GraphSearcher | None:
        path = self._path(character_id)
        try:
            mtime = path.stat().st_mtime
        except OSError:
            self._cache.pop(path.name, None)
            return None
        cached = self._cache.get(path.name)
        if cached is not None and cached[0] == mtime:
            return cached[1]
        store = GraphStore(path, min_confidence=self._cfg["min_confidence"])
        if not store.entities():
            return None
        if not store.check_fingerprint(self._embedder_name, self._embed_dim):
            if path.name not in self._stale_warned:
                self._stale_warned.add(path.name)
                logger.warning(
                    "图谱 %s 指纹失配（embedder/schema 变更），已跳过图谱检索；"
                    "请运行 scripts/build_graph.py --rebuild 重建",
                    path.name,
                )
            return None
        searcher = GraphSearcher(
            store,
            self._kb,
            namespace=f"graph_{(character_id or '').strip() or 'default'}",
            embedder=self._embedder,
            **self._cfg,
        )
        self._cache[path.name] = (mtime, searcher)
        return searcher

    def peek(self, character_id: str | None) -> dict:
        """状态探查（调试 API 用）：存在性 / 是否过期 / 统计。"""
        path = self._path(character_id)
        if not path.exists():
            return {"exists": False, "stale": False, "stats": {}, "path": str(path)}
        store = GraphStore(path, min_confidence=self._cfg["min_confidence"])
        stale = not store.check_fingerprint(self._embedder_name, self._embed_dim)
        return {
            "exists": True,
            "stale": stale,
            "stats": store.stats(),
            "path": str(path),
        }
