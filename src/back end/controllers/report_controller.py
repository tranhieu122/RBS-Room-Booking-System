"""Reporting and statistics logic."""
from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from controllers.booking_controller import BookingController
    from controllers.room_controller import RoomController
    from controllers.user_controller import UserController
    from controllers.equipment_controller import EquipmentController


class ReportController:
    def __init__(
        self,
        room_controller: "RoomController",
        booking_controller: "BookingController",
        user_controller: "UserController",
        equipment_controller: "EquipmentController",
    ) -> None:
        self.room_ctrl    = room_controller
        self.booking_ctrl = booking_controller
        self.user_ctrl    = user_controller
        self.equip_ctrl   = equipment_controller

    # ── Dashboard overview ────────────────────────────────────────────────────

    def build_dashboard(self, date_from: str = "",
                        date_to: str = "") -> dict[str, int]:
        if date_from or date_to:
            bookings = self.booking_ctrl.list_bookings(
                from_today=False, date_from=date_from, date_to=date_to)
            total_bookings = len(bookings)
            pending = sum(1 for b in bookings if b.status == "Cho duyet")
            rejected = sum(1 for b in bookings if b.status == "Tu choi")
        else:
            stats = self.booking_ctrl.booking_stats()
            total_bookings = stats["total"]
            pending = stats["Cho duyet"]
            rejected = stats["Tu choi"]
        return {
            "Tong phong":     self.room_ctrl.room_dao.count_active(),
            "Tong dat phong": total_bookings,
            "Cho duyet":      pending,
            "Tu choi":        rejected,
            "Nguoi dung":     self.user_ctrl.user_dao.count_active(),
            "Thiet bi":       self.equip_ctrl.equipment_dao.count_all(),
        }

    # ── Room usage ────────────────────────────────────────────────────────────

    def room_usage_rows(self, date_from: str = "", date_to: str = "") -> list[tuple[str, int]]:
        bookings = self.booking_ctrl.list_bookings(
            from_today=False, date_from=date_from, date_to=date_to)
        
        counter: dict[str, int] = {}
        for b in bookings:
            if b.status in ("Da duyet", "Hoat dong"):
                counter[b.room_id] = counter.get(b.room_id, 0) + 1
                
        return [(r.room_id, counter.get(r.room_id, 0))
                for r in self.room_ctrl.list_rooms()]

    def room_stats_table(self, date_from: str = "",
                         date_to: str = "") -> list[tuple[str, int, int, int, str]]:
        """Return per-room stats: (room_id, total, approved, rejected, rate_pct)."""
        bookings = self.booking_ctrl.list_bookings(
            from_today=False, date_from=date_from, date_to=date_to)
        
        # stats maps room_id -> {status -> count}
        stats: dict[str, dict[str, int]] = {}
        for b in bookings:
            stats.setdefault(b.room_id, {})
            stats[b.room_id][b.status] = stats[b.room_id].get(b.status, 0) + 1
            
        result: list[tuple[str, int, int, int, str]] = []
        for r in self.room_ctrl.list_rooms():
            s = stats.get(r.room_id, {})
            total = sum(s.values())
            # Map rule statuses to approved/rejected equivalents
            approved = s.get("Da duyet", 0) + s.get("Hoat dong", 0)
            rejected = s.get("Tu choi", 0) + s.get("Huy", 0)
            rate = f"{int(approved / total * 100)}%" if total > 0 else "0%"
            result.append((r.room_id, total, approved, rejected, rate))
        return [row for row in result if row[1] > 0]

    def top_rooms(self, n: int = 5) -> list[tuple[str, int]]:
        """Return the *n* rooms with the most bookings: [(room_id, count), ...]."""
        usage = self.room_usage_rows()
        return sorted(usage, key=lambda x: x[1], reverse=True)[:n]

    # ── Time-series / trend ───────────────────────────────────────────────────

    def daily_booking_trend(self, days: int = 14) -> list[tuple[str, int]]:
        """Delegate to BookingController for the last *days* days trend."""
        return self.booking_ctrl.daily_booking_trend(days)

    def monthly_booking_counts(self) -> list[tuple[str, int]]:
        """Return (YYYY-MM, count) sorted ascending for the past 12 months."""
        from datetime import date, timedelta # type: ignore
        today = date.today()
        months = []
        for i in range(11, -1, -1):
            # Calculate approx first day of each month
            m = today.month - i
            y = today.year
            while m <= 0:
                m += 12
                y -= 1
            months.append(f"{y:04d}-{m:02d}") # type: ignore

        stored_counts = self.booking_ctrl.booking_dao.count_by_month_prefixes(months)
        counts: dict[str, int] = {
            m: stored_counts.get(m, 0) for m in months
        } # type: ignore
        return [(m, counts[m]) for m in months] # type: ignore

    # ── Slot / user analytics ─────────────────────────────────────────────────

    def slot_distribution(self) -> dict[str, int]:
        """Return booking counts per slot."""
        return self.booking_ctrl.slot_usage_stats()

    def status_distribution(self) -> dict[str, int]:
        """Return booking counts per status."""
        stats = self.booking_ctrl.booking_stats()
        return {
            "Cho duyet": stats["Cho duyet"],
            "Da duyet":  stats["Da duyet"],
            "Tu choi":   stats["Tu choi"],
        }

    def top_users(self, n: int = 5) -> list[tuple[str, str, int]]:
        """Return [(user_id, full_name, booking_count)] sorted by most bookings."""
        return self.booking_ctrl.booking_dao.top_users(n)
