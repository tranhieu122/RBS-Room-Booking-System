"""Room model."""
from __future__ import annotations
from dataclasses import dataclass

@dataclass
class Room:
    room_id: str
    name: str
    capacity: int
    room_type: str
    equipment: str
    status: str = "Hoat dong"
