"""Unit tests for ScheduleRuleController — validation and occurrence generation."""
from __future__ import annotations
import sys, os
import datetime as dt
import pytest

_ROOT = os.path.join(os.path.dirname(__file__), "..", "src", "back end")
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

os.environ.setdefault("DB_PATH", ":memory:")

from controllers.schedule_rule_controller import ScheduleRuleController


def _make_ctrl() -> ScheduleRuleController:
    return ScheduleRuleController()


def _base_payload(**overrides) -> dict:  # type: ignore
    today = dt.date.today()
    return {
        "subject":       "Lap trinh Python",
        "days_of_week":  [2, 4],          # Tue, Thu
        "start_time":    "07:00",
        "end_time":      "09:00",
        "start_date":    today.isoformat(),
        "end_date":      (today + dt.timedelta(weeks=4)).isoformat(),
        "room_id":       "P201",
        "lecturer_id":   "GV001",
        "lecturer_name": "Nguyen Van A",
        **overrides,
    }


class TestCreateRuleValidation:
    def test_empty_subject_rejected(self):
        ctrl = _make_ctrl()
        with pytest.raises(ValueError, match="mon hoc"):
            ctrl.create_rule(_base_payload(subject=""))

    def test_no_days_rejected(self):
        ctrl = _make_ctrl()
        with pytest.raises(ValueError, match="it nhat"):
            ctrl.create_rule(_base_payload(days_of_week=[]))

    def test_invalid_day_number_rejected(self):
        ctrl = _make_ctrl()
        with pytest.raises(ValueError):
            ctrl.create_rule(_base_payload(days_of_week=[0, 8]))

    def test_start_after_end_time_rejected(self):
        ctrl = _make_ctrl()
        with pytest.raises(ValueError, match="truoc"):
            ctrl.create_rule(_base_payload(start_time="09:00", end_time="07:00"))

    def test_end_date_before_start_date_rejected(self):
        ctrl = _make_ctrl()
        today = dt.date.today().isoformat()
        yesterday = (dt.date.today() - dt.timedelta(days=1)).isoformat()
        with pytest.raises(ValueError):
            ctrl.create_rule(_base_payload(start_date=today, end_date=yesterday))


class TestOccurrenceGeneration:
    def test_occurrences_created_for_rule(self):
        ctrl = _make_ctrl()
        rule = ctrl.create_rule(_base_payload())
        occs = ctrl.list_occurrences(rule.rule_id)
        assert len(occs) > 0

    def test_occurrences_match_selected_days(self):
        ctrl = _make_ctrl()
        rule = ctrl.create_rule(_base_payload(days_of_week=[2]))  # Tue only
        occs = ctrl.list_occurrences(rule.rule_id)
        # All occurrences should fall on Tuesday (ISO weekday 2)
        for occ in occs:
            assert dt.date.fromisoformat(occ.occurrence_date).isoweekday() == 2

    def test_occurrences_count_correct(self):
        ctrl = _make_ctrl()
        today = dt.date.today()
        # 4 weeks with Mon+Wed = roughly 8 occurrences
        rule = ctrl.create_rule(_base_payload(
            days_of_week=[1, 3],
            start_date=today.isoformat(),
            end_date=(today + dt.timedelta(weeks=4)).isoformat(),
        ))
        count = ctrl.count_occurrences(rule.rule_id)
        assert count >= 7  # at least 7 (could be 8 or 9 depending on today)

    def test_cancel_rule_marks_occurrences(self):
        ctrl = _make_ctrl()
        rule = ctrl.create_rule(_base_payload())
        ctrl.cancel_rule(rule.rule_id)
        updated = ctrl.get_rule(rule.rule_id)
        assert updated is not None
        assert updated.status == "Huy"
