"""用户画像提取器：规则层 + LLM 层 + 组合降级。

设计（架构师 ADR-3/7）：
- ``RuleProfileExtractor``：同步正则模板，confidence=0.3，永不失败（降级兜底）。
  模板覆盖 PRD 4 类（preference / habit / important_date / fact）+ correction 否定识别。
- ``LLMProfileExtractor``：复用全局 LLMPort（参考 LLMEmotionDetector 健壮模式）：
  ``asyncio.wait_for(timeout)`` + 异常只 logger.warning + JSON 三级解析兜底；
  提示词限定只提取用户稳定属性，不提取角色内容；type 枚举校验。
- ``extract_profile_entries``：组合策略——LLM 可用（非 mock 且 api_key 非空）时
  规则 + LLM 结果合并（LLM 优先、规则补漏）；否则仅规则（隐私：mock 零外发）。
"""
from __future__ import annotations

import asyncio
import json
import logging
import re
from typing import Sequence

from ...config import Settings, get_settings
from ..llm.base import LLMPort
from ..llm.factory import build_llm
from .profile_models import ProfileEntry, ProfileType, normalize_key

logger = logging.getLogger(__name__)

# LLM 提取只在非 mock 且有 api_key 时启用（与 emotion 的 _llm_layer_available 语义一致）
_LLM_ALLOWED_TYPES = ("preference", "habit", "important_date", "fact", "correction")

# 规则提取通用辅助：从中文句子中抽「话题词」——取第一个「喜欢/讨厌/…」后的相邻片段
_TOKEN_SPLIT = re.compile(r"[，。！？、,.!?\s]+")


class RuleProfileExtractor:
    """规则提取器：正则模板 → ProfileEntry（confidence=0.3，永不失败）。"""

    # 类型中文标签（与 profile_models 一致，供 text 可读句）
    _TYPE_LABELS = {
        "preference": "偏好",
        "habit": "习惯",
        "important_date": "重要日期",
        "fact": "事实",
        "correction": "更正",
    }

    # 模板：(正则, type, key, value提取)
    # 动词捕获：value 拼成可读画像句（「喜欢咖啡」「习惯早起」…）
    _PREFERENCE = re.compile(
        r"我(?:特别|真的|超级|非常|最)?(?P<verb>喜欢|爱吃|最爱|爱喝|最爱吃|好喜欢|想喝|想吃)\s*(?P<value>[^，。！？,.!?\s]+(?:[^，。！？,.!?]*)?)"
    )
    _PREFERENCE_NEG = re.compile(
        r"我(?:特别|真的|超级|非常|最)?(?P<verb>讨厌|不喜欢|最烦|吃不惯|喝不惯|受不了|不爱)\s*(?P<value>[^，。！？,.!?\s]+(?:[^，。！？,.!?]*)?)"
    )
    _HABIT = re.compile(
        r"我(?P<verb>每天|每周|习惯|总是|经常|日常|睡前|起床后|平时)\s*(?P<value>[^，。！？,.!?\s]+(?:[^，。！？,.!?]*)?)"
    )
    _DATE = re.compile(
        r"(?:我)?(?:生日|纪念日|每年的|我的生日|生日是|生日在|纪念日是|纪念日)\s*(?:是|在|为)?\s*(?P<value>\d{1,2}月\d{1,2}日|\d{4}-\d{1,2}-\d{1,2})"
    )
    _FACT = re.compile(
        r"我(?:住在|养了|家里有|今年|从事|是|来自|毕业|在|有)\s*(?P<value>[^，。！？,.!?\s]+(?:[^，。！？,.!?]*)?)"
    )
    _CORRECTION = re.compile(
        r"(?:其实|现在|已经|不过|但是)?(?:我)?(?:不再|不|现在不|改成|别|不要|其实我?不)\s*(?P<verb>喜欢|需要|想要|讨厌|爱|吃|喝|用)\s*(?P<value>[^，。！？,.!?\s]+(?:[^，。！？,.!?]*)?)"
    )

    def extract(self, turns: Sequence[dict]) -> list[ProfileEntry]:
        """从对话轮次提取画像条目（同步、永不失败）。

        turns: [{"role": "user"|"assistant", "content": "..."}]
        仅处理 user 轮（画像只从用户话语提取）；异常整轮吞掉。
        """
        entries: list[ProfileEntry] = []
        try:
            for i, turn in enumerate(turns):
                if not isinstance(turn, dict):
                    continue
                if turn.get("role") != "user":
                    continue
                text = str(turn.get("content") or "").strip()
                if not text:
                    continue
                entries.extend(self._extract_one(text, source_round=i))
        except Exception as exc:  # noqa: BLE001
            logger.warning("规则画像提取失败（降级为空）：%s", exc)
        return entries

    def _extract_one(self, text: str, source_round: int) -> list[ProfileEntry]:
        out: list[ProfileEntry] = []
        # 否定/改口 → correction（优先：同一句若同时命中普通模板，以 correction 覆盖语义）
        m = self._CORRECTION.search(text)
        if m:
            value = m.group("value").strip()
            if value:
                verb = m.group("verb") or ""
                out.append(
                    self._entry(
                        "correction",
                        self._key_from_value(value),
                        f"不再{verb}{value}",
                        source_round,
                    )
                )
                return out
        # 喜好（正）
        m = self._PREFERENCE.search(text)
        if m:
            value = m.group("value").strip()
            if value:
                verb = m.group("verb") or "喜欢"
                out.append(
                    self._entry(
                        "preference",
                        self._key_from_value(value),
                        f"{verb}{value}",
                        source_round,
                    )
                )
        else:
            m = self._PREFERENCE_NEG.search(text)
            if m:
                value = m.group("value").strip()
                if value:
                    verb = m.group("verb") or "不喜欢"
                    out.append(
                        self._entry(
                            "preference",
                            self._key_from_value(value),
                            f"{verb}{value}",
                            source_round,
                        )
                    )
        # 习惯
        m = self._HABIT.search(text)
        if m:
            value = m.group("value").strip()
            if value:
                verb = m.group("verb") or "习惯"
                out.append(
                    self._entry(
                        "habit", self._key_from_value(value), f"{verb}{value}", source_round
                    )
                )
        # 重要日期
        m = self._DATE.search(text)
        if m:
            value = m.group("value").strip()
            if value:
                out.append(
                    self._entry(
                        "important_date", self._date_key(value), value, source_round
                    )
                )
        # 事实（独立于上面的类，同一句可同时产出 preference + fact）
        m = self._FACT.search(text)
        if m:
            value = m.group("value").strip()
            if value:
                out.append(
                    self._entry(
                        "fact", self._key_from_value(value), value, source_round
                    )
                )
        return out

    @staticmethod
    def _key_from_value(value: str) -> str:
        """从值片段抽 key：取第一个有意义的词（去标点后的首个词）。"""
        parts = [p for p in _TOKEN_SPLIT.split(value) if p.strip()]
        return parts[0] if parts else value

    @staticmethod
    def _date_key(value: str) -> str:
        return "生日" if "生日" in value or re.match(r"^\d", value) else "纪念日"

    def _entry(self, type_: ProfileType, key: str, value: str, source_round: int) -> ProfileEntry:
        return ProfileEntry(
            type=type_,
            key=key,
            value=value,
            importance=0.5 if type_ == "important_date" else 0.4,
            confidence=0.3,
            source_round=source_round,
        )


class LLMProfileExtractor:
    """LLM 提取器：复用全局 LLMPort，JSON 数组输出 + 三级解析兜底（永不抛出）。"""

    _SYSTEM_PROMPT = (
        "你是用户画像提取助手。从用户的发言中提取「用户自己的稳定属性」，"
        "只输出单行 JSON 数组，不要任何其他文字："
        '[{"type": "preference|habit|important_date|fact|correction", '
        '"key": "<简短属性名>", "value": "<属性值/描述>", "importance": 0.0-1.0}]。'
        "规则："
        "- 只提取与用户本人相关的属性（喜好/习惯/重要日期/事实/改口），不要提取角色、天气、闲聊内容；"
        "- type 只能是 preference/habit/important_date/fact/correction 之一；"
        "- correction 表示用户否定或改口（如「其实我不喜欢咖啡」）；"
        "- 没有可提取内容时输出 []。"
    )

    def __init__(
        self,
        *,
        llm: LLMPort | None = None,
        timeout: float = 8.0,
        settings: Settings | None = None,
    ) -> None:
        self._llm = llm
        self._timeout = timeout
        self._parse_fail = 0
        # 未注入 llm 时尝试按 settings 构建全局 LLMPort（复用连接池）
        if self._llm is None and settings is not None:
            try:
                self._llm = build_llm(settings)
            except Exception as exc:  # noqa: BLE001
                logger.warning("LLM 画像提取器构建失败，该层禁用：%s", exc)
                self._llm = None

    @property
    def available(self) -> bool:
        """LLM 提取层是否可用（有 llm 实例才算可用）。"""
        return self._llm is not None

    async def extract(self, turns: Sequence[dict]) -> list[ProfileEntry]:
        """异步提取：超时/异常/解析失败 → 返回 []（由组合层回退规则）。"""
        if self._llm is None:
            return []
        blob = "\n".join(
            f"{t.get('role', '?')}: {t.get('content', '')}"
            for t in turns
            if isinstance(t, dict) and t.get("role") == "user"
        )
        if not blob.strip():
            return []
        try:
            raw = await asyncio.wait_for(
                self._llm.generate(
                    system=self._SYSTEM_PROMPT, user=blob, temperature=0.0
                ),
                timeout=self._timeout,
            )
        except asyncio.TimeoutError:
            logger.warning("LLM 画像提取超时（%.1fs）", self._timeout)
            return []
        except Exception as exc:  # noqa: BLE001
            logger.warning("LLM 画像提取失败：%s", exc)
            return []
        return self._parse_json(raw or "")

    def _parse_json(self, raw: str) -> list[ProfileEntry]:
        """三级解析：json.loads → 正则抽 JSON 数组 → [] 兜底（记 parse_fail）。"""
        text = raw.strip()
        if not text:
            self._parse_fail += 1
            return []
        # 容忍 ```json 代码块包裹
        if text.startswith("```"):
            text = re.sub(r"^```(?:json)?\s*", "", text).strip()
            text = re.sub(r"\s*```$", "", text).strip()
        try:
            obj = json.loads(text)
        except (json.JSONDecodeError, TypeError, ValueError):
            obj = self._regex_extract(text)
            # 正则兜底也拿不到对象 → 解析失败（计数 + 日志）
            if not obj:
                self._parse_fail += 1
                logger.warning("LLM 画像输出解析失败：%r", raw[:160])
        if not isinstance(obj, list):
            self._parse_fail += 1
            logger.warning("LLM 画像输出解析失败：%r", raw[:160])
            return []
        entries: list[ProfileEntry] = []
        for item in obj:
            if not isinstance(item, dict):
                continue
            try:
                entry = self._coerce(item)
            except Exception:  # noqa: BLE001
                continue
            if entry is not None:
                entries.append(entry)
        return entries

    def _regex_extract(self, text: str) -> list[dict]:
        """正则兜底：抽 ``{...}`` 对象片段拼成数组。"""
        found: list[dict] = []
        for m in re.finditer(r"\{[^{}]*\}", text):
            try:
                obj = json.loads(m.group(0))
            except (json.JSONDecodeError, TypeError, ValueError):
                continue
            if isinstance(obj, dict):
                found.append(obj)
        return found

    def _coerce(self, item: dict) -> ProfileEntry | None:
        """单条 LLM 输出 → ProfileEntry（type 枚举校验，非法丢弃）。"""
        raw_type = str(item.get("type", "")).strip().lower()
        if raw_type not in _LLM_ALLOWED_TYPES:
            return None
        key = str(item.get("key", "")).strip()
        value = str(item.get("value", "")).strip()
        if not key or not value:
            return None
        try:
            importance = float(item.get("importance", 0.5))
        except (TypeError, ValueError):
            importance = 0.5
        importance = max(0.0, min(1.0, importance))
        return ProfileEntry(
            type=raw_type,  # type: ignore[arg-type]
            key=key,
            value=value,
            importance=importance,
            confidence=0.6,
            source_round=0,
        )


def _llm_layer_available(s: Settings) -> bool:
    """LLM 提取是否可用：非 mock 且 api_key 非空（隐私：mock 零外发）。"""
    return s.llm_provider != "mock" and bool(s.llm_api_key)


def build_profile_extractors(
    settings: Settings | None = None,
    llm: LLMPort | None = None,
) -> tuple[RuleProfileExtractor, LLMProfileExtractor | None]:
    """按配置构建提取器组合：规则层恒有；LLM 层仅在可用时构建。"""
    s = settings or get_settings()
    rule = RuleProfileExtractor()
    llm_ext = None
    if _llm_layer_available(s):
        llm_ext = LLMProfileExtractor(
            llm=llm, timeout=s.profile_llm_timeout, settings=s
        )
        if llm_ext.available is False:
            llm_ext = None
    return rule, llm_ext


async def extract_profile_entries(
    turns: Sequence[dict],
    rule: RuleProfileExtractor | None = None,
    llm: LLMProfileExtractor | None = None,
    llm_available: bool = False,
) -> list[ProfileEntry]:
    """组合提取：LLM 可用 → 规则 + LLM 合并（LLM 优先、规则补漏）；否则仅规则。

    - 合并按去重键（{type}:{norm_key}）去重：LLM 条目优先，规则条目补漏。
    - 任何异常只 logger.warning，绝不向上抛（P0-5 降级）。
    - 异步：LLM 提取为 async（await），由调用方在事件循环内调用。
    """
    rule_ext = rule or RuleProfileExtractor()
    try:
        rule_entries = rule_ext.extract(turns)
    except Exception as exc:  # noqa: BLE001
        logger.warning("规则画像提取异常（降级为空）：%s", exc)
        rule_entries = []
    if not llm_available or llm is None:
        return rule_entries
    try:
        llm_entries = await llm.extract(turns)
    except Exception as exc:  # noqa: BLE001
        logger.warning("LLM 画像提取异常（回退规则）：%s", exc)
        llm_entries = []
    merged: dict[str, ProfileEntry] = {}
    for e in llm_entries:
        merged[e.dedup_key] = e
    for e in rule_entries:
        merged.setdefault(e.dedup_key, e)
    return list(merged.values())
