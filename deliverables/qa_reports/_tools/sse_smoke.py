"""SSE 聊天流冒烟：找到正确的请求体 schema 并打通一次真实流式回复。"""
import json
import os
import sys
import tempfile
from pathlib import Path

t = Path(tempfile.mkdtemp(prefix="smoke_sse_"))
for k, v in dict(
    ROLEPLAY_LLM_PROVIDER="mock",
    ROLEPLAY_RAG_IMPL="memory",
    ROLEPLAY_EMBEDDER="hashing",
    ROLEPLAY_ENABLE_WEB="false",
    ROLEPLAY_EMOTION_DETECTOR="keyword",
).items():
    os.environ[k] = v
os.environ["ROLEPLAY_KNOWLEDGE_DIR"] = str(t / "k")
os.environ["ROLEPLAY_CHARACTERS_DIR"] = str(t / "c")
os.environ["ROLEPLAY_SESSION_MEMORY_DIR"] = str(t / "s")

sys.path.insert(0, str(Path(".").resolve() / "src"))

from fastapi.testclient import TestClient  # noqa: E402

from roleplay.main import app  # noqa: E402

with TestClient(app) as c:
    s = c.get("/openapi.json").json()
    op = s["paths"]["/chat/stream"]["post"]
    body = op.get("requestBody", {}).get("content", {})
    print("requestBody content types:", list(body.keys()))
    schema = list(body.values())[0].get("schema", {}) if body else {}
    ref = schema.get("$ref", "")
    print("ref:", ref)
    if ref:
        name = ref.split("/")[-1]
        props = s["components"]["schemas"][name]
        print("required:", props.get("required"))
        print("properties:", list(props.get("properties", {}).keys()))

    fields = list(props.get("properties", {}).keys()) if ref else []
    if not fields:
        fields = ["message"]

    print()
    print("=== probing /chat/stream ===")
    for f in fields:
        payload = {f: "你好，我今天有点难过"}
        try:
            r = c.request("POST", "/chat/stream", json=payload, timeout=60)
        except Exception as e:  # noqa: BLE001
            print("  field=%-16s EXC %s: %s" % (f, type(e).__name__, str(e)[:200]))
            continue
        if r.status_code == 200:
            print("  WINNER field=%s -> 200 bytes=%d ct=%s"
                  % (f, len(r.content), r.headers.get("content-type")))
            for line in r.text.splitlines()[:12]:
                print("     ", line[:200])
            break
        print("  field=%-16s -> %s %s" % (f, r.status_code, r.text[:130].replace("\n", " ")))

    print()
    print("=== probing /chat (non-stream) ===")
    for f in fields:
        payload = {f: "你好"}
        r = c.request("POST", "/chat", json=payload, timeout=60)
        if r.status_code == 200:
            print("  WINNER field=%s -> 200" % f)
            print("  body: %s" % r.text[:400])
            break
        print("  field=%-16s -> %s %s" % (f, r.status_code, r.text[:130].replace("\n", " ")))
