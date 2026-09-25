# -*- coding: utf-8 -*-
"""检索链路结构化埋点（Spec 的 M-11 / F8a）。

为什么必须有这一层
    三个真实痛点，且都**无法从现有数据看出来**：
    1. **跳过是静默的**——`semantic_items` 为空既可能是"索引没建"，也可能是"本轮无候选"，
       代码里两者长得完全一样，看板的空态因此无法编码（架构 §7.6 原文）；
    2. **"没发生"与"没跑到"在数据上长得一样**——负样本零注入既可能是"护栏有效"，
       也可能是"语义链接压根没触发"，不给执行计数就无法区分（本项目最重要的方法论产出）；
    3. **通道有货但被融合层挤出**（桶 4）此前完全不可观测——`via` 恒为 `plot_graph`，
       图谱占比是个恒 1.0 的无效指标。

三条硬纪律（架构 §7.6.5）
    1. **埋点失败绝不影响检索**：全程 try-except，异常时 `trace=None` 并记 warning；
    2. **不写查询原文**：只写 `query_hash`（sha256 前 16 位）；
    3. **计时用 `time.perf_counter()`**，与 eval 脚本同口径。

落盘双轨（用途不同，不可互相替代）
    A. 运行期 jsonl：`data/knowledge/_audit/retrieval_trace/<cid>.jsonl`（默认**关**，
       `plot_trace_enabled`；常开会污染 p95）
    B. 评测报告内嵌：`trace` 段由 M-12 聚合产出（评测默认开）
"""
from __future__ import annotations

import hashlib
import json
import logging
import time
from dataclasses import asdict, dataclass, field
from enum import Enum
from pathlib import Path

logger = logging.getLogger(__name__)

TRACE_SCHEMA = "retrieval-trace-v1"
ABLATION_SCHEMA = "ablation-v1"

# 六通道固定顺序（架构 §7.6.1）：下游看板/报告的瀑布图按此顺序渲染，
# **顺序不可调**——它是"每通道每轮必有一条记录"这一契约的载体。
CHANNEL_ORDER = ("别名精确", "BM25 兜底", "语义向量", "图传播", "篇章路由", "扩展查询")

# 机器口径 path -> 展示口径通道名。`mention` 块按种子来源归组（seed_path），
# 由 ChannelRecord.of_chunk 处理——这是本契约最容易被实现者搞错的一点。
PATH_TO_CHANNEL = {
    "exact": "别名精确",
    "lexical": "BM25 兜底",
    "semantic": "语义向量",
    "edge": "图传播",
    "chapter": "篇章路由",
    "semantic_zh": "扩展查询",
    "mention": "图传播",  # 兜底；实际由 seed_path 决定
}


class ChannelSkipReason(str, Enum):
    """通道跳过原因（9 值固定，架构 §7.6.2）——设计师瀑布图空态的数据源。"""

    NOT_ENABLED = "not_enabled"
    INDEX_MISSING = "index_missing"
    FINGERPRINT_STALE = "fingerprint_stale"
    EMBED_FAILED = "embed_failed"
    NO_SEED = "no_seed"
    GATE_REJECTED = "gate_rejected"
    NO_CANDIDATE = "no_candidate"
    RERANK_UNAVAILABLE = "rerank_unavailable"
    BUDGET_EXHAUSTED = "budget_exhausted"


SKIP_REASONS = tuple(r.value for r in ChannelSkipReason)


def query_hash(query: str) -> str:
    """查询指纹（sha256 前 16 位）。**绝不落盘查询原文**（PRD §9 隐私约束）。"""
    return hashlib.sha256((query or "").encode("utf-8")).hexdigest()[:16]


def config_hash(config: dict) -> str:
    """影响检索的 plot_* 配置快照指纹（同一配置的多次运行才可比）。"""
    payload = json.dumps(
        {k: v for k, v in sorted((config or {}).items()) if str(k).startswith("plot_")},
        ensure_ascii=False, sort_keys=True, default=str,
    )
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()[:16]


def channel_of_block(path: str, meta: dict) -> str | None:
    """块级 path（+ ``seed_path``）→ 展示口径通道名。

    ``mention`` 块按**种子来源**归组：种子的来源决定它算「别名精确」还是「语义向量」。
    这是本契约最容易被实现者搞错的一点（架构 §7.6.1 说明栏原文点名），
    因此**候选计数与保留计数必须共用本函数**——否则两边归组口径漂移，
    ``kept_rate`` 会出现 >100% 这种不可能读数（实测踩到：种子数当分子、块数当分母）。
    """
    if path == "mention":
        seed_path = str(meta.get("seed_path") or "")
        if seed_path == "semantic":
            return "语义向量"
        if seed_path == "token":
            return "BM25 兜底"
        return "别名精确"
    return PATH_TO_CHANNEL.get(str(path))


@dataclass
class ChannelRecord:
    """``channels[]`` 的一条（每条 = 一个通道的一轮记录，共 6 条）。

    ``hit_count`` 与 ``hit_blocks`` 是**两个不同量纲**，不可互相替代：
      - ``hit_count``：该通道本轮命中数（按各通道自身的自然单位；「别名精确」是
        **种子来源维度**（架构 §7.6.1），故其自然单位是**种子数**）；
      - ``hit_blocks``：该通道**归因到的候选块数**（由 :func:`channel_of_block` 归组，
        与 ``kept_in_final`` 同量纲）——只有它才能与 ``kept_in_final`` 相除得到保留率。
    缺 ``hit_blocks`` 时按 ``hit_count`` 兜底（块通道两者相等）。
    """

    channel: str
    enabled: bool
    executed: bool = False
    hit_count: int = 0
    hit_blocks: int = 0
    skip_reason: str | None = None
    latency_ms: float = 0.0
    weight: float = 1.0
    kept_in_final: int = 0
    detail: dict = field(default_factory=dict)

    def __post_init__(self) -> None:
        # 未显式给 hit_blocks 时与 hit_count 同值（块通道的常态）
        if not self.hit_blocks:
            self.hit_blocks = int(self.hit_count or 0)

    def finish(self, skip_reason: "ChannelSkipReason | str | None" = None) -> None:
        """出口统一收口：``hit_count == 0`` 时必须带 ``skip_reason``（契约硬约束）。"""
        if self.hit_count == 0:
            self.skip_reason = (
                skip_reason.value if isinstance(skip_reason, ChannelSkipReason)
                else (skip_reason or ChannelSkipReason.NO_CANDIDATE.value)
            )
        else:
            self.skip_reason = None


@dataclass
class EntityLinkMargin:
    """``entity_link_margin`` 子结构——AC-3 阈值标定的**唯一**依据。"""

    triggered: bool = False
    candidates: int = 0
    top1_score: float | None = None
    top2_score: float | None = None
    margin: float | None = None
    threshold: float = 0.5
    linked: bool = False
    reject_reason: str | None = None

    def fill(self, scores: list[float], *, threshold: float, linked: bool,
             reject_reason: str | None = None) -> None:
        self.triggered = True
        self.candidates = len(scores)
        if scores:
            ordered = sorted(scores, reverse=True)
            self.top1_score = float(ordered[0])
            self.top2_score = float(ordered[1]) if len(ordered) > 1 else None
            # 只有一个候选时 margin 无定义 -> None（不是 0，0 会被误读成"两个候选分数相同"）
            self.margin = (float(ordered[0] - ordered[1]) if len(ordered) > 1 else None)
        self.threshold = float(threshold)
        self.linked = bool(linked)
        self.reject_reason = reject_reason


@dataclass
class RetrievalTrace:
    """一次 ``retrieve()`` 调用的完整 trace（字段与架构 §7.6.4 顶层表逐一对应）。"""

    character_id: str = ""
    query_lang: str = "other"
    query_len: int = 0
    pipeline_version: str = "plot-v1.0"
    config_hash: str = ""
    seeds_total: int = 0
    seeds: list[dict] = field(default_factory=list)
    channels: list[ChannelRecord] = field(default_factory=list)
    entity_link_margin: EntityLinkMargin = field(default_factory=EntityLinkMargin)
    fallbacks: list[str] = field(default_factory=list)
    latency: dict = field(default_factory=dict)
    final_chunks: int = 0
    final_paths: dict = field(default_factory=dict)
    # 以下由 finish() 填充，不在构造参数里
    event: str = "retrieval_trace"
    trace_schema: str = TRACE_SCHEMA
    query_hash: str = ""
    timestamp: str = ""

    def __post_init__(self) -> None:
        if not self.channels:
            self.channels = [
                ChannelRecord(channel=name, enabled=False) for name in CHANNEL_ORDER
            ]

    # —— 通道读写 ——
    def channel(self, name: str) -> ChannelRecord:
        for rec in self.channels:
            if rec.channel == name:
                return rec
        rec = ChannelRecord(channel=name, enabled=False)
        self.channels.append(rec)
        return rec

    def mark(self, name: str, *, executed: bool | None = None,
             hit_count: int | None = None, skip_reason=None, weight: float | None = None,
             enabled: bool | None = None, hit_blocks: int | None = None,
             **detail) -> ChannelRecord:
        rec = self.channel(name)
        if enabled is not None:
            rec.enabled = enabled
        if executed is not None:
            rec.executed = executed
        if hit_count is not None:
            rec.hit_count = int(hit_count)
        if hit_blocks is not None:
            rec.hit_blocks = int(hit_blocks)
        elif hit_count is not None and not rec.hit_blocks:
            rec.hit_blocks = int(hit_count)
        if weight is not None:
            rec.weight = float(weight)
        if detail:
            rec.detail.update(detail)
        if hit_count is not None:
            rec.finish(skip_reason)
        elif skip_reason is not None:
            rec.finish(skip_reason)
        return rec

    def fallback(self, reason: "ChannelSkipReason | str") -> None:
        v = reason.value if isinstance(reason, ChannelSkipReason) else str(reason)
        if v not in self.fallbacks:
            self.fallbacks.append(v)

    # —— 收口 ——
    def finish(self, *, query: str, final_chunks: list | None = None,
               latency: dict | None = None) -> "RetrievalTrace":
        self.query_hash = query_hash(query)
        self.query_len = len(query or "")
        self.timestamp = time.strftime("%Y-%m-%dT%H:%M:%S")
        self.final_chunks = len(final_chunks or [])
        paths: dict[str, int] = {}
        for c in final_chunks or []:
            for p in ((getattr(c, "metadata", None) or {}).get("paths") or []):
                paths[p] = paths.get(p, 0) + 1
        self.final_paths = paths
        if latency:
            self.latency = latency
        if final_chunks is not None:
            self._attribute_kept(final_chunks)
        return self

    def _attribute_kept(self, final_chunks: list) -> None:
        """把最终块的 ``paths`` 归因回六通道（``kept_in_final``）。

        这里是桶 4「融合层稀释」的量化入口：``hit_count - kept_in_final`` 即"有货没进"。
        ``mention`` 块按 ``seed_path`` 归组——种子的来源决定它算"别名精确"还是"扩展查询"。
        """
        counts: dict[str, int] = {name: 0 for name in CHANNEL_ORDER}
        for c in final_chunks:
            meta = getattr(c, "metadata", None) or {}
            for p in (meta.get("paths") or []):
                name = self._channel_of_path(p, meta)
                if name:
                    counts[name] = counts.get(name, 0) + 1
        for rec in self.channels:
            rec.kept_in_final = int(counts.get(rec.channel, 0))

    @staticmethod
    def _channel_of_path(path: str, meta: dict) -> str | None:
        return channel_of_block(path, meta)

    def to_dict(self) -> dict:
        d = asdict(self)
        d["channels"] = [asdict(c) for c in self.channels]
        return d


# ── 落盘（轨道 A：运行期 jsonl，默认关）──────────────────────────────
def trace_path(base_dir: str | Path, character_id: str) -> Path:
    return Path(base_dir) / "_audit" / "retrieval_trace" / f"{character_id}.jsonl"


def append_jsonl(path: str | Path, trace: RetrievalTrace) -> bool:
    """追加一条 trace。**任何异常都吞掉**——埋点失败绝不能影响检索主链路。"""
    try:
        p = Path(path)
        p.parent.mkdir(parents=True, exist_ok=True)
        with p.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(trace.to_dict(), ensure_ascii=False) + "\n")
        return True
    except Exception as exc:  # noqa: BLE001
        logger.warning("检索埋点落盘失败（不影响检索）：%s", exc)
        return False


class TraceCollector:
    """检索器侧的埋点收集器：计时 + 通道登记 + 异常零传播。

    用法（在 ``retrieve()`` 内）::

        tc = TraceCollector(enabled=..., character_id=..., config=..., out_path=...)
        with tc.stage("link_ms"):
            ...
        tc.trace.mark("图传播", hit_count=len(edge_items), weight=...)
        tc.finish(query=query, final_chunks=out)
    """

    def __init__(self, *, enabled: bool, character_id: str = "", config: dict | None = None,
                 out_path: str | Path | None = None, pipeline_version: str = "plot-v1.0",
                 query_lang: str = "other") -> None:
        self.enabled = bool(enabled)
        self.out_path = out_path
        self._stages: dict[str, float] = {}
        self._t0 = time.perf_counter()
        self._t_last = self._t0
        if self.enabled:
            self.trace: RetrievalTrace | None = RetrievalTrace(
                character_id=character_id,
                config_hash=config_hash(config or {}),
                pipeline_version=pipeline_version,
                query_lang=query_lang,
            )
        else:
            self.trace = None

    # —— 计时 ——
    def stage(self, name: str) -> "_Stage":
        return _Stage(self, name)

    def _enter(self) -> None:
        self._t_last = time.perf_counter()

    def _exit(self, name: str) -> None:
        now = time.perf_counter()
        self._stages[name] = self._stages.get(name, 0.0) + (now - self._t_last) * 1000.0
        self._t_last = now

    # —— 便捷登记（trace 关闭时全部为 no-op）——
    def mark(self, *args, **kwargs):
        if self.trace is not None:
            try:
                return self.trace.mark(*args, **kwargs)
            except Exception as exc:  # noqa: BLE001
                logger.warning("埋点登记失败（不影响检索）：%s", exc)
        return None

    def fallback(self, reason) -> None:
        if self.trace is not None:
            try:
                self.trace.fallback(reason)
            except Exception as exc:  # noqa: BLE001
                logger.warning("埋点降级登记失败：%s", exc)

    def set_seeds(self, seeds: dict) -> None:
        if self.trace is None:
            return
        try:
            self.trace.seeds_total = len(seeds or {})
            self.trace.seeds = [
                {"entity_id": str(eid),
                 "name": str((info or {}).get("name") or ""),
                 "seed_path": str((info or {}).get("path") or ""),
                 "weight": float((info or {}).get("weight") or 0.0),
                 "specificity": float((info or {}).get("specificity", 1.0)),
                 "gate_passed": bool((info or {}).get("gate_passed", True))}
                for eid, info in (seeds or {}).items()
            ]
        except Exception as exc:  # noqa: BLE001
            logger.warning("埋点种子登记失败：%s", exc)

    def finish(self, *, query: str, final_chunks: list | None) -> RetrievalTrace | None:
        if self.trace is None:
            return None
        try:
            self._stages["total_ms"] = (time.perf_counter() - self._t0) * 1000.0
            self.trace.finish(query=query, final_chunks=final_chunks,
                              latency=dict(self._stages))
            if self.out_path is not None:
                append_jsonl(self.out_path, self.trace)
            return self.trace
        except Exception as exc:  # noqa: BLE001
            logger.warning("埋点收口失败（不影响检索）：%s", exc)
            return None


class _Stage:
    """``with tc.stage("link_ms"):`` —— 异常照常向上抛，计时照常收口。"""

    def __init__(self, tc: TraceCollector, name: str) -> None:
        self._tc = tc
        self._name = name

    def __enter__(self) -> "_Stage":
        self._tc._enter()
        return self

    def __exit__(self, *exc) -> bool:
        self._tc._exit(self._name)
        return False
