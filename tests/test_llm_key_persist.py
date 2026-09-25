"""LLM api_key 持久化补丁回归测试（2026-09-19）。

背景：`/api/llm/switch` 原先只把 provider/model/base_url 写进 .env，api_key **不落盘**。
于是进程重启后 `build_llm` 只能读 .env 里的旧 key，Web 之外的入口
（QQ 渠道走全局实例，没有请求级 override）会带着过期凭据打端点 → 401。

补丁：switch 时一并把 api_key 落盘到本机 .env。约定：

- api_key 非空 → 写入 .env；
- api_key 为空 → **保持 .env 原值不动**（不能把手写的 key 清空）；
- .env 不存在 → 返回 (False, detail)，由调用方提示，不抛异常；
- 全程零网络：只做文件读写，不调用任何模型接口（测试里也不消耗任何额度）。
"""
import pytest
from fastapi.testclient import TestClient

from roleplay.api.llm_config import _persist_llm_env
from roleplay.config import get_settings
from roleplay.core.llm.factory import _GLOBAL_LLM_CACHE, reset_global_llm
from roleplay.main import app

FAKE_KEY = "test-key-not-a-real-credential"


@pytest.fixture
def tmp_env(tmp_path, monkeypatch):
    """把 cwd 切到临时目录，Path('.env') 即指向临时 .env，绝不碰真实配置。"""
    monkeypatch.chdir(tmp_path)
    # 本文件的断言对象是 .env 文件本身，而 pydantic-settings 里**环境变量优先级高于 .env**：
    # 外层 shell / CI 若注入了同名 ROLEPLAY_LLM_*，会把 .env 的值整个盖掉，
    # 断言就变成在测环境变量而不是测持久化。先摘掉这些变量，让 .env 成为唯一来源。
    for k in ("ROLEPLAY_LLM_PROVIDER", "ROLEPLAY_LLM_MODEL",
              "ROLEPLAY_LLM_API_KEY", "ROLEPLAY_LLM_BASE_URL"):
        monkeypatch.delenv(k, raising=False)
    env_file = tmp_path / ".env"
    env_file.write_text(
        "ROLEPLAY_APP_NAME=RoleplayAI\n"
        "ROLEPLAY_LLM_PROVIDER=deepseek\n"
        "ROLEPLAY_LLM_MODEL=deepseek-chat\n"
        "ROLEPLAY_LLM_API_KEY=stale-placeholder\n"
        "ROLEPLAY_LLM_BASE_URL=https://api.deepseek.com/v1\n"
        "# 注释行应原样保留\n",
        encoding="utf-8",
    )
    return tmp_path


@pytest.fixture(autouse=True)
def _clean_caches():
    """settings 与全局 LLM 缓存都会读 .env，测试前后清掉避免互相污染。"""
    reset_global_llm()
    get_settings.cache_clear()
    yield
    reset_global_llm()
    get_settings.cache_clear()


def _read_env(root) -> dict:
    out = {}
    for line in (root / ".env").read_text(encoding="utf-8").splitlines():
        s = line.strip()
        if not s or s.startswith("#"):
            continue
        k, _, v = s.partition("=")
        out[k.strip()] = v.strip()
    return out


# ───────────────────────── _persist_llm_env 单元契约 ─────────────────────────
def test_persist_writes_api_key_when_provided(tmp_env):
    ok, detail = _persist_llm_env("openai", "gpt-4o", "https://api.openai.com/v1", FAKE_KEY)
    assert ok is True, detail
    env = _read_env(tmp_env)
    assert env["ROLEPLAY_LLM_PROVIDER"] == "openai"
    assert env["ROLEPLAY_LLM_MODEL"] == "gpt-4o"
    assert env["ROLEPLAY_LLM_BASE_URL"] == "https://api.openai.com/v1"
    # 核心：key 确实落盘了（这就是「重启后不再 401」的依据）
    assert env["ROLEPLAY_LLM_API_KEY"] == FAKE_KEY
    # 注释与无关项不被破坏
    assert "注释行应原样保留" in (tmp_env / ".env").read_text(encoding="utf-8")


def test_persist_keeps_existing_key_when_key_empty(tmp_env):
    """传空 key → 保持 .env 原值，不清空（避免把手写凭据误删）。"""
    ok, _ = _persist_llm_env("openai", "gpt-4o", "https://api.openai.com/v1", "")
    assert ok is True
    assert _read_env(tmp_env)["ROLEPLAY_LLM_API_KEY"] == "stale-placeholder"


def test_persist_blank_key_replaces_stale_value(tmp_env):
    """真实场景：.env 里是过期占位 key，前端传入正确 key → 必须被覆盖。"""
    assert _read_env(tmp_env)["ROLEPLAY_LLM_API_KEY"] == "stale-placeholder"
    ok, _ = _persist_llm_env("openai", "cn:deepseek-v4.1-flash",
                             "http://127.0.0.1:7863/v1", FAKE_KEY)
    assert ok is True
    assert _read_env(tmp_env)["ROLEPLAY_LLM_API_KEY"] == FAKE_KEY


def test_persist_without_env_file_reports_failure(tmp_path, monkeypatch):
    """无 .env（纯环境变量注入模式）→ 返回 False + 说明，不抛异常。"""
    monkeypatch.chdir(tmp_path)
    ok, detail = _persist_llm_env("openai", "gpt-4o", "https://api.openai.com/v1")
    assert ok is False
    assert ".env" in detail


# ───────────────────────── /switch 端到端（仍零网络） ─────────────────────────
def test_switch_persists_api_key_end_to_end(tmp_env):
    """POST /api/llm/switch 带 key → .env 落盘，且下一次 get_settings 读得到。

    用 ollama + localhost 端点，构造 provider 只创建 httpx 客户端、不发请求。
    """
    with TestClient(app) as client:
        resp = client.post("/api/llm/switch", json={
            "provider": "ollama",
            "model": "qwen2.5:1.5b",
            "base_url": "http://localhost:11434/v1",
            "api_key": FAKE_KEY,
        })
    assert resp.status_code == 200
    assert resp.json()["ok"] is True

    env = _read_env(tmp_env)
    assert env["ROLEPLAY_LLM_PROVIDER"] == "ollama"
    assert env["ROLEPLAY_LLM_API_KEY"] == FAKE_KEY

    # 模拟「重启」：清缓存后从 .env 重新加载，key 仍在 → 全局实例不再裸奔
    get_settings.cache_clear()
    assert get_settings().llm_api_key == FAKE_KEY


def test_config_response_still_never_returns_key(tmp_env):
    """补丁不得破坏脱敏契约：/api/llm/config 仍然只给 has_api_key 布尔。"""
    with TestClient(app) as client:
        data = client.get("/api/llm/config").json()
    assert "api_key" not in data
    assert isinstance(data["has_api_key"], bool)
