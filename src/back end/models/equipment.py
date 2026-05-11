"""Equipment model."""
from __future__ import annotations
from dataclasses import dataclass

@dataclass
class Equipment:
    equipment_id: str
    name: str
    equipment_type: str
    room_id: str
    status: str
    purchase_date: str
