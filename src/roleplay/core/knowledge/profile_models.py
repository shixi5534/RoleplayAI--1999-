"""用户画像数据模型（UserProfile 模块）。

设计（架构师 ADR-1/2/7）：
- 一条画像 = vector store 一条记录：text 为可读画像句，metadata 承载结构化字段。
- ``ProfileEntry`` 为提取器产出与 upsert 输入的 DTO（pydantic，强校验）。
- 类型枚举：preference / habit / important_date / fact / correction；
  correction 是「否定/改口」标记，入库时覆盖旧条目并降权（ADR-4）。
- ``normalize_key`` 为去重键的归一化：key 小写 + 去空白（ADR-4 共享约定）。
"""
from __future__ import annotations

import re
from datetime import datetime, timezone
from typing import Literal

from pydantic import BaseModel, Field, field_validator

# 画像条目类型（唯一事实源；LLM 提取 / 规则提取 / 入库校验共用）
ProfileType = Literal[
    "preference", "habit", "important_date", "fact", "correction"
]

# 类型 → 中文标签（用于 text 可读画像句与调试展示）
PROFILE_TYPE_LABELS: dict[str, str] = {
    "preference": "偏好",
    "habit": "习惯",
    "important_date": "重要日期",
    "fact": "事实",
    "correction": "更正",
}

# 去重/同义检查跳过同义检索的置信度下限（低于此值只走精确键，省成本）
SYNONYM_CHECK_MIN_CONFIDENCE = 0.4


def normalize_key(key: str) -> str:
    """去重键归一化：key 小写 + 去全部空白（ADR-4 共享约定）。"""
    return re.sub(r"\s+", "", key or "").lower()


def now_iso() -> str:
    """ISO8601 UTC 时间戳（metadata 落盘与 updated_at 用）。"""
    return datetime.now(timezone.utc).isoformat()


class ProfileEntry(BaseModel):
    """一条用户画像条目（提取器输出 / upsert 输入的统一 DTO）。

    - type        : preference/habit/important_date/fact/correction
    - key         : 稳定属性的键（如「咖啡」）；去重按 {type}:{norm(key)}
    - value       : 属性值/描述（如「喜欢喝拿铁」）
    - importance  : [0,1]，越高越优先注入（correction 降半后下限 0.3）
    - confidence  : [0,1]，规则层固定 0.3，LLM 层可给更高
    - source_round: 提取自第几轮（history 游标位置），仅日志/调试用
    - updated_at  : ISO8601 UTC；由 upsert 覆盖为写入时刻
    - versions    : 更新版本号（精确键命中 +1，上限 10）
    - history     : 旧 value 历史（上限 10 条，仅精确更新时追加）
    """

    type: ProfileType
    key: str = Field(..., min_length=1)
    value: str = Field(..., min_length=1)
    importance: float = Field(0.5, ge=0.0, le=1.0)
    confidence: float = Field(0.5, ge=0.0, le=1.0)
    source_round: int = 0
    updated_at: str = Field(default_factory=now_iso)
    versions: int = Field(1, ge=1)
    history: list[str] = Field(default_factory=list)

    @field_validator("type")
    @classmethod
    def _validate_type(cls, v: str) -> str:
        # pydantic Literal 已校验；此处再兜一层，兼容字符串形式传入时给明确报错
        allowed = ("preference", "habit", "important_date", "fact", "correction")
        if v not in allowed:
            raise ValueError(f"非法画像类型: {v!r}，允许 {allowed}")
        return v

    @field_validator("key", "value")
    @classmethod
    def _strip_text(cls, v: str) -> str:
        return v.strip()

    @property
    def dedup_key(self) -> str:
        """去重键：{type}:{norm_key}（ADR-4 核心约定）。"""
        return f"{self.type}:{normalize_key(self.key)}"

    def to_meta(self) -> dict:
        """转为 vector store metadata（KB 自动补 ts/id/namespace）。"""
        return {
            "type": self.type,
            "key": self.key,
            "value": self.value,
            "importance": float(self.importance),
            "confidence": float(self.confidence),
            "source_round": int(self.source_round),
            "updated_at": self.updated_at,
            "versions": int(self.versions),
            "history": list(self.history),
        }

    @classmethod
    def from_meta(cls, meta: dict) -> "ProfileEntry":
        """从 vector store metadata 还原为 ProfileEntry（检索/查重用）。"""
        return cls(
            type=meta.get("type", "fact"),
            key=meta.get("key", ""),
            value=meta.get("value", ""),
            importance=float(meta.get("importance", 0.5)),
            confidence=float(meta.get("confidence", 0.5)),
            source_round=int(meta.get("source_round", 0)),
            updated_at=meta.get("updated_at", now_iso()),
            versions=int(meta.get("versions", 1)),
            history=list(meta.get("history", []) or []),
        )
