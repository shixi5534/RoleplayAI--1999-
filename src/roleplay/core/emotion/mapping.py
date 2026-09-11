"""情绪 → Live2D 表情/动作 映射器。

关键设计（落实上一轮核实结论）：
- 映射使用**表情名**（如 "e_nanguo"）而非索引 —— 因为两套 Live2D 模型
  的表情数组顺序不同，写死索引换模型即错位。运行时由前端 model.expression(name) 解析。
- 内置默认映射，即使 emotion_map.json 缺失也能返回合理结果（优雅降级）。
- 15 类全链路穿透（ADR-7）：新增 8 类细分情绪，expression 沿用父类、motion 细分；
  resolve() 父类链回退：emotions[emotion] → emotions[EMOTION_PARENT[emotion]] → default。
"""
import json
from pathlib import Path

from ...models.chat import EMOTION_PARENT, EmotionLabel

# 内置默认映射（与 frontend/assets/live2d/emotion_map.json 保持一致）
# 15 类 = 原 7 类 + 新增 8 类（expression 沿用父类、motion 细分）
_DEFAULT_MAP: dict = {
    "version": "2.0",
    "emotions": {
        "happy":    {"expression": "e_weixiao", "motion": "b_diantou", "priority": 2},
        "sad":      {"expression": "e_nanguo",  "motion": "t_nanguo",  "priority": 2},
        "angry":    {"expression": "e_yansu",   "motion": "b_yaotou",  "priority": 3},
        "anxious":  {"expression": "e_yihuo",   "motion": "b_shanzi",  "priority": 2},
        "surprise": {"expression": "e_yihuo",   "motion": "t_yihuo",   "priority": 3},
        "fear":     {"expression": "e_yansu",   "motion": "b_zhelian", "priority": 3},
        "neutral":  {"expression": "e_idle",    "motion": "b_idle",    "priority": 1},
        # —— 新增 8 类（expression 沿用父类，motion 细分动作组）——
        "love":         {"expression": "e_weixiao", "motion": "t_weixiao",  "priority": 3},
        "grateful":     {"expression": "e_weixiao", "motion": "b_diantou",  "priority": 2},
        "excited":      {"expression": "e_weixiao", "motion": "b_liaofa",   "priority": 3},
        "disappointed": {"expression": "e_nanguo",  "motion": "b_yaotou",  "priority": 3},
        "lonely":       {"expression": "e_nanguo",  "motion": "b_zhelian", "priority": 2},
        "embarrassed":  {"expression": "e_yihuo",   "motion": "b_zhelian", "priority": 2},
        "confused":     {"expression": "e_yihuo",   "motion": "b_shanzi",  "priority": 2},
        "sleepy":       {"expression": "e_idle",    "motion": "b_diantou", "priority": 1},
    },
    "default": {"expression": "e_idle", "motion": "b_idle", "priority": 1},
    "score_threshold": 0.3,
}


class Live2DEmotionMapper:
    def __init__(self, map_path: str | None = None) -> None:
        self._data = _DEFAULT_MAP
        if map_path:
            p = Path(map_path)
            if p.exists():
                try:
                    self._data = json.loads(p.read_text(encoding="utf-8"))
                except (json.JSONDecodeError, OSError):
                    self._data = _DEFAULT_MAP  # 文件损坏 → 降级

    def resolve(
        self, emotion: EmotionLabel, *, score: float = 1.0, model_id: str | None = None
    ) -> dict | None:
        """返回 {model_id, expression, motion, priority} 或 None（低于阈值不切换）。

        父类链回退（ADR-7）：emotions[emotion] → emotions[EMOTION_PARENT[emotion]] → default。
        父类本身（happy/sad/...）无父类，直接走 default。
        """
        if score < self._data.get("score_threshold", 0.5):
            return None
        emotions = self._data.get("emotions", {})
        entry = emotions.get(emotion)
        if entry is None:
            parent = EMOTION_PARENT.get(emotion)
            if parent is not None:
                entry = emotions.get(parent)
        entry = entry or self._data.get("default")
        if not entry:
            return None
        return {
            "model_id": model_id,
            "expression": entry["expression"],
            "motion": entry.get("motion"),
            "priority": entry.get("priority", 1),
        }
