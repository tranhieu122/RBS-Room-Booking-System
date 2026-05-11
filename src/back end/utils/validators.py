"""Input validation helpers."""
from __future__ import annotations
import datetime
import re

EMAIL_PATTERN = re.compile(r"^[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}$")
PHONE_PATTERN  = re.compile(r"^(0\d{9}|\+84\d{9})$")
ROOM_PATTERN   = re.compile(r"^[A-Z]\d{3}$")


def is_valid_email(value: str) -> bool:
    return bool(EMAIL_PATTERN.match(value.strip()))


def is_valid_phone(value: str) -> bool:
    return bool(PHONE_PATTERN.match(value.strip()))


def is_valid_room_code(value: str) -> bool:
    return bool(ROOM_PATTERN.match(value.strip().upper()))


def is_valid_date(value: str) -> bool:
    """Return True if *value* is a valid YYYY-MM-DD date string."""
    try:
        datetime.date.fromisoformat(value.strip())
        return True
    except ValueError:
        return False


def is_future_date(value: str) -> bool:
    """Return True if *value* is today or a future date."""
    try:
        d = datetime.date.fromisoformat(value.strip())
        return d >= datetime.date.today()
    except ValueError:
        return False


def sanitize(value: str, max_len: int = 255) -> str:
    """Strip whitespace and truncate to *max_len* characters."""
    return value.strip()[:max_len]


def password_strength(password: str) -> tuple[int, str]:
    """Return *(score 0-4, label)* for the given password.

    Score:  0=very weak  1=weak  2=fair  3=strong  4=very strong
    """
    p = password
    score = 0
    if len(p) >= 8:
        score += 1
    if len(p) >= 12:
        score += 1
    if re.search(r"[A-Z]", p) and re.search(r"[a-z]", p):
        score += 1
    if re.search(r"\d", p) and re.search(r"[^A-Za-z0-9]", p):
        score += 1
    labels = ["Rat yeu", "Yeu", "Trung binh", "Manh", "Rat manh"]
    return score, labels[score]
