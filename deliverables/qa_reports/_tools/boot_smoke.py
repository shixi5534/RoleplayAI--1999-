"""应用启动冒烟（离线 mock 配置）：import app -> 列出路由 -> TestClient 打关键端点。

只读：不改任何数据（数据目录已重定向到临时目录）。
"""
import os
import tempfile
from pathlib import Path

_TMP = Path(tempfile.mkdtemp(prefix="smoke_boot_"))
os.environ["ROLEPLAY_LLM_PROVIDER"] = "mock"
os.environ["ROLEPLAY_RAG_IMPL"] = "memory"
os.environ["ROLEPLAY_EMBEDDER"] = "hashing"
os.environ["ROLEPLAY_ENABLE_WEB"] = "false"
os.environ["ROLEPLAY_EMOTION_DETECTOR"] = "keyword"
os.environ["ROLEPLAY_KNOWLEDGE_DIR"] = str(_TMP / "k")
os.environ["ROLEPLAY_CHARACTERS_DIR"] = str(_TMP / "c")
os.environ["ROLEPLAY_SESSION_MEMORY_DIR"] = str(_TMP / "s")

import sys
ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "src"))

from fastapi.testclient import TestClient  # noqa: E402

from roleplay.main import app  # noqa: E402

print("=== ROUTES ===")
routes = []
for r in app.routes:
    m = getattr(r, "methods", None)
    if m:
        routes.append((sorted(m - {"HEAD", "OPTIONS"}), r.path))
for m, p in sorted(routes, key=lambda x: x[1]):
    print("  %-22s %s" % (",".join(m) if m else "-", p))
print("total_routes=%d" % len(routes))

print()
print("=== ENDPOINT SMOKE ===")
PROBES = [
    ("GET", "/"),
    ("GET", "/api/characters"),
    ("GET", "/api/llm/config"),
    ("GET", "/api/llm/ollama/models"),
    ("GET", "/api/sessions"),
    ("GET", "/docs"),
    ("GET", "/openapi.json"),
    ("GET", "/__nonexistent__"),
]
with TestClient(app) as c:
    for method, path in PROBES:
        try:
            resp = c.get(path, timeout=30)
            body = resp.text[:120].replace("\n", " ")
            print("  %-40s -> %s  len=%d  %s" % (path, resp.status_code, len(resp.content), body))
        except Exception as e:  # noqa: BLE001
            print("  %-40s -> EXC %s: %s" % (path, type(e).__name__, str(e)[:150]))

    print()
    print("=== CHAT SSE SMOKE (mock provider) ===")
    try:
        with c.stream("POST", "/api/chat", json={"message": "你好，我今天有点难过",
                                                 "session_id": "smoke"}, timeout=60) as r:
            print("  status=%s content-type=%s" % (r.status_code, r.headers.get("content-type")))
            chunks = []
            for i, line in enumerate(r.iter_lines()):
                chunks.append(line)
                if i >= 40:
                    break
            text = "\n".join([x for x in chunks if isinstance(x, str)])
            print("  first_lines=%d bytes=%d" % (len(chunks), len(text)))
            print("  preview: %s" % text[:400].replace("\n", " | "))
    except Exception as e:  # noqa: BLE001
        print("  CHAT EXC %s: %s" % (type(e).__name__, str(e)[:300]))

print()
print("=== OpenAPI schema validity ===")
try:
    schema = app.openapi()
    print("  title=%s paths=%d" % (schema.get("info", {}).get("title"), len(schema.get("paths", {}))))
    bad = []
    for p, ops in schema.get("paths", {}).items():
        for op_name, op in ops.items():
            if op_name not in ("get", "post", "put", "delete", "patch"):
                continue
            for code, resp in op.get("responses", {}).items():
                if "$ref" not in str(resp) and "content" not in resp and "description" not in resp:
                    bad.append((p, op_name, code))
    print("  malformed_responses=%d" % len(bad))
    for b in bad[:10]:
        print("   ", b)
except Exception as e:  # noqa: BLE001
    print("  SCHEMA EXC %s: %s" % (type(e).__name__, str(e)[:300]))
