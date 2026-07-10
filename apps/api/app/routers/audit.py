from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel, Field

from app.services.auth import get_current_user
from app.services.store import store

router = APIRouter(prefix="/audit", tags=["audit"])


class AuditItem(BaseModel):
    id: UUID
    action: str
    meta: dict[str, Any] = Field(default_factory=dict)
    at: datetime


@router.get("", response_model=list[AuditItem])
def list_my_audit(
    limit: int = Query(default=50, ge=1, le=100),
    user=Depends(get_current_user),
) -> list[AuditItem]:
    """User-visible audit trail (own actions only; meta is PII-minimized)."""
    rows = store.list_audit_logs(user.id, limit=limit)
    return [AuditItem(id=r.id, action=r.action, meta=r.meta, at=r.at) for r in rows]
