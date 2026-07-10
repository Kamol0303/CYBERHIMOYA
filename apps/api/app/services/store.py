from __future__ import annotations

import hashlib
import secrets
from dataclasses import dataclass, field
from datetime import datetime, timezone
from hashlib import sha256
from typing import Any
from uuid import UUID, uuid4


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


class InMemoryStore:
    """V1 in-memory store. Replace with PostgreSQL in later sprints."""

    def __init__(self) -> None:
        self.users: dict[UUID, UserRow] = {}
        self.users_by_email_hash: dict[str, UUID] = {}
        self.consents: dict[UUID, list[ConsentRow]] = {}
        self.scans: list[ScanRow] = []
        self.audits: list[AuditRow] = []
        self.refresh_tokens: dict[str, UUID] = {}

    def create_user(self, email: str, password: str, locale: str = "uz") -> UserRow:
        eh = hash_email(email)
        if eh in self.users_by_email_hash:
            raise ValueError("email_taken")
        user = UserRow(
            id=uuid4(),
            email=email.strip().lower(),
            email_hash=eh,
            password_hash=hash_password(password),
            locale=locale,
        )
        self.users[user.id] = user
        self.users_by_email_hash[eh] = user.id
        self.consents[user.id] = []
        self.audit(user.id, "user.register", {"locale": locale})
        return user

    def authenticate(self, email: str, password: str) -> UserRow | None:
        uid = self.users_by_email_hash.get(hash_email(email))
        if not uid:
            return None
        user = self.users[uid]
        if user.deleted_at is not None:
            return None
        if not verify_password(password, user.password_hash):
            return None
        return user

    def get_user(self, user_id: UUID) -> UserRow | None:
        user = self.users.get(user_id)
        if user is None or user.deleted_at is not None:
            return None
        return user

    def upsert_consent(
        self, user_id: UUID, consent_type: str, granted: bool, source: str
    ) -> ConsentRow:
        rows = self.consents.setdefault(user_id, [])
        for row in rows:
            if row.consent_type == consent_type:
                row.granted = granted
                row.changed_at = utcnow()
                row.source = source
                self.audit(user_id, "consent.upsert", {"type": consent_type, "granted": granted})
                return row
        row = ConsentRow(
            id=uuid4(),
            user_id=user_id,
            consent_type=consent_type,
            granted=granted,
            changed_at=utcnow(),
            source=source,
        )
        rows.append(row)
        self.audit(user_id, "consent.upsert", {"type": consent_type, "granted": granted})
        return row

    def list_consents(self, user_id: UUID) -> list[ConsentRow]:
        return list(self.consents.get(user_id, []))

    def add_scan(self, row: ScanRow) -> ScanRow:
        self.scans.append(row)
        return row

    def request_erasure(self, user_id: UUID) -> None:
        user = self.users.get(user_id)
        if not user:
            return
        user.deleted_at = utcnow()
        user.email = f"erased+{user.id}@invalid.local"
        self.audit(user_id, "user.erasure_requested", {})

    def audit(self, actor_id: UUID | None, action: str, meta: dict[str, Any]) -> None:
        self.audits.append(
            AuditRow(id=uuid4(), actor_id=actor_id, action=action, meta=meta, at=utcnow())
        )


store = InMemoryStore()
