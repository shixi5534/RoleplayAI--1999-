"""QQ 渠道适配器（OneBot v11 / NapCat）单元测试。

覆盖：
- 文本抽取：私聊 / 群@过滤 / 空文本 / 非文本段忽略
- 指令：!help / !clear / !char / !voice / !lang（含权限与群聊约束）
- 语音回复：record 段组装、发送失败降级、端到端语音+台词双发
- 端到端：启动客户端连本地 mock OneBot server，验证私聊转发、群@才回
"""
import asyncio
import json
import types

from websockets.asyncio.server import serve

from roleplay.channels.qq_onebot import QQChannel
from roleplay.core.voice.clip_store import ClipStore
from roleplay.core.voice.voice_reply import VoiceReplyService
from roleplay.models.chat import EmotionInfo


# ── 测试替身 ──
class _FakeResp:
    def __init__(self, reply, emotion=None):
        self.response = types.SimpleNamespace(
            reply=reply, emotion=emotion if emotion is not None else EmotionInfo()
        )


class _FakeOrch:
    def __init__(self, reply="角色回复", emotion=None):
        self._reply = reply
        self._emotion = emotion
        self.cleared = []
        self._character_store = None

    async def run(self, req):
        return _FakeResp(self._reply, self._emotion)

    def clear_session(self, sid):
        self.cleared.append(sid)
        return True


def _make_settings(**kw):
    defaults = dict(
        qq_bot_uin="10001",
        qq_group_at_only=True,
        qq_command_prefix="!",
        qq_allow_from="",
        qq_admin_uin="",
        qq_character_id="",
        qq_napcat_ws_url="ws://127.0.0.1:3001",
        qq_ws_token="",
        # 语音回复（默认全关，与生产 Settings 默认一致）
        qq_voice_enabled=False,
        qq_voice_lang="zh",
        qq_voice_clip_manifest="",
        qq_voice_emotion_threshold=0.6,
        qq_voice_cooldown_sec=60.0,
        qq_voice_max_sec=65.0,
        qq_voice_group_enabled=False,
    )
    defaults.update(kw)
    return types.SimpleNamespace(**defaults)


def _make_channel(orch=None, **kw):
    channel = QQChannel(orch or _FakeOrch())
    channel.settings = _make_settings(**kw)
    channel.bot_uin = channel.settings.qq_bot_uin
    channel._voice.settings = channel.settings  # 替身配置同步给语音服务
    return channel


# ── 文本抽取 ──
def test_extract_private_text():
    ch = _make_channel()
    assert ch._extract_text([{"type": "text", "data": {"text": "你好"}}], "private", None) == "你好"


def test_extract_group_at_returns_text():
    ch = _make_channel()
    segs = [
        {"type": "at", "data": {"qq": "10001"}},
        {"type": "text", "data": {"text": "在吗"}},
    ]
    assert ch._extract_text(segs, "group", 123) == "在吗"


def test_extract_group_no_at_returns_none():
    ch = _make_channel()
    segs = [{"type": "text", "data": {"text": "大家好"}}]
    assert ch._extract_text(segs, "group", 123) is None


def test_extract_group_at_disabled_replies_anyway():
    ch = _make_channel(qq_group_at_only=False)
    segs = [{"type": "text", "data": {"text": "大家好"}}]
    assert ch._extract_text(segs, "group", 123) == "大家好"


def test_extract_empty_text_returns_none():
    ch = _make_channel()
    assert ch._extract_text([{"type": "text", "data": {"text": "   "}}], "private", None) is None


def test_extract_image_only_returns_none():
    ch = _make_channel()
    segs = [{"type": "image", "data": {"url": "x"}}]
    assert ch._extract_text(segs, "private", None) is None


# ── 指令 ──
async def test_command_help():
    ch = _make_channel()
    out = await ch._handle_command("!help", "qq:private:20002", "20002")
    assert out and "!clear" in out and "!char" in out


async def test_command_clear():
    orch = _FakeOrch()
    ch = _make_channel(orch)
    ch._session_chars["qq:private:20002"] = "hero"
    out = await ch._handle_command("!clear", "qq:private:20002", "20002")
    assert out and "已清空" in out
    assert "qq:private:20002" in orch.cleared
    assert "qq:private:20002" not in ch._session_chars


async def test_command_char_lists():
    orch = _FakeOrch()
    orch._character_store = types.SimpleNamespace(
        list=lambda: [
            {"id": "a", "name": "A", "active": True},
            {"id": "b", "name": "B", "active": False},
        ]
    )
    ch = _make_channel(orch)
    out = await ch._handle_command("!char", "qq:private:20002", "20002")
    assert out and "可用角色" in out and "a（当前）" in out


async def test_command_char_switch():
    ch = _make_channel()
    out = await ch._handle_command("!char hero", "qq:private:20002", "20002")
    assert out and "hero" in out
    assert ch._session_chars["qq:private:20002"] == "hero"


async def test_command_unknown_falls_through():
    ch = _make_channel()
    assert await ch._handle_command("!nonsense", "qq:private:20002", "20002") is None


async def test_command_respects_admin():
    ch = _make_channel(qq_admin_uin="999")
    # 非管理员发指令 → 视为 None（回退普通对话）
    assert await ch._handle_command("!clear", "qq:private:20002", "20002") is None
    # 管理员可用
    out = await ch._handle_command("!clear", "qq:private:999", "999")
    assert out and "已清空" in out


# ── 语音指令 ──
async def test_command_voice_on_off():
    ch = _make_channel()
    sid = "qq:private:20002"
    out = await ch._handle_command("!voice on", sid, "20002")
    assert "已开启" in out and ch._voice.is_enabled(sid) is True
    out = await ch._handle_command("!voice off", sid, "20002")
    assert "已关闭" in out and ch._voice.is_enabled(sid) is False


async def test_command_voice_status_shows_usage():
    ch = _make_channel()
    out = await ch._handle_command("!voice", "qq:private:20002", "20002")
    assert "语音回复" in out and "voice on|off" in out


async def test_command_voice_on_rejected_in_group():
    ch = _make_channel()  # qq_voice_group_enabled 默认 False
    out = await ch._handle_command(
        "!voice on", "qq:group:555:20002", "20002", is_group=True
    )
    assert "群聊语音未开放" in out
    assert ch._voice.is_enabled("qq:group:555:20002") is False


async def test_command_lang_switch():
    ch = _make_channel()
    sid = "qq:private:20002"
    out = await ch._handle_command("!lang en", sid, "20002")
    assert "英文" in out and ch._voice.get_lang(sid) == "en"
    out = await ch._handle_command("!lang zh", sid, "20002")
    assert "中文" in out and ch._voice.get_lang(sid) == "zh"
    out = await ch._handle_command("!lang", sid, "20002")
    assert "用法" in out


async def test_clear_resets_voice_session_state():
    ch = _make_channel()
    sid = "qq:private:20002"
    ch._voice.set_enabled(sid, True)
    ch._voice.set_lang(sid, "en")
    out = await ch._handle_command("!clear", sid, "20002")
    assert "已清空" in out
    assert ch._voice.is_enabled(sid) is False  # 回到全局默认（关）
    assert ch._voice.get_lang(sid) == "zh"


async def test_handle_returns_reply_and_emotion():
    ch = _make_channel()
    sid = "qq:private:20002"
    reply, emotion = await ch._handle("你好", sid, "20002")
    assert reply == "角色回复"
    assert emotion is not None and emotion.emotion == "neutral"
    # 指令回复：文本有效、情绪为 None
    reply, emotion = await ch._handle("!help", sid, "20002")
    assert "!clear" in reply and emotion is None


# ── 语音发送 ──
def _decision(**kw):
    from roleplay.core.voice.voice_reply import VoiceDecision

    defaults = dict(
        audio=b"mp3-bytes", kind="clip", slot="happy", clip_id="zh_h1",
        lang="zh", duration=5.0, subtitle={"zh": "台词", "en": "line"},
    )
    defaults.update(kw)
    return VoiceDecision(**defaults)


async def test_send_voice_builds_record_segment():
    import base64

    ch = _make_channel()
    captured = {}

    async def fake_send_msg(message="", user_id=None, group_id=None, *,
                            segments=None, wait_response=False):
        captured["segments"] = segments
        captured["user_id"] = user_id
        captured["wait_response"] = wait_response
        return {"status": "ok"}

    ch._send_msg = fake_send_msg
    assert await ch._send_voice(user_id="20002", msg_id=1001, decision=_decision()) is True
    assert captured["wait_response"] is True  # 语音必须等应答判定成败
    segs = captured["segments"]
    assert segs[0] == {"type": "reply", "data": {"id": "1001"}}
    assert segs[1]["type"] == "record"
    payload = segs[1]["data"]["file"]
    assert payload.startswith("base64://")
    assert base64.b64decode(payload[len("base64://"):]) == b"mp3-bytes"


async def test_send_voice_degrades_on_send_failure():
    ch = _make_channel()

    async def fake_send_timeout(message="", user_id=None, group_id=None, *,
                                segments=None, wait_response=False):
        return None  # 连接异常 / 应答超时

    ch._send_msg = fake_send_timeout
    assert await ch._send_voice(user_id="20002", decision=_decision()) is False

    async def fake_send_failed(message="", user_id=None, group_id=None, *,
                               segments=None, wait_response=False):
        return {"status": "failed", "retcode": 1200}  # NapCat 转码失败等

    ch._send_msg = fake_send_failed
    assert await ch._send_voice(user_id="20002", decision=_decision()) is False


# ── 端到端（本地 mock OneBot server） ──
async def _run_e2e(message_event, expect_reply=True):
    received = []

    async def handler(ws):
        await ws.send(json.dumps(message_event))
        async for msg in ws:
            data = json.loads(msg)
            if data.get("action") == "send_msg":
                received.append(data["params"]["message"])
                break

    orch = _FakeOrch(reply="角色回复: 收到")
    async with serve(handler, "127.0.0.1", 0) as server:
        port = server.sockets[0].getsockname()[1]
        ch = _make_channel(orch)
        ch.settings.qq_napcat_ws_url = f"ws://127.0.0.1:{port}"
        task = asyncio.create_task(ch.start())
        try:
            for _ in range(100):
                if received or not expect_reply:
                    break
                await asyncio.sleep(0.05)
        finally:
            ch.stop()
            task.cancel()
            try:
                await task
            except (asyncio.CancelledError, Exception):
                pass
    return received


async def test_e2e_private_message():
    event = {
        "post_type": "message",
        "message_type": "private",
        "user_id": 20002,
        "sender": {"user_id": 20002},
        "message": [{"type": "text", "data": {"text": "你好"}}],
    }
    received = await _run_e2e(event, expect_reply=True)
    assert received and "角色回复: 收到" in received[0]


async def test_e2e_group_at_replies():
    event = {
        "post_type": "message",
        "message_type": "group",
        "group_id": 555,
        "user_id": 20002,
        "sender": {"user_id": 20002},
        "message": [
            {"type": "at", "data": {"qq": "10001"}},
            {"type": "text", "data": {"text": "在吗"}},
        ],
    }
    received = await _run_e2e(event, expect_reply=True)
    assert received and "角色回复: 收到" in received[0]


async def test_e2e_group_no_at_ignored():
    event = {
        "post_type": "message",
        "message_type": "group",
        "group_id": 555,
        "user_id": 20002,
        "sender": {"user_id": 20002},
        "message": [{"type": "text", "data": {"text": "大家好"}}],
    }
    received = await _run_e2e(event, expect_reply=False)
    assert received == []


# ── 端到端：语音回复（record 段 + 台词文本，LLM 文字不再发） ──
def _write_clip_manifest(root):
    """造一个最小切片库：happy 槽位中/英各一条，音频为占位字节。"""
    root.mkdir(parents=True, exist_ok=True)
    (root / "zh").mkdir(exist_ok=True)
    (root / "en").mkdir(exist_ok=True)
    clips = [
        {"id": "zh_h1", "lang": "zh", "file": "zh/h1.mp3", "dur": 5.0,
         "subtitle": {"zh": "中配台词", "en": "en line"}},
        {"id": "en_h1", "lang": "en", "file": "en/h1.mp3", "dur": 4.0,
         "subtitle": {"zh": "英配台词中文", "en": "en line"}},
    ]
    manifest = {
        "character": "tester", "version": 1, "langs": ["zh", "en"],
        "clips": clips, "slots": {"happy": ["zh_h1", "en_h1"]},
    }
    for c in clips:
        (root / c["file"]).write_bytes(f"audio:{c['id']}".encode())
    path = root / "manifest.json"
    path.write_text(json.dumps(manifest, ensure_ascii=False), encoding="utf-8")
    return path


async def test_e2e_voice_reply_sends_record_then_subtitle(tmp_path):
    manifest_path = _write_clip_manifest(tmp_path / "voice")
    event = {
        "post_type": "message",
        "message_type": "private",
        "user_id": 20002,
        "message_id": 1001,
        "sender": {"user_id": 20002},
        "message": [{"type": "text", "data": {"text": "今天太开心了"}}],
    }
    received = []

    async def handler(ws):
        await ws.send(json.dumps(event))
        async for msg in ws:
            data = json.loads(msg)
            if data.get("action") == "send_msg":
                received.append(data["params"]["message"])
                # 模拟 NapCat 应答（语音发送等应答判定成败）
                await ws.send(json.dumps(
                    {"status": "ok", "retcode": 0, "echo": data.get("echo")}
                ))
                if len(received) >= 2:
                    break

    orch = _FakeOrch(
        reply="角色回复: 收到",
        emotion=EmotionInfo(emotion="happy", score=0.9, source="llm"),
    )
    async with serve(handler, "127.0.0.1", 0) as server:
        port = server.sockets[0].getsockname()[1]
        ch = _make_channel(orch, qq_voice_enabled=True)
        ch._voice = VoiceReplyService(ch.settings, store=ClipStore(manifest_path))
        ch.settings.qq_napcat_ws_url = f"ws://127.0.0.1:{port}"
        task = asyncio.create_task(ch.start())
        try:
            for _ in range(100):
                if len(received) >= 2:
                    break
                await asyncio.sleep(0.05)
        finally:
            ch.stop()
            task.cancel()
            try:
                await task
            except (asyncio.CancelledError, Exception):  # noqa: BLE001
                pass

    assert len(received) == 2
    first = received[0]
    assert isinstance(first, list)  # 消息段数组
    assert first[0] == {"type": "reply", "data": {"id": "1001"}}
    assert first[1]["type"] == "record"
    assert first[1]["data"]["file"].startswith("base64://")
    assert received[1] == "中配台词"  # 与配音语言同步的台词文本


async def test_e2e_low_emotion_still_gets_text_reply(tmp_path):
    """语音开但情绪不达标 → 照常收到 LLM 文字（零回归语义）。"""
    event = {
        "post_type": "message",
        "message_type": "private",
        "user_id": 20002,
        "sender": {"user_id": 20002},
        "message": [{"type": "text", "data": {"text": "今天天气如何"}}],
    }
    received = []

    async def handler(ws):
        await ws.send(json.dumps(event))
        async for msg in ws:
            data = json.loads(msg)
            if data.get("action") == "send_msg":
                received.append(data["params"]["message"])
                break

    orch = _FakeOrch(
        reply="角色回复: 收到",
        emotion=EmotionInfo(emotion="happy", score=0.4, source="llm"),  # 低于 0.6 阈值
    )
    async with serve(handler, "127.0.0.1", 0) as server:
        port = server.sockets[0].getsockname()[1]
        ch = _make_channel(orch, qq_voice_enabled=True)
        ch._voice = VoiceReplyService(
            ch.settings, store=ClipStore(_write_clip_manifest(tmp_path / "voice"))
        )
        ch.settings.qq_napcat_ws_url = f"ws://127.0.0.1:{port}"
        task = asyncio.create_task(ch.start())
        try:
            for _ in range(100):
                if received:
                    break
                await asyncio.sleep(0.05)
        finally:
            ch.stop()
            task.cancel()
            try:
                await task
            except (asyncio.CancelledError, Exception):  # noqa: BLE001
                pass

    assert received and "角色回复: 收到" in received[0]
