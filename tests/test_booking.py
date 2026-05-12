"""Unit tests for BookingController — validation and filtering."""
from __future__ import annotations
import sys, os
import datetime as dt
import pytest

_ROOT = os.path.join(os.path.dirname(__file__), "..", "src", "back end")
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

os.environ.setdefault("DB_PATH", ":memory:")

from controllers.booking_controller import BookingController
from controllers.auth_controller import AuthController
from controllers.schedule_rule_controller import ScheduleRuleController


# ── Helpers ───────────────────────────────────────────────────────────────────

def _make_user(role: str = "Sinh vien"):
    ctrl = AuthController()
    import uuid
    uname = "bk_" + uuid.uuid4().hex[:6]
    return ctrl.register("Test User", uname, f"{uname}@test.com",
                         "0901234567", "pass1234", role=role)


def _single_day_rule_payload(day: dt.date, **overrides) -> dict:  # type: ignore
    return {
        "subject": "Lap trinh Python",
        "days_of_week": [day.isoweekday()],
        "start_time": "07:00",
        "end_time": "09:00",
        "start_date": day.isoformat(),
        "end_date": day.isoformat(),
        "room_id": "P201",
        "lecturer_id": "GV001",
        "lecturer_name": "Nguyen Van A",
        **overrides,
    }


# ── create_booking validation ─────────────────────────────────────────────────

class TestCreateBookingValidation:
    def test_past_date_rejected(self):
        user = _make_user()
        ctrl = BookingController()
        past = (dt.date.today() - dt.timedelta(days=1)).isoformat()
        with pytest.raises(ValueError, match="da qua"):
            ctrl.create_booking(user, "P101", past, "Ca 1", "Hoc nhom")

    def test_too_far_future_rejected(self):
        user = _make_user()
        ctrl = BookingController()
        far = (dt.date.today() + dt.timedelta(days=60)).isoformat()
        with pytest.raises(ValueError, match="trong vong"):
            ctrl.create_booking(user, "P101", far, "Ca 1", "Hoc nhom")

    def test_invalid_slot_rejected(self):
        user = _make_user()
        ctrl = BookingController()
        tomorrow = (dt.date.today() + dt.timedelta(days=1)).isoformat()
        with pytest.raises(ValueError, match="Ca hoc"):
            ctrl.create_booking(user, "P101", tomorrow, "Ca X", "Hoc nhom")

    def test_empty_purpose_rejected(self):
        user = _make_user()
        ctrl = BookingController()
        tomorrow = (dt.date.today() + dt.timedelta(days=1)).isoformat()
        with pytest.raises(ValueError):
            ctrl.create_booking(user, "P101", tomorrow, "Ca 1", "   ")

    def test_valid_booking_creates_record(self):
        user = _make_user()
        ctrl = BookingController()
        tomorrow = (dt.date.today() + dt.timedelta(days=1)).isoformat()
        booking = ctrl.create_booking(user, "P101", tomorrow, "Ca 1", "Hoc nhom")
        assert booking.room_id == "P101"
        assert booking.status == "Cho duyet"
        assert booking.user_id == user.user_id


# ── list_bookings filter ──────────────────────────────────────────────────────

class TestListBookings:
    def test_non_admin_sees_only_own_bookings(self):
        user1 = _make_user()
        user2 = _make_user()
        ctrl = BookingController()
        tomorrow = (dt.date.today() + dt.timedelta(days=1)).isoformat()
        ctrl.create_booking(user1, "P102", tomorrow, "Ca 2", "Giang day")
        ctrl.create_booking(user2, "P103", tomorrow, "Ca 3", "Hoc bai")

        bookings = ctrl.list_bookings(current_user=user1, from_today=False)
        assert all(b.user_id == user1.user_id for b in bookings)

    def test_status_filter(self):
        user = _make_user()
        ctrl = BookingController()
        tomorrow = (dt.date.today() + dt.timedelta(days=1)).isoformat()
        b = ctrl.create_booking(user, "P104", tomorrow, "Ca 4", "Test")
        ctrl.approve_booking(b.booking_id)

        approved = ctrl.list_bookings(status="Da duyet", from_today=False)
        assert any(x.booking_id == b.booking_id for x in approved)

    def test_available_slots_excludes_booked(self):
        user = _make_user()
        ctrl = BookingController()
        tomorrow = (dt.date.today() + dt.timedelta(days=2)).isoformat()
        ctrl.create_booking(user, "P105", tomorrow, "Ca 1", "Hoc")
        ctrl.create_booking(user, "P105", tomorrow, "Ca 2", "Hoc")
        slots = ctrl.available_slots("P105", tomorrow)
        assert "Ca 1" not in slots
        assert "Ca 2" not in slots
        assert "Ca 3" in slots

    def test_get_rule_booking_details(self):
        day = dt.date.today() + dt.timedelta(days=1)
        rule = ScheduleRuleController().create_rule(_single_day_rule_payload(day))

        booking = BookingController().get_booking(f"RULE-{rule.rule_id}")

        assert booking is not None
        assert booking.booking_id == f"RULE-{rule.rule_id}"
        assert booking.room_id == "P201"

    def test_cancelled_booking_does_not_block_update(self):
        user = _make_user()
        ctrl = BookingController()
        day = (dt.date.today() + dt.timedelta(days=1)).isoformat()
        cancelled = ctrl.create_booking(user, "P105", day, "Ca 1", "Old")
        ctrl.cancel_booking(cancelled.booking_id, user)
        booking = ctrl.create_booking(user, "P104", day, "Ca 2", "Move me")

        updated = ctrl.update_booking(booking.booking_id, user, "P105", day, "Ca 1", "Moved")

        assert updated.room_id == "P105"
        assert updated.slot == "Ca 1"

    def test_update_booking_rejects_recurring_conflict(self):
        user = _make_user()
        ctrl = BookingController()
        day = dt.date.today() + dt.timedelta(days=1)
        ScheduleRuleController().create_rule(_single_day_rule_payload(day))
        booking = ctrl.create_booking(user, "P104", day.isoformat(), "Ca 2", "Move me")

        with pytest.raises(ValueError, match="co lich"):
            ctrl.update_booking(booking.booking_id, user, "P201", day.isoformat(), "Ca 1", "Moved")

    def test_cancelled_rule_frees_slot(self):
        day = dt.date.today() + dt.timedelta(days=1)
        rule_ctrl = ScheduleRuleController()
        rule = rule_ctrl.create_rule(_single_day_rule_payload(day))
        booking_ctrl = BookingController()
        assert "Ca 1" not in booking_ctrl.available_slots("P201", day.isoformat())

        rule_ctrl.update_rule_status(rule.rule_id, "Huy")

        assert "Ca 1" in booking_ctrl.available_slots("P201", day.isoformat())

        rule_ctrl.update_rule_status(rule.rule_id, "Hoat dong")

        assert "Ca 1" not in booking_ctrl.available_slots("P201", day.isoformat())

    def test_date_filter_excludes_out_of_range_rules(self):
        admin = _make_user(role="Admin")
        day = dt.date.today() + dt.timedelta(days=1)
        rule = ScheduleRuleController().create_rule(_single_day_rule_payload(day))
        future = (day + dt.timedelta(days=10)).isoformat()

        bookings = BookingController().list_bookings(
            current_user=admin,
            date_from=future,
            date_to=future,
            from_today=False,
        )

        assert all(b.booking_id != f"RULE-{rule.rule_id}" for b in bookings)
