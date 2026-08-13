"""用户画像（UserProfile）：用户稳定属性的存储 / 去重 / 检索 / 提醒。

设计（架构师 ADR-1/2/4/6）：
- **独立类**：组合 KnowledgeBase，与 LongTermMemory 并列挂在 KnowledgeServices；
  写入独立命名空间（默认 ``profile``），按用户级全局共享（预留 ``profile:<uid>``）。
- **存储形态**：一条画像 = vector store 一条记录，text 为可读画像句，
  metadata 承载 ``{type,key,value,importance,confidence,source_round,updated_at,versions,history}``。
- **去重算法（ADR-4）**：
  1. 去重键 ``{type}:{norm_key}``（norm_key = key 小写去空白）；
  2. 精确键命中 → 更新 value + versions+1 + updated_at（versions 上限 10，旧值入 history）；
  3. 未命中且 confidence ≥ 0.4 → 向量同义检查（相似度 > synonym_threshold 判同义更新，不新增）；
  4. correction（type=correction）→ 覆盖旧条目 + importance 降半（下限 0.3）+ corrected=True；
     找不到原条目 → 转存 fact 条目 importance=0.3；
  5. 超 profile_max_items 按 importance 淘汰最低（保留 important_date）。
- **检索排序（ADR-5）**：``score × exp(-λ·age) × (0.5+0.5·imp) × (0.5+0.5·conf)``。
- **提醒（ADR-6）**：同步扫描 important_date 条目，|距今天数| ≤ reminder_days → 提醒行。
"""
from __future__ import annotations

import asyncio
import logging
import math
import re
import time
from datetime import date, datetime

from ..rag.base import RetrievedChunk
from .profile_models import (
    PROFILE_TYPE_LABELS,
    SYNONYM_CHECK_MIN_CONFIDENCE,
    ProfileEntry,
    normalize_key,
    now_iso,
)
from .vector_store import KnowledgeBase

logger = logging.getLogger(__name__)


class UserProfile:
    """用户画像存储与检索（组合 KnowledgeBase，独立命名空间）。"""

    def __init__(
        self,
        kb: KnowledgeBase,
        namespace: str = "profile",
        decay_lambda: float = 0.05,
        synonym_threshold: float = 0.85,
        reminder_days: int = 3,
        max_items: int = 200,
        top_k: int = 5,
    ) -> None:
        self._kb = kb
        self._ns = namespace
        self._lam = decay_lambda
        self._syn_th = synonym_threshold
        self._rem_days = reminder_days
        self._max_items = max_items
        self._top_k = top_k
        # 写临界区锁：把「去重判定 + 写入」串行化，防止并发 upsert 同 key 竞态
        # （check-then-act 非原子：两个任务都在 aadd 前读到「不存在」→ 各自新增）。
        # 采用全局单锁而非 per-key 锁：画像写入低频（每 N 轮一次）且条目有硬上限，
        # 全局锁简单、无锁表清理负担，并发正确性等价（QA B4 竞态）。
        self._write_lock = asyncio.Lock()

    # ── 公共查询 ──
    @property
    def namespace(self) -> str:
        """画像命名空间（供注入块来源标注 / 合成提醒 chunk 使用）。"""
        return self._ns

    def count(self) -> int:
        """画像条目总数。"""
        return self._kb.count(self._ns).get(self._ns, 0)

    def list_entries(self) -> list[ProfileEntry]:
        """返回全部画像条目（按存储序），调试 / 统计用。"""
        return [
            ProfileEntry.from_meta(it.get("meta", {}))
            for it in self._kb.list_items(self._ns)
        ]

    # ── 写入：upsert（去重 / 同义 / correction / 上限淘汰） ──
    async def upsert(self, entries: list[ProfileEntry], source_round: int | None = None) -> int:
        """把提取的画像条目写入知识库（原子：remove 旧 + aadd 新）。返回处理条数。

        - source_round：提取自第几轮（历史游标位置），写入 metadata 供排查。
        - 同一次调用内多条目按去重键串行处理：后到的精确命中先到的（不重复新增）。
        - 并发安全：整个「去重判定 + 写入」在 _write_lock 临界区内串行执行，
          防止并发 upsert 同 key 时 check-then-act 竞态导致重复条目（QA B4 P1）。
        - 任何单条目异常只 logger.warning 并跳过，绝不向上抛（P0-5 降级）。
        """
        if not entries:
            return 0
        # 注意：入口处只做空判定；每个条目的处理在锁内串行，避免竞态
        async with self._write_lock:
            handled = 0
            for raw in entries:
                entry = (
                    raw.model_copy(update={"source_round": source_round})
                    if source_round is not None
                    else raw
                )
                try:
                    if entry.type == "correction":
                        if await self._apply_correction(entry):
                            handled += 1
                            continue
                        # 找不到原条目 → 转存 fact 条目 importance=0.3（ADR-4 步骤 4）
                        entry = entry.model_copy(
                            update={"type": "fact", "importance": 0.3}
                        )
                    existing = self._find_exact(entry)
                    if existing is not None:
                        await self._update_existing(existing, entry)
                        handled += 1
                        continue
                    if entry.confidence >= SYNONYM_CHECK_MIN_CONFIDENCE:
                        syn = await self._find_synonym(entry)
                        if syn is not None:
                            await self._update_existing(syn, entry)
                            handled += 1
                            continue
                    await self._add_new(entry)
                    handled += 1
                    # 新增后若超上限再淘汰（保留 important_date，淘汰低 importance）
                    await self._prune_to_max()
                except Exception as exc:  # noqa: BLE001
                    logger.warning("用户画像条目写入失败（跳过）：%s", exc)
            return handled

    async def _apply_correction(self, entry: ProfileEntry) -> bool:
        """correction 处理：按 key 精确/同义找原条目 → 覆盖 + 降权。找到返回 True。"""
        target = self._find_by_key(entry.key)
        if target is None:
            hits = await self._kb.asearch(
                f"{entry.key} {entry.value}",
                top_k=3,
                namespaces=[self._ns],
                min_score=0.0,
            )
            for c in hits:
                if c.score < self._syn_th:
                    continue
                target = self._find_by_id(c.metadata.get("id"))
                if target is not None:
                    break
        if target is None:
            return False
        meta = dict(target.get("meta", {}))
        old_imp = float(meta.get("importance", 0.5))
        new_meta = dict(meta)
        new_meta.update(
            {
                "value": entry.value,
                "importance": max(0.3, old_imp * 0.5),
                "confidence": max(float(meta.get("confidence", 0.5)), entry.confidence),
                "source_round": entry.source_round,
                "updated_at": now_iso(),
                "versions": min(10, int(meta.get("versions", 1)) + 1),
                "corrected": True,
            }
        )
        new_meta["history"] = self._append_history(meta, entry.value)
        await self._replace_item(target, new_meta)
        return True

    async def _update_existing(self, item: dict, entry: ProfileEntry) -> None:
        """精确键/同义命中 → 更新该条（保留 canonical key），versions+1。"""
        meta = dict(item.get("meta", {}))
        new_meta = dict(meta)
        new_meta.update(
            {
                "value": entry.value,
                "importance": max(float(meta.get("importance", 0.5)), entry.importance),
                "confidence": max(float(meta.get("confidence", 0.5)), entry.confidence),
                "source_round": entry.source_round,
                "updated_at": now_iso(),
                "versions": min(10, int(meta.get("versions", 1)) + 1),
            }
        )
        new_meta["history"] = self._append_history(meta, entry.value)
        await self._replace_item(item, new_meta)

    @staticmethod
    def _append_history(meta: dict, new_value: str) -> list[str]:
        """旧 value 追加进 history（上限 10）。"""
        old_value = meta.get("value", "")
        history = list(meta.get("history", []) or [])
        if old_value and old_value != new_value:
            history.append(str(old_value))
            history = history[-10:]
        return history

    async def _replace_item(self, item: dict, new_meta: dict) -> None:
        """原子更新：remove 旧 + aadd 新（ADR-2：更新 = remove(old_id) + aadd）。

        注意：``KnowledgeBase.remove`` 为同步方法（返回 bool），此处直接调用；
        随后 aadd 为异步。顺序保证「先删旧、后加新」，删除成功但新增失败时
        由 upsert 调用方捕获并记录（单条失败不影响其它条目）。
        """
        # KB 自动补的字段不写入 metadata（避免 id/namespace 重复注入）
        new_meta.pop("id", None)
        new_meta.pop("namespace", None)
        new_meta.pop("ts", None)
        entry = ProfileEntry.from_meta(new_meta)
        text = self._to_text(entry)
        self._kb.remove(self._ns, item["id"])
        await self._kb.aadd([text], metadatas=[new_meta], namespace=self._ns)

    async def _add_new(self, entry: ProfileEntry) -> None:
        await self._kb.aadd(
            [self._to_text(entry)], metadatas=[entry.to_meta()], namespace=self._ns
        )

    async def _prune_to_max(self) -> int:
        """超出 profile_max_items 时按 importance 淘汰最低（保留 important_date）。"""
        items = self._kb.list_items(self._ns)
        if len(items) <= self._max_items:
            return 0
        candidates = [
            it
            for it in items
            if it.get("meta", {}).get("type") != "important_date"
        ]
        candidates.sort(
            key=lambda it: float(it.get("meta", {}).get("importance", 0.5))
        )
        removed = 0
        while self.count() > self._max_items and candidates:
            victim = candidates.pop(0)
            if self._kb.remove(self._ns, victim["id"]):
                removed += 1
        if removed:
            logger.info("用户画像淘汰 %d 条低 importance 条目", removed)
        return removed

    # ── 查重辅助 ──
    def _find_exact(self, entry: ProfileEntry) -> dict | None:
        """精确键命中：metadata type 相同 + norm(key) 相同。"""
        norm = normalize_key(entry.key)
        for it in self._kb.list_items(self._ns):
            meta = it.get("meta", {})
            if meta.get("type") == entry.type and normalize_key(
                meta.get("key", "")
            ) == norm:
                return it
        return None

    def _find_by_key(self, key: str) -> dict | None:
        """按 key（跨类型）查找原条目（correction 用）。"""
        norm = normalize_key(key)
        for it in self._kb.list_items(self._ns):
            if normalize_key(it.get("meta", {}).get("key", "")) == norm:
                return it
        return None

    def _find_by_id(self, item_id: str | None) -> dict | None:
        if not item_id:
            return None
        for it in self._kb.list_items(self._ns):
            if it.get("id") == item_id:
                return it
        return None

    async def _find_synonym(self, entry: ProfileEntry) -> dict | None:
        """同义检查：向量检索 top 命中 type 相同且 score ≥ 阈值 → 判同义。"""
        hits = await self._kb.asearch(
            f"{entry.key} {entry.value}",
            top_k=3,
            namespaces=[self._ns],
            min_score=0.0,
        )
        norm = normalize_key(entry.key)
        for c in hits:
            meta = c.metadata
            if meta.get("type") != entry.type:
                continue
            if normalize_key(meta.get("key", "")) == norm:
                continue  # 精确键由 _find_exact 处理
            if c.score >= self._syn_th:
                return self._find_by_id(meta.get("id"))
        return None

    # ── 检索：importance × 置信 × 时间衰减 综合排序（ADR-5） ──
    async def retrieve(self, query: str, top_k: int | None = None) -> list[RetrievedChunk]:
        """按 query 检索画像，eff = score × exp(-λ·age) × (0.5+0.5·imp) × (0.5+0.5·conf)。"""
        k = top_k or self._top_k
        raw = await self._kb.asearch(
            query, top_k=k * 4, namespaces=[self._ns], min_score=0.0
        )
        now = time.time()
        scored: list[tuple[float, RetrievedChunk]] = []
        for c in raw:
            ts = c.metadata.get("ts", now)
            try:
                age_days = max(0.0, (now - float(ts)) / 86400.0)
            except (TypeError, ValueError):
                age_days = 0.0
            decay = math.exp(-self._lam * age_days)
            imp = float(c.metadata.get("importance", 0.5))
            conf = float(c.metadata.get("confidence", 0.5))
            eff = c.score * decay * (0.5 + 0.5 * imp) * (0.5 + 0.5 * conf)
            scored.append((eff, c))
        scored.sort(key=lambda x: x[0], reverse=True)
        return [c for _, c in scored[:k]]

    # ── 提醒：important_date 扫描（ADR-6，纯同步只读） ──
    def check_reminders(self, today: date | datetime | None = None) -> list[str]:
        """扫描 important_date 条目，|距今天数| ≤ reminder_days → 提醒行。

        - 支持 ``YYYY-MM-DD`` 与 ``M月D日``（年周期，已过则顺延次年再判窗口）。
        - 日期解析失败一律跳过，绝不抛异常。
        """
        if today is None:
            today = date.today()
        elif isinstance(today, datetime):
            today = today.date()
        out: list[str] = []
        for it in self._kb.list_items(self._ns):
            meta = it.get("meta", {})
            if meta.get("type") != "important_date":
                continue
            raw = str(meta.get("value", "")).strip()
            d = self._parse_date(raw, today)
            if d is None:
                continue
            days = (d - today).days
            if abs(days) <= self._rem_days:
                key = str(meta.get("key") or "重要日期")
                out.append(self._reminder_line(key, raw, days))
        return out

    @staticmethod
    def _parse_date(raw: str, today: date) -> date | None:
        """解析日期；失败返回 None（调用方跳过）。"""
        if not raw:
            return None
        m = re.match(r"^(\d{4})-(\d{1,2})-(\d{1,2})$", raw)
        if m:
            try:
                return date(int(m.group(1)), int(m.group(2)), int(m.group(3)))
            except ValueError:
                return None
        m = re.match(r"^(\d{1,2})月(\d{1,2})日$", raw)
        if m:
            month, day = int(m.group(1)), int(m.group(2))
            try:
                d = date(today.year, month, day)
            except ValueError:
                return None
            # 年度事件：今年已过（超出窗口）→ 顺延次年再判窗口
            if (d - today).days < 0:
                try:
                    d = date(today.year + 1, month, day)
                except ValueError:
                    return None
            return d
        return None

    def _reminder_line(self, key: str, date_str: str, days: int) -> str:
        if days == 0:
            return f"今天是用户的{key}（{date_str}），记得送上祝福"
        if days == 1:
            return f"明天（{date_str}）是用户的{key}"
        if days == -1:
            return f"昨天（{date_str}）是用户的{key}"
        if days > 1:
            return f"{days}天后（{date_str}）是用户的{key}"
        return f"{-days}天前（{date_str}）是用户的{key}"

    # ── 文本化 ──
    def _to_text(self, entry: ProfileEntry) -> str:
        """可读画像句：``（{类型中文}）{key}：{value}``（ADR-2）。"""
        label = PROFILE_TYPE_LABELS.get(entry.type, entry.type)
        return f"（{label}）{entry.key}：{entry.value}"
