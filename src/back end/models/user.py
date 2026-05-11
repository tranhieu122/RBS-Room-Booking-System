"""User model."""
from __future__ import annotations
from dataclasses import dataclass

@dataclass
class User:
    user_id: str
    username: str
    full_name: str
    role: str
    email: str
    phone: str
    password_hash: str
    status: str = "Hoat dong"
