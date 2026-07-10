from __future__ import annotations

import hashlib
import secrets
from dataclasses import dataclass, field
from datetime import datetime, timezone
from hashlib import sha256
from typing import Any
from uuid import UUID


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


def hash_email(email: str) -> str:
    return sha256(email.strip().lower().encode("utf-8")).hexdigest()


def hash_password(password: str) -> str:
    salt = secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt.encode("utf-8"), 120_000)
    return f"pbkdf2_sha256${salt}${digest.hex()}"


def verify_password(password: str, encoded: str) -> bool:
    try:
        algo, salt, digest = encoded.split("$", 2)
    except ValueError:
        return False
    if algo != "pbkdf2_sha256":
        return False
    check = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt.encode("utf-8"), 120_000)
    return secrets.compare_digest(check.hex(), digest)


@dataclass
class UserRow:
    id: UUID
    email: str
    email_hash: str
    password_hash: str
    role: str = "user"
    locale: str = "uz"
    created_at: datetime = field(default_factory=utcnow)
    deleted_at: datetime | None = None


@dataclass
class ConsentRow:
    id: UUID
    user_id: UUID
    consent_type: str
    granted: bool
    changed_at: datetime
    source: str


@dataclass
class ScanRow:
    id: UUID
    user_id: UUID | None
    scan_type: str
    score: int
    verdict: str
    reasons: list[dict[str, Any]]
    subject_hash: str
    mitre_tags: list[str]
    meta: dict[str, Any]
    created_at: datetime


@dataclass
class AuditRow:
    id: UUID
    actor_id: UUID | None
    action: str
    meta: dict[str, Any]
    at: datetime
