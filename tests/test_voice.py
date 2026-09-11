"""语音后端（STT/TTS）单元测试。

测试策略：
- Mock faster-whisper / edge-tts 外部依赖，避免真实网络调用
- 验证 API 路由、参数传递、错误处理

注意（2026-07-31 第7轮修复适配）：
- STT 后端第1轮从 Ollama Whisper 重写为 faster-whisper 本地推理，
  测试相应从 mock httpx 改为 mock faster_whisper.WhisperModel
- TTS 后端第2轮加入空输出校验（>1000 bytes），mock 的 stream 输出
  必须超过该阈值，否则触发 RuntimeError
"""
import asyncio
import io
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from roleplay.config import Settings, get_settings
from roleplay.main import app


@pytest.fixture
def settings_with_stt():
    """启用 STT 的配置。"""
    return Settings(
        stt_backend_enabled=True,
        whisper_model="base",
        whisper_model_path="C:/Users/Lenovo/fw_model",
        voice_request_timeout=30.0,
    )


@pytest.fixture
def settings_with_tts():
    """启用 TTS 的配置。"""
    return Settings(
        tts_backend_enabled=True,
        edge_tts_default_voice="zh-CN-XiaoxiaoNeural",
        tts_default_format="mp3",
    )


@pytest.fixture
def settings_voice_disabled():
    """语音后端禁用的配置。"""
    return Settings(
        stt_backend_enabled=False,
        tts_backend_enabled=False,
    )


class TestSTT:
    """STT 单元测试。"""

    @pytest.mark.asyncio
    async def test_stt_disabled_raises(self, settings_voice_disabled):
        """STT 未启用时应抛出 RuntimeError。"""
        from roleplay.core.voice.stt import transcribe_audio

        audio = io.BytesIO(b"fake audio data")
        with pytest.raises(RuntimeError, match="STT 后端未启用"):
            await transcribe_audio(audio, settings_voice_disabled)

    @pytest.mark.asyncio
    @patch("roleplay.core.voice.stt._get_whisper_model")
    async def test_stt_success(self, mock_get_model, settings_with_stt):
        """STT 成功返回文本（faster-whisper 本地推理）。"""
        from roleplay.core.voice.stt import transcribe_audio

        # Mock faster_whisper.WhisperModel.transcribe 返回一个 segment
        class _FakeSegment:
            text = "你好，世界"

        class _FakeSegments:
            def __iter__(self):
                return iter([_FakeSegment()])

        mock_model = MagicMock()
        mock_model.transcribe.return_value = (_FakeSegments(), MagicMock())
        mock_get_model.return_value = mock_model

        audio = io.BytesIO(b"fake audio data")

        result = await transcribe_audio(audio, settings_with_stt)
        assert result == "你好，世界"
        # 验证 transcribe 被调用且使用中文
        _, kwargs = mock_model.transcribe.call_args
        assert kwargs["language"] == "zh"


class TestTTS:
    """TTS 单元测试。"""

    @pytest.mark.asyncio
    async def test_tts_disabled_raises(self, settings_voice_disabled):
        """TTS 未启用时应抛出 RuntimeError。"""
        from roleplay.core.voice.tts import synthesize_speech_to_bytes

        with pytest.raises(RuntimeError, match="TTS 后端未启用"):
            await synthesize_speech_to_bytes("你好", settings_voice_disabled)
    @pytest.mark.asyncio
    @patch("roleplay.core.voice.tts._get_edge_tts")
    async def test_tts_success(self, mock_get_edge_tts, settings_with_tts):
        """TTS 成功返回音频流。"""
        from roleplay.core.voice.tts import synthesize_speech_to_bytes

        # 注意：输出必须 > _TTS_MIN_OUTPUT_BYTES(1000)，否则触发空输出校验
        chunk = b"a" * 1200

        # Mock edge_tts.Communicate.stream() 为异步迭代器
        async def mock_stream():
            yield {"type": "audio", "data": chunk}

        mock_communicate = MagicMock()
        mock_communicate.stream.return_value = mock_stream()

        mock_edge_tts = MagicMock()
        mock_edge_tts.Communicate.return_value = mock_communicate
        mock_get_edge_tts.return_value = mock_edge_tts

        result = await synthesize_speech_to_bytes("测试文本", settings_with_tts, voice_id="zh-CN-XiaoxiaoNeural")
        assert result == chunk

    @pytest.mark.asyncio
    @patch("roleplay.core.voice.tts._get_edge_tts")
    async def test_tts_with_custom_params(self, mock_get_edge_tts, settings_with_tts):
        """TTS 支持自定义参数。"""
        from roleplay.core.voice.tts import synthesize_speech_to_bytes

        chunk = b"a" * 1200

        async def mock_stream():
            yield {"type": "audio", "data": chunk}

        mock_communicate = MagicMock()
        mock_communicate.stream.return_value = mock_stream()

        mock_edge_tts = MagicMock()
        mock_edge_tts.Communicate.return_value = mock_communicate
        mock_get_edge_tts.return_value = mock_edge_tts

        result = await synthesize_speech_to_bytes(
            "测试",
            settings_with_tts,
            voice_id="zh-CN-YunxiNeural",
            speed=1.2,
            pitch=10,
            volume=80,
        )
        assert result == chunk
        # 验证参数传递
        call_args = mock_edge_tts.Communicate.call_args
        assert call_args[0][0] == "测试"
        assert call_args[0][1] == "zh-CN-YunxiNeural"
        # 验证语速映射：speed=1.2 → rate=+20%（第7轮修复后）
        kwargs = call_args[1] if len(call_args) > 1 else {}
        rate = kwargs.get("rate") if kwargs else call_args[0][2] if len(call_args[0]) > 2 else ""
        assert "+20%" in str(rate)


# ---------------------------------------------------------------------------
# 第8轮 TTS 合成失败专项修复测试
# 覆盖：pitch 负值符号、参数 clamp、Communicate 重试重建、文本切分、确定性错误不重试
# ---------------------------------------------------------------------------

class TestTTSParams:
    """_build_tts_params 纯函数（参数集中计算）。"""

    def _mk(self, **kw):
        from roleplay.core.voice.tts import _build_tts_params

        s = Settings(tts_backend_enabled=True, edge_tts_default_voice="zh-CN-XiaoxiaoNeural")
        return _build_tts_params(settings=s, **kw)

    def test_pitch_negative_sign(self):
        """pitch 负值必须生成 '-10Hz'（第8轮修复：原为非法 '+-10Hz'）。"""
        p = self._mk(pitch=-10)
        assert p["pitch"] == "-10Hz"

    def test_pitch_positive_and_zero(self):
        assert self._mk(pitch=10)["pitch"] == "+10Hz"
        assert self._mk(pitch=0)["pitch"] == "+0Hz"
        assert self._mk(pitch=None)["pitch"] == "+0Hz"

    def test_pitch_clamped(self):
        """pitch 超界 clamp 到 [-50, 50]。"""
        assert self._mk(pitch=-100)["pitch"] == "-50Hz"
        assert self._mk(pitch=100)["pitch"] == "+50Hz"

    def test_rate_mapping_and_clamp(self):
        assert self._mk(speed=1.0)["rate"] == "+0%"
        assert self._mk(speed=1.2)["rate"] == "+20%"
        assert self._mk(speed=0.5)["rate"] == "-50%"
        assert self._mk(speed=2.0)["rate"] == "+100%"
        # 越界 clamp
        assert self._mk(speed=3.0)["rate"] == "+100%"
        assert self._mk(speed=0.1)["rate"] == "-50%"
        assert self._mk(speed=None)["rate"] == "+0%"

    def test_volume_mapping(self):
        """volume(0~100) → edge-tts 偏移（-100% ~ +0%）。"""
        assert self._mk(volume=100)["volume"] == "+0%"
        assert self._mk(volume=50)["volume"] == "-50%"
        assert self._mk(volume=0)["volume"] == "-100%"
        assert self._mk(volume=None)["volume"] == "+0%"

    def test_voice_precedence(self):
        p = self._mk(voice_id="zh-CN-YunxiNeural")
        assert p["voice"] == "zh-CN-YunxiNeural"
        # 未指定 voice_id 用全局默认
        p2 = self._mk()
        assert p2["voice"] == "zh-CN-XiaoxiaoNeural"


class TestTTSVoiceValidation:
    def test_known_voice_passes(self):
        from roleplay.core.voice.tts import _validate_voice

        _validate_voice("zh-CN-XiaoxiaoNeural")  # 不应抛

    def test_empty_voice_raises(self):
        from roleplay.core.voice.tts import _validate_voice

        with pytest.raises(RuntimeError, match="voice_id 为空"):
            _validate_voice("")
        with pytest.raises(RuntimeError, match="voice_id 为空"):
            _validate_voice("  ")

    def test_bad_format_voice_raises_fast(self):
        """格式明显非法的 voice 立即拒绝（不空跑重试）。"""
        from roleplay.core.voice.tts import _validate_voice

        with pytest.raises(RuntimeError, match="无效的 voice_id"):
            _validate_voice("not-a-voice!!")

    def test_unknown_format_voice_passes(self):
        """格式合法但不在白名单（远端可能新增音色）：放行交给 edge-tts 判断。"""
        from roleplay.core.voice.tts import _validate_voice

        _validate_voice("zh-CN-NewVoiceNeural")  # 不应抛


class TestTTSTextSplitting:
    def test_short_text_single_chunk(self):
        from roleplay.core.voice.tts import _split_long_text

        assert _split_long_text("你好世界") == ["你好世界"]

    def test_long_text_split_on_punct(self):
        from roleplay.core.voice.tts import _split_long_text

        text = "第一句。第二句！第三句？" * 20  # 240 字，max_chars=500 内不分
        chunks = _split_long_text(text, max_chars=50)
        assert len(chunks) > 1
        assert all(len(c) <= 50 for c in chunks)
        # 每段以句末标点结束（标点边界切分）
        assert all(c[-1] in "。！？" for c in chunks)

    def test_long_text_no_punct_hard_split(self):
        from roleplay.core.voice.tts import _split_long_text

        text = "无标点文本" * 100  # 500 字无标点
        chunks = _split_long_text(text, max_chars=50)
        assert len(chunks) > 1
        assert all(len(c) <= 50 for c in chunks)
        # 拼接回原文（无损）
        assert "".join(chunks) == text

    def test_all_chunks_non_empty(self):
        from roleplay.core.voice.tts import _split_long_text

        text = "短。中！长？" * 30
        chunks = _split_long_text(text, max_chars=20)
        assert chunks and all(c for c in chunks)


class TestTTSRetryRebuild:
    """第8轮修复：重试必须新建 Communicate（stream() 只能调用一次）。"""

    @pytest.mark.asyncio
    @patch("roleplay.core.voice.tts._get_edge_tts")
    async def test_retry_creates_new_communicate(self, mock_get_edge_tts, settings_with_tts):
        from roleplay.core.voice.tts import synthesize_speech_to_bytes

        chunk = b"a" * 1200
        calls = {"n": 0}

        def make_stream():
            async def stream_once():
                calls["n"] += 1
                if calls["n"] == 1:
                    raise ConnectionError("first attempt network error")
                yield {"type": "audio", "data": chunk}

            return stream_once()

        mock_communicate = MagicMock()
        mock_communicate.stream.side_effect = lambda: make_stream()

        mock_edge_tts = MagicMock()
        mock_edge_tts.Communicate.return_value = mock_communicate
        mock_get_edge_tts.return_value = mock_edge_tts

        result = await synthesize_speech_to_bytes("测试重试", settings_with_tts)
        assert result == chunk
        # 重试 2 次 = 新建 2 个 Communicate（第8轮修复前复用一个对象必失败）
        assert mock_edge_tts.Communicate.call_count == 2

    @pytest.mark.asyncio
    @patch("roleplay.core.voice.tts._get_edge_tts")
    async def test_deterministic_value_error_no_retry(self, mock_get_edge_tts, settings_with_tts):
        """确定性参数错误（Invalid voice）立即失败，不消耗重试。"""
        from roleplay.core.voice.tts import synthesize_speech_to_bytes

        async def bad_stream():
            if False:  # noqa: SIM210 - 让函数成为 async generator（含 yield 才能被 async for 迭代）
                yield b""
            raise ValueError("Invalid voice 'zh-CN-Nope'")

        mock_communicate = MagicMock()
        mock_communicate.stream.return_value = bad_stream()

        mock_edge_tts = MagicMock()
        mock_edge_tts.Communicate.return_value = mock_communicate
        mock_get_edge_tts.return_value = mock_edge_tts

        with pytest.raises(RuntimeError, match="参数错误"):
            await synthesize_speech_to_bytes("测试", settings_with_tts)
        # 只尝试 1 次（第8轮修复前会重试 3 次）
        assert mock_edge_tts.Communicate.call_count == 1


class TestVoiceAPI:
    """语音 API 路由测试。

    使用 app.dependency_overrides[get_settings] 覆盖 FastAPI 依赖注入，
    而非 patch 模块属性（后者无法影响路由已导入的函数引用）。
    参考 tests/test_api.py::test_rate_limit_triggers 的正确写法。

    注意：get_settings 被 lru_cache 缓存，override 前必须 cache_clear()，
    否则 FastAPI 解析依赖时命中缓存实例，override 的 lambda 不生效。
    """

    @staticmethod
    def _apply_settings(settings_obj):
        get_settings.cache_clear()
        app.dependency_overrides[get_settings] = lambda: settings_obj

    def test_stt_endpoint_disabled(self, settings_voice_disabled):
        """STT 端点未启用时返回 400（前置检查，与 TTS 端点语义对齐）。"""
        self._apply_settings(settings_voice_disabled)
        try:
            with TestClient(app) as client:
                # 音频 >32 bytes 以通过空音频校验，从而走到后端禁用检查
                response = client.post(
                    "/voice/stt",
                    files={"audio": ("test.wav", b"x" * 100, "audio/wav")},
                )
                assert response.status_code == 400
        finally:
            app.dependency_overrides.pop(get_settings, None)

    def test_stt_endpoint_empty_audio(self, settings_voice_disabled):
        """STT 端点空音频返回 400（第7轮审核新增校验）。"""
        self._apply_settings(settings_voice_disabled)
        try:
            with TestClient(app) as client:
                response = client.post(
                    "/voice/stt",
                    files={"audio": ("test.wav", b"", "audio/wav")},
                )
                assert response.status_code == 400
        finally:
            app.dependency_overrides.pop(get_settings, None)

    def test_tts_endpoint_disabled(self, settings_voice_disabled):
        """TTS 端点未启用时返回 400（与 STT 端点语义对齐）。"""
        self._apply_settings(settings_voice_disabled)
        try:
            with TestClient(app) as client:
                response = client.post(
                    "/voice/tts",
                    data={"text": "你好"},
                )
                assert response.status_code == 400
        finally:
            app.dependency_overrides.pop(get_settings, None)

    @patch("roleplay.core.voice.stt._get_whisper_model")
    def test_stt_endpoint_success(self, mock_get_model, settings_with_stt):
        """STT 端点成功返回识别结果。"""
        # Mock faster-whisper
        class _FakeSegment:
            text = "识别结果"

        class _FakeSegments:
            def __iter__(self):
                return iter([_FakeSegment()])

        mock_model = MagicMock()
        mock_model.transcribe.return_value = (_FakeSegments(), MagicMock())
        mock_get_model.return_value = mock_model

        self._apply_settings(settings_with_stt)
        try:
            with TestClient(app) as client:
                response = client.post(
                    "/voice/stt",
                    files={"audio": ("test.wav", b"x" * 100, "audio/wav")},
                )
                assert response.status_code == 200
                assert response.json() == {"text": "识别结果"}
        finally:
            app.dependency_overrides.pop(get_settings, None)

    @patch("roleplay.core.voice.tts._get_edge_tts")
    def test_tts_endpoint_success(self, mock_get_edge_tts, settings_with_tts):
        """TTS 端点成功返回音频流。"""
        chunk = b"a" * 1200  # 必须 > 1000 阈值

        async def mock_stream():
            yield {"type": "audio", "data": chunk}

        mock_communicate = MagicMock()
        mock_communicate.stream.return_value = mock_stream()

        mock_edge_tts = MagicMock()
        mock_edge_tts.Communicate.return_value = mock_communicate
        mock_get_edge_tts.return_value = mock_edge_tts

        self._apply_settings(settings_with_tts)
        try:
            with TestClient(app) as client:
                response = client.post(
                    "/voice/tts",
                    data={"text": "测试文本"},
                )
                assert response.status_code == 200
                assert response.content == chunk
                assert response.headers["content-type"] == "audio/mpeg"
        finally:
            app.dependency_overrides.pop(get_settings, None)
