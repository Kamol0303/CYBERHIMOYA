from __future__ import annotations

from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

from app.services.auth import get_current_user
from app.services.dns_check import assess_domain, normalize_domain
from app.services.store import store

router = APIRouter(prefix="/dns", tags=["dns"])


class DnsCheckRequest(BaseModel):
    domain: str = Field(min_length=1, max_length=253)


class DnsCheckResponse(BaseModel):
    domain: str
    verdict: str
    score: int
    allowlisted: bool
    recommended_action: str
    reasons: list[dict[str, str]]
    defensive_only: bool = True


class DomainAllowlistItem(BaseModel):
    id: UUID
    domain: str
    note: str | None = None
    created_at: datetime


class DomainAllowlistCreate(BaseModel):
    domain: str = Field(min_length=1, max_length=253)
    note: str | None = Field(default=None, max_length=200)


@router.post("/check", response_model=DnsCheckResponse)
def dns_check(body: DnsCheckRequest, user=Depends(get_current_user)) -> DnsCheckResponse:
    try:
        domain = normalize_domain(body.domain)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Invalid domain"
        ) from exc
    allowlisted = store.is_domain_allowlisted(user.id, domain)
    result = assess_domain(domain, allowlisted=allowlisted)
    return DnsCheckResponse(**result)


@router.get("/allowlist", response_model=list[DomainAllowlistItem])
def list_allowlist(user=Depends(get_current_user)) -> list[DomainAllowlistItem]:
    rows = store.list_domain_allowlist(user.id)
    return [
        DomainAllowlistItem(id=r.id, domain=r.domain, note=r.note, created_at=r.created_at)
        for r in rows
    ]


@router.post("/allowlist", response_model=DomainAllowlistItem, status_code=status.HTTP_201_CREATED)
def add_allowlist(
    body: DomainAllowlistCreate, user=Depends(get_current_user)
) -> DomainAllowlistItem:
    try:
        domain = normalize_domain(body.domain)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Invalid domain"
        ) from exc
    row = store.add_domain_allowlist(user.id, domain, body.note)
    store.audit(user.id, "dns.allowlist.add", {"domain": domain})
    return DomainAllowlistItem(
        id=row.id, domain=row.domain, note=row.note, created_at=row.created_at
    )


@router.delete("/allowlist/{entry_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_allowlist(entry_id: UUID, user=Depends(get_current_user)) -> None:
    ok = store.remove_domain_allowlist(user.id, entry_id)
    if not ok:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Allowlist entry not found")
    store.audit(user.id, "dns.allowlist.remove", {"id": str(entry_id)})
