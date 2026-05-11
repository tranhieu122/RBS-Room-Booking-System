"""DAOs for room_ratings and room_issues tables."""
from __future__ import annotations
import sqlite3
from dataclasses import dataclass
from database.sqlite_db import get_connection


@dataclass
class RoomRating:
    rating_id: int
    room_id: str
    user_id: str
    user_name: str
    stars: int
    comment: str
    created_at: str = ""


@dataclass
class RoomIssue:
    issue_id: int
    room_id: str
    user_id: str
    user_name: str
    description: str
    status: str = "Chua xu ly"
    created_at: str = ""


class RoomRatingDAO:
    def add(self, room_id: str, user_id: str, user_name: str,
            stars: int, comment: str) -> RoomRating:
        conn = get_connection()
        cur = conn.execute(
            """INSERT INTO room_ratings (room_id, user_id, user_name, stars, comment)
               VALUES (?, ?, ?, ?, ?)""",
            (room_id, user_id, user_name, stars, comment),
        )
        conn.commit()
        row = conn.execute(
            "SELECT * FROM room_ratings WHERE id=?", (cur.lastrowid,)
        ).fetchone()
        return _row_to_rating(row)

    def list_by_room(self, room_id: str) -> list[RoomRating]:
        conn = get_connection()
        rows = conn.execute(
            "SELECT * FROM room_ratings WHERE room_id=? ORDER BY created_at DESC",
            (room_id,),
        ).fetchall()
        return [_row_to_rating(r) for r in rows]

    def average_stars(self, room_id: str) -> float:
        conn = get_connection()
        row = conn.execute(
            "SELECT AVG(stars) FROM room_ratings WHERE room_id=?", (room_id,)
        ).fetchone()
        return round(row[0] or 0.0, 1)

    def user_rating(self, room_id: str, user_id: str) -> RoomRating | None:
        conn = get_connection()
        row = conn.execute(
            "SELECT * FROM room_ratings WHERE room_id=? AND user_id=? ORDER BY id DESC LIMIT 1",
            (room_id, user_id),
        ).fetchone()
        return _row_to_rating(row) if row else None


class RoomIssueDAO:
    def report(self, room_id: str, user_id: str, user_name: str,
               description: str) -> RoomIssue:
        conn = get_connection()
        cur = conn.execute(
            """INSERT INTO room_issues (room_id, user_id, user_name, description)
               VALUES (?, ?, ?, ?)""",
            (room_id, user_id, user_name, description),
        )
        conn.commit()
        row = conn.execute(
            "SELECT * FROM room_issues WHERE id=?", (cur.lastrowid,)
        ).fetchone()
        return _row_to_issue(row)

    def list_all(self, room_id: str = "") -> list[RoomIssue]:
        conn = get_connection()
        if room_id:
            rows = conn.execute(
                "SELECT * FROM room_issues WHERE room_id=? ORDER BY created_at DESC",
                (room_id,),
            ).fetchall()
        else:
            rows = conn.execute(
                "SELECT * FROM room_issues ORDER BY created_at DESC"
            ).fetchall()
        return [_row_to_issue(r) for r in rows]

    def update_status(self, issue_id: int, status: str) -> None:
        conn = get_connection()
        conn.execute(
            "UPDATE room_issues SET status=? WHERE id=?", (status, issue_id)
        )
        conn.commit()


def _row_to_rating(row: sqlite3.Row) -> RoomRating:
    return RoomRating(
        rating_id=row["id"],
        room_id=row["room_id"],
        user_id=row["user_id"],
        user_name=row["user_name"],
        stars=row["stars"],
        comment=row["comment"],
        created_at=row["created_at"],
    )


def _row_to_issue(row: sqlite3.Row) -> RoomIssue:
    return RoomIssue(
        issue_id=row["id"],
        room_id=row["room_id"],
        user_id=row["user_id"],
        user_name=row["user_name"],
        description=row["description"],
        status=row["status"],
        created_at=row["created_at"],
    )


# ─── Equipment Maintenance Reports ───────────────────────────────────────────

@dataclass
class EquipmentReport:
    report_id: int
    equipment_id: str
    equipment_name: str
    room_id: str
    user_id: str
    user_name: str
    description: str
    status: str = "Cho xu ly"
    created_at: str = ""


class EquipmentReportDAO:
    def report(self, equipment_id: str, equipment_name: str, room_id: str,
               user_id: str, user_name: str, description: str) -> EquipmentReport:
        conn = get_connection()
        cur = conn.execute(
            """INSERT INTO equipment_reports
               (equipment_id, equipment_name, room_id, user_id, user_name, description)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (equipment_id, equipment_name, room_id, user_id, user_name, description),
        )
        conn.commit()
        row = conn.execute(
            "SELECT * FROM equipment_reports WHERE id=?", (cur.lastrowid,)
        ).fetchone()
        return _row_to_equip_report(row)

    def list_all(self, room_id: str = "", status: str = "") -> list[EquipmentReport]:
        conn = get_connection()
        sql = "SELECT * FROM equipment_reports"
        params: list[str] = []
        conditions: list[str] = []
        if room_id:
            conditions.append("room_id=?")
            params.append(room_id)
        if status:
            conditions.append("status=?")
            params.append(status)
        if conditions:
            sql += " WHERE " + " AND ".join(conditions)
        sql += " ORDER BY created_at DESC"
        rows = conn.execute(sql, params).fetchall()
        return [_row_to_equip_report(r) for r in rows]

    def update_status(self, report_id: int, status: str) -> None:
        conn = get_connection()
        conn.execute(
            "UPDATE equipment_reports SET status=? WHERE id=?", (status, report_id)
        )
        conn.commit()


def _row_to_equip_report(row: sqlite3.Row) -> EquipmentReport:
    return EquipmentReport(
        report_id=row["id"],
        equipment_id=row["equipment_id"],
        equipment_name=row["equipment_name"],
        room_id=row["room_id"],
        user_id=row["user_id"],
        user_name=row["user_name"],
        description=row["description"],
        status=row["status"],
        created_at=row["created_at"],
    )
