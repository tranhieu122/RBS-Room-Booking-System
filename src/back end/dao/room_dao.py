"""SQLite-backed room repository."""
from __future__ import annotations
import sqlite3
from models.room import Room
from database.sqlite_db import get_connection


def _row_to_room(row: sqlite3.Row) -> Room:
    return Room(
        room_id=row["id"],
        name=row["name"],
        capacity=row["capacity"],
        room_type=row["room_type"],
        equipment=row["equipment"],
        status=row["status"],
    )


class RoomDAO:
    def list_all(self) -> list[Room]:
        conn = get_connection()
        rows = conn.execute(
            "SELECT * FROM rooms WHERE status != 'Da xoa' ORDER BY id"
        ).fetchall()
        return [_row_to_room(r) for r in rows]

    def find_by_id(self, room_id: str) -> Room | None:
        conn = get_connection()
        row = conn.execute("SELECT * FROM rooms WHERE id=?", (room_id,)).fetchone()
        return _row_to_room(row) if row else None

    def save(self, room: Room) -> Room:
        conn = get_connection()
        conn.execute(
            """
            INSERT INTO rooms (id,name,capacity,room_type,equipment,status)
            VALUES (?,?,?,?,?,?)
            ON CONFLICT(id) DO UPDATE SET
                name=excluded.name,
                capacity=excluded.capacity,
                room_type=excluded.room_type,
                equipment=excluded.equipment,
                status=excluded.status
            """,
            (room.room_id, room.name, room.capacity, room.room_type,
             room.equipment, room.status),
        )
        conn.commit()
        return room

    def delete(self, room_id: str) -> None:
        """Soft-delete: mark status as 'Da xoa' instead of hard DELETE."""
        conn = get_connection()
        conn.execute("UPDATE rooms SET status='Da xoa' WHERE id=?", (room_id,))
        conn.commit()
