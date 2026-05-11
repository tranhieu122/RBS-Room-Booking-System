"""SQLite-backed equipment repository."""
from __future__ import annotations
import sqlite3
from models.equipment import Equipment
from database.sqlite_db import get_connection


def _row_to_equipment(row: sqlite3.Row) -> Equipment:
    return Equipment(
        equipment_id=row["id"],
        name=row["name"],
        equipment_type=row["equipment_type"],
        room_id=row["room_id"],
        status=row["status"],
        purchase_date=row["purchase_date"],
    )


class EquipmentDAO:
    def list_all(self) -> list[Equipment]:
        conn = get_connection()
        rows = conn.execute("SELECT * FROM equipment ORDER BY id").fetchall()
        return [_row_to_equipment(r) for r in rows]

    def find_by_id(self, equipment_id: str) -> Equipment | None:
        conn = get_connection()
        row = conn.execute("SELECT * FROM equipment WHERE id=?", (equipment_id,)).fetchone()
        return _row_to_equipment(row) if row else None

    def save(self, equipment: Equipment) -> Equipment:
        conn = get_connection()
        conn.execute(
            """
            INSERT INTO equipment (id,name,equipment_type,room_id,status,purchase_date)
            VALUES (?,?,?,?,?,?)
            ON CONFLICT(id) DO UPDATE SET
                name=excluded.name,
                equipment_type=excluded.equipment_type,
                room_id=excluded.room_id,
                status=excluded.status,
                purchase_date=excluded.purchase_date
            """,
            (equipment.equipment_id, equipment.name, equipment.equipment_type,
             equipment.room_id, equipment.status, equipment.purchase_date),
        )
        conn.commit()
        return equipment

    def delete(self, equipment_id: str) -> None:
        conn = get_connection()
        conn.execute("DELETE FROM equipment WHERE id=?", (equipment_id,))
        conn.commit()
