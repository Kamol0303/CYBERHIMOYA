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
            raise ValueError(
                f"Unsupported database URL scheme: {url!r}. "
                "Use sqlite:///... or postgresql://..."
            )
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
            CREATE TABLE IF NOT EXISTS emergency_logs (
              id TEXT PRIMARY KEY,
              user_id TEXT NOT NULL REFERENCES users(id),
              status TEXT NOT NULL,
              channel TEXT NOT NULL,
              evidence_code TEXT NOT NULL,
              modules TEXT NOT NULL,
              confidence REAL NOT NULL,
              dry_run INTEGER NOT NULL,
              meta TEXT NOT NULL,
              created_at TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS devices (
              id TEXT PRIMARY KEY,
              user_id TEXT NOT NULL REFERENCES users(id),
              platform TEXT NOT NULL,
              app_version TEXT NOT NULL,
              device_label TEXT,
              fingerprint TEXT NOT NULL,
              created_at TEXT NOT NULL,
              last_seen_at TEXT NOT NULL,
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
              meta TEXT NOT NULL,
              created_at TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS threat_events (
              id TEXT PRIMARY KEY,
              user_id TEXT NOT NULL REFERENCES users(id),
              category TEXT NOT NULL,
              severity TEXT NOT NULL,
              subject_hash TEXT NOT NULL,
              mitre_tags TEXT NOT NULL,
              meta TEXT NOT NULL,
              detected_at TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS notifications (
              id TEXT PRIMARY KEY,
              user_id TEXT NOT NULL REFERENCES users(id),
              level TEXT NOT NULL,
              body_key TEXT NOT NULL,
              body_params TEXT NOT NULL,
              subject_hash TEXT,
              related_event_id TEXT,
              read_at TEXT,
              created_at TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS reports (
              id TEXT PRIMARY KEY,
              user_id TEXT NOT NULL REFERENCES users(id),
              status TEXT NOT NULL,
              payload TEXT NOT NULL,
              created_at TEXT NOT NULL
            );
            """
        )
        self._conn.commit()

    def reset(self) -> None:
        for table in (
            "refresh_tokens",
            "emergency_logs",
            "message_reports",
            "devices",
            "threat_events",
            "notifications",
            "reports",
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

    def add_emergency_log(self, row: EmergencyLogRow) -> EmergencyLogRow:
        from app.services.store_models import EmergencyLogRow as EL

        assert isinstance(row, EL)
        self._conn.execute(
            """
            INSERT INTO emergency_logs
            (id, user_id, status, channel, evidence_code, modules, confidence, dry_run, meta, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                str(row.id),
                str(row.user_id),
                row.status,
                row.channel,
                row.evidence_code,
                json.dumps(row.modules),
                row.confidence,
                1 if row.dry_run else 0,
                json.dumps(row.meta),
                row.created_at.isoformat(),
            ),
        )
        self._conn.commit()
        return row

    def list_emergency_logs(self, user_id: UUID, limit: int = 20) -> list:
        from app.services.store_models import EmergencyLogRow

        rows = self._conn.execute(
            """
            SELECT * FROM emergency_logs WHERE user_id = ?
            ORDER BY created_at DESC LIMIT ?
            """,
            (str(user_id), limit),
        ).fetchall()
        return [
            EmergencyLogRow(
                id=UUID(r["id"]),
                user_id=UUID(r["user_id"]),
                status=r["status"],
                channel=r["channel"],
                evidence_code=r["evidence_code"],
                modules=json.loads(r["modules"]),
                confidence=float(r["confidence"]),
                dry_run=bool(r["dry_run"]),
                meta=json.loads(r["meta"] or "{}"),
                created_at=_parse_dt(r["created_at"]),
            )
            for r in rows
        ]

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

        existing = self._conn.execute(
            """
            SELECT * FROM devices
            WHERE user_id = ? AND platform = ? AND fingerprint = ?
            """,
            (str(user_id), platform, fingerprint),
        ).fetchone()
        now = utcnow()
        if existing:
            self._conn.execute(
                """
                UPDATE devices SET app_version = ?, device_label = ?, last_seen_at = ?
                WHERE id = ?
                """,
                (app_version, device_label, now.isoformat(), existing["id"]),
            )
            self._conn.commit()
            row = self._conn.execute(
                "SELECT * FROM devices WHERE id = ?", (existing["id"],)
            ).fetchone()
        else:
            device_id = str(uuid4())
            self._conn.execute(
                """
                INSERT INTO devices
                (id, user_id, platform, app_version, device_label, fingerprint, created_at, last_seen_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    device_id,
                    str(user_id),
                    platform,
                    app_version,
                    device_label,
                    fingerprint,
                    now.isoformat(),
                    now.isoformat(),
                ),
            )
            self._conn.commit()
            row = self._conn.execute(
                "SELECT * FROM devices WHERE id = ?", (device_id,)
            ).fetchone()
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

        rows = self._conn.execute(
            "SELECT * FROM devices WHERE user_id = ? ORDER BY last_seen_at DESC",
            (str(user_id),),
        ).fetchall()
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
        cur = self._conn.execute(
            "DELETE FROM devices WHERE id = ? AND user_id = ?",
            (str(device_id), str(user_id)),
        )
        self._conn.commit()
        return cur.rowcount > 0

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
        self._conn.execute(
            """
            INSERT INTO message_reports
            (id, user_id, source, text_hash, preview, score, scam_family, meta, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
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
                utcnow().isoformat(),
            ),
        )
        self._conn.commit()

    def add_threat_event(self, row) -> None:
        self._conn.execute(
            """
            INSERT INTO threat_events
            (id, user_id, category, severity, subject_hash, mitre_tags, meta, detected_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                str(row.id),
                str(row.user_id),
                row.category,
                row.severity,
                row.subject_hash,
                json.dumps(row.mitre_tags),
                json.dumps(row.meta),
                row.detected_at.isoformat(),
            ),
        )
        self._conn.commit()

    def find_recent_threat_event(self, user_id: UUID, subject_hash: str, within_seconds: int = 900):
        from app.services.store_models import ThreatEventRow
        from datetime import timedelta

        cutoff = (utcnow() - timedelta(seconds=within_seconds)).isoformat()
        r = self._conn.execute(
            """
            SELECT * FROM threat_events
            WHERE user_id = ? AND subject_hash = ? AND detected_at >= ?
            ORDER BY detected_at DESC LIMIT 1
            """,
            (str(user_id), subject_hash, cutoff),
        ).fetchone()
        if not r:
            return None
        return ThreatEventRow(
            id=UUID(r["id"]),
            user_id=UUID(r["user_id"]),
            category=r["category"],
            severity=r["severity"],
            subject_hash=r["subject_hash"],
            mitre_tags=json.loads(r["mitre_tags"] or "[]"),
            meta=json.loads(r["meta"] or "{}"),
            detected_at=_parse_dt(r["detected_at"]),
        )

    def list_threat_events(self, user_id: UUID, limit: int = 50, severity: str | None = None):
        from app.services.store_models import ThreatEventRow

        if severity:
            rows = self._conn.execute(
                """
                SELECT * FROM threat_events WHERE user_id = ? AND severity = ?
                ORDER BY detected_at DESC LIMIT ?
                """,
                (str(user_id), severity, limit),
            ).fetchall()
        else:
            rows = self._conn.execute(
                """
                SELECT * FROM threat_events WHERE user_id = ?
                ORDER BY detected_at DESC LIMIT ?
                """,
                (str(user_id), limit),
            ).fetchall()
        return [
            ThreatEventRow(
                id=UUID(r["id"]),
                user_id=UUID(r["user_id"]),
                category=r["category"],
                severity=r["severity"],
                subject_hash=r["subject_hash"],
                mitre_tags=json.loads(r["mitre_tags"] or "[]"),
                meta=json.loads(r["meta"] or "{}"),
                detected_at=_parse_dt(r["detected_at"]),
            )
            for r in rows
        ]

    def get_threat_event(self, user_id: UUID, event_id: UUID):
        rows = self.list_threat_events(user_id, limit=500)
        for r in rows:
            if r.id == event_id:
                return r
        return None

    def add_notification(self, row) -> None:
        self._conn.execute(
            """
            INSERT INTO notifications
            (id, user_id, level, body_key, body_params, subject_hash, related_event_id, read_at, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                str(row.id),
                str(row.user_id),
                row.level,
                row.body_key,
                json.dumps(row.body_params),
                row.subject_hash,
                str(row.related_event_id) if row.related_event_id else None,
                row.read_at.isoformat() if row.read_at else None,
                row.created_at.isoformat(),
            ),
        )
        self._conn.commit()

    def list_notifications(self, user_id: UUID, unread_only: bool = False, limit: int = 50):
        from app.services.store_models import NotificationRow

        if unread_only:
            rows = self._conn.execute(
                """
                SELECT * FROM notifications WHERE user_id = ? AND read_at IS NULL
                ORDER BY created_at DESC LIMIT ?
                """,
                (str(user_id), limit),
            ).fetchall()
        else:
            rows = self._conn.execute(
                """
                SELECT * FROM notifications WHERE user_id = ?
                ORDER BY created_at DESC LIMIT ?
                """,
                (str(user_id), limit),
            ).fetchall()
        return [
            NotificationRow(
                id=UUID(r["id"]),
                user_id=UUID(r["user_id"]),
                level=r["level"],
                body_key=r["body_key"],
                body_params=json.loads(r["body_params"] or "{}"),
                subject_hash=r["subject_hash"],
                related_event_id=UUID(r["related_event_id"]) if r["related_event_id"] else None,
                read_at=_parse_dt(r["read_at"]),
                created_at=_parse_dt(r["created_at"]),
            )
            for r in rows
        ]

    def mark_notification_read(self, user_id: UUID, notification_id: UUID) -> bool:
        cur = self._conn.execute(
            """
            UPDATE notifications SET read_at = ?
            WHERE id = ? AND user_id = ? AND read_at IS NULL
            """,
            (utcnow().isoformat(), str(notification_id), str(user_id)),
        )
        self._conn.commit()
        return cur.rowcount > 0

    def add_report(self, row) -> None:
        self._conn.execute(
            """
            INSERT INTO reports (id, user_id, status, payload, created_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                str(row.id),
                str(row.user_id),
                row.status,
                json.dumps(row.payload),
                row.created_at.isoformat(),
            ),
        )
        self._conn.commit()

    def get_report(self, user_id: UUID, report_id: UUID):
        from app.services.store_models import ReportRow

        r = self._conn.execute(
            "SELECT * FROM reports WHERE id = ? AND user_id = ?",
            (str(report_id), str(user_id)),
        ).fetchone()
        if not r:
            return None
        return ReportRow(
            id=UUID(r["id"]),
            user_id=UUID(r["user_id"]),
            status=r["status"],
            payload=json.loads(r["payload"] or "{}"),
            created_at=_parse_dt(r["created_at"]),
        )

    def get_scan(self, user_id: UUID, scan_id: UUID):
        row = self._conn.execute(
            "SELECT * FROM scan_results WHERE id = ? AND user_id = ?",
            (str(scan_id), str(user_id)),
        ).fetchone()
        if not row:
            return None
        return self._row_to_scan(row)

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


def create_store(database_url: str | None = None):
    url = database_url or settings.database_url
    if url.startswith("postgres://") or url.startswith("postgresql://"):
        # Normalize postgres:// → postgresql:// for psycopg
        if url.startswith("postgres://"):
            url = "postgresql://" + url[len("postgres://") :]
        from app.services.pg_store import PostgresStore

        return PostgresStore(url)
    return SqliteStore(url)


# Default store — tests force sqlite:///:memory: via conftest env before import.
store = create_store()
