"""延迟退化定位：同一会话连续请求 vs 每次新会话，观察耗时随轮次的变化。

目标：验证「同一 session_id 连续 /chat/stream 越来越慢」这一现象，并定位与
历史长度、画像提取节奏（ROLEPLAY_PROFILE_EXTRACT_EVERY）、Web 搜索初始化之间的关系。
只发请求，不写项目数据。
"""
import statistics
import sys
import time

import httpx

BASE = sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:8123"


def run_series(c, label, sid_factory, n=12):
    print("\n[%s] n=%d" % (label, n))
    rows = []
    for i in range(n):
        sid = sid_factory(i)
        t0 = time.time()
        try:
            r = c.post("/chat/stream", json={"session_id": sid, "message": "第%d轮 你好" % i})
            dt = time.time() - t0
            rows.append((i, r.status_code, dt, len(r.content)))
            print("   #%02d %s %7.2fs bytes=%5d" % (i, r.status_code, dt, len(r.content)))
        except Exception as e:  # noqa: BLE001
            dt = time.time() - t0
            rows.append((i, "EXC", dt, 0))
            print("   #%02d EXC %s %7.2fs" % (i, type(e).__name__, dt))
    good = [r[2] for r in rows if r[1] == 200]
    if good:
        print("   -> min=%.2f p50=%.2f max=%.2f  first=%.2f last=%.2f  growth=%.1fx"
              % (min(good), statistics.median(good), max(good), good[0], good[-1],
                 (good[-1] / good[0]) if good[0] > 0 else 0))
    return rows


with httpx.Client(base_url=BASE, timeout=300) as c:
    print("[health]", c.get("/health").status_code)

    # A: 每轮新会话（隔离历史增长因素）
    run_series(c, "A 每轮新会话", lambda i: "sessA-%d" % i, n=12)

    # B: 同一会话连续（复现退化）
    run_series(c, "B 同一会话连续", lambda i: "sessB", n=12)

    # C: 同一会话，但先制造更多历史，看是否与历史长度相关
    print("\n[C 同一会话已有 20 轮历史后再打 6 次]")
    for i in range(20):
        c.post("/chat/stream", json={"session_id": "sessC", "message": "铺垫 %d" % i})
    run_series(c, "C 长历史会话", lambda i: "sessC", n=6)

    # D: 观察历史长度
    print("\n[历史长度]")
    for sid in ("sessA-0", "sessB", "sessC"):
        r = c.get("/api/sessions/%s/history" % sid)
        if r.status_code == 200:
            h = r.json().get("history", [])
            print("   %-8s turns=%d chars=%d" % (sid, len(h), sum(len(m.get("content", "")) for m in h)))

    # E: 非流式端点是否同样退化
    run_series(c, "E 非流式 /chat 同会话", lambda i: "sessE", n=8)
