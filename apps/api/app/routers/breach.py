from __future__ import annotations

from fastapi import APIRouter, Depends

from app.models.schemas import BreachCheckRequest, BreachCheckResponse, BreachItem
from app.services import breach as breach_svc
from app.services.auth import get_optional_user
from app.services.store import store

router = APIRouter(tags=["breach"])


@router.post("/breach-check", response_model=BreachCheckResponse)
def breach_check(
    body: BreachCheckRequest,
    user=Depends(get_optional_user),
) -> BreachCheckResponse:
    result = breach_svc.check_email(str(body.email))
    store.audit(
        user.id if user else None,
        "breach.checked",
        {
            "found": result["found"],
            "breach_count": result["breach_count"],
            "email_hash_prefix": result["email_hash_prefix"],
        },
    )
    return BreachCheckResponse(
        found=result["found"],
        breach_count=result["breach_count"],
        breaches=[BreachItem(**b) for b in result["breaches"]],
        recommendations=result["recommendations"],
        email_hash_prefix=result["email_hash_prefix"],
    )
