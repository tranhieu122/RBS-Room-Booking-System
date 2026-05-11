"""Booking model."""
from __future__ import annotations
from dataclasses import dataclass, field

@dataclass
class Booking:
    booking_id: str
    user_id: str
    user_name: str
    room_id: str
    booking_date: str
    slot: str
    purpose: str
    status: str = "Cho duyet"
    rejection_reason: str = ""
