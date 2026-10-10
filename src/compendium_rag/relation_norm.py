# -*- coding: utf-8 -*-
"""关系谓语归一化策略（v9 优化 P1）。

三层来源，从「确证」到「兜底」：

1. vendor 词表 :mod:`relation_vocab`（canonical 77 + SYNONYM_MAP + 规则归约）；
2. 审查期 sidecar ``predicate_grouping_v1.json``（8313 个自由谓语的归组判定，
   边覆盖率 0.8545）；
3. 方向裁决表 ``relation_direction_v1.json``（人工核过原文的 swap / same_direction）。

**方向优先于合规。** ``inverse_predicate_map.json`` 的 ``direction_loss_watch``
列的是「师从 / 死于 / 隶属于」这类方向敏感形：一旦被并进方向相反的 canonical，
边的事实就反了（「A 师从 B」变成「A 指导 B」）。没有确证裁决时保留原谓语并计入
``kept:direction_blocked`` —— 合规率少一分，比把事实写反便宜得多。

丢弃只限「谓语本身不成立」的两类：否定式（把否定写成肯定边）与黑名单噪声。
超长 / 含标点 / 待审核一律**保留原谓语**：删边等于销毁证据，合规率不该用数据换。
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path
from typing import NamedTuple

from .relation_vocab import (REASON_DROP_EMPTY, REASON_DROP_JUNK,
                             REASON_DROP_NEGATION, classify_relation)

DROP_REASONS = frozenset({REASON_DROP_NEGATION, REASON_DROP_JUNK, REASON_DROP_EMPTY})

DATA_DIR = Path(__file__).resolve().parents[2] / "data" / "compendium_rag"
OVERRIDES_PATH = DATA_DIR / "predicate_grouping_v1.json"
INVERSE_MAP_PATH = DATA_DIR / "inverse_predicate_map.json"
DIRECTION_POLICY_PATH = DATA_DIR / "relation_direction_v1.json"


@dataclass(frozen=True)
class DirectionPolicy:
    """人工裁决过的方向处理：swap 要换端点，same_direction 可直接并入。"""

    swap: dict[str, str] = field(default_factory=dict)
    same_direction: frozenset[str] = frozenset()

    @staticmethod
    def load(path: Path = DIRECTION_POLICY_PATH) -> "DirectionPolicy":
        if not path.exists():
            return DirectionPolicy()
        d = json.loads(path.read_text(encoding="utf-8"))
        return DirectionPolicy(swap=dict(d.get("swap") or {}),
                              same_direction=frozenset(d.get("same_direction") or []))


def load_overrides(path: Path = OVERRIDES_PATH) -> dict[str, str]:
    """sidecar 归组表 → ``{原谓语: canonical}``；判定为无对应 canonical 的不收。"""
    if not path.exists():
        return {}
    d = json.loads(path.read_text(encoding="utf-8"))
    out: dict[str, str] = {}
    for raw, v in (d.get("mapping") or {}).items():
        canon = (v or {}).get("canonical")
        if canon:
            out[str(raw)] = str(canon)
    return out


def load_direction_signals(path: Path = INVERSE_MAP_PATH) -> tuple[frozenset[str], frozenset[frozenset[str]]]:
    """→ (方向敏感谓语集, 互逆 canonical 对集)。文件缺失时返回空集（全部走阻断）。"""
    if not path.exists():
        return frozenset(), frozenset()
    d = json.loads(path.read_text(encoding="utf-8"))
    watch = frozenset(str(x) for x in (d.get("direction_loss_watch") or []))
    pairs = frozenset(frozenset((str(a), str(b)))
                      for a, b in (d.get("inverse_pairs") or []) if a and b)
    return watch, pairs


class Mapped(NamedTuple):
    """归一结果。``relation`` 为空串表示该边应丢弃。

    ``intended`` 是「按词表本该并成的 canonical」——即使被方向闸拦下也照实记录，
    否则裁决表拿不到待办清单。``code`` 是判定来源，用于对账：
    ``canonical`` / ``synonym`` / ``rule`` / ``override`` / ``swap`` /
    ``same_direction`` / ``kept:*``（保留原谓语）/ ``drop:*``（丢弃）。
    """

    src: str
    relation: str
    dst: str
    code: str
    intended: str


@dataclass(frozen=True)
class VocabTables:
    """三层判定表的只读快照。缺文件时退化为空表（= 只走 vendor 词表）。"""

    overrides: dict[str, str] = field(default_factory=dict)
    watch: frozenset[str] = frozenset()
    inverse_pairs: frozenset[frozenset[str]] = frozenset()
    policy: DirectionPolicy = field(default_factory=DirectionPolicy)

    @staticmethod
    def load(overrides_path: Path = OVERRIDES_PATH,
             inverse_path: Path = INVERSE_MAP_PATH,
             policy_path: Path = DIRECTION_POLICY_PATH) -> "VocabTables":
        watch, pairs = load_direction_signals(inverse_path)
        return VocabTables(overrides=load_overrides(overrides_path),
                           watch=watch, inverse_pairs=pairs,
                           policy=DirectionPolicy.load(policy_path))


@lru_cache(maxsize=1)
def default_tables() -> VocabTables:
    """进程内单例：归一化对每块都跑，3695 次重复读三个 JSON 不可接受。"""
    return VocabTables.load()


def map_relation(src: str, rel: str, dst: str, *,
                 tables: VocabTables | None = None) -> Mapped:
    """把一条 ``(src, rel, dst)`` 归一。``tables=None`` 用 :func:`default_tables`。"""
    t = tables if tables is not None else default_tables()
    canon, reason = classify_relation(rel)
    if canon is None:
        if reason in DROP_REASONS:
            return Mapped(src, "", dst, reason, "")
        hit = t.overrides.get(rel)
        if hit:
            canon, reason = hit, "override"
        else:
            return Mapped(src, rel, dst, f"kept:{reason}", "")
    if canon == rel:
        return Mapped(src, rel, dst, reason, canon)

    if t.policy.swap.get(rel) == canon:
        return Mapped(dst, canon, src, "swap", canon)
    risky = rel in t.watch or frozenset((rel, canon)) in t.inverse_pairs
    if risky:
        if rel in t.policy.same_direction:
            return Mapped(src, canon, dst, "same_direction", canon)
        return Mapped(src, rel, dst, "kept:direction_blocked", canon)
    return Mapped(src, canon, dst, reason, canon)
