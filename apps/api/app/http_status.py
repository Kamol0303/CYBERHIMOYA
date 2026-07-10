from __future__ import annotations

from fastapi import status

# Prefer the non-deprecated Starlette constant when available.
if hasattr(status, "HTTP_422_UNPROCESSABLE_CONTENT"):
    UNPROCESSABLE = status.HTTP_422_UNPROCESSABLE_CONTENT
else:
    UNPROCESSABLE = 422
