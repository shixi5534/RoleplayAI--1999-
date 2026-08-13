"""语音模块：STT/TTS 抽象层。

设计原则：
- 对 config.voice_* 字段提供后端实现
- STT: 本地 Whisper（通过 Ollama）或可扩展云端
- TTS: edge-tts 异步实现
- API 层仅做请求/响应封装，核心逻辑在此
"""

from .stt import transcribe_audio
from .tts import synthesize_speech

__all__ = ["transcribe_audio", "synthesize_speech"]
