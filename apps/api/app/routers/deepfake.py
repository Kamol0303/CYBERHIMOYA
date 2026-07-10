from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

from app.services.auth import get_current_user
from app.services.deepfake import assess_voice_meta
from app.services.store import store

router = APIRouter(prefix="/deepfake", tags=["deepfake"])


class DeepfakeVoiceRequest(BaseModel):
    """Metadata-only request — do not upload raw audio in V1 stub."""

    duration_ms: int = Field(ge=1, le=600_000)
    sample_rate_hz: int = Field(default=16000, ge=8000, le=96000)
    filename_hint: str | None = Field(default=None, max_length=128)


class DeepfakeVoiceResponse(BaseModel):
    score: int
    verdict: str
    confidence: float
    recommended_action: str
    reasons: list[dict[str, str]]
    mitre_tags: list[str]
    meta_hash: str
    model_version: str
    defensive_only: bool = True
    audio_stored: bool = False


def _has_audio_consent(user_id) -> bool:
    for row in store.list_consents(user_id):
        if row.consent_type == "audio_upload" and row.granted:
            return True
    return False


@router.post("/voice", response_model=DeepfakeVoiceResponse)
def deepfake_voice(
    body: DeepfakeVoiceRequest, user=Depends(get_current_user)
) -> DeepfakeVoiceResponse:
    """FR-042 — requires audio_upload consent; no live recording; audio not stored."""
    if not _has_audio_consent(user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="audio_upload consent required",
        )
    result = assess_voice_meta(
        duration_ms=body.duration_ms,
        sample_rate_hz=body.sample_rate_hz,
        filename_hint=body.filename_hint,
    )
    store.audit(
        user.id,
        "deepfake.voice_assess",
        {"meta_hash": result["meta_hash"], "score": result["score"], "audio_stored": False},
    )
    return DeepfakeVoiceResponse(**result)
