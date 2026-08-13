"""测试公共夹具。

- 固定为离线 mock 配置（不依赖任何 API Key / 网络）。
- 将 src/ 加入 sys.path，无需先 pip install 即可导入 roleplay 包。
- 提供 detector / orchestrator / client 三个核心 fixture。
"""
import os
import sys
import tempfile
from pathlib import Path

# 在任何 app 模块导入前固定配置
# 用直接赋值（而非 setdefault）确保覆盖任何已存在的环境变量，强制离线、跳过 Ollama 探测
os.environ["ROLEPLAY_LLM_PROVIDER"] = "mock"
os.environ["ROLEPLAY_RAG_IMPL"] = "memory"
os.environ["ROLEPLAY_EMBEDDER"] = "hashing"
os.environ["ROLEPLAY_ENABLE_EMOTION"] = "true"
os.environ["ROLEPLAY_ENABLE_LIVE2D"] = "false"
os.environ["ROLEPLAY_ENABLE_WEB"] = "false"  # 测试不联网，避免网络超时拖慢/挂起
os.environ["ROLEPLAY_EMOTION_DETECTOR"] = "keyword"  # 测试默认最快路径（不触发 LLM/分类器）
# 用户画像：固定测试配置（提取节奏 2 轮加速验证；LLM 层 mock 模式零外发）
os.environ["ROLEPLAY_PROFILE_ENABLED"] = "true"
os.environ["ROLEPLAY_PROFILE_EXTRACT_EVERY"] = "2"
os.environ["ROLEPLAY_PROFILE_TOP_K"] = "3"
os.environ["ROLEPLAY_PROFILE_MAX_ITEMS"] = "200"
os.environ["ROLEPLAY_PROFILE_LLM_TIMEOUT"] = "8.0"
os.environ["ROLEPLAY_PROFILE_SYNONYM_THRESHOLD"] = "0.85"
os.environ["ROLEPLAY_PROFILE_REMINDER_DAYS"] = "3"
os.environ["ROLEPLAY_PROFILE_NAMESPACE"] = "profile"

# 持久化目录指向临时目录：避免加载/污染真实 ./data（尤其 smoke 测试遗留数据），
# 同时让每次 app 构建只需种子一个人设，显著提速并保持用例隔离。
_TMP = Path(tempfile.mkdtemp(prefix="roleplay_test_"))
os.environ["ROLEPLAY_KNOWLEDGE_DIR"] = str(_TMP / "knowledge")
os.environ["ROLEPLAY_CHARACTERS_DIR"] = str(_TMP / "characters")
os.environ["ROLEPLAY_SESSION_MEMORY_DIR"] = str(_TMP / "sessions")

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

from roleplay.config import get_settings  # noqa: E402
from roleplay.core.emotion.detector import KeywordEmotionDetector  # noqa: E402
from roleplay.core.llm.mock import MockLLMProvider  # noqa: E402
from roleplay.core.rag.memory import InMemoryVectorStore  # noqa: E402
from roleplay.core.orchestrator import ChatOrchestrator  # noqa: E402


@pytest.fixture
def settings():
    get_settings.cache_clear()
    yield get_settings()
    get_settings.cache_clear()


@pytest.fixture
def detector():
    return KeywordEmotionDetector(enabled=True)


@pytest.fixture
def orchestrator():
    orch = ChatOrchestrator(
        llm=MockLLMProvider(),
        emotion=KeywordEmotionDetector(enabled=True),
        rag=InMemoryVectorStore(),
        enable_emotion=True,
    )
    orch._rag.add(
        ["我喜欢在雨天散步，听雨声很放松。", "工作压力大时可以深呼吸放松。"]
    )
    return orch


@pytest.fixture
def client():
    from roleplay.api.deps import build_orchestrator
    from roleplay.main import app

    # TestClient 上下文会触发 lifespan，自动把编排器装配进 app.state
    with TestClient(app) as c:
        yield c
