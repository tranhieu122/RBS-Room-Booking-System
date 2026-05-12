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

    def search(
        self,
        lecturer_id: str = "",
        room_id: str = "",
        status: str = "",
        date_from: str = "",
        date_to: str = "",
        keyword: str = "",
    ) -> list[ScheduleRule]:
        clauses: list[str] = []
        params: list[object] = []
        if lecturer_id:
            clauses.append("lecturer_id = ?")
            params.append(lecturer_id)
        if room_id:
            clauses.append("room_id = ?")
            params.append(room_id)
        if status:
            clauses.append("status = ?")
            params.append(status)
        if date_from:
            clauses.append("end_date >= ?")
            params.append(date_from)
        if date_to:
            clauses.append("start_date <= ?")
            params.append(date_to)
        if keyword:
            kw = f"%{keyword}%"
            clauses.append(
                "(lecturer_name LIKE ? OR room_id LIKE ? OR subject LIKE ? OR CAST(id AS TEXT) LIKE ?)"
            )
            params.extend([kw, kw, kw, kw])
        where = ("WHERE " + " AND ".join(clauses)) if clauses else ""
        conn = get_connection()
        rows = conn.execute(
            f"SELECT * FROM schedule_rules {where} ORDER BY start_date DESC, id DESC",
            params,
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

    def update_rule(self, rule: ScheduleRule) -> None:
        """Update all editable fields of an existing rule."""
        conn = get_connection()
        days_str = ",".join(str(d) for d in sorted(rule.days_of_week))
        conn.execute(
            """
            UPDATE schedule_rules
            SET subject=?, days_of_week=?, start_time=?, end_time=?,
                start_date=?, end_date=?, room_id=?, lecturer_id=?,
                lecturer_name=?, status=?
            WHERE id=?
            """,
            (rule.subject, days_str, rule.start_time, rule.end_time,
             rule.start_date, rule.end_date, rule.room_id, rule.lecturer_id,
             rule.lecturer_name, rule.status, rule.rule_id),
        )
        conn.commit()

    def update_status(self, rule_id: int, status: str) -> None:
        conn = get_connection()
        conn.execute(
            "UPDATE schedule_rules SET status=? WHERE id=?", (status, rule_id)
        )
        conn.commit()

    def delete_occurrences(self, rule_id: int) -> None:
        """Delete all occurrences for a given rule (used before regenerating)."""
        conn = get_connection()
        conn.execute("DELETE FROM schedule_occurrences WHERE rule_id=?", (rule_id,))
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

    def used_slots_by_room(self, occurrence_date: str) -> dict[str, set[str]]:
        conn = get_connection()
        rows = conn.execute(
            """
            SELECT o.room_id, o.start_time
            FROM schedule_occurrences o
            JOIN schedule_rules r ON o.rule_id = r.id
            WHERE o.occurrence_date = ?
              AND o.status != 'Huy'
              AND r.status != 'Huy'
            """,
            (occurrence_date,),
        ).fetchall()
        start_to_slot = {
            "07:00": "Ca 1",
            "09:35": "Ca 2",
            "13:00": "Ca 3",
            "15:35": "Ca 4",
            "18:15": "Ca 5",
        }
        result: dict[str, set[str]] = {}
        for r in rows:
            slot = start_to_slot.get(str(r["start_time"]))
            if slot:
                result.setdefault(str(r["room_id"]), set()).add(slot)
        return result

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
