"""SQLite-backed user repository."""
from __future__ import annotations
import sqlite3
from models.user import User
from database.sqlite_db import get_connection


def _row_to_user(row: sqlite3.Row) -> User:
    return User(
        user_id=row["id"],
        username=row["username"],
        full_name=row["full_name"],
        role=row["role"],
        email=row["email"],
        phone=row["phone"],
        password_hash=row["password_hash"],
        status=row["status"],
    )


class UserDAO:
    def __init__(self) -> None:
        # Ensures DB file + schema + seed exist
        get_connection()

    def list_all(self) -> list[User]:
        conn = get_connection()
        rows = conn.execute(
            "SELECT * FROM users WHERE status != 'Da xoa' ORDER BY id"
        ).fetchall()
        return [_row_to_user(r) for r in rows]

    def search(self, keyword: str = "",
               role: str = "", status: str = "") -> list[User]:
        """SQL-level search to avoid loading the whole users table."""
        clauses = ["status != 'Da xoa'"]
        params: list[object] = []
        if keyword:
            kw = f"%{keyword}%"
            clauses.append(
                "(username LIKE ? OR full_name LIKE ? OR email LIKE ? OR role LIKE ?)")
            params.extend([kw, kw, kw, kw])
        if role:
            clauses.append("role = ?")
            params.append(role)
        if status:
            clauses.append("status = ?")
            params.append(status)
        where = "WHERE " + " AND ".join(clauses)
        conn = get_connection()
        rows = conn.execute(
            f"SELECT * FROM users {where} ORDER BY id", params
        ).fetchall()
        return [_row_to_user(r) for r in rows]

    def find_by_id(self, user_id: str) -> User | None:
        conn = get_connection()
        row = conn.execute("SELECT * FROM users WHERE id=?", (user_id,)).fetchone()
        return _row_to_user(row) if row else None

    def find_by_username(self, username: str) -> User | None:
        conn = get_connection()
        row = conn.execute("SELECT * FROM users WHERE username=?", (username,)).fetchone()
        return _row_to_user(row) if row else None

    def find_by_email(self, email: str) -> User | None:
        conn = get_connection()
        row = conn.execute(
            "SELECT * FROM users WHERE lower(email)=lower(?)", (email,)
        ).fetchone()
        return _row_to_user(row) if row else None

    def count_active(self) -> int:
        conn = get_connection()
        row = conn.execute(
            "SELECT COUNT(*) FROM users WHERE status != 'Da xoa'"
        ).fetchone()
        return int(row[0]) if row else 0

    def save(self, user: User) -> User:
        conn = get_connection()
        conn.execute(
            """
            INSERT INTO users (id,username,full_name,role,email,phone,password_hash,status)
            VALUES (?,?,?,?,?,?,?,?)
            ON CONFLICT(id) DO UPDATE SET
                username=excluded.username,
                full_name=excluded.full_name,
                role=excluded.role,
                email=excluded.email,
                phone=excluded.phone,
                password_hash=excluded.password_hash,
                status=excluded.status
            """,
            (user.user_id, user.username, user.full_name, user.role,
             user.email, user.phone, user.password_hash, user.status),
        )
        conn.commit()
        return user

    def delete(self, user_id: str) -> None:
        """Soft-delete: mark status as 'Da xoa' instead of hard DELETE."""
        conn = get_connection()
        conn.execute("UPDATE users SET status='Da xoa' WHERE id=?", (user_id,))
        conn.commit()
