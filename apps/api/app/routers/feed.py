from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query, status
from fastapi.responses import FileResponse

from app.config import settings
from app.models.schemas import ThreatFeedSyncResponse
from app.services.feed import FEEDS_DIR, ensure_feed_files, load_feed_pack, sync_feed

router = APIRouter(prefix="/threat-feed", tags=["threat-feed"])


@router.get("/sync", response_model=ThreatFeedSyncResponse)
def threat_feed_sync(
    since_version: str | None = Query(default=None),
) -> ThreatFeedSyncResponse:
    return sync_feed(since_version)


@router.get("/delta/{version}")
def threat_feed_delta(version: str):
    """Signed feed pack download (same bytes as /cdn/feeds/{version}.json)."""
    path = FEEDS_DIR / f"{version}.json"
    if not path.exists():
        if version == settings.feed_version:
            ensure_feed_files(version)
        else:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Unknown feed version")
    return FileResponse(path, media_type="application/json", filename=f"{version}.json")


@router.get("/verify")
def threat_feed_verify(version: str | None = Query(default=None)) -> dict:
    """Server-side sanity check that on-disk pack signature matches."""
    from app.services.feed import sign_payload

    pack = load_feed_pack(version)
    expected = sign_payload(pack["signed_payload"])
    return {
        "version": pack["version"],
        "valid": expected == pack["signature"],
        "item_counts": pack["item_counts"],
        "defensive_only": True,
    }
