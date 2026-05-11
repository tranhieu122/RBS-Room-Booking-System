"""Notification data-access object."""
from __future__ import annotations
from database.sqlite_db import get_connection


class NotificationDAO:
    def list_for_user(self, user_id: str) -> list[dict]:
        conn = get_connection()
        rows = conn.execute(
            "SELECT * FROM notifications WHERE recipient_id=? ORDER BY created_at DESC LIMIT 100",
            (user_id,),
        ).fetchall()
        return [dict(r) for r in rows]

    def count_unread(self, user_id: str) -> int:
        conn = get_connection()
        row = conn.execute(
            "SELECT COUNT(*) FROM notifications WHERE recipient_id=? AND is_read=0",
            (user_id,),
        ).fetchone()
        return int(row[0])

    def mark_read(self, notif_id: int) -> None:
        conn = get_connection()
        conn.execute("UPDATE notifications SET is_read=1 WHERE id=?", (notif_id,))
        conn.commit()

    def mark_all_read(self, user_id: str) -> None:
        conn = get_connection()
        conn.execute(
            "UPDATE notifications SET is_read=1 WHERE recipient_id=?", (user_id,)
        )
        conn.commit()

    def create(self, sender_id: str, sender_name: str,
               recipient_id: str, title: str, message: str) -> None:
        conn = get_connection()
        conn.execute(
            """INSERT INTO notifications
               (sender_id, sender_name, recipient_id, title, message)
               VALUES (?,?,?,?,?)""",
            (sender_id, sender_name, recipient_id, title, message),
        )
        conn.commit()

    def delete(self, notif_id: int) -> None:
        conn = get_connection()
        conn.execute("DELETE FROM notifications WHERE id=?", (notif_id,))
        conn.commit()
