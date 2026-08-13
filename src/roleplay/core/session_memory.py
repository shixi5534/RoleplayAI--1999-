"""对话会话记忆：按 session_id 维护多轮上下文，支持本地持久化。

「对话记忆」核心 —— 之前 session_id 永远固定为 "demo" 且后端完全未使用，
LLM 每轮只拿到单条最新消息。现在：每个前端生成独立 session_id（localStorage 持久化），
后端按会话累积历史，角色得以跨轮次/跨会话记住聊过的内容。

设计要点：
- 仅本地单用户使用，文件级持久化（每个 session 一个 JSON，重启不丢）。
- session_id 由前端生成（crypto.randomUUID），服务端做安全清洗（仅允许安全字符、限长），
  杜绝路径穿越。
- 轮次上限保护：超出后丢弃最早的轮次，避免 token 无限增长。
- 历史摘要：独立文件 `<sid>.summary.json` 落盘（不混入会话数组），供 orchestrator
  增量复用，避免每轮重复压缩同一批旧历史。
"""
import json
import os
import re
import threading
import time
from pathlib import Path

from pydantic import BaseModel, Field

_SAFE = re.compile(r"^[A-Za-z0-9_-]{1,128}$")
_TURN_CAP = 40  # 最多保留的「用户+助手」轮次数（80 条消息）
_SUMMARY_SUFFIX = ".summary"  # 摘要文件 <sid>.summary.json 的 stem 后缀，加载时跳过


class _Turn(BaseModel):
    role: str  # "user" | "assistant"
    content: str
    ts: float = Field(default_factory=time.time)


class SessionMemory:
    def __init__(self, persist_dir: Path | None = None, max_turns: int = _TURN_CAP) -> None:
        self._lock = threading.RLock()
        self._sessions: dict[str, list[_Turn]] = {}
        self._dir = persist_dir
        self._max = max_turns
        if self._dir:
            try:
                self._dir.mkdir(parents=True, exist_ok=True)
                self._load_all()
            except OSError:
                self._dir = None  # 目录不可写则退化为纯内存

    @staticmethod
    def _safe(sid: str) -> str | None:
        """清洗 session_id：仅允许安全字符，拒绝路径穿越/注入。"""
        if sid and _SAFE.match(sid):
            return sid
        return None

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
            if len(turns) > self._max * 2:
                del turns[: len(turns) - self._max * 2]
            self._save(sid)

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
        try:
            for f in self._dir.glob("*.json"):
                if f.stem.endswith(_SUMMARY_SUFFIX):
                    continue  # 摘要文件不是会话数组，跳过
                try:
                    data = json.loads(f.read_text(encoding="utf-8"))
                    self._sessions[f.stem] = [_Turn(**d) for d in data]
                except (OSError, ValueError, TypeError):
                    continue
        except OSError:
            pass
