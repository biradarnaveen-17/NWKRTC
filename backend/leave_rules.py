"""Pure validation helpers for the prototype leave workflow."""
from datetime import date, timedelta

ELIGIBILITY_DAYS_AHEAD = 9

def eligible_leave_date(today: date) -> date:
    """The user-described portal rule: leave date is exactly 9 calendar days ahead."""
    return today + timedelta(days=ELIGIBILITY_DAYS_AHEAD)

def validate_one_day_cl_request(today: date, leave_from: date, leave_to: date, leave_type: str) -> None:
    """Validate the requested one-day CL before it can be queued."""
    if leave_type != "CL":
        raise ValueError("This prototype currently supports Casual Leave (CL) only.")
    if leave_from != leave_to:
        raise ValueError("This workflow is configured for a one-day leave: From and To must match.")
    expected = eligible_leave_date(today)
    if leave_from != expected:
        raise ValueError(
            f"For this prototype's rule, select {expected.isoformat()} "
            f"(exactly {ELIGIBILITY_DAYS_AHEAD} calendar days ahead of today)."
        )
