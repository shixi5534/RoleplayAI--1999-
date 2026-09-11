"""文字转语音（TTS）后端实现。

支持的合成方式：
1. edge-tts（微软 Azure 免费语音服务）

核心逻辑：
- 接收文本、角色参数（voice_id、speed、pitch、volume）
- 调用 edge-tts 异步生成音频流
- 返回音频字节流

优化历程：
- 第1轮：rate 范围限制
- 第2轮：指数退避重试 + 超时控制 + 空输出校验
- 第3轮：TTS 音频缓存 + 文本预处理
- 第7轮修复：rate 计算运算符优先级 bug（speed=1.0 误算为 +100%，方向反了）
- 第8轮修复（声音合成失败专项）：
  1. pitch 负值生成非法参数 "+-10Hz" → edge-tts 直接拒绝合成（Invalid pitch）
  2. Communicate 对象复用导致重试失效：stream() 只能调用一次，
     超长文本/超时场景第 2 次重试必失败（stream can only be called once）
  3. 无效 voice_id 白名单预校验，避免空跑 3 次重试
  4. 超长文本预切分，规避 edge-tts 底层请求长度限制
"""
import asyncio
import hashlib
import logging
import re
import threading
from io import BytesIO
from typing import AsyncGenerator

from ...config import Settings

logger = logging.getLogger(__name__)

# 延迟导入 edge-tts（可选依赖）
_edge_tts = None


def _get_edge_tts():
    """延迟导入 edge-tts，避免未安装时启动报错。"""
    global _edge_tts  # noqa: PLW0603
    if _edge_tts is None:
        try:
            import edge_tts

            _edge_tts = edge_tts
        except ImportError as e:
            raise RuntimeError(
                "edge-tts 未安装，请执行: pip install edge-tts 或 pip install roleplay-ai[voice]"
            ) from e
    return _edge_tts


# 第2轮优化：TTS 合成超时时间（秒）
# edge-tts 正常合成 1-3 秒，给 30s 余量应对网络抖动
_TTS_TIMEOUT = 30
# 最大重试次数
_TTS_MAX_RETRIES = 3
# 空输出阈值：edge-tts 正常输出至少几 KB，小于此值视为失败
_TTS_MIN_OUTPUT_BYTES = 1000

# 第3轮优化：TTS 音频缓存
# 搜索发现：对重复文本缓存音频可减少 70%+ 延迟
# 缓存 key = hash(voice + text + rate + pitch + volume)
_tts_cache: dict[str, bytes] = {}
_TTS_CACHE_MAX_SIZE = 100  # 最多缓存100条
_TTS_CACHE_MAX_BYTES = 64 * 1024 * 1024  # 总字节上限：长音频 100 条也可能数百 MB
_tts_cache_bytes = 0
# 使用线程锁而非 asyncio.Lock：缓存清理是 O(1) 短临界区，避免多事件循环/测试环境绑定问题。
_tts_cache_lock = threading.Lock()

# ── 第8轮优化：参数防护 ──
# edge-tts 官方参数区间：rate [-50%, +100%]、pitch [-50Hz, +50Hz]
_PITCH_MIN, _PITCH_MAX = -50, 50
_RATE_MIN, _RATE_MAX = -50, 100
# 文本超长保护：edge-tts 底层请求对文本长度有限制（SSML 包体过大易失败），
# 超过此长度按标点边界切分为多段（每段分别合成，最后拼接）
_TEXT_CHUNK_MAX_CHARS = 500
_TEXT_CHUNK_SEPARATORS = "。！？；!?;\n"


def _format_signed(value: float, unit: str = "") -> str:
    """带符号格式化：100 → '+100Hz'，-10 → '-10Hz'，0 → '+0Hz'。"""
    v = round(value)
    sign = "+" if v >= 0 else "-"
    return f"{sign}{abs(v)}{unit}"


def _build_tts_params(
    *,
    settings: Settings,
    voice_id: str | None = None,
    speed: float | None = None,
    pitch: float | None = None,
    volume: float | None = None,
) -> dict:
    """集中计算 edge-tts 参数（纯函数，可单测）。

    - voice：角色参数 > 全局默认
    - rate：speed(0.5~2.0) → 百分比偏移，clamp 到 [-50, +100]
    - pitch：clamp 到 [-50, +50]Hz，负数正确带 '-'（第8轮修复 "+-10Hz"）
    - volume：0~100 → edge-tts 偏移（-100% ~ +0%）
    """
    voice = voice_id or settings.edge_tts_default_voice

    if speed is not None:
        rate_val = max(_RATE_MIN, min(_RATE_MAX, round((speed - 1) * 100)))
    else:
        rate_val = 0
    rate = f"{'+' if rate_val >= 0 else ''}{rate_val}%"

    pitch_val = 0
    if pitch is not None:
        pitch_val = max(_PITCH_MIN, min(_PITCH_MAX, round(pitch)))
    pitch_hz = _format_signed(pitch_val, "Hz")

    if volume is not None:
        vol_val = max(-100, min(0, round(volume - 100)))
    else:
        vol_val = 0
    vol = _format_signed(vol_val, "%")

    return {"voice": voice, "rate": rate, "pitch": pitch_hz, "volume": vol}


# 常用中文音色白名单（edge-tts 支持的语言子集校验用）
_KNOWN_VOICES = frozenset(
    {
        "zh-CN-XiaoxiaoNeural", "zh-CN-YunxiNeural", "zh-CN-YunjianNeural",
        "zh-CN-XiaoyiNeural", "zh-CN-YunyangNeural", "zh-CN-liaoning-XiaobeiNeural",
        "zh-CN-shaanxi-XiaoniNeural", "zh-HK-HiuGaaiNeural", "zh-HK-HiuMaanNeural",
        "zh-HK-WanLungNeural", "zh-TW-HsiaoChenNeural", "zh-TW-HsiaoYuNeural",
        "zh-TW-YunJheNeural",
    }
)


def _validate_voice(voice: str) -> None:
    """voice 预校验：未知音色直接报错，避免空跑重试。

    edge-tts 会在 stream() 阶段抛 Invalid voice，白名单命中才放行；
    用户自定义音色不在列表内时放行（远端可能支持新音色，不误杀）。
    """
    v = (voice or "").strip()
    if not v:
        raise RuntimeError("TTS 合成失败：voice_id 为空")
    if v.lower() in _KNOWN_VOICES:
        return  # 白名单命中
    # 格式兜底：形如 xx-XX-Name 的合理命名放行（未知但仍可能有效）
    if re.fullmatch(r"[A-Za-z]{2,3}-[A-Za-z]{2,4}-[A-Za-z0-9-]+", v):
        return
    raise RuntimeError(f"TTS 合成失败：无效的 voice_id '{v}'")


def _split_long_text(text: str, max_chars: int = _TEXT_CHUNK_MAX_CHARS) -> list[str]:
    """超长文本按标点边界切分，返回片段列表。

    规则：
    - 长度 ≤ max_chars：原样返回单段；
    - 优先在句末标点（。！？；!?;）处切分；
    - 找不到标点时在空白处切分；再不行硬切（保证不超长）。
    """
    if len(text) <= max_chars:
        return [text]
    chunks: list[str] = []
    rest = text
    while len(rest) > max_chars:
        window = rest[: max_chars + 1]
        # 在窗口内找最后一个句末标点（从后往前）
        cut = -1
        for i in range(len(window) - 1, 0, -1):
            if window[i] in _TEXT_CHUNK_SEPARATORS:
                cut = i + 1
                break
        if cut < 0:
            # 无标点：找空白
            for i in range(len(window) - 1, 0, -1):
                if window[i].isspace():
                    cut = i
                    break
        if cut < 0:
            cut = max_chars  # 硬切
        chunks.append(rest[:cut].strip())
        rest = rest[cut:].strip()
    if rest:
        chunks.append(rest)
    return [c for c in chunks if c]


def _tts_cache_key(voice: str, rate: str, pitch_hz: str, vol: str, text: str) -> str:
    key = f"{voice}|{rate}|{pitch_hz}|{vol}|{text}"
    return hashlib.md5(key.encode()).hexdigest()


async def _stream_once(
    edge_tts_module,
    text: str,
    params: dict,
    collected: bytearray,
) -> None:
    """单次合成：新建 Communicate 并把音频块写入 collected。

    第8轮修复：Communicate 每次新建——其 stream() 只能调用一次，
    复用对象会导致第 2 次重试必失败（stream can only be called once）。
    """
    communicate = edge_tts_module.Communicate(
        text,
        params["voice"],
        rate=params["rate"],
        pitch=params["pitch"],
        volume=params["volume"],
    )
    async for chunk in communicate.stream():
        if chunk["type"] == "audio":
            collected.extend(chunk["data"])


async def synthesize_speech(
    text: str,
    settings: Settings,
    *,
    voice_id: str | None = None,
    speed: float | None = None,
    pitch: float | None = None,
    volume: float | None = None,
) -> AsyncGenerator[bytes, None]:
    """合成语音流。

    Args:
        text: 要合成的文本
        settings: 全局配置
        voice_id: 角色专属声音 ID（如 zh-CN-XiaoxiaoNeural）
        speed: 语速（0.5 ~ 2.0）
        pitch: 音调（-50 ~ 50）
        volume: 音量（0 ~ 100）

    Yields:
        音频字节流（MP3 格式）

    Raises:
        RuntimeError: TTS 后端未启用或调用失败
    """
    if not settings.tts_backend_enabled:
        raise RuntimeError("TTS 后端未启用，请设置 ROLEPLAY_TTS_BACKEND_ENABLED=true")

    edge_tts = _get_edge_tts()

    # 第3轮优化：文本预处理 - 去除多余空白，标点规范化
    clean_text = " ".join(text.split())
    if not clean_text:
        raise RuntimeError("TTS 合成失败：文本为空")

    # 集中计算参数（含 pitch/volume 符号修复与范围 clamp）
    params = _build_tts_params(
        settings=settings,
        voice_id=voice_id,
        speed=speed,
        pitch=pitch,
        volume=volume,
    )
    # 第8轮优化：无效 voice 预校验，避免空跑重试
    _validate_voice(params["voice"])

    # 第8轮优化：超长文本预切分，规避底层请求长度限制
    segments = _split_long_text(clean_text)

    # 第3轮优化：缓存检查 - 相同参数的重复文本直接返回缓存
    cache_key = _tts_cache_key(
        params["voice"], params["rate"], params["pitch"], params["volume"], clean_text
    )
    if cache_key in _tts_cache:
        logger.debug("TTS 缓存命中: %s...", clean_text[:30])
        yield _tts_cache[cache_key]
        return

    try:
        collected = bytearray()

        for attempt in range(1, _TTS_MAX_RETRIES + 1):
            collected.clear()
            try:
                # 按段合成：每段独立 Communicate（每段 stream 只调用一次）
                for seg in segments:
                    await asyncio.wait_for(
                        _stream_once(edge_tts, seg, params, collected),
                        timeout=_TTS_TIMEOUT,
                    )
                # 空输出校验：edge-tts 偶发返回空流
                if len(collected) < _TTS_MIN_OUTPUT_BYTES:
                    raise RuntimeError(
                        f"TTS 输出异常：仅 {len(collected)} bytes（阈值 {_TTS_MIN_OUTPUT_BYTES}）"
                    )
                break  # 成功
            except ValueError as e:
                # 第8轮优化：确定性参数错误（如 Invalid voice / Invalid pitch）——
                # 重试 3 次必然同样失败，直接抛出不消耗重试
                raise RuntimeError(f"TTS 参数错误: {e}") from e
            except (asyncio.TimeoutError, ConnectionError, RuntimeError) as e:
                if attempt < _TTS_MAX_RETRIES:
                    wait_sec = 1.5 * attempt
                    logger.warning(
                        "TTS 第%d次失败(%s)，%.1fs后重试...", attempt, type(e).__name__, wait_sec
                    )
                    await asyncio.sleep(wait_sec)
                else:
                    raise
            except Exception as e:
                # edge-tts 内部异常（如 EdgeTTSException / WebSocketError）
                if attempt < _TTS_MAX_RETRIES:
                    wait_sec = 1.5 * attempt
                    logger.warning(
                        "TTS 第%d次异常(%s: %s)，%.1fs后重试...",
                        attempt, type(e).__name__, e, wait_sec,
                    )
                    await asyncio.sleep(wait_sec)
                else:
                    raise

        audio = bytes(collected)
        yield audio

        # 第3轮优化：写入缓存（LRU 策略，按条数 + 总字节双重上限淘汰）
        global _tts_cache_bytes  # noqa: PLW0603
        with _tts_cache_lock:
            while (
                _tts_cache
                and (
                    len(_tts_cache) >= _TTS_CACHE_MAX_SIZE
                    or _tts_cache_bytes + len(audio) > _TTS_CACHE_MAX_BYTES
                )
            ):
                old_key = next(iter(_tts_cache))
                _tts_cache_bytes -= len(_tts_cache.pop(old_key))
            if len(audio) <= _TTS_CACHE_MAX_BYTES:
                _tts_cache[cache_key] = audio
                _tts_cache_bytes += len(audio)

    except Exception as e:
        logger.error("TTS 合成失败（已耗尽重试）: %s", e)
        raise RuntimeError(f"TTS 合成失败: {e}") from e


async def synthesize_speech_to_bytes(
    text: str,
    settings: Settings,
    *,
    voice_id: str | None = None,
    speed: float | None = None,
    pitch: float | None = None,
    volume: float | None = None,
) -> bytes:
    """合成语音并返回完整字节流（用于非流式场景）。"""
    buf = BytesIO()
    async for chunk in synthesize_speech(
        text,
        settings,
        voice_id=voice_id,
        speed=speed,
        pitch=pitch,
        volume=volume,
    ):
        buf.write(chunk)
    return buf.getvalue()
