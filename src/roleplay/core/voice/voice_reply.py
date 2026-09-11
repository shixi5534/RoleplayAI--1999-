"""QQ 语音回复决策器：判定"本轮要不要出声、出什么声"（渠道无关，纯业务）。

链路定位（docs/QQ语音回复方案.md §3.1）：

    channels/qq_onebot.py ──► voice_reply.decide() ──► clip_store.pick()（P0）
                                              └──► tts（P1 兜底，未接）

关键语义（实现前已与方案对齐）：
- 情绪信号来自 Orchestrator 对**用户消息**的情绪检测（不是对回复的），
  即"用户难过 → 角色发 sad 槽位原声"，与前端 宠物姿态→槽位 的行为一致。
- score 口径随检测来源不同：LLM/分类器是 [0,1] 置信分；关键词层是权重累加
  （单次命中仅 0.3~0.5，多命中封顶 1.0），且关键词层只在正则真实命中时才产出
  非 neutral 标签。因此 keyword 来源的真实命中视为已达标，不做阈值比较——
  否则关键词档位部署（无 LLM）下任何情绪都过不了 0.6 阈值，功能形同虚设。
- neutral 一律不出声：责任链对 neutral 恒下沉，最终 score 恒为 0，本处再显式挡一道。
- P0 仅原声切片来源；无切片命中/任何异常 → 返回 None，由渠道降级发文字。
  绝不因为语音失败而丢回复。
"""
from __future__ import annotations

import logging
import time
from dataclasses import dataclass

from ...config import get_settings
from ...models.chat import EmotionInfo
from .clip_store import ClipEntry, ClipStore, default_manifest_path

logger = logging.getLogger(__name__)

# 情绪 → 语音槽位（照搬前端 pet-voice.js 的 POSE_TO_SLOT，保证 Web/宠物/QQ 三端
# 行为一致；并补齐前端没有的后端细分情绪）。confused→surprise 为有意保留前端
# 口径（后端 EMOTION_PARENT 的 confused→anxious 仅用于 Live2D 表情回退，两者用途
# 不同，不要互相"对齐"）。
EMOTION_TO_SLOT: dict[str, str] = {
    "happy": "happy", "love": "happy", "grateful": "happy", "excited": "happy",
    "sad": "sad", "angry": "sad", "disappointed": "sad", "lonely": "sad",
    "surprise": "surprise", "confused": "surprise", "fear": "surprise",
    "sleepy": "sleep",
    "anxious": "idle", "embarrassed": "idle", "neutral": "idle",
}


@dataclass(frozen=True)
class VoiceDecision:
    """一次"要出声"的决策产物：渠道据此拼 record 段发送。"""

    audio: bytes  # mp3 字节（base64 后走 OneBot record 段）
    kind: str  # 来源类型："clip"（P1 将增加 "tts"）
    slot: str  # 命中的槽位
    clip_id: str  # 切片 id（kind=clip 时有效）
    lang: str  # 本次配音语言
    duration: float  # 秒（切片库自带，用于时长校验与日志）
    subtitle: dict  # {"zh": ..., "en": ...} 双语台词


class VoiceReplyService:
    """会话级语音回复状态 + 触发判定。

    一个渠道实例持有一个服务实例；会话状态存内存 dict（与渠道 _session_chars
    同款，重启丢失，属设计内）。方法均为同步纯内存操作，不碰 IO（选片读文件
    在 decide 内完成，量级 ~百 KB）。
    """

    def __init__(self, settings=None, store: ClipStore | None = None) -> None:
        self.settings = settings or get_settings()
        self._store = store  # 注入则直接用（测试）；否则首次 decide 时懒加载
        self._store_failed = False
        self._enabled: dict[str, bool] = {}  # session_id -> !voice on/off 覆盖
        self._lang: dict[str, str] = {}  # session_id -> !lang 覆盖
        self._last_at: dict[str, float] = {}  # session_id -> 上次出声时刻(monotonic)
        self._last_clip: dict[str, str] = {}  # session_id -> 上次切片 id（去重）

    # ── 触发判定（P0：L1 开关 + L3 情感阈值 + 冷却；L2 关键词/L4 概率为 P1） ──
    def decide(
        self,
        session_id: str,
        emotion: EmotionInfo | None,
        *,
        is_group: bool = False,
    ) -> VoiceDecision | None:
        s = self.settings
        if not self.is_enabled(session_id):
            return None
        if is_group and not getattr(s, "qq_voice_group_enabled", False):
            return None
        if (
            emotion is None
            or emotion.emotion == "neutral"
            or emotion.emotion not in EMOTION_TO_SLOT
        ):
            return None
        # 关键词层只在正则真实命中时产出非 neutral 标签 → 视为已达标（见模块 docstring）
        threshold = float(getattr(s, "qq_voice_emotion_threshold", 0.6))
        if emotion.source != "keyword" and emotion.score < threshold:
            return None
        if not self._cooldown_ok(session_id):
            return None

        entry = self._pick(session_id, EMOTION_TO_SLOT[emotion.emotion])
        if entry is None:
            return None
        try:
            audio = self._store.read_bytes(entry) if self._store else b""
        except OSError as exc:
            logger.warning("QQ 语音：切片读取失败（%s），本轮降级文字：%s", entry.id, exc)
            return None
        if not audio:
            return None

        now = time.monotonic()
        self._last_at[session_id] = now
        self._last_clip[session_id] = entry.id
        return VoiceDecision(
            audio=audio,
            kind="clip",
            slot=EMOTION_TO_SLOT[emotion.emotion],
            clip_id=entry.id,
            lang=entry.lang,
            duration=entry.dur,
            subtitle=dict(entry.subtitle),
        )

    # ── 会话状态（供渠道 !voice / !lang / !clear 指令读写） ──
    def is_enabled(self, session_id: str) -> bool:
        override = self._enabled.get(session_id)
        if override is None:
            return bool(getattr(self.settings, "qq_voice_enabled", False))
        return override

    def set_enabled(self, session_id: str, on: bool) -> None:
        self._enabled[session_id] = bool(on)

    def get_lang(self, session_id: str) -> str:
        return self._lang.get(session_id) or getattr(
            self.settings, "qq_voice_lang", "zh"
        )

    def set_lang(self, session_id: str, lang: str) -> None:
        self._lang[session_id] = "en" if lang == "en" else "zh"

    def clear_session(self, session_id: str) -> None:
        """!clear 时随会话记忆一并清空（回到全局默认）。"""
        self._enabled.pop(session_id, None)
        self._lang.pop(session_id, None)
        self._last_at.pop(session_id, None)
        self._last_clip.pop(session_id, None)

    # ── 内部 ──
    def _cooldown_ok(self, session_id: str) -> bool:
        cooldown = float(getattr(self.settings, "qq_voice_cooldown_sec", 60.0))
        if cooldown <= 0:
            return True
        last = self._last_at.get(session_id, 0.0)
        return (time.monotonic() - last) >= cooldown

    def _pick(self, session_id: str, slot: str) -> ClipEntry | None:
        store = self._get_store()
        if store is None:
            return None
        max_sec = float(getattr(self.settings, "qq_voice_max_sec", 65.0))
        entry = store.pick(slot, self.get_lang(session_id), exclude=self._last_clip.get(session_id))
        if entry is None:
            return None
        if entry.dur > max_sec:
            logger.info(
                "QQ 语音：切片 %s 时长 %.1fs 超上限 %.0fs，本轮降级文字",
                entry.id, entry.dur, max_sec,
            )
            return None
        return entry

    def _get_store(self) -> ClipStore | None:
        if self._store is not None:
            return self._store
        if self._store_failed:
            return None
        path = default_manifest_path(self.settings)
        if path is None:
            self._store_failed = True
            logger.warning(
                "QQ 语音：未找到切片 manifest，语音回复停用"
                "（可用 ROLEPLAY_QQ_VOICE_CLIP_MANIFEST 指定路径）"
            )
            return None
        try:
            self._store = ClipStore(path)
        except Exception as exc:  # noqa: BLE001
            self._store_failed = True
            logger.warning("QQ 语音：切片库加载失败，语音回复停用：%s", exc)
            return None
        logger.info(
            "QQ 语音：切片库就绪 %s（clips=%d slots=%d）",
            path, len(self._store.clips), len(self._store.slots),
        )
        return self._store
