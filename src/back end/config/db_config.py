"""Database configuration."""
from __future__ import annotations
import os
from dataclasses import dataclass

@dataclass(frozen=True)
class DatabaseConfig:
    host: str = os.getenv("DB_HOST", "127.0.0.1")
    port: int = int(os.getenv("DB_PORT", "3306"))
    user: str = os.getenv("DB_USER", "root")
    password: str = os.getenv("DB_PASSWORD", "")
    database: str = os.getenv("DB_NAME", "classroom_booking")

    def as_dict(self) -> dict[str, str | int]:
        return {"host": self.host, "port": self.port, "user": self.user,
                "password": self.password, "database": self.database}

def get_database_config() -> DatabaseConfig:
    return DatabaseConfig()
