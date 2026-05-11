"""Notification business logic."""
from __future__ import annotations
from dao.notification_dao import NotificationDAO
from models.user import User
from utils.logger import get_logger

_log = get_logger(__name__)


class NotificationController:
    def __init__(self) -> None:
        self.notif_dao = NotificationDAO()

    # ── Send ─────────────────────────────────────────────────────────────────

    def send_to_user(self, sender: User, recipient_id: str,
                     title: str, message: str) -> None:
        if not title.strip():
            raise ValueError("Tieu de khong duoc de trong.")
        if not message.strip():
            raise ValueError("Noi dung thong bao khong duoc de trong.")
        self.notif_dao.create(sender.user_id, sender.full_name,
                              recipient_id, title.strip(), message.strip())
        _log.info("Notification sent from %s to %s: %s",
                  sender.user_id, recipient_id, title)

    def send_system(self, recipient_id: str, title: str, message: str) -> None:
        """Send a system-generated notification (no human sender)."""
        if not title.strip() or not message.strip():
            return
        self.notif_dao.create("SYSTEM", "He thong",
                              recipient_id, title.strip(), message.strip())

    def send_to_role(self, sender: User, role: str, title: str,
                     message: str, user_list: list[User]) -> int:
        targets = [u for u in user_list if u.role == role]
        return self._bulk_send(sender, title, message, targets)

    def send_to_all(self, sender: User, title: str, message: str,
                    user_list: list[User]) -> int:
        # Include sender in the list so they can see their own broadcast for confirmation
        targets = user_list
        return self._bulk_send(sender, title, message, targets)

    def _bulk_send(self, sender: User, title: str, message: str,
                   targets: list[User]) -> int:
        if not title.strip():
            raise ValueError("Tieu de khong duoc de trong.")
        if not message.strip():
            raise ValueError("Noi dung thong bao khong duoc de trong.")
        for u in targets:
            self.notif_dao.create(sender.user_id, sender.full_name,
                                  u.user_id, title.strip(), message.strip())
        _log.info("Bulk notification from %s to %d users: %s",
                  sender.user_id, len(targets), title)
        return len(targets)

    # ── Read ─────────────────────────────────────────────────────────────────

    def get_notifications(self, user_id: str,
                          unread_only: bool = False) -> list[dict]:
        notifs = self.notif_dao.list_for_user(user_id)
        if unread_only:
            notifs = [n for n in notifs if not n.get("is_read")]
        return notifs

    def count_unread(self, user_id: str) -> int:
        return self.notif_dao.count_unread(user_id)

    def mark_all_read(self, user_id: str) -> None:
        self.notif_dao.mark_all_read(user_id)

    def mark_read(self, notif_id: int) -> None:
        self.notif_dao.mark_read(notif_id)

    # ── Delete ────────────────────────────────────────────────────────────────

    def delete(self, notif_id: int) -> None:
        self.notif_dao.delete(notif_id)

    def delete_all_read(self, user_id: str) -> int:
        """Delete all read notifications for a user. Returns count deleted."""
        notifs = self.notif_dao.list_for_user(user_id)
        read_ids = [n["id"] for n in notifs if n.get("is_read")]
        for nid in read_ids:
            self.notif_dao.delete(nid)
        _log.info("Deleted %d read notifications for user %s",
                  len(read_ids), user_id)
        return len(read_ids)
