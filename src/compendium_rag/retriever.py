# -*- coding: utf-8 -*-
"""图谱检索：实体链接 → PPR 展开激活 → 证据收集 → 三通道融合。

算法来源与取舍：
- **个性化 PageRank（PPR）** 作为图上的"展开激活"：以查询命中的实体为种子，
  边权 = confidence × 观察次数（对数压缩）作为转移权重，迭代至收敛。
  相比朴素 k-hop BFS，PPR 能让多跳关联自然浮到前排，且天然抑制热门节点的
  无差别扩散（这是 HippoRAG 系列在 multi-hop 上的核心增益点）。
- **三通道召回**：图通道（PPR 高分边挂的原文块）+ 提及通道（种子实体自身的
  出现块，覆盖属性类问题）+ 向量通道（bge-m3 语义兜底，覆盖图谱漏抽时）。
  三路用 RRF 融合——避免各通道分数量纲不一致导致的权重调参地狱。
"""
from __future__ import annotations

import json
import math
import re
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np

from .chunker import Chunk
from .embedder import cosine
from .graph_store import Edge, GraphStore


@dataclass
class Seed:
    eid: str
    name: str
    score: float
    how: str      # exact | alias | vector


@dataclass
class Evidence:
    chunk_id: str
    score: float
    channels: dict[str, float] = field(default_factory=dict)
    ppr: float = 0.0
    reasons: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {"chunk_id": self.chunk_id, "score": round(self.score, 6),
                "channels": {k: round(v, 6) for k, v in self.channels.items()},
                "ppr": round(self.ppr, 6), "reasons": self.reasons}


@dataclass
class RetrievalResult:
    query: str
    seeds: list[Seed] = field(default_factory=list)
    evidence: list[Evidence] = field(default_factory=list)
    edges: list[tuple[str, str, str, float]] = field(default_factory=list)
    graph_ok: bool = True
    note: str = ""

    def to_dict(self) -> dict:
        return {
            "query": self.query,
            "graph_ok": self.graph_ok,
            "note": self.note,
            "seeds": [{"eid": s.eid, "name": s.name,
                       "score": round(s.score, 6), "how": s.how} for s in self.seeds],
            "edges": [{"src": s, "relation": r, "dst": d, "ppr": round(p, 6)}
                      for s, r, d, p in self.edges],
            "evidence": [e.to_dict() for e in self.evidence],
        }


class ChunkIndex:
    """块向量索引（npz：向量矩阵 + chunk_id 顺序）。"""

    def __init__(self, chunk_ids: list[str], matrix: np.ndarray) -> None:
        self.chunk_ids = chunk_ids
        self.matrix = matrix
        self._pos = {c: i for i, c in enumerate(chunk_ids)}

    @property
    def size(self) -> int:
        return len(self.chunk_ids)

    @staticmethod
    def build(chunk_ids: list[str], vectors: list[list[float]]) -> "ChunkIndex":
        if not vectors:
            return ChunkIndex(list(chunk_ids), np.zeros((0, 0), dtype=np.float32))
        m = np.asarray(vectors, dtype=np.float32)
        if m.ndim == 1:                      # 空输入或单条退化情形
            m = m.reshape(1, -1) if m.size else np.zeros((0, 0), dtype=np.float32)
        if m.size == 0:
            return ChunkIndex(list(chunk_ids), np.zeros((0, 0), dtype=np.float32))
        norms = np.linalg.norm(m, axis=1, keepdims=True)
        norms[norms == 0] = 1.0
        return ChunkIndex(list(chunk_ids), m / norms)

    def search(self, qvec: list[float], top_k: int) -> list[tuple[str, float]]:
        if self.matrix.size == 0:
            return []
        q = np.asarray(qvec, dtype=np.float32)
        n = np.linalg.norm(q)
        if n == 0:
            return []
        q = q / n
        sims = self.matrix @ q
        k = min(top_k, len(sims))
        idx = np.argpartition(-sims, k - 1)[:k]
        idx = idx[np.argsort(-sims[idx])]
        return [(self.chunk_ids[i], float(sims[i])) for i in idx]

    def save(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        np.savez_compressed(path, chunk_ids=np.array(self.chunk_ids, dtype=object),
                            matrix=self.matrix)

    @staticmethod
    def load(path: Path) -> "ChunkIndex":
        d = np.load(path, allow_pickle=True)
        return ChunkIndex([str(x) for x in d["chunk_ids"]], d["matrix"])


class EntityVectorIndex:
    """实体名向量索引（查询侧实体链接的向量兜底）。"""

    def __init__(self, eids: list[str], names: list[str], matrix: np.ndarray) -> None:
        self.eids = eids
        self.names = names
        self.matrix = matrix

    @staticmethod
    def build(eids: list[str], names: list[str],
              vectors: list[list[float]]) -> "EntityVectorIndex":
        if not vectors:
            return EntityVectorIndex(list(eids), list(names),
                                     np.zeros((0, 0), dtype=np.float32))
        m = np.asarray(vectors, dtype=np.float32)
        if m.ndim == 1:
            m = m.reshape(1, -1) if m.size else np.zeros((0, 0), dtype=np.float32)
        if m.size == 0:
            return EntityVectorIndex(list(eids), list(names),
                                     np.zeros((0, 0), dtype=np.float32))
        norms = np.linalg.norm(m, axis=1, keepdims=True)
        norms[norms == 0] = 1.0
        return EntityVectorIndex(list(eids), list(names), m / norms)

    def search(self, qvec: list[float], top_k: int) -> list[tuple[str, str, float]]:
        if self.matrix.size == 0:
            return []
        q = np.asarray(qvec, dtype=np.float32)
        n = np.linalg.norm(q)
        if n == 0:
            return []
        q = q / n
        sims = self.matrix @ q
        k = min(top_k, len(sims))
        idx = np.argpartition(-sims, k - 1)[:k]
        idx = idx[np.argsort(-sims[idx])]
        return [(self.eids[i], self.names[i], float(sims[i])) for i in idx]

    def save(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        np.savez_compressed(path,
                            eids=np.array(self.eids, dtype=object),
                            names=np.array(self.names, dtype=object),
                            matrix=self.matrix)

    @staticmethod
    def load(path: Path) -> "EntityVectorIndex":
        d = np.load(path, allow_pickle=True)
        return EntityVectorIndex([str(x) for x in d["eids"]],
                                 [str(x) for x in d["names"]], d["matrix"])


# ── 实体名匹配 ──

RE_ASCII_WORD = re.compile(r"[A-Za-z0-9_]")


def _name_matches(name: str, ql: str) -> bool:
    """判断实体名是否出现在查询里（对短名/西文名做词边界约束）。

    为什么不能直接 ``name in query``：本作有大量**单字符/短西文角色名**——
    ``X``（语料 841 行）、``J``（622）、``Z``（557）、``37``（999）、``APPLe``，
    它们是货真价实的角色。朴素的子串匹配会让 ``X`` 命中任何含 x 的英文单词
    （如 "max"），也会让查询里顺便出现的字母污染种子集。
    因此：纯 ASCII 名要求**词边界**；中日韩名长度 ≥ 2 做子串匹配，
    单字同样要求边界（避免「火」命中「火焰」）。
    """
    if not name or not ql:
        return False
    is_ascii = all(ord(c) < 128 for c in name)
    if is_ascii:
        pat = re.compile(r"(?<![A-Za-z0-9_])" + re.escape(name.lower()) +
                         r"(?![A-Za-z0-9_])")
        return bool(pat.search(ql))
    if len(name) >= 2:
        return name in ql
    return bool(re.search(r"(?<![\u4e00-\u9fff])" + re.escape(name) +
                          r"(?![\u4e00-\u9fff])", ql))


# ── 图算法 ──

def build_adjacency(graph: GraphStore) -> tuple[
        dict[str, list[tuple[str, float]]], dict[str, float], list[Edge]]:
    """构造无向加权邻接表（关系是有方向的，但激活应当双向传播）。

    权重 = confidence（下限 0.1）× (1 + log(1 + count))，即"出现多次的边更可信"，
    但对数压缩防止高频边垄断转移概率。
    """
    adj: dict[str, list[tuple[str, float]]] = {}
    weight_sum: dict[str, float] = {}
    usable: list[Edge] = []
    for e in graph.edges:
        w = max(0.1, e.confidence) * (1.0 + math.log1p(max(0, e.count - 1)))
        adj.setdefault(e.src, []).append((e.dst, w))
        adj.setdefault(e.dst, []).append((e.src, w))
        weight_sum[e.src] = weight_sum.get(e.src, 0.0) + w
        weight_sum[e.dst] = weight_sum.get(e.dst, 0.0) + w
        usable.append(e)
    return adj, weight_sum, usable


def personalized_pagerank(
    adj: dict[str, list[tuple[str, float]]],
    seeds: dict[str, float],
    damping: float = 0.85,
    max_iter: int = 50,
    tol: float = 1e-6,
) -> dict[str, float]:
    """PPR 幂迭代。seeds 会先归一化为个性化向量。"""
    if not seeds:
        return {}
    total = sum(seeds.values()) or 1.0
    teleport = {k: v / total for k, v in seeds.items()}
    nodes = set(adj.keys()) | set(teleport.keys())
    score = {n: 0.0 for n in nodes}
    for n in nodes:
        score[n] = teleport.get(n, 0.0)

    for _ in range(max_iter):
        nxt = {n: (1.0 - damping) * teleport.get(n, 0.0) for n in nodes}
        dangling = 0.0
        for n in nodes:
            s = score[n]
            if s <= 0.0:
                continue
            nbrs = adj.get(n)
            if not nbrs:
                dangling += s
                continue
            wsum = sum(w for _, w in nbrs) or 1.0
            for m, w in nbrs:
                nxt[m] = nxt.get(m, 0.0) + damping * s * (w / wsum)
        if dangling:
            share = damping * dangling / len(nodes)
            for n in nodes:
                nxt[n] = nxt.get(n, 0.0) + share
        delta = sum(abs(nxt[n] - score[n]) for n in nodes)
        score = nxt
        if delta < tol:
            break
    mx = max(score.values()) or 1.0
    return {k: v / mx for k, v in score.items()}


# ── 检索引擎 ──

class GraphRetriever:
    """Compendium 图谱检索器。全部数据在内存，查询毫秒级。"""

    def __init__(self, graph: GraphStore, chunks: list[Chunk],
                 chunk_index: ChunkIndex | None = None,
                 entity_index: EntityVectorIndex | None = None) -> None:
        self.graph = graph
        self.chunks = {c.chunk_id: c for c in chunks}
        self.chunk_index = chunk_index
        self.entity_index = entity_index
        self._adj, self._wsum, self._edges = build_adjacency(graph)
        self._edge_chunks: dict[str, list[int]] = {}
        for i, e in enumerate(self._edges):
            for cid in e.chunk_ids:
                self._edge_chunks.setdefault(cid, []).append(i)
        # 实体 -> 直接提及块
        self._ent_chunks: dict[str, list[str]] = {
            eid: list(ent.chunk_ids) for eid, ent in graph.entities.items()}

    # ── ① 实体链接 ──

    def link(self, query: str, top_k: int = 6,
             threshold: float = 0.0) -> list[Seed]:
        """实体链接：名字/别名直接匹配优先，向量相似兜底。"""
        q = (query or "").strip()
        if not q:
            return []
        seeds: dict[str, Seed] = {}
        ql = q.lower()

        # 长名优先，避免「伊索」抢「伊索尔德」。
        # ⚠ 必须带**显式次级键**：Python 的 sorted 是稳定排序，只按 len 排时，
        #   同长键的先后完全由 dict 插入序决定 —— 而 alias_index 的插入序在
        #   暖进程（Applier 落盘后内存态）与冷启动（自 graph.json 重建）之间不同，
        #   实测 300 题里有 37 题的 seeds 会因此改变（#39 核验，2026-09-27）。
        #   次级键取键本身（字典序），使排序结果与插入序无关，暖冷恒等。
        cands = sorted(self.graph.alias_index.keys(), key=lambda k: (-len(k), k))
        for name in cands:
            if not _name_matches(name, ql):
                continue
            eid = self.graph.alias_index[name]
            ent = self.graph.entities[eid]
            how = "exact" if name == ent.name else "alias"
            sc = 1.0 if how == "exact" else 0.9
            cur = seeds.get(eid)
            if cur is None or sc > cur.score:
                seeds[eid] = Seed(eid, ent.name, sc, how)

        return sorted(seeds.values(), key=lambda s: -s.score)[:top_k]

    def merge_vector_seeds(self, seeds: list[Seed], hits: list[tuple[str, str, float]],
                           threshold: float, top_k: int) -> list[Seed]:
        by_eid = {s.eid: s for s in seeds}
        for eid, name, sim in hits:
            if sim < threshold:
                continue
            cur = by_eid.get(eid)
            sc = sim * 0.85       # 向量命中略低于精确匹配
            if cur is None:
                by_eid[eid] = Seed(eid, name, sc, "vector")
            elif sc > cur.score:
                cur.score, cur.how = sc, "vector"
        return sorted(by_eid.values(), key=lambda s: -s.score)[:top_k]

    # ── ② 图通道：PPR → 边 → 证据块 ──

    def graph_channel(self, seeds: list[Seed], damping: float = 0.85,
                      max_iter: int = 50, max_edges: int = 30
                      ) -> tuple[dict[str, float], list[tuple[str, str, str, float]]]:
        if not seeds:
            return {}, []
        seed_map = {s.eid: s.score for s in seeds}
        ppr = personalized_pagerank(self._adj, seed_map, damping, max_iter)

        scored: list[tuple[float, Edge]] = []
        for e in self._edges:
            # 边分 = 两端 PPR 之和 × 置信度：两跳关联自然浮起
            s = ppr.get(e.src, 0.0) + ppr.get(e.dst, 0.0)
            sc = s * max(0.1, e.confidence)
            if sc > 0:
                scored.append((sc, e))
        scored.sort(key=lambda kv: -kv[0])
        scored = scored[:max_edges]

        edges = [(e.src, e.relation, e.dst, sc) for sc, e in scored]
        chunk_scores: dict[str, float] = {}
        for sc, e in scored:
            for cid in e.chunk_ids:
                chunk_scores[cid] = max(chunk_scores.get(cid, 0.0), sc)
        return chunk_scores, edges

    # ── ③ 提及通道：种子实体自身的出现块 ──

    def mention_channel(self, seeds: list[Seed],
                        per_entity: int = 3) -> dict[str, float]:
        out: dict[str, float] = {}
        for s in seeds:
            cids = self._ent_chunks.get(s.eid, [])
            for cid in cids[:per_entity]:
                out[cid] = max(out.get(cid, 0.0), s.score)
        return out

    # ── ④ 向量通道 ──

    def vector_channel(self, qvec: list[float], top_k: int) -> dict[str, float]:
        if self.chunk_index is None:
            return {}
        hits = self.chunk_index.search(qvec, top_k)
        return {cid: sc for cid, sc in hits}

    # ── 融合（RRF）──

    @staticmethod
    def rrf_fuse(channels: dict[str, dict[str, float]], k: int = 60,
                 weights: dict[str, float] | None = None,
                 top_n: int = 20) -> list[Evidence]:
        """Reciprocal Rank Fusion：按各通道排名融合，规避量纲不一致。"""
        weights = weights or {}
        agg: dict[str, Evidence] = {}
        for ch, scored in channels.items():
            if not scored:
                continue
            w = weights.get(ch, 1.0)
            ranked = sorted(scored.items(), key=lambda kv: -kv[1])
            for rank, (cid, raw) in enumerate(ranked, start=1):
                ev = agg.setdefault(cid, Evidence(chunk_id=cid, score=0.0))
                ev.channels[ch] = raw
                ev.score += w * (1.0 / (k + rank))
                ev.reasons.append(f"{ch}#{rank}")
        out = sorted(agg.values(), key=lambda e: -e.score)
        return out[:top_n]

    # ── 端到端 ──

    def retrieve(self, query: str, qvec: list[float] | None = None,
                 *, top_k: int = 6, entity_link_top: int = 6,
                 seed_threshold: float = 0.34,
                 entity_vec_hits: list[tuple[str, str, float]] | None = None,
                 vector_top: int = 30, weights: dict[str, float] | None = None,
                 ) -> RetrievalResult:
        res = RetrievalResult(query=query)
        seeds = self.link(query, top_k=entity_link_top)
        if entity_vec_hits:
            seeds = self.merge_vector_seeds(seeds, entity_vec_hits,
                                            seed_threshold, entity_link_top)
        # 低分种子丢弃（防止向量兜底的噪声实体污染 PPR 种子集）
        seeds = [s for s in seeds if s.score >= seed_threshold] or seeds[:2]
        res.seeds = seeds

        if not seeds:
            res.graph_ok = False
            res.note = "实体链接零命中，图谱通道为空"
        else:
            g_chunks, edges = self.graph_channel(
                seeds, damping=0.85, max_iter=50)
            res.edges = edges
            channels = {
                "graph": g_chunks,
                "mention": self.mention_channel(seeds),
            }
            if qvec is not None:
                channels["vector"] = self.vector_channel(qvec, vector_top)
            evs = self.rrf_fuse(channels, weights=weights, top_n=max(top_k * 4, 24))
            ppr_map, _ = self.graph_channel(seeds)
            for e in evs:
                e.ppr = ppr_map.get(e.chunk_id, 0.0)
            res.evidence = evs
        if not res.evidence and qvec is not None:
            # 图谱零命中时的向量兜底，保证不空手而归
            v = self.vector_channel(qvec, vector_top)
            res.evidence = self.rrf_fuse({"vector": v}, top_n=top_k)
            res.note = (res.note + "；" if res.note else "") + "图谱零命中，回落向量通道"
        return res

    def context(self, res: RetrievalResult, top_k: int = 6,
                max_chars: int = 3000) -> str:
        """把检索结果渲染成可注入 LLM 的上下文（含实体卡与关系路径）。"""
        parts: list[str] = []
        if res.seeds:
            lines = ["【图谱实体】"]
            for s in res.seeds[:6]:
                ent = self.graph.entities.get(s.eid)
                if not ent:
                    continue
                ali = f"（别名：{'、'.join(ent.aliases[:4])}）" if ent.aliases else ""
                d = f" — {ent.desc}" if ent.desc else ""
                lines.append(f"- {ent.name}·{ent.type}{ali}{d}")
            parts.append("\n".join(lines))
        if res.edges:
            lines = ["【关系脉络】"]
            for s, r, d, _ in res.edges[:15]:
                lines.append(f"- {s} —{r}→ {d}")
            parts.append("\n".join(lines))
        if res.evidence:
            lines = ["【原文证据】"]
            for e in res.evidence[:top_k]:
                c = self.chunks.get(e.chunk_id)
                if not c:
                    continue
                loc = f"{c.chapter_title}"
                if c.scene_title:
                    loc += f" / {c.scene_title}"
                lines.append(f"[{loc}] {c.text}")
            parts.append("\n\n".join(lines))
        out = "\n\n".join(parts)
        return out[:max_chars]
