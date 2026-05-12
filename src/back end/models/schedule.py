"""Schedule model."""
from __future__ import annotations
from dataclasses import dataclass

@dataclass
class Schedule:
    room_id: str
    weekday: str
    slot: str
    label: str
    status: str
    user_id: str = ""

