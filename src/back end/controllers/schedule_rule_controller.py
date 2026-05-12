"""Business logic for weekly recurring schedule rules."""
from __future__ import annotations
import datetime as dt
from dao.schedule_rule_dao import ScheduleRuleDAO
from models.schedule_rule import ScheduleRule, ScheduleOccurrence
from utils.logger import get_logger

_log = get_logger(__name__)
_SLOT_TIME_MAP = {
    "Ca 1": ("07:00", "09:30"),
    "Ca 2": ("09:35", "12:00"),
    "Ca 3": ("13:00", "15:30"),
    "Ca 4": ("15:35", "18:00"),
    "Ca 5": ("18:15", "20:45"),
}

# ISO weekday labels (1=Mon … 7=Sun)
WEEKDAY_LABELS: dict[int, str] = {
    1: "Thứ 2", 2: "Thứ 3", 3: "Thứ 4",
    4: "Thứ 5", 5: "Thứ 6", 6: "Thứ 7", 7: "Chủ nhật",
}

SLOT_TIME_RANGES = [
    ("07:00", "09:30"),
    ("09:35", "12:00"),
    ("13:00", "15:30"),
    ("15:35", "18:00"),
    ("18:15", "20:45"),
]

VALID_STATUSES = {"Cho duyet", "Hoat dong", "Da xong", "Huy"}


class ScheduleRuleController:
    def __init__(self) -> None:
        self.dao = ScheduleRuleDAO()

    # ── Queries ───────────────────────────────────────────────────────────────

    def list_rules(self, status: str = "") -> list[ScheduleRule]:
        rules = self.dao.list_all()
        if status:
            rules = [r for r in rules if r.status == status]
        return rules

    def get_rule(self, rule_id: int) -> ScheduleRule | None:
        return self.dao.find_by_id(rule_id)

    def list_occurrences(self, rule_id: int) -> list[ScheduleOccurrence]:
        return self.dao.list_occurrences(rule_id)

    def count_occurrences(self, rule_id: int) -> int:
        return self.dao.count_occurrences(rule_id)

    def list_occurrences_in_range(
        self, date_from: str, date_to: str
    ) -> list[ScheduleOccurrence]:
        return self.dao.list_occurrences_by_date_range(date_from, date_to)

    # ── Create ────────────────────────────────────────────────────────────────

    def create_rule(self, payload: dict) -> ScheduleRule: # type: ignore
        """Validate, save a ScheduleRule, then auto-generate all occurrences."""
        subject = payload.get("subject", "").strip() # type: ignore
        if not subject:
            raise ValueError("Ten mon hoc / ten buoi day khong duoc de trong.")

        days_of_week: list[int] = list(payload.get("days_of_week", [])) # type: ignore
        if not days_of_week:
            raise ValueError("Phai chon it nhat mot thu trong tuan.")
        invalid = [d for d in days_of_week if d not in range(1, 8)]
        if invalid:
            raise ValueError(f"Gia tri thu khong hop le: {invalid}")

        start_time: str = payload.get("start_time", "").strip() # type: ignore
        end_time: str   = payload.get("end_time", "").strip() # type: ignore
        if not start_time or not end_time:
            raise ValueError("Phai nhap gio bat dau va gio ket thuc.")
        try:
            t_start = dt.time.fromisoformat(start_time) # type: ignore
            t_end   = dt.time.fromisoformat(end_time) # type: ignore
        except ValueError:
            raise ValueError("Dinh dang gio phai la HH:MM.")
        if t_start >= t_end:
            raise ValueError("Gio bat dau phai truoc gio ket thuc.")

        start_date: str = payload.get("start_date", "").strip() # type: ignore
        end_date:   str = payload.get("end_date", "").strip() # type: ignore
        try:
            d_start = dt.date.fromisoformat(start_date) # type: ignore
            d_end   = dt.date.fromisoformat(end_date) # type: ignore
        except ValueError:
            raise ValueError("Ngay bat dau / ket thuc phai theo dinh dang YYYY-MM-DD.")
        if d_start > d_end:
            raise ValueError("Ngay bat dau phai truoc hoac bang ngay ket thuc.")
        if (d_end - d_start).days > 365 * 3:
            raise ValueError("Khoang thoi gian khong duoc vuot qua 3 nam.")

        room_id: str      = payload.get("room_id", "").strip() # type: ignore
        lecturer_id: str  = payload.get("lecturer_id", "").strip() # type: ignore
        if not room_id:
            raise ValueError("Phai chon phong hoc.")
        if not lecturer_id:
            raise ValueError("Phai nhap ma giang vien.")

        lecturer_name: str = payload.get("lecturer_name", "").strip() # type: ignore

        rule = ScheduleRule(
            subject=subject, # type: ignore
            days_of_week=sorted(days_of_week),
            start_time=start_time, # type: ignore
            end_time=end_time, # type: ignore
            start_date=start_date, # type: ignore
            end_date=end_date, # type: ignore
            room_id=room_id, # type: ignore
            lecturer_id=lecturer_id, # type: ignore
            lecturer_name=lecturer_name, # type: ignore
            status=payload.get("status", "Cho duyet"),
        )
        
        # ── CONFLICT CHECK ────────────────────────────────────────────────────
        occurrences = self._generate_occurrences(rule)
        self._check_conflicts(rule, occurrences)
        # ── END CONFLICT CHECK ────────────────────────────────────────────────
        
        rule = self.dao.save(rule)
        # Reuse generated occurrences
        for occ in occurrences: occ.rule_id = rule.rule_id
        self.dao.insert_occurrences(occurrences)
        _log.info(
            "ScheduleRule #%d created — %d occurrences generated",
            rule.rule_id, len(occurrences),
        )
        return rule

    # ── Update status ─────────────────────────────────────────────────────────

    def update_rule_status(self, rule_id: int, status: str) -> None:
        if status not in VALID_STATUSES:
            raise ValueError(f"Trang thai khong hop le: {status}")
            
        # LOGIC FIX: Re-check conflicts when activating a rule
        if status == "Hoat dong":
            rule = self.get_rule(rule_id)
            if rule:
                occs = self._generate_occurrences(rule)
                self._check_conflicts(rule, occs)
                
        self.dao.update_status(rule_id, status)

    def update_occurrence_status(self, occ_id: int, status: str) -> None:
        valid = {"Du kien", "Da dien ra", "Huy"}
        if status not in valid:
            raise ValueError(f"Trang thai buoi hoc khong hop le: {status}")
        self.dao.update_occurrence_status(occ_id, status)

    # ── Delete ────────────────────────────────────────────────────────────────

    def delete_rule(self, rule_id: int) -> None:
        self.dao.delete(rule_id)
        _log.info("ScheduleRule #%d deleted (with all occurrences)", rule_id)

    # ── Occurrence generation ─────────────────────────────────────────────────

    @staticmethod
    def _generate_occurrences(rule: ScheduleRule) -> list[ScheduleOccurrence]:
        """Expand a ScheduleRule into concrete daily occurrences."""
        d_start = dt.date.fromisoformat(rule.start_date)
        d_end   = dt.date.fromisoformat(rule.end_date)
        target_days = set(rule.days_of_week)
        occurrences: list[ScheduleOccurrence] = []

        current = d_start
        while current <= d_end:
            iso_wd = current.isoweekday()  # 1=Mon … 7=Sun
            if iso_wd in target_days:
                occurrences.append(ScheduleOccurrence(
                    rule_id=rule.rule_id,
                    occurrence_date=current.isoformat(),
                    day_of_week=iso_wd,
                    subject=rule.subject,
                    start_time=rule.start_time,
                    end_time=rule.end_time,
                    room_id=rule.room_id,
                    lecturer_name=rule.lecturer_name,
                    status="Du kien",
                ))
            current += dt.timedelta(days=1)
        return occurrences

    def _check_conflicts(self, rule: ScheduleRule, occurrences: list[ScheduleOccurrence]) -> None:
        """Centralized conflict checking for recurring rules vs bookings and other rules."""
        from dao.booking_dao import BookingDAO
        booking_dao = BookingDAO()
        
        # 1. Check against one-off bookings
        _SLOT_START_MAP = {
            "07:00": "Ca 1", "09:35": "Ca 2",
            "13:00": "Ca 3", "15:35": "Ca 4",
            "18:15": "Ca 5",
        }
        
        for occ in occurrences:
            slot = _SLOT_START_MAP.get(occ.start_time)
            if slot:
                existing = booking_dao.search(
                    room_id=occ.room_id, date_from=occ.occurrence_date, 
                    date_to=occ.occurrence_date
                )
                conflicts = [b for b in existing if b.slot == slot and b.status == "Da duyet"]
                if conflicts:
                    raise ValueError(
                        f"Xung dot: Ngay {occ.occurrence_date} tai phong {occ.room_id} "
                        f"da co lich dat truoc '{conflicts[0].purpose}'."
                    )

        # 2. Check against other recurring rules in the same range
        range_occs = self.dao.list_occurrences_by_date_range(rule.start_date, rule.end_date)
        for ro in range_occs:
            # Skip itself
            if ro["rule_id"] == rule.rule_id:
                continue
            if ro["room_id"] == rule.room_id and ro["status"] != "Huy":
                if ro["start_time"] == rule.start_time:
                    d_obj = dt.date.fromisoformat(ro["occurrence_date"])
                    if d_obj.isoweekday() in rule.days_of_week:
                        raise ValueError(
                            f"Xung dot: Ngay {ro['occurrence_date']} da co lich chu ky khac "
                            f"'{ro['subject']}' tai phong {rule.room_id}."
                        )

    # ── Helpers ───────────────────────────────────────────────────────────────

    @staticmethod
    def days_label(days_of_week: list[int]) -> str:
        """Return human-readable day list, e.g. 'T2, T4, T6'."""
        short = {1: "T2", 2: "T3", 3: "T4", 4: "T5", 5: "T6", 6: "T7", 7: "CN"}
        return ", ".join(short.get(d, str(d)) for d in sorted(days_of_week))
