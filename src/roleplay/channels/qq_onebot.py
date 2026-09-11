"""QQ 渠道适配器：OneBot v11 WebSocket 客户端（对接 NapCatQQ）。

职责边界（严格只做渠道，不动大脑）：
- 连接 NapCat 暴露的正向 OneBot v11 WebSocket；
- 收事件 → 解析纯文本 → 构造 ChatRequest → 调 ChatOrchestrator.run()；
- 把 ChatResponse.reply 通过 OneBot send_msg 发回 QQ；命中语音条件时改发
  角色原声切片（base64 record 段，失败静默降级文字），决策见 core/voice/voice_reply；
- 支持断线重连、!clear/!help/!char/!voice/!lang 指令、get_login_info 兜底 bot_uin。

人设 / RAG / 情感 / 会话记忆全部复用 ChatOrchestrator，本模块零业务逻辑。
"""
from __future__ import annotations

import asyncio
import base64
import json
import logging
from typing import Any

from websockets.asyncio.client import connect as ws_connect
from websockets.exceptions import ConnectionClosed

from ..config import get_settings
from ..core.orchestrator import ChatOrchestrator
from ..core.voice.voice_reply import VoiceDecision, VoiceReplyService
from ..models.chat import ChatRequest, EmotionInfo

logger = logging.getLogger(__name__)

_ACTION_ID = 0  # OneBot 动作自增 id（回协用）


class QQChannel:
    """一个 QQ 号的 OneBot v11 客户端。

    生命周期：start() 进入重连主循环，直到 stop() 被调用或任务被取消。
    """

    def __init__(self, orch: ChatOrchestrator) -> None:
        self.settings = get_settings()
        self.orch = orch
        self.bot_uin: str = self.settings.qq_bot_uin or ""
        self.ws: Any = None
        self._send_lock = asyncio.Lock()
        self._pending: dict[str, asyncio.Future] = {}  # echo -> Future[response]
        self._session_chars: dict[str, str] = {}  # session_id -> character_id 覆盖
        self._voice = VoiceReplyService(self.settings)  # 语音回复决策（会话态在其内部）
        self._stop = asyncio.Event()
        self._reconnect_delay = 1.0
        self._tasks: set[asyncio.Task] = set()  # 消息处理任务强引用（防 GC 中途回收）

    # ── 生命周期 ──
    async def start(self) -> None:
        self._stop.clear()
        while not self._stop.is_set():
            try:
                await self._connect_loop()
            except asyncio.CancelledError:
                # 任务被取消：直接退出主循环（上下文管理器会关闭 WS）
                break
            except Exception as exc:  # noqa: BLE001
                logger.warning(
                    "QQ 渠道连接异常，%ss 后重连：%s", self._reconnect_delay, exc
                )
            if self._stop.is_set():
                break
            await asyncio.sleep(self._reconnect_delay)
            self._reconnect_delay = min(self._reconnect_delay * 2, 30.0)
        logger.info("QQ 渠道已停止")

    def stop(self) -> None:
        self._stop.set()

    # ── 连接 / 重连 ──
    async def _connect_loop(self) -> None:
        url = self.settings.qq_napcat_ws_url
        token = self.settings.qq_ws_token
        display_url = url
        if token:
            sep = "&" if "?" in url else "?"
            url = f"{url}{sep}access_token={token}"
            display_url = url.replace(f"access_token={token}", "access_token=***")
        logger.info("QQ 渠道连接 NapCat：%s", display_url)
        async with ws_connect(
            url, ping_interval=20, ping_timeout=20, close_timeout=10
        ) as ws:  # 断线时上下文退出 → 触发重连
            self.ws = ws
            self._reconnect_delay = 1.0  # 连上了，重置退避
            if not self.bot_uin:
                info = await self._call_action("get_login_info", wait_response=True)
                uid = (info or {}).get("data", {}).get("user_id")
                if uid:
                    self.bot_uin = str(uid)
            logger.info("QQ 渠道已连接，bot_uin=%s", self.bot_uin or "(未知)")
            msg_count = 0
            try:
                async for raw in ws:
                    msg_count += 1
                    try:
                        data = json.loads(raw)
                    except (json.JSONDecodeError, TypeError):
                        continue
                    await self._dispatch(data)
            except ConnectionClosed as e:
                logger.warning(
                    "QQ WS 连接被关闭 code=%s reason=%r 已收消息=%d",
                    e.code, e.reason, msg_count,
                )
                raise
            except Exception as exc:  # noqa: BLE001
                logger.warning("QQ WS 读取异常，已收消息=%d：%s", msg_count, exc)
                raise

    # ── 事件分发 ──
    async def _dispatch(self, data: dict) -> None:
        # 动作回协：路由回等待中的 Future（如 get_login_info）
        echo = data.get("echo")
        if echo is not None:
            fut = self._pending.pop(echo, None)
            if fut is not None and not fut.done():
                fut.set_result(data)
            return
        post_type = data.get("post_type")
        if post_type == "meta_event":
            return  # lifecycle / heartbeat：无需处理
        if post_type == "message":
            # 尽快交出去，避免阻塞 WS 读循环（并发用户各跑各的会话锁）。
            # 必须持有强引用并记录异常：裸 create_task 只留弱引用，任务可能
            # 被 GC 中途回收，任务内异常也会被静默吞掉（丢回复无迹可查）。
            task = asyncio.create_task(self._on_message(data))
            self._tasks.add(task)
            task.add_done_callback(self._on_message_done)
        # notice / request 等忽略

    def _on_message_done(self, task: asyncio.Task) -> None:
        self._tasks.discard(task)
        if not task.cancelled() and task.exception() is not None:
            logger.error("QQ 消息处理异常：%s", task.exception())

    # ── 消息接入 ──
    async def _on_message(self, data: dict) -> None:
        msg_type = data.get("message_type")  # private / group
        sender = data.get("sender", {})
        user_id = str(sender.get("user_id", ""))
        group_id = data.get("group_id")
        text = self._extract_text(data.get("message"), msg_type, group_id)
        logger.info("QQ 收到消息 type=%s user=%s group=%s text=%r", msg_type, user_id, group_id, text)
        if text is None:
            return  # 群内未@ / 无法解析 → 忽略

        # 私聊白名单
        if msg_type == "private" and self.settings.qq_allow_from:
            allowed = {u.strip() for u in self.settings.qq_allow_from.split(",") if u.strip()}
            if user_id not in allowed:
                logger.info("QQ 私聊被白名单拦截：%s", user_id)
                return

        session_id = (
            f"qq:private:{user_id}" if msg_type == "private"
            else f"qq:group:{group_id}:{user_id}"
        )
        is_group = msg_type == "group"
        handled = await self._handle(text, session_id, user_id, is_group=is_group)
        if not handled:
            return
        reply, emotion = handled

        # 语音回复（默认关）：命中 → 发原声切片；发送失败降级文字（绝不丢回复）。
        # 成功时附带台词文本，让用户看到"她说了什么"（与配音语言同步）。
        decision = self._voice.decide(session_id, emotion, is_group=is_group)
        if decision is not None:
            voice_ok = await self._send_voice(
                user_id=None if is_group else user_id,
                group_id=group_id if is_group else None,
                msg_id=data.get("message_id"),
                decision=decision,
            )
            if voice_ok:
                subtitle = (decision.subtitle or {}).get(decision.lang, "")
                if subtitle:
                    await self._send_msg(
                        message=subtitle,
                        user_id=None if is_group else user_id,
                        group_id=group_id if is_group else None,
                    )
                return

        if is_group:
            await self._send_msg(group_id=group_id, message=reply)
        else:
            await self._send_msg(user_id=user_id, message=reply)

    def _extract_text(self, message: Any, msg_type: str | None, group_id: Any) -> str | None:
        """从 OneBot message（str 或 segment 数组）抽取纯文本。

        - 群聊且开启仅@才回、且消息未@机器人 → 返回 None（不回复）。
        - 图片/语音/表情等非文本段 v1 忽略。
        """
        if isinstance(message, str):
            segments = [{"type": "text", "data": {"text": message}}]
        elif isinstance(message, list):
            segments = message
        else:
            return None

        at_bot = False
        parts: list[str] = []
        for seg in segments:
            t = seg.get("type")
            if t == "text":
                parts.append(seg.get("data", {}).get("text", ""))
            elif t == "at":
                qq = str(seg.get("data", {}).get("qq", ""))
                if qq and qq == self.bot_uin:
                    at_bot = True
            # 其它类型（image/voice/face/reply…）v1 不处理
        raw = "".join(parts).strip()
        if msg_type == "group" and self.settings.qq_group_at_only and not at_bot:
            return None
        return raw or None

    # ── 业务逻辑（薄封装，全交给 Orchestrator） ──
    async def _handle(
        self, text: str, session_id: str, user_id: str, *, is_group: bool = False
    ) -> tuple[str, EmotionInfo | None] | None:
        """处理一条消息，返回 (回复文本, 情绪信号)。

        情绪信号来自 Orchestrator 对用户消息的检测，供语音触发判定使用；
        指令回复无情绪（None）。
        """
        prefix = self.settings.qq_command_prefix
        if text.startswith(prefix):
            handled = await self._handle_command(
                text, session_id, user_id, is_group=is_group
            )
            if handled is not None:
                return handled, None
            # 未知指令 → 当作普通消息（去掉前缀，避免把 "!" 当内容）
            text = text[len(prefix):].strip()
            if not text:
                return None

        char_id = self._session_chars.get(session_id) or (
            self.settings.qq_character_id or None
        )
        try:
            req = ChatRequest(
                session_id=session_id,
                message=text,
                character_id=char_id or None,
            )
        except Exception as exc:  # noqa: BLE001
            logger.warning("QQ ChatRequest 校验失败：%s", exc)
            return "（消息内容不合规，无法处理）", None
        try:
            res = await self.orch.run(req)
            return res.response.reply, res.response.emotion
        except Exception as exc:  # noqa: BLE001
            logger.exception("QQ 渠道调用 Orchestrator 失败")
            return "（暂时无法回复，请稍后再试）", None

    async def _handle_command(
        self, text: str, session_id: str, user_id: str, *, is_group: bool = False
    ) -> str | None:
        # 指令权限：设了管理员则仅管理员可用；否则对所有人开放（个人小号场景）
        admin = self.settings.qq_admin_uin.strip()
        if admin and user_id != admin:
            return None

        prefix = self.settings.qq_command_prefix
        body = text[len(prefix):].strip()
        cmd = body.split(" ", 1)[0].lower()

        if cmd in ("help", "帮助", "?"):
            return (
                f"QQ 角色扮演指令：\n"
                f"{prefix}help  - 显示本帮助\n"
                f"{prefix}clear - 清空与你的对话记忆\n"
                f"{prefix}char  - 查看可用角色\n"
                f"{prefix}char <角色id> - 切换角色\n"
                f"{prefix}voice on|off - 开/关语音回复（情绪够强时出声）\n"
                f"{prefix}lang zh|en - 切换配音语言（只影响语音，不影响回复语种）"
            )
        if cmd == "clear":
            self.orch.clear_session(session_id)
            self._session_chars.pop(session_id, None)
            self._voice.clear_session(session_id)
            return "已清空与你的对话记忆。"
        if cmd == "char":
            arg = body[len(cmd):].strip()
            store = getattr(self.orch, "_character_store", None)
            if not arg:
                if store is not None and hasattr(store, "list"):
                    items = store.list()
                    if items:
                        lines = "，".join(
                            f"{it['id']}{'（当前）' if it.get('active') else ''}"
                            for it in items
                        )
                        return f"可用角色：{lines}\n切换：{prefix}char <角色id>"
                return "（未启用多角色）"
            self._session_chars[session_id] = arg
            return f"已切换到角色：{arg}"
        if cmd == "voice":
            arg = body[len(cmd):].strip().lower()
            if arg in ("on", "开", "开启", "打开"):
                if is_group and not self.settings.qq_voice_group_enabled:
                    return "群聊语音未开放（ROLEPLAY_QQ_VOICE_GROUP_ENABLED=false），暂无法开启。"
                self._voice.set_enabled(session_id, True)
                return (
                    f"语音回复已开启（当前配音：{self._voice.get_lang(session_id)}），"
                    f"仅本会话生效。"
                )
            if arg in ("off", "关", "关闭"):
                self._voice.set_enabled(session_id, False)
                return "语音回复已关闭。"
            state = "开" if self._voice.is_enabled(session_id) else "关"
            return f"语音回复：{state}，配音：{self._voice.get_lang(session_id)}。用法：{prefix}voice on|off"
        if cmd == "lang":
            arg = body[len(cmd):].strip().lower()
            if arg in ("zh", "中", "中文", "zh-cn"):
                self._voice.set_lang(session_id, "zh")
                return "配音已切换：中文。"
            if arg in ("en", "英", "英文", "english", "en-us"):
                self._voice.set_lang(session_id, "en")
                return "配音已切换：英文。"
            return (
                f"当前配音：{self._voice.get_lang(session_id)}。"
                f"用法：{prefix}lang zh|en（只影响语音，不影响回复语种）"
            )
        return None  # 未知指令 → 回退普通对话

    # ── OneBot 动作（API 调用） ──
    async def _call_action(
        self, action: str, params: dict | None = None, *, wait_response: bool = False
    ) -> dict | None:
        global _ACTION_ID
        if self.ws is None:
            return None
        _ACTION_ID += 1
        echo = f"qq-{_ACTION_ID}"
        payload = {"action": action, "params": params or {}, "echo": echo}
        fut: asyncio.Future | None = None
        if wait_response:
            fut = asyncio.get_running_loop().create_future()
            self._pending[echo] = fut
        try:
            async with self._send_lock:
                await self.ws.send(json.dumps(payload, ensure_ascii=False))
        except Exception as exc:  # noqa: BLE001
            logger.warning("QQ 渠道发送动作失败：%s", exc)
            self._pending.pop(echo, None)
            return None
        if fut is not None:
            try:
                return await asyncio.wait_for(fut, timeout=5.0)
            except asyncio.TimeoutError:
                self._pending.pop(echo, None)
                return None
        return None

    async def _send_msg(
        self,
        message: str = "",
        user_id: Any = None,
        group_id: Any = None,
        *,
        segments: list[dict] | None = None,
        wait_response: bool = False,
    ) -> dict | None:
        """发消息。segments 非空时发消息段数组（语音等富消息），否则发纯文本。

        wait_response=True 时等待 OneBot 应答并返回（含 status/retcode，可判定
        发送成败）；False 为既有的"发后即忘"，返回 None。原有纯文本调用的
        行为不变（零回归）。
        """
        params: dict[str, Any] = {
            "message": segments if segments is not None else message
        }
        if user_id is not None:
            params["message_type"] = "private"
            params["user_id"] = int(user_id) if str(user_id).isdigit() else user_id
        else:
            params["message_type"] = "group"
            params["group_id"] = int(group_id) if str(group_id).isdigit() else group_id
        return await self._call_action(
            "send_msg", params, wait_response=wait_response
        )

    async def _send_voice(
        self,
        *,
        user_id: Any = None,
        group_id: Any = None,
        msg_id: Any = None,
        decision: VoiceDecision,
    ) -> bool:
        """发一条语音：引用原消息（可选）+ base64 record 段。

        base64 优先：file:// 是 NapCat 进程所在机器的路径，跨机/Docker 部署会失效；
        单条切片仅几十~几百 KB，base64 无额外代价。NapCat 内置 ffmpeg 自动转 silk。
        返回 False 时由调用方降级发文字（绝不因为语音失败而丢回复）。
        """
        b64 = base64.b64encode(decision.audio).decode("ascii")
        segments: list[dict] = []
        if msg_id:
            segments.append({"type": "reply", "data": {"id": str(msg_id)}})
        segments.append({"type": "record", "data": {"file": f"base64://{b64}"}})
        try:
            # 语音必须等应答才能判定成败（普通文本发后即忘，行为不变）；
            # resp 为 None（连接异常/应答超时）或 status=failed（如 silk 转码失败）→ 降级
            resp = await self._send_msg(
                user_id=user_id,
                group_id=group_id,
                segments=segments,
                wait_response=True,
            )
        except Exception:  # noqa: BLE001
            logger.exception("QQ 语音发送异常，降级文字")
            return False
        status = (resp or {}).get("status")
        if resp is None or status == "failed":
            logger.warning(
                "QQ 语音发送失败(status=%s, clip=%s)，降级文字；"
                "请检查 NapCat 版本（silk 转码 bug 已在 4.9.21 修复）与 ffmpeg 是否安装",
                status, decision.clip_id,
            )
            return False
        return True


async def start_qq_channel(app) -> None:
    """应用生命周期入口：取出 orchestrator 并启动 QQ 渠道。"""
    orch = getattr(app.state, "orchestrator", None)
    if orch is None:
        logger.warning("QQ 渠道启动失败：未找到 app.state.orchestrator")
        return
    channel = QQChannel(orch)
    await channel.start()
