"""情感检测：策略模式（EmotionPort 抽象 + 关键词/LLM/责任链实现）。

统一 15 类情绪（原 7 类 + 新增 8 类细分）。

实现（架构师 ADR-1/2/4/5）：
- ``EmotionPort``：抽象 async 接口。
- ``KeywordEmotionDetector``：关键词正则 15 类，永不失败（责任链末层）。
- ``LLMEmotionDetector``：复用全局 LLMPort，单行 JSON 输出 + 三级解析兜底。
- ``FallbackChainDetector``：责任链 [LLM, classifier, keyword]，逐级降级，
  任何异常只 logger.warning 并继续下一级。
- ``build_emotion_detector``：按配置组装（keyword / classifier / llm / auto）。
"""
import asyncio
import json
import logging
import re
from abc import ABC, abstractmethod

from ...config import Settings, get_settings
from ...models.chat import EmotionInfo, EmotionLabel
from ..llm.base import LLMPort
from ..llm.factory import build_llm

logger = logging.getLogger(__name__)

# 15 类关键词表：原 7 类正则保留 + 新增 8 类（PRD 示例句驱动的细分情绪）。
# weight 为每次命中的分数增量；多关键词命中可叠加，最终封顶 1.0。
EMOTION_PATTERNS: dict[str, dict] = {
    "happy": {"patterns": [r"太[好棒开心]", r"喜[欢悦]", r"开心", r"哈哈", r"真不错", r"满意", r"太好了", r"棒极了"], "weight": 0.3},
    "sad": {"patterns": [r"难过", r"伤心", r"失[落望]", r"沮[丧]", r"不开心", r"难受", r"哭", r"悲痛"], "weight": 0.4},
    "angry": {"patterns": [r"生气", r"愤怒", r"烦", r"讨厌", r"垃圾", r"差劲", r"不满", r"火大"], "weight": 0.5},
    "anxious": {"patterns": [r"焦虑", r"担心", r"害怕", r"紧张", r"不安", r"着急", r"来不及", r"慌张"], "weight": 0.4},
    "surprise": {"patterns": [r"天哪", r"不敢相信", r"居然", r"竟然", r"震惊", r"没想到", r"我的天"], "weight": 0.45},
    "fear": {"patterns": [r"恐惧", r"怕死", r"吓人", r"恐怖", r"毛骨悚然", r"危险"], "weight": 0.5},
    "neutral": {"patterns": [], "weight": 0.0},
    # —— 新增 8 类（细分情绪；父类见 models/chat.EMOTION_PARENT）——
    "love": {"patterns": [r"我爱你", r"喜欢你", r"好喜欢你", r"好爱你", r"心动", r"想念", r"爱死"], "weight": 0.45},
    "grateful": {"patterns": [r"谢谢", r"感谢", r"感激", r"感恩", r"多谢", r"太感谢"], "weight": 0.4},
    "excited": {"patterns": [r"兴奋", r"激动", r"好激动", r"太激动", r"超级开心", r"耶"], "weight": 0.4},
    "disappointed": {"patterns": [r"失望", r"失落", r"沮丧", r"灰心", r"没劲", r"唉声叹气"], "weight": 0.5},
    "lonely": {"patterns": [r"孤独", r"寂寞", r"孤单", r"没人陪", r"一个人好"], "weight": 0.45},
    "embarrassed": {"patterns": [r"尴尬", r"不好意思", r"害羞", r"丢人", r"难为情", r"脸红"], "weight": 0.4},
    "confused": {"patterns": [r"搞不懂", r"不明白", r"迷惑", r"困惑", r"糊涂", r"想不通", r"怎么回事"], "weight": 0.4},
    "sleepy": {"patterns": [r"困了", r"好困", r"想睡", r"犯困", r"打哈欠", r"好累", r"累死"], "weight": 0.4},
}

# 标签别名表：LLM 输出/外部标签 → 15 类之一（normalize_emotion_label 用）。
# 键为「小写 + 去空格/下划线/连字符」后的形态。
_EMOTION_ALIASES: dict[str, str] = {
    "happy": "happy", "joy": "happy", "glad": "happy", "delighted": "happy", "cheerful": "happy",
    "sad": "sad", "unhappy": "sad", "upset": "sad", "sorrow": "sad", "grief": "sad",
    "angry": "angry", "mad": "angry", "furious": "angry", "irritated": "angry",
    "anxious": "anxious", "worried": "anxious", "nervous": "anxious", "uneasy": "anxious",
    "surprise": "surprise", "surprised": "surprise", "shocked": "surprise", "amazed": "surprise",
    "fear": "fear", "afraid": "fear", "scared": "fear", "terrified": "fear", "frightened": "fear",
    "neutral": "neutral", "calm": "neutral",
    "love": "love", "loving": "love",
    "grateful": "grateful", "thankful": "grateful", "appreciative": "grateful",
    "excited": "excited", "thrilled": "excited", "eager": "excited",
    "disappointed": "disappointed", "letdown": "disappointed", "frustrated": "disappointed",
    "lonely": "lonely", "isolated": "lonely", "solitary": "lonely",
    "embarrassed": "embarrassed", "shy": "embarrassed", "ashamed": "embarrassed", "awkward": "embarrassed",
    "confused": "confused", "puzzled": "confused", "bewildered": "confused",
    "sleepy": "sleepy", "tired": "sleepy", "drowsy": "sleepy", "fatigued": "sleepy",
}


def normalize_emotion_label(raw: object) -> EmotionLabel:
    """把任意来源的标签归一化为 15 类之一；非法/空 → neutral。

    处理流程：小写化 → strip → 去空格/下划线/连字符 → 别名表映射 → 非法回 neutral。
    """
    if raw is None:
        return "neutral"
    s = str(raw).strip().lower()
    s = re.sub(r"[\s_\-]+", "", s)
    return _EMOTION_ALIASES.get(s, "neutral")


class EmotionPort(ABC):
    """情感检测抽象端口（异步）。"""

    @abstractmethod
    async def detect(self, text: str) -> EmotionInfo:
        """返回检测到的情绪与置信度（及来源 source，仅日志用）。"""


class KeywordEmotionDetector(EmotionPort):
    """关键词正则检测器（永不失败，责任链末层）。"""

    def __init__(self, enabled: bool = True) -> None:
        self.enabled = enabled

    async def detect(self, text: str) -> EmotionInfo:
        if not self.enabled:
            return EmotionInfo(emotion="neutral", score=0.0, source="keyword")
        scores: dict[str, float] = {}
        for emotion, cfg in EMOTION_PATTERNS.items():
            score = 0.0
            for pat in cfg["patterns"]:
                for m in re.finditer(pat, text):
                    start = max(0, m.start() - 2)
                    prefix = text[start : m.start()]
                    if re.search(r"[不没别]", prefix):  # 否定词前缀：避免"不生气"误判
                        continue
                    score += cfg["weight"]
            if score > 0:
                scores[emotion] = score
        if not scores:
            return EmotionInfo(emotion="neutral", score=0.0, source="keyword")
        best = max(scores, key=scores.get)
        # 分数封顶 1.0，保持 [0,1] 契约直觉（多关键词命中时可能 >1）
        return EmotionInfo(
            emotion=best, score=min(1.0, round(scores[best], 2)), source="keyword"
        )


class LLMEmotionDetector(EmotionPort):
    """LLM 辅助情绪检测（复用全局 LLMPort，JSON 输出 + 三级解析兜底）。

    - 提示词要求单行 JSON ``{"emotion": "<15类之一>", "score": 0-1, "reason": "..."}``，
      温度固定 0.0（确定性优先）。
    - 解析三级兜底：``json.loads`` → 正则抽 ``"emotion":"..."`` → neutral（记 parse_fail）。
    - 超时/异常只 logger.warning 不抛出；低置信结果下沉（返回 neutral，由责任链继续）。
    - 注：LLMPort 接口不透传 max_tokens，故 max_tokens=64 仅以提示词约束（不新建客户端）。
    """

    _SYSTEM_PROMPT = (
        "你是情绪识别助手。只输出单行 JSON，不要任何其他文字："
        '{"emotion": "<15类之一>", "score": 0.0-1.0, "reason": "<一句话，可选>"}。'
        "15 类：happy,sad,angry,anxious,surprise,fear,neutral,"
        "love,grateful,excited,disappointed,lonely,embarrassed,confused,sleepy。"
    )

    def __init__(
        self,
        *,
        llm: LLMPort | None = None,
        timeout: float = 8.0,
        confidence: float = 0.4,
        enabled: bool = True,
        settings: Settings | None = None,
    ) -> None:
        self._llm = llm
        self._timeout = timeout
        self._confidence = confidence
        self._enabled = enabled
        self._parse_fail = 0
        # 未注入 llm 时尝试按 settings 构建全局 LLMPort（复用连接池/重试/脱敏）
        if self._llm is None and settings is not None:
            try:
                self._llm = build_llm(settings)
            except Exception as exc:  # noqa: BLE001
                logger.warning("LLM 情绪检测器构建失败，该层禁用：%s", exc)
                self._llm = None
        if self._llm is None:
            self._enabled = False

    @property
    def enabled(self) -> bool:
        return self._enabled

    async def detect(self, text: str) -> EmotionInfo:
        if not self._enabled or self._llm is None:
            return EmotionInfo(emotion="neutral", score=0.0, source="none")
        try:
            raw = await asyncio.wait_for(
                self._llm.generate(
                    system=self._SYSTEM_PROMPT, user=text, temperature=0.0
                ),
                timeout=self._timeout,
            )
        except asyncio.TimeoutError:
            logger.warning("LLM 情绪检测超时（%.1fs）", self._timeout)
            return EmotionInfo(emotion="neutral", score=0.0, source="none")
        except Exception as exc:  # noqa: BLE001
            logger.warning("LLM 情绪检测失败：%s", exc)
            return EmotionInfo(emotion="neutral", score=0.0, source="none")
        info = self._parse_json(raw or "")
        # 低置信 → 中性（责任链下沉下一级；中性本身也继续下沉）
        if info.emotion != "neutral" and info.score < self._confidence:
            return EmotionInfo(emotion="neutral", score=0.0, source="llm")
        return info

    def _parse_json(self, raw: str) -> EmotionInfo:
        """三级解析：json.loads → 正则抽 emotion → neutral 兜底（记 parse_fail）。"""
        text = raw.strip()
        if not text:
            self._parse_fail += 1
            return EmotionInfo(emotion="neutral", score=0.0, source="llm")
        # 容忍 ```json 代码块包裹
        if text.startswith("```"):
            text = re.sub(r"^```(?:json)?\s*", "", text).strip()
            text = re.sub(r"\s*```$", "", text).strip()
        try:
            obj = json.loads(text)
        except (json.JSONDecodeError, TypeError, ValueError):
            m = re.search(r'"emotion"\s*:\s*"([^"]+)"', text)
            if m:
                return self._build(m.group(1), text)
            self._parse_fail += 1
            logger.warning("LLM 情绪输出解析失败：%r", raw[:120])
            return EmotionInfo(emotion="neutral", score=0.0, source="llm")
        if not isinstance(obj, dict):
            self._parse_fail += 1
            return EmotionInfo(emotion="neutral", score=0.0, source="llm")
        emotion = normalize_emotion_label(obj.get("emotion", ""))
        try:
            score = float(obj.get("score", 0.0))
        except (TypeError, ValueError):
            score = 0.0
        score = max(0.0, min(1.0, score))
        return EmotionInfo(emotion=emotion, score=score, source="llm")

    def _build(self, emotion_raw: str, text: str) -> EmotionInfo:
        """正则兜底：从原始文本重建 EmotionInfo（score 尽力抽取，缺省 0.0）。"""
        emotion = normalize_emotion_label(emotion_raw)
        m = re.search(r'"score"\s*:\s*([0-9.]+)', text)
        score = max(0.0, min(1.0, float(m.group(1)))) if m else 0.0
        return EmotionInfo(emotion=emotion, score=score, source="llm")


class FallbackChainDetector(EmotionPort):
    """责任链：按序尝试注入的检测器，逐级降级。

    - 每级：``try: r = await det.detect(text); if r.emotion != "neutral" and r.score > 0: return r``，
      任何异常只 logger.warning 并继续下一级。
    - 关键词层永不失败（不抛异常），故链必有兜底。
    - 全部下沉 → neutral/0/none。
    """

    def __init__(self, chain: list[EmotionPort] | None = None) -> None:
        self.chain = list(chain or [])

    async def detect(self, text: str) -> EmotionInfo:
        for det in self.chain:
            try:
                r = await det.detect(text)
            except Exception as exc:  # noqa: BLE001
                logger.warning(
                    "情绪检测器 %s 异常，降级下一级：%s", type(det).__name__, exc
                )
                continue
            # 采纳条件（ADR-4 语义：上层只在中性/低置信时下沉）：
            # 非 neutral 且 score>0 才采纳；neutral 一律继续下一级（分类器/关键词更敏感）。
            if r.emotion != "neutral" and r.score > 0:
                return r
        return EmotionInfo(emotion="neutral", score=0.0, source="none")


def _llm_layer_available(s: Settings) -> bool:
    """LLM 层是否可用：非 mock 且 api_key 非空（auto 模式隐私约束：不私自外发）。"""
    return s.llm_provider != "mock" and bool(s.llm_api_key)


def build_emotion_detector(
    *, enabled: bool = True, settings: Settings | None = None
) -> EmotionPort:
    """按配置组装检测器（签名保持向后兼容：``build_emotion_detector(enabled=...)``）。

    组装逻辑（ADR-5）：
    - enabled=False → 恒 neutral 的关键词层（原有行为）。
    - emotion_detector=keyword → 仅关键词。
    - classifier → 分类器 + 关键词（分类器不可用时仅关键词）。
    - llm → LLM + 分类器 + 关键词（LLM 不可用则降级 classifier→keyword）。
    - auto → LLM 可用时同 llm；否则同 classifier；分类器也不可用时仅关键词。
    """
    s = settings or get_settings()
    kw = KeywordEmotionDetector(enabled=enabled)
    if not enabled:
        return kw

    # 延迟导入避免循环（classifier 顶部 import EmotionPort from .detector）
    from .classifier import LocalClassifierDetector

    cls_det = LocalClassifierDetector(
        enabled=True,
        backend=s.emotion_classifier_backend,
        confidence=s.emotion_confidence_threshold,
    )

    mode = s.emotion_detector
    use_llm = mode in ("llm", "auto") and _llm_layer_available(s)
    use_cls = mode in ("classifier", "llm", "auto") and cls_det.available

    if not use_llm and not use_cls:
        return kw

    parts: list[EmotionPort] = []
    if use_llm:
        llm_det = LLMEmotionDetector(
            llm=build_llm(s),
            timeout=s.emotion_llm_timeout,
            confidence=s.emotion_confidence_threshold,
        )
        if llm_det.enabled:
            parts.append(llm_det)
    if use_cls:
        parts.append(cls_det)
    parts.append(kw)
    if len(parts) == 1:
        return kw
    return FallbackChainDetector(chain=parts)
