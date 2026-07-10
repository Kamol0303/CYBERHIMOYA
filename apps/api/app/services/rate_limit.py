from __future__ import annotations

import time
from collections import defaultdict
from threading import Lock

from fastapi import Request

from app.config import settings


class GuestRateLimitExceeded(Exception):
    """Raised when a guest IP exceeds the hourly scan quota."""

    def __init__(self, *, limit: int, instance: str | None = None) -> None:
        self.limit = limit
        self.instance = instance
        super().__init__("Guest scan quota exceeded")


class GuestRateLimiter:
    """Simple in-process guest rate limit for scan endpoints."""

    def __init__(self) -> None:
        self._hits: dict[str, list[float]] = defaultdict(list)
        self._lock = Lock()

    def reset(self) -> None:
        with self._lock:
            self._hits.clear()

    def check(
        self,
        key: str,
        limit: int | None = None,
        window_seconds: int = 3600,
        *,
        instance: str | None = None,
    ) -> dict[str, str]:
        limit = limit if limit is not None else settings.guest_rate_limit_per_hour
        now = time.time()
        with self._lock:
            bucket = [t for t in self._hits[key] if now - t < window_seconds]
            if len(bucket) >= limit:
                self._hits[key] = bucket
                raise GuestRateLimitExceeded(limit=limit, instance=instance)
            bucket.append(now)
            self._hits[key] = bucket
            remaining = max(0, limit - len(bucket))
            return {
                "X-RateLimit-Limit": str(limit),
                "X-RateLimit-Remaining": str(remaining),
            }


guest_limiter = GuestRateLimiter()


def client_key(request: Request) -> str:
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip()
    if request.client:
        return request.client.host
    return "unknown"
