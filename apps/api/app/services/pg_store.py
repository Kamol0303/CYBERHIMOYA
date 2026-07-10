from __future__ import annotations

import json
from pathlib import Path
from typing import Any
from uuid import UUID, uuid4

from app.services.store_models import (
    ConsentRow,
    EmergencyLogRow,
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
                CREATE TABLE IF NOT EXISTS emergency_logs (
                  id TEXT PRIMARY KEY,
                  user_id TEXT NOT NULL REFERENCES users(id),
                  status TEXT NOT NULL,
                  channel TEXT NOT NULL,
                  evidence_code TEXT NOT NULL,
                  modules JSONB NOT NULL,
                  confidence DOUBLE PRECISION NOT NULL,
                  dry_run BOOLEAN NOT NULL,
                  meta JSONB NOT NULL,
                  created_at TIMESTAMPTZ NOT NULL
                );
                CREATE TABLE IF NOT EXISTS devices (
                  id TEXT PRIMARY KEY,
                  user_id TEXT NOT NULL REFERENCES users(id),
                  platform TEXT NOT NULL,
                  app_version TEXT NOT NULL,
                  device_label TEXT,
                  fingerprint TEXT NOT NULL,
                  created_at TIMESTAMPTZ NOT NULL,
                  last_seen_at TIMESTAMPTZ NOT NULL,
                  UNIQUE(user_id, platform, fingerprint)
                );
                CREATE TABLE IF NOT EXISTS message_reports (
                  id TEXT PRIMARY KEY,
                  user_id TEXT REFERENCES users(id),
                  source TEXT NOT NULL,
                  text_hash TEXT NOT NULL,
                  preview TEXT NOT NULL,
                  score INTEGER NOT NULL,
                  scam_family TEXT,
                  meta JSONB NOT NULL,
                  created_at TIMESTAMPTZ NOT NULL
                );
                """
            )
        self._conn.commit()

    def reset(self) -> None:
        with self._conn.cursor() as cur:
            for table in (
                "refresh_tokens",
                "emergency_logs",
                "message_reports",
                "devices",
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

    def add_emergency_log(self, row: EmergencyLogRow) -> EmergencyLogRow:
        with self._conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO emergency_logs
                (id, user_id, status, channel, evidence_code, modules, confidence, dry_run, meta, created_at)
                VALUES (%s, %s, %s, %s, %s, %s::jsonb, %s, %s, %s::jsonb, %s)
                """,
                (
                    str(row.id),
                    str(row.user_id),
                    row.status,
                    row.channel,
                    row.evidence_code,
                    json.dumps(row.modules),
                    row.confidence,
                    row.dry_run,
                    json.dumps(row.meta),
                    row.created_at.isoformat(),
                ),
            )
        self._conn.commit()
        return row

    def list_emergency_logs(self, user_id: UUID, limit: int = 20) -> list[EmergencyLogRow]:
        with self._conn.cursor() as cur:
            cur.execute(
                """
                SELECT * FROM emergency_logs WHERE user_id = %s
                ORDER BY created_at DESC LIMIT %s
                """,
                (str(user_id), limit),
            )
            rows = cur.fetchall()
        out: list[EmergencyLogRow] = []
        for r in rows:
            modules = r["modules"]
            meta = r["meta"]
            if isinstance(modules, str):
                modules = json.loads(modules)
            if isinstance(meta, str):
                meta = json.loads(meta)
            out.append(
                EmergencyLogRow(
                    id=UUID(r["id"]),
                    user_id=UUID(r["user_id"]),
                    status=r["status"],
                    channel=r["channel"],
                    evidence_code=r["evidence_code"],
                    modules=modules or [],
                    confidence=float(r["confidence"]),
                    dry_run=bool(r["dry_run"]),
                    meta=meta or {},
                    created_at=_parse_dt(r["created_at"]),
                )
            )
        return out

    def has_emergency_consent(self, user_id: UUID) -> bool:
        for row in self.list_consents(user_id):
            if row.consent_type == "emergency_law_enforcement" and row.granted:
                return True
        return False

    def upsert_device(
        self,
        user_id: UUID,
        platform: str,
        app_version: str,
        fingerprint: str,
        device_label: str | None = None,
    ):
        from app.services.store_models import DeviceRow

        now = utcnow()
        with self._conn.cursor() as cur:
            cur.execute(
                """
                SELECT * FROM devices
                WHERE user_id = %s AND platform = %s AND fingerprint = %s
                """,
                (str(user_id), platform, fingerprint),
            )
            existing = cur.fetchone()
            if existing:
                cur.execute(
                    """
                    UPDATE devices SET app_version = %s, device_label = %s, last_seen_at = %s
                    WHERE id = %s
                    """,
                    (app_version, device_label, now, existing["id"]),
                )
                device_id = existing["id"]
            else:
                device_id = str(uuid4())
                cur.execute(
                    """
                    INSERT INTO devices
                    (id, user_id, platform, app_version, device_label, fingerprint, created_at, last_seen_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    """,
                    (
                        device_id,
                        str(user_id),
                        platform,
                        app_version,
                        device_label,
                        fingerprint,
                        now,
                        now,
                    ),
                )
            cur.execute("SELECT * FROM devices WHERE id = %s", (device_id,))
            row = cur.fetchone()
        self._conn.commit()
        return DeviceRow(
            id=UUID(row["id"]),
            user_id=UUID(row["user_id"]),
            platform=row["platform"],
            app_version=row["app_version"],
            device_label=row["device_label"],
            fingerprint=row["fingerprint"],
            created_at=_parse_dt(row["created_at"]),
            last_seen_at=_parse_dt(row["last_seen_at"]),
        )

    def list_devices(self, user_id: UUID):
        from app.services.store_models import DeviceRow

        with self._conn.cursor() as cur:
            cur.execute(
                "SELECT * FROM devices WHERE user_id = %s ORDER BY last_seen_at DESC",
                (str(user_id),),
            )
            rows = cur.fetchall()
        return [
            DeviceRow(
                id=UUID(r["id"]),
                user_id=UUID(r["user_id"]),
                platform=r["platform"],
                app_version=r["app_version"],
                device_label=r["device_label"],
                fingerprint=r["fingerprint"],
                created_at=_parse_dt(r["created_at"]),
                last_seen_at=_parse_dt(r["last_seen_at"]),
            )
            for r in rows
        ]

    def delete_device(self, user_id: UUID, device_id: UUID) -> bool:
        with self._conn.cursor() as cur:
            cur.execute(
                "DELETE FROM devices WHERE id = %s AND user_id = %s",
                (str(device_id), str(user_id)),
            )
            deleted = cur.rowcount > 0
        self._conn.commit()
        return deleted

    def add_message_report(
        self,
        *,
        report_id: UUID,
        user_id: UUID | None,
        source: str,
        text_hash: str,
        preview: str,
        score: int,
        scam_family: str | None,
        meta: dict[str, Any],
    ):
        with self._conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO message_reports
                (id, user_id, source, text_hash, preview, score, scam_family, meta, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s::jsonb, %s)
                """,
                (
                    str(report_id),
                    str(user_id) if user_id else None,
                    source,
                    text_hash,
                    preview,
                    score,
                    scam_family,
                    json.dumps(meta),
                    utcnow(),
                ),
            )
        self._conn.commit()

    def add_threat_event(self, row) -> None:
        raise NotImplementedError("threat_events: use SQLite store in V1.4 or extend PostgresStore")

    def find_recent_threat_event(self, user_id: UUID, subject_hash: str, within_seconds: int = 900):
        return None

    def list_threat_events(self, user_id: UUID, limit: int = 50, severity: str | None = None):
        return []

    def get_threat_event(self, user_id: UUID, event_id: UUID):
        return None

    def add_notification(self, row) -> None:
        raise NotImplementedError("notifications: use SQLite store in V1.4 or extend PostgresStore")

    def list_notifications(self, user_id: UUID, unread_only: bool = False, limit: int = 50):
        return []

    def mark_notification_read(self, user_id: UUID, notification_id: UUID) -> bool:
        return False

    def add_report(self, row) -> None:
        raise NotImplementedError("reports: use SQLite store in V1.4 or extend PostgresStore")

    def get_report(self, user_id: UUID, report_id: UUID):
        return None

    def get_scan(self, user_id: UUID, scan_id: UUID):
        return None

    def add_risk_score_history(self, row) -> None:
        raise NotImplementedError(
            "risk_score_history: use SQLite store in V1.4 or extend PostgresStore"
        )

    def list_risk_score_history(self, user_id: UUID, limit: int = 50):
        return []

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
