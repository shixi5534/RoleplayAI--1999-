"""真实服务器并发 / 延迟 / 限流验证（对已运行的 uvicorn 发压）。

用法: python real_server_probe.py http://127.0.0.1:PORT
只读：只发请求，不写项目数据（服务端用临时数据目录启动）。
"""
import json
import statistics
import sys
import time

import httpx

BASE = sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:8123"


def pct(vals, p):
    if not vals:
        return 0
    vals = sorted(vals)
    k = max(0, min(len(vals) - 1, int(round((p / 100.0) * len(vals) + 0.5)) - 1))
    return vals[k]


def main():
    with httpx.Client(base_url=BASE, timeout=180) as c:
        r = c.get("/health")
        print("[health] %s %s" % (r.status_code, r.text[:80]))

        # --- 冷启动单请求延迟 ---
        print("\n[单请求延迟 /chat/stream x8 串行]")
        lat = []
        for i in range(8):
            t0 = time.time()
            rr = c.post("/chat/stream", json={"session_id": "lat-%d" % i, "message": "你好"})
            dt = time.time() - t0
            lat.append(dt)
            print("   #%d %s %.2fs bytes=%d" % (i, rr.status_code, dt, len(rr.content)))
        print("   min=%.2f p50=%.2f max=%.2f" % (min(lat), statistics.median(lat), max(lat)))

        # --- 并发 ---
        for conc in (10, 30):
            print("\n[并发 %d 路 /chat/stream]" % conc)
            lat = []
            codes = {}
            t0 = time.time()
            with httpx.Client(base_url=BASE, timeout=300) as cc:
                reqs = [
                    cc.build_request("POST", "/chat/stream",
                                     json={"session_id": "c%d-%d" % (conc, i),
                                           "message": "第%d路" % i})
                    for i in range(conc)
                ]
                # 用 asyncio 并发
                import asyncio

                async def run():
                    async with httpx.AsyncClient(base_url=BASE, timeout=300) as ac:
                        async def one(i):
                            t = time.time()
                            try:
                                rr = await ac.post("/chat/stream",
                                                   json={"session_id": "c%d-%d" % (conc, i),
                                                         "message": "第%d路" % i})
                                return rr.status_code, time.time() - t, len(rr.content)
                            except Exception as e:  # noqa: BLE001
                                return "EXC:%s" % type(e).__name__, time.time() - t, 0

                        return await asyncio.gather(*[one(i) for i in range(conc)])

                results = asyncio.run(run())
            wall = time.time() - t0
            for code, dt, size in results:
                codes[code] = codes.get(code, 0) + 1
                lat.append(dt)
            print("   wall=%.2fs codes=%s" % (wall, codes))
            print("   min=%.2f p50=%.2f p95=%.2f max=%.2f"
                  % (min(lat), pct(lat, 50), pct(lat, 95), max(lat)))
            slow = [x for x in lat if x > 20]
            print("   >20s: %d / %d" % (len(slow), len(lat)))

        # --- 限流 ---
        print("\n[限流: 连打 /health x80]")
        codes = {}
        t0 = time.time()
        for _ in range(80):
            rr = c.get("/health")
            codes[rr.status_code] = codes.get(rr.status_code, 0) + 1
        print("   %.2fs codes=%s" % (time.time() - t0, codes))

        print("\n[限流: 连打 /chat/stream x50]")
        codes = {}
        t0 = time.time()
        for i in range(50):
            try:
                rr = c.post("/chat/stream", json={"session_id": "rl", "message": "hi"})
                codes[rr.status_code] = codes.get(rr.status_code, 0) + 1
                if rr.status_code == 429:
                    print("   第 %d 次触发限流" % (i + 1))
                    break
            except Exception as e:  # noqa: BLE001
                codes["EXC:%s" % type(e).__name__] = codes.get("EXC:%s" % type(e).__name__, 0) + 1
                break
        print("   %.2fs codes=%s" % (time.time() - t0, codes))

        # --- 会话隔离 ---
        print("\n[会话隔离]")
        for sid in ("c10-0", "c10-5", "c10-9"):
            rr = c.get("/api/sessions/%s/history" % sid)
            if rr.status_code == 200:
                d = rr.json()
                h = d.get("history", [])
                us = [m.get("content", "") for m in h if m.get("role") == "user"]
                print("   %-8s turns=%d users=%s" % (sid, len(h), json.dumps(us, ensure_ascii=False)[:80]))
            else:
                print("   %-8s -> %s" % (sid, rr.status_code))


if __name__ == "__main__":
    main()
