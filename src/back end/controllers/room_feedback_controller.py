"""Controller for room rating and issue reporting."""
from __future__ import annotations
from dao.room_feedback_dao import RoomRatingDAO, RoomIssueDAO, RoomRating, RoomIssue
from models.user import User
from utils.logger import get_logger

_log = get_logger(__name__)


class RoomFeedbackController:
    def __init__(self) -> None:
        self.rating_dao = RoomRatingDAO()
        self.issue_dao  = RoomIssueDAO()

    # ── Ratings ──────────────────────────────────────────────────────────────

    def add_rating(self, room_id: str, user: User, stars: int, comment: str) -> RoomRating:
        if stars < 1 or stars > 5:
            raise ValueError("So sao phai tu 1 den 5.")
        if not room_id:
            raise ValueError("Khong xac dinh duoc phong.")
        return self.rating_dao.add(room_id, user.user_id, user.full_name,
                                   stars, comment.strip())

    def get_ratings(self, room_id: str) -> list[RoomRating]:
        return self.rating_dao.list_by_room(room_id)

    def get_user_rating(self, room_id: str, user_id: str) -> RoomRating | None:
        """Return the rating a specific user gave for a room, or None."""
        return self.rating_dao.user_rating(room_id, user_id)

    def average_stars(self, room_id: str) -> float:
        return self.rating_dao.average_stars(room_id)

    # ── Issues ───────────────────────────────────────────────────────────────

    def report_issue(self, room_id: str, user: User, description: str) -> RoomIssue:
        if not description.strip():
            raise ValueError("Mo ta loi khong duoc de trong.")
        if not room_id:
            raise ValueError("Khong xac dinh duoc phong.")
        return self.issue_dao.report(room_id, user.user_id,
                                     user.full_name, description.strip())

    def get_issues(self, room_id: str = "") -> list[RoomIssue]:
        return self.issue_dao.list_all(room_id)

    def resolve_issue(self, issue_id: int) -> None:
        self.issue_dao.update_status(issue_id, "Da xu ly")
