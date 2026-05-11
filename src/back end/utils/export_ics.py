"""Export bookings / schedule occurrences to ICS (iCalendar) format.

Usage:
    from utils.export_ics import export_bookings_to_ics, export_occurrences_to_ics
"""
from __future__ import annotations
import datetime as dt
import os
import uuid


# ── Helpers ───────────────────────────────────────────────────────────────────

def _ics_datetime(d: dt.date, t: dt.time | None = None) -> str:
    """Return iCal datetime string (local, floating)."""
    if t is None:
        return d.strftime("%Y%m%d")
    return dt.datetime.combine(d, t).strftime("%Y%m%dT%H%M%S")


def _escape(text: str) -> str:
    """Escape ICS text values per RFC 5545."""
    return (text
            .replace("\\", "\\\\")
            .replace(";",  "\\;")
            .replace(",",  "\\,")
            .replace("\n", "\\n"))


_SLOT_TIMES: dict[str, tuple[str, str]] = {
    "Ca 1": ("07:00", "09:00"),
    "Ca 2": ("09:15", "11:15"),
    "Ca 3": ("13:00", "15:00"),
    "Ca 4": ("15:15", "17:15"),
    "Ca 5": ("17:30", "19:30"),
}


# ── Core builder ──────────────────────────────────────────────────────────────

def _build_vevent(
    uid: str,
    summary: str,
    dtstart: str,
    dtend: str,
    location: str = "",
    description: str = "",
    date_only: bool = False,
) -> str:
    lines = [
        "BEGIN:VEVENT",
        f"UID:{uid}",
        f"DTSTAMP:{dt.datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')}",
    ]
    if date_only:
        lines.append(f"DTSTART;VALUE=DATE:{dtstart}")
        lines.append(f"DTEND;VALUE=DATE:{dtend}")
    else:
        lines.append(f"DTSTART:{dtstart}")
        lines.append(f"DTEND:{dtend}")
    lines.append(f"SUMMARY:{_escape(summary)}")
    if location:
        lines.append(f"LOCATION:{_escape(location)}")
    if description:
        lines.append(f"DESCRIPTION:{_escape(description)}")
    lines.append("END:VEVENT")
    return "\r\n".join(lines)


def _wrap_calendar(vevents: list[str], calname: str = "Lich dat phong") -> str:
    header = "\r\n".join([
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "PRODID:-//BTL-Nhom24//Classroom Booking//VI",
        f"X-WR-CALNAME:{_escape(calname)}",
        "CALSCALE:GREGORIAN",
        "METHOD:PUBLISH",
    ])
    body   = "\r\n".join(vevents)
    footer = "END:VCALENDAR"
    return header + "\r\n" + body + "\r\n" + footer + "\r\n"


# ── Public API ────────────────────────────────────────────────────────────────

def export_bookings_to_ics(bookings: list, file_path: str) -> None:
    """Write one-off bookings (Booking model list) to an ICS file.

    Args:
        bookings:  List of Booking objects (must have booking_date, slot,
                   room_id, user_name, purpose, status).
        file_path: Destination .ics path.
    """
    vevents: list[str] = []
    for b in bookings:
        times = _SLOT_TIMES.get(getattr(b, "slot", ""), None)
        booking_date_obj = dt.date.fromisoformat(b.booking_date)
        if times:
            t_start = dt.time.fromisoformat(times[0])
            t_end   = dt.time.fromisoformat(times[1])
            dtstart = _ics_datetime(booking_date_obj, t_start)
            dtend   = _ics_datetime(booking_date_obj, t_end)
            date_only = False
        else:
            dtstart = _ics_datetime(booking_date_obj)
            # ICS all-day DTEND is exclusive next day
            dtend   = _ics_datetime(booking_date_obj + dt.timedelta(days=1))
            date_only = True

        summary = f"[{b.slot}] {b.room_id} — {b.purpose}"
        desc    = (f"Nguoi dat: {b.user_name}\n"
                   f"Trang thai: {b.status}\n"
                   f"Ma dat phong: {b.booking_id}")
        uid = f"booking-{b.booking_id}@btl-nhom24"

        vevents.append(_build_vevent(
            uid=uid, summary=summary,
            dtstart=dtstart, dtend=dtend,
            location=b.room_id, description=desc,
            date_only=date_only,
        ))

    ics_content = _wrap_calendar(vevents, "Lich dat phong hoc")
    os.makedirs(os.path.dirname(os.path.abspath(file_path)), exist_ok=True)
    with open(file_path, "w", encoding="utf-8", newline="") as f:
        f.write(ics_content)


def export_occurrences_to_ics(occurrences: list, file_path: str) -> None:
    """Write recurring schedule occurrences (ScheduleOccurrence list) to ICS.

    Args:
        occurrences: List of ScheduleOccurrence objects (must have
                     occurrence_date, start_time, end_time, subject,
                     room_id, lecturer_name, status).
        file_path:   Destination .ics path.
    """
    vevents: list[str] = []
    for occ in occurrences:
        if getattr(occ, "status", "") == "Huy":
            continue
        occ_date = dt.date.fromisoformat(occ.occurrence_date)
        try:
            t_start = dt.time.fromisoformat(occ.start_time)
            t_end   = dt.time.fromisoformat(occ.end_time)
            dtstart = _ics_datetime(occ_date, t_start)
            dtend   = _ics_datetime(occ_date, t_end)
            date_only = False
        except (ValueError, AttributeError):
            dtstart = _ics_datetime(occ_date)
            dtend   = _ics_datetime(occ_date + dt.timedelta(days=1))
            date_only = True

        summary = f"[CK] {occ.subject} — {occ.room_id}"
        desc    = (f"Giang vien: {getattr(occ, 'lecturer_name', '')}\n"
                   f"Phong: {occ.room_id}\n"
                   f"Trang thai: {getattr(occ, 'status', '')}")
        uid = f"occ-{getattr(occ, 'occ_id', uuid.uuid4().hex)}@btl-nhom24"

        vevents.append(_build_vevent(
            uid=uid, summary=summary,
            dtstart=dtstart, dtend=dtend,
            location=occ.room_id, description=desc,
            date_only=date_only,
        ))

    ics_content = _wrap_calendar(vevents, "Lich day theo chu ky")
    os.makedirs(os.path.dirname(os.path.abspath(file_path)), exist_ok=True)
    with open(file_path, "w", encoding="utf-8", newline="") as f:
        f.write(ics_content)
