from __future__ import annotations

import time
from collections import defaultdict
from threading import Lock

from fastapi import HTTPException, Request, status

from app.config import settings


class GuestRateLimiter:
    """Simple in-process guest rate limit for scan endpoints."""

    def __init__(self) -> None:
        self._hits: dict[str, list[float]] = defaultdict(list)
        self._lock = Lock()

    def reset(self) -> None:
        with self._lock:
            self._hits.clear()

    def check(self, key: str, limit: int | None = None, window_seconds: int = 3600) -> dict[str, str]:
        limit = limit if limit is not None else settings.guest_rate_limit_per_hour
        now = time.time()
        with self._lock:
            bucket = [t for t in self._hits[key] if now - t < window_seconds]
            remaining = max(0, limit - len(bucket))
            if len(bucket) >= limit:
                self._hits[key] = bucket
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail="Guest scan quota exceeded. Sign in or try later.",
                    headers={
                        "X-RateLimit-Limit": str(limit),
                        "X-RateLimit-Remaining": "0",
                    },
                )
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
