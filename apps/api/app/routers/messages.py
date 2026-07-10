from __future__ import annotations

from fastapi import APIRouter, Depends, Request, Response

from app.models.schemas import SuspiciousMessageRequest, SuspiciousMessageResponse
from app.services.auth import get_optional_user
from app.services.message_scoring import report_suspicious_message
from app.services.rate_limit import client_key, guest_limiter

router = APIRouter(prefix="/messages", tags=["messages"])


def _enforce_guest_limit(request: Request, response: Response, user) -> None:
    if user is None:
        headers = guest_limiter.check(client_key(request), instance=request.url.path)
        for k, v in headers.items():
            response.headers[k] = v


@router.post("/suspicious", response_model=SuspiciousMessageResponse)
def report_message(
    body: SuspiciousMessageRequest,
    request: Request,
    response: Response,
    user=Depends(get_optional_user),
) -> SuspiciousMessageResponse:
    _enforce_guest_limit(request, response, user)
    result = report_suspicious_message(
        body.text,
        body.source,
        body.entities.model_dump(),
        user.id if user else None,
    )
    return SuspiciousMessageResponse(**result)
