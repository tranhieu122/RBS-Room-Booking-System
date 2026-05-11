"""Legacy stub — ứng dụng đã chuyển sang SQLite (database/sqlite_db.py).

File này giữ lại để tránh lỗi nếu có code cũ import DatabaseConnection.
Không cần MySQL / mysql-connector-python.
"""
from __future__ import annotations
from database.sqlite_db import get_connection as _get_sqlite


class DatabaseConnection:
    """Stub forwards sang SQLite connection để không vỡ import cũ."""
    _instance: "DatabaseConnection | None" = None

    def __new__(cls) -> "DatabaseConnection":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def connect(self):
        return _get_sqlite()

    def close(self) -> None:
        pass  # SQLite connection được quản lý bởi sqlite_db.py
