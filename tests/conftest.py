"""Shared pytest fixtures and configuration."""
from __future__ import annotations
import os
import sys
import pytest

# Point all tests at an isolated in-memory SQLite DB
os.environ["DB_PATH"] = ":memory:"

# Make sure back-end code is importable
_backend = os.path.join(os.path.dirname(__file__), "..", "src", "back end")
if _backend not in sys.path:
    sys.path.insert(0, _backend)


@pytest.fixture(autouse=True)
def fresh_database():
    """Give each test a clean in-memory database."""
    from database.sqlite_db import reset_connection

    reset_connection()
    yield
    reset_connection()
