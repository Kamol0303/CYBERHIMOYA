from __future__ import annotations

from fastapi import APIRouter, Query

from app.models.schemas import ThreatFeedSyncResponse
from app.services.feed import sync_feed

router = APIRouter(prefix="/threat-feed", tags=["threat-feed"])


@router.get("/sync", response_model=ThreatFeedSyncResponse)
def threat_feed_sync(
    since_version: str | None = Query(default=None),
) -> ThreatFeedSyncResponse:
    return sync_feed(since_version)
