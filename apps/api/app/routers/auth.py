from __future__ import annotations

from fastapi import APIRouter, HTTPException, status

from app.config import settings
from app.models.schemas import LoginRequest, MeStatsResponse, RegisterRequest, TokenResponse, UserProfile
from app.services.auth import create_access_token, create_refresh_token, get_current_user
from app.services.store import store
from fastapi import Depends

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
def register(body: RegisterRequest) -> TokenResponse:
    try:
        user = store.create_user(body.email, body.password, body.locale)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")
    return TokenResponse(
        access_token=create_access_token(user.id, user.role),
        refresh_token=create_refresh_token(user.id),
        expires_in=settings.access_token_ttl_seconds,
    )


@router.post("/token", response_model=TokenResponse)
def token(body: LoginRequest) -> TokenResponse:
    user = store.authenticate(body.email, body.password)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    store.audit(user.id, "auth.login", {})
    return TokenResponse(
        access_token=create_access_token(user.id, user.role),
        refresh_token=create_refresh_token(user.id),
        expires_in=settings.access_token_ttl_seconds,
    )


@router.post("/revoke", status_code=status.HTTP_204_NO_CONTENT)
def revoke(refresh_token: str) -> None:
    store.refresh_tokens.pop(refresh_token, None)


me_router = APIRouter(tags=["me"])


@me_router.get("/me", response_model=UserProfile)
def me(user=Depends(get_current_user)) -> UserProfile:
    return UserProfile(
        id=user.id,
        email=user.email,
        role=user.role,
        locale=user.locale,
        created_at=user.created_at,
    )


@me_router.get("/me/stats", response_model=MeStatsResponse)
def me_stats(user=Depends(get_current_user)) -> MeStatsResponse:
    return MeStatsResponse(
        scans=len(store.list_scans(user_id=user.id, limit=10_000)),
        threat_events=len(store.list_threat_events(user.id, limit=10_000)),
        unread_notifications=len(
            store.list_notifications(user.id, unread_only=True, limit=10_000)
        ),
        domain_allowlist=len(store.list_domain_allowlist(user.id)),
        risk_history=len(store.list_risk_score_history(user.id, limit=10_000)),
        devices=len(store.list_devices(user.id)),
    )


@me_router.delete("/me", status_code=status.HTTP_202_ACCEPTED)
def erase_me(user=Depends(get_current_user)) -> dict:
    store.request_erasure(user.id)
    return {"status": "erasure_queued", "detail": "Account marked for erasure (V1 foundation)."}
