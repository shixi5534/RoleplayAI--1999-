"""结构化 if-then 行为规则引擎（应用层纯函数，无副作用、无 LLM 开销）。

设计（升级方案 A）：
- 角色卡新增可选字段 ``behavior_rules_structured``：规则列表
  ``[{id, condition: {type, field, pattern, case_sensitive}, action, priority, enabled}]``。
- 本模块提供：
  - ``validate_rules``：校验/清洗规则列表（非法规则丢弃，不阻断卡片加载）；
  - ``match_condition``：纯代码判定（子串 / 正则 / 情绪标签），零 LLM 开销；
  - ``render_rules``：按 priority 排序，只注入命中的 enabled 规则。

向后兼容：``behavior_rules_structured`` 为空/非法时返回空串，调用方回落原
``behavior_rules`` 文本（自由文本路径不变）。
"""
from __future__ import annotations

import logging
import re
from typing import Any

logger = logging.getLogger(__name__)

# 支持的判定类型与字段（v1：不含状态机；状态机留待 v2 扩展）
CONDITION_TYPES = ("text_contains", "text_regex", "emotion_is")
CONDITION_FIELDS = ("user_message", "current_emotion")
MAX_RULES = 50  # 规则数上限（防角色卡膨胀）

_RULES_HEADER = (
    "【行为规则（当条件命中时必须遵守）】\n"
    "以下规则优先级高于人设描述；未命中的规则无需理会。"
)


def _clean_rules(raw: Any) -> list[dict]:
    """把任意输入清洗为合法规则列表（不抛异常，非法条目丢弃）。"""
    if not isinstance(raw, list):
        return []
    out: list[dict] = []
    seen: set[str] = set()
    for item in raw[:MAX_RULES]:
        if not isinstance(item, dict):
            continue
        cond = item.get("condition")
        if not isinstance(cond, dict):
            continue
        ctype = str(cond.get("type", "")).strip().lower()
        field = str(cond.get("field", "")).strip().lower()
        pattern = str(cond.get("pattern", "") or "")
        action = str(item.get("action", "") or "").strip()
        if ctype not in CONDITION_TYPES or field not in CONDITION_FIELDS:
            continue
        if not action:
            continue
        if not pattern:
            continue
        if ctype == "text_regex":
            try:
                re.compile(pattern)
            except re.error:
                logger.warning("行为规则正则非法，丢弃 rule id=%s", item.get("id"))
                continue
        rid = str(item.get("id", "")).strip()
        if rid and rid in seen:
            continue  # id 去重
        if rid:
            seen.add(rid)
        try:
            priority = int(item.get("priority", 0))
        except (TypeError, ValueError):
            priority = 0
        rule: dict[str, Any] = {
            "id": rid,
            "condition": {
                "type": ctype,
                "field": field,
                "pattern": pattern,
                "case_sensitive": bool(cond.get("case_sensitive", False)),
            },
            "action": action,
            "priority": priority,
            "enabled": bool(item.get("enabled", True)),
            "category": str(item.get("category", "") or "").strip(),
        }
        out.append(rule)
    return out


def validate_rules(raw: Any) -> list[dict]:
    """校验入口：与 _clean_rules 同义（保留独立命名供外部调用）。"""
    return _clean_rules(raw)


def match_condition(cond: dict, context: dict[str, Any]) -> bool:
    """纯代码判定单个条件是否命中。context: {user_message, current_emotion}。

    - text_contains：子串包含（默认忽略大小写）；
    - text_regex：正则 search（编译异常视为不命中）；
    - emotion_is：与当前情绪标签相等（None 不命中）。
    """
    ctype = cond.get("type")
    field = cond.get("field")
    pattern = cond.get("pattern") or ""
    value = context.get(field)
    if value is None:
        return False
    text = str(value)
    if ctype == "text_contains":
        if cond.get("case_sensitive"):
            return pattern in text
        return pattern.lower() in text.lower()
    if ctype == "text_regex":
        try:
            flags = 0 if cond.get("case_sensitive") else re.IGNORECASE
            return re.search(pattern, text, flags) is not None
        except re.error:
            return False
    if ctype == "emotion_is":
        return text == pattern
    return False


def render_rules(raw: Any, context: dict[str, Any]) -> str:
    """命中规则 → 提示词规则块（按 priority 降序）。无命中返回空串。

    context 至少包含 user_message；current_emotion 可选（emotion 未启用时为 None）。
    """
    rules = _clean_rules(raw)
    if not rules:
        return ""
    active = [r for r in rules if r["enabled"]]
    active.sort(key=lambda r: r["priority"], reverse=True)
    lines: list[str] = []
    for r in active:
        if match_condition(r["condition"], context):
            lines.append(f"- {r['action']}")
    if not lines:
        return ""
    return _RULES_HEADER + "\n" + "\n".join(lines)
