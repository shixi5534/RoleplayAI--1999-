# -*- coding: utf-8 -*-
"""图谱存储：实体/边/别名，原子落盘，来源溯源。

设计取舍：
- **纯 Python dict + JSON**，零第三方依赖（networkx/neo4j 都不引入）——
  本库语料规模（数千块）下内存图完全够用，且便于测试与审阅；
- 每条边强制携带 ``chunk_ids`` 与 ``evidence``：**可溯源到原文**，
  这是图谱 RAG 不产生幻觉的底线；
- 头部写 ``fingerprint``（语料指纹 + 模型 + 提示词版本 + schema 版本），
  语料或抽取模型变更后拒绝复用旧图谱，避免"图谱与语料漂移"。
"""
from __future__ import annotations

import json
import re
from dataclasses import asdict, dataclass, field
from pathlib import Path

SCHEMA_VERSION = "1"


@dataclass
class Entity:
    eid: str
    name: str
    type: str = "概念"
    aliases: list[str] = field(default_factory=list)
    desc: str = ""
    mentions: int = 0
    chunk_ids: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return asdict(self)

    @staticmethod
    def from_dict(d: dict) -> "Entity":
        return Entity(eid=d["eid"], name=d.get("name", ""), type=d.get("type", "概念"),
                      aliases=list(d.get("aliases") or []), desc=d.get("desc", ""),
                      mentions=int(d.get("mentions") or 0),
                      chunk_ids=list(d.get("chunk_ids") or []))


@dataclass
class Edge:
    src: str
    dst: str
    relation: str
    confidence: float = 0.0
    evidence: str = ""
    chunk_ids: list[str] = field(default_factory=list)
    count: int = 1

    @property
    def key(self) -> tuple[str, str, str]:
        return (self.src, self.relation, self.dst)

    def to_dict(self) -> dict:
        return asdict(self)

    @staticmethod
    def from_dict(d: dict) -> "Edge":
        return Edge(src=d["src"], dst=d["dst"], relation=d.get("relation", ""),
                    confidence=float(d.get("confidence") or 0.0),
                    evidence=d.get("evidence", ""),
                    chunk_ids=list(d.get("chunk_ids") or []),
                    count=int(d.get("count") or 1))


# ── 实体归一（union-find）──

class _DSU:
    def __init__(self) -> None:
        self.p: dict[str, str] = {}

    def find(self, x: str) -> str:
        self.p.setdefault(x, x)
        while self.p[x] != x:
            self.p[x] = self.p[self.p[x]]
            x = self.p[x]
        return x

    def union(self, a: str, b: str) -> None:
        ra, rb = self.find(a), self.find(b)
        if ra != rb:
            self.p[rb] = ra


# 西文全名的分隔符：`伊索尔德·冯·迪塔斯多夫` / `Ada Lovelace`
RE_FULLNAME_SEP = ("·", "・", "‧", "•", " ")

# 「组织·成员角色」型构造的尾词。
# 本作大量使用 `组织·身份` 的写法指代该组织的**无名成员**：
#   重塑·信徒 / 重塑·门徒 / 重塑·暴徒 / 重塑·坏蛋
# 它**不是** `名·姓` 式的全名，而是"某组织的一个信徒"。若按全名规则
# `重塑` + `·` + `信徒` 会把「重塑之手」这个**敌对组织**与其**杂兵**合并成
# 同一实体（实测发生：重塑之手 → 重塑·信徒，两者语义完全不同）。
# 因此尾词命中此表时不做分隔符归并。
GENERIC_ROLE_SUFFIX = frozenset({
    "信徒", "门徒", "暴徒", "坏蛋", "成员", "手下", "部下", "士兵", "兵",
    "首领", "头目", "干部", "使者", "代言人", "追随者", "拥护者", "走狗",
    "杂兵", "小兵", "护卫", "守卫", "仆从", "仆人", "学徒", "研究员",
    "工程师", "医生", "护士", "工人", "农民", "商人", "顾客", "观众",
})


# 同一构造的成员编号：`重塑·门徒Ⅰ` / `重塑·门徒2` 与 `重塑·门徒` 是同一类
# 「组织·身份」写法，编号只是同台分身的标记。不先剥掉它，
# `tail in GENERIC_ROLE_SUFFIX` 会漏判，组织又被焊回成员身上。
RE_MEMBER_INDEX = re.compile(r"[0-9０-９ⅠⅡⅢⅣⅤⅥⅦⅧⅨⅩⅪⅫ①②③④⑤⑥⑦⑧⑨⑩]+$")


def _merge_candidates(names: list[str], alias_edges: list[tuple[str, str]]) -> _DSU:
    """构造合并关系：别名声明的等价 + 保守的全名/简称归并。"""
    dsu = _DSU()
    for n in names:
        dsu.find(n)

    # ① 别名声明（来自抽取结果 aliases 字段）
    for a, b in alias_edges:
        if a in dsu.p and b in dsu.p:
            dsu.union(a, b)

    # ② 保守全名归并：长名 = 短名 + 分隔符 + 其余
    #    `伊索尔德` + `伊索尔德·冯·迪塔斯多夫` → 合并
    #    但「组织·成员角色」（`重塑` + `·` + `信徒`）**不合并**，见 GENERIC_ROLE_SUFFIX。
    by_len = sorted(names, key=len)
    for i, short in enumerate(by_len):
        if len(short) < 2:
            continue
        for long in by_len[i + 1:]:
            if not long.startswith(short):
                continue
            rest = long[len(short):]
            if not rest or rest[0] not in RE_FULLNAME_SEP:
                continue
            tail = rest.lstrip("".join(RE_FULLNAME_SEP))
            if RE_MEMBER_INDEX.sub("", tail) in GENERIC_ROLE_SUFFIX or tail.endswith("们"):
                continue          # `组织·成员` 构造，不是全名
            dsu.union(long, short)
    return dsu


def canonical_pick(members: list[str],
                   counts: dict[str, int] | None = None) -> str:
    """从同一实体的多个写法里选最规范的名称。

    优选顺序（`counts` 为该写法的出现次数）：
      1. **出现次数最多**——"语料里最常用的叫法"是最可靠的规范化依据，
         比任何形态规则都稳；
      2. 中文全名（含 `·`）优先于简称；
      3. 长度更长者优先；
      4. 字典序，保证结果确定。

    修复背景：早期只按"含分隔符 + 长度"排序，导致「重塑之手」（组织，
    出现 37 次）被选成「重塑·信徒」（杂兵标签）—— 次数优先级能避免这类误选。
    """
    if counts:
        def score(n: str) -> tuple:
            has_sep = any(s in n for s in RE_FULLNAME_SEP)
            return (-counts.get(n, 0), 0 if has_sep else 1, -len(n))
    else:
        def score(n: str) -> tuple:
            has_sep = any(s in n for s in RE_FULLNAME_SEP)
            return (0, 0 if has_sep else 1, -len(n))
    return sorted(members, key=lambda n: (score(n), n))[0]


class GraphStore:
    """实体关系图（内存 + JSON 落盘）。"""

    def __init__(self, fingerprint: str = "") -> None:
        self.fingerprint = fingerprint
        self.entities: dict[str, Entity] = {}
        self.edges: list[Edge] = []
        self.alias_index: dict[str, str] = {}   # 任意写法 -> eid
        self._edge_index: dict[tuple[str, str, str], Edge] = {}

    # ── 构建 ──

    def build_from_extractions(
        self,
        per_chunk: list[tuple[str, object]],
        *,
        min_confidence: float = 0.0,
    ) -> dict:
        """从 ``[(chunk_id, Extraction), ...]`` 构建图谱。

        分三步：收集观察 → 实体归一 → 加边。返回构建统计。
        """
        # ① 收集
        obs_entities: dict[str, dict] = {}     # name -> {types, aliases, descs}
        obs_edges: list[tuple[str, str, str, float, str, str]] = []
        chunk_speakers: dict[str, list[str]] = {}

        for chunk_id, ex in per_chunk:  # type: ignore[assignment]
            if ex is None or not getattr(ex, "ok", True):
                continue
            if not getattr(ex, "entities", None) and not getattr(ex, "relations", None):
                continue
            for e in ex.entities:  # type: ignore[attr-defined]
                if not e.name:
                    continue
                o = obs_entities.setdefault(
                    e.name, {"types": {}, "aliases": set(), "descs": {}})
                o["types"][e.type] = o["types"].get(e.type, 0) + 1
                o["aliases"].update(a for a in e.aliases if a)
                if e.desc:
                    o["descs"][e.desc] = o["descs"].get(e.desc, 0) + 1
            for r in ex.relations:  # type: ignore[attr-defined]
                if r.confidence < min_confidence:
                    continue
                obs_edges.append((r.src, r.dst, r.relation, r.confidence,
                                  r.evidence, chunk_id))
                obs_entities.setdefault(
                    r.src, {"types": {}, "aliases": set(), "descs": {}})
                obs_entities.setdefault(
                    r.dst, {"types": {}, "aliases": set(), "descs": {}})

        # ② 归一：别名 + 全名/简称
        names = sorted(obs_entities.keys())
        alias_edges: list[tuple[str, str]] = []
        for n, o in obs_entities.items():
            for a in o["aliases"]:
                if a != n:
                    alias_edges.append((n, a))
        dsu = _merge_candidates(names, alias_edges)

        groups: dict[str, list[str]] = {}
        for n in names:
            groups.setdefault(dsu.find(n), []).append(n)

        self.entities.clear()
        self.alias_index.clear()
        name_to_eid: dict[str, str] = {}
        for root, members in groups.items():
            # 各写法的观察次数 = 被抽到的次数 + 被声明为别名的次数，
            # 用于挑选"语料里最常用的叫法"作为规范名
            obs_count: dict[str, int] = {}
            for m in members:
                o = obs_entities[m]
                obs_count[m] = (sum(o["types"].values())
                                + sum(o["descs"].values()))
            canon = canonical_pick(members, obs_count)
            eid = canon
            name_to_eid.update({m: eid for m in members})
            types: dict[str, int] = {}
            aliases: set[str] = set()
            descs: dict[str, int] = {}
            for m in members:
                o = obs_entities[m]
                for t, c in o["types"].items():
                    types[t] = types.get(t, 0) + c
                aliases.update(o["aliases"])
                for d, c in o["descs"].items():
                    descs[d] = descs.get(d, 0) + c
            etype = max(types.items(), key=lambda kv: kv[1])[0] if types else "概念"
            desc = max(descs.items(), key=lambda kv: kv[1])[0] if descs else ""
            aliases.discard(canon)
            aliases -= set(members)
            self.entities[eid] = Entity(
                eid=eid, name=canon, type=etype,
                aliases=sorted(aliases), desc=desc)
            for m in members:
                self.alias_index[m] = eid
            for a in aliases:
                self.alias_index.setdefault(a, eid)

        # ③ 加边（合并同一三元组的多次观察）
        self.edges.clear()
        self._edge_index.clear()
        merged: dict[tuple[str, str, str], Edge] = {}
        for src, dst, rel, conf, ev, chunk_id in obs_edges:
            s = name_to_eid.get(src)
            d = name_to_eid.get(dst)
            if not s or not d or s == d:
                continue
            key = (s, rel, d)
            e = merged.get(key)
            if e is None:
                e = Edge(src=s, dst=d, relation=rel, confidence=conf,
                         evidence=ev, chunk_ids=[chunk_id])
                merged[key] = e
            else:
                e.count += 1
                e.confidence = max(e.confidence, conf)
                if chunk_id not in e.chunk_ids:
                    e.chunk_ids.append(chunk_id)
                if not e.evidence and ev:
                    e.evidence = ev
        self.edges = list(merged.values())
        self._edge_index = merged

        # ④ 提及统计：实体名/别名在 chunk 文本中的出现次数
        self._count_mentions(per_chunk)
        return self.stats()

    def _count_mentions(self, per_chunk: list[tuple[str, object]]) -> None:
        for chunk_id, ex in per_chunk:  # type: ignore[assignment]
            if ex is None:
                continue
            for e in ex.entities:  # type: ignore[attr-defined]
                eid = self.alias_index.get(e.name)
                if not eid:
                    continue
                ent = self.entities.get(eid)
                if ent is None:
                    continue
                ent.mentions += 1
                if chunk_id not in ent.chunk_ids:
                    ent.chunk_ids.append(chunk_id)

    # ── 查询 ──

    def resolve(self, name: str) -> str | None:
        """任意写法 → eid。"""
        if not name:
            return None
        return self.alias_index.get(name.strip())

    def neighbors(self, eid: str) -> list[Edge]:
        return [e for e in self.edges if e.src == eid or e.dst == eid]

    def out_edges(self, eid: str) -> list[Edge]:
        return [e for e in self.edges if e.src == eid]

    def edge_chunk_ids(self) -> dict[str, list[str]]:
        """chunk_id -> 涉及它的边索引（证据回查用）。"""
        out: dict[str, list[int]] = {}
        for i, e in enumerate(self.edges):
            for cid in e.chunk_ids:
                out.setdefault(cid, []).append(i)
        return out

    # ── 持久化 ──

    def to_dict(self) -> dict:
        return {
            "schema": f"compendium_rag.graph/v{SCHEMA_VERSION}",
            "fingerprint": self.fingerprint,
            "entities": [e.to_dict() for e in self.entities.values()],
            "edges": [e.to_dict() for e in self.edges],
        }

    @staticmethod
    def from_dict(d: dict) -> "GraphStore":
        g = GraphStore(fingerprint=d.get("fingerprint", ""))
        for ed in d.get("entities", []):
            e = Entity.from_dict(ed)
            g.entities[e.eid] = e
            g.alias_index[e.name] = e.eid
            for a in e.aliases:
                g.alias_index.setdefault(a, e.eid)
        g.edges = [Edge.from_dict(x) for x in d.get("edges", [])]
        g._edge_index = {e.key: e for e in g.edges}
        return g

    def save(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        tmp = path.with_suffix(path.suffix + ".tmp")
        tmp.write_text(json.dumps(self.to_dict(), ensure_ascii=False),
                       encoding="utf-8")
        tmp.replace(path)

    @staticmethod
    def load(path: Path) -> "GraphStore":
        return GraphStore.from_dict(json.loads(path.read_text(encoding="utf-8")))

    def check_fingerprint(self, expected: str) -> tuple[bool, str]:
        if not self.fingerprint:
            return False, "图谱缺少 fingerprint"
        if self.fingerprint != expected:
            return False, f"指纹不匹配：图谱={self.fingerprint} 期望={expected}"
        return True, "ok"

    # ── 统计 ──

    def stats(self) -> dict:
        by_type: dict[str, int] = {}
        for e in self.entities.values():
            by_type[e.type] = by_type.get(e.type, 0) + 1
        by_rel: dict[str, int] = {}
        for e in self.edges:
            by_rel[e.relation] = by_rel.get(e.relation, 0) + 1
        connected: set[str] = set()
        for e in self.edges:
            connected.add(e.src)
            connected.add(e.dst)
        iso = [eid for eid in self.entities if eid not in connected]
        n = len(self.entities) or 1
        return {
            "entities": len(self.entities),
            "edges": len(self.edges),
            "entity_types": dict(sorted(by_type.items(), key=lambda kv: -kv[1])),
            "relation_types": len(by_rel),
            "top_relations": sorted(by_rel.items(), key=lambda kv: -kv[1])[:20],
            "isolated_entities": len(iso),
            "isolated_ratio": round(len(iso) / n, 4),
            "multi_edge_entities": sum(
                1 for eid in self.entities if len(self.neighbors(eid)) > 1),
        }


def fingerprint_of(corpus_fp: str, model: str, prompt_version: str,
                   chunk_chars: int) -> str:
    """图谱身份指纹：任一要素变化即失效。"""
    import hashlib
    h = hashlib.sha256()
    for part in (SCHEMA_VERSION, corpus_fp, model, prompt_version, str(chunk_chars)):
        h.update(part.encode("utf-8"))
        h.update(b"|")
    return h.hexdigest()[:16]
