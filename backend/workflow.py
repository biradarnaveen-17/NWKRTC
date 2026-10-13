"""Deterministic mock workflow for development; never contacts the live portal."""
from dataclasses import dataclass, asdict
from datetime import date
from typing import Any

from backend.leave_rules import validate_one_day_cl_request


@dataclass
class WorkflowResult:
    status: str
    steps: list[str]
    message: str
    leave_date: str

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


def run_mock_workflow(today: date, leave_date: date, leave_type: str = "CL") -> WorkflowResult:
    """Validate a request and walk through simulated steps without browser/network activity."""
    steps = ["preflight_started"]
    try:
        validate_one_day_cl_request(today, leave_date, leave_date, leave_type)
    except ValueError as exc:
        steps.append("validation_failed")
        return WorkflowResult(
            status="REJECTED",
            steps=steps,
            message=str(exc),
            leave_date=leave_date.isoformat(),
        )

    steps.extend([
        "date_rule_validated",
        "mock_login_ready",
        "mock_dashboard_opened",
        "mock_auto_sanction_selected",
        "mock_short_leave_selected",
        "mock_cl_selected",
        "mock_dates_selected",
        "simulation_complete",
    ])
    return WorkflowResult(
        status="SIMULATED",
        steps=steps,
        message=(
            "Mock workflow completed. No NWKRTC website was opened and no leave was submitted."
        ),
        leave_date=leave_date.isoformat(),
    )
