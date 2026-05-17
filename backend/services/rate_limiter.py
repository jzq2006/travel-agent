"""滑动窗口速率限制器 — 基于内存的实现。

原理：
    每个客户端（按 IP + user_id 标识）维护一个请求时间戳列表。
    每次请求时清理超出窗口的旧记录，检查剩余数量是否超过阈值。

为什么不用 Redis：
    这是单机部署的项目，内存限流足够。如果需要多实例部署，
    只需把 _windows 换成 Redis 的 sorted set，接口不变。
"""

import time
from collections import defaultdict
from threading import Lock

from fastapi import HTTPException


class RateLimiter:
    def __init__(self, max_requests: int = 10, window_seconds: int = 60):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self._windows: dict[str, list[float]] = defaultdict(list)
        self._lock = Lock()

    def check(self, key: str):
        """检查是否超过速率限制，超限则抛出 429。"""
        now = time.time()
        cutoff = now - self.window_seconds

        with self._lock:
            # 清理窗口外的旧记录
            window = self._windows[key]
            self._windows[key] = [t for t in window if t > cutoff]

            if len(self._windows[key]) >= self.max_requests:
                raise HTTPException(
                    status_code=429,
                    detail=f"请求过于频繁，请 {self.window_seconds // 60} 分钟后再试",
                )

            self._windows[key].append(now)

    def check_request(self, request, user=None):
        """从 FastAPI 请求中提取标识并检查限流。"""
        ip = request.client.host if request.client else "unknown"
        uid = user["user_id"] if user else "anonymous"
        self.check(f"{ip}:{uid}")


# ── 预配置的限流器 ──

# Agent 方案生成：每分钟最多 5 次（消耗 token 大）
plan_limiter = RateLimiter(max_requests=5, window_seconds=60)

# Agent 聊天/追问：每分钟最多 15 次（消耗 token 小）
chat_limiter = RateLimiter(max_requests=15, window_seconds=60)
