from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any
from uuid import UUID

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt

from app.config import settings
from app.services.store import UserRow, store

ALGORITHM = "HS256"
bearer = HTTPBearer(auto_error=False)


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def create_access_token(user_id: UUID, role: str) -> str:
    payload = {
        "sub": str(user_id),
        "role": role,
        "typ": "access",
        "exp": _utcnow() + timedelta(seconds=settings.access_token_ttl_seconds),
    }
    return jwt.encode(payload, settings.secret_key, algorithm=ALGORITHM)


def create_refresh_token(user_id: UUID) -> str:
    token = jwt.encode(
        {
            "sub": str(user_id),
            "typ": "refresh",
            "exp": _utcnow() + timedelta(seconds=settings.refresh_token_ttl_seconds),
        },
        settings.secret_key,
        algorithm=ALGORITHM,
    )
    store.refresh_tokens[token] = user_id
    return token


def decode_token(token: str) -> dict[str, Any]:
    try:
        return jwt.decode(token, settings.secret_key, algorithms=[ALGORITHM])
    except JWTError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        ) from exc


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer),
) -> UserRow:
    if credentials is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Auth required")
    payload = decode_token(credentials.credentials)
    if payload.get("typ") != "access":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Access token required")
    user = store.get_user(UUID(payload["sub"]))
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return user


def get_optional_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer),
) -> UserRow | None:
    if credentials is None:
        return None
    try:
        return get_current_user(credentials)
    except HTTPException:
        return None
