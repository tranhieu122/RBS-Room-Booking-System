"""SQLite-backed ScheduleRule / ScheduleOccurrence repository."""
from __future__ import annotations
import sqlite3
from models.schedule_rule import ScheduleRule, ScheduleOccurrence
from database.sqlite_db import get_connection


def _row_to_rule(row: sqlite3.Row) -> ScheduleRule:
    return ScheduleRule(
        rule_id=row["id"],
        subject=row["subject"],
        days_of_week=[int(d) for d in row["days_of_week"].split(",") if d],
        start_time=row["start_time"],
        end_time=row["end_time"],
        start_date=row["start_date"],
        end_date=row["end_date"],
        room_id=row["room_id"],
        lecturer_id=row["lecturer_id"],
        lecturer_name=row["lecturer_name"],
        status=row["status"],
        created_at=row["created_at"],
    )


def _row_to_occ(row: sqlite3.Row) -> ScheduleOccurrence:
    return ScheduleOccurrence(
        occ_id=row["id"],
        rule_id=row["rule_id"],
        occurrence_date=row["occurrence_date"],
        day_of_week=row["day_of_week"],
        subject=row["subject"],
        start_time=row["start_time"],
        end_time=row["end_time"],
        room_id=row["room_id"],
        lecturer_name=row["lecturer_name"],
        status=row["status"],
    )


class ScheduleRuleDAO:
    # ── Rules ─────────────────────────────────────────────────────────────────

    def list_all(self) -> list[ScheduleRule]:
        conn = get_connection()
        rows = conn.execute(
            "SELECT * FROM schedule_rules ORDER BY start_date DESC, id DESC"
        ).fetchall()
        return [_row_to_rule(r) for r in rows]

    def find_by_id(self, rule_id: int) -> ScheduleRule | None:
        conn = get_connection()
        row = conn.execute(
            "SELECT * FROM schedule_rules WHERE id=?", (rule_id,)
        ).fetchone()
        return _row_to_rule(row) if row else None

    def save(self, rule: ScheduleRule) -> ScheduleRule:
        conn = get_connection()
        days_str = ",".join(str(d) for d in sorted(rule.days_of_week))
        cur = conn.execute(
            """
            INSERT INTO schedule_rules
                (subject, days_of_week, start_time, end_time,
                 start_date, end_date, room_id, lecturer_id,
                 lecturer_name, status)
            VALUES (?,?,?,?,?,?,?,?,?,?)
            """,
            (rule.subject, days_str, rule.start_time, rule.end_time,
             rule.start_date, rule.end_date, rule.room_id, rule.lecturer_id,
             rule.lecturer_name, rule.status),
        )
        conn.commit()
        rule.rule_id = cur.lastrowid or 0
        return rule

    def update_status(self, rule_id: int, status: str) -> None:
        conn = get_connection()
        conn.execute(
            "UPDATE schedule_rules SET status=? WHERE id=?", (status, rule_id)
        )
        conn.commit()

    def delete(self, rule_id: int) -> None:
        conn = get_connection()
        # Occurrences are deleted via ON DELETE CASCADE
        conn.execute("DELETE FROM schedule_rules WHERE id=?", (rule_id,))
        conn.commit()

    # ── Occurrences ───────────────────────────────────────────────────────────

    def insert_occurrences(self, occurrences: list[ScheduleOccurrence]) -> None:
        if not occurrences:
            return
        conn = get_connection()
        conn.executemany(
            """
            INSERT INTO schedule_occurrences
                (rule_id, occurrence_date, day_of_week, subject,
                 start_time, end_time, room_id, lecturer_name, status)
            VALUES (?,?,?,?,?,?,?,?,?)
            """,
            [
                (o.rule_id, o.occurrence_date, o.day_of_week, o.subject,
                 o.start_time, o.end_time, o.room_id, o.lecturer_name, o.status)
                for o in occurrences
            ],
        )
        conn.commit()

    def list_occurrences(self, rule_id: int) -> list[ScheduleOccurrence]:
        conn = get_connection()
        rows = conn.execute(
            "SELECT * FROM schedule_occurrences WHERE rule_id=? "
            "ORDER BY occurrence_date",
            (rule_id,),
        ).fetchall()
        return [_row_to_occ(r) for r in rows]

    def list_occurrences_by_date_range(
        self, date_from: str, date_to: str
    ) -> list[dict]:
        """Return occurrences with parent rule status."""
        conn = get_connection()
        rows = conn.execute(
            """
            SELECT o.*, r.status as rule_status, r.lecturer_id
            FROM schedule_occurrences o
            JOIN schedule_rules r ON o.rule_id = r.id
            WHERE o.occurrence_date >= ? AND o.occurrence_date <= ?
            ORDER BY o.occurrence_date, o.start_time
            """,
            (date_from, date_to),
        ).fetchall()
        return [dict(r) for r in rows]

    def count_occurrences(self, rule_id: int) -> int:
        conn = get_connection()
        row = conn.execute(
            "SELECT COUNT(*) FROM schedule_occurrences WHERE rule_id=?",
            (rule_id,),
        ).fetchone()
        return row[0] if row else 0

    def update_occurrence_status(self, occ_id: int, status: str) -> None:
        conn = get_connection()
        conn.execute(
            "UPDATE schedule_occurrences SET status=? WHERE id=?",
            (status, occ_id),
        )
        conn.commit()
