from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Any
from uuid import UUID, uuid4

from app.config import settings
from app.services.store_models import (
    AuditRow,
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

    return datetime.fromisoformat(value)


class SqliteStore:
    """SQLite persistence (default). Set CGA_DATABASE_URL=postgresql://... later."""

    def __init__(self, database_url: str | None = None) -> None:
        self.database_url = database_url or settings.database_url
        self._conn = self._connect()
        self._init_schema()

    def _connect(self) -> sqlite3.Connection:
        url = self.database_url
        if url.startswith("sqlite:///"):
            path = url.removeprefix("sqlite:///")
            if path != ":memory:":
                Path(path).parent.mkdir(parents=True, exist_ok=True)
            conn = sqlite3.connect(path, check_same_thread=False)
        elif url == ":memory:" or url == "sqlite:///:memory:":
            conn = sqlite3.connect(":memory:", check_same_thread=False)
        else:
            # Non-SQLite URLs fall back to local sqlite file until Postgres driver lands.
            path = settings.sqlite_fallback_path
            Path(path).parent.mkdir(parents=True, exist_ok=True)
            conn = sqlite3.connect(path, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        return conn

    def _init_schema(self) -> None:
        self._conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS users (
              id TEXT PRIMARY KEY,
              email TEXT NOT NULL,
              email_hash TEXT NOT NULL UNIQUE,
              password_hash TEXT NOT NULL,
              role TEXT NOT NULL DEFAULT 'user',
              locale TEXT NOT NULL DEFAULT 'uz',
              created_at TEXT NOT NULL,
              deleted_at TEXT
            );
            CREATE TABLE IF NOT EXISTS consent_records (
              id TEXT PRIMARY KEY,
              user_id TEXT NOT NULL REFERENCES users(id),
              consent_type TEXT NOT NULL,
              granted INTEGER NOT NULL,
              changed_at TEXT NOT NULL,
              source TEXT NOT NULL,
              UNIQUE(user_id, consent_type)
            );
            CREATE TABLE IF NOT EXISTS scan_results (
              id TEXT PRIMARY KEY,
              user_id TEXT REFERENCES users(id),
              scan_type TEXT NOT NULL,
              score INTEGER NOT NULL,
              verdict TEXT NOT NULL,
              reasons TEXT NOT NULL,
              subject_hash TEXT,
              mitre_tags TEXT,
              meta TEXT NOT NULL,
              created_at TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS audit_logs (
              id TEXT PRIMARY KEY,
              actor_id TEXT,
              action TEXT NOT NULL,
              meta TEXT NOT NULL,
              at TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS refresh_tokens (
              token TEXT PRIMARY KEY,
              user_id TEXT NOT NULL REFERENCES users(id)
            );
            """
        )
        self._conn.commit()

    def reset(self) -> None:
        for table in (
            "refresh_tokens",
            "audit_logs",
            "scan_results",
            "consent_records",
            "users",
        ):
            self._conn.execute(f"DELETE FROM {table}")
        self._conn.commit()

    def create_user(self, email: str, password: str, locale: str = "uz") -> UserRow:
        eh = hash_email(email)
        existing = self._conn.execute(
            "SELECT id FROM users WHERE email_hash = ?", (eh,)
        ).fetchone()
        if existing:
            raise ValueError("email_taken")
        user = UserRow(
            id=uuid4(),
            email=email.strip().lower(),
            email_hash=eh,
            password_hash=hash_password(password),
            locale=locale,
        )
        self._conn.execute(
            """
            INSERT INTO users (id, email, email_hash, password_hash, role, locale, created_at, deleted_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, NULL)
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
        row = self._conn.execute(
            "SELECT * FROM users WHERE email_hash = ?", (hash_email(email),)
        ).fetchone()
        if not row or row["deleted_at"] is not None:
            return None
        user = self._row_to_user(row)
        if not verify_password(password, user.password_hash):
            return None
        return user

    def get_user(self, user_id: UUID) -> UserRow | None:
        row = self._conn.execute(
            "SELECT * FROM users WHERE id = ?", (str(user_id),)
        ).fetchone()
        if not row or row["deleted_at"] is not None:
            return None
        return self._row_to_user(row)

    def upsert_consent(
        self, user_id: UUID, consent_type: str, granted: bool, source: str
    ) -> ConsentRow:
        existing = self._conn.execute(
            "SELECT * FROM consent_records WHERE user_id = ? AND consent_type = ?",
            (str(user_id), consent_type),
        ).fetchone()
        now = utcnow()
        if existing:
            self._conn.execute(
                """
                UPDATE consent_records
                SET granted = ?, changed_at = ?, source = ?
                WHERE id = ?
                """,
                (1 if granted else 0, now.isoformat(), source, existing["id"]),
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
        self._conn.execute(
            """
            INSERT INTO consent_records (id, user_id, consent_type, granted, changed_at, source)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                str(row.id),
                str(user_id),
                consent_type,
                1 if granted else 0,
                now.isoformat(),
                source,
            ),
        )
        self._conn.commit()
        self.audit(user_id, "consent.upsert", {"type": consent_type, "granted": granted})
        return row

    def list_consents(self, user_id: UUID) -> list[ConsentRow]:
        rows = self._conn.execute(
            "SELECT * FROM consent_records WHERE user_id = ? ORDER BY changed_at DESC",
            (str(user_id),),
        ).fetchall()
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
        self._conn.execute(
            """
            INSERT INTO scan_results
            (id, user_id, scan_type, score, verdict, reasons, subject_hash, mitre_tags, meta, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
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
        if user_id:
            rows = self._conn.execute(
                """
                SELECT * FROM scan_results WHERE user_id = ?
                ORDER BY created_at DESC LIMIT ?
                """,
                (str(user_id), limit),
            ).fetchall()
        else:
            rows = self._conn.execute(
                "SELECT * FROM scan_results ORDER BY created_at DESC LIMIT ?",
                (limit,),
            ).fetchall()
        return [self._row_to_scan(r) for r in rows]

    def request_erasure(self, user_id: UUID) -> None:
        user = self.get_user(user_id)
        if not user:
            return
        erased_email = f"erased+{user_id}@invalid.local"
        self._conn.execute(
            """
            UPDATE users SET deleted_at = ?, email = ?, email_hash = ?
            WHERE id = ?
            """,
            (
                utcnow().isoformat(),
                erased_email,
                hash_email(erased_email),
                str(user_id),
            ),
        )
        self._conn.execute("DELETE FROM refresh_tokens WHERE user_id = ?", (str(user_id),))
        self._conn.commit()
        self.audit(user_id, "user.erasure_requested", {})

    def audit(self, actor_id: UUID | None, action: str, meta: dict[str, Any]) -> None:
        self._conn.execute(
            "INSERT INTO audit_logs (id, actor_id, action, meta, at) VALUES (?, ?, ?, ?, ?)",
            (
                str(uuid4()),
                str(actor_id) if actor_id else None,
                action,
                json.dumps(meta),
                utcnow().isoformat(),
            ),
        )
        self._conn.commit()

    # refresh token map compatibility
    @property
    def refresh_tokens(self) -> "_RefreshTokenProxy":
        return _RefreshTokenProxy(self._conn)

    def _row_to_user(self, row: sqlite3.Row) -> UserRow:
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

    def _row_to_scan(self, row: sqlite3.Row) -> ScanRow:
        return ScanRow(
            id=UUID(row["id"]),
            user_id=UUID(row["user_id"]) if row["user_id"] else None,
            scan_type=row["scan_type"],
            score=row["score"],
            verdict=row["verdict"],
            reasons=json.loads(row["reasons"]),
            subject_hash=row["subject_hash"] or "",
            mitre_tags=json.loads(row["mitre_tags"] or "[]"),
            meta=json.loads(row["meta"] or "{}"),
            created_at=_parse_dt(row["created_at"]),
        )


class _RefreshTokenProxy:
    def __init__(self, conn: sqlite3.Connection) -> None:
        self._conn = conn

    def __setitem__(self, token: str, user_id: UUID) -> None:
        self._conn.execute(
            "INSERT OR REPLACE INTO refresh_tokens (token, user_id) VALUES (?, ?)",
            (token, str(user_id)),
        )
        self._conn.commit()

    def pop(self, token: str, default: Any = None) -> Any:
        row = self._conn.execute(
            "SELECT user_id FROM refresh_tokens WHERE token = ?", (token,)
        ).fetchone()
        self._conn.execute("DELETE FROM refresh_tokens WHERE token = ?", (token,))
        self._conn.commit()
        if not row:
            return default
        return UUID(row["user_id"])

    def clear(self) -> None:
        self._conn.execute("DELETE FROM refresh_tokens")
        self._conn.commit()


# Default store — tests override via reset() on memory DB when configured.
store = SqliteStore()
