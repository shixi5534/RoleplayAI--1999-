"""API 层测试（TestClient，离线 mock）。"""
import json


def test_health(client):
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_chat_sync(client):
    r = client.post("/chat", json={"session_id": "s", "message": "我好开心"})
    assert r.status_code == 200
    body = r.json()
    assert body["reply"]
    assert body["emotion"]["emotion"] == "happy"


def test_chat_stream_emits_events(client):
    # 注："害怕"属于 anxious 词表；触发 fear 需用恐惧类词（如"恐怖/恐惧"）
    msg = "这地方好恐怖，我很恐惧"
    r = client.post("/chat/stream", json={"session_id": "stream-fresh", "message": msg})
    assert r.status_code == 200
    text = r.text
    assert "event: emotion" in text
    assert "event: chunk" in text
    assert "event: done" in text

    # 解析全部事件，验证顺序与增量流式
    events: list[tuple[str, str]] = []
    for block in text.split("\n\n"):
        if not block.strip():
            continue
        lines = block.split("\n")
        ev = next((l[6:].strip() for l in lines if l.startswith("event:")), None)
        data = next((l[5:].strip() for l in lines if l.startswith("data:")), None)
        events.append((ev, data))
    types = [t for t, _ in events]
    assert types[0] == "emotion", "情感事件应先于文本分片"
    assert types[-1] == "done", "末尾应以 done 结束"
    assert types.count("chunk") >= 2, "真流式应产出多个分片（而非整段一次性下发）"

    # 重组 chunk 文本须与「同消息在全新会话下的同步回复」逐字一致（验证逐片无损）
    chunks = [json.loads(d) for t, d in events if t == "chunk"]
    joined = "".join(chunks)
    sync = client.post(
        "/chat", json={"session_id": "sync-fresh-other", "message": msg}
    ).json()
    assert joined == sync["reply"], "流式重组文本应与同步回复一致"

    # emotion 载荷与映射一致
    emo = json.loads(next(d for t, d in events if t == "emotion"))
    assert emo["emotion"] == "fear"


def test_chat_validation_error(client):
    # message 为空应触发 422（统一异常处理）
    r = client.post("/chat", json={"session_id": "s", "message": ""})
    assert r.status_code == 422
    assert r.json()["error"]["code"] == "validation_error"


def test_security_headers_present(client):
    r = client.get("/health")
    assert r.headers.get("X-Content-Type-Options") == "nosniff"
    assert r.headers.get("X-Frame-Options") == "DENY"
    assert "default-src 'self'" in r.headers.get("Content-Security-Policy", "")


def test_cors_wildcard_no_credentials(client):
    # 默认 cors_origins='*'：通配源可访问，但绝不可带凭据（规范非法组合）。
    r = client.get("/health", headers={"Origin": "http://evil.example.com"})
    assert r.headers.get("access-control-allow-origin") == "*"
    assert (r.headers.get("access-control-allow-credentials") or "false") != "true"


def test_web_ingest_disabled_by_default(client):
    # 默认 enable_url_ingest=False → 联网导入应被拒（403）
    r = client.post("/api/knowledge/web-ingest", json={"query": "测试"})
    assert r.status_code == 403


def test_ingest_url_requires_allowlist(client):
    # 默认 enable_url_ingest=False → URL 导入被全局开关拦截（403），
    # 与 web-ingest 语义一致（kill-switch 优先于白名单校验）。
    r = client.post(
        "/api/knowledge/ingest",
        json={"type": "url", "url": "https://example.com/page"},
    )
    assert r.status_code == 403


def test_ingest_url_enabled_but_empty_allowlist(client):
    # 开关开启但 allowed_ingest_hosts 为空 → 422（白名单校验拒绝），杜绝未授权 SSRF
    from roleplay.api.deps import get_settings_dep
    from roleplay.config import Settings
    client.app.dependency_overrides[get_settings_dep] = lambda req: Settings(
        enable_url_ingest=True, allowed_ingest_hosts=""
    )
    try:
        r = client.post(
            "/api/knowledge/ingest",
            json={"type": "url", "url": "https://example.com/page"},
        )
        assert r.status_code == 422
    finally:
        client.app.dependency_overrides.clear()


def test_whitespace_only_message_rejected(client):
    # 纯空白消息应被 field_validator 拦截为 422
    r = client.post("/chat", json={"session_id": "s", "message": "   "})
    assert r.status_code == 422
    assert r.json()["error"]["code"] == "validation_error"


def test_rate_limit_triggers(client):
    # 将限流降到 1/min 并清空计数桶，验证第二次请求被 429
    from roleplay.api.ratelimit import _rate_buckets
    from roleplay.config import Settings, get_settings

    _rate_buckets.clear()
    low = Settings(rate_limit_per_minute=1)
    client.app.dependency_overrides[get_settings] = lambda: low
    try:
        r1 = client.post("/chat", json={"session_id": "s", "message": "你好"})
        r2 = client.post("/chat", json={"session_id": "s", "message": "在吗"})
        assert r1.status_code == 200
        assert r2.status_code == 429
    finally:
        client.app.dependency_overrides.clear()


def test_stream_emotion_score_capped(client):
    # SSE emotion 事件的情绪分数应 <= 1.0（多关键词命中封顶）
    r = client.post("/chat/stream", json={"session_id": "s", "message": "我好难过好难过好难过"})
    assert r.status_code == 200
    for block in r.text.split("\n\n"):
        if block.startswith("event: emotion"):
            data_line = [l for l in block.split("\n") if l.startswith("data:")][0]
            import json

            payload = json.loads(data_line[5:].strip())
            assert 0.0 <= payload["score"] <= 1.0


def test_stream_emotion_contract_no_source_leak(client):
    # SSE 契约回归（ADR-6）：emotion 事件体仍只含 {emotion, score}，
    # 新增的 source 字段绝不进入协议体（仅日志/内部使用）。
    r = client.post("/chat/stream", json={"session_id": "s", "message": "我爱你"})
    assert r.status_code == 200
    for block in r.text.split("\n\n"):
        if block.startswith("event: emotion"):
            data_line = [l for l in block.split("\n") if l.startswith("data:")][0]
            import json

            payload = json.loads(data_line[5:].strip())
            assert set(payload.keys()) == {"emotion", "score"}
            assert payload["emotion"] == "love"


def test_stream_new_emotion_through_sse(client):
    # 15 类新增情绪（grateful）全链路穿透到 SSE
    r = client.post("/chat/stream", json={"session_id": "s", "message": "太感谢你了"})
    assert r.status_code == 200
    found = False
    for block in r.text.split("\n\n"):
        if block.startswith("event: emotion"):
            data_line = [l for l in block.split("\n") if l.startswith("data:")][0]
            import json

            payload = json.loads(data_line[5:].strip())
            if payload["emotion"] == "grateful":
                found = True
    assert found
