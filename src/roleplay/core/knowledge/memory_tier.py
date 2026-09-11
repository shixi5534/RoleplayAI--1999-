"""分层记忆：长期记忆（合并 + 衰减 + 保留策略）。

架构：
- 短期记忆 = SessionMemory（最近 N 轮，始终作为 history 注入，见 orchestrator）。
- 长期记忆 = 这里：把对话中「值得记住」的片段合并沉淀到知识库 events 命名空间，
  检索时按 相似度 × 时间衰减 × 重要性 综合排序，并定期清理过期/低分记忆。

满足需求 4：区分长期/短期 + 合理的衰减与保留策略。
"""
from __future__ import annotations

import logging
import math
import time
from typing import Iterable, List

from ..rag.base import RetrievedChunk
from .vector_store import KnowledgeBase

logger = logging.getLogger(__name__)

# 命中这些关键词的对话片段视为更高重要性（关键事件 / 决定 / 承诺）
_IMPORTANCE_HINTS = [
    "记住", "永远", "不要", "必须", "约定", "决定", "重要", "喜欢", "讨厌",
    "remember", "never", "always", "must", "promise", "decide", "important",
]

# 极低重要性清理阈值。
# 注意：结构化条目（consolidate_entries）的 importance 标度是 [0,1]
# （规则提取器 0.4~0.55、LLM 提取器缺省 0.5、纠错条目下限 0.3），
# 而整段合并（consolidate）的 importance 标度是 [1,3]。
# 旧阈值 0.6 会误杀全部结构化条目（写一条清一条，长期记忆形同虚设），
# 统一取 0.3 作为「极不重要」下限（与纠错条目下限一致，正常条目均能保留）。
_PRUNE_MIN_IMPORTANCE = 0.3


class LongTermMemory:
    def __init__(
        self,
        kb: KnowledgeBase,
        namespace: str = "events",
        decay_lambda: float = 0.05,
        retention_days: int = 60,
    ) -> None:
        self._kb = kb
        self._ns = namespace
        self._lam = decay_lambda
        self._ret = retention_days

    @staticmethod
    def _importance(text: str) -> float:
        t = (text or "").lower()
        score = 1.0
        for hint in _IMPORTANCE_HINTS:
            if hint in t:
                score += 0.4
        # 长度适中更可能含关键信息
        if 30 <= len(text) <= 400:
            score += 0.2
        return min(score, 3.0)

    def _ns_for(self, character_id: str | None) -> str:
        """长期记忆命名空间：按角色隔离（无角色回退公共 events）。"""
        return f"events:{character_id}" if character_id else self._ns

    async def consolidate(
        self,
        session_id: str,
        turns: List[dict],
        character_id: str | None = None,
    ) -> int:
        """把最近若干轮对话合并沉淀为一条长期记忆（事件）。返回写入条数。异步。

        按 character_id 写入 events:<character_id> 命名空间，跨角色严格隔离。
        （整段合并路径，保留向后兼容；结构化逐条写入见 consolidate_entries）
        """
        if not turns:
            return 0
        lines = [f"{t.get('role', '?')}: {t.get('content', '')}" for t in turns]
        text = "\n".join(lines)
        meta = {
            "session_id": session_id,
            "character_id": character_id or "",
            "type": "event",
            "importance": self._importance(text),
        }
        ns = self._ns_for(character_id)
        ids = await self._kb.aadd([text], metadatas=[meta], namespace=ns)
        return len(ids)

    async def consolidate_entries(
        self,
        session_id: str,
        entries: List[dict],
        character_id: str | None = None,
    ) -> int:
        """把结构化提取的事实/事件条目逐条写入长期记忆（升级方案 C）。返回写入条数。

        entries: [{"type","content","subject","predicate","object",
                   "importance","confidence","occurred_round"}]
        text = 单句事实（content），meta 承载结构化字段；旧整段条目照常可检索。
        """
        if not entries:
            return 0
        texts: List[str] = []
        metas: List[dict] = []
        for e in entries:
            content = str(e.get("content", "") or "").strip()
            if not content:
                continue
            texts.append(content)
            metas.append(
                {
                    "session_id": session_id,
                    "character_id": character_id or "",
                    "type": str(e.get("type", "fact")),
                    "subject": str(e.get("subject", "") or ""),
                    "predicate": str(e.get("predicate", "") or ""),
                    "object": str(e.get("object", "") or ""),
                    "importance": float(e.get("importance", 0.5)),
                    "confidence": float(e.get("confidence", 0.5)),
                    "occurred_round": int(e.get("occurred_round", 0)),
                }
            )
        if not texts:
            return 0
        ns = self._ns_for(character_id)
        ids = await self._kb.aadd(texts, metadatas=metas, namespace=ns)
        return len(ids)

    async def retrieve(self, query: str, top_k: int = 3, character_id: str | None = None) -> List[RetrievedChunk]:
        """检索长期记忆，按 相似度 × 时间衰减 × 重要性 综合排序。异步。

        仅检索当前角色（events:<character_id>）的长期记忆，跨角色不串台。
        """
        ns = self._ns_for(character_id)
        raw = await self._kb.asearch(
            query, top_k=top_k * 4, namespaces=[ns], min_score=0.0
        )
        now = time.time()
        scored: List[tuple[float, RetrievedChunk]] = []
        for c in raw:
            ts = c.metadata.get("ts", now)
            try:
                age_days = max(0.0, (now - float(ts)) / 86400.0)
            except (TypeError, ValueError):
                age_days = 0.0
            decay = math.exp(-self._lam * age_days)
            imp = float(c.metadata.get("importance", 1.0))
            eff = c.score * decay * (0.5 + 0.5 * imp)
            scored.append((eff, c))
        scored.sort(key=lambda x: x[0], reverse=True)
        return [c for _, c in scored[:top_k]]

    def prune(self, character_id: str | None = None) -> int:
        """清理过期或低分的长期记忆（按角色命名空间）。返回清理条数。"""
        now = time.time()
        ret = self._ret
        ns = self._ns_for(character_id)

        def _pred(it: dict) -> bool:
            ts = it.get("ts", now)
            age_days = (now - ts) / 86400.0 if ts else 0.0
            imp = float(it.get("meta", {}).get("importance", 1.0))
            # 超期且重要性低 → 直接清；或极不重要 → 清
            # （阈值与结构化条目 [0,1] 标度对齐，见 _PRUNE_MIN_IMPORTANCE 注释）
            return (age_days > ret and imp < 2.0) or imp < _PRUNE_MIN_IMPORTANCE

        removed = self._kb.filter_remove(ns, _pred)
        if removed:
            logger.info("长期记忆清理：移除 %d 条", removed)
        return removed
