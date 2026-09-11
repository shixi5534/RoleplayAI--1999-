"""语音 API 路由。

提供两个端点：
- POST /voice/stt   上传音频 → 返回识别文本
- POST /voice/tts    提交文本 → 返回音频流

前置依赖：
- STT: ROLEPLAY_STT_BACKEND_ENABLED=true + faster-whisper 安装
- TTS: ROLEPLAY_TTS_BACKEND_ENABLED=true + edge-tts 安装
"""
import logging
from typing import Annotated

from fastapi import APIRouter, Depends, File, Form, UploadFile
from fastapi.responses import JSONResponse, StreamingResponse

from ..config import Settings, get_settings
from ..core.voice import transcribe_audio, synthesize_speech
from .ratelimit import rate_limit

logger = logging.getLogger(__name__)

# TTS/STT 为重资源接口（调用外部服务/本地模型推理），挂限流防被无限刷
router = APIRouter(prefix="/voice", tags=["voice"], dependencies=[Depends(rate_limit)])


@router.post("/stt")
async def stt_endpoint(
    audio: Annotated[UploadFile, File(description="音频文件（wav/mp3/ogg）")],
    settings: Settings = Depends(get_settings),
) -> dict:
    """语音转文字。

    Args:
        audio: 上传的音频文件
        settings: 注入的配置

    Returns:
        {"text": "识别出的文本"}

    Raises:
        400: STT 后端未启用
        500: 识别失败
    """
    # 前置检查与 TTS 端对齐：未启用 STT 后端时返回 400，而非靠底层 RuntimeError 走 500
    if not settings.stt_backend_enabled:
        return JSONResponse(status_code=400, content={"detail": "STT 后端未启用（请设置 ROLEPLAY_STT_BACKEND_ENABLED=true）"})
    try:
        # 分块读取并限制大小（防内存 DoS：整文件读入内存会被数 GB 上传撑爆）
        # 上限 25MB（约 15 分钟 CD 音质 / 数小时压缩语音，远超对话场景需求）
        MAX_AUDIO_BYTES = 25 * 1024 * 1024
        chunks: list[bytes] = []
        total = 0
        # 用 read() 分块读取（兼容各版本 Starlette UploadFile；stream() 在部分版本不存在）
        while True:
            chunk = await audio.read(1024 * 1024)  # 1MB/块
            if not chunk:
                break
            total += len(chunk)
            if total > MAX_AUDIO_BYTES:
                logger.warning("STT 拒绝超大音频上传 (>25MB, 实际 %d bytes)", total)
                return JSONResponse(status_code=413, content={"detail": "音频文件过大（上限 25MB）"})
            chunks.append(chunk)
        audio_bytes = b"".join(chunks)
        if not audio_bytes or len(audio_bytes) < 32:
            # 空/极小文件：避免白白跑一次模型推理
            logger.warning("STT 拒绝空音频上传 (%d bytes)", len(audio_bytes))
            return JSONResponse(status_code=400, content={"detail": "音频为空或无法识别"})
        from io import BytesIO

        audio_stream = BytesIO(audio_bytes)
        text = await transcribe_audio(audio_stream, settings)
        return {"text": text}
    except RuntimeError as e:
        logger.error("STT 失败: %s", e)
        return JSONResponse(status_code=500, content={"detail": "语音识别失败，请查看服务日志"})
    except Exception as e:
        logger.error("STT 未预期异常: %s", e)
        return JSONResponse(status_code=500, content={"detail": "语音识别失败，请查看服务日志"})


@router.post("/tts")
async def tts_endpoint(
    text: Annotated[str, Form(description="要合成的文本", max_length=5000)],
    voice_id: Annotated[str | None, Form(description="角色专属声音ID")] = None,
    speed: Annotated[float | None, Form(description="语速 0.5-2.0")] = None,
    pitch: Annotated[float | None, Form(description="音调 -50~50")] = None,
    volume: Annotated[float | None, Form(description="音量 0-100")] = None,
    settings: Settings = Depends(get_settings),
) -> StreamingResponse:
    """文字转语音。

    Args:
        text: 要合成的文本（上限 5000 字符，防超大文本切出数千段逐段调 edge-tts）
        voice_id: 角色 voice_id（可选，默认用配置）
        speed: 语速（可选）
        pitch: 音调（可选）
        volume: 音量（可选）
        settings: 注入的配置

    Returns:
        音频流（MP3 格式）

    Raises:
        400: TTS 后端未启用
        500: 合成失败
    """
    # TTS 后端启用检查必须在构造 StreamingResponse 之前，
    # 否则 RuntimeError 会延迟到响应流迭代时才抛出，无法转为 JSON 错误。
    if not settings.tts_backend_enabled:
        logger.warning("TTS 请求被拒绝：后端未启用")
        return JSONResponse(
            status_code=400,
            content={"detail": "TTS 后端未启用，请设置 ROLEPLAY_TTS_BACKEND_ENABLED=true"},
        )
    try:
        return StreamingResponse(
            synthesize_speech(
                text,
                settings,
                voice_id=voice_id,
                speed=speed,
                pitch=pitch,
                volume=volume,
            ),
            media_type="audio/mpeg",
        )
    except RuntimeError as e:
        logger.error("TTS 失败: %s", e)
        return JSONResponse(status_code=500, content={"detail": "语音合成失败，请查看服务日志"})
    except Exception as e:
        logger.error("TTS 未预期异常: %s", e)
        return JSONResponse(status_code=500, content={"detail": "语音合成失败，请查看服务日志"})