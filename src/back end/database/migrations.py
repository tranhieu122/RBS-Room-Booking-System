"""Lightweight, in-process database migration system.

How it works
────────────
SQLite stores a 32-bit integer in the database header: PRAGMA user_version.
We use that as the current schema version.  Each migration is a (version, sql)
pair.  On startup, only the migrations whose version > current user_version are
run, in order.  After all pending migrations succeed the header is updated.

Adding a new migration
──────────────────────
Append a new tuple to MIGRATIONS:

    (3, \"ALTER TABLE users ADD COLUMN last_login TEXT;\"),

The next time the app starts the column will be added automatically.

Usage
─────
Call `run_migrations(conn)` once after the connection is open and the baseline
schema has been applied.
"""
from __future__ import annotations

import sqlite3
from utils.logger import get_logger

_log = get_logger(__name__)

# ── Migration table ───────────────────────────────────────────────────────────
# Each entry: (target_version: int, sql: str)
# Versions must be consecutive and start at 1.
MIGRATIONS: list[tuple[int, str]] = [
    (1, """
        -- v1: add rejection_reason column to bookings
        ALTER TABLE bookings ADD COLUMN rejection_reason TEXT NOT NULL DEFAULT '';
    """),
    (2, """
        -- v2: add notes column to room_issues
        ALTER TABLE room_issues ADD COLUMN notes TEXT NOT NULL DEFAULT '';
    """),
    (3, """
        -- v3: internal notification system
        CREATE TABLE IF NOT EXISTS notifications (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            sender_id    TEXT NOT NULL,
            sender_name  TEXT NOT NULL,
            recipient_id TEXT NOT NULL,
            title        TEXT NOT NULL,
            message      TEXT NOT NULL,
            is_read      INTEGER NOT NULL DEFAULT 0,
            created_at   TEXT NOT NULL DEFAULT (datetime('now'))
        );
    """),
    (4, """
        -- v4: performance indexes for notifications
        CREATE INDEX IF NOT EXISTS idx_notif_recipient ON notifications(recipient_id);
        CREATE INDEX IF NOT EXISTS idx_notif_read      ON notifications(is_read);
    """),
    (5, """
        -- v5: equipment maintenance request table
        CREATE TABLE IF NOT EXISTS equipment_reports (
            id             INTEGER PRIMARY KEY AUTOINCREMENT,
            equipment_id   TEXT NOT NULL,
            equipment_name TEXT NOT NULL DEFAULT '',
            room_id        TEXT NOT NULL,
            user_id        TEXT NOT NULL,
            user_name      TEXT NOT NULL,
            description    TEXT NOT NULL,
            status         TEXT NOT NULL DEFAULT 'Cho xu ly',
            created_at     TEXT NOT NULL DEFAULT (datetime('now')),
            FOREIGN KEY (room_id) REFERENCES rooms(id)
        );
        CREATE INDEX IF NOT EXISTS idx_equip_reports_room      ON equipment_reports(room_id);
        CREATE INDEX IF NOT EXISTS idx_equip_reports_equip     ON equipment_reports(equipment_id);
        CREATE INDEX IF NOT EXISTS idx_equip_reports_status    ON equipment_reports(status);
    """),
]


def get_version(conn: sqlite3.Connection) -> int:
    """Return the current schema version stored in the DB header."""
    return conn.execute("PRAGMA user_version").fetchone()[0]


def set_version(conn: sqlite3.Connection, version: int) -> None:
    # user_version is an integer pragma — cannot use ? placeholders
    conn.execute(f"PRAGMA user_version = {int(version)}")


def run_migrations(conn: sqlite3.Connection) -> None:
    """Apply any pending migrations and update user_version."""
    current = get_version(conn)
    pending = [(v, sql) for v, sql in MIGRATIONS if v > current]

    if not pending:
        _log.debug("Schema is up-to-date at version %d", current)
        return

    _log.info("Running %d pending migration(s) (current version: %d)",
              len(pending), current)

    for version, sql in pending:
        _log.info("Applying migration v%d", version)
        try:
            conn.executescript(sql)
            conn.commit()
            set_version(conn, version)
            conn.commit()
            _log.info("Migration v%d applied successfully", version)
        except sqlite3.OperationalError as exc:
            # Column already exists (e.g. if someone ran an older migration
            # manually) — treat as harmless and advance the version pointer.
            if "duplicate column name" in str(exc).lower():
                _log.warning(
                    "Migration v%d skipped (column already exists): %s",
                    version, exc)
                set_version(conn, version)
                conn.commit()
            else:
                _log.error("Migration v%d failed: %s", version, exc,
                           exc_info=True)
                raise
