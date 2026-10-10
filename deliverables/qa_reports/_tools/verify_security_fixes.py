"""独立复验安全修复（S1 SSRF / S2a headers / S2b 脱敏 / S3 token）。

不采信代理自述，全部亲自实测。重点包含「防误伤」验证：
本地 Ollama 必须仍可用，否则修复就是错的。
只读（临时数据目录）。
"""
import asyncio
import os
import sys
import tempfile
from pathlib import Path

_t = Path(tempfile.mkdtemp(prefix="secfix_"))
for k, v in dict(
    ROLEPLAY_LLM_PROVIDER="mock",
    ROLEPLAY_RAG_IMPL="memory",
    ROLEPLAY_EMBEDDER="hashing",
    ROLEPLAY_ENABLE_WEB="false",
    ROLEPLAY_EMOTION_DETECTOR="keyword",
).items():
    os.environ[k] = v
os.environ["ROLEPLAY_KNOWLEDGE_DIR"] = str(_t / "k")
os.environ["ROLEPLAY_CHARACTERS_DIR"] = str(_t / "c")
os.environ["ROLEPLAY_SESSION_MEMORY_DIR"] = str(_t / "s")

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "src"))

FAILS = []


def check(label, ok, detail=""):
    print("   [%s] %s%s" % ("PASS" if ok else "FAIL", label, ("  <- " + detail) if detail else ""))
    if not ok:
        FAILS.append(label)


# ─────────────────────────── S1: SSRF 拦截 + 防误伤 ───────────────────────────
print("=" * 74)
print("S1) /chat 路径（factory）的 base_url 校验")

from roleplay.core.llm.factory import build_llm_from_config  # noqa: E402
from roleplay.models.chat import LLMOverride  # noqa: E402

MUST_BLOCK = [
    "http://169.254.169.254/latest/meta-data",
    "http://169.254.1.1/",
    "http://100.64.0.1/v1",
    "file:///c:/windows/win.ini",
    "gopher://x/",
    "ftp://x/",
    "https://evil.example.com/v1",
    "http://8.8.8.8/v1",
]
MUST_ALLOW = [
    "http://127.0.0.1:11434/v1",     # 本地 Ollama（防误伤，最重要）
    "http://127.0.0.1:11434",
    "http://localhost:11434/v1",
    "http://192.168.1.50:11434/v1",  # 内网 Ollama
    "http://10.0.0.5:8000/v1",
    "http://172.16.5.5:8000/v1",
    "https://api.deepseek.com/v1",   # 云端白名单
]

print("   应拦截：")
for t in MUST_BLOCK:
    try:
        build_llm_from_config(None, LLMOverride(provider="ollama", model="m",
                                                base_url=t, api_key="k"))
        check("block %s" % t, False, "竟然被接受")
    except Exception as e:  # noqa: BLE001
        check("block %s" % t, True, type(e).__name__)

print("   应放行（防误伤）：")
for t in MUST_ALLOW:
    try:
        build_llm_from_config(None, LLMOverride(provider="ollama", model="m",
                                                base_url=t, api_key="k"))
        check("allow %s" % t, True)
    except Exception as e:  # noqa: BLE001
        check("allow %s" % t, False, "%s: %s" % (type(e).__name__, str(e)[:90]))

# ─────────────────────── S1 端到端：/chat 带恶意 base_url ───────────────────────
print()
print("S1-端到端) POST /chat 携带恶意 llm.base_url")
from fastapi.testclient import TestClient  # noqa: E402

from roleplay.main import app  # noqa: E402

with TestClient(app) as c:
    r = c.post("/chat", json={
        "session_id": "ssrf", "message": "你好",
        "llm": {"provider": "openai", "model": "x",
                "base_url": "http://169.254.169.254/latest/meta-data", "api_key": "k"},
    })
    check("恶意 base_url 被拒（4xx）", r.status_code >= 400,
          "status=%s body=%s" % (r.status_code, r.text[:110].replace("\n", " ")))
    # 合法本地 ollama 仍可用
    r2 = c.post("/chat", json={
        "session_id": "ok", "message": "你好",
        "llm": {"provider": "ollama", "model": "qwen2.5:1.5b",
                "base_url": "http://127.0.0.1:11434/v1"},
    })
    check("合法本地 ollama 仍可用（不 5xx 崩溃）", r2.status_code < 500,
          "status=%s" % r2.status_code)

# ────────────────────────── S2a: Retry-After 透传 ──────────────────────────
print()
print("S2a) HTTPException headers 透传（Retry-After）")
# 在**独立 app** 上注册真实处理器并挂一条抛 429 的路由。
# （不能往 roleplay.main:app 追加路由：frontend 的 StaticFiles 挂在 "/"，
#   后加的路由会被它抢先匹配成 404。）
from fastapi import FastAPI, HTTPException  # noqa: E402

from roleplay.errors.handlers import register_exception_handlers  # noqa: E402

_probe_app = FastAPI()
register_exception_handlers(_probe_app)


@_probe_app.get("/probe")
async def _probe_429():
    raise HTTPException(status_code=429, detail="too many",
                        headers={"Retry-After": "42"})


with TestClient(_probe_app) as c:
    resp = c.get("/probe")
ra = resp.headers.get("retry-after")
check("429 保留 Retry-After", ra == "42",
      "status=%s retry-after=%r" % (resp.status_code, ra))

# 反向对照：确认该断言真的能失败（去掉 headers 时应拿不到）
_probe_app2 = FastAPI()
register_exception_handlers(_probe_app2)


@_probe_app2.get("/probe")
async def _probe_429_nohdr():
    raise HTTPException(status_code=429, detail="too many")  # 不带 headers


with TestClient(_probe_app2) as c:
    r2 = c.get("/probe")
check("对照：无 headers 时确无 Retry-After（断言非恒真）",
      r2.headers.get("retry-after") is None,
      "retry-after=%r" % r2.headers.get("retry-after"))

# ────────────────────────── S2b: 深层嵌套脱敏 ──────────────────────────
print()
print("S2b) _sanitize 深层嵌套 api_key 是否仍脱敏")
from roleplay.errors.handlers import _sanitize  # noqa: E402

deep = {"api_key": "SECRET_TOP"}
cur = deep
for _ in range(18):
    cur["nested"] = {"api_key": "SECRET_DEEP"}
    cur = cur["nested"]
out = str(_sanitize(deep))
check("深层 api_key 不穿透", "SECRET_DEEP" not in out and "SECRET_TOP" not in out,
      "输出含 SECRET=%s" % ("SECRET" in out))

# ────────────────────────── S3: token 脱敏 ──────────────────────────
print()
print("S3) QQ 重连日志 token 脱敏")
from roleplay.channels.qq_onebot import _redact_url  # noqa: E402

TOKEN = "SUPER_SECRET_TOKEN_123"
txt = "连接失败 ws://127.0.0.1:3001?access_token=%s end" % TOKEN
red = _redact_url(txt, TOKEN)
check("token 被脱敏", TOKEN not in red, "结果=%s" % red[:90])

# 空 token 时：**不应**发生 replace("","***") 灾难替换（每个字符间插 ***），
# 但 access_token= 的正则兜底**仍应生效**（纵深防御，即使拿不到 token 也能打码）。
plain = "这是一段普通日志，没有凭据"
check("空 token 不做灾难性替换（普通文本保持原样）",
      _redact_url(plain, "") == plain, "结果=%r" % _redact_url(plain, "")[:60])
fallback = _redact_url("ws://x/?access_token=real_secret", "")
check("空 token 时 access_token 正则兜底仍打码",
      "real_secret" not in fallback, "结果=%s" % fallback)

print()
print("=" * 74)
print("汇总：%s" % ("全部通过 [OK]" if not FAILS else "失败项 %s [FAIL]" % FAILS))
