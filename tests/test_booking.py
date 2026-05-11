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


# ── Helpers ───────────────────────────────────────────────────────────────────

def _make_user(role: str = "Sinh vien"):
    ctrl = AuthController()
    import uuid
    uname = "bk_" + uuid.uuid4().hex[:6]
    return ctrl.register("Test User", uname, f"{uname}@test.com",
                         "0901234567", "pass1234", role=role)


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
