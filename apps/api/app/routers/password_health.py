from __future__ import annotations

from fastapi import APIRouter
from pydantic import BaseModel, Field

from app.services.password_health import assess_password

router = APIRouter(tags=["password-health"])


class PasswordHealthRequest(BaseModel):
    password: str = Field(min_length=1, max_length=256)


class PasswordHealthResponse(BaseModel):
    score: int
    verdict: str
    reasons: list[dict[str, str]]
    recommendations: list[str]
    defensive_only: bool = True


@router.post("/password-health", response_model=PasswordHealthResponse)
def password_health(body: PasswordHealthRequest) -> PasswordHealthResponse:
    """Assess password strength. Password is never stored or audited."""
    result = assess_password(body.password)
    return PasswordHealthResponse(**result)
