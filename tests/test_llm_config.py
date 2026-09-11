"""LLM 配置接口测试（前端「模型切换」功能配套）。

覆盖：
- GET  /api/llm/config   脱敏配置：绝不返回 api_key，含云端预设与 ollama 默认地址
- GET  /api/llm/ollama/models  Ollama 拉取失败时优雅降级（不抛 500）
- POST /api/llm/test     连通性测试：ollama 空 key 兜底；云端无效 key 返回 ok=false
- ChatRequest.llm        LLMOverride 字段校验（provider 枚举 / 长度边界）
"""
import json

import pytest
from fastapi.testclient import TestClient

from roleplay.main import app


@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c


class TestLLMConfig:
    def test_config_never_leaks_api_key(self, client):
        resp = client.get("/api/llm/config")
        assert resp.status_code == 200
        data = resp.json()
        # 脱敏契约：响应里绝不能出现 key 本身，只有 has_api_key 布尔
        assert "api_key" not in data
        assert "has_api_key" in data
        assert isinstance(data["has_api_key"], bool)
        # 必备字段
        assert data["provider"]
        assert data["model"]
        assert "cloud_presets" in data
        assert data["ollama_default_url"] == "http://localhost:11434"

    def test_config_cloud_presets_contain_openai_and_deepseek(self, client):
        data = client.get("/api/llm/config").json()
        presets = data["cloud_presets"]
        assert "openai" in presets and "deepseek" in presets
        assert "models" in presets["openai"] and presets["openai"]["models"]
        assert "base_url" in presets["openai"]

    def test_ollama_models_endpoint_fallback(self, client):
        # Ollama 未启动/不可达时：200 + 空列表 + error 说明（不抛 500，前端回退默认清单）
        resp = client.get("/api/llm/ollama/models")
        assert resp.status_code == 200
        data = resp.json()
        assert "models" in data and isinstance(data["models"], list)
        assert "error" in data


class TestLLMTest:
    def test_test_validation_rejects_bad_provider(self, client):
        resp = client.post("/api/llm/test", json={"provider": "not-a-provider", "model": "x"})
        assert resp.status_code == 422  # pydantic 枚举校验

    def test_test_requires_model(self, client):
        resp = client.post("/api/llm/test", json={"provider": "ollama", "model": ""})
        assert resp.status_code == 422  # min_length=1

    def test_test_ollama_mock_returns_ok(self, client, monkeypatch):
        # 注入假 provider：连通性测试应返回 ok=true
        class FakeProvider:
            def __init__(self, **kwargs):
                pass

            async def generate(self, **kwargs):
                return "ok"

            async def aclose(self):
                pass

        # OpenAILikeProvider 在 llm_test 函数内 import，patch 其定义源模块即可
        import roleplay.core.llm.openai_like as openai_like

        monkeypatch.setattr(openai_like, "OpenAILikeProvider", FakeProvider)
        resp = client.post(
            "/api/llm/test",
            json={"provider": "ollama", "model": "qwen2.5:1.5b"},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["ok"] is True
        assert data["provider"] == "ollama"
        assert data["model"] == "qwen2.5:1.5b"

    def test_test_cloud_invalid_key_returns_fail(self, client, monkeypatch):
        class FailingProvider:
            def __init__(self, **kwargs):
                pass

            async def generate(self, **kwargs):
                raise RuntimeError("401 Unauthorized")

            async def aclose(self):
                pass

        import roleplay.core.llm.openai_like as openai_like

        monkeypatch.setattr(openai_like, "OpenAILikeProvider", FailingProvider)
        resp = client.post(
            "/api/llm/test",
            json={
                "provider": "deepseek",
                "model": "deepseek-chat",
                "base_url": "https://api.deepseek.com/v1",
                "api_key": "sk-invalid",
            },
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["ok"] is False
        assert data["detail"]  # 有失败原因


class TestChatRequestLLMOverride:
    def test_llm_override_embedded_in_chat_request(self, client):
        # llm 覆盖字段随聊天请求发送：后端应能解析（此处 mock provider，不真连网）
        resp = client.post(
            "/chat",
            json={
                "session_id": "test-llm-override",
                "message": "你好",
                "llm": {"provider": "ollama", "model": "qwen2.5:1.5b"},
            },
        )
        assert resp.status_code == 200
        data = resp.json()
        assert "reply" in data

    def test_llm_override_rejects_bad_provider(self, client):
        resp = client.post(
            "/chat",
            json={
                "session_id": "test-llm-override-bad",
                "message": "你好",
                "llm": {"provider": "bad", "model": "x"},
            },
        )
        assert resp.status_code == 422

    def test_llm_override_max_length(self):
        from roleplay.models.chat import LLMOverride

        with pytest.raises(Exception):
            LLMOverride(provider="o" * 40)  # max_length=32
        with pytest.raises(Exception):
            LLMOverride(model="m" * 200)  # max_length=128

    def test_llm_override_all_none_ok(self):
        from roleplay.models.chat import LLMOverride

        o = LLMOverride()
        assert o.provider is None and o.model is None and o.api_key is None
