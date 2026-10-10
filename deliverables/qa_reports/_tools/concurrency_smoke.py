"""并发 + 隔离 + 限流冒烟。

- 并发 20 路 /chat/stream，检验是否有串会话（A 的回复跑到 B 的历史里）
- 会话隔离：两个 session 互不可见
- 限流：连续 N 次请求是否触发 429
- 长连接不挂起：每路都必须在超时内返回
只读：数据目录重定向到临时目录。
"""
import concurrent.futures as cf
import os
import sys
import tempfile
import time
from pathlib import Path

t = Path(tempfile.mkdtemp(prefix="smoke_conc_"))
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


def one_call(sid, msg, client):
    t0 = time.time()
    try:
        r = client.request("POST", "/chat/stream", json={"session_id": sid, "message": msg},
                           timeout=120)
        return sid, r.status_code, len(r.content), round(time.time() - t0, 2)
    except Exception as e:  # noqa: BLE001
        return sid, "EXC", "%s:%s" % (type(e).__name__, str(e)[:80]), round(time.time() - t0, 2)


with TestClient(app) as c:
    print("=== 1) 并发 20 路不同会话 ===")
    jobs = [("conc-%02d" % i, "第%d路：你好" % i) for i in range(20)]
    t0 = time.time()
    # TestClient 非线程安全，这里刻意用线程池压力化：只统计，不据此断言线程安全
    results = []
    with cf.ThreadPoolExecutor(max_workers=8) as ex:
        futs = [ex.submit(one_call, sid, msg, c) for sid, msg in jobs]
        for f in cf.as_completed(futs):
            results.append(f.result())
    print("  wall=%.2fs" % (time.time() - t0))
    codes = {}
    for sid, code, size, dur in results:
        codes[code] = codes.get(code, 0) + 1
    print("  status distribution:", codes)
    slow = [r for r in results if isinstance(r[3], float) and r[3] > 20]
    print("  slow(>20s): %d" % len(slow))
    for r in sorted(results, key=lambda x: -x[3] if isinstance(x[3], float) else 0)[:5]:
        print("    slowest:", r)

    print()
    print("=== 2) 会话隔离校验 ===")
    for sid in ("conc-01", "conc-05", "conc-19"):
        r = c.get("/api/sessions/%s/history" % sid, timeout=60)
        if r.status_code == 200:
            d = r.json()
            hist = d.get("history", [])
            users = [m.get("content", "") for m in hist if m.get("role") == "user"]
            print("  %-9s turns=%d user_msgs=%s" % (sid, len(hist), users[:3]))
        else:
            print("  %-9s -> %s" % (sid, r.status_code))

    print()
    print("=== 3) 限流探测（连续 60 次 /health） ===")
    codes2 = {}
    t0 = time.time()
    for i in range(60):
        rr = c.get("/health", timeout=30)
        codes2[rr.status_code] = codes2.get(rr.status_code, 0) + 1
    print("  %.2fs status=%s" % (time.time() - t0, codes2))

    print()
    print("=== 4) 限流探测（连续 40 次 /chat/stream） ===")
    codes3 = {}
    t0 = time.time()
    for i in range(40):
        rr = c.request("POST", "/chat/stream",
                       json={"session_id": "rl", "message": "hi"}, timeout=60)
        codes3[rr.status_code] = codes3.get(rr.status_code, 0) + 1
    print("  %.2fs status=%s" % (time.time() - t0, codes3))
