"""长期记忆事件提取器（升级方案 C）：把对话轮次提取为事实/事件级条目。

设计（与用户画像提取器 extractors.py 同构，复用其健壮范式）：
- ``RuleEventExtractor``：同步规则层——按重要性关键词切句，永不失败（降级兜底）。
- ``LLMEventExtractor``：复用全局 LLMPort，输出
  ``[{type: fact|event, content, subject, predicate, object, importance}]``，
  ``asyncio.wait_for(timeout)`` + 异常只 logger.warning + JSON 三级解析兜底。
- ``extract_event_entries``：组合策略——LLM 可用时 LLM + 规则合并（LLM 优先、
  规则补漏）；否则仅规则（mock 零外发，与画像提取一致的隐私语义）。

条目由 memory_tier 逐条写入 events:<cid> 命名空间（text=单句事实，
meta 承载 type/subject/predicate/object/importance/occurred_round）。
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

logger = logging.getLogger(__name__)

# 事件条目类型（LLM 输出与入库校验共用）
EVENT_ALLOWED_TYPES = ("fact", "event")

# 重要性提示词：命中这些关键词的句子视为更值得沉淀（与 memory_tier 共享语义）
_IMPORTANCE_HINTS = [
    "记住", "永远", "不要", "必须", "约定", "决定", "重要", "喜欢", "讨厌",
    "remember", "never", "always", "must", "promise", "decide", "important",
]

# 句子切分：中文/英文标点 + 换行
_SENT_SPLIT = re.compile(r"[。！？!?；;\n]+")


class RuleEventExtractor:
    """规则事件提取器：按重要性关键词切句 → 单句事实（永不失败）。"""

    def extract(self, turns: Sequence[dict]) -> list[dict]:
        """从对话轮次提取事实/事件条目（同步、永不失败）。

        turns: [{"role": "user"|"assistant", "content": "..."}]
        仅处理含重要性关键词的句子；条目为 dict（text/meta 由 memory_tier 组装）。
        """
        entries: list[dict] = []
        try:
            for i, turn in enumerate(turns):
                if not isinstance(turn, dict):
                    continue
                text = str(turn.get("content") or "").strip()
                if not text:
                    continue
                for sent in _SENT_SPLIT.split(text):
                    sent = sent.strip()
                    if not sent or len(sent) < 4:
                        continue
                    if self._has_hint(sent):
                        entries.append(
                            {
                                "type": "fact",
                                "content": sent,
                                "subject": turn.get("role", "user"),
                                "predicate": "",
                                "object": "",
                                "importance": min(
                                    1.0, 0.4 + 0.15 * self._hint_count(sent)
                                ),
                                "confidence": 0.3,
                                "occurred_round": i,
                            }
                        )
        except Exception as exc:  # noqa: BLE001
            logger.warning("规则事件提取失败（降级为空）：%s", exc)
        return entries

    @staticmethod
    def _has_hint(text: str) -> bool:
        t = (text or "").lower()
        return any(h in t for h in _IMPORTANCE_HINTS)

    @staticmethod
    def _hint_count(text: str) -> int:
        t = (text or "").lower()
        return sum(1 for h in _IMPORTANCE_HINTS if h in t)


class LLMEventExtractor:
    """LLM 事件提取器：JSON 数组输出 + 三级解析兜底（永不抛出）。"""

    _SYSTEM_PROMPT = (
        "你是对话记忆提取助手。从对话中提取「值得长期记住的事实与事件」，"
        "只输出单行 JSON 数组，不要任何其他文字："
        '[{"type": "fact|event", "content": "<一句简洁事实>", '
        '"subject": "<主语>", "predicate": "<谓语/关系>", "object": "<宾语>", '
        '"importance": 0.0-1.0}]。'
        "规则："
        "- fact 是稳定事实（喜好/约定/身份/关系等），event 是发生过的重要事件；"
        "- content 必须是完整单句，可脱离上下文理解；"
        "- 只提取用户与角色之间值得长期记住的内容，不要天气、寒暄等闲聊；"
        "- importance：约定/承诺/喜好等稳定信息给高分，一般事件给低分；"
        "- 没有可提取内容时输出 []。"
    )

    def __init__(
        self,
        *,
        llm: LLMPort | None = None,
        timeout: float = 10.0,
        settings: Settings | None = None,
    ) -> None:
        self._llm = llm
        self._timeout = timeout
        self._parse_fail = 0
        if self._llm is None and settings is not None:
            try:
                self._llm = build_llm(settings)
            except Exception as exc:  # noqa: BLE001
                logger.warning("LLM 事件提取器构建失败，该层禁用：%s", exc)
                self._llm = None

    @property
    def available(self) -> bool:
        return self._llm is not None

    async def extract(self, turns: Sequence[dict]) -> list[dict]:
        if self._llm is None:
            return []
        blob = "\n".join(
            f"{t.get('role', '?')}: {t.get('content', '')}"
            for t in turns
            if isinstance(t, dict)
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
            logger.warning("LLM 事件提取超时（%.1fs）", self._timeout)
            return []
        except Exception as exc:  # noqa: BLE001
            logger.warning("LLM 事件提取失败：%s", exc)
            return []
        return self._parse_json(raw or "")

    def _parse_json(self, raw: str) -> list[dict]:
        """三级解析：json.loads → 正则抽 JSON 数组 → [] 兜底。"""
        text = raw.strip()
        if not text:
            return []
        if text.startswith("```"):
            text = re.sub(r"^```(?:json)?\s*", "", text).strip()
            text = re.sub(r"\s*```$", "", text).strip()
        try:
            obj = json.loads(text)
        except (json.JSONDecodeError, TypeError, ValueError):
            obj = self._regex_extract(text)
            if not obj:
                self._parse_fail += 1
                logger.warning("LLM 事件输出解析失败：%r", raw[:160])
        if not isinstance(obj, list):
            self._parse_fail += 1
            logger.warning("LLM 事件输出解析失败：%r", raw[:160])
            return []
        entries: list[dict] = []
        for item in obj:
            if not isinstance(item, dict):
                continue
            entry = self._coerce(item)
            if entry is not None:
                entries.append(entry)
        return entries

    def _regex_extract(self, text: str) -> list[dict]:
        found: list[dict] = []
        for m in re.finditer(r"\{[^{}]*\}", text):
            try:
                obj = json.loads(m.group(0))
            except (json.JSONDecodeError, TypeError, ValueError):
                continue
            if isinstance(obj, dict):
                found.append(obj)
        return found

    @staticmethod
    def _coerce(item: dict) -> dict | None:
        raw_type = str(item.get("type", "")).strip().lower()
        if raw_type not in EVENT_ALLOWED_TYPES:
            return None
        content = str(item.get("content", "")).strip()
        if not content:
            return None
        try:
            importance = float(item.get("importance", 0.5))
        except (TypeError, ValueError):
            importance = 0.5
        importance = max(0.0, min(1.0, importance))
        return {
            "type": raw_type,
            "content": content,
            "subject": str(item.get("subject", "") or "").strip(),
            "predicate": str(item.get("predicate", "") or "").strip(),
            "object": str(item.get("object", "") or "").strip(),
            "importance": importance,
            "confidence": 0.6,
            "occurred_round": 0,
        }


def _llm_layer_available(s: Settings) -> bool:
    """LLM 提取是否可用：非 mock，且（有 api_key 或本地 provider）。

    原实现要求 ``api_key`` 非空，导致 **Ollama 部署下事件 LLM 层静默降级**
    （Ollama 本地推理不需要 key，见 factory.py:43 的 "ollama" 兜底）。
    "不外发"的隐私约束对本地 provider 不适用，故豁免。
    """
    if s.llm_provider == "mock":
        return False
    return bool(s.llm_api_key) or s.llm_provider == "ollama"


def build_event_extractors(
    settings: Settings | None = None,
    llm: LLMPort | None = None,
) -> tuple[RuleEventExtractor, LLMEventExtractor | None]:
    """按配置构建事件提取器组合：规则层恒有；LLM 层仅在可用时构建。"""
    s = settings or get_settings()
    rule = RuleEventExtractor()
    llm_ext = None
    if _llm_layer_available(s):
        llm_ext = LLMEventExtractor(llm=llm, timeout=10.0, settings=s)
        if llm_ext.available is False:
            llm_ext = None
    return rule, llm_ext


async def extract_event_entries(
    turns: Sequence[dict],
    rule: RuleEventExtractor | None = None,
    llm: LLMEventExtractor | None = None,
    llm_available: bool = False,
) -> list[dict]:
    """组合提取：LLM 可用 → LLM + 规则合并；否则仅规则。任何异常绝不向上抛。

    - 合并去重：content 完全一致去重，LLM 条目优先。
    - 返回 [{"type","content","subject","predicate","object","importance",
      "confidence","occurred_round"}]，由 memory_tier 逐条写入。
    """
    rule_ext = rule or RuleEventExtractor()
    try:
        rule_entries = rule_ext.extract(turns)
    except Exception as exc:  # noqa: BLE001
        logger.warning("规则事件提取异常（降级为空）：%s", exc)
        rule_entries = []
    if not llm_available or llm is None:
        return rule_entries
    try:
        llm_entries = await llm.extract(turns)
    except Exception as exc:  # noqa: BLE001
        logger.warning("LLM 事件提取异常（回退规则）：%s", exc)
        llm_entries = []
    merged: list[dict] = []
    seen: set[str] = set()
    for e in llm_entries:
        key = e["content"].strip().lower()
        if key not in seen:
            seen.add(key)
            merged.append(e)
    for e in rule_entries:
        key = e["content"].strip().lower()
        if key not in seen:
            seen.add(key)
            merged.append(e)
    return merged
