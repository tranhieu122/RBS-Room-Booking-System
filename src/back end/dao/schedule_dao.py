"""SQLite-backed schedule repository."""
from __future__ import annotations
import sqlite3
from models.schedule import Schedule
from database.sqlite_db import get_connection


def _row_to_schedule(row: sqlite3.Row) -> Schedule:
    return Schedule(
        room_id=row["room_id"],
        weekday=row["weekday"],
        slot=row["slot"],
        label=row["label"],
        status=row["status"],
    )


class ScheduleDAO:
    def list_all(self) -> list[Schedule]:
        conn = get_connection()
        rows = conn.execute(
            "SELECT * FROM schedules ORDER BY room_id, weekday, slot"
        ).fetchall()
        return [_row_to_schedule(r) for r in rows]

    def find_by_room(self, room_id: str) -> list[Schedule]:
        conn = get_connection()
        rows = conn.execute(
            "SELECT * FROM schedules WHERE room_id=? ORDER BY weekday, slot",
            (room_id,),
        ).fetchall()
        return [_row_to_schedule(r) for r in rows]

    def save(self, schedule: Schedule) -> Schedule:
        conn = get_connection()
        conn.execute(
            """
            INSERT INTO schedules (room_id, weekday, slot, label, status)
            VALUES (?,?,?,?,?)
            ON CONFLICT(room_id, weekday, slot) DO UPDATE SET
                label=excluded.label,
                status=excluded.status
            """,
            (schedule.room_id, schedule.weekday, schedule.slot,
             schedule.label, schedule.status),
        )
        conn.commit()
        return schedule

    def delete_by_room(self, room_id: str) -> None:
        conn = get_connection()
        conn.execute("DELETE FROM schedules WHERE room_id=?", (room_id,))
        conn.commit()

    # backwards-compat with old code that called build_schedule(booking_rows)
    def build_schedule(self, booking_rows: list[object]) -> list[Schedule]:  # noqa: ARG002
        return self.list_all()
