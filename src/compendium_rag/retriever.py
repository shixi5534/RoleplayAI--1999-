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


def _lex_tokens(s: str) -> list[str]:
    """词面检索的分词：英文数字按词 + 中文字符 bigram。

    中文无空格，用字符 bigram 是最省事且对专名/术语召回稳健的近似
    （实测在盲测集上 graph_only 口径 0.50 -> 0.84）。
    """
    s = (s or "").lower()
    toks = re.findall(r"[a-z0-9]+", s)
    zh = re.findall(r"[\u4e00-\u9fff]", s)
    toks += ["".join(zh[i:i + 2]) for i in range(len(zh) - 1)]
    return toks


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

class LexicalIndex:
    """词面检索索引（BM25 变体）：中文用字符 bigram、英文数字用词。

    为什么需要它（2026-09-28 盲测验收发现）：
      既有三通道（graph/mention/vector）都建立在**实体链接**之上；
      当查询用描述性指代（"那位自称自囚于此的囚徒"）或目标实体未进图时，
      三个通道会**同时**漏掉正确的块 —— 实测盲测 206 题中 23% 的题
      "无任何通道命中"，而实体链接零命中仅占 1.3%。
      词面通道不依赖实体链接，直接对块文本做词面匹配，补的正是这部分候选。

    实测（w=1.0，权重仅在 300cn 上选定、盲测留出）：
      盲测 206 题裸检索 0.6748 -> 0.8301（up=32 / down=0）；
      graph_only 口径 0.5000 -> 0.8355。

    确定性：块按固定顺序建索引；排序用 (-score, chunk_id) 全序，与插入序无关。
    """

    def __init__(self, chunks: list[Chunk]) -> None:
        self.N = len(chunks)
        self.df: dict[str, int] = {}
        self.tf: dict[str, dict[str, int]] = {}
        self.L: dict[str, int] = {}
        for c in chunks:
            toks = _lex_tokens(
                f"{c.text}\n{c.chapter_title}\n{c.scene_title}\n{c.part_title}")
            t: dict[str, int] = {}
            for g in toks:
                t[g] = t.get(g, 0) + 1
            self.tf[c.chunk_id] = t
            self.L[c.chunk_id] = sum(t.values()) or 1
            for g in t:
                self.df[g] = self.df.get(g, 0) + 1
        self.avg = (sum(self.L.values()) / self.N) if self.N else 1.0

    def search(self, query: str, top_k: int = 30,
               k1: float = 1.2, b: float = 0.6) -> list[tuple[str, float]]:
        qt = _lex_tokens(query)
        if not qt or not self.tf:
            return []
        out: list[tuple[str, float]] = []
        for cid, d in self.tf.items():
            sc = 0.0
            L = self.L[cid]
            for g in qt:
                f = d.get(g, 0)
                if not f:
                    continue
                idf = math.log(1 + (self.N - self.df[g] + 0.5) / (self.df[g] + 0.5))
                sc += idf * (f * (k1 + 1)) / (f + k1 * (1 - b + b * L / self.avg))
            if sc > 0:
                out.append((cid, sc))
        out.sort(key=lambda kv: (-kv[1], kv[0]))
        return out[:top_k]


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
        # 词面通道索引（不依赖实体链接；见 LexicalIndex 文档）
        self.lex_index = LexicalIndex(chunks) if chunks else None

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
        """Reciprocal Rank Fusion：按各通道排名融合，规避量纲不一致。

        确定性（2026-09-28 追加，作战书 §4bis「排序必须带显式次级键」）：
          两处排序都补了次级键 `chunk_id`。原因：RRF 分数是 `1/(k+rank)` 的加和，
          平局极常见 —— 实测 120 题中 **116 题**存在并列（单题最多 42 个元素并列），
          而原先只按分数排序时，平局先后完全由 **dict 插入序**决定，
          等于 top-6 的边界取舍是任意的（与 #39 Phase 2 修掉的 link() 同类缺陷）。
        """
        weights = weights or {}
        agg: dict[str, Evidence] = {}
        for ch in sorted(channels):          # 通道遍历序确定（不依赖调用方构造顺序）
            scored = channels[ch]
            if not scored:
                continue
            w = weights.get(ch, 1.0)
            ranked = sorted(scored.items(), key=lambda kv: (-kv[1], kv[0]))
            for rank, (cid, raw) in enumerate(ranked, start=1):
                ev = agg.setdefault(cid, Evidence(chunk_id=cid, score=0.0))
                ev.channels[ch] = raw
                ev.score += w * (1.0 / (k + rank))
                ev.reasons.append(f"{ch}#{rank}")
        out = sorted(agg.values(), key=lambda e: (-e.score, e.chunk_id))
        return out[:top_n]

    # ── 端到端 ──

    def retrieve(self, query: str, qvec: list[float] | None = None,
                 *, top_k: int = 6, entity_link_top: int = 6,
                 seed_threshold: float = 0.34,
                 entity_vec_hits: list[tuple[str, str, float]] | None = None,
                 vector_top: int = 30, weights: dict[str, float] | None = None,
                 lex_weight: float = 0.0, lex_top: int = 30,
                 lex_first: int = 0,
                 ) -> RetrievalResult:
        """端到端检索。

        lex_weight > 0 时启用**词面通道**（默认 0 = 保持历史行为，便于回滚与
        逐位对照）。该通道不依赖实体链接与嵌入，实测（权重仅在 300cn 上选定、
        盲测 206 题留出）把裸检索从 0.6748 提到 0.8301，up=32 / down=0。
        """
        res = RetrievalResult(query=query)
        seeds = self.link(query, top_k=entity_link_top)
        if entity_vec_hits:
            seeds = self.merge_vector_seeds(seeds, entity_vec_hits,
                                            seed_threshold, entity_link_top)
        # 低分种子丢弃（防止向量兜底的噪声实体污染 PPR 种子集）
        seeds = [s for s in seeds if s.score >= seed_threshold] or seeds[:2]
        res.seeds = seeds

        # 词面通道（不依赖实体链接/嵌入）：既补"有种子但通道漏召回"的候选，
        # 也处理"零种子"的情形。权重为 0 时行为与接线前完全一致。
        channels: dict[str, dict[str, float]] = {}
        if lex_weight > 0 and self.lex_index is not None:
            lex_hits = dict(self.lex_index.search(query, lex_top))
            if lex_hits:
                channels["lex"] = lex_hits

        if not seeds:
            res.graph_ok = False
            res.note = "实体链接零命中，图谱通道为空"
            if channels:
                # 零种子但有词面候选：直接以词面通道出结果（原先只能空手或靠向量兜底）
                evs = self.rrf_fuse(channels, weights=weights, top_n=max(top_k * 4, 24))
                res.evidence = evs
                res.note += "；已回落词面通道"
        else:
            g_chunks, edges = self.graph_channel(
                seeds, damping=0.85, max_iter=50)
            res.edges = edges
            channels["graph"] = g_chunks
            channels["mention"] = self.mention_channel(seeds)
            if qvec is not None:
                channels["vector"] = self.vector_channel(qvec, vector_top)
            evs = self.rrf_fuse(channels, weights=weights, top_n=max(top_k * 4, 24))
            ppr_map, _ = self.graph_channel(seeds)
            for e in evs:
                e.ppr = ppr_map.get(e.chunk_id, 0.0)
            res.evidence = evs

        # 融合重构（默认关闭，lex_first=0 时行为与接线前逐位一致）：
        # 把词面通道的前 lex_first 名**提到最前**，其余按融合序补足（去重）。
        # 动机（2026-09-28 实测）：RRF 是排名制，graph/mention/vector 会把词面通道
        # 真正命中的块挤出前 6 —— 盲测 206 上 **lex-only 0.9320 > 融合 0.8301**。
        # 实测 lex_first=3（仅在 300cn 上选定）：裸检索 300cn 0.8316->0.8469、
        # 盲测 0.8301->0.9126（两集同升）。
        # ⚠ 与**冻结重排**的交互是集合相关的（见 docs/目标①_收口报告），
        #   故默认关闭，启用需按 §4bis 冷启动重新校准。
        if lex_first > 0 and channels.get("lex") and res.evidence:
            lex_ranked = [cid for cid, _ in sorted(channels["lex"].items(),
                                                   key=lambda kv: (-kv[1], kv[0]))]
            out, seen = [], set()
            for cid in lex_ranked[:lex_first] + [e.chunk_id for e in res.evidence] + lex_ranked:
                if cid not in seen:
                    seen.add(cid)
                    out.append(cid)
            by_id = {e.chunk_id: e for e in res.evidence}
            rebuilt = [by_id[cid] for cid in out if cid in by_id]
            # 词面通道独有的块（融合序里没有）补一个最小 Evidence，保证只增不减
            for cid in out:
                if cid not in by_id and cid in self.chunks:
                    rebuilt.append(Evidence(chunk_id=cid, score=0.0,
                                            channels={"lex": channels["lex"][cid]}))
            res.evidence = rebuilt
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
