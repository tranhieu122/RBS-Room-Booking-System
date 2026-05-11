"""Unit tests for AuthController — login, register, rate limiting."""
from __future__ import annotations
import sys, os
import pytest

# Resolve the back-end source root
_ROOT = os.path.join(os.path.dirname(__file__), "..", "src", "back end")
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

# Use an in-memory DB so tests don't touch real data
os.environ.setdefault("DB_PATH", ":memory:")

from controllers.auth_controller import (
    AuthController, _login_attempts, _MAX_ATTEMPTS, _LOCKOUT_SECS,
    _record_failure, _clear_failures, _check_lockout,
)


# ── Helpers ───────────────────────────────────────────────────────────────────
def _make_ctrl() -> AuthController:
    return AuthController()


# ── Register + Authenticate ───────────────────────────────────────────────────

class TestRegister:
    def test_register_success(self):
        ctrl = _make_ctrl()
        user = ctrl.register("Test User", "testuser1", "test1@example.com",
                             "0901234567", "secret123")
        assert user.username == "testuser1"
        assert user.role == "Sinh vien"
        assert not user.password_hash.startswith("secret")  # must be hashed

    def test_register_duplicate_username(self):
        ctrl = _make_ctrl()
        ctrl.register("A", "dupu", "a@example.com", "0901234561", "pass123")
        with pytest.raises(ValueError, match="da duoc su dung"):
            ctrl.register("B", "dupu", "b@example.com", "0901234562", "pass456")

    def test_register_short_password(self):
        ctrl = _make_ctrl()
        with pytest.raises(ValueError, match="it nhat 6"):
            ctrl.register("A", "newu1", "aa@example.com", "0901234563", "abc")

    def test_register_invalid_email(self):
        ctrl = _make_ctrl()
        with pytest.raises(ValueError, match="Email"):
            ctrl.register("A", "newu2", "not-an-email", "0901234564", "pass123")


class TestAuthenticate:
    def setup_method(self):
        _login_attempts.clear()

    def test_login_success(self):
        ctrl = _make_ctrl()
        ctrl.register("Login Test", "loginuser", "login@example.com",
                      "0901111111", "mypassword")
        user = ctrl.authenticate("loginuser", "mypassword")
        assert user is not None
        assert user.username == "loginuser"

    def test_login_wrong_password_returns_none(self):
        ctrl = _make_ctrl()
        ctrl.register("WP User", "wpuser", "wp@example.com",
                      "0902222222", "correctpw")
        result = ctrl.authenticate("wpuser", "wrongpw")
        assert result is None

    def test_login_nonexistent_user_returns_none(self):
        ctrl = _make_ctrl()
        result = ctrl.authenticate("ghost_user", "anypass")
        assert result is None


# ── Rate limiting ─────────────────────────────────────────────────────────────

class TestRateLimiting:
    def setup_method(self):
        _login_attempts.clear()

    def test_no_lockout_below_max(self):
        for _ in range(_MAX_ATTEMPTS - 1):
            _record_failure("ratelimit_user")
        assert _check_lockout("ratelimit_user") == 0

    def test_lockout_after_max_attempts(self):
        for _ in range(_MAX_ATTEMPTS):
            _record_failure("ratelimit_user2")
        assert _check_lockout("ratelimit_user2") > 0

    def test_authenticate_raises_on_lockout(self):
        ctrl = _make_ctrl()
        ctrl.register("Lock Me", "lockme", "lock@example.com",
                      "0903333333", "rightpw")
        for _ in range(_MAX_ATTEMPTS):
            _record_failure("lockme")
        with pytest.raises(PermissionError, match="khoa"):
            ctrl.authenticate("lockme", "rightpw")

    def test_clear_failures_removes_lockout(self):
        for _ in range(_MAX_ATTEMPTS):
            _record_failure("clearme")
        assert _check_lockout("clearme") > 0
        _clear_failures("clearme")
        assert _check_lockout("clearme") == 0
