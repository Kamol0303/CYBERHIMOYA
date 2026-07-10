from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field, HttpUrl


class Verdict(str, Enum):
    malicious = "malicious"
    suspicious = "suspicious"
    clean = "clean"
    unknown = "unknown"


class ProblemDetail(BaseModel):
    type: str
    title: str
    status: int
    detail: str
    instance: str | None = None


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "Bearer"
    expires_in: int


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    locale: str = Field(default="uz", pattern="^(uz|ru|en)$")


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class ConsentType(str, Enum):
    analytics_meta = "analytics_meta"
    sms = "sms"
    vpn = "vpn"
    audio_upload = "audio_upload"
    emergency_law_enforcement = "emergency_law_enforcement"


class ConsentUpsert(BaseModel):
    consent_type: ConsentType
    granted: bool
    source: str = "ui"


class ConsentRecord(BaseModel):
    id: UUID
    user_id: UUID
    consent_type: ConsentType
    granted: bool
    changed_at: datetime
    source: str


class ScanContext(BaseModel):
    source: str = Field(default="manual", pattern="^(manual|qr|extension|share)$")
    client_cache_hit: bool = False


class UrlScanRequest(BaseModel):
    url: str = Field(min_length=4, max_length=2048)
    context: ScanContext = Field(default_factory=ScanContext)


class Reason(BaseModel):
    code: str
    message_key: str


class UrlScanResponse(BaseModel):
    scan_id: UUID
    url_normalized: str
    score: int = Field(ge=0, le=100)
    confidence: float = Field(ge=0.0, le=1.0)
    verdict: Verdict
    reasons: list[Reason]
    mitre_tags: list[str]
    scam_family: str | None = None
    actor_hint: str | None = None
    recommended_action: str
    scanned_at: datetime


class RiskScoreRequest(BaseModel):
    features: dict[str, Any]
    subject_type: str = Field(pattern="^(url|file|message|device)$")
    subject_id: str | None = None


class RiskScoreResponse(BaseModel):
    score: int = Field(ge=0, le=100)
    confidence: float = Field(ge=0.0, le=1.0)
    reasons: list[Reason]
    mitre_tags: list[str]
    model_version: str = "score-2026.07.1"


class ThreatFeedSyncResponse(BaseModel):
    version: str
    generated_at: datetime
    delta_url: str | None = None
    signature: str
    algorithm: str = "ed25519"
    item_counts: dict[str, int]
    items: list[dict[str, Any]] = Field(default_factory=list)


class UserProfile(BaseModel):
    id: UUID
    email: EmailStr
    role: str
    locale: str
    created_at: datetime


class HealthResponse(BaseModel):
    status: str
    version: str
    defensive_only: bool = True
