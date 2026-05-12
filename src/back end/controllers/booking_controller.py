"""Booking business logic and conflict checks."""
from __future__ import annotations
import datetime as dt
import threading
import uuid
from typing import Any
from dao.booking_dao import BookingDAO
from dao.user_dao import UserDAO
from models.booking import Booking
from models.schedule import Schedule
from models.user import User
from utils.email_notifier import send_booking_notification
from utils.logger import get_logger

_log = get_logger(__name__)
_SLOT_TIME_MAP = {
    "Ca 1": ("07:00", "09:30"),
    "Ca 2": ("09:35", "12:00"),
    "Ca 3": ("13:00", "15:30"),
    "Ca 4": ("15:35", "18:00"),
    "Ca 5": ("18:15", "20:45"),
}
_SLOT_START_MAP = {time_range[0]: slot for slot, time_range in _SLOT_TIME_MAP.items()}


class BookingController:
    SLOT_OPTIONS = ["Ca 1", "Ca 2", "Ca 3", "Ca 4", "Ca 5"]
    WEEKDAY_LABELS = {0: "Thứ 2", 1: "Thứ 3", 2: "Thứ 4",
                      3: "Thứ 5", 4: "Thứ 6", 5: "Thứ 7", 6: "Chủ nhật"}
    VALID_STATUSES = {"Cho duyet", "Da duyet", "Tu choi", "Da huy"}

    def __init__(self) -> None:
        self.booking_dao = BookingDAO()

    # ── Queries ───────────────────────────────────────────────────────────────

    def get_booking(self, booking_id: str) -> Booking | None:
        """Return a single booking by ID, or None if not found."""
        if isinstance(booking_id, str) and booking_id.startswith("RULE-"):
            try:
                rule_id = int(booking_id.replace("RULE-", ""))
                from dao.schedule_rule_dao import ScheduleRuleDAO
                r = ScheduleRuleDAO().find_by_id(rule_id)
                if r:
                    return Booking(
                        booking_id=f"RULE-{r.rule_id}",
                        user_id=r.lecturer_id,
                        user_name=r.lecturer_name,
                        room_id=r.room_id,
                        booking_date=f"{r.start_date} -> {r.end_date}",
                        slot=f"Thứ {r.days_of_week}",
                        purpose=f"[Lịch Chu Kỳ] {r.subject}",
                        status=r.status
                    )
            except Exception:
                pass
        return self.booking_dao.find_by_id(booking_id)

    def list_bookings(self, current_user: User | None = None,
                      status: str = "", room_id: str = "", date_text: str = "",
                      from_today: bool = True,
                      date_from: str = "", date_to: str = "",
                      keyword: str = "",
                      page: int = 0, page_size: int = 0,
                      user_id: str = "") -> list[Booking]:
        """Return filtered bookings using SQL-level filtering for performance."""
        uid = user_id
        if not uid and current_user is not None and current_user.role != "Admin":
            uid = current_user.user_id

        bookings = self.booking_dao.search(
            user_id=uid,
            status=status,
            room_id=room_id,
            date_from=date_text or date_from,
            date_to=date_to,
            keyword=keyword,
            from_today=from_today,
        )
        
        # 2. Include relevant schedule rules
        try:
            from dao.schedule_rule_dao import ScheduleRuleDAO
            rule_dao = ScheduleRuleDAO()
            
            # If user_id is specified, get rules for that user.
            # If no user_id, and either it's an Admin or no specific user context is provided (like Reports), include ALL rules.
            rules_to_include = []
            rule_status = ""
            if status:
                s_map = {"Da duyet": "Hoat dong", "Tu choi": "Huy", "Cho duyet": "Cho duyet"}
                rule_status = s_map.get(status, status)
            
            filter_start = date_text or date_from
            filter_end = date_text or date_to
            
            if user_id:
                rules_to_include = rule_dao.search(
                    lecturer_id=user_id,
                    room_id=room_id,
                    status=rule_status,
                    date_from=filter_start,
                    date_to=filter_end,
                    keyword=keyword,
                )
            else:
                # If no user_id filter, we include rules if:
                # 1. current_user is Admin
                # 2. current_user is None (internal call from ReportController)
                if current_user is None or current_user.role == "Admin":
                    rules_to_include = rule_dao.search(
                        room_id=room_id,
                        status=rule_status,
                        date_from=filter_start,
                        date_to=filter_end,
                        keyword=keyword,
                    )
            
            for r in rules_to_include:
                # Format days for display: [1, 3] -> "T2, T4"
                short_days = {1: "T2", 2: "T3", 3: "T4", 4: "T5", 5: "T6", 6: "T7", 7: "CN"}
                days_label = ", ".join(short_days.get(d, str(d)) for d in sorted(r.days_of_week))
                
                # Convert Rule to a 'Booking-like' object for display
                b_rule = Booking(
                    booking_id=f"RULE-{r.rule_id}",
                    user_id=r.lecturer_id,
                    user_name=r.lecturer_name,
                    room_id=r.room_id,
                    booking_date=f"{r.start_date} ~ {r.end_date}",
                    slot=days_label,
                    purpose=f"[CK] {r.subject}",
                    status=r.status
                )
                bookings.append(b_rule)
        except Exception as e:
            _log.error("Error including schedule rules in list_bookings: %s", e)

        if page_size > 0:
            start = page * page_size
            bookings = bookings[start: start + page_size]
        return bookings

    def count_bookings(self, current_user: User | None = None,
                       status: str = "", room_id: str = "",
                       from_today: bool = True) -> int:
        """Count bookings matching the same filters (without pagination)."""
        return len(self.list_bookings(current_user=current_user, status=status,
                                      room_id=room_id, from_today=from_today,
                                      page=0, page_size=0))

    def _used_slots(
        self,
        room_id: str,
        booking_date: str,
        booking_statuses: set[str],
        exclude_booking_id: str = "",
    ) -> set[str]:
        used = {
            b.slot for b in self.booking_dao.search(
                room_id=room_id, date_from=booking_date, date_to=booking_date
            )
            if b.status in booking_statuses and b.booking_id != exclude_booking_id
        }

        try:
            from dao.schedule_rule_dao import ScheduleRuleDAO

            occs = ScheduleRuleDAO().list_occurrences_by_date_range(booking_date, booking_date)
            for o in occs:
                if (
                    o["room_id"] == room_id
                    and o["status"] != "Huy"
                    and o.get("rule_status") != "Huy"
                ):
                    slot = _SLOT_START_MAP.get(o["start_time"])
                    if slot:
                        used.add(slot)
        except Exception:
            pass
        return used

    def available_slots(self, room_id: str, booking_date: str) -> list[str]:
        used = self._used_slots(room_id, booking_date, {"Cho duyet", "Da duyet"})
        return [s for s in self.SLOT_OPTIONS if s not in used]

    def used_slots_by_room(self, booking_date: str) -> dict[str, set[str]]:
        used = self.booking_dao.used_slots_by_room(
            booking_date, {"Cho duyet", "Da duyet"}
        )
        try:
            from dao.schedule_rule_dao import ScheduleRuleDAO

            for room_id, slots in ScheduleRuleDAO().used_slots_by_room(booking_date).items():
                used.setdefault(room_id, set()).update(slots)
        except Exception:
            pass
        return used

    def approve_booking(self, booking_id: str) -> Booking:
        """Shortcut to approve a booking (Admin action)."""
        return self.update_status(booking_id, "Da duyet")

    def reject_booking(self, booking_id: str, reason: str = "") -> Booking:
        """Shortcut to reject a booking."""
        booking = self.booking_dao.find_by_id(booking_id)
        if booking is None:
            raise ValueError("Khong tim thay yeu cau dat phong.")
        booking.status = "Tu choi"
        if reason:
            booking.rejection_reason = reason
        saved = self.booking_dao.save(booking)
        self._fire_email(saved, "Tu choi")
        return saved

    # ── Create / Edit / Delete ────────────────────────────────────────────────

    MAX_ADVANCE_DAYS = 30  # Cannot book more than 30 days in the future

    def create_booking(self, user: User, room_id: str, booking_date: str,
                       slot: str, purpose: str) -> Booking:
        try:
            parsed_booking_date = (
                booking_date
                if isinstance(booking_date, dt.date)
                else dt.date.fromisoformat(booking_date)
            )
        except (TypeError, ValueError):
            parsed_booking_date = None
        if parsed_booking_date is not None and parsed_booking_date < dt.date.today() and user.role != "Admin":
            raise ValueError("Khong the dat phong cho ngay da qua.")

        # Robust date parsing
        try:
            if isinstance(booking_date, dt.date):
                dt_obj = booking_date
            else:
                # Try common formats if isoformat fails
                try:
                    dt_obj = dt.date.fromisoformat(booking_date)
                except ValueError:
                    # Try dd/mm/yyyy
                    dt_obj = dt.datetime.strptime(booking_date, "%d/%m/%Y").date()
            booking_date = dt_obj.isoformat()
        except Exception:
            raise ValueError(f"Ngày đặt phòng '{booking_date}' không đúng định dạng (Y-M-D hoặc D/M/Y).")

        if dt_obj < dt.date.today() and user.role != "Admin":
            raise ValueError("Khong the dat phong cho ngay da qua.")

        if (dt_obj - dt.date.today()).days > self.MAX_ADVANCE_DAYS:
            raise ValueError(
                f"Chi duoc dat phong trong vong {self.MAX_ADVANCE_DAYS} ngay toi "
                f"(muon nhat: {(dt.date.today() + dt.timedelta(days=self.MAX_ADVANCE_DAYS)).isoformat()})."
            )
            
        if slot not in self.SLOT_OPTIONS:
            raise ValueError("Ca hoc khong hop le.")

        if not purpose.strip():
            raise ValueError("Mục đích đặt phòng không được để trống.")

        # Verify room is active
        from dao.room_dao import RoomDAO
        room_obj = RoomDAO().find_by_id(room_id)
        if room_obj is None:
            raise ValueError("Phòng không tồn tại.")
        if room_obj.status != "Hoạt động" and room_obj.status != "Hoat dong":
            raise ValueError(f"Phòng '{room_id}' hiện không khả dụng (trạng thái: {room_obj.status}).")

        # Conflict check
        if slot not in self.available_slots(room_id, booking_date):
            raise ValueError(f"Phòng {room_id} đã có lịch trong ca {slot} ngày {booking_date}.")

        new_id = "B" + uuid.uuid4().hex[:8].upper()
        booking = Booking(
            booking_id=new_id, user_id=user.user_id, user_name=user.full_name,
            room_id=room_id, booking_date=booking_date, slot=slot,
            purpose=purpose.strip(),
            status="Da duyet" if user.role == "Admin" else "Cho duyet",
        )
        
        saved = self.booking_dao.save(booking)
        _log.info("Successfully saved booking %s", saved.booking_id)
        
        if saved.status == "Da duyet":
            self._fire_email(saved, "Da duyet")
        return saved

    def update_status(self, booking_id: str, new_status: str) -> Booking:
        if new_status not in self.VALID_STATUSES:
            raise ValueError(f"Trang thai '{new_status}' khong hop le.")
        booking = self.booking_dao.find_by_id(booking_id)
        if booking is None:
            raise ValueError("Khong tim thay yeu cau dat phong.")
        old_status = booking.status
        
        # LOGIC FIX: Re-check conflicts when approving, in case another booking/rule was approved/activated
        if new_status == "Da duyet" and old_status != "Da duyet":
            used_slots = self._used_slots(
                booking.room_id,
                booking.booking_date,
                {"Da duyet"},
                exclude_booking_id=booking_id,
            )

            if booking.slot in used_slots:
                raise ValueError(f"Khong the duyet: Phong '{booking.room_id}' da co lich chinh thuc trong ca nay.")

        booking.status = new_status
        saved = self.booking_dao.save(booking)
        _log.info("Booking %s status %s → %s", booking_id, old_status, new_status)

        if new_status in ("Da duyet", "Tu choi"):
            self._fire_email(saved, new_status)
        return saved

    def _fire_email(self, booking: Booking, status: str) -> None:
        """Send email notification in a background thread (non-blocking)."""
        try:
            user = UserDAO().find_by_id(booking.user_id)
            email = getattr(user, "email", "") if user else ""
        except Exception:
            email = ""
        if email:
            threading.Thread(
                target=send_booking_notification,
                args=(email, booking.user_name, booking.booking_id,
                      booking.room_id, booking.booking_date,
                      booking.slot, status),
                daemon=True,
            ).start()

    def update_booking(self, booking_id: str, current_user: User, room_id: str,
                       booking_date: str, slot: str, purpose: str) -> Booking:
        """Edit booking fields. Owner or Admin only."""
        booking = self.booking_dao.find_by_id(booking_id)
        if booking is None:
            raise ValueError("Khong tim thay yeu cau dat phong.")
        if current_user.role != "Admin" and booking.user_id != current_user.user_id:
            raise PermissionError("Ban khong co quyen sua lich nay.")
        try:
            update_dt = dt.date.fromisoformat(booking_date)
        except ValueError:
            raise ValueError("Ngay dat phong phai theo dinh dang YYYY-MM-DD.")
        if update_dt < dt.date.today() and current_user.role != "Admin":
            raise ValueError("Khong the dat phong cho ngay da qua.")
        if slot not in self.SLOT_OPTIONS:
            raise ValueError("Ca hoc khong hop le.")
        if not purpose.strip():
            raise ValueError("Muc dich dat phong khong duoc de trong.")
        # Check conflict, excluding current booking
        used = self._used_slots(
            room_id,
            booking_date,
            {"Cho duyet", "Da duyet"},
            exclude_booking_id=booking_id,
        )
        if slot in used:
            raise ValueError("Phong da co lich trong ca hoc nay.")
        booking.room_id = room_id
        booking.booking_date = booking_date
        booking.slot = slot
        booking.purpose = purpose.strip()
        # Reset status to pending if not admin
        if current_user.role != "Admin":
            booking.status = "Cho duyet"
        saved = self.booking_dao.save(booking)
        _log.info("Booking %s updated by %s", booking_id, current_user.user_id)
        return saved

    def cancel_booking(self, booking_id: str, current_user: User) -> Booking:
        """Cancel a booking if it's still pending. Owner only."""
        booking = self.booking_dao.find_by_id(booking_id)
        if booking is None:
            raise ValueError("Khong tim thay yeu cau dat phong.")
        if booking.user_id != current_user.user_id:
            raise PermissionError("Ban chi co the huy lich dat cua chinh minh.")
        if booking.status != "Cho duyet":
            raise ValueError("Chi co the huy lich khi dang o trang thai 'Cho duyet'.")
        
        booking.status = "Da huy"
        saved = self.booking_dao.save(booking)
        _log.info("Booking %s cancelled by user %s", booking_id, current_user.user_id)
        return saved

    def create_recurring_booking(self,
                                user: User,
                                room_id: str,
                                initial_date: str,
                                slot: str,
                                days_of_week: list[int],  # [0, 2, 4] for Mon, Wed, Fri
                                end_date: str = "",
                                num_weeks: int = 0,
                                purpose: str = "") -> list[str]:
        """
        Create multiple bookings for a recurring weekly schedule.
        Returns a list of booking IDs created.
        """
        import datetime as dt
        
        booking_ids = []
        try:
            current_date = dt.date.fromisoformat(initial_date)
        except ValueError:
            raise ValueError("Ngay bat dau khong hop le.")
            
        # Determine end date
        if num_weeks > 0:
            # e.g. 4 weeks means from now until 28 days later
            end_date_obj = current_date + dt.timedelta(weeks=num_weeks)
        elif end_date:
            try:
                end_date_obj = dt.date.fromisoformat(end_date)
            except ValueError:
                raise ValueError("Ngay ket thuc khong hop le.")
        else:
            raise ValueError("Phai cung cap ngay ket thuc hoặc so tuan lap lai.")
            
        if end_date_obj <= current_date:
            raise ValueError("Ngay ket thuc phai sau ngay bat dau.")
            
        if (end_date_obj - current_date).days > 180: # Max 6 months
            raise ValueError("Thoi gian lap lai toi da la 6 thang.")

        # Iterate through dates
        temp_date = current_date
        while temp_date <= end_date_obj:
            if temp_date.weekday() in days_of_week:
                d_str = temp_date.isoformat()
                # Check availability (including recurring rules)
                if slot in self.available_slots(room_id, d_str):
                    try:
                        # Re-use create_booking for validation and consistency
                        b = self.create_booking(user, room_id, d_str, slot, purpose)
                        booking_ids.append(b.booking_id)
                    except Exception as e:
                        _log.warning("Conflict creating recurring booking for %s: %s", d_str, e)
                else:
                    _log.info("Slot %s for room %s on %s is already occupied, skipping.", slot, room_id, d_str)
            
            temp_date += dt.timedelta(days=1)
            
        if not booking_ids:
            raise ValueError("Khong co ca hoc nao con trong trong khoang thoi gian ban chon.")
            
        return booking_ids

    def delete_booking(self, booking_id: str, current_user: User) -> None:
        """Delete a booking. Owner or Admin only."""
        booking = self.booking_dao.find_by_id(booking_id)
        if booking is None:
            raise ValueError("Khong tim thay yeu cau dat phong.")
        if current_user.role != "Admin" and booking.user_id != current_user.user_id:
            raise PermissionError("Ban khong co quyen xoa lich nay.")
        self.booking_dao.delete(booking_id)
        _log.info("Booking %s deleted by user %s", booking_id, current_user.user_id)

    # ── Analytics / Suggestions ───────────────────────────────────────────────

    def booking_stats(self) -> dict[str, int]:
        """Return counts grouped by status."""
        counts = self.booking_dao.count_by_status()
        return {
            "total":     sum(counts.values()),
            "Cho duyet": counts.get("Cho duyet", 0),
            "Da duyet":  counts.get("Da duyet", 0),
            "Tu choi":   counts.get("Tu choi", 0),
        }

    def daily_booking_trend(self, days: int = 14) -> list[tuple[str, int]]:
        """Return list of (date_str, count) for the last *days* days."""
        today = dt.date.today()
        date_range = [(today - dt.timedelta(days=i)).isoformat()
                      for i in range(days - 1, -1, -1)]
        stored_counts = self.booking_dao.count_by_date_range(date_range[0], date_range[-1])
        counts: dict[str, int] = {d: 0 for d in date_range}
        counts.update({d: stored_counts.get(d, 0) for d in counts})
        return [(d, counts[d]) for d in date_range]

    def slot_usage_stats(self) -> dict[str, int]:
        """Return {slot_name: booking_count} for all time."""
        result = {s: 0 for s in self.SLOT_OPTIONS}
        for slot, count in self.booking_dao.count_by_slot().items():
            if slot in result:
                result[slot] = count
        return result

    def suggest_alternatives(
        self,
        room_id: str,
        booking_date: str,
        slot: str,
        all_room_ids: list[str],
        days_ahead: int = 7,
    ) -> dict[str, list[tuple[str, str]]]:
        """Return two suggestion groups:

        'other_rooms'   – [(room_id, slot)] rooms free on the same date+slot
        'other_slots'   – [(date_str, slot)] free combos for the same room
                           in the next `days_ahead` days (incl. today)
        """
        try:
            base_date = dt.date.fromisoformat(booking_date)
        except ValueError:
            return {"other_rooms": [], "other_slots": []}

        slot_cache: dict[tuple[str, str], list[str]] = {}

        def free_slots(rid: str, date_str: str) -> list[str]:
            key = (rid, date_str)
            if key not in slot_cache:
                slot_cache[key] = self.available_slots(rid, date_str)
            return slot_cache[key]

        other_rooms: list[tuple[str, str]] = []
        for rid in all_room_ids:
            if rid == room_id:
                continue
            if slot in free_slots(rid, booking_date):
                other_rooms.append((rid, slot))

        other_slots: list[tuple[str, str]] = []
        for delta in range(0, days_ahead + 1):
            d = base_date + dt.timedelta(days=delta)
            date_str = d.isoformat()
            free = free_slots(room_id, date_str)
            for s in free:
                if date_str == booking_date and s == slot:
                    continue
                other_slots.append((date_str, s))

        return {"other_rooms": other_rooms, "other_slots": other_slots}

    # ── Schedule ─────────────────────────────────────────────────────────────

    def build_schedule(self, week_offset: int = 0) -> list[Schedule]:
        """Return Schedule rows for the week at *week_offset* from today's week.

        Includes both one-off bookings AND recurring schedule occurrences.
        """
        rows: list[Schedule] = []
        today = dt.date.today()
        week_start = today - dt.timedelta(days=today.weekday()) + dt.timedelta(weeks=week_offset)
        week_end   = week_start + dt.timedelta(days=6)

        # ── One-off bookings ─────────────────────────────────────────────────
        for b in self.booking_dao.search(
            date_from=week_start.isoformat(),
            date_to=week_end.isoformat(),
            from_today=False,
        ):
            try:
                d = dt.date.fromisoformat(b.booking_date)
            except Exception:
                continue
            if not (week_start <= d <= week_end):
                continue
            weekday = self.WEEKDAY_LABELS[d.weekday()]
            rows.append(Schedule(room_id=b.room_id, weekday=weekday,
                                 slot=b.slot,
                                 label=f"{b.room_id} – {b.user_name}",
                                 status=b.status,
                                 user_id=b.user_id,
                                 source_id=b.booking_id))


        # ── Recurring schedule occurrences ───────────────────────────────────
        _SLOT_TIME_MAP = {
            "Ca 1": ("07:00", "09:30"),
            "Ca 2": ("09:35", "12:00"),
            "Ca 3": ("13:00", "15:30"),
            "Ca 4": ("15:35", "18:00"),
            "Ca 5": ("18:15", "20:45"),
        }
        _SLOT_TIME_MAP_INV = {v: k for k, v in _SLOT_TIME_MAP.items()}
        try:
            from dao.schedule_rule_dao import ScheduleRuleDAO
            occ_dao = ScheduleRuleDAO()
            occurrences = occ_dao.list_occurrences_by_date_range(
                week_start.isoformat(), week_end.isoformat()
            )
            for occ in occurrences:
                if occ["status"] == "Huy" or occ.get("rule_status") == "Huy":
                    continue
                try:
                    d = dt.date.fromisoformat(occ["occurrence_date"])
                except Exception:
                    continue
                weekday = self.WEEKDAY_LABELS[d.weekday()]
                # Try exact match first, then fallback to start-time match
                slot = _SLOT_TIME_MAP_INV.get((occ["start_time"], occ["end_time"]))
                if not slot:
                    # Fallback: find Ca based on start time only
                    slot = next((k for k, v in _SLOT_TIME_MAP.items() if v[0] == occ["start_time"]), 
                               f"{occ['start_time']}–{occ['end_time']}")
                name_part = f" ({occ['lecturer_name']})" if occ['lecturer_name'] else ""
                
                # Rule approval logic
                rule_st = occ.get("rule_status", "Hoat dong")
                final_status = "Lich day" if rule_st == "Hoat dong" else rule_st

                rows.append(Schedule(
                    room_id=occ["room_id"],
                    weekday=weekday,
                    slot=slot,
                    label=f"[CK] {occ['subject']}{name_part}",
                    status=final_status,
                    user_id=occ.get("lecturer_id", ""),
                    source_id=f"RULE-{occ['rule_id']}"
                ))

        except Exception:
            pass  # never crash the calendar if occurrence query fails

        return rows

    def week_date_range(self, week_offset: int = 0) -> tuple[dt.date, dt.date]:
        """Return (monday, sunday) for the given week_offset."""
        today = dt.date.today()
        monday = today - dt.timedelta(days=today.weekday()) + dt.timedelta(weeks=week_offset)
        return monday, monday + dt.timedelta(days=6)

    def get_class(self, class_id: str) -> Any:
        """Mock/Wrapper to get class details. 
        In this system, class_id can be a booking_id or rule_id."""
        # Try finding in bookings
        booking = self.booking_dao.find_by_id(class_id)
        if booking:
            # Add time_range for display
            booking.time_range = _SLOT_TIME_MAP.get(booking.slot, ("", ""))[0]
            return booking
        
        # Try finding in schedule_rules
        if class_id.startswith("RULE-"):
            rule_id = class_id.replace("RULE-", "")
            try:
                from dao.schedule_rule_dao import ScheduleRuleDAO
                rule = ScheduleRuleDAO().find_by_id(int(rule_id))
                if rule:
                    # Wrap it in a simple object with common fields
                    class AnyClass: pass
                    c = AnyClass()
                    c.booking_id = class_id
                    c.name = rule.subject
                    c.room_id = rule.room_id
                    c.time_range = f"{rule.start_time}-{rule.end_time}"
                    return c
            except Exception:
                pass
        return None

    def get_enrollment_list(self, class_id: str) -> list[dict]:
        """Return list of students for a class."""
        from database.sqlite_db import get_connection
        conn = get_connection()
        query = """
            SELECT u.id, u.full_name, u.role, u.email, u.phone
            FROM users u
            JOIN class_enrollments ce ON u.id = ce.user_id
            WHERE ce.class_id = ?
        """
        rows = conn.execute(query, (class_id,)).fetchall()
        
        # Format for UI
        students = []
        for i, r in enumerate(rows, 1):
            # Split full name into first/last name for the dialog
            parts = r["full_name"].split()
            last_name = parts[-1] if parts else ""
            first_name = " ".join(parts[:-1]) if len(parts) > 1 else ""
            
            students.append({
                "stt": i,
                "ma_so": r["id"],
                "ho_dem": first_name,
                "ten": last_name,
                "email": r["email"],
                "phone": r["phone"]
            })
        return students


    def check_user_conflict(self, user_id: str, booking_date: str, slot: str) -> Booking | None:
        """Check if a user already has a booking or class at the given time."""
        # 1. Check one-off bookings
        user_bookings = self.booking_dao.search(
            user_id=user_id, date_from=booking_date, date_to=booking_date
        )
        for b in user_bookings:
            if b.slot == slot and b.status in ("Cho duyet", "Da duyet"):
                return b
        
        # 2. Check recurring occurrences
        try:
            from dao.schedule_rule_dao import ScheduleRuleDAO
            occs = ScheduleRuleDAO().list_occurrences_by_date_range(booking_date, booking_date)
            _SLOT_START_MAP = {
                "07:00": "Ca 1", "09:35": "Ca 2",
                "13:00": "Ca 3", "15:35": "Ca 4",
                "18:15": "Ca 5",
            }
            for o in occs:
                if (
                    o.get("lecturer_id") == user_id
                    and o["status"] != "Huy"
                    and o.get("rule_status") != "Huy"
                ):
                    if _SLOT_START_MAP.get(o["start_time"]) == slot:
                        # Wrap in a dummy booking for consistent interface
                        return Booking(
                            booking_id=f"RULE-{o['rule_id']}",
                            user_id=user_id,
                            user_name=o.get("lecturer_name", ""),
                            room_id=o["room_id"],
                            booking_date=booking_date,
                            slot=slot,
                            purpose=o["subject"],
                            status="Da duyet"
                        )
        except Exception:
            pass
            
        return None
