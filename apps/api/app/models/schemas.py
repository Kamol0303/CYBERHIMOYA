from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field


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
    intent_tags: list[str] = Field(default_factory=list)
    campaign_id: str | None = None
    kill_chain_stage: str | None = None
    scanned_at: datetime


class QrScanRequest(BaseModel):
    payload_text: str = Field(min_length=1, max_length=4096)
    image_sha256: str | None = Field(default=None, pattern="^[a-fA-F0-9]{64}$")


class QrScanResponse(BaseModel):
    scan_id: UUID
    qr_type: str
    payload_preview: str
    url_normalized: str | None = None
    score: int = Field(ge=0, le=100)
    confidence: float = Field(ge=0.0, le=1.0)
    verdict: Verdict
    reasons: list[Reason]
    mitre_tags: list[str]
    scam_family: str | None = None
    actor_hint: str | None = None
    recommended_action: str
    intent_tags: list[str] = Field(default_factory=list)
    campaign_id: str | None = None
    kill_chain_stage: str | None = None
    scanned_at: datetime


class FileScanRequest(BaseModel):
    sha256: str = Field(pattern="^[a-fA-F0-9]{64}$")
    file_name: str | None = Field(default=None, max_length=255)
    run_yara: bool = False


class FileScanResponse(BaseModel):
    scan_id: UUID
    sha256: str
    file_name: str | None = None
    score: int = Field(ge=0, le=100)
    confidence: float = Field(ge=0.0, le=1.0)
    verdict: Verdict
    ti_hits: list[dict[str, str]] = Field(default_factory=list)
    yara_matches: list[dict[str, str]] = Field(default_factory=list)
    reasons: list[Reason]
    mitre_tags: list[str]
    scam_family: str | None = None
    actor_hint: str | None = None
    recommended_action: str
    intent_tags: list[str] = Field(default_factory=list)
    campaign_id: str | None = None
    kill_chain_stage: str | None = None
    scanned_at: datetime


class ScanHistoryItem(BaseModel):
    scan_id: UUID
    scan_type: str
    score: int
    verdict: str
    subject_hash: str
    mitre_tags: list[str]
    scam_family: str | None = None
    recommended_action: str | None = None
    intent_tags: list[str] = Field(default_factory=list)
    campaign_id: str | None = None
    created_at: datetime


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


class RiskScoreHistoryItem(BaseModel):
    id: UUID
    subject_type: str
    subject_hash: str
    score: int
    confidence: float
    model_version: str
    created_at: datetime


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


class MeStatsResponse(BaseModel):
    scans: int
    threat_events: int
    unread_notifications: int
    domain_allowlist: int
    risk_history: int
    devices: int
    defensive_only: bool = True


class HealthResponse(BaseModel):
    status: str
    version: str
    defensive_only: bool = True
    storage: str = "sqlite"


class EmergencyConsentRequest(BaseModel):
    granted: bool
    source: str = "ui"


class EmergencyConfirmRequest(BaseModel):
    modules: list[str] = Field(min_length=1, max_length=20)
    confidence: float = Field(ge=0.0, le=1.0)
    incident_ref: str | None = Field(default=None, max_length=128)


class EmergencyConfirmResponse(BaseModel):
    confirm_token: str
    expires_at: datetime
    modules: list[str]
    requires_second_confirm: bool = True


class EmergencyDispatchRequest(BaseModel):
    confirm_token: str
    channel: str = Field(default="api", pattern="^(sms|api|email)$")


class EmergencyLogItem(BaseModel):
    id: UUID
    status: str
    channel: str
    evidence_code: str
    modules: list[str]
    confidence: float
    dry_run: bool
    created_at: datetime


class EmergencyAllowlistResponse(BaseModel):
    aq039_resolved: bool
    dry_run_forced: bool
    sms_destinations_configured: int
    api_endpoints_configured: int
    email_destinations_configured: int
    note: str
    defensive_only: bool = True


class MetricsResponse(BaseModel):
    version: str
    environment: str
    defensive_only: bool = True
    emergency_dry_run: bool
    scan_rows: int
    feed_version: str
    threat_event_rows: int = 0
    notification_rows: int = 0
    domain_allowlist_rows: int = 0


class MessageEntities(BaseModel):
    urls: list[str] = Field(default_factory=list)
    bot_username: str | None = None


class SuspiciousMessageRequest(BaseModel):
    text: str = Field(min_length=1, max_length=4000)
    source: str = Field(default="paste", pattern="^(telegram_share|paste|sms_meta)$")
    entities: MessageEntities = Field(default_factory=MessageEntities)


class SuspiciousMessageResponse(BaseModel):
    report_id: UUID
    score: int = Field(ge=0, le=100)
    confidence: float = Field(ge=0.0, le=1.0)
    verdict: Verdict
    reasons: list[Reason]
    mitre_tags: list[str]
    scam_family: str | None = None
    actor_hint: str | None = None
    recommended_action: str
    intent_tags: list[str] = Field(default_factory=list)
    campaign_id: str | None = None
    kill_chain_stage: str | None = None
    preview: str
    reported_at: datetime


class BreachCheckRequest(BaseModel):
    email: EmailStr


class BreachItem(BaseModel):
    name: str
    year: int
    data_classes: list[str] = Field(default_factory=list)


class BreachCheckResponse(BaseModel):
    found: bool
    breach_count: int
    breaches: list[BreachItem]
    recommendations: list[str] = Field(default_factory=list)
    email_hash_prefix: str


class DeviceRegisterRequest(BaseModel):
    platform: str = Field(pattern="^(web|android|windows|extension)$")
    app_version: str = Field(default="0.3.0", max_length=32)
    device_label: str | None = Field(default=None, max_length=128)
    fingerprint: str | None = Field(default=None, max_length=128)


class DeviceRecord(BaseModel):
    id: UUID
    platform: str
    app_version: str
    device_label: str | None = None
    fingerprint: str
    created_at: datetime
    last_seen_at: datetime


class ThreatEventItem(BaseModel):
    event_id: UUID
    category: str
    severity: str
    subject_hash: str
    mitre_tags: list[str]
    score: int | None = None
    scam_family: str | None = None
    detected_at: datetime


class NotificationItem(BaseModel):
    id: UUID
    level: str
    body_key: str
    body_params: dict[str, Any] = Field(default_factory=dict)
    subject_hash: str | None = None
    related_event_id: UUID | None = None
    read_at: datetime | None = None
    created_at: datetime


class ReportCreateRequest(BaseModel):
    from_ts: datetime = Field(alias="from")
    to_ts: datetime = Field(alias="to")
    types: list[str] = Field(default_factory=lambda: ["scan", "threat_event"])
    format: str = Field(default="json", pattern="^(json)$")
    redact_pii: bool = True

    model_config = {"populate_by_name": True}


class ReportResponse(BaseModel):
    report_id: UUID
    status: str
    created_at: datetime
    payload: dict[str, Any] | None = None
