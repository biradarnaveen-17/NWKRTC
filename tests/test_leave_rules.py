from datetime import date, timedelta

import pytest

from backend.leave_rules import eligible_leave_date, validate_one_day_cl_request


def test_eligible_date_is_exactly_nine_calendar_days_ahead():
    today = date(2026, 10, 14)
    assert eligible_leave_date(today) == date(2026, 10, 23)


def test_rule_handles_month_boundary():
    today = date(2026, 10, 28)
    assert eligible_leave_date(today) == date(2026, 11, 6)


def test_valid_one_day_cl_request():
    today = date(2026, 10, 14)
    target = today + timedelta(days=9)
    validate_one_day_cl_request(today, target, target, "CL")


def test_rejects_wrong_date():
    today = date(2026, 10, 14)
    with pytest.raises(ValueError, match="exactly 9 calendar days"):
        validate_one_day_cl_request(today, today + timedelta(days=8), today + timedelta(days=8), "CL")


def test_rejects_non_cl():
    today = date(2026, 10, 14)
    target = today + timedelta(days=9)
    with pytest.raises(ValueError, match="CL.*only"):
        validate_one_day_cl_request(today, target, target, "EL")


def test_rejects_multi_day_request():
    today = date(2026, 10, 14)
    with pytest.raises(ValueError, match="one-day leave"):
        validate_one_day_cl_request(today, today + timedelta(days=9), today + timedelta(days=10), "CL")
