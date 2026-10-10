"""对话会话记忆：按 session_id 维护多轮上下文，支持本地持久化。

「对话记忆」核心 —— 之前 session_id 永远固定为 "demo" 且后端完全未使用，
LLM 每轮只拿到单条最新消息。现在：每个前端生成独立 session_id（localStorage 持久化），
后端按会话累积历史，角色得以跨轮次/跨会话记住聊过的内容。

设计要点：
- 仅本地单用户使用，文件级持久化（每个 session 一个 JSON，重启不丢）。
- session_id 由前端生成（crypto.randomUUID），服务端做安全清洗（仅允许安全字符、限长），
  杜绝路径穿越。
- 轮次上限保护：超出后丢弃最早的轮次，避免 token 无限增长。
- **字符预算保护（P0-B）**：轮次上限只挡「条数」，挡不住「单条 MB 级」——
  实测确认原实现里 `token`/`budget`/`max_chars` 关键词计数为 0，一条 872MB 的回复
  依然能占满历史。故在条数上限之外再加一道**体量**闸（`max_total_chars`），
  从最旧开始丢弃直到进入预算，但**至少保留最近 1 轮**。
- 历史摘要：独立文件 `<sid>.summary.json` 落盘（不混入会话数组），供 orchestrator
  增量复用，避免每轮重复压缩同一批旧历史。
"""
import json
import logging
import os
import re
import threading
import time
from pathlib import Path

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

_SAFE = re.compile(r"^[A-Za-z0-9_-]{1,128}$")
_TURN_CAP = 40  # 最多保留的「用户+助手」轮次数（80 条消息）
# ── 字符预算（P0-B）──
# 默认 120_000 字符的依据：
#   1) 与条数上限对齐：_TURN_CAP=40 轮在「每轮接近满长」的最坏情况下约为
#      40 × 3_000 字符 = 120_000（云端档 max_tokens=2048 ≈ 中文 3_000 字/条）。
#      即：这个预算刚好装得下 40 轮正常长度对话，不会误伤正常使用。
#   2) 与模型上下文对齐：约 70k-120k token 量级，给 persona / RAG / 剧情注入
#      与当轮输出留出余量，不至于把上下文窗口挤爆。
#   3) 与故障量级拉开：被 mock 自我复制污染的会话实测达 7.77 亿字符，
#      本预算比它低 4 个数量级——既能让正常会话无损，又能立刻切断膨胀。
# 如需更长/更短记忆，用 ROLEPLAY_SESSION_MEMORY_MAX_CHARS 覆盖。
_CHAR_BUDGET = 120_000
# 至少保留的最近轮数（1 轮 = 至多 2 条消息）：宁可在单条超长时暂时越过预算，
# 也不把历史清空（角色「失忆」比上下文超长更糟）。
_MIN_KEEP_TURNS = 1
# 启动加载时单个会话文件的大小闸（防膨胀遗留：read_text 一个 GB 级 JSON 会直接
# 把进程内存打爆——实测正是 7.3GB 现场）。正常 40 轮会话文件仅 ~20KB。
_MAX_LOAD_FLOOR_BYTES = 4_000_000
_LOAD_BYTES_FACTOR = 32  # 实际上限 = max(4MB, 字符预算 × 32)
_SUMMARY_SUFFIX = ".summary"  # 摘要文件 <sid>.summary.json 的 stem 后缀，加载时跳过


class _Turn(BaseModel):
    role: str  # "user" | "assistant"
    content: str
    ts: float = Field(default_factory=time.time)


class SessionMemory:
    def __init__(
        self,
        persist_dir: Path | None = None,
        max_turns: int = _TURN_CAP,
        max_total_chars: int = _CHAR_BUDGET,
    ) -> None:
        """max_turns 限「条数」，max_total_chars 限「体量」——两道闸都生效。

        max_total_chars <= 0 表示关闭字符预算（仅保留条数上限，兼容旧行为）。
        """
        self._lock = threading.RLock()
        self._sessions: dict[str, list[_Turn]] = {}
        self._dir = persist_dir
        self._max = max_turns
        self._max_chars = max_total_chars
        if self._dir:
            try:
                self._dir.mkdir(parents=True, exist_ok=True)
                self._load_all()
            except OSError:
                self._dir = None  # 目录不可写则退化为纯内存

    @staticmethod
    def _safe(sid: str) -> str | None:
        """清洗 session_id：安全字符原样保留（前端 UUID 零迁移）；其余字符
        确定性转义为 _xHH 后仍限长 128，杜绝路径穿越/注入。

        此前对不安全 id 一律整条拒绝，而 QQ 渠道 id 形如 ``qq:private:123``
        含冒号，导致 get_history/append_many/clear 全部静默失效——QQ 多轮
        记忆为空、!clear 假成功。转义既保住文件名安全，又不丢渠道记忆。"""
        if not sid:
            return None
        if _SAFE.match(sid):
            return sid
        escaped = re.sub(r"[^A-Za-z0-9_-]", lambda m: "_x%02x" % ord(m.group(0)), sid)
        return escaped[:128] or None

    def append(self, session_id: str, role: str, content: str) -> None:
        sid = self._safe(session_id)
        if not sid:
            return
        content = (content or "").strip()
        if not content:
            return
        with self._lock:
            turns = self._sessions.setdefault(sid, [])
            turns.append(_Turn(role=role, content=content))
            self._trim(sid, turns)
            self._save(sid)

    def append_many(self, session_id: str, turns: list[tuple[str, str]]) -> None:
        """批量追加多条消息（如一轮对话的 user+assistant），单次加锁 + 单次落盘。

        热路径优化：一轮对话 2 次 append 会触发 2 次全量序列化/原子替换，
        批量后写放大减半，也减少事件循环内的同步 IO 次数。
        """
        sid = self._safe(session_id)
        if not sid or not turns:
            return
        items = [
            (role, (content or "").strip())
            for role, content in turns
            if (content or "").strip()
        ]
        if not items:
            return
        with self._lock:
            bucket = self._sessions.setdefault(sid, [])
            for role, content in items:
                bucket.append(_Turn(role=role, content=content))
            self._trim(sid, bucket)
            self._save(sid)

    # ── 截断（条数 + 体量双闸） ──
    def _trim(self, sid: str, turns: list[_Turn]) -> None:
        """就地截断：先按条数上限，再按字符预算（从最旧丢弃）。

        两道闸都在 `self._lock` 内调用，`_save` 之前执行，故落盘内容与内存一致。

        字符预算语义（P0-B）：
        - 从**最旧**开始丢，直到总字符数 ≤ max_total_chars。
        - **始终至少保留最近 `_MIN_KEEP_TURNS` 轮**（最多 2×N 条消息）；若首条就超预算，
          历史会暂时停留在「1 轮 + 1 条超长消息」，但不再吸收更多旧消息。
        - 单条消息本身超预算**不抛异常**：保留该条并记一条 warning（见下）。
        """
        # 闸 1：条数上限（原语义不变：_max 轮 = 至多 2×_max 条消息）
        limit = self._max * 2
        if len(turns) > limit:
            del turns[: len(turns) - limit]

        # 闸 2：字符预算
        if self._max_chars <= 0 or not turns:
            return
        keep = _MIN_KEEP_TURNS * 2  # 预留的最近条数（不做任何丢弃的下限）
        total = sum(len(t.content) for t in turns)
        if total <= self._max_chars:
            return
        drop = 0
        # 只允许丢到「还剩 keep 条」，保证最近 1 轮永远在。
        while drop < len(turns) - keep and total > self._max_chars:
            total -= len(turns[drop].content)
            drop += 1
        if drop:
            del turns[:drop]
            logger.warning(
                "会话 %s 历史超出字符预算 %d，已丢弃最早 %d 条消息（保留 %d 条）",
                sid,
                self._max_chars,
                drop,
                len(turns),
            )
        if total > self._max_chars:
            # 走到这里说明：剩下的全是最近 keep 条，其中至少一条自身就超预算。
            # 不抛异常——保留该条（角色不断片），只提示部署侧该回复异常长。
            logger.warning(
                "会话 %s 仍有 %d 字符超出预算 %d：单条消息自身超长（最长 %d 字符），"
                "按「至少保留最近 1 轮」保留，未做截断",
                sid,
                total,
                self._max_chars,
                max(len(t.content) for t in turns),
            )

    def get_history(self, session_id: str) -> list[dict]:
        """返回 OpenAI 格式的历史（不含当前轮），供 LLM 拼装 messages。"""
        sid = self._safe(session_id)
        if not sid:
            return []
        with self._lock:
            return [
                {"role": t.role, "content": t.content}
                for t in self._sessions.get(sid, [])
            ]

    def clear(self, session_id: str) -> bool:
        sid = self._safe(session_id)
        if not sid:
            return False
        with self._lock:
            self._sessions.pop(sid, None)
            if self._dir:
                try:
                    self._dir.joinpath(f"{sid}.json").unlink(missing_ok=True)
                    # 摘要与对话同生命周期：清空记忆时一并删除
                    self._summary_path(sid).unlink(missing_ok=True)
                except OSError:
                    pass
            return True

    # ── 历史摘要（独立文件，不混入会话数组） ──
    def _summary_path(self, sid: str) -> Path:
        return self._dir.joinpath(f"{sid}.summary.json")

    def get_summary(self, session_id: str) -> dict | None:
        """读取会话的历史摘要（无则返回 None）。"""
        sid = self._safe(session_id)
        if not sid or not self._dir:
            return None
        try:
            data = json.loads(self._summary_path(sid).read_text(encoding="utf-8"))
            if isinstance(data, dict):
                return data
        except (OSError, ValueError):
            pass
        return None

    def save_summary(self, session_id: str, summary: dict) -> None:
        """持久化会话摘要（原子写，复用 _save 的临时文件模式）。"""
        sid = self._safe(session_id)
        if not sid or not self._dir or not summary:
            return
        path = self._summary_path(sid)
        data = json.dumps(summary, ensure_ascii=False)
        tmp = path.with_name(f".{sid}.{os.getpid()}.tmp")
        try:
            tmp.write_text(data, encoding="utf-8")
            os.replace(tmp, path)
        except OSError:
            try:
                if tmp.exists():
                    tmp.unlink()
            except OSError:
                pass

    # ── 持久化（文件级，单用户本地足够） ──
    def _path(self, sid: str) -> Path:
        return self._dir.joinpath(f"{sid}.json")

    def _save(self, sid: str) -> None:
        if not self._dir:
            return
        path = self._path(sid)
        data = json.dumps(
            [t.model_dump() for t in self._sessions.get(sid, [])],
            ensure_ascii=False,
        )
        # 原子写：先写临时文件，再 os.replace 同盘替换（崩溃/断电不会留下半个文件）
        tmp = path.with_name(f".{sid}.{os.getpid()}.tmp")
        try:
            tmp.write_text(data, encoding="utf-8")
            os.replace(tmp, path)
        except OSError:
            try:
                if tmp.exists():
                    tmp.unlink()
            except OSError:
                pass

    def _load_all(self) -> None:
        # 单文件大小闸：膨胀遗留的会话文件可能是 GB 级，直接 read_text 会先把进程内存
        # 打爆（实测现场 7.3GB）。超限文件跳过加载并由上层重建（数据不值当为它 OOM）。
        max_bytes = max(_MAX_LOAD_FLOOR_BYTES, self._max_chars * _LOAD_BYTES_FACTOR)
        try:
            for f in self._dir.glob("*.json"):
                if f.stem.endswith(_SUMMARY_SUFFIX):
                    continue  # 摘要文件不是会话数组，跳过
                try:
                    size = f.stat().st_size
                    if size > max_bytes:
                        logger.warning(
                            "会话文件 %s 达 %d 字节（上限 %d），判定为膨胀遗留，跳过加载",
                            f.name,
                            size,
                            max_bytes,
                        )
                        continue
                    data = json.loads(f.read_text(encoding="utf-8"))
                    turns = [_Turn(**d) for d in data]
                except (OSError, ValueError, TypeError):
                    continue
                # 加载即截断：文件可能在上限之内但仍超预算（如 3MB 字符 ≈ 3M 字符）。
                # 只改内存，落盘留到下一次写入（避免启动期无谓 IO）。
                self._trim(f.stem, turns)
                self._sessions[f.stem] = turns
        except OSError:
            pass
