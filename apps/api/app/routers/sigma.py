from __future__ import annotations

from fastapi import APIRouter
from pydantic import BaseModel, Field

from app.services.sigma_rules import list_sigma_rules

router = APIRouter(prefix="/sigma", tags=["sigma"])


class SigmaRuleItem(BaseModel):
    id: str
    title: str
    version: str
    status: str
    mitre_tags: list[str] = Field(default_factory=list)
    platforms: list[str] = Field(default_factory=list)
    defensive_only: bool = True


@router.get("/rules", response_model=list[SigmaRuleItem])
def get_sigma_rules() -> list[SigmaRuleItem]:
    """FR-081 catalog stub — titles/MITRE only, no attack playbooks."""
    return [SigmaRuleItem(**r) for r in list_sigma_rules()]
