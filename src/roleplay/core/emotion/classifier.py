"""轻量本地情绪分类器：零依赖「哈希特征 + 逻辑回归头」。

架构师 ADR-3（P1 落地）：
- 特征：字符/词哈希（复用 HashingEmbedder 思路：``hashlib.md5`` + 768 维，
  CJK 按「单字 unigram + 相邻 bigram」哈希，英数整词哈希）。
- 分类头：15 类逻辑回归，权重为**内置常量**（每类种子关键词表 + 稀疏系数 + bias），
  随代码分发、确定性构建（同一关键词 → 同一 md5 索引 → 同一权重）。
- 推理：同步计算经 ``asyncio.to_thread`` 跑，不阻塞事件循环。
- 依赖：numpy 可选（缺失时回退纯 Python ``math`` 点积，功能照常）。
- jina 后端（P1.5）仅留接口位：backend="jina" 时自动禁用，绝不上抛。

设计说明（P1 启发式权重 + 精确命中去碰撞）：
- 768 维特征哈希天然存在 bigram 索引碰撞（实测「不错/不通」等会撞同一桶），
  纯哈希打分会在中性文本上误报。因此分类决策采用「精确关键词命中」：
  文本的 unigram/bigram 集合 ⊇ 种子关键词的 unigram/bigram 集合 → 该类计数 +coef。
  哈希线性头只用于把命中强度换算成 [0,1] 置信分（logit → sigmoid）。
- 语义：无任何种子关键词精确命中 → neutral（绝不在中性文本上误报）；
  命中多个类 → 累计 coef 最高者胜出；置信分与 emotion_confidence_threshold 可比。

本文件不 import detector 模块（避免循环导入）；仅依赖 models/chat 与 stdlib。
"""
import asyncio
import hashlib
import logging
import math
import re

from ...models.chat import EmotionInfo

logger = logging.getLogger(__name__)

# 15 类顺序（与权重矩阵行序一致；索引即类别）
CLASSES: list[str] = [
    "happy", "sad", "angry", "anxious", "surprise", "fear", "neutral",
    "love", "grateful", "excited", "disappointed", "lonely", "embarrassed", "confused", "sleepy",
]
CLASS_INDEX: dict[str, int] = {name: i for i, name in enumerate(CLASSES)}

_DIM = 768

_TOKEN = re.compile(r"[A-Za-z0-9_]+|[一-鿿]")


def _md5_idx(tok: str) -> int:
    """单个 token 的确定性 md5 哈希索引（特征与权重共用）。"""
    return int(hashlib.md5(tok.encode("utf-8")).hexdigest(), 16) % _DIM


def _token_indices(keyword: str) -> list[int]:
    """关键词 → 权重特征索引（与 _hash_features 对齐）。

    规则：英数 token 整词哈希；CJK 单字关键词挂 unigram，
    多字关键词只挂相邻 bigram（避免「不/好」等高频字跨词碰撞）。
    """
    toks = _TOKEN.findall((keyword or "").lower())
    if not toks:
        toks = [keyword or " "]
    indices: list[int] = []
    for tok in toks:
        if re.fullmatch(r"[a-z0-9_]+", tok):
            indices.append(_md5_idx(tok))
        else:
            chars = list(tok)
            if len(chars) == 1:
                indices.append(_md5_idx(chars[0]))
            for i in range(len(chars) - 1):
                indices.append(_md5_idx(chars[i] + chars[i + 1]))
    return indices


def _hash_features(text: str, dim: int = _DIM) -> list[float]:
    """字符/词哈希特征（与 _token_indices 对称）：unigram(所有字) + 相邻 bigram。"""
    vec = [0.0] * dim
    toks = _TOKEN.findall((text or "").lower())
    if not toks:
        toks = [text or " "]
    for tok in toks:
        if re.fullmatch(r"[a-z0-9_]+", tok):
            vec[_md5_idx(tok)] += 1.0
        else:
            chars = list(tok)
            for ch in chars:
                vec[_md5_idx(ch)] += 1.0
            for i in range(len(chars) - 1):
                vec[_md5_idx(chars[i] + chars[i + 1])] += 1.0
    return vec


def _l2_norm(vec: list[float]) -> float:
    return math.sqrt(sum(v * v for v in vec))


def _sigmoid(x: float) -> float:
    """logit → [0,1] 概率（数值稳定）。"""
    if x >= 0:
        z = math.exp(-x)
        return 1.0 / (1.0 + z)
    z = math.exp(x)
    return z / (1.0 + z)


def _ngrams(text: str) -> tuple[set[str], set[str]]:
    """文本的 unigram 集合 + bigram 集合（用于精确关键词命中判定）。"""
    bg: set[str] = set()
    uni: set[str] = set()
    for tok in _TOKEN.findall((text or "").lower()):
        if re.fullmatch(r"[a-z0-9_]+", tok):
            bg.add(tok)
            uni.add(tok)
        else:
            chars = list(tok)
            for ch in chars:
                uni.add(ch)
            for i in range(len(chars) - 1):
                bg.add(chars[i] + chars[i + 1])
    return bg, uni


def _keyword_ngrams(keyword: str) -> tuple[set[str], set[str]]:
    """种子关键词的 unigram/bigram 集合（与 _ngrams 对齐）。"""
    toks = _TOKEN.findall((keyword or "").lower())
    if not toks:
        toks = [keyword or " "]
    uni: set[str] = set()
    bg: set[str] = set()
    for tok in toks:
        if re.fullmatch(r"[a-z0-9_]+", tok):
            bg.add(tok)
            uni.add(tok)
        else:
            chars = list(tok)
            if len(chars) == 1:
                uni.add(chars[0])
            for i in range(len(chars) - 1):
                bg.add(chars[i] + chars[i + 1])
    return uni, bg


# ───────────────────────── 内置常量：15 类种子关键词表 ─���───────────────────────
# 每类 4-6 条中文关键词（与 PRD 示例句同源）；coef 为该类命中的正权重。
# 分类决策用「精确命中」（见模块 docstring），权重用于累计同类多关键词命中强度。
_CLASS_KEYWORDS: dict[str, list[tuple[str, float]]] = {
    "happy": [("开心", 0.40), ("高兴", 0.40), ("太好了", 0.35), ("真不错", 0.35), ("满意", 0.35)],
    "sad": [("难过", 0.45), ("伤心", 0.45), ("失落", 0.40), ("沮丧", 0.40), ("难受", 0.40)],
    "angry": [("生气", 0.50), ("愤怒", 0.50), ("讨厌", 0.40), ("烦", 0.40), ("火大", 0.45)],
    "anxious": [("焦虑", 0.45), ("担心", 0.45), ("紧张", 0.40), ("不安", 0.40), ("着急", 0.40)],
    "surprise": [("天哪", 0.45), ("震惊", 0.45), ("居然", 0.40), ("竟然", 0.40), ("没想到", 0.40)],
    "fear": [("恐惧", 0.50), ("恐怖", 0.50), ("吓人", 0.45), ("危险", 0.40), ("怕", 0.45), ("吓", 0.40)],
    "love": [("爱", 0.55), ("喜欢", 0.50), ("心动", 0.45), ("想念", 0.45)],
    "grateful": [("谢谢", 0.50), ("感谢", 0.50), ("感激", 0.45), ("感恩", 0.45)],
    "excited": [("兴奋", 0.50), ("激动", 0.50), ("太激动", 0.45), ("超级开心", 0.45)],
    "disappointed": [("失望", 0.50), ("灰心", 0.45), ("没劲", 0.40), ("唉", 0.35)],
    "lonely": [("孤独", 0.50), ("寂寞", 0.50), ("孤单", 0.45), ("没人陪", 0.45)],
    "embarrassed": [("尴尬", 0.50), ("害羞", 0.45), ("丢人", 0.40), ("脸红", 0.40)],
    "confused": [("搞不懂", 0.45), ("不明白", 0.45), ("困惑", 0.45), ("糊涂", 0.40), ("想不通", 0.40)],
    "sleepy": [("困", 0.50), ("想睡", 0.45), ("犯困", 0.45), ("打哈欠", 0.40), ("好累", 0.40)],
}

# 非 neutral 类的 bias：仅用于哈希头的置信分基准（无命中时分类决策已回 neutral）
_NEG_BIAS = -0.10


def _build_sparse_table() -> tuple:
    """由种子关键词常量确定性构建稀疏权重表。

    返回 ((class_idx, ((idx, coef), ...), bias), ...)；同一关键词哈希索引一致，
    权重完全可复现（随代码分发即内置常量表）。
    """
    rows: list[tuple[int, tuple, float]] = []
    for cls in CLASSES:
        cls_idx = CLASS_INDEX[cls]
        if cls == "neutral":
            rows.append((cls_idx, ((0, 0.0),), 0.0))
            continue
        sparse: dict[int, float] = {}
        for kw, coef in _CLASS_KEYWORDS.get(cls, []):
            for idx in _token_indices(kw):
                sparse[idx] = sparse.get(idx, 0.0) + coef
        rows.append((cls_idx, tuple(sorted(sparse.items())), _NEG_BIAS))
    return tuple(rows)


# 模块级构建一次：确定性常量表
_W: tuple = _build_sparse_table()
# 按类别索引直接取稀疏权重与 bias，避免每次推理 next(...) 线性扫描
_W_BY_CLASS: dict[int, dict[int, float]] = {
    cls_idx: dict(sparse) for cls_idx, sparse, _bias in _W
}
_W_BIAS: dict[int, float] = {cls_idx: bias for cls_idx, _sparse, bias in _W}
# 种子关键词的 unigram/bigram 集合预计算：推理热路径不再为每个关键词重复分词
_KEYWORD_NGRAM_CACHE: dict[str, list[tuple[str, float, set, set]]] = {
    cls: [
        (kw, coef, _keyword_ngrams(kw)[0], _keyword_ngrams(kw)[1])
        for kw, coef in kws
    ]
    for cls, kws in _CLASS_KEYWORDS.items()
}


# ───────────────────────── 分类头（P1 哈希 / P1.5 jina 预留） ─────────────────────────
class _ClassifierHead:
    def predict(self, vec: list[float]) -> tuple[str, float]:
        """返回 (emotion, score)。vec 为归一化后的特征向量。"""
        raise NotImplementedError


class _HashingLinearHead(_ClassifierHead):
    """哈希特征 + 逻辑回归头（内置常量权重，纯 Python 点积兜底）。

    仅用于把「已精确命中的类别」的 logit 换算成 [0,1] 置信分。
    """

    def __init__(self) -> None:
        self._np = None
        try:
            import numpy as np  # type: ignore

            self._np = np
            w = np.zeros((len(CLASSES), _DIM), dtype=np.float32)
            b = np.zeros(len(CLASSES), dtype=np.float32)
            for cls_idx, sparse, bias in _W:
                b[cls_idx] = bias
                for idx, coef in sparse:
                    w[cls_idx, idx] = coef
            self._w = w
            self._b = b
        except Exception as exc:  # noqa: BLE001
            logger.info("numpy 不可用，分类器回退纯 Python 点积：%s", exc)
            self._np = None

    def predict(self, vec: list[float]) -> tuple[str, float]:
        if self._np is not None:
            v = self._np.asarray(vec, dtype=self._np.float32)
            logits = self._w @ v + self._b
            idx = int(self._np.argmax(logits))
            return CLASSES[idx], _sigmoid(float(self._np.max(logits)))
        # 纯 Python 兜底（与 numpy 路径等价）
        best_idx = 0
        best = -math.inf
        for cls_idx, sparse, bias in _W:
            total = bias
            for i, c in sparse:
                total += c * vec[i]
            if total > best:
                best = total
                best_idx = cls_idx
        return CLASSES[best_idx], _sigmoid(best)


class _JinaHead(_ClassifierHead):
    """P1.5 预留：jina-embeddings 嵌入 + 线性头。本期不实现，构造即禁用。"""

    def __init__(self) -> None:
        self._enabled = False

    @property
    def enabled(self) -> bool:
        return self._enabled

    def predict(self, vec: list[float]) -> tuple[str, float]:
        return "neutral", 0.0


class LocalClassifierDetector:
    """本地分类器（实现 EmotionPort 语义，但不 import detector 以避免环）。

    依赖缺失（numpy / 后端不可���）时自动禁用：``available=False``，
    detect 返回 neutral/0/none，绝不上抛（降级原则）。
    """

    def __init__(
        self,
        *,
        enabled: bool = True,
        backend: str = "hashing",
        confidence: float = 0.4,
    ) -> None:
        self._enabled = enabled
        self._backend = backend
        self._confidence = confidence
        if backend == "jina":
            # P1.5 接口位：本期不实现 → 自动禁用
            self._head: _ClassifierHead | None = None
            self._available = False
            logger.info("分类器后端 jina 本期未实现，该层禁用")
        else:
            self._head = _HashingLinearHead()
            self._available = True

    @property
    def available(self) -> bool:
        return self._available

    async def detect(self, text: str) -> EmotionInfo:
        if not self._enabled or self._head is None:
            return EmotionInfo(emotion="neutral", score=0.0, source="none")
        # 同步推理丢线程池，不阻塞事件循环
        emotion, score = await asyncio.to_thread(self._predict_sync, text)
        if emotion == "neutral" or score < self._confidence:
            return EmotionInfo(emotion="neutral", score=0.0, source="none")
        return EmotionInfo(emotion=emotion, score=score, source="classifier")

    def _predict_sync(self, text: str) -> tuple[str, float]:
        """同步推理：精确关键词命中选类 → 哈希线性头算置信分。"""
        bg, uni = _ngrams(text)
        scores: dict[str, float] = {}
        for cls, kws in _KEYWORD_NGRAM_CACHE.items():
            total = 0.0
            for kw, coef, kuni, kbg in kws:
                if kuni.issubset(uni) and kbg.issubset(bg):
                    total += coef
            if total > 0:
                scores[cls] = total
        if not scores:
            return "neutral", 0.0
        best_cls = max(scores, key=scores.get)
        # 置信分：命中类的哈希 logit → sigmoid（特征含文本全部 unigram+bigram）
        vec = _hash_features(text)
        norm = _l2_norm(vec) or 1.0
        vec = [v / norm for v in vec]
        cls_idx = CLASS_INDEX[best_cls]
        sparse = _W_BY_CLASS[cls_idx]
        bias = _W_BIAS[cls_idx]
        logit = bias + sum(coef * vec[idx] for idx, coef in sparse.items())
        return best_cls, _sigmoid(logit)
