"""轻量级请求频率限制（内存滑动窗口）。

- 按客户端 IP 计数，窗口 60s；超过阈值返回 429。
- 单进程内存实现，足够本地/小流量场景；分布式需换 Redis。
- rate_limit_per_minute <= 0 时关闭（便于测试或受前置网关保护时）。

并发与内存安全：
- 全局 _rate_buckets 由 asyncio.Lock 保护，避免高并发下计数竞争。
- 每次检查时清理过期（窗口外）时间戳；若某 IP 桶在窗口内已无记录则直接删除该桶，
  防止长期运行下的字典内存泄漏。
"""
import asyncio
import time
from collections import defaultdict, deque

from fastapi import Depends, HTTPException, Request

from ..config import Settings, get_settings

_rate_buckets: dict[str, deque[float]] = defaultdict(deque)
_rate_lock = asyncio.Lock()


async def rate_limit(
    request: Request,
    settings: Settings = Depends(get_settings),
) -> None:
    if settings.rate_limit_per_minute <= 0:
        return
    client_ip = request.client.host if request.client else "anonymous"
    now = time.time()
    window_start = now - 60.0
    async with _rate_lock:
        bucket = _rate_buckets[client_ip]
        while bucket and bucket[0] <= window_start:
            bucket.popleft()
        # 窗口内已无记录：移除空桶（避免内存泄漏），并放行+记录本次请求
        if not bucket:
            _rate_buckets.pop(client_ip, None)
            _rate_buckets[client_ip].append(now)
            return
        if len(bucket) >= settings.rate_limit_per_minute:
            retry = int(max(0.0, bucket[0] + 60.0 - now)) + 1
            raise HTTPException(
                status_code=429,
                detail="请求过于频繁，请稍后再试",
                headers={"Retry-After": str(retry)},
            )
        bucket.append(now)
        # 被动清理：桶过多时（如多客户端/代理后），移除最旧记录已超出窗口的空桶，
        # 防止长期运行下字典无限增长。单客户端场景几乎不触发。
        if len(_rate_buckets) > 256:
            for ip in [ip for ip, dq in _rate_buckets.items() if not dq or dq[0] <= window_start]:
                _rate_buckets.pop(ip, None)
