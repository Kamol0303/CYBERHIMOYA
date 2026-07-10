from __future__ import annotations

from fastapi import status

# Starlette renamed 422 constant; keep compatibility across versions.
UNPROCESSABLE = getattr(
    status,
    "HTTP_422_UNPROCESSABLE_CONTENT",
    status.HTTP_422_UNPROCESSABLE_ENTITY,
)
