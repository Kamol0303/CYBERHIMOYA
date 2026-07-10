from __future__ import annotations

import json
from pathlib import Path
from typing import Any
from uuid import UUID, uuid4

from app.services.store_models import (
    ConsentRow,
    ScanRow,
    UserRow,
    hash_email,
    hash_password,
    utcnow,
    verify_password,
)


def _parse_dt(value: str | None):
    if value is None:
        return None
    from datetime import datetime

    if isinstance(value, datetime):
        return value
    return datetime.fromisoformat(str(value).replace("Z", "+00:00"))


class PostgresStore:
    """PostgreSQL persistence via psycopg. Same public API as SqliteStore."""

    def __init__(self, database_url: str) -> None:
        try:
            import psycopg
            from psycopg.rows import dict_row
        except ImportError as exc:
            raise RuntimeError(
                "psycopg is required for PostgreSQL. pip install 'psycopg[binary]'"
            ) from exc

        self.database_url = database_url
        self._psycopg = psycopg
        self._conn = psycopg.connect(database_url, row_factory=dict_row)
        self._conn.autocommit = False
        self._init_schema()

    def _init_schema(self) -> None:
        with self._conn.cursor() as cur:
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS users (
                  id TEXT PRIMARY KEY,
                  email TEXT NOT NULL,
                  email_hash TEXT NOT NULL UNIQUE,
                  password_hash TEXT NOT NULL,
                  role TEXT NOT NULL DEFAULT 'user',
                  locale TEXT NOT NULL DEFAULT 'uz',
                  created_at TIMESTAMPTZ NOT NULL,
                  deleted_at TIMESTAMPTZ
                );
                CREATE TABLE IF NOT EXISTS consent_records (
                  id TEXT PRIMARY KEY,
                  user_id TEXT NOT NULL REFERENCES users(id),
                  consent_type TEXT NOT NULL,
                  granted BOOLEAN NOT NULL,
                  changed_at TIMESTAMPTZ NOT NULL,
                  source TEXT NOT NULL,
                  UNIQUE(user_id, consent_type)
                );
                CREATE TABLE IF NOT EXISTS scan_results (
                  id TEXT PRIMARY KEY,
                  user_id TEXT REFERENCES users(id),
                  scan_type TEXT NOT NULL,
                  score INTEGER NOT NULL,
                  verdict TEXT NOT NULL,
                  reasons JSONB NOT NULL,
                  subject_hash TEXT,
                  mitre_tags JSONB,
                  meta JSONB NOT NULL,
                  created_at TIMESTAMPTZ NOT NULL
                );
                CREATE TABLE IF NOT EXISTS audit_logs (
                  id TEXT PRIMARY KEY,
                  actor_id TEXT,
                  action TEXT NOT NULL,
                  meta JSONB NOT NULL,
                  at TIMESTAMPTZ NOT NULL
                );
                CREATE TABLE IF NOT EXISTS refresh_tokens (
                  token TEXT PRIMARY KEY,
                  user_id TEXT NOT NULL REFERENCES users(id)
                );
                """
            )
        self._conn.commit()

    def reset(self) -> None:
        with self._conn.cursor() as cur:
            for table in (
                "refresh_tokens",
                "audit_logs",
                "scan_results",
                "consent_records",
                "users",
            ):
                cur.execute(f"DELETE FROM {table}")
        self._conn.commit()

    def create_user(self, email: str, password: str, locale: str = "uz") -> UserRow:
        eh = hash_email(email)
        with self._conn.cursor() as cur:
            cur.execute("SELECT id FROM users WHERE email_hash = %s", (eh,))
            if cur.fetchone():
                raise ValueError("email_taken")
            user = UserRow(
                id=uuid4(),
                email=email.strip().lower(),
                email_hash=eh,
                password_hash=hash_password(password),
                locale=locale,
            )
            cur.execute(
                """
                INSERT INTO users (id, email, email_hash, password_hash, role, locale, created_at, deleted_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, NULL)
                """,
                (
                    str(user.id),
                    user.email,
                    user.email_hash,
                    user.password_hash,
                    user.role,
                    user.locale,
                    user.created_at.isoformat(),
                ),
            )
        self._conn.commit()
        self.audit(user.id, "user.register", {"locale": locale})
        return user

    def authenticate(self, email: str, password: str) -> UserRow | None:
        with self._conn.cursor() as cur:
            cur.execute("SELECT * FROM users WHERE email_hash = %s", (hash_email(email),))
            row = cur.fetchone()
        if not row or row["deleted_at"] is not None:
            return None
        user = self._row_to_user(row)
        if not verify_password(password, user.password_hash):
            return None
        return user

    def get_user(self, user_id: UUID) -> UserRow | None:
        with self._conn.cursor() as cur:
            cur.execute("SELECT * FROM users WHERE id = %s", (str(user_id),))
            row = cur.fetchone()
        if not row or row["deleted_at"] is not None:
            return None
        return self._row_to_user(row)

    def upsert_consent(
        self, user_id: UUID, consent_type: str, granted: bool, source: str
    ) -> ConsentRow:
        now = utcnow()
        with self._conn.cursor() as cur:
            cur.execute(
                "SELECT * FROM consent_records WHERE user_id = %s AND consent_type = %s",
                (str(user_id), consent_type),
            )
            existing = cur.fetchone()
            if existing:
                cur.execute(
                    """
                    UPDATE consent_records
                    SET granted = %s, changed_at = %s, source = %s
                    WHERE id = %s
                    """,
                    (granted, now.isoformat(), source, existing["id"]),
                )
                self._conn.commit()
                self.audit(user_id, "consent.upsert", {"type": consent_type, "granted": granted})
                return ConsentRow(
                    id=UUID(existing["id"]),
                    user_id=user_id,
                    consent_type=consent_type,
                    granted=granted,
                    changed_at=now,
                    source=source,
                )
            row = ConsentRow(
                id=uuid4(),
                user_id=user_id,
                consent_type=consent_type,
                granted=granted,
                changed_at=now,
                source=source,
            )
            cur.execute(
                """
                INSERT INTO consent_records (id, user_id, consent_type, granted, changed_at, source)
                VALUES (%s, %s, %s, %s, %s, %s)
                """,
                (
                    str(row.id),
                    str(user_id),
                    consent_type,
                    granted,
                    now.isoformat(),
                    source,
                ),
            )
        self._conn.commit()
        self.audit(user_id, "consent.upsert", {"type": consent_type, "granted": granted})
        return row

    def list_consents(self, user_id: UUID) -> list[ConsentRow]:
        with self._conn.cursor() as cur:
            cur.execute(
                """
                SELECT * FROM consent_records WHERE user_id = %s
                ORDER BY changed_at DESC
                """,
                (str(user_id),),
            )
            rows = cur.fetchall()
        return [
            ConsentRow(
                id=UUID(r["id"]),
                user_id=UUID(r["user_id"]),
                consent_type=r["consent_type"],
                granted=bool(r["granted"]),
                changed_at=_parse_dt(r["changed_at"]),
                source=r["source"],
            )
            for r in rows
        ]

    def add_scan(self, row: ScanRow) -> ScanRow:
        with self._conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO scan_results
                (id, user_id, scan_type, score, verdict, reasons, subject_hash, mitre_tags, meta, created_at)
                VALUES (%s, %s, %s, %s, %s, %s::jsonb, %s, %s::jsonb, %s::jsonb, %s)
                """,
                (
                    str(row.id),
                    str(row.user_id) if row.user_id else None,
                    row.scan_type,
                    row.score,
                    row.verdict,
                    json.dumps(row.reasons),
                    row.subject_hash,
                    json.dumps(row.mitre_tags),
                    json.dumps(row.meta),
                    row.created_at.isoformat(),
                ),
            )
        self._conn.commit()
        return row

    def list_scans(self, user_id: UUID | None = None, limit: int = 20) -> list[ScanRow]:
        with self._conn.cursor() as cur:
            if user_id:
                cur.execute(
                    """
                    SELECT * FROM scan_results WHERE user_id = %s
                    ORDER BY created_at DESC LIMIT %s
                    """,
                    (str(user_id), limit),
                )
            else:
                cur.execute(
                    "SELECT * FROM scan_results ORDER BY created_at DESC LIMIT %s",
                    (limit,),
                )
            rows = cur.fetchall()
        return [self._row_to_scan(r) for r in rows]

    def request_erasure(self, user_id: UUID) -> None:
        user = self.get_user(user_id)
        if not user:
            return
        erased_email = f"erased+{user_id}@invalid.local"
        with self._conn.cursor() as cur:
            cur.execute(
                """
                UPDATE users SET deleted_at = %s, email = %s, email_hash = %s
                WHERE id = %s
                """,
                (
                    utcnow().isoformat(),
                    erased_email,
                    hash_email(erased_email),
                    str(user_id),
                ),
            )
            cur.execute("DELETE FROM refresh_tokens WHERE user_id = %s", (str(user_id),))
        self._conn.commit()
        self.audit(user_id, "user.erasure_requested", {})

    def audit(self, actor_id: UUID | None, action: str, meta: dict[str, Any]) -> None:
        with self._conn.cursor() as cur:
            cur.execute(
                "INSERT INTO audit_logs (id, actor_id, action, meta, at) VALUES (%s, %s, %s, %s::jsonb, %s)",
                (
                    str(uuid4()),
                    str(actor_id) if actor_id else None,
                    action,
                    json.dumps(meta),
                    utcnow().isoformat(),
                ),
            )
        self._conn.commit()

    @property
    def refresh_tokens(self) -> "_PgRefreshTokenProxy":
        return _PgRefreshTokenProxy(self._conn)

    def _row_to_user(self, row: dict) -> UserRow:
        return UserRow(
            id=UUID(row["id"]),
            email=row["email"],
            email_hash=row["email_hash"],
            password_hash=row["password_hash"],
            role=row["role"],
            locale=row["locale"],
            created_at=_parse_dt(row["created_at"]),
            deleted_at=_parse_dt(row["deleted_at"]),
        )

    def _row_to_scan(self, row: dict) -> ScanRow:
        reasons = row["reasons"]
        mitre = row["mitre_tags"]
        meta = row["meta"]
        if isinstance(reasons, str):
            reasons = json.loads(reasons)
        if isinstance(mitre, str):
            mitre = json.loads(mitre)
        if isinstance(meta, str):
            meta = json.loads(meta)
        return ScanRow(
            id=UUID(row["id"]),
            user_id=UUID(row["user_id"]) if row["user_id"] else None,
            scan_type=row["scan_type"],
            score=row["score"],
            verdict=row["verdict"],
            reasons=reasons or [],
            subject_hash=row["subject_hash"] or "",
            mitre_tags=mitre or [],
            meta=meta or {},
            created_at=_parse_dt(row["created_at"]),
        )


class _PgRefreshTokenProxy:
    def __init__(self, conn) -> None:
        self._conn = conn

    def __setitem__(self, token: str, user_id: UUID) -> None:
        with self._conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO refresh_tokens (token, user_id) VALUES (%s, %s)
                ON CONFLICT (token) DO UPDATE SET user_id = EXCLUDED.user_id
                """,
                (token, str(user_id)),
            )
        self._conn.commit()

    def pop(self, token: str, default: Any = None) -> Any:
        with self._conn.cursor() as cur:
            cur.execute("SELECT user_id FROM refresh_tokens WHERE token = %s", (token,))
            row = cur.fetchone()
            cur.execute("DELETE FROM refresh_tokens WHERE token = %s", (token,))
        self._conn.commit()
        if not row:
            return default
        return UUID(row["user_id"])

    def clear(self) -> None:
        with self._conn.cursor() as cur:
            cur.execute("DELETE FROM refresh_tokens")
        self._conn.commit()
