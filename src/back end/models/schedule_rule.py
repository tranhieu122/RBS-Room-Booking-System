"""ScheduleRule model – weekly recurring schedule template."""
from __future__ import annotations
from dataclasses import dataclass, field


@dataclass
class ScheduleRule:
    """One weekly-recurrence rule (schedule template)."""
    subject: str          # Mon hoc / Ten buoi day
    days_of_week: list[int]  # 1=T2 .. 6=T7, 7=CN  (ISO weekday)
    start_time: str       # "HH:MM"
    end_time: str         # "HH:MM"
    start_date: str       # "YYYY-MM-DD"
    end_date: str         # "YYYY-MM-DD"
    room_id: str          # e.g. "A101"
    lecturer_id: str      # user id of lecturer
    lecturer_name: str = ""
    status: str = "Hoat dong"   # Hoat dong / Da xong / Huy
    rule_id: int = 0      # 0 means not yet saved
    created_at: str = ""


@dataclass
class ScheduleOccurrence:
    """One generated occurrence from a ScheduleRule."""
    rule_id: int
    occurrence_date: str  # "YYYY-MM-DD"
    day_of_week: int      # 1-7
    subject: str
    start_time: str
    end_time: str
    room_id: str
    lecturer_name: str
    status: str = "Du kien"  # Du kien / Da dien ra / Huy
    occ_id: int = 0
