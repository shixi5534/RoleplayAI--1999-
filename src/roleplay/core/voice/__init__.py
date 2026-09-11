"""语音模块：STT/TTS 抽象层。

设计原则：
- 对 config.voice_* 字段提供后端实现
- STT: 本地 faster-whisper 或可扩展云端
- TTS: edge-tts 异步实现
- API 层仅做请求/响应封装，核心逻辑在此
"""

# 延迟导入：STT 模块 import 时会设置 CT2/OMP 环境变量并创建线程池，
# 语音功能默认关闭，不应在应用启动时产生这些副作用。
def transcribe_audio(*args, **kwargs):
    from .stt import transcribe_audio as _fn

    return _fn(*args, **kwargs)


def synthesize_speech(*args, **kwargs):
    from .tts import synthesize_speech as _fn

    return _fn(*args, **kwargs)


__all__ = ["transcribe_audio", "synthesize_speech"]
