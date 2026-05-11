"""User management business logic."""
from __future__ import annotations
from dao.user_dao import UserDAO
from models.user import User
from utils.password_hash import hash_password, verify_password
from utils.validators import is_valid_email, is_valid_phone
from utils.logger import get_logger

_log = get_logger(__name__)

VALID_ROLES    = {"Admin", "Giang vien", "Sinh vien"}
VALID_STATUSES = {"Hoat dong", "Khoa", "Da xoa"}


class UserController:
    def __init__(self) -> None:
        self.user_dao = UserDAO()

    # ── Queries ───────────────────────────────────────────────────────────────

    def get_user(self, user_id: str) -> User | None:
        return self.user_dao.find_by_id(user_id)

    def list_users(self, keyword: str = "",
                   role: str = "", status: str = "") -> list[User]:
        """Return users filtered by keyword, role and/or status via SQL."""
        return self.user_dao.search(keyword=keyword.strip(), role=role, status=status)

    # ── Mutations ─────────────────────────────────────────────────────────────

    def save_user(self, payload: dict[str, str]) -> User:
        user_id   = payload["user_id"].strip().upper()
        username  = payload["username"].strip()
        full_name = payload["full_name"].strip()
        email     = payload["email"].strip()
        phone     = payload["phone"].strip()

        if not user_id:
            raise ValueError("Ma nguoi dung khong duoc de trong.")
        if not username or len(username) < 3:
            raise ValueError("Ten dang nhap phai co it nhat 3 ky tu.")
        if not full_name:
            raise ValueError("Ho va ten khong duoc de trong.")
        if not is_valid_email(email):
            raise ValueError("Email khong hop le.")
        if not is_valid_phone(phone):
            raise ValueError("So dien thoai khong hop le.")
        role = payload.get("role", "").strip()
        if role and role not in VALID_ROLES:
            raise ValueError(f"Vai tro '{role}' khong hop le.")

        existing = self.user_dao.find_by_id(user_id)
        is_new = existing is None

        by_username = self.user_dao.find_by_username(username)
        if by_username is not None and by_username.user_id != user_id:
            raise ValueError(f"Ten dang nhap '{username}' da duoc su dung.")

        by_email = self.user_dao.find_by_email(email)
        if by_email is not None and by_email.user_id != user_id:
            raise ValueError("Email nay da duoc dang ky boi nguoi dung khac.")

        password = payload.get("password", "").strip()
        if password:
            if len(password) < 6:
                raise ValueError("Mat khau phai co it nhat 6 ky tu.")
            password_hash = hash_password(password)
        elif not is_new:
            password_hash = existing.password_hash  # type: ignore[union-attr]
        else:
            raise ValueError("Mat khau khong duoc de trong khi them moi.")

        user = User(
            user_id=user_id,
            username=username,
            full_name=full_name,
            role=role or "Sinh vien",
            email=email, phone=phone,
            password_hash=password_hash,
            status=payload.get("status", "Hoat dong").strip(),
        )
        saved = self.user_dao.save(user)
        _log.info("%s user %s (%s)", "Created" if is_new else "Updated",
                  user_id, username)
        return saved

    def delete_user(self, user_id: str) -> None:
        self.user_dao.delete(user_id)
        _log.info("User %s soft-deleted", user_id)

    def change_password(self, user_id: str, old_password: str,
                        new_password: str) -> None:
        """Verify old password then set new one.  Raises ValueError on failure."""
        user = self.user_dao.find_by_id(user_id)
        if user is None:
            raise ValueError("Khong tim thay nguoi dung.")
        if not verify_password(old_password, user.password_hash):
            raise ValueError("Mat khau cu khong dung.")
        if len(new_password.strip()) < 6:
            raise ValueError("Mat khau moi phai co it nhat 6 ky tu.")
        if old_password.strip() == new_password.strip():
            raise ValueError("Mat khau moi phai khac mat khau cu.")
        user.password_hash = hash_password(new_password.strip())
        self.user_dao.save(user)
        _log.info("Password changed for user %s", user_id)

    def update_profile(self, user_id: str, full_name: str,
                       email: str, phone: str) -> User:
        """Update non-sensitive profile fields.  Raises ValueError on failure."""
        user = self.user_dao.find_by_id(user_id)
        if user is None:
            raise ValueError("Khong tim thay nguoi dung.")
        full_name = full_name.strip()
        email     = email.strip()
        phone     = phone.strip()
        if not full_name:
            raise ValueError("Ho va ten khong duoc de trong.")
        if not is_valid_email(email):
            raise ValueError("Email khong hop le.")
        if not is_valid_phone(phone):
            raise ValueError("So dien thoai khong hop le.")
        by_email = self.user_dao.find_by_email(email)
        if by_email is not None and by_email.user_id != user_id:
            raise ValueError("Email nay da duoc dang ky boi nguoi dung khac.")
        user.full_name = full_name
        user.email     = email
        user.phone     = phone
        saved = self.user_dao.save(user)
        _log.info("Profile updated for user %s", user_id)
        return saved

    def set_status(self, user_id: str, new_status: str) -> User:
        """Activate or lock an account."""
        if new_status not in VALID_STATUSES:
            raise ValueError(f"Trang thai '{new_status}' khong hop le.")
        user = self.user_dao.find_by_id(user_id)
        if user is None:
            raise ValueError("Khong tim thay nguoi dung.")
        user.status = new_status
        saved = self.user_dao.save(user)
        _log.info("User %s status → %s", user_id, new_status)
        return saved
