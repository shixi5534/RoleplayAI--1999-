# -*- coding: utf-8 -*-
"""Compendium GraphRAG —— 配置。

**独立性契约**：本包不 import 任何 ``roleplay.*`` 模块，不读写
``data/knowledge``、``data/lore`` 等既有资产，所有配置走 ``CMPRAG_`` 前缀，
与既有 ``ROLEPLAY_`` / ``plot_*`` / ``graph_*`` 命名空间零交集。
"""
from __future__ import annotations

import os
from dataclasses import dataclass, field, replace
from functools import lru_cache
from pathlib import Path

# 仓库根：src/compendium_rag/config.py -> parents[2]
ROOT = Path(__file__).resolve().parents[2]

# Compendium 本地副本（vendor 下的只读数据源）
DEFAULT_SOURCE = ROOT / "vendor" / "Reverse1999-Story-Compendium"
DEFAULT_READABLE = DEFAULT_SOURCE / "readable" / "story_zh_CN_chapter_edition"

# 本库独占的数据目录，与既有系统的知识库目录完全分离（互不读写）
DEFAULT_DATA_DIR = ROOT / "data" / "compendium_rag"


def _load_dotenv(path: Path) -> dict[str, str]:
    """最小 .env 读取（不引入 python-dotenv 依赖）。仅取 KEY=VALUE 行。"""
    out: dict[str, str] = {}
    if not path.exists():
        return out
    for raw in path.read_text(encoding="utf-8", errors="ignore").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        out[k.strip()] = v.strip().strip('"').strip("'")
    return out


_ENV_FILE = _load_dotenv(ROOT / ".env")


def _env(name: str, default: str = "") -> str:
    """先查进程环境变量，再查 .env 文件。"""
    v = os.environ.get(name)
    if v is not None and v != "":
        return v
    return _ENV_FILE.get(name, default) or default


def _env_int(name: str, default: int) -> int:
    try:
        return int(_env(name, str(default)))
    except ValueError:
        return default


def _env_float(name: str, default: float) -> float:
    try:
        return float(_env(name, str(default)))
    except ValueError:
        return default


def _env_bool(name: str, default: bool) -> bool:
    raw = _env(name, "").strip().lower()
    if not raw:
        return default
    return raw in ("1", "true", "yes", "on", "y")


def _env_opt_int(name: str) -> int | None:
    """未设置 / 空 / 非法 → ``None``（不是 0）。用于「None 表示关闭」的旋钮。"""
    raw = _env(name, "").strip()
    if not raw:
        return None
    try:
        return int(raw)
    except ValueError:
        return None


def _env_opt_float(name: str) -> float | None:
    """未设置 / 空 / 非法 → ``None``（不是 0.0）。用于「None 表示关闭」的旋钮。"""
    raw = _env(name, "").strip()
    if not raw:
        return None
    try:
        return float(raw)
    except ValueError:
        return None


@dataclass(frozen=True)
class Settings:
    """Compendium GraphRAG 设置。全部可用 ``CMPRAG_`` 环境变量覆盖。"""

    # ── 数据源 ──
    source_dir: Path = DEFAULT_READABLE
    data_dir: Path = DEFAULT_DATA_DIR
    categories: tuple[str, ...] = (
        "mainline", "activity", "character", "anecdote", "appendix_unbound",
    )

    # ── 分块 ──
    chunk_chars: int = field(default_factory=lambda: _env_int("CMPRAG_CHUNK_CHARS", 900))
    chunk_overlap_turns: int = field(
        default_factory=lambda: _env_int("CMPRAG_CHUNK_OVERLAP_TURNS", 1))
    min_chunk_chars: int = field(default_factory=lambda: _env_int("CMPRAG_MIN_CHUNK_CHARS", 120))

    # ── 云端 LLM（全部抽取走云端）──
    llm_base_url: str = field(
        default_factory=lambda: _env("CMPRAG_LLM_BASE_URL")
        or _env("ROLEPLAY_LLM_BASE_URL", "http://127.0.0.1:7863/v1"))
    llm_api_key: str = field(
        default_factory=lambda: _env("CMPRAG_LLM_API_KEY")
        or _env("ROLEPLAY_LLM_API_KEY"))
    llm_model: str = field(
        default_factory=lambda: _env("CMPRAG_LLM_MODEL", "cn:kimi-k2.6"))
    llm_temperature: float = field(
        default_factory=lambda: _env_float("CMPRAG_LLM_TEMPERATURE", 0.1))
    llm_max_tokens: int = field(
        default_factory=lambda: _env_int("CMPRAG_LLM_MAX_TOKENS", 2048))
    llm_timeout: float = field(
        default_factory=lambda: _env_float("CMPRAG_LLM_TIMEOUT", 120.0))
    llm_concurrency: int = field(
        default_factory=lambda: _env_int("CMPRAG_LLM_CONCURRENCY", 8))
    llm_max_retries: int = field(
        default_factory=lambda: _env_int("CMPRAG_LLM_MAX_RETRIES", 3))

    # ── 嵌入（图谱实体链接 / 向量兜底）：本地 Ollama bge-m3 ──
    embed_base_url: str = field(
        default_factory=lambda: _env("CMPRAG_EMBED_BASE_URL")
        or _env("ROLEPLAY_OLLAMA_BASE_URL", "http://localhost:11434"))
    embed_model: str = field(
        default_factory=lambda: _env("CMPRAG_EMBED_MODEL", "bge-m3"))
    embed_dim: int = field(default_factory=lambda: _env_int("CMPRAG_EMBED_DIM", 1024))
    embed_timeout: float = field(
        default_factory=lambda: _env_float("CMPRAG_EMBED_TIMEOUT", 120.0))

    # ── 图谱 ──
    edge_min_confidence: float = field(
        default_factory=lambda: _env_float("CMPRAG_EDGE_MIN_CONFIDENCE", 0.5))
    alias_link_threshold: float = field(
        default_factory=lambda: _env_float("CMPRAG_ALIAS_LINK_THRESHOLD", 0.90))

    # ── 检索 ──
    ppr_damping: float = field(default_factory=lambda: _env_float("CMPRAG_PPR_DAMPING", 0.85))
    ppr_max_iter: int = field(default_factory=lambda: _env_int("CMPRAG_PPR_MAX_ITER", 50))
    # 图通道保留的边数上限。2026-10-09 前是 retriever 里的字面量 30，**从未被观测过**：
    # P3 步骤1 抽样 24 题里 23 题有种子，这 23 题的返回边数**全部正好等于 30**
    # （触顶率 23/23 = 100%），即这个截断在每题上都在切东西。接成参数 ≠ 调参数——
    # 默认值必须仍是 30；真要改就得按 §4bis 冷启动重校准，并两档同报。
    graph_max_edges: int = field(default_factory=lambda: _env_int("CMPRAG_GRAPH_MAX_EDGES", 30))
    top_k: int = field(default_factory=lambda: _env_int("CMPRAG_TOP_K", 6))
    # 融合候选池宽度（G1 修复）：**与 top_k 解耦**。top_k 只控输出条数，
    # 池宽控"进入 RRF 融合的候选有多少"。None = 按 max(top_k*4, 24) 推导，
    # 与改造前的行为逐位等价；显式设值则直接用它（ES 的 rank_window_size 语义）。
    retrieval_pool_top_n: int | None = field(
        default_factory=lambda: _env_opt_int("CMPRAG_RETRIEVAL_POOL_TOP_N"))
    # 向量通道余弦相似度下限（G2 修复）。**默认 None = 完全关闭**，
    # 关掉时逐结果与改造前一致（LightRAG 曾因绝对阈值造成"全空"而移除该字段）。
    # 本仓库 bge-m3 中文语料实测分布 0.32–0.67 / 中位 0.50（k1c300 n=4578，
    # p10=0.4247），不要套用 BGE 模型卡那个 [0.6,1] 区间。
    # 标定流程见计划 D3；未标定前不得默认开启。
    retrieval_vector_min_score: float | None = field(
        default_factory=lambda: _env_opt_float("CMPRAG_RETRIEVAL_VECTOR_MIN_SCORE"))
    entity_link_top: int = field(default_factory=lambda: _env_int("CMPRAG_ENTITY_LINK_TOP", 6))
    seed_score_threshold: float = field(
        default_factory=lambda: _env_float("CMPRAG_SEED_SCORE_THRESHOLD", 0.34))
    vector_weight: float = field(
        default_factory=lambda: _env_float("CMPRAG_VECTOR_WEIGHT", 1.0))
    graph_weight: float = field(
        default_factory=lambda: _env_float("CMPRAG_GRAPH_WEIGHT", 1.0))
    # 词面通道（BM25 变体，不依赖实体链接/嵌入）。
    # 默认 0.0 = 关闭，保持历史行为逐位可复现；经 300cn 选定的生产值为 **1.0**
    # （2026-09-28 盲测验收：盲测 206 题裸检索 0.6748 -> 0.8301，up=32 / down=0）。
    # 启用方式：CMPRAG_LEX_WEIGHT=1.0。
    # ⚠ 启用后评测语义变化，按 §4bis 必须**冷启动重新校准**（eval300 + 泛化 + 安全线）
    #   才能引用新数字，不得与历史基线直接比较。
    lex_weight: float = field(
        default_factory=lambda: _env_float("CMPRAG_LEX_WEIGHT", 0.0))
    lex_top: int = field(default_factory=lambda: _env_int("CMPRAG_LEX_TOP", 30))
    # 融合重构：把词面通道前 N 名提到最前（0=关闭，保持历史行为）。
    # 经 300cn 选定的值为 **3**：裸检索 300cn 0.8316->0.8469、盲测 0.8301->0.9126。
    # ⚠ 与冻结重排的交互是集合相关的，启用需冷启动重新校准（§4bis）。
    lex_first: int = field(default_factory=lambda: _env_int("CMPRAG_LEX_FIRST", 0))
    # RRF 的排名折扣常数 k（score = Σ w/(k+rank)）。默认 60 = 历史行为（逐位可复现）。
    # k 越小，各通道**头部名次**的相对权重越大：k=60 时 rank1 与 rank6 只差
    # 1/61 vs 1/66（+8%），而 k=1 时是 1/2 vs 1/7（3.5×）——
    # 即小 k 让"在多个通道都排前列"的候选显著胜出，压过"只在单通道霸榜"的候选。
    # 前序会话只扫过**通道权重**（w_lex 1→16）而从未扫过 k，故这是未探索的杠杆。
    rrf_k: int = field(default_factory=lambda: _env_int("CMPRAG_RRF_K", 60))
    context_max_chars: int = field(
        default_factory=lambda: _env_int("CMPRAG_CONTEXT_MAX_CHARS", 3000))

    # ── 派生路径 ──
    @property
    def corpus_path(self) -> Path:
        return self.data_dir / "corpus.json"

    @property
    def graph_path(self) -> Path:
        return self.data_dir / "graph.json"

    @property
    def index_path(self) -> Path:
        return self.data_dir / "chunk_index.npz"

    @property
    def cache_dir(self) -> Path:
        return self.data_dir / "cache"

    @property
    def reports_dir(self) -> Path:
        return self.data_dir / "reports"

    def ensure_dirs(self) -> None:
        for d in (self.data_dir, self.cache_dir, self.reports_dir):
            d.mkdir(parents=True, exist_ok=True)

    def with_(self, **kw) -> "Settings":
        return replace(self, **kw)


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
