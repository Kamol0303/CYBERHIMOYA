"""Deepfake voice stub (FR-042) — consent-gated, no live capture."""

from __future__ import annotations

from hashlib import sha256


def assess_voice_meta(*, duration_ms: int, sample_rate_hz: int, filename_hint: str | None) -> dict:
    """Heuristic stub — never stores audio bytes; only meta features."""
    score = 15
    reasons: list[dict[str, str]] = []
    name = (filename_hint or "").lower()

    if duration_ms < 800:
        score += 10
        reasons.append({"code": "TOO_SHORT", "message_key": "deepfake.too_short"})
    if duration_ms > 120_000:
        score += 5
        reasons.append({"code": "LONG_CLIP", "message_key": "deepfake.long_clip"})
    if sample_rate_hz and sample_rate_hz < 8000:
        score += 20
        reasons.append({"code": "LOW_RATE", "message_key": "deepfake.low_rate"})
    if any(tok in name for tok in ("clone", "tts", "synth", "fake", "deepfake")):
        score += 35
        reasons.append({"code": "NAME_HEURISTIC", "message_key": "deepfake.name_heuristic"})

    score = max(0, min(100, score))
    if score >= 70:
        verdict = "suspicious"
        action = "warn_and_review"
    elif score >= 40:
        verdict = "watch"
        action = "caution"
    else:
        verdict = "unlikely"
        action = "allow"

    meta_hash = sha256(
        f"{duration_ms}|{sample_rate_hz}|{(filename_hint or '')[:64]}".encode("utf-8")
    ).hexdigest()

    return {
        "score": score,
        "verdict": verdict,
        "confidence": min(0.75, 0.4 + score / 250),
        "recommended_action": action,
        "reasons": reasons
        or [{"code": "NO_SIGNAL", "message_key": "deepfake.clean"}],
        "mitre_tags": ["T1656"] if score >= 40 else [],
        "meta_hash": meta_hash,
        "model_version": "deepfake-stub-2026.07.1",
        "defensive_only": True,
        "audio_stored": False,
    }
