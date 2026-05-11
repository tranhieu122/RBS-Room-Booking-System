"""Authentication logic."""
from __future__ import annotations
import datetime as dt # type: ignore
import uuid
from dao.user_dao import UserDAO
from models.user import User
from utils.password_hash import verify_password, hash_password
from utils.validators import is_valid_email, is_valid_phone
from utils.logger import get_logger

_log = get_logger(__name__)

# ── Rate-limiting constants ────────────────────────────────────────────────────
_MAX_ATTEMPTS  = 5           # lock after this many consecutive failures
_LOCKOUT_SECS  = 300         # 5-minute lockout window

# Tracks {username: (fail_count, first_fail_timestamp)}
_login_attempts: dict[str, tuple[int, float]] = {}


def _check_lockout(username: str) -> int:
    """Return seconds remaining in lockout (0 = not locked)."""
    import time
    entry = _login_attempts.get(username)
    if entry is None:
        return 0
    count, first_fail = entry
    if count < _MAX_ATTEMPTS:
        return 0
    elapsed = time.time() - first_fail
    remaining = int(_LOCKOUT_SECS - elapsed)
    return max(remaining, 0)


def _record_failure(username: str) -> None:
    import time
    entry = _login_attempts.get(username)
    if entry is None:
        _login_attempts[username] = (1, time.time())
    else:
        count, first_fail = entry
        elapsed = time.time() - first_fail
        if elapsed >= _LOCKOUT_SECS:
            # Old lockout expired — reset counter
            _login_attempts[username] = (1, time.time())
        else:
            _login_attempts[username] = (count + 1, first_fail)


def _clear_failures(username: str) -> None:
    _login_attempts.pop(username, None)


class AuthController:
    def __init__(self) -> None:
        self.user_dao = UserDAO()

    # ── Login ─────────────────────────────────────────────────────────────────
    def authenticate(self, username: str, password: str) -> User | None:
        uname = username.strip()

        # Check lockout before hitting the DB
        remaining = _check_lockout(uname)
        if remaining > 0:
            mins = remaining // 60
            secs = remaining % 60
            raise PermissionError(
                f"Tai khoan tam khoa {mins}:{secs:02d} phut do dang nhap sai nhieu lan. "
                "Vui long thu lai sau."
            )

        user = self.user_dao.find_by_username(uname)
        if user is None or user.status != "Hoat dong":
            _record_failure(uname)
            _log.warning("Failed login attempt for username='%s'", uname)
            return None
        if not verify_password(password, user.password_hash):
            _record_failure(uname)
            attempts_left = _MAX_ATTEMPTS - (_login_attempts.get(uname, (0,))[0])
            _log.warning("Wrong password for username='%s' (%d attempts left)",
                         uname, max(attempts_left, 0))
            return None

        # Success — clear failure counter
        _clear_failures(uname)
        # Auto-upgrade legacy SHA-256 hash to PBKDF2 on successful login
        if not user.password_hash.startswith("pbkdf2:"):
            user.password_hash = hash_password(password)
            self.user_dao.save(user)
            _log.info("Upgraded password hash for '%s' to PBKDF2", uname)
        _log.info("User '%s' (%s) logged in", user.username, user.role)
        return user

    # ── Register ──────────────────────────────────────────────────────────────
    def register(self, full_name: str, username: str, email: str,
                 phone: str, password: str, role: str = "Sinh vien") -> User:
        """Create a new account.  Raises ValueError on validation failure."""
        full_name = full_name.strip()
        username  = username.strip()
        email     = email.strip()
        phone     = phone.strip()
        password  = password.strip()

        if not full_name:
            raise ValueError("Ho va ten khong duoc de trong.")
        if not username or len(username) < 3:
            raise ValueError("Ten dang nhap phai co it nhat 3 ky tu.")
        if self.user_dao.find_by_username(username) is not None:
            raise ValueError(f"Ten dang nhap '{username}' da duoc su dung.")
        if not is_valid_email(email):
            raise ValueError("Email khong hop le.")
        if self.user_dao.find_by_email(email) is not None:
            raise ValueError("Email nay da duoc dang ky.")
        if not is_valid_phone(phone):
            raise ValueError("So dien thoai khong hop le (10 chu so).")
        if len(password) < 6:
            raise ValueError("Mat khau phai co it nhat 6 ky tu.")

        # Generate a short unique ID
        new_id = ("SV" + uuid.uuid4().hex[:6]).upper()
        user = User(
            user_id=new_id,
            username=username,
            full_name=full_name,
            role=role,
            email=email,
            phone=phone,
            password_hash=hash_password(password),
            status="Hoat dong",
        )
        _log.info("New account registered: username='%s' role='%s'", username, role)
        return self.user_dao.save(user)

    # ── Forgot / reset password ───────────────────────────────────────────────
    def find_account_for_reset(self, username: str,
                               email: str) -> User | None:
        """Return the user only if both username AND email match."""
        username = username.strip()
        email    = email.strip().lower()
        user = self.user_dao.find_by_username(username)
        if user is None:
            return None
        if user.email.lower() != email:
            return None
        return user

    def reset_password(self, username: str, email: str,
                       new_password: str) -> None:
        """Verify identity then update password.  Raises ValueError on failure."""
        if len(new_password.strip()) < 6:
            raise ValueError("Mat khau moi phai co it nhat 6 ky tu.")
        user = self.find_account_for_reset(username, email)
        if user is None:
            raise ValueError(
                "Khong tim thay tai khoan voi ten dang nhap va email nay.")
        user.password_hash = hash_password(new_password.strip())
        self.user_dao.save(user)

    def change_password(self, username: str, old_password: str,
                        new_password: str) -> None:
        """Change password for a logged-in user after verifying old password."""
        new_password = new_password.strip()
        if len(new_password) < 6:
            raise ValueError("Mat khau moi phai co it nhat 6 ky tu.")
        user = self.authenticate(username, old_password)
        if user is None:
            raise ValueError("Mat khau hien tai khong dung.")
        if old_password.strip() == new_password:
            raise ValueError("Mat khau moi phai khac mat khau cu.")
        user.password_hash = hash_password(new_password)
        self.user_dao.save(user)
        _log.info("Password changed via profile for user '%s'", username)
